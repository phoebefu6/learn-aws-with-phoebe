/* learn-aws-with-phoebe - cost engine (browser + node)
   Bytes come from real files: the NYC TLC sample written three ways, measured by DuckDB's
   parquet_metadata() and the file sizes on disk (materials/build-taxi-sample.py).
   Athena bills bytes scanned, rounded up to the nearest MB, 10 MB minimum per query.
   Units: MB = 2^20 bytes, GB = 2^30, TB = 2^40 (stated on the widget).
   Scaling the sample to a learner's table size is MODELLED: measured bytes x (your size / sample CSV size). */
(function (root) {
  "use strict";
  var MB = Math.pow(2, 20), GB = Math.pow(2, 30), TB = Math.pow(2, 40);

  function sum(o, keys) { var s = 0; keys.forEach(function (k) { s += o[k] || 0; }); return s; }
  function allCols(o) { return Object.keys(o); }

  /* q = { cols: [...], from: "YYYY-MM-DD" | null, to: "YYYY-MM-DD" | null } */
  function scanned(meta, layout, q) {
    var filtered = !!(q.from && q.to);
    if (layout === "csv") return meta.csv.bytes;                       /* a row format is read whole */
    if (layout === "parquet") {
      var cols = q.cols.slice();
      if (filtered && cols.indexOf("tpep_pickup_datetime") < 0) cols.push("tpep_pickup_datetime"); /* the filter reads its column */
      var p = meta.parquet, overhead = p.bytes - sum(p.cols, allCols(p.cols));
      return overhead + sum(p.cols, cols);
    }
    var total = 0;                                                      /* partitioned: prune folders, then columns */
    meta.partitioned.forEach(function (f) {
      if (filtered && (f.day < q.from || f.day > q.to)) return;
      total += (f.bytes - sum(f.cols, allCols(f.cols))) + sum(f.cols, q.cols);
    });
    return total;
  }
  function stored(meta, layout) {
    return layout === "csv" ? meta.csv.bytes : layout === "parquet" ? meta.parquet.bytes : meta.partitioned_bytes;
  }
  function athenaCost(bytes, usdPerTB) {
    var billedMB = Math.max(10, Math.ceil(bytes / MB));
    return { billedMB: billedMB, usd: billedMB * MB / TB * usdPerTB };
  }
  /* tiered GB-month price list rows [{begin, end, usd}] */
  function tiered(gb, rows) {
    var cost = 0;
    rows.forEach(function (r) {
      var lo = Number(r.begin), hi = r.end === "Inf" ? Infinity : Number(r.end);
      if (gb > lo) cost += (Math.min(gb, hi) - lo) * r.usd;
    });
    return cost;
  }
  function scale(meta, csvGB) { return csvGB * GB / meta.csv.bytes; }

  var api = { MB: MB, GB: GB, TB: TB, scanned: scanned, stored: stored, athenaCost: athenaCost, tiered: tiered, scale: scale };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.AwsCost = api;
})(this);
