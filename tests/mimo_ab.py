# Greedy A/B: same prompts on both lanes, decode tok/s + DFlash acceptance from /metrics deltas.
import json,time,urllib.request,re
L={"A":"http://192.168.192.2:8888","B":"http://192.168.192.1:8888"}
P=["Write a Python function that returns the n-th Fibonacci number iteratively, with a docstring and 3 doctests.",
   "Explain in about 250 words how a bloom filter works and when to use one.",
   "Write a bash script that finds the 10 largest files under a directory and prints their sizes in human-readable form."]
def metrics(u):
    t=urllib.request.urlopen(u+"/metrics",timeout=10).read().decode(); d={}
    for k in ("vllm:spec_decode_num_drafts_total","vllm:spec_decode_num_draft_tokens_total","vllm:spec_decode_num_accepted_tokens_total"):
        d[k]=sum(float(m) for m in re.findall(r"^"+re.escape(k)+r"(?:\{[^}]*\})? ([0-9.e+]+)$",t,re.M))
    return d
def run(u,p):
    body={"model":"mimo-v2.6-flash","messages":[{"role":"user","content":p}],"max_tokens":400,"temperature":0,"stream":True,"stream_options":{"include_usage":True},"chat_template_kwargs":{"enable_thinking":False}}
    r=urllib.request.urlopen(urllib.request.Request(u+"/v1/chat/completions",json.dumps(body).encode(),{"Content-Type":"application/json"}),timeout=600)
    first=None;n=0
    for line in r:
        line=line.decode().strip()
        if not line.startswith("data:") or line.endswith("[DONE]"): continue
        d=json.loads(line[5:])
        if d.get("usage"): n=d["usage"]["completion_tokens"]
        if first is None and any(c.get("delta",{}).get("content") for c in d.get("choices",[])): first=time.time()
    return n,(n-1)/(time.time()-first)
for name,u in L.items():
    run(u,"hi")  # warm
    for p in P:
        m0=metrics(u); n,tps=run(u,p); m1=metrics(u)
        dr=m1["vllm:spec_decode_num_drafts_total"]-m0["vllm:spec_decode_num_drafts_total"]
        acc=m1["vllm:spec_decode_num_accepted_tokens_total"]-m0["vllm:spec_decode_num_accepted_tokens_total"]
        print(f"{name} {p[:28]:28s} tokens {n:4d}  {tps:5.1f} tok/s  accepted/draft {acc/dr if dr else 0:.2f}")
