# Analyst session 5 - Lambda or a container. The handler runs locally on moto S3; the bill uses real prices.
import io, json, os, time, zipfile, boto3, duckdb
from moto import mock_aws

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
# us-east-1, AWS Price List, retrieved 2026-10-03
LAMBDA_REQ, LAMBDA_GBS = 0.20 / 1e6, 0.0000166667
FARGATE_VCPU_HR, FARGATE_GB_HR = 0.04048, 0.004445

def handler(event, context=None):
    """S3 put event -> read the CSV that landed -> write it back as Parquet under curated/."""
    s3 = boto3.client("s3")
    rec = event["Records"][0]["s3"]
    bucket, key = rec["bucket"]["name"], rec["object"]["key"]
    s3.download_file(bucket, key, "/tmp/in.csv")
    duckdb.execute("COPY (SELECT * FROM read_csv_auto('/tmp/in.csv')) TO '/tmp/out.parquet' (FORMAT parquet)")
    out_key = key.replace("raw/", "curated/").replace(".csv", ".parquet")
    s3.upload_file("/tmp/out.parquet", bucket, out_key)
    return {"in": key, "out": out_key, "bytes_in": os.path.getsize("/tmp/in.csv"), "bytes_out": os.path.getsize("/tmp/out.parquet")}

with mock_aws():
    s3 = boto3.client("s3"); s3.create_bucket(Bucket="acme-lake")
    duckdb.execute("COPY (SELECT * FROM 'yellow_tripdata_2024-01_sample.parquet' WHERE CAST(tpep_pickup_datetime AS DATE) = DATE '2024-01-15') TO 'day.csv' (HEADER)")
    s3.upload_file("day.csv", "acme-lake", "raw/nyc_taxi/2024-01-15.csv")
    t0 = time.perf_counter()
    print(handler({"Records": [{"s3": {"bucket": {"name": "acme-lake"}, "object": {"key": "raw/nyc_taxi/2024-01-15.csv"}}}]}))
    print(f"handler ran in {time.perf_counter() - t0:.2f} s on this laptop")

    # Register it as a Lambda function; moto checks the configuration, it does not run your code here
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("handler.py", "def handler(event, context):\n    return event\n")
    iam = boto3.client("iam")
    role = iam.create_role(RoleName="ingest-role", AssumeRolePolicyDocument=json.dumps({"Version": "2012-10-17", "Statement": [
        {"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}))["Role"]["Arn"]
    lam = boto3.client("lambda")
    cfg = lam.create_function(FunctionName="ingest", Runtime="python3.12", Role=role, Handler="handler.handler",
                              Code={"ZipFile": buf.getvalue()}, Timeout=900, MemorySize=1024)
    print("registered:", cfg["FunctionName"], "| timeout", cfg["Timeout"], "s | memory", cfg["MemorySize"], "MB")
    bad = lam.create_function(FunctionName="too-long", Runtime="python3.12", Role=role, Handler="handler.handler",
                              Code={"ZipFile": buf.getvalue()}, Timeout=901, MemorySize=1024)
    print("moto also accepted a", bad["Timeout"], "s timeout; real Lambda caps it at 900 s. A mock is not a quota check.")

def lambda_month(invocations, seconds, memory_mb):
    return invocations * LAMBDA_REQ + invocations * seconds * memory_mb / 1024 * LAMBDA_GBS

def fargate_month(vcpu, gb, hours=730):
    return hours * (vcpu * FARGATE_VCPU_HR + gb * FARGATE_GB_HR)

print("one file a day, 20 s at 1 GB:      Lambda ${:,.2f}/month".format(lambda_month(30, 20, 1024)))
print("one file a minute, 20 s at 1 GB:   Lambda ${:,.2f}/month".format(lambda_month(43200, 20, 1024)))
print("a container always on, 1 vCPU 2 GB: Fargate ${:,.2f}/month".format(fargate_month(1, 2)))
