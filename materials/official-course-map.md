# learn-aws-with-phoebe - official course map (source of truth for every page)

Title: **AWS for Data & AI Teams**. Bucket deng, difficulty 2, audience both, two tracks:
Leader a1-a6 (no code, no account) and Analyst b1-b8 (Python, runs locally against moto and DuckDB;
an optional real Free Tier path on each page). Built 2026-10-03. Region for every price: us-east-1.

Evidence tiers: **[source]** read at source on 2026-10-03 (quote + URL in `sources-aws-docs.md`, or
in the IAM section below, read by the course lead); **[pricelist]** read from the AWS Price List bulk
API JSON on 2026-10-03 (`prices-us-east-1.json`, with SKU and publicationDate); **[measured]** computed
in this build from real files or real code runs (scripts in `materials/`); **[modelled]** an
assumption-driven calculation, always labelled on the page; **[constructed]** an invented example.
Never quote a number that is not in this file.

Re-verify before delivery: every price (Price List changes without notice), the Free Tier terms, the
Lambda quota page, Bedrock model availability, and the Regions/AZ count.

---

## 1. Seams (link, never teach)

| Topic | Owner course | URL |
|---|---|---|
| Warehouse modelling (facts, dimensions, SCDs, marts) | learn-data-warehouse | https://phoebefu6.github.io/learn-data-warehouse-with-phoebe/ |
| Pipelines, ingestion, batch transformation | learn-data-engineering | https://phoebefu6.github.io/learn-data-engineering-with-phoebe/ |
| Scheduling and orchestration (Airflow etc.) | learn-data-orchestration | https://phoebefu6.github.io/learn-data-orchestration-with-phoebe/ |
| Access-control CONCEPTS: RBAC, ABAC, least privilege as a principle, access reviews | learn-data-access-control | https://phoebefu6.github.io/learn-data-access-control-with-phoebe/ |
| MLOps tooling | learn-dataops | https://phoebefu6.github.io/learn-dataops-with-phoebe/ |
| GPU and inference infrastructure; file formats in depth ("Cheap bytes, expensive reads") | learn-ai-infra | https://phoebefu6.github.io/learn-ai-infra-with-phoebe/ |
| Streaming (Kinesis, Kafka, MSK) | learn-streaming-data | https://phoebefu6.github.io/learn-streaming-data-with-phoebe/ |
| Claude on Bedrock specifics | learn-claude (session 68, Bedrock and Vertex) | https://phoebefu6.github.io/learn-claude-with-phoebe/courses/68-bedrock-vertex.html |

This course teaches IAM **as AWS implements it** (policy JSON, evaluation order, conditions), never
RBAC/ABAC theory. It teaches S3/Athena layout **as a bill**, never file-format internals.

## 2. Not covered (say so honestly; self-study pointers only)

EC2 instance families and networking (VPC, subnets, security groups, PrivateLink) beyond one sentence;
EMR, SageMaker, Kinesis, MSK, DynamoDB, RDS, Lake Formation permissions, Iceberg tables, KMS key
policies, Organizations account design beyond SCPs, cross-account access, role sessions and session
policies, RCPs, Savings Plans and Reserved Instances, the AWS certification syllabi. Certificates and
AWS Skill Builder courses stay official.

## 3. Verified facts (use only these)

### 3.1 Platform basics
- 39 Regions, 124 Availability Zones, plans for 7 more AZs and 2 more Regions (Saudi Arabia, Chile). [source] aws.amazon.com/about-aws/global-infrastructure
- "An AWS Region is a physical location in the world where we have multiple Availability Zones." AZs "consist of one or more discrete data centers, each with redundant power, networking, and connectivity, housed in separate facilities." [source] AWS overview whitepaper
- Shared responsibility: security "of" the cloud (AWS) versus security "in" the cloud (customer); customer responsibility "will be determined by the AWS Cloud services that a customer selects." [source]
- Free Tier (as of 2026-10-03): new accounts get $100 in credits at once and can earn up to $100 more, "up to $200 over 6 months"; the account "closes on its own 6 months after you open it or when your credits run out"; "You won't be charged unless you convert to a Paid plan." Payment card: "No. A payment method isn't required to sign up for most new customers", but "In some cases, we may request additional information, such as a payment method". 30+ services always free within monthly limits. [source] aws.amazon.com/free and free-tier FAQs
  - PAGE RULE: the optional real-account path on analyst pages is labelled "needs an AWS account; AWS says most new customers are not asked for a card on the Free plan, some are, and a Paid plan needs one". This corrects the brief's assumption that a card is always required.
- Well-Architected Data Analytics Lens: published December 22, 2023 (last major update; first published May 20, 2020). Six pillars. BP 11.1 "Decoupling storage from compute allows you to manage the cost of storage and compute separately"; BP 10.4 partitioning "a full table scan is avoided"; BP 7.1 central catalog "an integral part of data governance"; BP 5.2 least privilege "giving only enough access for systems to do the job"; BP 13.1 "use Amazon S3 Lifecycle configurations to expire data automatically"; BP 13.1.6 "Using Parquet over CSV format can reduce storage costs significantly." [source] Teach that the lens is almost three years old.

### 3.2 S3
- Storage class table (durability 11 nines for all but RRS; availability; AZs; minimum duration; minimum billable size): Standard 99.99%, >=3 AZ, none, none; Standard-IA 99.9%, >=3, 30 days, 128 KB; Intelligent-Tiering 99.9%, >=3, none, none; One Zone-IA 99.5%, 1 AZ, 30 days, 128 KB; Express One Zone 99.95%, 1 AZ; Glacier Instant Retrieval 99.9%, 90 days, 128 KB; Glacier Flexible Retrieval 90 days; Deep Archive 180 days. [source]
- One Zone-IA "is not resilient to the physical loss of the Availability Zone". [source]
- Intelligent-Tiering: moves objects not accessed for 30 consecutive days to Infrequent Access, 90 days to Archive Instant Access; no retrieval fees; objects under 128 KB not monitored; monitoring fee $0.0025 per 1,000 objects a month. [source]
- Retrieval: Instant Retrieval milliseconds; Flexible minutes to 12 hours; Deep Archive 9 to 48 hours ("within 12 hours" standard, "within 48 hours" bulk). [source]
- Lifecycle: transition and expiration actions; waterfall model; Deep Archive "can go only one way"; since September 2024 objects under 128 KB are not transitioned by default; early transition is charged for the rest of the minimum duration. A "30 days before Standard-IA" HARD RULE could NOT be verified: teach only the 30-day minimum charge and the example rule "Transition objects to the S3 Standard-IA storage class 30 days after creation." [source]
- Performance: "at least 3,500 PUT/COPY/POST/DELETE or 5,500 GET/HEAD requests per second per partitioned Amazon S3 prefix"; no limit on prefixes. [source]
- Consistency: "strong read-after-write consistency for PUT and DELETE requests of objects ... in all AWS Regions"; bucket configurations eventually consistent. [source]
- Data transfer in from the internet is free; 100 GB a month of transfer out to the internet free, aggregated. [source]
- Prices, us-east-1, per GB-month [pricelist, S3 offer published 2026-09-28; Deep Archive offer 2026-09-11]: Standard $0.023 first 50 TB, $0.022 next 450 TB, $0.021 over 500 TB; Intelligent-Tiering frequent $0.023; Standard-IA $0.0125; One Zone-IA $0.01; Glacier Instant Retrieval $0.004; Glacier Flexible (Amazon Glacier) $0.0036; Deep Archive $0.00099. Requests: PUT/COPY/POST/LIST $0.005 per 1,000; GET and other $0.0004 per 1,000. Standard-IA retrieval $0.01 per GB.

### 3.3 IAM (read at source by the course lead, 2026-10-03)
Pages: "Policy evaluation logic"; "How AWS enforcement code logic evaluates requests to allow or deny access"; "Condition operators"; "Conditions with multiple context keys or values"; "Policy elements: Action", "Resource", "NotAction"; IAM best practices.
- "By default, all requests are implicitly denied with the exception of the AWS account root user, which has full access." "An explicit deny overrides an explicit allow."
- Order: Deny evaluation across SCPs, RCPs, resource-based, identity-based, boundaries, session policies (any explicit Deny = final Deny) -> RCPs -> SCPs (no Allow = Deny) -> resource-based policies -> identity-based (no Allow = implicit Deny) -> permissions boundary (no Allow = Deny) -> session policies (not a session principal = Allow).
- Same account: identity + resource-based permissions are a UNION; identity + boundary is an INTERSECTION; identity + SCP must both allow.
- Resource-based policies that grant permissions to an IAM user ARN "are not limited by an implicit deny in an identity-based policy or permissions boundary."
- Action names: "The prefix and the action name are case insensitive"; `*` and `?` wildcards; `iam:*AccessKey*` example.
- Resource: wildcards within ARN segments; `bucket/*/test/*` matches `bucket/1/2/test/3/object.jpg` and not `bucket/1-test/object.jpg`; "In the Resource element, the IAM user name is case sensitive."
- Conditions: missing key -> "the values do not match and the condition is false" (negated operators true); multiple operators AND, multiple keys AND, multiple values OR, negated multiple values NOR; IpAddress without prefix = /32; StringEquals "Exact matching, case sensitive"; Bool aws:SecureTransport examples.
- NotAction with Allow: "allows users to access every action in every AWS service except for IAM"; "could result in granting users more permissions than you intended."
- Best practices: "grant only the permissions required to perform a task"; temporary credentials and roles over long-term access keys; IAM Access Analyzer generates least-privilege policies from activity; MFA, passkeys and security keys. [source]
- Bedrock has no `bedrock:Converse` IAM action: the AWS service reference JSON lists 262 Bedrock actions, with InvokeModel and InvokeModelWithResponseStream for inference. [source, servicereference.us-east-1.amazonaws.com/v1/bedrock/bedrock.json]

### 3.4 Glue Data Catalog and Athena
- Catalog "stores metadata about your organization's data sets ... an index to the location, schema, and runtime metrics"; organised into databases and tables; populated by crawlers; used by Lake Formation, Athena, Redshift Spectrum, EMR. Partition projection: "Athena calculates partition values and locations using the table properties"; usable only through Athena. [source]
- Glue prices [pricelist]: Data Catalog storage $1 per 100,000 objects a month beyond the free tier ($0.00001 per object); requests $1 per million; crawler $0.44 per DPU-hour; ETL $0.44 per DPU-hour (Glue 6.0+ Gen2 $0.308; Flex Gen2 $0.203).
- Athena: $5.00 per TB scanned [pricelist, offer published 2026-09-11]; "rounded up to the nearest megabyte, with a 10 MB minimum per query"; no charge for DDL or failed queries; cancelled queries billed for data scanned; "save up to 90% per query ... by compressing, partitioning, and converting your data into columnar formats"; "you pay for the number of bytes scanned before decompression"; "Datasets that consist of many small files result in poor overall query performance"; "For small files, the overhead of the columnar file format outweighs the benefits"; 128 MB is the default Parquet ROW GROUP size, NOT a file-size target (no file-size number at source); too many partition keys fragment data. [source]

### 3.5 Compute
- Lambda quotas: timeout 900 s; memory 128 MB to 10,240 MB; one vCPU at 1,769 MB; /tmp 512 MB to 10,240 MB; zip 50 MB zipped / 250 MB unzipped; container image 10 GB; payload 6 MB synchronous, **1 MB asynchronous** (not the older 256 KB), 200 MB streamed; 1,000 concurrent executions default (new accounts start lower). Billing per 1 ms; free tier 1M requests and 400,000 GB-seconds a month. [source]
- Lambda prices [pricelist]: $0.20 per 1M requests; $0.0000166667 per GB-second (first 6 billion GB-s), then $0.000015, then $0.0000133334 (x86).
- Fargate [pricelist, us-east-1]: $0.04048 per vCPU-hour; $0.004445 per GB-hour (x86).
- Redshift Serverless: one RPU = 16 GB memory; default base 128 RPU; base 4 to 512 (1,024 in five Regions incl. us-east-1); billed per second with a 60-second minimum; no compute charge when no queries run; storage billed separately; open connection pools can generate cost; cancelled queries billed for time run. [source] Prices [pricelist]: $0.375 per RPU-hour; managed storage $0.024 per GB-month.

### 3.6 Bedrock
- "a fully managed service that provides secure, enterprise-grade access to high-performing foundation models"; "supports 100+ foundation models". The overview no longer says "single API". Knowledge Bases (RAG), Guardrails, model customization (supervised fine-tuning, reinforcement fine-tuning, distillation), batch inference ("submit multiple prompts and generate responses asynchronously"; not for provisioned models). Bedrock Agents (now "Agents Classic") "is no longer open to new customers"; successor AgentCore. [source]
- Pricing: batch "at a 50% lower price compared to on-demand"; Flex tier 50% discount, Priority 75% premium. [source] Nova Micro on-demand $0.000035 per 1K input tokens, $0.00014 per 1K output; batch $0.0000175 / $0.00007; Nova Lite $0.00006 / $0.00024. [pricelist, Bedrock offer published 2026-10-03]
- Data: providers "don't have access to Amazon Bedrock logs or to customer prompts and completions"; "your content is not used to improve the base models and is not shared with any model providers"; CAVEAT: for some models prompts and completions "are retained within the AWS boundary for up to 30 days and may be reviewed by AWS". [source] Teach both.

### 3.7 Cost tooling
- AWS Budgets alerts on actual and forecasted spend; updated up to three times a day; notifications can lag. Cost allocation tags must be activated before they appear on billing reports; up to 24 h to appear and up to 24 h to activate. [source]

### 3.8 The dataset
- NYC TLC Trip Record Data, yellow taxi, January 2024 (`yellow_tripdata_2024-01.parquet`, 49,961,641 bytes, sha256 c4d59da7...0510, 2,964,624 rows, 2,964,606 with a January 2024 pickup). Published monthly with a two-month delay, stored as Parquet; disclaimer: "The trip data was not created by the TLC, and TLC makes no representations as to the accuracy of these data." Data dictionary: https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf [source]
- Shipped sample: `data/yellow_tripdata_2024-01_sample.parquet`, 100,000 rows drawn with numpy seed 20240101, sorted by pickup, 2,776,217 bytes, 19 columns. [measured]

## 4. Canon numbers (measured or computed; node and Python agree exactly)

### 4.1 Layouts of the 100,000-row sample (DuckDB 1.5.6, Snappy) [measured]
- CSV one file 10,095,345 B · Parquet one file 2,387,037 B (23.6% of the CSV) · Parquet partitioned by pickup day 3,023,334 B in 31 files (29.9%; files of 73,785 to 113,419 B holding 2,310 to 3,897 trips each: the small-files overhead is visible).
- Two columns (payment_type, tip_amount) in the single Parquet file: 172,585 B of column chunks; plus 24,832 B of file overhead = 197,417 B.
- Moto upload: raw/ 1 object 10,095,345 B; curated/nyc_taxi_flat/ 1 object 2,387,037 B; curated/nyc_taxi/ 31 objects 3,023,334 B; key `curated/nyc_taxi/pickup_date=2024-01-15/data_0.parquet`.

### 4.2 Bytes scanned per query (sample) and cost at 1,024 GB of CSV, 100 queries a day [measured bytes; modelled scaling]
| Query | CSV | Parquet | Partitioned |
|---|---|---|---|
| Q1 every column, month | 10,095,345 (100%) $5.00/q $15,000/mo | 2,387,037 (23.64%) $1.18/q $3,547/mo | 3,023,334 (29.95%) $1.50/q $4,492/mo |
| Q2 avg tip by payment type, month | 10,095,345 $5.00 $15,000 | 197,417 (1.96%) $0.10/q $293/mo | 381,251 (3.78%) $0.19/q $566/mo |
| Q3 fares on 15 January | 10,095,345 $5.00 $15,000 | 822,585 (8.15%) $0.41/q $1,222/mo | 8,968 (0.09%) $0.00/q $13/mo |
| Q4 pickups per zone, 15-21 January | 10,095,345 $5.00 $15,000 | 760,406 (7.53%) $0.38/q $1,130/mo | 58,887 (0.58%) $0.03/q $88/mo |
- At sample size every query bills the 10 MB minimum: $0.000048. [measured]
- Partitioned LOSES on whole-month queries (Q1, Q2): 31 small files carry 31 footers. Linear scaling overstates this at large sizes; say so.
- Storage per month at 1,024 GB CSV-equivalent: CSV 1,024.0 GB Standard $23.55, Standard-IA $12.80, Deep Archive $1.01; Parquet 242.1 GB $5.57 / $3.03 / $0.24; partitioned 306.7 GB $7.05 / $3.83 / $0.30. Headline: storing a terabyte costs $23.55 a month; scanning it 100 times a day as CSV costs $15,000. [computed]
- Answers are identical across layouts (DuckDB): Q2 payment_type 1 avg tip 4.1507 on 78,236 trips; Q3 2,591 trips, fares $50,935.89; Q4 top zones 161 (1,088), 132 (1,086), 237 (1,085). [measured]

### 4.3 IAM evaluator [measured; node and Python agree on 192 verdicts]
- 36 test cases, each tied to a doc sentence: 36/36 pass, 16 of 36 requests allowed.
- Break "an Allow beats a Deny": 30/36 pass, **6 fail** (T04, T20, T28, T33, T34, T35: every explicit-deny case that also has an Allow).
- Break "a missing key matches": 34/36, **2 fail** (T16 tag missing would allow; T22 HTTPS deny with key absent would deny).
- Anti-lever (`"Action": "*", "Resource": "*"` Allow added to every case): allowed 16 -> **28 of 36**; only 24/36 still match the docs' verdicts (12 implicit denies turned to allows).
- The analyst role on 24 data-team actions: **7 of 24 allowed -> 22 of 24** with the wildcard; the 2 explicit Denies (DeleteBucket, PutBucketPolicy) still hold. The demo request s3:PutObject into curated/ goes implicit Deny -> Allow.

### 4.4 Build-along outputs (materials/buildalong/outputs/*.txt) [measured]
- b2 moto with IAM enforced: GetObject curated ALLOWED; GetObject raw AccessDenied; PutObject curated AccessDenied; DeleteBucket AccessDenied.
- b3 Glue: lake.nyc_taxi, 19 columns, partition key pickup_date, 31 partitions; 15-21 January needs 7 of 31.
- b5 handler: 2024-01-15 CSV 262,544 B -> Parquet 81,729 B (timing varies by laptop). Moto accepted a 901 s timeout that real Lambda rejects (900 s max): a mock is not a quota check. Lambda one file a day, 20 s at 1 GB: $0.01/month; one a minute: $14.41/month; Fargate 1 vCPU 2 GB always on: $36.04/month. [modelled workloads, real prices]
- b6 [modelled]: Athena Q2-style query, 20 GB scanned: 10/day $34.87, 50 $152.05, 100 $298.54, 300 $884.47, 1,000 $2,935.26 a month (incl. $5.57 storage). Redshift Serverless 8 RPU busy 1 h/day $95.81/mo, 4 h/day $365.81/mo (incl. managed storage). Break-even about 31 and 123 queries a day. 60-second minimum: a 5-second query on an idle 8 RPU warehouse bills $0.0500, not $0.0042.
- b7: Converse request validated by botocore's schema, stubbed reply labelled STUBBED; a malformed request raises ParamValidationError; 1,000,000 notes x 120 input + 8 output tokens on Nova Micro: on-demand $5.32, batch $2.66 [modelled volumes]; least privilege is bedrock:InvokeModel on one foundation-model ARN.

Versions installed and used: moto 5.2.3, boto3 1.43.108, botocore 1.43.108, duckdb 1.5.6, pyarrow 25.0.1, pandas 3.0.6, Python 3.11.11, node 22.6.0.

## 5. Per-session coverage

### Leader (no code, no account)
- **a1 What AWS is to a data team** - Regions/AZs (39/124), shared responsibility, the five services a data team actually touches (S3, IAM, Glue, Athena, Lambda) plus Redshift and Bedrock; storage decoupled from compute (Lens BP 11.1); the Free plan (credits, 6 months, card usually not required). Figure: the data platform as storage + catalog + engines + identity around it. Build-along: map your team's current tools onto the AWS boxes.
- **a2 S3 is the lake** - buckets, keys, prefixes (no folders), storage classes and minimums, lifecycle waterfall, raw/curated zones, 11 nines vs availability; 3,500/5,500 per prefix. Canon: $23.55 to store a terabyte. Build-along: a lifecycle policy on paper for raw/curated/archive.
- **a3 Who can touch what** - IAM users, roles, policies; implicit deny, explicit deny wins; identity + resource union, boundary intersection, SCP ceiling; temporary credentials over access keys; Access Analyzer. Canon: wildcard 7 -> 22 of 24. Seam: RBAC/ABAC concepts in learn-data-access-control. Build-along: the access matrix for three roles.
- **a4 Compute or serverless** - Lambda limits, Fargate always-on, Redshift Serverless per-second with 60 s minimum, Athena per byte; Canon: Lambda $0.01 vs $14.41 vs Fargate $36.04; the four billing meters (time, bytes, requests, storage). Build-along: classify five jobs by meter.
- **a5 The bill you did not plan** - Athena CSV $15,000/month vs partitioned $88; storage cheap, scanning expensive; small files; Redshift idle minimum and open connection pools; Budgets (actual + forecast, up to three refreshes a day), cost allocation tags need activating; data transfer out. Build-along: a five-line cost guardrail plan.
- **a6 A data platform on one page** - capstone: S3 zones + Glue catalog + Athena + Lambda ingest + IAM roles + Budgets + Bedrock for AI; Lens pillars and its 2023 date; the six questions to ask any AWS data proposal. Build-along: the one-page platform diagram.

### Analyst (Python, local)
- **b1 S3 layout and Parquet** - script b1_layout.py; three layouts, keys, moto upload, parquet_metadata column chunks; seam: format internals in learn-ai-infra.
- **b2 IAM policies as code** - b2_policies.py, moto with IAM enforcement (set_initial_no_auth_action_count), policy JSON, explicit deny guardrails, why moto's enforcement is a teaching mock and the evaluator in b8 follows the docs.
- **b3 The Glue Data Catalog** - b3_catalog.py; table, schema, partition keys, partitions; crawler vs explicit DDL; partition projection; catalog pricing.
- **b4 Athena: pay per byte scanned** - b4_athena.py; Q2-Q4 bytes; 10 MB minimum; small files; compression billed before decompression.
- **b5 Lambda or a container** - b5_lambda.py; handler on moto S3; quotas; the 901 s lesson; Lambda vs Fargate cost.
- **b6 Redshift or Athena** - b6_redshift_or_athena.py; bytes vs time; break-even 31 / 123 queries a day [modelled]; 60 s minimum; seam: warehouse modelling in learn-data-warehouse.
- **b7 Bedrock for AI teams** - b7_bedrock.py; Converse schema check with Stubber; batch vs on-demand; least-privilege InvokeModel; data retention caveat; Agents Classic closed; seam: learn-claude session 68, learn-ai-infra.
- **b8 The IAM and cost bench** - the computed bench (section 4.2, 4.3).

## 6. Citation appendix (short forms used on pages)
- AWS IAM User Guide, "Policy evaluation logic" and "How AWS enforcement code logic evaluates requests to allow or deny access", read 2026-10-03.
- AWS IAM User Guide, "Condition operators"; "Conditions with multiple context keys or values"; "Policy elements: Action / Resource / NotAction"; "Security best practices in IAM".
- Amazon S3 User Guide, "Understanding and managing Amazon S3 storage classes"; "Managing the lifecycle of objects"; "Best practices design patterns: optimizing Amazon S3 performance".
- AWS Glue Developer Guide, "AWS Glue Data Catalog". Amazon Athena User Guide, "Partitioning data", "Columnar storage formats", "Optimize data"; Athena pricing page.
- AWS Lambda Developer Guide, "Lambda quotas"; Lambda pricing page.
- Amazon Redshift Management Guide, "Compute capacity for Amazon Redshift Serverless", "Billing for Amazon Redshift Serverless".
- Amazon Bedrock User Guide, "What is Amazon Bedrock?", "Data protection", "Data retention", "Batch inference"; Bedrock pricing and FAQs; AWS service reference JSON for Bedrock.
- AWS Well-Architected Data Analytics Lens (December 22, 2023).
- AWS Price List bulk API, us-east-1 offers for AmazonS3, AmazonS3GlacierDeepArchive, AmazonAthena, AWSLambda, AmazonECS, AmazonRedshift, AWSGlue, AmazonBedrock, retrieved 2026-10-03.
- NYC Taxi and Limousine Commission, "TLC Trip Record Data", yellow taxi January 2024.

## 7. Derived numbers (computed from rows above; pages may quote these)
- 1,024 GB for a month: Glacier Instant Retrieval $4.10 (1,024 x $0.004), Glacier Flexible Retrieval $3.69 (1,024 x $0.0036). [computed]
- Lambda per invocation at 20 s and 1 GB: $0.000333534 (20 x $0.0000166667 + $0.0000002); Fargate 1 vCPU 2 GB always on $36.04/month; crossover about 108,000 invocations a month. [computed, modelled workload]
- Lambda one file a minute (43,200 runs, 864,000 GB-s) with the free tier applied (1M requests, 400,000 GB-s free): 464,000 billed GB-s x $0.0000166667 = about $7.73 a month. [computed, modelled workload; free tier terms re-verify]
