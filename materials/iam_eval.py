"""Python port of assets/aws-iam.js. Same scope, same order, same break modes.

Run: python3 iam_eval.py            -> prints the canon lines the bench must reproduce
     python3 iam_eval.py --json     -> machine-readable verdicts, compared against node by compare-iam.sh
"""
import ipaddress, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def arr(x):
    return [] if x is None else (x if isinstance(x, list) else [x])


def glob_re(p, ci):
    s = "".join(".*" if ch == "*" else "." if ch == "?" else re.escape(ch) for ch in p)
    return re.compile("^" + s + "$", re.I if ci else 0)


def action_match(pattern, action):
    return bool(glob_re(pattern, True).match(action))


def resource_match(pattern, arn):
    if pattern == "*":
        return True
    P, A = pattern.split(":"), arn.split(":")
    if len(P) < 6 or len(A) < 6:
        if len(P) > len(A):
            return False
        for i in range(len(P) - 1):
            if not glob_re(P[i], False).match(A[i]):
                return False
        last, rest = P[-1], ":".join(A[len(P) - 1:])
        if len(P) == len(A):
            return bool(glob_re(last, False).match(rest))
        return last.endswith("*") and bool(glob_re(last, False).match(rest))
    p6 = P[:5] + [":".join(P[5:])]
    a6 = A[:5] + [":".join(A[5:])]
    return all(glob_re(p6[j], False).match(a6[j]) for j in range(6))


def in_cidr(ip, cidr):
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr if "/" in cidr else cidr + "/32", strict=False)
    except ValueError:
        return False


OPS = {
    "StringEquals": lambda c, v: c == v,
    "StringNotEquals": lambda c, v: c != v,
    "StringLike": lambda c, v: bool(glob_re(v, False).match(c)),
    "IpAddress": in_cidr,
    "NotIpAddress": lambda c, v: not in_cidr(c, v),
    "Bool": lambda c, v: str(c).lower() == str(v).lower(),
}
NEGATED = {"StringNotEquals", "NotIpAddress"}


def condition_holds(cond, ctx, opts):
    if not cond:
        return True
    for op, block in cond.items():
        if op not in OPS:
            raise ValueError("operator not implemented: " + op)
        for key, vals in block.items():
            vals = [str(v) for v in arr(vals)]
            if key not in (ctx or {}):
                if opts.get("missingTrue") or op in NEGATED:
                    continue
                return False
            cv = str(ctx[key])
            ok = all(OPS[op](cv, v) for v in vals) if op in NEGATED else any(OPS[op](cv, v) for v in vals)
            if not ok:
                return False
    return True


def principal_match(principal, user):
    if principal is None or principal == "*":
        return True
    return any(p == "*" or p == user for p in arr((principal or {}).get("AWS")))


def applies(st, req, opts, is_res):
    if is_res and not principal_match(st.get("Principal"), req["principal"]):
        return False
    if "NotAction" in st:
        act_ok = not any(action_match(a, req["action"]) for a in arr(st["NotAction"]))
    else:
        act_ok = any(action_match(a, req["action"]) for a in arr(st.get("Action")))
    if not act_ok:
        return False
    if not any(resource_match(r, req["resource"]) for r in arr(st.get("Resource"))):
        return False
    return condition_holds(st.get("Condition"), req.get("context"), opts)


def scan(policies, effect, req, opts, is_res=False):
    hits = []
    for pol in policies:
        for i, st in enumerate(arr(pol.get("Statement"))):
            if st.get("Effect") == effect and applies(st, req, opts, is_res):
                hits.append(f"{pol.get('name', 'policy')} #{st.get('Sid', i + 1)}")
    return hits


def evaluate(s, req, opts=None):
    opts = opts or {}
    idp = arr(s.get("identity"))
    rp = [s["resource"]] if s.get("resource") else []
    bd = [s["boundary"]] if s.get("boundary") else []
    scp = [s["scp"]] if s.get("scp") else []
    denies = scan(scp, "Deny", req, opts) + scan(rp, "Deny", req, opts, True) + scan(idp, "Deny", req, opts) + scan(bd, "Deny", req, opts)
    id_allow, rp_allow = scan(idp, "Allow", req, opts), scan(rp, "Allow", req, opts, True)
    if denies and not opts.get("flipDeny"):
        return "explicit"
    if denies and opts.get("flipDeny") and (id_allow or rp_allow):
        return "allow"
    if scp and not scan(scp, "Allow", req, opts):
        return "implicit"
    if rp_allow:
        return "allow"
    if not id_allow:
        return "implicit"
    if bd and not scan(bd, "Allow", req, opts):
        return "implicit"
    return "allow"


ANTI = {"name": "wildcard", "Statement": [{"Sid": "AllowEverything", "Effect": "Allow", "Action": "*", "Resource": "*"}]}


def with_anti(s):
    c = json.loads(json.dumps(s))
    c["identity"] = arr(c.get("identity")) + [ANTI]
    return c


def run(cases, opts=None, mutate=None):
    rows = [(c["id"], c["expect"], evaluate(mutate(c["set"]) if mutate else c["set"], c["request"], opts)) for c in cases]
    return {"pass": sum(e == g for _, e, g in rows), "allowed": sum(g == "allow" for _, _, g in rows), "rows": rows}


def universe(data, anti=False):
    s = with_anti(data["analyst"]) if anti else data["analyst"]
    out = []
    for action, res in data["universe"]:
        out.append(evaluate(s, {"principal": data["user"], "action": action, "resource": res, "context": data["universe_ctx"]}))
    return out


if __name__ == "__main__":
    data = json.load(open(os.path.join(HERE, "iam-cases.json")))
    C = data["cases"]
    res = {
        "normal": run(C), "flipDeny": run(C, {"flipDeny": True}), "missingTrue": run(C, {"missingTrue": True}),
        "anti": run(C, None, with_anti), "universe": universe(data), "universe_anti": universe(data, True),
    }
    if "--json" in sys.argv:
        print(json.dumps({k: (v if k.startswith("universe") else [g for _, _, g in v["rows"]]) for k, v in res.items()}))
    else:
        n = len(C)
        print(f"cases {n}")
        for k in ("normal", "flipDeny", "missingTrue", "anti"):
            r = res[k]
            print(f"{k:12s} pass {r['pass']}/{n}  fail {n - r['pass']}  allowed {r['allowed']}/{n}")
        print("universe allowed", res["universe"].count("allow"), "of", len(data["universe"]),
              "| with Action:* ", res["universe_anti"].count("allow"))
        for (a, r), g0, g1 in zip(data["universe"], res["universe"], res["universe_anti"]):
            print(f"  {a:38s} {g0:9s} -> {g1}")
        for cid, e, g in res["flipDeny"]["rows"]:
            if e != g:
                print("  flip fails", cid, e, "->", g)
        for cid, e, g in res["missingTrue"]["rows"]:
            if e != g:
                print("  missing fails", cid, e, "->", g)
