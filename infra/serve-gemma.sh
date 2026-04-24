#!/usr/bin/env bash
# serve-gemma.sh — 啟動 Gemma 4 31B Instruct (via vLLM) 當 OpenAI-兼容 endpoint
#
# 用法：
#   ./serve-gemma.sh          前景啟動（Ctrl+C 停）
#   ./serve-gemma.sh bg       背景啟動，log 寫到 /tmp/vllm-serve.log
#   ./serve-gemma.sh stop     停掉背景啟動的服務
#
# 上線後：
#   curl http://localhost:8000/v1/models
#   curl http://localhost:8000/v1/chat/completions ...

set -euo pipefail

SNAP=/user_data/.cache/huggingface/hub/models--google--gemma-4-31B-it/snapshots/439edf5652646a0d1bd8b46bfdc1d3645761a445
VENV=/user_data/vllm-workshop/.venv
PORT=8000
LOG=/tmp/vllm-serve.log

# 選兩張記憶體最空的 GPU（避開 0 號，可能有殘留）
PICKED_GPUS=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits \
  | awk -F', ' '$1 != 0 {print $1, $2}' \
  | sort -k2 -n | head -2 | awk '{print $1}' | paste -sd,)

case "${1:-fg}" in
  stop)
    pkill -9 -f "vllm serve" && echo "vllm stopped" || echo "(nothing to stop)"
    ;;
  bg)
    source "$VENV/bin/activate"
    echo "Using GPU(s): $PICKED_GPUS"
    : > "$LOG"
    CUDA_VISIBLE_DEVICES="$PICKED_GPUS" nohup vllm serve "$SNAP" \
      --served-model-name gemma-4 \
      --tensor-parallel-size 2 \
      --gpu-memory-utilization 0.80 \
      --max-model-len 16384 \
      --dtype bfloat16 \
      --port "$PORT" \
      --host 127.0.0.1 \
      --enable-auto-tool-choice \
      --tool-call-parser gemma4 \
      > "$LOG" 2>&1 &
    echo "vllm PID: $!  log: $LOG"
    echo "Wait ~3 min for weights to load, then: curl localhost:$PORT/v1/models"
    ;;
  fg|*)
    source "$VENV/bin/activate"
    echo "Using GPU(s): $PICKED_GPUS"
    CUDA_VISIBLE_DEVICES="$PICKED_GPUS" vllm serve "$SNAP" \
      --served-model-name gemma-4 \
      --tensor-parallel-size 2 \
      --gpu-memory-utilization 0.80 \
      --max-model-len 16384 \
      --dtype bfloat16 \
      --port "$PORT" \
      --host 127.0.0.1 \
      --enable-auto-tool-choice \
      --tool-call-parser gemma4
    ;;
esac
