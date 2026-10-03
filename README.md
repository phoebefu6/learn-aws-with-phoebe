# AWS for Data & AI Teams - learn-aws-with-phoebe

Fourteen 45-minute sessions on AWS for data and AI teams, by Phoebe Fu.

- **Leader track (6 sessions, no code, no account):** what AWS is to a data team, S3 as the lake, IAM as AWS implements it, compute versus serverless, the bill you did not plan, and a data platform on one page.
- **Analyst track (8 sessions, Python on a laptop):** boto3 against moto (a local mock of the AWS API) and DuckDB as the Athena stand-in, on 100,000 real NYC TLC yellow taxi trips (January 2024). Ends in a bench that evaluates IAM policies with AWS's documented logic, checked against 36 cases from the docs, and prices queries from the AWS Price List (us-east-1, retrieved 2026-10-03).

Open `index.html`, or the published site at https://phoebefu6.github.io/learn-aws-with-phoebe/.

## What is shipped

- `courses/` - the 14 session pages.
- `assets/aws-iam.js` - the policy evaluator (browser and node); `aws-cost.js` - the cost engine; `aws-bench.js` - the bench UI; `aws-sample.js` and `aws-iam-cases.js` - generated data.
- `data/yellow_tripdata_2024-01_sample.parquet` - the 100,000-row seeded sample. Source: NYC Taxi and Limousine Commission, TLC Trip Record Data. The TLC states it makes no representations as to the accuracy of the data.

## Reproduce the numbers

Verified with Python 3.11, moto 5.2.3, boto3 1.43.108, duckdb 1.5.6, pyarrow 25.0.1, node 22.

```
python3 materials/iam_eval.py                    # IAM canon (Python port)
node materials/run-iam-node.js                   # IAM canon (browser engine in node)
python3 materials/aws_reference.py               # cost canon (Python)
node materials/compare-cost.js                   # cost canon (browser engine in node)
```

Prices change. Re-verify every price against the AWS Price List before relying on it.
