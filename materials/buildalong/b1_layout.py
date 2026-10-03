# Analyst session 1 - S3 layout and Parquet, run locally against moto (a mock of the AWS API)
import os, boto3, duckdb
from moto import mock_aws

SAMPLE = "yellow_tripdata_2024-01_sample.parquet"     # 100,000 real NYC TLC trips, January 2024
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

# 1. Write the same rows three ways
con = duckdb.connect()
con.execute("SET threads=1")
con.execute(f"CREATE TABLE trips AS SELECT *, CAST(tpep_pickup_datetime AS DATE) AS pickup_date FROM '{SAMPLE}'")
os.makedirs("out", exist_ok=True)
con.execute("COPY (SELECT * EXCLUDE (pickup_date) FROM trips) TO 'out/trips.csv' (HEADER)")
con.execute("COPY (SELECT * EXCLUDE (pickup_date) FROM trips) TO 'out/trips.parquet' (FORMAT parquet, COMPRESSION snappy)")
con.execute("COPY trips TO 'out/partitioned' (FORMAT parquet, COMPRESSION snappy, PARTITION_BY (pickup_date), OVERWRITE_OR_IGNORE)")

# 2. Upload them under a raw / curated layout in a mocked bucket
with mock_aws():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="acme-lake")
    s3.upload_file("out/trips.csv", "acme-lake", "raw/nyc_taxi/2024/01/trips.csv")
    s3.upload_file("out/trips.parquet", "acme-lake", "curated/nyc_taxi_flat/2024-01.parquet")
    for root, _, files in os.walk("out/partitioned"):
        for f in files:
            part = root.split("partitioned/")[1]                      # pickup_date=2024-01-15
            s3.upload_file(os.path.join(root, f), "acme-lake", f"curated/nyc_taxi/{part}/{f}")
    pages = s3.get_paginator("list_objects_v2").paginate(Bucket="acme-lake")
    objs = [o for p in pages for o in p["Contents"]]
    for prefix in ("raw/", "curated/nyc_taxi_flat/", "curated/nyc_taxi/"):
        sel = [o for o in objs if o["Key"].startswith(prefix)]
        print(f"{prefix:24s} {len(sel):3d} objects {sum(o['Size'] for o in sel):>10,d} bytes")
    print("one partition key:", sorted(o["Key"] for o in objs if "2024-01-15" in o["Key"])[0])

# 3. What a columnar engine must read for: average tip by payment type
cols = con.execute("""SELECT path_in_schema, SUM(total_compressed_size) FROM parquet_metadata('out/trips.parquet')
                      GROUP BY 1 ORDER BY 2 DESC""").fetchall()
need = sum(b for c, b in cols if c in ("payment_type", "tip_amount"))
print("parquet column chunks:", len(cols), "| two columns needed:", f"{need:,d}", "bytes of", f"{os.path.getsize('out/trips.parquet'):,d}")
print("csv must be read whole:", f"{os.path.getsize('out/trips.csv'):,d}", "bytes")
