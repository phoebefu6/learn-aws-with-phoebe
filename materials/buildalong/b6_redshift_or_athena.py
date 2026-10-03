# Analyst session 6 - Redshift Serverless or Athena: a lake bills bytes, a warehouse bills time.
# Prices: us-east-1, AWS Price List, retrieved 2026-10-03. Bytes: measured in session 4.
# The warehouse side is MODELLED: how long your queries keep RPUs busy is an assumption you set.
ATHENA_TB, RPU_HR, RMS_GB_MO, S3_GB_MO = 5.00, 0.375, 0.024, 0.023
GB_PER_QUERY = 20.0          # Q2 on 1 TB of CSV-equivalent data, stored as one Parquet file (session 4)
STORED_GB = 242.1            # that table as Parquet

def athena_month(queries_per_day):
    return queries_per_day * 30 * GB_PER_QUERY / 1024 * ATHENA_TB + STORED_GB * S3_GB_MO

def redshift_month(busy_hours_per_day, base_rpu=8):
    return busy_hours_per_day * 30 * base_rpu * RPU_HR + STORED_GB * RMS_GB_MO

print(f"{'queries/day':>11s} {'Athena $/mo':>12s} | warehouse busy 1 h/day at 8 RPU: ${redshift_month(1):,.2f}/mo, 4 h/day: ${redshift_month(4):,.2f}/mo")
for q in (10, 50, 100, 300, 1000):
    print(f"{q:>11d} {athena_month(q):>12,.2f}")
for busy in (1, 4):
    cross = (redshift_month(busy) - STORED_GB * S3_GB_MO) / (30 * GB_PER_QUERY / 1024 * ATHENA_TB)
    print(f"break-even with a warehouse busy {busy} h/day at 8 RPU: about {cross:,.0f} queries a day")
print("60-second minimum: a 5-second query on an idle warehouse bills", f"${8 * 60 / 3600 * RPU_HR:.4f}", "at 8 RPU, not", f"${8 * 5 / 3600 * RPU_HR:.4f}")
