"""Write the IAM test table (materials/iam-cases.json + assets/aws-iam-cases.js).

Each case's expected verdict is derived from a sentence in the AWS IAM User Guide, named in
`doc`. expect is one of: allow, explicit (explicit Deny), implicit (implicit deny).
Serialised with json.dumps, never string interpolation.
"""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACCT = "111122223333"
USER = f"arn:aws:iam::{ACCT}:user/ana"
LAKE = "arn:aws:s3:::acme-lake"
EVAL = "Policy evaluation logic"
COND = "Condition operators"
MULTI = "Conditions with multiple context keys or values"
NOTA = "Policy elements: NotAction"
ACT = "Policy elements: Action"
RES = "Policy elements: Resource"
ENF = "How AWS enforcement code logic evaluates requests"


def pol(name, *stmts):
    return {"name": name, "Version": "2012-10-17", "Statement": list(stmts)}


def st(effect, action, resource, cond=None, sid=None, not_action=False, principal=None):
    s = {"Effect": effect}
    if sid:
        s["Sid"] = sid
    if principal is not None:
        s["Principal"] = principal
    s["NotAction" if not_action else "Action"] = action
    s["Resource"] = resource
    if cond:
        s["Condition"] = cond
    return s


def req(action, resource, **ctx):
    return {"principal": USER, "action": action, "resource": resource, "context": ctx}


ID_READ = pol("analyst-read", st("Allow", "s3:GetObject", LAKE + "/*", sid="ReadLake"))
ID_S3_ALL = pol("s3-all", st("Allow", "s3:*", "*", sid="AllS3"))
SECURE_DENY = pol("deny-plain-http", st("Deny", "s3:*", [LAKE, LAKE + "/*"],
                                         {"Bool": {"aws:SecureTransport": "false"}}, sid="DenyHttp"))
TAG_ALLOW = pol("tagged", st("Allow", "iam:*AccessKey*", f"arn:aws:iam::{ACCT}:user/*",
                             {"StringEquals": {"aws:PrincipalTag/job-category": "iamuser-admin"}}, sid="TagGate"))
IP_ALLOW = pol("office-ip", st("Allow", "athena:StartQueryExecution", "*",
                               {"IpAddress": {"aws:SourceIp": "203.0.113.0/24"}}, sid="OfficeOnly"))
BUCKET_POLICY_USER = pol("bucket-policy", st("Allow", "s3:GetObject", LAKE + "/*", sid="AnaReads",
                                             principal={"AWS": USER}))
BOUNDARY_GET = pol("boundary-read-only", st("Allow", "s3:GetObject", "*", sid="BoundaryRead"))
SCP_S3_ONLY = pol("scp-s3-only", st("Allow", "s3:*", "*", sid="ScpS3"))

C = []


def case(cid, title, doc, rule, set_, request, expect):
    C.append({"id": cid, "title": title, "doc": doc, "rule": rule,
              "set": set_, "request": request, "expect": expect})


k = lambda: f"{LAKE}/raw/2024/01/trips.parquet"

case("T01", "Identity policy allows the exact action", EVAL,
     "If any statement in any applicable identity-based policies allows the requested action, evaluation continues; no boundary, so Allow",
     {"identity": [ID_READ]}, req("s3:GetObject", k()), "allow")
case("T02", "No policy at all", ENF, "By default, all requests are implicitly denied",
     {"identity": []}, req("s3:GetObject", k()), "implicit")
case("T03", "Allowed to read, asks to write", ENF,
     "no statements in identity-based policies that allow the requested action: implicitly denied",
     {"identity": [ID_READ]}, req("s3:PutObject", k()), "implicit")
case("T04", "s3:* allowed, DeleteObject explicitly denied", ENF, "An explicit deny overrides an explicit allow",
     {"identity": [ID_S3_ALL, pol("no-delete", st("Deny", "s3:DeleteObject", "*", sid="NoDelete"))]},
     req("s3:DeleteObject", k()), "explicit")
case("T05", "Same policies, a read", ENF, "the Deny names DeleteObject only, so the s3:* Allow stands",
     {"identity": [ID_S3_ALL, pol("no-delete", st("Deny", "s3:DeleteObject", "*", sid="NoDelete"))]},
     req("s3:GetObject", k()), "allow")
case("T06", "Action names ignore case", ACT, "The prefix and the action name are case insensitive",
     {"identity": [pol("odd-case", st("Allow", "S3:getobject", LAKE + "/*"))]}, req("s3:GetObject", k()), "allow")
case("T07", "Wildcard inside an action name, match", ACT,
     "iam:*AccessKey* applies to CreateAccessKey, DeleteAccessKey, ListAccessKeys and UpdateAccessKey",
     {"identity": [pol("keys", st("Allow", "iam:*AccessKey*", "*"))]},
     req("iam:ListAccessKeys", f"arn:aws:iam::{ACCT}:user/ana"), "allow")
case("T08", "Wildcard inside an action name, no match", ACT, "ListUsers does not contain AccessKey",
     {"identity": [pol("keys", st("Allow", "iam:*AccessKey*", "*"))]},
     req("iam:ListUsers", f"arn:aws:iam::{ACCT}:user/ana"), "implicit")
case("T09", "Single-character wildcard in an action", ACT, "? is a single-character match wildcard",
     {"identity": [pol("q", st("Allow", "s3:Get?bject", LAKE + "/*"))]}, req("s3:GetObject", k()), "allow")
case("T10", "Resource * runs across slashes", RES,
     "the ARN bucket/*/test/* applies to bucket/1/2/test/3/object.jpg",
     {"identity": [pol("tests", st("Allow", "s3:GetObject", LAKE + "/*/test/*"))]},
     req("s3:GetObject", LAKE + "/1/2/test/3/object.jpg"), "allow")
case("T11", "Resource pattern that must not match", RES,
     "the ARN would not match bucket/1-test/object.jpg",
     {"identity": [pol("tests", st("Allow", "s3:GetObject", LAKE + "/*/test/*"))]},
     req("s3:GetObject", LAKE + "/1-test/object.jpg"), "implicit")
case("T12", "Resource names are case sensitive", RES, "In the Resource element, the IAM user name is case sensitive",
     {"identity": [pol("bob", st("Allow", "iam:GetUser", f"arn:aws:iam::{ACCT}:user/Bob"))]},
     req("iam:GetUser", f"arn:aws:iam::{ACCT}:user/bob"), "implicit")
case("T13", "Bucket ARN is not its objects", RES,
     "arn:aws:s3:::bucket names the bucket; objects need bucket/*",
     {"identity": [pol("bucket-only", st("Allow", "s3:GetObject", LAKE))]}, req("s3:GetObject", k()), "implicit")
case("T14", "StringEquals on a principal tag, match", COND, "Policy condition iamuser-admin, request iamuser-admin: Match",
     {"identity": [TAG_ALLOW]},
     req("iam:CreateAccessKey", f"arn:aws:iam::{ACCT}:user/ana", **{"aws:PrincipalTag/job-category": "iamuser-admin"}), "allow")
case("T15", "StringEquals on a principal tag, other value", COND, "request dev-ops: No match",
     {"identity": [TAG_ALLOW]},
     req("iam:CreateAccessKey", f"arn:aws:iam::{ACCT}:user/ana", **{"aws:PrincipalTag/job-category": "dev-ops"}), "implicit")
case("T16", "StringEquals, tag missing from the request", COND,
     "If the key that you specify in a policy condition is not present in the request context, the values do not match",
     {"identity": [TAG_ALLOW]}, req("iam:CreateAccessKey", f"arn:aws:iam::{ACCT}:user/ana"), "implicit")
case("T17", "IpAddress inside the range", COND, "203.0.113.0/24 with aws:SourceIp 203.0.113.1: Match",
     {"identity": [IP_ALLOW]}, req("athena:StartQueryExecution", "*", **{"aws:SourceIp": "203.0.113.1"}), "allow")
case("T18", "IpAddress outside the range", COND, "203.0.113.0/24 with aws:SourceIp 198.51.100.1: No match",
     {"identity": [IP_ALLOW]}, req("athena:StartQueryExecution", "*", **{"aws:SourceIp": "198.51.100.1"}), "implicit")
case("T19", "IP without a prefix means /32", COND,
     "If you specify an IP address without the associated routing prefix, IAM uses the default prefix value of /32",
     {"identity": [pol("one-ip", st("Allow", "athena:StartQueryExecution", "*", {"IpAddress": {"aws:SourceIp": "203.0.113.5"}}))]},
     req("athena:StartQueryExecution", "*", **{"aws:SourceIp": "203.0.113.6"}), "implicit")
case("T20", "Deny plain HTTP: request over HTTP", COND, "Bool aws:SecureTransport false, request false: Match",
     {"identity": [ID_S3_ALL, SECURE_DENY]}, req("s3:GetObject", k(), **{"aws:SecureTransport": "false"}), "explicit")
case("T21", "Deny plain HTTP: request over TLS", COND, "Bool aws:SecureTransport false, request true: No match",
     {"identity": [ID_S3_ALL, SECURE_DENY]}, req("s3:GetObject", k(), **{"aws:SecureTransport": "true"}), "allow")
case("T22", "Deny plain HTTP: key absent", COND, "No aws:SecureTransport in the request context: No match",
     {"identity": [ID_S3_ALL, SECURE_DENY]}, req("s3:GetObject", k()), "allow")
case("T23", "Several values for one key are OR", MULTI,
     "If a single condition operator includes multiple values for a context key, those values are evaluated using a logical OR",
     {"identity": [pol("teams", st("Allow", "glue:GetTable", "*", {"StringEquals": {"aws:PrincipalTag/team": ["finance", "growth"]}}))]},
     req("glue:GetTable", f"arn:aws:glue:us-east-1:{ACCT}:table/sales/orders", **{"aws:PrincipalTag/team": "growth"}), "allow")
case("T24", "Two operators in one block are AND", MULTI,
     "If your policy statement has multiple condition operators, the condition operators are evaluated using a logical AND",
     {"identity": [pol("tag-and-ip", st("Allow", "athena:StartQueryExecution", "*",
                                         {"StringEquals": {"aws:PrincipalTag/team": "growth"},
                                          "IpAddress": {"aws:SourceIp": "203.0.113.0/24"}}))]},
     req("athena:StartQueryExecution", "*", **{"aws:PrincipalTag/team": "growth", "aws:SourceIp": "198.51.100.7"}), "implicit")
case("T25", "NotAction allows everything except IAM: an S3 read", NOTA,
     "allows users to access every action in every AWS service except for IAM",
     {"identity": [pol("not-iam", st("Allow", "iam:*", "*", not_action=True))]}, req("s3:GetObject", k()), "allow")
case("T26", "NotAction allows everything except IAM: an IAM call", NOTA, "iam:CreateUser is in the excluded list",
     {"identity": [pol("not-iam", st("Allow", "iam:*", "*", not_action=True))]},
     req("iam:CreateUser", f"arn:aws:iam::{ACCT}:user/eve"), "implicit")
case("T27", "Bucket policy names the user, no identity policy", EVAL,
     "same account: the resulting permissions are the union of identity-based and resource-based",
     {"identity": [], "resource": BUCKET_POLICY_USER}, req("s3:GetObject", k()), "allow")
case("T28", "Bucket policy explicitly denies the user", EVAL, "An explicit deny in either of these policies overrides the allow",
     {"identity": [ID_S3_ALL], "resource": pol("bucket-deny", st("Deny", "s3:GetObject", LAKE + "/*", principal={"AWS": USER}))},
     req("s3:GetObject", k()), "explicit")
case("T29", "Boundary narrower than the identity policy", EVAL,
     "identity-based policies and permissions boundary: the resulting permissions are the intersection",
     {"identity": [ID_S3_ALL], "boundary": BOUNDARY_GET}, req("s3:PutObject", k()), "implicit")
case("T30", "Inside both identity policy and boundary", EVAL, "allowed by both, so in the intersection",
     {"identity": [ID_S3_ALL], "boundary": BOUNDARY_GET}, req("s3:GetObject", k()), "allow")
case("T31", "Bucket policy grants the user ARN, boundary does not allow", ENF,
     "resource-based policies that grant permissions to an IAM user ARN are not limited by an implicit deny in an identity-based policy or permissions boundary",
     {"identity": [], "resource": pol("bucket-put", st("Allow", "s3:PutObject", LAKE + "/*", principal={"AWS": USER})),
      "boundary": BOUNDARY_GET}, req("s3:PutObject", k()), "allow")
case("T32", "SCP allows only S3, user asks Athena", ENF,
     "If the enforcement code does not find any applicable Allow statements in the SCPs, final decision of Deny",
     {"identity": [IP_ALLOW], "scp": SCP_S3_ONLY},
     req("athena:StartQueryExecution", "*", **{"aws:SourceIp": "203.0.113.1"}), "implicit")
case("T33", "SCP explicitly denies a delete", EVAL, "An explicit deny in the identity-based policy, an SCP, or an RCP overrides the allow",
     {"identity": [ID_S3_ALL], "scp": pol("scp", st("Allow", "*", "*"), st("Deny", "s3:DeleteBucket", "*", sid="KeepBuckets"))},
     req("s3:DeleteBucket", LAKE), "explicit")
case("T34", "Deny in the boundary itself", EVAL, "An explicit deny in either of these policies overrides the allow",
     {"identity": [ID_S3_ALL], "boundary": pol("boundary", st("Allow", "s3:*", "*"), st("Deny", "s3:PutBucketPolicy", "*"))},
     req("s3:PutBucketPolicy", LAKE), "explicit")
case("T35", "Deny outside the office, from outside", COND, "NotIpAddress: all IP addresses except the specified range",
     {"identity": [ID_S3_ALL, pol("office-fence", st("Deny", "*", "*", {"NotIpAddress": {"aws:SourceIp": "203.0.113.0/24"}}))]},
     req("s3:GetObject", k(), **{"aws:SourceIp": "198.51.100.9"}), "explicit")
case("T36", "Deny outside the office, from inside", COND, "203.0.113.20 is in the range, so the Deny does not apply",
     {"identity": [ID_S3_ALL, pol("office-fence", st("Deny", "*", "*", {"NotIpAddress": {"aws:SourceIp": "203.0.113.0/24"}}))]},
     req("s3:GetObject", k(), **{"aws:SourceIp": "203.0.113.20"}), "allow")

# The analyst role used on the bench's request tester and by the anti-lever count.
ANALYST = {
    "identity": [
        pol("analyst-lake-read",
            st("Allow", ["s3:GetObject", "s3:ListBucket"], [LAKE, LAKE + "/curated/*"], sid="ReadCurated"),
            st("Allow", ["athena:StartQueryExecution", "athena:GetQueryResults", "glue:GetTable", "glue:GetDatabase", "glue:GetPartitions"], "*", sid="QueryLake"),
            st("Allow", "s3:PutObject", "arn:aws:s3:::acme-athena-results/*", sid="WriteResults")),
        pol("guardrails",
            st("Deny", "s3:*", [LAKE, LAKE + "/*"], {"Bool": {"aws:SecureTransport": "false"}}, sid="DenyHttp"),
            st("Deny", ["s3:DeleteBucket", "s3:PutBucketPolicy"], "*", sid="KeepTheLake")),
    ]
}
UNIVERSE = [
    ["s3:GetObject", LAKE + "/curated/trips/2024-01.parquet"],
    ["s3:ListBucket", LAKE],
    ["s3:GetObject", LAKE + "/raw/trips/2024-01.csv"],
    ["s3:PutObject", LAKE + "/curated/trips/2024-01.parquet"],
    ["s3:DeleteObject", LAKE + "/curated/trips/2024-01.parquet"],
    ["s3:PutObject", "arn:aws:s3:::acme-athena-results/q1.csv"],
    ["s3:DeleteBucket", LAKE],
    ["s3:PutBucketPolicy", LAKE],
    ["athena:StartQueryExecution", f"arn:aws:athena:us-east-1:{ACCT}:workgroup/primary"],
    ["athena:GetQueryResults", f"arn:aws:athena:us-east-1:{ACCT}:workgroup/primary"],
    ["glue:GetTable", f"arn:aws:glue:us-east-1:{ACCT}:table/lake/trips"],
    ["glue:GetPartitions", f"arn:aws:glue:us-east-1:{ACCT}:table/lake/trips"],
    ["glue:DeleteTable", f"arn:aws:glue:us-east-1:{ACCT}:table/lake/trips"],
    ["glue:CreateCrawler", f"arn:aws:glue:us-east-1:{ACCT}:crawler/new"],
    ["lambda:InvokeFunction", f"arn:aws:lambda:us-east-1:{ACCT}:function:ingest"],
    ["lambda:UpdateFunctionCode", f"arn:aws:lambda:us-east-1:{ACCT}:function:ingest"],
    ["iam:CreateUser", f"arn:aws:iam::{ACCT}:user/eve"],
    ["iam:AttachUserPolicy", f"arn:aws:iam::{ACCT}:user/ana"],
    ["iam:CreateAccessKey", f"arn:aws:iam::{ACCT}:user/ana"],
    ["redshift-serverless:CreateWorkgroup", f"arn:aws:redshift-serverless:us-east-1:{ACCT}:workgroup/new"],
    ["bedrock:InvokeModel", "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"],
    ["ec2:RunInstances", f"arn:aws:ec2:us-east-1:{ACCT}:instance/*"],
    ["kms:Decrypt", f"arn:aws:kms:us-east-1:{ACCT}:key/1234abcd"],
    ["s3:GetObject", "arn:aws:s3:::someone-elses-bucket/secret.csv"],
]
UNIVERSE_CTX = {"aws:SecureTransport": "true", "aws:SourceIp": "203.0.113.10"}

data = {"user": USER, "cases": C, "analyst": ANALYST, "universe": UNIVERSE, "universe_ctx": UNIVERSE_CTX}
json.dump(data, open(os.path.join(REPO, "materials", "iam-cases.json"), "w"), indent=1)
with open(os.path.join(REPO, "assets", "aws-iam-cases.js"), "w") as f:
    f.write("/* generated by materials/build-iam-cases.py with json.dumps; do not edit by hand */\n")
    f.write("window.AWS_IAM_CASES = " + json.dumps(data, separators=(",", ":")) + ";\n")
print(len(C), "cases;", len(UNIVERSE), "actions in the universe")
