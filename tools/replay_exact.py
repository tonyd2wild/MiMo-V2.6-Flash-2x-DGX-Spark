# Replay a captured request body exactly (only toggling stream), N times; count tool calls per response.
import json, sys, time, urllib.request
U=sys.argv[1]; body0=json.load(open(sys.argv[2])); N=int(sys.argv[3]); stream=sys.argv[4]=="stream"
for i in range(N):
    body=dict(body0); body["stream"]=stream
    if not stream: body.pop("stream_options",None)
    t=time.time(); r=urllib.request.urlopen(urllib.request.Request(U,json.dumps(body).encode(),{"Content-Type":"application/json"}),timeout=3600)
    if stream:
        calls={}; fin=None; toks=None
        for line in r:
            line=line.decode().strip()
            if not line.startswith("data:") or line.endswith("[DONE]"): continue
            d=json.loads(line[5:])
            if d.get("usage"): toks=d["usage"]["completion_tokens"]
            for c in d.get("choices",[]):
                fin=c.get("finish_reason") or fin
                for tc in (c.get("delta") or {}).get("tool_calls") or []:
                    calls.setdefault(tc["index"],{"name":None,"args":""})
                    if tc.get("function",{}).get("name"): calls[tc["index"]]["name"]=tc["function"]["name"]
                    calls[tc["index"]]["args"]+=tc.get("function",{}).get("arguments") or ""
        n=len(calls); names=" ".join((v["name"] or "?")[:4] for v in calls.values())
    else:
        d=json.load(r); c=d["choices"][0]; tcs=c["message"].get("tool_calls") or []; n=len(tcs); fin=c["finish_reason"]; toks=d["usage"]["completion_tokens"]; names=" ".join(t["function"]["name"][:4] for t in tcs)
    print(f"{'stream' if stream else 'nostream'} run{i+1}: finish={fin} tokens={toks} calls={n} {time.time()-t:.0f}s {names[:100]}",flush=True)
