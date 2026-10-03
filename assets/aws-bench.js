/* learn-aws-with-phoebe - the IAM + cost bench (analyst session 8)
   Needs: aws-iam.js (AwsIam), aws-iam-cases.js (AWS_IAM_CASES), aws-cost.js (AwsCost), aws-sample.js (AWS_SAMPLE).
   Every verdict is computed by the evaluator in this page; every byte count comes from the
   real sample files; dollars use the AWS Price List rows shipped in aws-sample.js. */
(function () {
  "use strict";
  var IAM = window.AwsIam, D = window.AWS_IAM_CASES, COST = window.AwsCost, S = window.AWS_SAMPLE;
  if (!IAM || !D || !COST || !S) return;

  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    for (var k in (attrs || {})) e.setAttribute(k, attrs[k]);
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function fmt(n, d) { return Number(n).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }); }
  var KIND = { allow: "Allow", explicit: "Deny (explicit)", implicit: "Deny (implicit)" };

  /* ---------------- IAM panel ---------------- */
  var iamRoot = document.getElementById("aws-iam-bench");
  if (iamRoot) {
    var state = { anti: false, flip: false, missing: false };
    iamRoot.innerHTML =
      '<div class="aws-panel">' +
      '<div class="aws-scope"><b>Scope, stated:</b> an IAM user inside one account; identity policies, an optional bucket (resource) policy, ' +
      'an optional permissions boundary and an optional SCP. Session policies, RCPs, roles and cross-account requests are not modelled, ' +
      'and the evaluator refuses operators it does not implement rather than guessing.</div>' +
      '<h4 class="aws-h">1 · Ask as the analyst</h4>' +
      '<div class="aws-row"><label class="aws-wide">Request <select id="aws-req"></select></label>' +
      '<label>Over TLS <select id="aws-tls"><option value="true">aws:SecureTransport = true</option><option value="false">false (plain HTTP)</option><option value="">key absent</option></select></label>' +
      '<label>Source IP <input id="aws-ip" value="203.0.113.10" size="14"></label></div>' +
      '<div class="aws-verdict" id="aws-verdict"></div><ul class="aws-trace" id="aws-trace"></ul>' +
      '<div class="aws-row"><button class="btn aws-anti" id="aws-anti" type="button">Anti-lever: add "Action": "*" Allow</button>' +
      '<span class="aws-count" id="aws-count"></span></div>' +
      '<details class="aws-pol"><summary>The analyst\'s two policies (what the evaluator reads)</summary><pre id="aws-pol"></pre></details>' +
      '<h4 class="aws-h">2 · The test table: ' + D.cases.length + ' cases from the AWS docs</h4>' +
      '<div class="aws-row"><button class="btn aws-break" id="aws-flip" type="button">Break: let an Allow beat a Deny</button>' +
      '<button class="btn aws-break" id="aws-miss" type="button">Break: a missing key matches</button>' +
      '<span class="aws-score" id="aws-score"></span></div>' +
      '<div class="aws-tablewrap"><table class="clean aws-cases" id="aws-cases"></table></div>' +
      '</div>';

    var sel = document.getElementById("aws-req");
    D.universe.forEach(function (u, i) {
      var short = u[1].replace(/^arn:aws:/, "").replace(/111122223333/, "acct");
      sel.appendChild(el("option", { value: i }, esc(u[0] + "  on  " + short)));
    });
    sel.value = "3"; /* PutObject into curated: implicitly denied for the analyst */
    document.getElementById("aws-pol").textContent = JSON.stringify(D.analyst.identity, null, 1);

    function ctx() {
      var c = {}, tls = document.getElementById("aws-tls").value, ip = document.getElementById("aws-ip").value.trim();
      if (tls !== "") c["aws:SecureTransport"] = tls;
      if (ip) c["aws:SourceIp"] = ip;
      return c;
    }
    function roleSet() { return state.anti ? IAM.withAntiLever(D.analyst) : D.analyst; }
    function opts() { return { flipDeny: state.flip, missingTrue: state.missing }; }

    function renderRequest() {
      var u = D.universe[Number(sel.value)];
      var r = IAM.evaluate(roleSet(), { principal: D.user, action: u[0], resource: u[1], context: ctx() }, opts());
      var v = document.getElementById("aws-verdict");
      v.className = "aws-verdict is-" + r.kind;
      v.innerHTML = "<b>" + KIND[r.kind] + "</b> <span>decided by " + esc(r.by) + "</span>";
      document.getElementById("aws-trace").innerHTML = r.trace.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("");
      /* count over the 24 data-team actions, with the default context */
      function countAllowed(set) {
        return D.universe.filter(function (x) {
          return IAM.evaluate(set, { principal: D.user, action: x[0], resource: x[1], context: D.universe_ctx }, opts()).kind === "allow";
        }).length;
      }
      var base = countAllowed(D.analyst), wide = countAllowed(IAM.withAntiLever(D.analyst));
      var t0 = IAM.runCases(D.cases, opts()).allowed, t1 = IAM.runCases(D.cases, opts(), IAM.withAntiLever).allowed;
      document.getElementById("aws-count").innerHTML = state.anti
        ? "Allowed for the analyst: <b>" + base + " → " + wide + "</b> of " + D.universe.length + " actions · test table: <b>" + t0 + " → " + t1 + "</b> of " + D.cases.length + " requests allowed"
        : "Allowed for the analyst: <b>" + base + "</b> of " + D.universe.length + " actions · test table: <b>" + t0 + "</b> of " + D.cases.length + " allowed";
    }

    function renderCases() {
      var res = IAM.runCases(D.cases, opts());
      var tb = document.getElementById("aws-cases");
      var rows = "<tr><th>Case</th><th>Expected (from the docs)</th><th>Evaluator</th><th></th></tr>";
      D.cases.forEach(function (c, i) {
        var g = res.rows[i];
        rows += '<tr class="' + (g.ok ? "" : "aws-fail") + '"><td><b>' + c.id + "</b> " + esc(c.title) +
          '<span class="aws-doc">' + esc(c.doc) + ": " + esc(c.rule) + "</span></td><td>" + KIND[c.expect] + "</td><td>" + KIND[g.got] +
          "</td><td>" + (g.ok ? "pass" : "<b>FAIL</b>") + "</td></tr>";
      });
      tb.innerHTML = rows;
      var sc = document.getElementById("aws-score");
      sc.className = "aws-score " + (res.fail ? "is-bad" : "is-good");
      sc.innerHTML = "<b>" + res.pass + " of " + D.cases.length + "</b> pass" + (res.fail ? " · <b>" + res.fail + " fail</b>: the tests caught the broken logic" : "");
    }

    function toggle(btn, key) {
      state[key] = !state[key];
      btn.classList.toggle("is-on", state[key]);
      renderRequest(); renderCases();
    }
    document.getElementById("aws-anti").addEventListener("click", function () { toggle(this, "anti"); });
    document.getElementById("aws-flip").addEventListener("click", function () { toggle(this, "flip"); });
    document.getElementById("aws-miss").addEventListener("click", function () { toggle(this, "missing"); });
    ["aws-req", "aws-tls"].forEach(function (id) { document.getElementById(id).addEventListener("change", renderRequest); });
    document.getElementById("aws-ip").addEventListener("input", renderRequest);
    renderRequest(); renderCases();
  }

  /* ---------------- cost panel ---------------- */
  var costRoot = document.getElementById("aws-cost-bench");
  if (costRoot) {
    var M = S.meta, P = S.prices, LAY = [["csv", "CSV, one file"], ["parquet", "Parquet, one file"], ["partitioned", "Parquet, partitioned by day"]];
    var CLASSES = [["STANDARD", "S3 Standard"], ["STANDARD_IA", "S3 Standard-IA"], ["INTELLIGENT_TIERING_FA", "Intelligent-Tiering, frequent tier"],
                   ["GLACIER_IR", "Glacier Instant Retrieval"], ["DEEP_ARCHIVE", "Glacier Deep Archive"]];
    var days = M.partitioned.map(function (f) { return f.day; });
    costRoot.innerHTML =
      '<div class="aws-panel">' +
      '<div class="aws-stamp">Prices: AWS Price List bulk API, <b>' + esc(P.region) + '</b>, retrieved <b>' + esc(P.retrieved) +
      '</b> (Athena offer published ' + esc(P.athena_pub) + ', S3 ' + esc(P.s3_pub) + '): Athena $' + fmt(P.athena_tb, 2) +
      ' per TB scanned, 10 MB minimum per query. <b>Re-verify before delivery.</b></div>' +
      '<div class="aws-row"><label>Your table, as CSV <input id="aws-gb" type="number" min="1" step="1" value="1024"> GB</label>' +
      '<label>Queries a day <input id="aws-qpd" type="number" min="0" step="1" value="100"></label>' +
      '<label>Storage class <select id="aws-class"></select></label></div>' +
      '<div class="aws-row"><label>Query <select id="aws-q"></select></label></div>' +
      '<div class="aws-custom" id="aws-custom" hidden><div class="aws-cols" id="aws-cols"></div>' +
      '<label>From <select id="aws-from"></select></label> <label>to <select id="aws-to"></select></label> ' +
      '<label><input type="checkbox" id="aws-nofilter"> whole month</label></div>' +
      '<div class="aws-tablewrap"><table class="clean aws-costs" id="aws-costs"></table></div>' +
      '<p class="aws-note" id="aws-note"></p></div>';

    var qs = document.getElementById("aws-q");
    S.queries.forEach(function (q, i) { qs.appendChild(el("option", { value: i }, esc(q.id + " · " + q.label))); });
    qs.appendChild(el("option", { value: "custom" }, "Your own: pick columns and days"));
    qs.value = "1";
    var cs = document.getElementById("aws-class");
    CLASSES.forEach(function (c) { cs.appendChild(el("option", { value: c[0] }, c[1])); });
    var cols = document.getElementById("aws-cols");
    M.columns.forEach(function (c) {
      var lab = el("label", {}, '<input type="checkbox" value="' + esc(c) + '"' + (c === "fare_amount" ? " checked" : "") + "> " + esc(c));
      cols.appendChild(lab);
    });
    ["aws-from", "aws-to"].forEach(function (id, j) {
      var s = document.getElementById(id);
      days.forEach(function (d) { s.appendChild(el("option", { value: d }, d)); });
      s.value = j ? "2024-01-21" : "2024-01-15";
    });

    function query() {
      if (qs.value !== "custom") return S.queries[Number(qs.value)];
      var picked = [].slice.call(cols.querySelectorAll("input:checked")).map(function (x) { return x.value; });
      var whole = document.getElementById("aws-nofilter").checked;
      var f = document.getElementById("aws-from").value, t = document.getElementById("aws-to").value;
      if (f > t) { var tmp = f; f = t; t = tmp; }
      return { id: "Yours", cols: picked.length ? picked : ["fare_amount"], from: whole ? null : f, to: whole ? null : t };
    }

    function render() {
      document.getElementById("aws-custom").hidden = qs.value !== "custom";
      var gb = Math.max(1, Number(document.getElementById("aws-gb").value) || 1);
      var qpd = Math.max(0, Number(document.getElementById("aws-qpd").value) || 0);
      var cls = cs.value, f = COST.scale(M, gb), q = query();
      var rows = "<tr><th>Layout</th><th>Bytes read, sample <span class=\"aws-tag\">measured</span></th><th>Share of the CSV</th>" +
                 "<th>At your size <span class=\"aws-tag m\">modelled</span></th><th>Per query</th><th>Per month</th><th>Storage / month</th></tr>";
      var best = null;
      LAY.forEach(function (L) {
        var b = COST.scanned(M, L[0], q), x = COST.athenaCost(b * f, P.athena_tb);
        var stGB = COST.stored(M, L[0]) * f / COST.GB, st = COST.tiered(stGB, P.s3[cls]);
        var month = x.usd * qpd * 30;
        if (best === null || month < best.m) best = { m: month, name: L[1] };
        rows += "<tr><td><b>" + L[1] + "</b></td><td>" + fmt(b, 0) + " B</td><td>" + fmt(100 * b / M.csv.bytes, 2) + "%</td><td>" +
                fmt(b * f / COST.GB, 1) + " GB</td><td>$" + fmt(x.usd, 2) + "</td><td><b>$" + fmt(month, 0) + "</b></td><td>$" + fmt(st, 2) +
                " <span class=\"aws-dim\">(" + fmt(stGB, 0) + " GB)</span></td></tr>";
      });
      document.getElementById("aws-costs").innerHTML = rows;
      var sampleBill = COST.athenaCost(COST.scanned(M, "csv", q), P.athena_tb);
      document.getElementById("aws-note").innerHTML =
        "Cheapest to query: <b>" + esc(best.name) + "</b>. At sample size every layout bills the 10 MB minimum, $" + fmt(sampleBill.usd, 6) +
        " a query, so the difference only appears at scale. Sample: " + fmt(M.rows, 0) + " real NYC TLC yellow taxi trips, January 2024; CSV " +
        fmt(M.csv.bytes, 0) + " B, Parquet " + fmt(M.parquet.bytes, 0) + " B, partitioned " + fmt(M.partitioned_bytes, 0) + " B in " +
        M.partitioned.length + " files. Scaling is linear in bytes, which overstates the per-file overhead of the partitioned layout at large sizes. " +
        "Units: GB = 2^30 bytes, TB = 2^40.";
    }
    ["aws-gb", "aws-qpd"].forEach(function (id) { document.getElementById(id).addEventListener("input", render); });
    ["aws-class", "aws-q", "aws-from", "aws-to", "aws-nofilter"].forEach(function (id) { document.getElementById(id).addEventListener("change", render); });
    cols.addEventListener("change", render);
    render();
  }
})();
