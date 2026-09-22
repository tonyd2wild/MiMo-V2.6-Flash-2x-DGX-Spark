# Audio + video smoke test. usage: mimo_media.py <chat-completions url> <speech.wav> <motion.mp4>
# speech.wav says "The secret password is purple elephant."; motion.mp4 is a red box sliding right on white.
import base64, json, sys, time, urllib.request, urllib.error
U, WAV, MP4 = sys.argv[1:4]
b64 = lambda p: base64.b64encode(open(p, "rb").read()).decode()
def ask(parts, label):
    body = {"model": "mimo-v2.6-flash", "max_tokens": 120, "temperature": 0, "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{"role": "user", "content": parts}]}
    t = time.time()
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(U, json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=900))
        print(f"{label} {time.time()-t:.1f}s prompt_tokens {r['usage']['prompt_tokens']}: {r['choices'][0]['message']['content'][:300]!r}", flush=True)
    except urllib.error.HTTPError as e:
        print(f"{label} HTTP {e.code}: {e.read().decode()[:300]}", flush=True)
ask([{"type": "input_audio", "input_audio": {"data": b64(WAV), "format": "wav"}},
     {"type": "text", "text": "Transcribe this audio exactly, then tell me the secret password."}], "audio(input_audio)")
ask([{"type": "audio_url", "audio_url": {"url": "data:audio/wav;base64," + b64(WAV)}},
     {"type": "text", "text": "What is the secret password in this audio?"}], "audio(audio_url)")
ask([{"type": "video_url", "video_url": {"url": "data:video/mp4;base64," + b64(MP4)}},
     {"type": "text", "text": "Describe this video: what object is shown, what color is it, and which direction does it move?"}], "video")
