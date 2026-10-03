"""Build the shipped NYC TLC sample and measure bytes per layout.

Input : yellow_tripdata_2024-01.parquet from the NYC TLC Trip Record Data page
        (https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet,
        sha256 c4d59da7bbc8abaeeeb1727947ee93d9891a71acb42854bd80db1571b2030510, fetched 2026-10-03)
Output: data/yellow_tripdata_2024-01_sample.parquet  (100,000 seeded rows, shipped)
        <work>/layouts/{csv,parquet,partitioned}       (rebuilt by learners in analyst session 1)
        materials/taxi-layout-metadata.json             (bytes per file per column, read by the bench)
Run   : python build-taxi-sample.py <path to full month parquet> <work dir>
Pinned: duckdb 1.5.6, pyarrow 25.0.1, numpy from the same venv.
"""
import json, os, sys, glob
import duckdb, numpy as np, pyarrow.parquet as pq, pyarrow as pa

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, WORK = sys.argv[1], sys.argv[2]
SEED, N = 20240101, 100_000

t = pq.read_table(SRC)
ts = t.column("tpep_pickup_datetime").to_numpy()
keep = (ts >= np.datetime64("2024-01-01")) & (ts < np.datetime64("2024-02-01"))
t = t.filter(pa.array(keep))
idx = np.sort(np.random.default_rng(SEED).choice(t.num_rows, N, replace=False))
s = t.take(pa.array(idx)).sort_by("tpep_pickup_datetime")
out = os.path.join(REPO, "data", "yellow_tripdata_2024-01_sample.parquet")
pq.write_table(s, out, compression="snappy")
print("in-month rows", t.num_rows, "sample", s.num_rows, "->", os.path.getsize(out), "bytes")

c = duckdb.connect()
c.execute("SET threads=1")
c.execute(f"CREATE TABLE trips AS SELECT *, CAST(tpep_pickup_datetime AS DATE) AS pickup_date FROM '{out}'")
L = os.path.join(WORK, "layouts")
os.system(f"rm -rf '{L}'")
os.makedirs(L)
c.execute(f"COPY (SELECT * EXCLUDE (pickup_date) FROM trips) TO '{L}/trips.csv' (HEADER)")
c.execute(f"COPY (SELECT * EXCLUDE (pickup_date) FROM trips) TO '{L}/trips.parquet' (FORMAT parquet, COMPRESSION snappy)")
c.execute(f"COPY trips TO '{L}/partitioned' (FORMAT parquet, COMPRESSION snappy, PARTITION_BY (pickup_date))")

def colbytes(path):
    rows = c.execute(f"SELECT path_in_schema, SUM(total_compressed_size) FROM parquet_metadata('{path}') GROUP BY 1").fetchall()
    return {k: int(v) for k, v in rows}

meta = {
    "source": "NYC TLC yellow taxi trip records, January 2024, 100,000-row seeded sample (seed 20240101)",
    "rows": s.num_rows,
    "columns": [f.name for f in s.schema],
    "csv": {"bytes": os.path.getsize(f"{L}/trips.csv")},
    "parquet": {"bytes": os.path.getsize(f"{L}/trips.parquet"), "cols": colbytes(f"{L}/trips.parquet")},
    "partitioned": [],
}
for p in sorted(glob.glob(f"{L}/partitioned/pickup_date=*/*.parquet")):
    day = p.split("pickup_date=")[1].split("/")[0]
    rows = c.execute(f"SELECT COUNT(*) FROM '{p}'").fetchone()[0]
    meta["partitioned"].append({"day": day, "rows": rows, "bytes": os.path.getsize(p), "cols": colbytes(p)})
meta["partitioned_bytes"] = sum(x["bytes"] for x in meta["partitioned"])
json.dump(meta, open(os.path.join(REPO, "materials", "taxi-layout-metadata.json"), "w"), indent=1)
print("csv", meta["csv"]["bytes"], "parquet", meta["parquet"]["bytes"], "partitioned", meta["partitioned_bytes"], "files", len(meta["partitioned"]))
