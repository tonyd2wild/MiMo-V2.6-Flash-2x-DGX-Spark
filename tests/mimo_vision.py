# Vision smoke test: draws a known image locally (no downloads), asks the model to describe it.
import base64, io, json, sys, time, urllib.request
from PIL import Image, ImageDraw
U=sys.argv[1]
img=Image.new("RGB",(512,384),"white"); d=ImageDraw.Draw(img)
d.rectangle([40,40,220,200],fill="red"); d.ellipse([280,60,470,250],fill="blue")
d.polygon([(120,360),(220,230),(320,360)],fill="green"); d.text((300,320),"MIMO 42",fill="black")
b=io.BytesIO(); img.save(b,"PNG"); url="data:image/png;base64,"+base64.b64encode(b.getvalue()).decode()
body={"model":"mimo-v2.6-flash","max_tokens":300,"temperature":0.2,"chat_template_kwargs":{"enable_thinking":False},
      "messages":[{"role":"user","content":[{"type":"image_url","image_url":{"url":url}},
      {"type":"text","text":"List every shape in this image with its color, and read any text."}]}]}
t=time.time(); r=json.load(urllib.request.urlopen(urllib.request.Request(U,json.dumps(body).encode(),{"Content-Type":"application/json"}),timeout=600))
print(f"vision {time.time()-t:.1f}s prompt_tokens {r['usage']['prompt_tokens']}:", r["choices"][0]["message"]["content"][:600].replace("\n"," | "))
