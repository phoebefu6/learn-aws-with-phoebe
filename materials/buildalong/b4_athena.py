# Analyst session 4 - Athena bills bytes scanned. DuckDB stands in for the engine; the bytes are the files'.
import math, os
import duckdb

MB, TB, USD_PER_TB = 2 ** 20, 2 ** 40, 5.00        # us-east-1, AWS Price List, retrieved 2026-10-03
con = duckdb.connect()

def file_overhead(path):
    cols = con.execute(f"SELECT SUM(total_compressed_size) FROM parquet_metadata('{path}')").fetchone()[0]
    return os.path.getsize(path) - cols

def col_bytes(path, cols):
    q = ",".join(f"'{c}'" for c in cols)
    return con.execute(f"SELECT COALESCE(SUM(total_compressed_size),0) FROM parquet_metadata('{path}') WHERE path_in_schema IN ({q})").fetchone()[0]

def scanned(layout, cols, days=None):
    if layout == "csv":
        return os.path.getsize("out/trips.csv")
    if layout == "parquet":
        need = cols + (["tpep_pickup_datetime"] if days else [])
        return file_overhead("out/trips.parquet") + col_bytes("out/trips.parquet", need)
    total = 0
    for d in sorted(os.listdir("out/partitioned")):
        day = d.split("=")[1]
        if days and not (days[0] <= day <= days[1]):
            continue
        for f in os.listdir(f"out/partitioned/{d}"):
            p = f"out/partitioned/{d}/{f}"
            total += file_overhead(p) + col_bytes(p, cols)
    return total

def bill(b):
    mb = max(10, math.ceil(b / MB))
    return mb * MB / TB * USD_PER_TB

Q = [("Q2 avg tip by payment type, month", ["payment_type", "tip_amount"], None),
     ("Q3 fares on 15 January", ["fare_amount"], ("2024-01-15", "2024-01-15")),
     ("Q4 pickups per zone, 15-21 January", ["PULocationID"], ("2024-01-15", "2024-01-21"))]
csv = os.path.getsize("out/trips.csv")
for name, cols, days in Q:
    print(name)
    for layout in ("csv", "parquet", "partitioned"):
        b = scanned(layout, cols, days)
        print(f"   {layout:11s} {b:>10,d} bytes  {b / csv:7.2%} of the CSV  billed ${bill(b):.6f}")
print("at 1 TB of CSV, Q4 partitioned would scan", f"{scanned('partitioned', ['PULocationID'], ('2024-01-15','2024-01-21')) / csv * 1024:.1f}", "GB")

ans = con.execute("""SELECT payment_type, ROUND(AVG(tip_amount),4), COUNT(*) FROM read_parquet('out/partitioned/*/*.parquet', hive_partitioning=true)
                     GROUP BY 1 ORDER BY 1""").fetchall()
print("Q2 answer (partitioned):", ans)
