#!/bin/bash
# mimo_up.sh <label> (root on Reddie): start both MiMo TP2 instances (workers first, then heads), poll both heads.
# A = Reddie(0) + Spark4(1), B = Bluey(0) + Asusi(1). Knobs (MAXLEN GMU SEQS SPEC EXTRA_ARGS) are forwarded.
LBL=${1:?label}; D=/var/tmp/boot-results/mimo; mkdir -p $D; L=$D/boot-$LBL.log
exec > >(tee -a "$L") 2>&1
J="sudo -u tonyspark2 ssh -i /home/tonyspark2/.ssh/id_ed25519_shared -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15"
FWD="MAXLEN=${MAXLEN:-} GMU=${GMU:-} SEQS=${SEQS:-} SPEC=${SPEC:-} KV_DTYPE=${KV_DTYPE:-} MOE=${MOE:-} EXTRA_ARGS='${EXTRA_ARGS:-}'"
echo "=== mimo_up $LBL $(date -u +%T) $FWD"
T0=$(date -u +%s)
echo "--- workers: Spark4 (A rank 1), Asusi (B rank 1)"
$J -n tonyspark4@192.168.192.4 "$FWD bash ~/mimo_node.sh A 1"
$J -n tonyspark3@192.168.192.3 "$FWD bash ~/mimo_node.sh B 1"
echo "--- heads: Reddie (A rank 0), Bluey (B rank 0)"
eval "$FWD sudo -u tonyspark2 -E bash /home/tonyspark2/mimo_node.sh A 0"
$J -n tonyspark1@192.168.192.1 "$FWD bash ~/mimo_node.sh B 0"
okA=0; okB=0
for i in $(seq 1 90); do
  sleep 30
  [ $okA = 0 ] && curl -s -m 5 http://192.168.192.2:8888/v1/models | grep -q mimo && { okA=1; echo "A SERVING $(date -u +%T) after $(( $(date -u +%s) - T0 ))s"; }
  [ $okB = 0 ] && curl -s -m 5 http://192.168.192.1:8888/v1/models | grep -q mimo && { okB=1; echo "B SERVING $(date -u +%T) after $(( $(date -u +%s) - T0 ))s"; }
  [ $okA = 1 ] && [ $okB = 1 ] && break
  dead=""
  docker ps --format '{{.Names}}' | grep -q '^vllm_mimo$' || dead="$dead reddie"
  for h in tonyspark4@192.168.192.4 tonyspark3@192.168.192.3 tonyspark1@192.168.192.1; do
    $J -n $h "docker ps --format '{{.Names}}' | grep -q '^vllm_mimo$'" || dead="$dead ${h%%@*}"
  done
  [ $((i % 4)) = 1 ] && echo "$(date -u +%T) A: $(docker logs --tail 1 vllm_mimo 2>&1 | cut -c1-150) | B: $($J -n tonyspark1@192.168.192.1 'docker logs --tail 1 vllm_mimo 2>&1 | cut -c1-150')"
  if [ -n "$dead" ]; then
    echo "CONTAINER GONE $(date -u +%T):$dead"
    for n in $dead; do
      case $n in
        reddie) docker logs --tail 60 vllm_mimo 2>&1 | grep -iE "error|Traceback|raise|Exception|OOM|killed" | tail -12;;
        *) h=$(echo "tonyspark4@192.168.192.4 tonyspark3@192.168.192.3 tonyspark1@192.168.192.1" | tr ' ' '\n' | grep "^$n@"); echo "== $n"; $J -n $h "docker logs --tail 60 vllm_mimo 2>&1 | grep -iE 'error|Traceback|raise|Exception|OOM|killed' | tail -12";;
      esac
    done
    break
  fi
done
echo "--- KV / memory lines"
echo "A:"; docker logs vllm_mimo 2>&1 | grep -iE "KV cache size|Maximum concurrency|Available KV|Model loading took|Loading weights took|speculative" | sed -E 's/^.*\] //' | tail -6
echo "B:"; $J -n tonyspark1@192.168.192.1 "docker logs vllm_mimo 2>&1 | grep -iE 'KV cache size|Maximum concurrency|Available KV|Model loading took|Loading weights took|speculative' | sed -E 's/^.*\] //' | tail -6"
echo "=== mimo_up $LBL done $(date -u +%T) A=$okA B=$okB"
