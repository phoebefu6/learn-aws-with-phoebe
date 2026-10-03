"""Writes index.html. Session cards, paths and the knowledge map data come from one list;
the map data is serialised with json.dumps (never an f-string)."""
import json, os, sys, html
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE = open(sys.argv[1]).read()

LEADER = [
  ("a1-what-aws-is-to-a-data-team.html", "🗺️", "What AWS is to a data team", "#34D399",
   "Regions and Availability Zones, which half of security is yours, the seven services a data platform is built from, and the four meters every bill runs on.",
   "start", ["Regions and AZs", "Four meters"]),
  ("a2-s3-is-the-lake.html", "🪣", "S3 is the lake", "#FBBF24",
   "Buckets, keys and prefixes, nine storage classes and their minimums, lifecycle rules, and the raw, curated and archive zones a data team actually needs.",
   None, ["Storage classes", "Lifecycle rules"]),
  ("a3-who-can-touch-what.html", "🔐", "Who can touch what", "#FBBF24",
   "IAM as AWS implements it: users, roles, policies, the default no, why an explicit Deny always wins, and what one wildcard hands an analyst.",
   None, ["Default deny", "The wildcard"]),
  ("a4-compute-or-serverless.html", "⚙️", "Compute or serverless", "#FB923C",
   "Lambda, a container on Fargate, Redshift Serverless and Athena compared by the meter each one runs on, with the quotas that decide which jobs fit.",
   None, ["Billing meters", "Lambda limits"]),
  ("a5-the-bill-you-did-not-plan.html", "🧾", "The bill you did not plan", "#FB923C",
   "Where data platform bills really come from: scans, small files, idle minimums and transfer, and the budgets and tags that catch them early.",
   None, ["Scan costs", "Budgets and tags"]),
  ("a6-a-data-platform-on-one-page.html", "📐", "A data platform on one page", "#F87171",
   "The capstone: storage, catalog, engines, identity, cost guardrails and AI on one page, and six questions to ask any AWS data proposal.",
   "capstone", ["One-page platform", "Six questions"]),
]
ANALYST = [
  ("b1-s3-layout-and-parquet.html", "🧱", "S3 layout and Parquet", "#34D399",
   "100,000 real New York taxi trips written as CSV, Parquet and partitioned Parquet, uploaded to a mocked bucket on your laptop, and measured byte by byte.",
   "start", ["Keys and prefixes", "Column pruning"]),
  ("b2-iam-policies-as-code.html", "📜", "IAM policies as code", "#FBBF24",
   "An analyst policy written as JSON and enforced by moto against real boto3 calls: read curated, denied raw, never delete the bucket.",
   None, ["Policy JSON", "Guardrail denies"]),
  ("b3-the-glue-catalog.html", "🗂️", "The Glue Data Catalog", "#FBBF24",
   "A table, its schema and 31 partitions registered in a mocked Glue catalog, and why the catalog decides which files a query can skip.",
   None, ["Tables and schemas", "Partitions"]),
  ("b4-athena-pay-per-byte.html", "💸", "Athena: pay per byte scanned", "#FB923C",
   "Three questions asked of three layouts, bytes measured from the files' own metadata, priced at $5.00 per terabyte with the 10 MB minimum.",
   None, ["Bytes scanned", "10 MB minimum"]),
  ("b5-lambda-or-a-container.html", "λ", "Lambda or a container", "#FB923C",
   "A CSV-to-Parquet handler run on a mocked S3 event, Lambda's real quotas, and what a mock does not check, priced against an always-on container.",
   None, ["Event handlers", "Mocks and quotas"]),
  ("b6-redshift-or-athena.html", "🏛️", "Redshift or Athena", "#FB923C",
   "A lake bills bytes, a warehouse bills time: the break-even between Athena and Redshift Serverless, with the 60-second minimum priced in.",
   None, ["Bytes or time", "Break-even"]),
  ("b7-bedrock-for-ai-teams.html", "🤖", "Bedrock for AI teams", "#FB923C",
   "A Converse request checked against Bedrock's real API schema without calling a model, batch against on-demand pricing, least privilege and data retention.",
   None, ["Converse API", "Batch pricing"]),
  ("b8-the-iam-and-cost-bench.html", "🎛️", "The IAM and cost bench", "#F87171",
   "A policy evaluator checked against 36 cases from the AWS docs, with a break button and a wildcard anti-lever, beside a cost panel on real bytes and real prices.",
   "capstone", ["36 doc cases", "Anti-lever", "Cost panel"]),
]

def cards(rows, track, n):
    out = []
    for i, (f, icon, title, diff, blurb, flag, _) in enumerate(rows, 1):
        label = f"{track} session {i}" + (" · start here" if flag == "start" else "")
        meta = ""
        if flag == "start":
            meta = '\n        <span class="meta"><span class="pill amber">▶ Start here</span></span>'
        elif flag == "capstone":
            meta = f'\n        <span class="meta"><span class="pill amber">the {track.lower()} capstone</span></span>'
        out.append(f'''      <a class="course-card" href="courses/{f}" style="--diff:{diff}">
        <span class="cicon">{icon}</span>
        <span class="cnum">{label}</span>
        <h3>{html.escape(title)}</h3>
        <p>{html.escape(blurb)}</p>{meta}
      </a>''')
    return "\n".join(out)

def short(t):
    return t.replace("What AWS is to a data team", "What AWS is").replace("A data platform on one page", "Platform on a page") \
            .replace("Athena: pay per byte scanned", "Pay per byte").replace("The bill you did not plan", "The surprise bill") \
            .replace("The IAM and cost bench", "The bench").replace("The Glue Data Catalog", "Glue catalog")

mm = {"title": "AWS for\nData & AI Teams", "centerColor": "#0E1F52", "sessions": []}
for rows in (LEADER, ANALYST):
    for f, icon, title, diff, blurb, flag, concepts in rows:
        mm["sessions"].append({"label": short(title), "href": "courses/" + f, "color": diff,
                               "concepts": [{"label": c, "href": "courses/" + f} for c in concepts]})

L = lambda i: "courses/" + LEADER[i - 1][0]
A = lambda i: "courses/" + ANALYST[i - 1][0]
def path(name, steps, note):
    parts = []
    for i, (href, lab) in enumerate(steps):
        if i: parts.append('        <span class="parr">→</span>')
        parts.append(f'        <a class="pstep" href="{href}">{lab}</a>')
    return f'      <div class="path"><b>{name}</b>\n' + "\n".join(parts) + f'\n        <span style="font-size:.82rem;color:var(--muted)">{note}</span>\n      </div>'

PAGE = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- social:start -->
<meta name="description" content="Fourteen sessions on AWS for data and AI teams: S3 as the lake, IAM as AWS implements it, compute versus serverless, Glue, Athena, Lambda, Redshift Serverless and Bedrock, ending in a bench that evaluates IAM policies against the AWS docs and prices queries on real taxi data.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Learn with Phoebe">
<meta property="og:title" content="AWS for Data &amp; AI Teams - Learn with Phoebe">
<meta property="og:description" content="Storing a terabyte in S3 costs $23.55 a month. Scanning it as CSV 100 times a day costs $15,000. One wildcard takes an analyst from 7 to 22 of 24 actions.">
<meta property="og:url" content="https://phoebefu6.github.io/learn-aws-with-phoebe/">
<meta property="og:image" content="https://phoebefu6.github.io/learn-aws-with-phoebe/assets/og-cover.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="AWS for Data &amp; AI Teams - Learn with Phoebe">
<meta name="twitter:description" content="S3, IAM, Athena, Lambda, Redshift and Bedrock for data teams, with a bench on real bytes and real prices.">
<meta name="twitter:image" content="https://phoebefu6.github.io/learn-aws-with-phoebe/assets/og-cover.png">
<!-- social:end -->
<title>AWS for Data &amp; AI Teams - Learn with Phoebe</title>
<link rel="stylesheet" href="assets/style.css?v=2">
{STYLE}
</head>
<body>

<header class="masthead">
  <div class="wrap">
    <div class="eyebrow">Learn with Phoebe · Data Engineering</div>
    <h1>AWS for <span class="accent">Data &amp; AI Teams</span></h1>
    <p class="sub">AWS rents storage and compute separately, each by its own meter, behind an identity system that says no by default. Six leader sessions teach a data leader to read that sentence in every proposal and every bill, with no code and no account. Eight analyst sessions build it in Python on a laptop, against a local mock of the AWS API, on 100,000 real New York taxi trips, and end in a bench that evaluates IAM policies the way AWS documents and prices queries from the AWS Price List.</p>
    <div class="stats-row">
      <div class="stat"><b data-count="14">14</b><span>sessions, two tracks</span></div>
      <div class="stat"><b data-count="100">100</b><span>thousand real taxi trips</span></div>
      <div class="stat"><b data-count="36">36</b><span>IAM cases from the AWS docs</span></div>
      <div class="stat"><b data-count="0">0</b><span>AWS accounts required</span></div>
      <div class="stat"><b data-count="45">45</b><span>min per session</span></div>
    </div>
  </div>
</header>

<main class="wrap">

  <section class="section">
    <div class="paths" style="margin-top:0">
      <h2>Leader track 🧭 <span style="font-size:.85rem;font-weight:600;color:var(--muted)">· six sessions, no code, no account</span></h2>
      <p class="plede">For data and AI leaders, managers and architects who sign off on cloud plans and bills. Where the bytes live, who may touch them, which meter is running, where the bill comes from, and the platform on one page.</p>
    </div>

    <div class="course-grid">
{cards(LEADER, "Leader", 6)}
    </div>
  </section>

  <section class="section">
    <div class="paths" style="margin-top:0">
      <h2>Analyst track 🔬 <span style="font-size:.85rem;font-weight:600;color:var(--muted)">· eight sessions, Python on your laptop</span></h2>
      <p class="plede">boto3 against moto, an open-source mock of the AWS API, and DuckDB as the Athena stand-in, on NYC TLC yellow taxi trips. Every page also offers an optional path on a real AWS account.</p>
    </div>

    <div class="course-grid">
{cards(ANALYST, "Analyst", 8)}
    </div>

    <div class="diff-legend">
      <span><i style="background:#34D399"></i>start here</span>
      <span><i style="background:#FBBF24"></i>foundations</span>
      <span><i style="background:#FB923C"></i>hands-on</span>
      <span><i style="background:#F87171"></i>advanced and capstone</span>
    </div>
  </section>

  <section class="section">
    <div class="paths">
      <h2>Choose your path 🗺️</h2>
      <p class="plede">Three doors into the same platform. Each track starts at its own session 1, because the meters and the default no are what make the rest arguable.</p>
{path("💼 I sign off on the cloud plan", [(L(1), "L1"), (L(3), "L3"), (L(5), "L5"), (L(6), "L6")], "the map, the gate, the bill, then the one-page platform")}
{path("🤖 I am putting AI on AWS", [(L(1), "L1"), (L(4), "L4"), (A(7), "A7"), (A(8), "A8")], "meters, compute choices, Bedrock, then the bench")}
{path("🔬 I build the lake", [(A(1), "A1"), (A(2), "A2"), (A(3), "A3"), (A(4), "A4"), (A(8), "A8")], "layout, policies, catalog, the scan bill, then the bench")}
    </div>
  </section>

  <section class="section">
    <div class="paths" style="margin-top:0">
      <h2>Your passport 🎫</h2>
      <p class="plede">Clear all three quiz questions in a session and it gets stamped. Fourteen stamps across both tracks, and they live in this browser only.</p>
    </div>
    <div class="pp-strip"></div>
  </section>

  <section class="section">
    <div class="paths" style="margin-top:0">
      <h2>What is real here 🧾</h2>
      <p class="plede">A course about cloud bills and permissions should be exact about which of its own numbers are measured, which are priced, and which are modelled.</p>
    </div>
    <table class="clean">
      <tr><th>Claim</th><th>Status</th></tr>
      <tr><td>The data</td><td>Real. NYC Taxi and Limousine Commission yellow taxi trips, January 2024; a 100,000-row sample drawn with a fixed seed, shipped with the course</td></tr>
      <tr><td>Every byte count</td><td>Measured from real files written by DuckDB and read back from their own Parquet metadata; an independent run agrees exactly</td></tr>
      <tr><td>Every price</td><td>Read from the AWS Price List for us-east-1 on 3 October 2026, with the date on every widget. Prices change: re-verify before relying on them</td></tr>
      <tr><td>The IAM evaluator</td><td>Written to AWS's documented evaluation logic for one stated scope, checked against 36 cases from the docs in the browser and in Python, and shown failing when deliberately broken</td></tr>
      <tr><td>AWS calls in the analyst track</td><td>Made with boto3 against moto, a mock that runs on your laptop. Nothing is created in AWS and nothing is billed; where moto is weaker than AWS, the page says so</td></tr>
      <tr><td>Costs at your table size</td><td>Modelled: measured bytes scaled linearly to the size you enter, labelled on the widget</td></tr>
    </table>
  </section>

  <section class="section mm-section">
    <h2>The knowledge map 🧠</h2>
    <p class="mm-lede">Both tracks at a glance - hover a session to spotlight its concepts, click any node to jump in.</p>
    <div class="mm-wrap"><div id="mindmap"></div></div>
  </section>

  <footer class="pagefoot">
    <span>learn-aws-with-phoebe · by Phoebe Fu &nbsp;·&nbsp; 📚 <a href="https://phoebefu6.github.io/learn-with-phoebe/">Learn with Phoebe ↗</a></span>
    <span>Neighbours on the shelf: <a href="https://phoebefu6.github.io/learn-data-engineering-with-phoebe/">Data Engineering ↗</a> &nbsp;·&nbsp; <a href="https://phoebefu6.github.io/learn-data-warehouse-with-phoebe/">Data Warehouse ↗</a> &nbsp;·&nbsp; <a href="https://phoebefu6.github.io/learn-data-access-control-with-phoebe/">Data Access Control ↗</a></span>
  </footer>

</main>

<script>
window.MINDMAP_DATA = {json.dumps(mm, indent=2, ensure_ascii=False)};
</script>
<script src="assets/app.js?v=2"></script>
<script src="assets/mindmap.js?v=1"></script>
</body>
</html>
'''
open(os.path.join(REPO, "index.html"), "w").write(PAGE)
print("index.html written", len(PAGE))
