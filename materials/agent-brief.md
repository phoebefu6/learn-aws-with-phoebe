# Agent brief - shared by every fan-out page of learn-aws-with-phoebe

You are writing ONE static HTML session page. No servers, no npm. **If your target file already
exists on disk, do not write it; report that and stop.** Write the file, return its path and one
line of coverage. No HTML in your reply.

## Read first, in this order

1. The template page for YOUR track. Copy its structure, classes, SVG grammar and quiz markup
   EXACTLY, including how many options each question has (4):
   - Leader track (a1-a6, no code): `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-aws-with-phoebe/courses/a1-what-aws-is-to-a-data-team.html`
   - Analyst track (b1-b8, Python): `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-aws-with-phoebe/courses/b1-s3-layout-and-parquet.html` (the bench page `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-aws-with-phoebe/courses/b8-the-iam-and-cost-bench.html` is also a model for tables of canon numbers)
2. The source map: every verified number, its evidence tier, per-session coverage, the seams. Use
   ONLY its numbers; never invent a statistic; if a fact is missing, teach the uncertainty.
   `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-aws-with-phoebe/materials/official-course-map.md`
   Deeper quotes with URLs: `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-aws-with-phoebe/materials/sources-aws-docs.md`
3. Analyst pages only: your build-along script and its REAL output, which you paste verbatim:
   `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-aws-with-phoebe/materials/buildalong/<script>.py` and
   `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-aws-with-phoebe/materials/buildalong/outputs/<script>.txt`.
   Show the code in 2-4 step boxes (split the script; keep it runnable when concatenated), then the
   output box labelled "(real output)". Never edit an output line. Where the output contains a
   timing ("handler ran in 0.04 s on this laptop"), say timings vary by machine.
4. The stylesheet `:root` block for the palette tokens: `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-aws-with-phoebe/assets/style.css`

## Page skeleton (keep every component)

toolbar (crumb EXACTLY "Leader session N of 6" or "Analyst session N of 8" after the repo link, as in
the template, #toggle-all, #zoom-toggle) · masthead (eyebrow "Learn AWS with Phoebe · Leader track ·
Session N of 6" or "... · Analyst track · Session N of 8", h1 with one `<span class="accent">`, .sub,
.chip-row with the level chip 🟢 Foundations (sessions 1-2) / 🟡 Core (3-4) / 🟠 Applied (5-7) /
🔴 Capstone (leader 6), audience chips as in the template, time chip "45 min", .agenda a1-a4) ·
main.wrap · section#intro (Part 0: kicker, .lede, .legend pills, .callout.win "★ What you walk out
with tonight") · 3 Parts, each `section.section#part-N` with section-kicker (klabel "Part N · covers
...", h2, `.tag.concept "N min live"`), a `.lede`, ONE figure, `details.card` accordions (summary:
`.mode.live` or `.mode.self`, title, `.mini`, `.caret ▶`), at least one `.callout.example` with
`span.ex-pill` "Real world" on the page · section#demo-1 Build-along (kicker `.tag.demo "★ 22 min ·
everyone builds"`, .lede, ONE figure, `.steps > .step`, each with a `.prompt-box.good` carrying a
`span.label`; leader pages: a paper exercise with worked example boxes; analyst pages: setup box
pointing back to analyst session 1's environment, the split script, the real output, then a
`.callout.tip` "On a real Free Tier account (optional)" whose first sentence is EXACTLY "Needs an AWS
account: AWS says most new customers are not asked for a card on the Free plan, some are, and a Paid
plan needs one." followed by what changes and what it costs, using Price List numbers from the map)
· section#exercise Homework (ol, 4 items) · section#quiz (3 x `.quiz-q data-answer="0-based"`,
`p.qtext`, 4 x `button.qopt` "A · ...", `p.qwhy`; one `p.quiz-score` after the last; vary the correct
letter) · section#official, h2 EXACTLY "What this session teaches, and where it came from",
`.covered > .covered-row` (pill solid ✓ / light ◐ + name + note), then the `.mono` line EXACTLY
"Every fact on this page, and its verification tier, is recorded in the course's source map." ·
section.cheat#cheatsheet (h3 "Leader session N cheat sheet <span>· pin this</span>" or "Analyst
session N cheat sheet ...", .grid-2 of six .cheat-item) · `.callout.next` with `.nx-pill` "Next
session" · footer.pagefoot · `<script src="../assets/app.js?v=1"></script>`.

Head: the template's social meta block with this page's own title/description/url;
`<title>Leader session N · Title - learn aws with phoebe</title>` (or Analyst);
`<link rel="stylesheet" href="../assets/style.css?v=1">`. Nothing else external.

First `details.card` in the FIRST Part is `open`; no other. Sentence case headings. Warm
practitioner voice, concrete, never dry. Inside prompt-boxes escape `&` `<` `>`. 450 to 650 lines
is guidance about depth, never a target: never collapse whitespace, dissolve a list into a
paragraph, or drop a component to fit.

## Hard rules (a violation is rework)

- NEVER an em dash or en dash, anywhere (prose, code, aria-labels, comments). Hyphen only.
- No meta text: never "this course", "in this course", "the course teaches", "banned here". Say
  "these pages" or name the session. State the professional norm directly with its reason.
- Attribution "by Phoebe Fu". Never "built with" a tool.
- Every number comes from the map (sections 3 and 4) or is labelled constructed or modelled. For
  constructed examples print "your numbers will differ"; never invent outputs as if run.
- Prices: always say "us-east-1, AWS Price List, 3 October 2026" near a dollar figure, and that
  prices must be re-verified before relying on them. Never quote a price that is not in the map.
- Contested or missing evidence: teach the disagreement; never resolve what the literature has not.
  Things the map marks "could not verify" (e.g. a 30-day hard rule before Standard-IA transitions,
  a 128 MB file-size target) must NOT be stated as rules.
- Citations in the exact form of the map's appendix; anything marked secondary is "reported".
- NEVER "lottery" or "lotteries". NEVER the bullet "✗" in prose lists (only the existing `prompt-box
  bad` label pattern from the template is allowed).
- Default to the English word. No Chinese terms.
- Seams: link, never teach (map section 1). IAM concepts like RBAC/ABAC belong to
  learn-data-access-control; warehouse modelling to learn-data-warehouse; pipelines to
  learn-data-engineering and learn-data-orchestration; MLOps to learn-dataops; GPU/inference infra
  to learn-ai-infra; streaming to learn-streaming-data.
- Titles, widget ids and class names must not collide with siblings: do not reuse "The policy bench",
  "Who can see what", "Cost and performance", "Performance and cost"; no new CSS classes (use only
  classes that exist in the template pages and style.css); no element ids beyond the section ids.
- moto honesty: moto is a mock; say so where it matters (it accepted a 901 s Lambda timeout real
  Lambda rejects; its IAM enforcement is a teaching aid, not AWS's engine).

## Figure grammar (hand-drawn, every figure)

Palette, ONLY these hexes (no invented greys): ink #232F3E · muted #4E5A6B · accent #183177 ·
deep #0E1F52 · mid #2B4A9A · soft #B9C4E6 · tint #EEF1FA · faint #C5CCD8 · hairline #E3E7EE ·
orange #FF9900 (fill only) · orange ink #5C3300 · orange tint #FFF3E0 · `#FFFFFF` · universal reds
`#991B1B` `#FEF2F2` `#FCA5A5` only for a wrong-way panel. Text on an orange fill is #232F3E or
#5C3300, never white; text on #183177 or #0E1F52 fills is #FFFFFF.

- `<figure class="zoomable">` > `<svg viewBox="0 0 880 H" role="img" aria-label="the data, not the
  shape">` > `<defs>` + `<style>` + content, then `<figcaption>🔍 Click to zoom - takeaway</figcaption>`.
  Grow H, never W.
- Prefix unique per figure, used for every class and id: `<page><letter>` e.g. `a2a`, `a2b`, `b5c`
  (a, b, c for Parts 1-3, d for the build-along).
- `<defs>` holds with prefix P: a wobble filter `id="PSk"` (`feTurbulence type="fractalNoise"
  baseFrequency="0.02" numOctaves="2" seed="<int>"` + `feDisplacementMap scale="2.4"
  xChannelSelector="R" yChannelSelector="G"`, `x="-3%" y="-3%" width="106%" height="106%"`), a hachure
  pattern `id="PHc"` (7x7 userSpaceOnUse, rotate(-38), one #183177 line, opacity .5), an open
  arrowhead `id="PAr"` (path `M1 1 L9 5 L1 9`, fill none, ink stroke 1.6). ALL shapes sit inside ONE
  `<g filter="url(#PSk)" fill="none" stroke="#232F3E" stroke-width="2" stroke-linecap="round"
  stroke-linejoin="round">`; rects carry a tiny rotation (-4 to 4 degrees for hand-placed items,
  under 1 for panels). Fills: white, tint, the hachure for "the pile" or "the data", and orange ONLY
  for the one thing the figure is about. Text classes: `.PH` 800 12px ink heading · `.PL` 600 12px
  ink label · `.PS` 400 11px muted · `.PB` 800 11px orange-ink · `.PV` 800 16-20px deep value · `.PW`
  800 12px white on a navy fill · `.PA` 700 11px accent axis caption · `.PN` 400 12px muted note.
  Do not override a class's fill with an inline style.
- ALL `<text>` outside the filtered group, sans stack, never below 10.5px.
- Lines and arrows must not pass through text (the gate flags "line-through-text"): route arrows
  around labels or stop them at box edges.
- Fit: max chars ≈ (box width - 20) / 7 at 12px, 6.4px/char at 11px; full-width note under 110
  chars; 40px between neighbouring point labels; bottom note 22px below the last row, H clears it by
  8px. When in doubt, shorten.
- Floor: one figure per Part plus one in the build-along. Draw the MECHANISM (a key prefix being
  pruned, a request walking the evaluation steps, a lifecycle waterfall, a meter running while a
  warehouse idles, a batch job queue), never a metaphor literally, never decoration.

## Voice and honesty

Every Part gets a real-world story. Real-world stories that are composites say "constructed" in
the callout or the coverage row. AWS facts are quoted from the map with their page names.

## Cross-links (absolute URLs)

- learn-data-warehouse: https://phoebefu6.github.io/learn-data-warehouse-with-phoebe/
- learn-data-engineering: https://phoebefu6.github.io/learn-data-engineering-with-phoebe/
- learn-data-orchestration: https://phoebefu6.github.io/learn-data-orchestration-with-phoebe/
- learn-data-access-control: https://phoebefu6.github.io/learn-data-access-control-with-phoebe/
- learn-dataops: https://phoebefu6.github.io/learn-dataops-with-phoebe/
- learn-ai-infra: https://phoebefu6.github.io/learn-ai-infra-with-phoebe/
- learn-streaming-data: https://phoebefu6.github.io/learn-streaming-data-with-phoebe/
- learn-claude session 68: https://phoebefu6.github.io/learn-claude-with-phoebe/courses/68-bedrock-vertex.html
- Hub: https://phoebefu6.github.io/learn-with-phoebe/

## Footer chain(s) and session titles

Footer left: "Leader session N of 6 · learn-aws-with-phoebe · by Phoebe Fu &nbsp;·&nbsp; 📚 <a href="https://phoebefu6.github.io/learn-with-phoebe/">Learn with Phoebe ↗</a>" (Analyst: "Analyst session N of 8 · ...").
Footer right: "<a href="prev.html">← Prev: Title</a> &nbsp;·&nbsp; <a href="next.html">Next: Title →</a>"; leader 6 ends "← Prev ... &nbsp;·&nbsp; <a href="../index.html">Course home</a>".

Leader chain: a1-what-aws-is-to-a-data-team.html "What AWS is to a data team" → a2-s3-is-the-lake.html
"S3 is the lake" → a3-who-can-touch-what.html "Who can touch what" → a4-compute-or-serverless.html
"Compute or serverless" → a5-the-bill-you-did-not-plan.html "The bill you did not plan" →
a6-a-data-platform-on-one-page.html "A data platform on one page".
Analyst chain: b1-s3-layout-and-parquet.html "S3 layout and Parquet" → b2-iam-policies-as-code.html
"IAM policies as code" → b3-the-glue-catalog.html "The Glue Data Catalog" →
b4-athena-pay-per-byte.html "Athena: pay per byte scanned" → b5-lambda-or-a-container.html "Lambda or
a container" → b6-redshift-or-athena.html "Redshift or Athena" → b7-bedrock-for-ai-teams.html "Bedrock
for AI teams" → b8-the-iam-and-cost-bench.html "The IAM and cost bench".
