# AWS source facts - read at source

Read on 2026-10-03. Every fact below was read on the live page at the URL given. Quotes are verbatim
except that AWS's en dashes have been normalised to hyphens (house rule: no em or en dashes).
Tier tag on every line: [read-at-source]. Prices that the AWS pricing pages render from a JSON feed
were read from that feed (the same data the page displays) and are marked "(pricing feed)".

---

## 1. S3 storage classes

Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html (comparison table "Comparing the Amazon S3 storage classes")

| Class | Durability | Availability | AZs | Min storage duration | Min billable object size |
|---|---|---|---|---|---|
| S3 Standard | 99.999999999% | 99.99% | >= 3 | None | None |
| S3 Standard-IA | 99.999999999% | 99.9% | >= 3 | 30 days | 128 KB |
| S3 Intelligent-Tiering | 99.999999999% | 99.9% | >= 3 | None | None |
| S3 One Zone-IA | 99.999999999% | 99.5% | 1 | 30 days | 128 KB |
| S3 Express One Zone | 99.999999999% | 99.95% | 1 | None | None |
| S3 Glacier Instant Retrieval | 99.999999999% | 99.9% | >= 3 | 90 days | 128 KB |
| S3 Glacier Flexible Retrieval | 99.999999999% | 99.99% (after you restore objects) | >= 3 | 90 days | NA (40 KB metadata overhead) |
| S3 Glacier Deep Archive | 99.999999999% | 99.99% (after you restore objects) | >= 3 | 180 days | NA (40 KB metadata overhead) |
| Reduced Redundancy (not recommended) | 99.99% | 99.99% | >= 3 | None | None |

All rows above [read-at-source]. Minimum durations 30 / 30 / 90 / 90 / 180 CONFIRMED.

- Default class: "If you don't specify the storage class when you upload an object, Amazon S3 assigns the S3 Standard storage class." [read-at-source]
- 128 KB billing floor + 30 days for IA: "If an object is less than 128 KB, Amazon S3 charges you for 128 KB." and "If you delete an object before the end of the 30-day minimum storage duration period, you are charged for 30 days." [read-at-source]
- One Zone-IA caveat: "the data is not resilient to the physical loss of the Availability Zone resulting from disasters, such as earthquakes and floods." [read-at-source]
- Resilience exception: "all of the storage classes except for S3 One Zone-IA (ONEZONE_IA) and S3 Express One Zone (EXPRESS_ONEZONE) are designed to be resilient to the physical loss of an Availability Zone" [read-at-source]
- Intelligent-Tiering fee: "For a small monthly object monitoring and automation fee, S3 Intelligent-Tiering monitors access patterns and automatically moves objects" [read-at-source]
- Intelligent-Tiering, no retrieval fees: "There are no retrieval fees for S3 Intelligent-Tiering." [read-at-source]
- Intelligent-Tiering 30-day move: "S3 Intelligent-Tiering moves objects that have not been accessed in 30 consecutive days to the Infrequent Access tier." [read-at-source]
- Intelligent-Tiering 90-day move: "any existing objects that have not been accessed for 90 consecutive days are automatically moved to the Archive Instant Access tier." [read-at-source]
- Intelligent-Tiering small objects: "If the size of an object is less than 128 KB, it is not monitored and not eligible for auto-tiering." [read-at-source]
- Intelligent-Tiering availability/durability: "S3 Intelligent-Tiering is designed for 99.9% availability and 99.999999999% durability." [read-at-source]

Intelligent-Tiering fee amount. Source: https://aws.amazon.com/s3/pricing/
- Page text: "You pay a monthly monitoring and automation charge per object stored in the S3 Intelligent-Tiering storage class" [read-at-source]
- Price row label: "Monitoring and Automation, All Storage / Month (Objects > 128 KB)" ... "per 1,000 objects" [read-at-source]
- US East (N. Virginia) value: 0.0000025 USD per object per month, i.e. $0.0025 per 1,000 objects (pricing feed) [read-at-source]

Retrieval times. Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/glacier-storage-classes.html
- Average retrieval, table: Instant Retrieval "Milliseconds"; Flexible Retrieval "Minutes to 12 hours"; Deep Archive "9 to 48 hours" [read-at-source]
- Flexible, Expedited: "Typically restores the object in 1-5 minutes." [read-at-source]
- Flexible, Standard: "Typically restores the object in 3-5 hours" [read-at-source]
- Flexible, Bulk: "Typically restores the object within 5-12 hours. Bulk retrievals are free." [read-at-source]
- Deep Archive, Standard: "Typically restores the object within 12 hours" [read-at-source]
- Deep Archive, Bulk: "Typically restores the object within 48 hours at a fraction of the cost of the Standard retrieval tier." [read-at-source]
- Deep Archive cost position: "S3 Glacier Deep Archive is the lowest-cost storage option in AWS." [read-at-source]

## 2. S3 Lifecycle

Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html
- Transition actions: "These actions define when objects transition to another storage class." [read-at-source]
- Expiration actions: "These actions define when objects expire. Amazon S3 deletes expired objects on your behalf." [read-at-source]
- Applies to existing objects: "the configuration rules apply to both existing objects and objects that you add later." [read-at-source]
- Bucket policy cannot block it: "You can't use a bucket policy to prevent deletions or transitions by an S3 Lifecycle rule." [read-at-source]

Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-transition-general-considerations.html
- Waterfall: "Amazon S3 supports a waterfall model for transitioning between storage classes" [read-at-source]
- Supported transitions (summarised from the list on the page, each bullet read):
  - Standard -> Standard-IA, Intelligent-Tiering, One Zone-IA, Glacier IR, Glacier Flexible, Deep Archive
  - Standard-IA -> Intelligent-Tiering, One Zone-IA, Glacier IR, Glacier Flexible, Deep Archive
  - One Zone-IA -> Glacier Flexible, Deep Archive
  - Glacier IR -> Glacier Flexible, Deep Archive
  - Glacier Flexible -> Deep Archive
  [read-at-source]
- Deep Archive is one-way: "The transition of objects to the S3 Glacier Deep Archive storage class can go only one way." [read-at-source]
- Small objects: "Amazon S3 applies a default behavior to S3 Lifecycle configurations that prevents objects smaller than 128 KB from being transitioned to any storage class." [read-at-source]
- Date of that change: "Starting September 2024, the default behavior prevents objects smaller than 128 KB from being transitioned to any storage class." [read-at-source]
- Early-transition charge: "If you transition objects out of these storage classes before the minimum duration, you are charged for the remainder of that duration." [read-at-source]
- Worked example on page: Glacier IR has 90-day minimum, so a later Deep Archive transition "must occur after at least 94 days." [read-at-source]

Example of the 30-day pattern. Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-configuration-examples.html
- "Transition objects to the S3 Standard-IA storage class 30 days after creation." [read-at-source]

## 3. S3 performance and consistency

Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html
- "your application can achieve at least 3,500 PUT/COPY/POST/DELETE or 5,500 GET/HEAD requests per second per partitioned Amazon S3 prefix." [read-at-source]
- "There are no limits to the number of prefixes in a bucket." [read-at-source]
- "if you create 10 prefixes in an Amazon S3 bucket to parallelize reads, you could scale your read performance to 55,000 read requests per second." [read-at-source]
- "While Amazon S3 is scaling to your new higher request rate, you may see some 503 (Slow Down) errors." [read-at-source]

Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html (section "Amazon S3 data consistency model")
- "Amazon S3 provides strong read-after-write consistency for PUT and DELETE requests of objects in your Amazon S3 bucket in all AWS Regions." [read-at-source]
- "Bucket configurations have an eventual consistency model." [read-at-source]
- "Amazon S3 does not support object locking for concurrent writers." [read-at-source]

## 4. IAM best practices

Source: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- Heading: "Apply least-privilege permissions" [read-at-source]
- Least privilege: "When you set permissions with IAM policies, grant only the permissions required to perform a task." [read-at-source]
- Human users: "Require your human users to use temporary credentials when accessing AWS." [read-at-source]
- Workloads heading: "Require workloads to use temporary credentials with IAM roles to access AWS" [read-at-source]
- Long-term keys: "Where possible, we recommend relying on temporary credentials instead of creating long-term credentials such as access keys." [read-at-source]
- Access Analyzer heading: "Use IAM Access Analyzer to generate least-privilege policies based on access activity" [read-at-source]
- Access Analyzer: "IAM Access Analyzer analyzes the services and actions that your IAM roles use, and then generates a fine-grained policy that you can use." [read-at-source]
- MFA: "for scenarios in which you need an IAM user or root user in your account, require MFA for additional security." [read-at-source]
- MFA type: "We recommend that you use phishing-resistant MFA such as passkeys and security keys wherever possible." [read-at-source]

## 5. IAM policy evaluation

Skipped by instruction (read by main thread).

## 6. Glue Data Catalog and Athena partition projection

Source: https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html
- "The AWS Glue Data Catalog is a centralized repository that stores metadata about your organization's data sets." [read-at-source]
- "It acts as an index to the location, schema, and runtime metrics of your data sources." [read-at-source]
- "This metadata is organized into databases and tables, similar to a traditional relational database catalog." [read-at-source]
- Crawler: "You can populate the Data Catalog using a crawler, which automatically scans your data sources and extracts metadata." [read-at-source]
- Schema: "The Data Catalog automatically captures and manages the schema of your data sources, including schema inference, evolution, and versioning." [read-at-source]
- Consumers: "The Data Catalog seamlessly integrates with other AWS services, such as AWS Lake Formation, Amazon Athena, Amazon Redshift Spectrum, and Amazon EMR." [read-at-source]

Source: https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html
- "In partition projection, Athena calculates partition values and locations using the table properties that you configure directly on your table in AWS Glue." [read-at-source]
- "Partition projection is usable only when the table is queried through Athena." [read-at-source]

## 7. Athena pricing and performance

Source: https://aws.amazon.com/athena/pricing/
- Price per TB, US East (N. Virginia): 5.00 USD per TB of data scanned (pricing feed; the page template reads "{price} per TB of data scanned") [read-at-source]
- Worked example on page: "(Price for 3 TB scanned is 3 * $5/TB = $15.)" [read-at-source]
- "You are charged for the number of bytes scanned per query, rounded up to the nearest megabyte, with a 10 MB minimum per query." [read-at-source]
- "There are no charges for Data Definition Language (DDL) statements like CREATE, ALTER, or DROP TABLE statements for managing partitions, or failed queries." [read-at-source]
- "Canceled queries are billed for the total amount of data scanned when the query is canceled." [read-at-source]
- "You can save up to 90% per query and get better performance by compressing, partitioning, and converting your data into columnar formats." [read-at-source]
- Page example: "There is a 3x savings from compression and 4x savings for reading only one column." [read-at-source]

Source: https://docs.aws.amazon.com/athena/latest/ug/partitions.html
- "By partitioning your data, you can restrict the amount of data scanned by each query, thus improving performance and reducing cost." [read-at-source]
- "If you query a partitioned table and specify the partition in the WHERE clause, Athena scans the data only from that partition." [read-at-source]

Source: https://docs.aws.amazon.com/athena/latest/ug/columnar-storage.html
- "Predicate pushdown in Parquet and ORC enables Athena queries to fetch only the blocks it needs, improving query performance." [read-at-source]
- Compression: "Compression by column, with compression algorithm selected for the column data type" [read-at-source]

Source: https://docs.aws.amazon.com/athena/latest/ug/performance-tuning-data-optimization-techniques.html
- Column projection: "Only the columns needed for the query are loaded" [read-at-source]
- Small files: "Datasets that consist of many small files result in poor overall query performance." [read-at-source]
- "loading a single bigger file from Amazon S3 is faster than loading the same records from many smaller files." [read-at-source]
- Columnar + small files: "For small files, the overhead of the columnar file format outweighs the benefits." [read-at-source]
- 128 MB figure (row groups, NOT a file-size target): "The default size for row groups is 128 MB, and for stripes, 64 MB." [read-at-source]
- Compression billing: "you pay for the number of bytes scanned before decompression." [read-at-source]
- Over-partitioning: "Having too many partition keys can result in fragmented datasets with too many files and files that are too small." [read-at-source]

## 8. Lambda quotas and pricing

Source: https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html
- Timeout: "900 seconds (15 minutes)." [read-at-source]
- Memory: "128 MB to 10,240 MB, in 1-MB increments." [read-at-source]
- One vCPU point: "At 1,769 MB, a function has the equivalent of one vCPU." [read-at-source]
- /tmp: "Between 512 MB and 10,240 MB, in 1-MB increments" [read-at-source]
- Zip package: "50 MB (zipped, when uploaded through the Lambda API or SDKs)." and "250 MB The maximum size of the contents of a deployment package, including layers and custom runtimes. (unzipped)" [read-at-source]
- Container image: "10 GB (maximum uncompressed image size, including all layers)" [read-at-source]
- Payload, synchronous: "6 MB each for request and response (synchronous)" [read-at-source]
- Payload, asynchronous: "1 MB (asynchronous)" [read-at-source]  NOTE: not the old 256 KB.
- Payload, streamed: "200 MB for each streamed response (synchronous)" [read-at-source]
- Concurrency: "Concurrent executions | 1,000 | Tens of thousands" (default quota, can be increased) [read-at-source]
- New-account caveat: "New AWS accounts have reduced concurrency and memory quotas for Lambda Functions and Lambda MicroVMs." [read-at-source]

Source: https://aws.amazon.com/lambda/pricing/
- Billing granularity: "Duration is calculated from the time your code begins executing until it returns or otherwise terminates, rounded up to the nearest 1ms" [read-at-source]
- Free tier: "The free tier includes one million requests and 400,000 GB-seconds per month." [read-at-source]
- Example rates on page: "The monthly request price is $0.20 per 1 million requests" and "The monthly compute price is $0.0000166667 per GB-s" (x86 example) [read-at-source]

## 9. Redshift Serverless

Source: https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-capacity.html
- RPU: "One RPU provides 16 GB of memory." [read-at-source]
- Default: "The default base capacity for Amazon Redshift Serverless is 128 RPUs." [read-at-source]
- Range: "You can adjust the Base capacity setting from 4 RPUs to 512 RPUs." [read-at-source]
- Steps: "You can set this value to 4 RPUs, or in units of 8 at or above 8 RPUs (8,16,24...512)." [read-at-source]
- Expanded max: "The maximum base RPUs available, 1024" ... in other Regions "the maximum base capacity is 512 RPUs." (1024 only in us-east-1, us-east-2, us-west-2, eu-west-1, eu-central-1) [read-at-source]
- 4 RPU limit: "Configurations of 4 base RPUs support managed storage capacity of up to 32 TB." [read-at-source]

Source: https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-billing-on-demand.html
- "When queries run, you're billed according to the capacity used in a given duration, in RPU hours on a per-second basis." [read-at-source]
- "When no queries are running, you aren't billed for compute capacity." [read-at-source]
- "You pay for the workloads you run in RPU-hours on a per-second basis, with a 60-second minimum charge." [read-at-source]
- Max capacity ceiling: "The top Max capacity setting is 5632 RPUs." [read-at-source]

Source: https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-billing.html
- "Storage is billed by GB / month. Storage billing is separate from billing for compute capacity." [read-at-source]
- "The minimum charge is for 60 seconds of resource usage, metered on a per-second basis." [read-at-source]
- Gotcha: "maintaining open connection pools can generate costs even when no actual user workloads are running." [read-at-source]
- Gotcha: "If you run a query and cancel it before it finishes, you are still billed for the time the query ran." [read-at-source]

## 10. Amazon Bedrock

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html
- "Amazon Bedrock is a fully managed service that provides secure, enterprise-grade access to high-performing foundation models from leading AI companies" [read-at-source]
- "Amazon Bedrock supports 100+ foundation models from industry-leading providers" [read-at-source]
- NOTE: the overview page no longer carries a "single API" phrase or a capabilities bullet list; capabilities below were each read on their own page.

Capabilities:
- Knowledge Bases / RAG (https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html): "RAG is a technique that uses information from data sources to improve the relevancy and accuracy of generated responses." [read-at-source]
- Guardrails (https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html): "Amazon Bedrock Guardrails provides configurable safeguards to help you build safe generative AI applications." [read-at-source]
- Agents (https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html): "Amazon Bedrock Agents (now Amazon Bedrock Agents Classic) is no longer open to new customers." Successor named: Amazon Bedrock AgentCore. [read-at-source]
- Customization (https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html): "Model customization is the process of providing training data to a model to improve its performance for specific use-cases." Methods listed: supervised fine-tuning, reinforcement fine-tuning, distillation. [read-at-source]
- Batch inference (https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html): "With batch inference, you can submit multiple prompts and generate responses asynchronously." [read-at-source]
- Batch limitation: "Batch inference isn't supported for provisioned models." [read-at-source]

Pricing. Source: https://aws.amazon.com/bedrock/pricing/
- Batch discount: "for batch inference at a 50% lower price compared to on-demand inference pricing." [read-at-source]
- Tiers: "Amazon Bedrock supports a variety of tiers including Standard, Flex, Priority, and Reserved tiers." [read-at-source]
- Tier pricing footnotes: "Flex tier pricing is at 50% discount to Standard tier pricing" and "Priority tier pricing is at 75% premium to Standard tier pricing" [read-at-source]
- Provisioned Throughput: page offers "Provisioned Throughput (PT) or On Demand (OD) pricing options" for custom models. [read-at-source]

Data privacy.
- https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html: model providers "don't have access to Amazon Bedrock logs or to customer prompts and completions." [read-at-source]
- https://aws.amazon.com/bedrock/faqs/: "AWS and the third-party model providers will not use any inputs to or outputs from Amazon Bedrock to train Amazon Nova, Amazon Titan, or any third-party models." [read-at-source]
- https://aws.amazon.com/bedrock/faqs/: "With Amazon Bedrock, your content is not used to improve the base models and is not shared with any model providers." [read-at-source]
- CAVEAT, https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html: some models require retention; for aws_review models prompts and completions "are retained within the AWS boundary for up to 30 days and may be reviewed by AWS" [read-at-source]

## 11. Well-Architected Data Analytics Lens

Source: https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/analytics-lens.html
- "Publication date: December 22, 2023" [read-at-source]
- Revisions (https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/document-revisions.html): latest entry "Major update" dated "December 22, 2023"; initial publication "May 20, 2020". No 2024-2026 revision listed. [read-at-source]
- Purpose: "a collection of customer-proven best practices for designing well-architected analytics workloads." [read-at-source]
- Pillars (from the lens TOC): Operational excellence, Security, Reliability, Performance efficiency, Cost optimization, Sustainability. [read-at-source]

Best practices:
- BP 11.1 Decouple storage from compute (https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/best-practice-11.1---decouple-storage-from-compute..html): "Decoupling storage from compute allows you to manage the cost of storage and compute separately" [read-at-source]
- BP 10.2 formats (https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/best-practice-10.2-choose-data-formatting-based-on-your-data-access-pattern..html): "Choosing the right format is a key step in the performance optimization of your analytics workloads." [read-at-source]
- BP 10.4 partitioning (https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/best-practice-10.4---partition-your-data-to-avoid-unnecessary-file-reads..html): "This means a full table scan is avoided, meaning faster performance and lower query cost." [read-at-source]
- BP 7.1 catalog (https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/best-practice-7.1---build-a-central-data-catalog-to-store-share-and-track-metadata-changes..html): "Building a central Data Catalog to store, share, and manage metadata across the organization is an integral part of data governance." [read-at-source]
- BP 5.2 least privilege (https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/best-practice-5.2---implement-least-privilege-policies-for-source-and-downstream-systems..html): "The principle of least privilege works by giving only enough access for systems to do the job." [read-at-source]
- BP 13.1 lifecycle (https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/best-practice-13.1-remove-unused-data-and-infrastructure..html): "If data is stored in Amazon S3, use Amazon S3 Lifecycle configurations to expire data automatically." [read-at-source]
- BP 13.1.6: "Using Parquet over CSV format can reduce storage costs significantly." [read-at-source]

## 12. AWS Free Tier

Source: https://aws.amazon.com/free/
- "When you create a new AWS Free Tier account, you get $100 in credits immediately. As you explore key services, you can earn up to $100 more." [read-at-source]
- "That's up to $200 over 6 months to build, break things, and experiment with no charges" [read-at-source]
- "The account closes on its own 6 months after you open it or when your credits run out, whichever comes first." [read-at-source]
- "You won't be charged unless you convert to a Paid plan." [read-at-source]
- Free plan service limit: "Access to all AWS services ... Limited to select services only" (Free plan column) [read-at-source]
- Always free: "30+ AWS services are always free within monthly usage limits on both the Free and Paid plans." [read-at-source]

Source: https://aws.amazon.com/free/free-tier-faqs/
- Payment card: "No. A payment method isn't required to sign up for most new customers." [read-at-source]
- Caveat: "In some cases, we may request additional information, such as a payment method, to verify your identity." [read-at-source]

## 13. Shared responsibility model

Source: https://aws.amazon.com/compliance/shared-responsibility-model/
- "this differentiation of responsibility is commonly referred to as Security "of" the Cloud versus Security "in" the Cloud." [read-at-source]
- AWS side: "AWS is responsible for protecting the infrastructure that runs all of the services offered in the AWS Cloud." [read-at-source]
- Customer side: "Customer responsibility will be determined by the AWS Cloud services that a customer selects." [read-at-source]

## 14. Regions and Availability Zones

Source: https://aws.amazon.com/about-aws/global-infrastructure/
- "The AWS Cloud spans 124 Availability Zones within 39 Geographic Regions, with announced plans for 7 more Availability Zones and 2 more AWS Regions" [read-at-source]
- Announced: "in the Kingdom of Saudi Arabia, and Chile." [read-at-source]
- "With three Availability Zones (AZs) per Region" [read-at-source]

Source: https://docs.aws.amazon.com/whitepapers/latest/aws-overview/global-infrastructure.html
- "An AWS Region is a physical location in the world where we have multiple Availability Zones." [read-at-source]
- "Availability Zones consist of one or more discrete data centers, each with redundant power, networking, and connectivity, housed in separate facilities." [read-at-source]

## 15. Budgets, cost allocation tags, data transfer

Source: https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html
- "You can choose to be alerted for both actual (after accruing) and forecasted (before accruing) spends." [read-at-source]
- Refresh: "AWS Budgets information is updated up to three times a day." [read-at-source]
- Lag caveat: "There can be a delay between when you incur a charge and when you receive a notification from AWS Budgets" [read-at-source]

Source: https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/activating-tags.html
(the requested cost-management/.../cost-alloc-tags.html returned only a header; this is the live page on the same topic)
- "For tags to appear on your billing reports, you must activate them." [read-at-source]
- "it can take up to 24 hours for the tag keys to appear on your cost allocation tags page for activation. It can then take up to 24 hours for tag keys to activate." [read-at-source]

Source: https://aws.amazon.com/s3/pricing/ (Data transfer)
- Free list includes: "Data transferred in from the internet." [read-at-source]
- Inbound price row "Data Transfer IN To Amazon S3 From Internet ... All data transfer in" = 0.00 USD per GB (pricing feed) [read-at-source]
- "AWS customers receive 100GB of data transfer out to the internet free each month, aggregated across all AWS Services and Regions (except China and GovCloud)." [read-at-source]

## 16. NYC TLC trip record data

Source: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- Monthly: "Trip data is published monthly on this website, typically with a two-month delay to allow time for full vendor submissions." [read-at-source]
- Format: "Due to the size of the datasets, the trip record files have been stored in the PARQUET format." [read-at-source]
- Fields: "Yellow and green taxi trip records include fields capturing pickup and drop-off dates/times, pickup and drop-off locations, trip distances, itemized fares" [read-at-source]
- Disclaimer: "The trip data was not created by the TLC, and TLC makes no representations as to the accuracy of these data." [read-at-source]
- Yellow data dictionary: https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf (link on page) [read-at-source]
- Files: monthly links of the form https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_YYYY-MM.parquet; the page lists Parquet files for every year back to 2009; latest yellow file on 2026-10-03 is yellow_tripdata_2026-08.parquet [read-at-source]
- Public: the files download without login from the page's links (observed, not a quoted statement) [read-at-source]

---

## Could not verify

1. A docs statement that objects must sit 30 days before a Lifecycle transition to Standard-IA or One Zone-IA. Not found on object-lifecycle-mgmt.html, lifecycle-transition-general-considerations.html, intro-lifecycle-rules.html or lifecycle-configuration-examples.html. Only the 30-day minimum storage CHARGE and a 30-day example rule are at source. Do not teach it as a hard rule.
2. "Parquet since 2022" for NYC TLC. The page says files "have been stored in the PARQUET format" and now serves Parquet for every year back to 2009; it gives no switch date.
3. A NYC TLC terms-of-use statement specific to the trip data. The only terms on the page are the generic nyc.gov footer "Terms of use" link plus the accuracy disclaimer quoted above.
4. A per-file size target for Athena (e.g. "files around 128 MB"). Athena docs give 128 MB only as the Parquet row group default, plus "avoid too many small files". No file-size number found.
5. A "single API" phrase and a capabilities list on the Bedrock overview page. The current page has neither.
6. A Provisioned Throughput definition on a Bedrock docs page. Only the pricing-page mention was read.
7. Athena "per TB" price as literal page text. The page renders it from a template; the 5.00 USD value was read from the pricing feed behind it and confirmed by the page's own "$5/TB" worked example.
8. cost-management/latest/userguide/cost-alloc-tags.html content. It returned only a header; facts came from awsaccountbilling .../activating-tags.html instead.
9. The S3 data transfer IN price as literal page text (template); value 0.00 came from the pricing feed, and the "Data transferred in from the internet" free-list line was read on the page.
