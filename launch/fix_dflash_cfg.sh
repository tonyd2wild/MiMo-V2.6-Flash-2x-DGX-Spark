#!/bin/bash
# Write a corrected copy of MiMo's dflash/config.json (trailing commas removed) to the node's MiMo cache dir.
SRC=/var/tmp/models/MiMo-V2.6-Flash-RL/dflash/config.json
[ -f $SRC ] || SRC=/mnt/reddie-models/MiMo-V2.6-Flash-RL/dflash/config.json
mkdir -p /var/tmp/mimo-cache
python3 - "$SRC" /var/tmp/mimo-cache/dflash-config.fixed.json <<'PY'
import json, re, sys
src, dst = sys.argv[1], sys.argv[2]
t = open(src).read()
fixed = re.sub(r",(\s*[}\]])", r"\1", t)
d = json.loads(fixed)
json.dump(d, open(dst, "w"), indent=2)
print("fixed", src, "->", dst, "keys", len(d), "block_size", d.get("block_size"), "target_layer_ids", d.get("dflash_config", {}).get("target_layer_ids"))
PY
