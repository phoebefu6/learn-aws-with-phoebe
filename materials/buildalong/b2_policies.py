# Analyst session 2 - IAM policies as code, enforced by moto against a real boto3 call
import json, os, boto3
from moto import mock_aws
from moto.core import set_initial_no_auth_action_count

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
ANALYST_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {"Sid": "ReadCurated", "Effect": "Allow", "Action": ["s3:GetObject", "s3:ListBucket"],
         "Resource": ["arn:aws:s3:::acme-lake", "arn:aws:s3:::acme-lake/curated/*"]},
        {"Sid": "KeepTheLake", "Effect": "Deny", "Action": ["s3:DeleteBucket", "s3:PutBucketPolicy"], "Resource": "*"},
    ],
}

@set_initial_no_auth_action_count(8)          # the first 8 calls (setup) run as admin; then IAM is enforced
@mock_aws
def main():
    iam, admin_s3 = boto3.client("iam"), boto3.client("s3")
    admin_s3.create_bucket(Bucket="acme-lake")
    admin_s3.put_object(Bucket="acme-lake", Key="curated/nyc_taxi/part-0.parquet", Body=b"PAR1...")
    admin_s3.put_object(Bucket="acme-lake", Key="raw/nyc_taxi/trips.csv", Body=b"VendorID,...")
    iam.create_user(UserName="ana")
    arn = iam.create_policy(PolicyName="analyst-lake-read", PolicyDocument=json.dumps(ANALYST_POLICY))["Policy"]["Arn"]
    iam.attach_user_policy(UserName="ana", PolicyArn=arn)
    key = iam.create_access_key(UserName="ana")["AccessKey"]
    ana = boto3.client("s3", aws_access_key_id=key["AccessKeyId"], aws_secret_access_key=key["SecretAccessKey"])
    tries = [
        ("GetObject curated", lambda: ana.get_object(Bucket="acme-lake", Key="curated/nyc_taxi/part-0.parquet")),
        ("GetObject raw", lambda: ana.get_object(Bucket="acme-lake", Key="raw/nyc_taxi/trips.csv")),
        ("PutObject curated", lambda: ana.put_object(Bucket="acme-lake", Key="curated/x.parquet", Body=b"x")),
        ("DeleteBucket", lambda: ana.delete_bucket(Bucket="acme-lake")),
    ]
    for name, call in tries:
        try:
            call(); print(f"{name:18s} ALLOWED")
        except Exception as e:
            print(f"{name:18s} {e.response['Error']['Code']}")

main()
