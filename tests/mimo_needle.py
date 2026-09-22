# Needle-in-haystack: hide a code at a given depth in N tokens of filler, ask for it back (temperature 0).
import json, random, sys, time, urllib.request
U = sys.argv[1]; targets = [int(x) for x in sys.argv[2].split(",")]; depths = [float(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "0.1,0.5,0.9").split(",")]
W = ("amber basin cedar delta ember fjord garnet harbor iris juniper kestrel lumen meadow nimbus orchid "
     "pylon quartz raven sierra tundra umber vessel willow xenon yarrow zephyr").split()
for n in targets:
    for d in depths:
        rnd = random.Random(n * 10 + int(d * 10)); words = [f"{rnd.choice(W)}{rnd.randint(0, 999)}" for _ in range(int(n * 0.215))]
        code = f"{rnd.randint(100000, 999999)}"; words.insert(int(len(words) * d), f". The secret vault code is {code}. ")
        prompt = " ".join(words) + "\n\nWhat is the secret vault code mentioned in the text above? Reply with just the number."
        body = {"model": "mimo-v2.6-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 20, "temperature": 0,
                "chat_template_kwargs": {"enable_thinking": False}}
        t = time.time()
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(U, json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=1800))
            ans = r["choices"][0]["message"]["content"].strip(); pt = r["usage"]["prompt_tokens"]
            print(f"needle {pt:>7} tok depth {d:.1f}: {'PASS' if code in ans else 'FAIL'} (want {code}, got {ans[:30]!r}) {time.time()-t:.0f}s", flush=True)
        except Exception as e:
            print(f"needle {n} depth {d}: ERROR {e}", flush=True)
