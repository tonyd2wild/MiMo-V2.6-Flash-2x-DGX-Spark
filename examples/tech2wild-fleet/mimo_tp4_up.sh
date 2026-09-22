#!/bin/bash
# mimo_tp4_up.sh <label> (root on Reddie): tear down both TP2 lanes, start one TP4 instance (workers first), poll.
LBL=${1:?label}; D=/var/tmp/boot-results/mimo; mkdir -p $D; L=$D/tp4-$LBL.log; exec > >(tee -a "$L") 2>&1
J="sudo -u tonyspark2 ssh -i /home/tonyspark2/.ssh/id_ed25519_shared -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15"
FWD="MAXLEN=${MAXLEN:-} GMU=${GMU:-} SEQS=${SEQS:-} SPEC=${SPEC:-} KV_DTYPE=${KV_DTYPE:-} MOE=${MOE:-} ASYNC_SCHED=${ASYNC_SCHED:-} REP_PENALTY=${REP_PENALTY:-} THINKING=${THINKING:-} EXTRA_ARGS='${EXTRA_ARGS:-}'"
echo "=== tp4 $LBL $(date -u +%T) $FWD"; T0=$(date -u +%s)
for h in tonyspark4@192.168.192.4 tonyspark3@192.168.192.3 tonyspark1@192.168.192.1; do $J -n $h "docker rm -f vllm_mimo >/dev/null 2>&1; true"; done; docker rm -f vllm_mimo >/dev/null 2>&1
echo "--- workers"; $J -n tonyspark4@192.168.192.4 "$FWD bash ~/mimo_node.sh T 1" | grep -E "started|MemAvail"
$J -n tonyspark3@192.168.192.3 "$FWD bash ~/mimo_node.sh T 2" | grep -E "started|MemAvail"; $J -n tonyspark1@192.168.192.1 "$FWD bash ~/mimo_node.sh T 3" | grep -E "started|MemAvail"
echo "--- head"; eval "$FWD sudo -u tonyspark2 -E bash /home/tonyspark2/mimo_node.sh T 0" | grep -E "started|MemAvail"
for i in $(seq 1 60); do sleep 30
  curl -s -m 5 http://192.168.192.2:8888/v1/models | grep -q mimo && { echo "SERVING $(date -u +%T) after $(( $(date -u +%s) - T0 ))s"; break; }
  docker ps -q -f name=vllm_mimo | grep -q . || { echo "HEAD DIED $(date -u +%T)"; docker logs vllm_mimo 2>&1 | grep -E "Error|error:" | tail -4 | cut -c1-220; break; }
  [ $((i % 4)) = 1 ] && echo "$(date -u +%T) $(docker logs --tail 1 vllm_mimo 2>&1 | cut -c1-140)"
done
docker logs vllm_mimo 2>&1 | grep -oE "(Model loading took.*|Available KV.*GiB|GPU KV cache size.*|Maximum concurrency.*)" | sort -u
echo "=== tp4 $LBL done $(date -u +%T)"
