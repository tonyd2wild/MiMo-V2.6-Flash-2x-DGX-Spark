#!/usr/bin/env python3
"""
stress-corrupt.py : corrupted-token + tool-call-storm detector for a vLLM OpenAI endpoint.

Usage:
  python3 /tmp/stress-corrupt.py --lane A=http://192.168.192.2:8888 [--lane B=http://...]
        [--model mimo-v2.6-flash] [--rounds 3] [--conc 4] [--out /tmp/stress-out]
        [--wait] [--probe long|tools|both]

Lanes are run strictly one after another (never simultaneously).
stdlib only.
"""
import argparse, json, os, re, sys, time, threading, statistics, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

TIMEOUT = 900
LINE_RE = re.compile(r'^\s*c\d{3}: 0x[0-9a-f]{6},?$')
# relaxed: tolerates quotes / uppercase / missing 0x / trailing spaces. Lines failing THIS are "hard_bad" (likely corruption)
RELAX_RE = re.compile(r"""^\s*['"]?c\d{3}['"]?\s*:\s*['"]?(0x)?[0-9a-fA-F]{6}['"]?\s*,?\s*$""")
# lines that are structural wrapper around the object literal, not counted as bad
STRUCT_RE = re.compile(r'^\s*((const|let|var)\s+)?PALETTE\s*=\s*\{\s*$|^\s*\}\s*;?\s*$|^\s*```\w*\s*$|^\s*$')

LONG_PROMPT = ("Output a JavaScript object literal named PALETTE with exactly 300 entries c000..c299, "
               "each a 6-digit lowercase hex colour, one per line, no comments, nothing else. "
               "Every line must have exactly this shape, unquoted, with a trailing comma: c017: 0x3fa2c1,")

TOOLS = [
    {"type": "function", "function": {"name": "grep", "description": "Search file contents for a regex pattern.",
        "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}},
                       "required": ["pattern", "path"]}}},
    {"type": "function", "function": {"name": "read", "description": "Read a file and return its contents with line numbers.",
        "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}},
    {"type": "function", "function": {"name": "write", "description": "Write content to a file, replacing it entirely.",
        "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}},
                       "required": ["file_path", "content"]}}},
    {"type": "function", "function": {"name": "todo_write", "description": "Replace the todo list.",
        "parameters": {"type": "object", "properties": {"todos": {"type": "array", "items": {"type": "object",
            "properties": {"content": {"type": "string"}, "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]}},
            "required": ["content", "status"]}}}, "required": ["todos"]}}},
]

TOOL_MESSAGES = [
    {"role": "system", "content": "You are a coding assistant working in the repository /work/app. Use the provided tools to make changes."},
    {"role": "user", "content": "There is a typo on line 218 of src/theme/palette.js, the gold entry is broken. Please fix it."},
    {"role": "assistant", "content": "", "tool_calls": [{"id": "call_read_1", "type": "function",
        "function": {"name": "read", "arguments": json.dumps({"file_path": "src/theme/palette.js"})}}]},
    {"role": "tool", "tool_call_id": "call_read_1", "content":
        "216:   amber: 0xf2a900,\n217:   honey: 0xe8b923,\n218:   gold: 0xf6c council,\n219:   sand: 0xd9c19c,\n220:   ochre: 0xcc7722,\n"},
]

print_lock = threading.Lock()
def log(*a):
    with print_lock:
        print(time.strftime("%H:%M:%S"), *a, flush=True)

# ---------------------------------------------------------------- HTTP helpers
def post_json(url, body, stream=False):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=TIMEOUT)

def wait_ready(base, model):
    while True:
        try:
            with urllib.request.urlopen(base + "/v1/models", timeout=10) as r:
                ids = [m.get("id") for m in json.load(r).get("data", [])]
            if model in ids:
                log(f"{base} ready, models={ids}")
                return
            log(f"{base} up but model {model!r} not in {ids}; waiting")
        except Exception as e:
            log(f"{base} not ready ({type(e).__name__}); waiting 30s")
        time.sleep(30)

# ---------------------------------------------------------------- probe 1: long generation
def stream_chat(base, body):
    """Return (content, reasoning, usage, finish_reason, tool_calls_by_index, n_chunks, raw_lines)."""
    body = dict(body); body["stream"] = True; body["stream_options"] = {"include_usage": True}
    content, reasoning, usage, finish, tcs, n_chunks, raw = [], [], None, None, {}, 0, []
    resp = post_json(base + "/v1/chat/completions", body, stream=True)
    for line in resp:
        line = line.decode("utf-8", "replace").rstrip("\n")
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            break
        try:
            obj = json.loads(payload)
        except Exception:
            raw.append("UNPARSEABLE_SSE: " + payload); continue
        if obj.get("usage"):
            usage = obj["usage"]
        for ch in obj.get("choices", []):
            d = ch.get("delta") or {}
            if d.get("content"):
                content.append(d["content"]); n_chunks += 1
            rc = d.get("reasoning_content") or d.get("reasoning")
            if rc:
                reasoning.append(rc)
            for tc in d.get("tool_calls") or []:
                i = tc.get("index", 0)
                slot = tcs.setdefault(i, {"id": None, "name": "", "arguments": ""})
                if tc.get("id"): slot["id"] = tc["id"]
                f = tc.get("function") or {}
                if f.get("name"): slot["name"] += f["name"]
                if f.get("arguments"): slot["arguments"] += f["arguments"]
            if ch.get("finish_reason"):
                finish = ch["finish_reason"]
    return "".join(content), "".join(reasoning), usage, finish, [tcs[k] for k in sorted(tcs)], n_chunks, raw

def analyze_long(text):
    lines = text.split("\n")
    bad, dup, nonascii, special = [], 0, 0, 0
    hard = []
    prev = None
    seen_idx = []
    for ln in lines:
        if not LINE_RE.match(ln) and not STRUCT_RE.match(ln):
            bad.append(ln)
            if not RELAX_RE.match(ln):
                hard.append(ln)
        if prev is not None and ln == prev and ln.strip():
            dup += 1
        prev = ln
        m = re.match(r'^\s*c(\d{3}):', ln)
        if m: seen_idx.append(int(m.group(1)))
    nonascii = sum(1 for ch in text if ord(ch) > 127)
    special = text.count("<|") + text.count("|>")
    good = sum(1 for ln in lines if LINE_RE.match(ln))
    missing = len(set(range(300)) - set(seen_idx))
    out_of_order = sum(1 for a, b in zip(seen_idx, seen_idx[1:]) if b != a + 1)
    return {"lines": len(lines), "good_lines": good, "bad_lines": len(bad), "bad_examples": bad[:3],
            "hard_bad": len(hard), "hard_examples": hard[:3],
            "dup_consecutive": dup, "non_ascii": nonascii, "special_tok": special,
            "missing_entries": missing, "out_of_order": out_of_order}

def run_long_one(base, model, name, n, outdir):
    body = {"model": model, "max_tokens": 6000, "messages": [{"role": "user", "content": LONG_PROMPT}]}
    t0 = time.time()
    try:
        content, reasoning, usage, finish, _, n_chunks, raw = stream_chat(base, body)
        err = None
    except Exception as e:
        content, reasoning, usage, finish, n_chunks, raw, err = "", "", None, "ERROR", 0, [], f"{type(e).__name__}: {e}"
    dt = time.time() - t0
    a = analyze_long(content)
    ctoks = (usage or {}).get("completion_tokens")
    rec = {"lane": name, "probe": "long", "n": n, "error": err, "finish_reason": finish, "secs": round(dt, 1),
           "completion_tokens": ctoks, "content_chunks": n_chunks, "reasoning_chars": len(reasoning), **a}
    path = os.path.join(outdir, f"{name}-long-{n:02d}.txt")
    with open(path, "w") as f:
        f.write("# " + json.dumps(rec) + "\n# ---- REASONING ----\n" + reasoning + "\n# ---- CONTENT ----\n" + content)
        if raw: f.write("\n# ---- RAW ISSUES ----\n" + "\n".join(raw))
    log(f"[{name} long #{n}] fin={finish} ctoks={ctoks} good={a['good_lines']} bad={a['bad_lines']} hard={a['hard_bad']} "
        f"nonascii={a['non_ascii']} dup={a['dup_consecutive']} special={a['special_tok']} missing={a['missing_entries']} {dt:.0f}s"
        + (f" ERR={err}" if err else ""))
    return rec

# ---------------------------------------------------------------- probe 2: tool storm
def check_tool_calls(tcs):
    """tcs: list of {name, arguments}. returns (n, n_bad, details)"""
    bad = 0; details = []
    for tc in tcs:
        args = tc.get("arguments")
        name = tc.get("name")
        problem = None
        if args is None or (isinstance(args, str) and args.strip() == ""):
            problem = "empty"
        elif isinstance(args, str):
            try:
                p = json.loads(args)
                if isinstance(p, dict) and not p: problem = "empty-object"
                elif not isinstance(p, dict): problem = "non-object"
            except Exception:
                problem = "unparseable"
        if not name: problem = (problem or "") + "+noname"
        if problem: bad += 1
        details.append({"name": name, "problem": problem, "args_head": (args or "")[:200] if isinstance(args, str) else str(args)[:200]})
    return len(tcs), bad, details

def run_tools_one(base, model, name, n, outdir, streaming):
    body = {"model": model, "max_tokens": 4000, "messages": TOOL_MESSAGES, "tools": TOOLS}
    t0 = time.time(); err = None; raw_text = ""
    try:
        if streaming:
            content, reasoning, usage, finish, tcs, _, raw = stream_chat(base, body)
            raw_text = "\n".join(raw)
        else:
            with post_json(base + "/v1/chat/completions", body) as r:
                obj = json.load(r)
            raw_text = json.dumps(obj, indent=1)
            ch = obj["choices"][0]; msg = ch["message"]
            finish = ch.get("finish_reason"); usage = obj.get("usage")
            content = msg.get("content") or ""
            reasoning = msg.get("reasoning_content") or msg.get("reasoning") or ""
            tcs = [{"id": t.get("id"), "name": (t.get("function") or {}).get("name"),
                    "arguments": (t.get("function") or {}).get("arguments")} for t in (msg.get("tool_calls") or [])]
    except urllib.error.HTTPError as e:
        err = f"HTTP {e.code}: {e.read()[:300]!r}"; content = reasoning = ""; usage = None; finish = "ERROR"; tcs = []
    except Exception as e:
        err = f"{type(e).__name__}: {e}"; content = reasoning = ""; usage = None; finish = "ERROR"; tcs = []
    dt = time.time() - t0
    n_tc, n_bad, details = check_tool_calls(tcs)
    storm = (n_tc > 4) or (n_bad > 0)
    special = content.count("<|") + reasoning.count("<|")
    nonascii = sum(1 for ch_ in content if ord(ch_) > 127)
    rec = {"lane": name, "probe": "tools-" + ("stream" if streaming else "nostream"), "n": n, "error": err,
           "finish_reason": finish, "secs": round(dt, 1), "completion_tokens": (usage or {}).get("completion_tokens"),
           "tool_calls": n_tc, "bad_arg_calls": n_bad, "storm": storm, "special_tok": special, "non_ascii": nonascii,
           "content_len": len(content), "reasoning_chars": len(reasoning), "calls": details}
    path = os.path.join(outdir, f"{name}-tools-{n:02d}.txt")
    with open(path, "w") as f:
        f.write("# " + json.dumps(rec) + "\n# ---- REASONING ----\n" + reasoning + "\n# ---- CONTENT ----\n" + content +
                "\n# ---- TOOL CALLS ----\n" + json.dumps(tcs, indent=1) + "\n# ---- RAW ----\n" + raw_text)
    log(f"[{name} {rec['probe']} #{n}] fin={finish} ctoks={rec['completion_tokens']} tool_calls={n_tc} bad_args={n_bad} "
        f"storm={storm} {dt:.0f}s " + " ".join(f"{d['name']}{'!'+d['problem'] if d['problem'] else ''}" for d in details)
        + (f" ERR={err}" if err else ""))
    return rec

# ---------------------------------------------------------------- driver
def run_lane(name, base, model, rounds, conc, outdir, probes):
    recs = []
    if "long" in probes:
        for r in range(rounds):
            log(f"== {name} long-generation round {r+1}/{rounds} (conc {conc})")
            with ThreadPoolExecutor(conc) as ex:
                futs = [ex.submit(run_long_one, base, model, name, r * conc + i + 1, outdir) for i in range(conc)]
                recs += [f.result() for f in futs]
    if "tools" in probes:
        for r in range(rounds):
            log(f"== {name} tool-storm round {r+1}/{rounds} (conc {conc}, half stream / half non-stream)")
            with ThreadPoolExecutor(conc) as ex:
                futs = [ex.submit(run_tools_one, base, model, name, r * conc + i + 1, outdir, bool(i % 2)) for i in range(conc)]
                recs += [f.result() for f in futs]
    return recs

def summarize(all_recs):
    rows = []
    groups = {}
    for r in all_recs:
        groups.setdefault((r["lane"], r["probe"]), []).append(r)
    print("\n" + "=" * 119)
    print(f"{'lane':<5}{'probe':<16}{'reqs':>5}{'errs':>5}{'bad_lines':>10}{'hard_bad':>9}{'non_ascii':>10}{'special':>8}{'dup':>5}{'storms':>7}{'badargs':>8}{'mean_ctoks':>11}{'mean_s':>8}")
    print("-" * 119)
    for (lane, probe), rs in sorted(groups.items()):
        ctoks = [r["completion_tokens"] for r in rs if r.get("completion_tokens") is not None]
        row = {"lane": lane, "probe": probe, "reqs": len(rs), "errs": sum(1 for r in rs if r["error"]),
               "bad_lines": sum(r.get("bad_lines", 0) for r in rs), "hard_bad": sum(r.get("hard_bad", 0) for r in rs), "non_ascii": sum(r.get("non_ascii", 0) for r in rs),
               "special": sum(r.get("special_tok", 0) for r in rs), "dup": sum(r.get("dup_consecutive", 0) for r in rs),
               "storms": sum(1 for r in rs if r.get("storm")), "badargs": sum(r.get("bad_arg_calls", 0) for r in rs),
               "mean_ctoks": round(statistics.mean(ctoks), 1) if ctoks else None,
               "mean_s": round(statistics.mean(r["secs"] for r in rs), 1)}
        rows.append(row)
        print(f"{lane:<5}{probe:<16}{row['reqs']:>5}{row['errs']:>5}{row['bad_lines']:>10}{row['hard_bad']:>9}{row['non_ascii']:>10}{row['special']:>8}{row['dup']:>5}{row['storms']:>7}{row['badargs']:>8}{str(row['mean_ctoks']):>11}{row['mean_s']:>8}")
    print("=" * 119)
    # examples
    print("\nBad-line examples (first 3 per request with bad lines):")
    for r in all_recs:
        if r.get("bad_lines"):
            print(f"  [{r['lane']} long #{r['n']}] bad={r['bad_lines']} hard_bad={r['hard_bad']} good={r['good_lines']} fin={r['finish_reason']} ctoks={r['completion_tokens']}")
            for ln in r["bad_examples"]:
                print("     bad : " + repr(ln)[:200])
            for ln in r["hard_examples"]:
                print("     HARD: " + repr(ln)[:200])
    print("\nStorm examples:")
    for r in all_recs:
        if r.get("storm"):
            print(f"  [{r['lane']} {r['probe']} #{r['n']}] tool_calls={r['tool_calls']} bad_args={r['bad_arg_calls']} fin={r['finish_reason']} ctoks={r['completion_tokens']}")
            for d in r["calls"][:6]:
                print(f"     {d['name']} {d['problem'] or 'ok'}: {d['args_head'][:120]!r}")
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", action="append", required=True, help="NAME=http://host:port (repeatable, run sequentially)")
    ap.add_argument("--model", default="mimo-v2.6-flash")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--conc", type=int, default=4)
    ap.add_argument("--out", default="/tmp/stress-out")
    ap.add_argument("--wait", action="store_true", help="poll /v1/models every 30s until model listed")
    ap.add_argument("--probe", default="both", choices=["long", "tools", "both"])
    ap.add_argument("--tag", default=time.strftime("%Y%m%d-%H%M%S"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    probes = ["long", "tools"] if args.probe == "both" else [args.probe]
    all_recs = []
    for spec in args.lane:
        name, base = spec.split("=", 1)
        base = base.rstrip("/")
        if args.wait:
            wait_ready(base, args.model)
        log(f"#### LANE {name} {base} model={args.model} rounds={args.rounds} conc={args.conc}")
        recs = run_lane(name, base, args.model, args.rounds, args.conc, args.out, probes)
        all_recs += recs
        with open(os.path.join(args.out, f"{name}-records-{args.tag}.json"), "w") as f:
            json.dump(recs, f, indent=1)
    rows = summarize(all_recs)
    with open(os.path.join(args.out, f"summary-{args.tag}.json"), "w") as f:
        json.dump({"rows": rows, "args": vars(args)}, f, indent=1)

if __name__ == "__main__":
    main()
