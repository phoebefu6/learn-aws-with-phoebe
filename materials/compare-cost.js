/* Prints the cost canon from assets/aws-cost.js in the same format as aws_reference.py */
const path = require("path"), fs = require("fs");
const cost = require(path.join(__dirname, "..", "assets", "aws-cost.js"));
global.window = {};
eval(fs.readFileSync(path.join(__dirname, "..", "assets", "aws-sample.js"), "utf8"));
const { meta, prices, queries } = window.AWS_SAMPLE;
const csvGB = 1024, qpd = 100, f = cost.scale(meta, csvGB), L3 = ["csv", "parquet", "partitioned"];
const fx = (n, d) => n.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
console.log(`sample rows ${meta.rows} | csv ${meta.csv.bytes} | parquet ${meta.parquet.bytes} | partitioned ${meta.partitioned_bytes} in ${meta.partitioned.length} files`);
for (const q of queries) for (const L of L3) {
  const b = cost.scanned(meta, L, q), s = cost.athenaCost(b, prices.athena_tb), x = cost.athenaCost(b * f, prices.athena_tb);
  console.log(`${q.id} ${L.padEnd(11)} sample_bytes ${String(b).padStart(9)} share_of_csv ${(b / meta.csv.bytes).toFixed(4)} sample_usd ${s.usd.toFixed(6)} | at ${csvGB} GB csv: ${fx(b * f / cost.GB, 1)} GB scanned $${fx(x.usd, 2)}/query $${fx(x.usd * qpd * 30, 0)}/month`);
}
for (const L of L3) {
  const gb = cost.stored(meta, L) * f / cost.GB;
  console.log(`store ${L.padEnd(11)} ${fx(gb, 1)} GB  STANDARD $${fx(cost.tiered(gb, prices.s3.STANDARD), 2)}/mo  STANDARD_IA $${fx(cost.tiered(gb, prices.s3.STANDARD_IA), 2)}/mo  DEEP_ARCHIVE $${fx(cost.tiered(gb, prices.s3.DEEP_ARCHIVE), 2)}/mo`);
}
