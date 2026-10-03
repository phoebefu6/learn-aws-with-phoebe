/* Node runner for assets/aws-iam.js on materials/iam-cases.json; same output shape as iam_eval.py --json */
const path = require("path");
const iam = require(path.join(__dirname, "..", "assets", "aws-iam.js"));
const data = require(path.join(__dirname, "iam-cases.json"));
const C = data.cases;
const kinds = (r) => r.rows.map((x) => x.got);
const uni = (anti) => data.universe.map(([action, resource]) =>
  iam.evaluate(anti ? iam.withAntiLever(data.analyst) : data.analyst,
    { principal: data.user, action, resource, context: data.universe_ctx }).kind);
const out = {
  normal: kinds(iam.runCases(C)), flipDeny: kinds(iam.runCases(C, { flipDeny: true })),
  missingTrue: kinds(iam.runCases(C, { missingTrue: true })), anti: kinds(iam.runCases(C, null, iam.withAntiLever)),
  universe: uni(false), universe_anti: uni(true),
};
if (process.argv.includes("--json")) console.log(JSON.stringify(out));
else for (const k of ["normal", "flipDeny", "missingTrue", "anti"]) {
  const r = iam.runCases(C, k === "flipDeny" ? { flipDeny: true } : k === "missingTrue" ? { missingTrue: true } : null, k === "anti" ? iam.withAntiLever : null);
  console.log(k, "pass", r.pass + "/" + C.length, "allowed", r.allowed);
}
