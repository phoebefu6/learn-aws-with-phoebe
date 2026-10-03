# Analyst session 3 - the Glue Data Catalog, run locally against moto
import os, boto3, duckdb
from moto import mock_aws

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
SAMPLE = "yellow_tripdata_2024-01_sample.parquet"
con = duckdb.connect()
schema = con.execute(f"DESCRIBE SELECT * FROM '{SAMPLE}'").fetchall()
TYPES = {"INTEGER": "int", "BIGINT": "bigint", "DOUBLE": "double", "VARCHAR": "string", "TIMESTAMP": "timestamp"}
columns = [{"Name": n.lower(), "Type": TYPES[t]} for n, t, *_ in schema]
days = [r[0] for r in con.execute(f"SELECT DISTINCT CAST(tpep_pickup_datetime AS DATE)::VARCHAR FROM '{SAMPLE}' ORDER BY 1").fetchall()]

with mock_aws():
    glue = boto3.client("glue")
    glue.create_database(DatabaseInput={"Name": "lake"})
    glue.create_table(DatabaseName="lake", TableInput={
        "Name": "nyc_taxi",
        "StorageDescriptor": {
            "Columns": columns,
            "Location": "s3://acme-lake/curated/nyc_taxi/",
            "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "SerdeInfo": {"SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"},
        },
        "PartitionKeys": [{"Name": "pickup_date", "Type": "date"}],
        "TableType": "EXTERNAL_TABLE",
        "Parameters": {"classification": "parquet"},
    })
    glue.batch_create_partition(DatabaseName="lake", TableName="nyc_taxi", PartitionInputList=[
        {"Values": [d], "StorageDescriptor": {"Location": f"s3://acme-lake/curated/nyc_taxi/pickup_date={d}/"}} for d in days])
    t = glue.get_table(DatabaseName="lake", Name="nyc_taxi")["Table"]
    print("table:", t["DatabaseName"] + "." + t["Name"], "|", len(t["StorageDescriptor"]["Columns"]), "columns |",
          "partition key:", t["PartitionKeys"][0]["Name"], "|", t["StorageDescriptor"]["Location"])
    print("first three columns:", [(c["Name"], c["Type"]) for c in t["StorageDescriptor"]["Columns"][:3]])
    parts = glue.get_partitions(DatabaseName="lake", TableName="nyc_taxi")["Partitions"]
    print("partitions registered:", len(parts), "| first:", parts[0]["StorageDescriptor"]["Location"] if parts else None)
    week = [p for p in parts if "2024-01-15" <= p["Values"][0] <= "2024-01-21"]
    print("a query on 15-21 January needs", len(week), "of", len(parts), "partitions")
