/* learn-aws-with-phoebe - IAM policy evaluator (browser + node)
   Implements AWS's documented evaluation logic for ONE scope, stated on the widget:
   a request by an IAM user, inside a single account, with
     identity-based policies, an optional resource-based policy, an optional
     permissions boundary and an optional SCP.
   Not implemented (and refused rather than guessed): session policies, RCPs,
   cross-account requests, role sessions, policy variables, NotPrincipal,
   NotResource, ForAllValues/ForAnyValue, numeric/date/ARN operators.
   Order, from "Policy evaluation logic" (IAM User Guide):
     1 any applicable explicit Deny in any policy -> Deny
     2 an SCP is attached and none of its statements allows -> Deny (implicit)
     3 a resource-based policy allows this user's ARN directly -> Allow
       (same account: not limited by an implicit deny in identity or boundary)
     4 no identity-based statement allows -> Deny (implicit)
     5 a boundary is set and does not allow -> Deny (implicit)
     6 otherwise Allow (an IAM user is not a session principal)
   opts.flipDeny    : break mode, an Allow wins over an explicit Deny (wrong on purpose)
   opts.missingTrue : break mode, a condition key missing from the request matches (wrong on purpose) */
(function (root) {
  "use strict";

  function arr(x) { return x === undefined || x === null ? [] : (Array.isArray(x) ? x : [x]); }

  function globToRe(p, ci) {
    var s = "";
    for (var i = 0; i < p.length; i++) {
      var ch = p[i];
      if (ch === "*") s += ".*";
      else if (ch === "?") s += ".";
      else s += ch.replace(/[\\^$.|+()[\]{}\/-]/g, "\\$&");
    }
    return new RegExp("^" + s + "$", ci ? "i" : "");
  }

  /* Action: "The prefix and the action name are case insensitive"; * and ? wildcards. */
  function actionMatch(pattern, action) { return globToRe(pattern, true).test(action); }

  /* Resource: case sensitive; * and ? match within a colon-delimited ARN segment;
     a * that is the last character of the pattern's last segment may run past colons. */
  function resourceMatch(pattern, arn) {
    if (pattern === "*") return true;
    var P = pattern.split(":"), A = arn.split(":");
    if (P.length < 6 || A.length < 6) {
      /* fewer segments than an ARN: only a trailing * can absorb the rest */
      if (P.length > A.length) return false;
      for (var i = 0; i < P.length - 1; i++) if (!globToRe(P[i], false).test(A[i])) return false;
      var last = P[P.length - 1];
      var rest = A.slice(P.length - 1).join(":");
      if (P.length === A.length) return globToRe(last, false).test(rest);
      return last.slice(-1) === "*" && globToRe(last, false).test(rest);
    }
    var p6 = P.slice(0, 5).concat([P.slice(5).join(":")]);
    var a6 = A.slice(0, 5).concat([A.slice(5).join(":")]);
    for (var j = 0; j < 6; j++) if (!globToRe(p6[j], false).test(a6[j])) return false;
    return true;
  }

  function ipToInt(ip) {
    var p = ip.split(".");
    if (p.length !== 4) return null;
    var n = 0;
    for (var i = 0; i < 4; i++) {
      var v = Number(p[i]);
      if (!(v >= 0 && v <= 255) || p[i] === "") return null;
      n = n * 256 + v;
    }
    return n;
  }
  function inCidr(ip, cidr) {
    var parts = cidr.split("/"), bits = parts.length > 1 ? Number(parts[1]) : 32; /* no prefix = /32 */
    var a = ipToInt(ip), b = ipToInt(parts[0]);
    if (a === null || b === null) return false;
    var size = Math.pow(2, 32 - bits);
    return Math.floor(a / size) === Math.floor(b / size);
  }

  var OPS = {
    StringEquals: function (ctx, v) { return ctx === v; },
    StringNotEquals: function (ctx, v) { return ctx !== v; },
    StringLike: function (ctx, v) { return globToRe(v, false).test(ctx); },
    IpAddress: function (ctx, v) { return inCidr(ctx, v); },
    NotIpAddress: function (ctx, v) { return !inCidr(ctx, v); },
    Bool: function (ctx, v) { return String(ctx).toLowerCase() === String(v).toLowerCase(); }
  };
  var NEGATED = { StringNotEquals: true, NotIpAddress: true };

  /* Every operator in the block must hold (AND); every key in an operator must hold (AND);
     several values for one key: any one may match (OR), and for a negated operator none may match.
     A key absent from the request context: no match, except a negated operator, which is true. */
  function conditionHolds(cond, context, opts) {
    if (!cond) return true;
    for (var op in cond) {
      if (!Object.prototype.hasOwnProperty.call(cond, op)) continue;
      if (!OPS[op]) throw new Error("operator not implemented: " + op);
      for (var key in cond[op]) {
        if (!Object.prototype.hasOwnProperty.call(cond[op], key)) continue;
        var vals = arr(cond[op][key]).map(String);
        var has = Object.prototype.hasOwnProperty.call(context || {}, key);
        if (!has) {
          if (opts && opts.missingTrue) continue;
          if (NEGATED[op]) continue;
          return false;
        }
        var cv = String(context[key]);
        var ok = NEGATED[op]
          ? vals.every(function (v) { return OPS[op](cv, v); })
          : vals.some(function (v) { return OPS[op](cv, v); });
        if (!ok) return false;
      }
    }
    return true;
  }

  function principalMatch(principal, userArn) {
    if (principal === undefined) return true; /* identity policies carry no Principal */
    if (principal === "*") return true;
    var aws = principal && principal.AWS;
    return arr(aws).some(function (p) { return p === "*" || p === userArn; });
  }

  function statementApplies(st, req, opts, isResourcePolicy) {
    if (isResourcePolicy && !principalMatch(st.Principal, req.principal)) return false;
    var actOk;
    if (st.NotAction !== undefined) actOk = !arr(st.NotAction).some(function (a) { return actionMatch(a, req.action); });
    else actOk = arr(st.Action).some(function (a) { return actionMatch(a, req.action); });
    if (!actOk) return false;
    if (!arr(st.Resource).some(function (r) { return resourceMatch(r, req.resource); })) return false;
    return conditionHolds(st.Condition, req.context, opts);
  }

  function statements(policy) { return policy ? arr(policy.Statement) : []; }

  function scan(policies, effect, req, opts, isRes) {
    var hits = [];
    policies.forEach(function (pol) {
      statements(pol).forEach(function (st, i) {
        if (st.Effect === effect && statementApplies(st, req, opts, isRes)) hits.push((pol.name || "policy") + " #" + (st.Sid || i + 1));
      });
    });
    return hits;
  }

  function evaluate(set, req, opts) {
    opts = opts || {};
    var idp = arr(set.identity), rp = set.resource ? [set.resource] : [],
        bd = set.boundary ? [set.boundary] : [], scp = set.scp ? [set.scp] : [];
    var trace = [];
    var denies = [].concat(scan(scp, "Deny", req, opts), scan(rp, "Deny", req, opts, true),
                           scan(idp, "Deny", req, opts), scan(bd, "Deny", req, opts));
    var idAllow = scan(idp, "Allow", req, opts);
    var rpAllow = scan(rp, "Allow", req, opts, true);
    if (denies.length && !opts.flipDeny) {
      trace.push("1 explicit Deny found: " + denies.join(", "));
      return { decision: "Deny", kind: "explicit", by: denies[0], trace: trace };
    }
    if (denies.length && opts.flipDeny && (idAllow.length || rpAllow.length)) {
      trace.push("1 BROKEN: explicit Deny " + denies[0] + " ignored because an Allow exists");
      return { decision: "Allow", kind: "allow", by: (rpAllow[0] || idAllow[0]), trace: trace };
    }
    trace.push("1 no explicit Deny");
    if (scp.length) {
      var scpAllow = scan(scp, "Allow", req, opts);
      if (!scpAllow.length) { trace.push("2 SCP attached, nothing in it allows"); return { decision: "Deny", kind: "implicit", by: "SCP", trace: trace }; }
      trace.push("2 SCP allows: " + scpAllow[0]);
    } else trace.push("2 no SCP");
    if (rpAllow.length) { trace.push("3 resource policy allows this user directly: " + rpAllow[0]); return { decision: "Allow", kind: "allow", by: rpAllow[0], trace: trace }; }
    trace.push(rp.length ? "3 resource policy does not allow this user" : "3 no resource policy");
    if (!idAllow.length) { trace.push("4 no identity-based statement allows"); return { decision: "Deny", kind: "implicit", by: "identity", trace: trace }; }
    trace.push("4 identity allows: " + idAllow[0]);
    if (bd.length) {
      var bAllow = scan(bd, "Allow", req, opts);
      if (!bAllow.length) { trace.push("5 permissions boundary does not allow"); return { decision: "Deny", kind: "implicit", by: "boundary", trace: trace }; }
      trace.push("5 boundary allows: " + bAllow[0]);
    } else trace.push("5 no permissions boundary");
    trace.push("6 IAM user, not a session principal: Allow");
    return { decision: "Allow", kind: "allow", by: idAllow[0], trace: trace };
  }

  /* Run a table of cases; returns pass count and each verdict. */
  function runCases(cases, opts, mutate) {
    var out = { pass: 0, fail: 0, allowed: 0, rows: [] };
    cases.forEach(function (c) {
      var set = mutate ? mutate(c.set) : c.set;
      var r = evaluate(set, c.request, opts);
      var ok = r.kind === c.expect;
      if (ok) out.pass++; else out.fail++;
      if (r.decision === "Allow") out.allowed++;
      out.rows.push({ id: c.id, expect: c.expect, got: r.kind, ok: ok });
    });
    return out;
  }

  var ANTI_LEVER = { name: "wildcard", Statement: [{ Sid: "AllowEverything", Effect: "Allow", Action: "*", Resource: "*" }] };
  function withAntiLever(set) {
    var copy = JSON.parse(JSON.stringify(set));
    copy.identity = arr(copy.identity).concat([ANTI_LEVER]);
    return copy;
  }

  var api = { evaluate: evaluate, runCases: runCases, withAntiLever: withAntiLever, ANTI_LEVER: ANTI_LEVER,
              actionMatch: actionMatch, resourceMatch: resourceMatch, inCidr: inCidr };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.AwsIam = api;
})(this);
