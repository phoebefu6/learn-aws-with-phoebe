"""Check that each analyst page's build-along code boxes contain every line of its script, and that
its '(real output)' box equals the saved output. Run: python3 check-buildalong.py"""
import html, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = {"b1-s3-layout-and-parquet.html": "b1_layout", "b2-iam-policies-as-code.html": "b2_policies",
         "b3-the-glue-catalog.html": "b3_catalog", "b4-athena-pay-per-byte.html": "b4_athena",
         "b5-lambda-or-a-container.html": "b5_lambda", "b6-redshift-or-athena.html": "b6_redshift_or_athena",
         "b7-bedrock-for-ai-teams.html": "b7_bedrock"}
bad = 0
for page, script in PAGES.items():
    p = os.path.join(HERE, "..", "courses", page)
    if not os.path.exists(p):
        print(f"{page}: missing"); continue
    s = open(p).read()
    demo = s[s.find('id="demo-1"'):s.find('id="exercise"')]
    boxes = [(html.unescape(re.sub(r"<[^>]+>", "", m.group(1))), html.unescape(re.sub(r"<[^>]+>", "", m.group(2))))
             for m in re.finditer(r'<div class="prompt-box good"><span class="label">(.*?)</span>(.*?)</div>', demo, re.S)]
    code = "\n".join(b for _, b in boxes)
    src = [l.rstrip() for l in open(os.path.join(HERE, "buildalong", script + ".py")) if l.strip() and not l.lstrip().startswith("#")]
    have = set(l.rstrip() for l in code.splitlines())
    missing = [l for l in src if l not in have]
    outs = [b for lab, b in boxes if "real output" in lab]
    want = open(os.path.join(HERE, "buildalong", "outputs", script + ".txt")).read().strip()
    out_ok = bool(outs) and outs[-1].strip() == want
    if script == "b5_lambda" and outs:   # the timing line is allowed to differ
        strip = lambda t: "\n".join(l for l in t.splitlines() if "handler ran in" not in l)
        out_ok = strip(outs[-1].strip()) == strip(want)
    print(f"{page}: code lines missing {len(missing)}, output {'MATCH' if out_ok else 'DIFFERS'}")
    for l in missing[:5]: print("   missing:", l)
    bad += len(missing) + (not out_ok)
print("TOTAL problems", bad)
