import json,time,urllib.request,sys
U=sys.argv[1]
def run(prompt,mt=600,think=False):
    body={"model":"mimo-v2.6-flash","messages":[{"role":"user","content":prompt}],"max_tokens":mt,"temperature":0.6,"stream":True,"stream_options":{"include_usage":True},"chat_template_kwargs":{"enable_thinking":think}}
    r=urllib.request.urlopen(urllib.request.Request(U,json.dumps(body).encode(),{"Content-Type":"application/json"}),timeout=900)
    t0=time.time();first=None;txt="";rs="";usage=None
    for line in r:
        line=line.decode().strip()
        if not line.startswith("data:") or line.endswith("[DONE]"): continue
        d=json.loads(line[5:])
        if d.get("usage"): usage=d["usage"]
        for c in d.get("choices",[]):
            dl=c.get("delta",{})
            if (dl.get("content") or dl.get("reasoning_content") or dl.get("reasoning")) and first is None: first=time.time()
            txt+=dl.get("content") or ""; rs+=(dl.get("reasoning_content") or dl.get("reasoning") or "")
    t1=time.time(); n=usage["completion_tokens"]
    print(f"ttft {first-t0:.2f}s  tokens {n}  decode {(n-1)/(t1-first):.1f} tok/s  reasoning_chars {len(rs)}")
    print("  "+txt[:400].replace("\n"," | "))
run("What is 17*23? Answer in one line.",100)
run("Write a Python function that returns the n-th Fibonacci number iteratively, with a docstring and 3 doctests.",600)
run("Explain in about 250 words how a bloom filter works and when to use one.",600)
