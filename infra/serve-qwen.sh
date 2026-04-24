#!/usr/bin/env bash
# serve-qwen.sh — 啟動 Qwen 2.5-Coder 32B as OpenAI-compatible endpoint
#
# 設計重點：
#   - port 8001（避開 Gemma 用的 8000，兩模型可同時服務）
#   - max-model-len 32K（coding 任務 context 需求大）
#   - tool-call-parser hermes（Qwen 2.5 系列標準格式）
#
# 用法：
#   ./serve-qwen.sh          前景
#   ./serve-qwen.sh bg       背景
#   ./serve-qwen.sh stop     停

set -euo pipefail

MODEL_ID=Qwen/Qwen2.5-Coder-32B-Instruct
VENV=/user_data/vllm-workshop/.venv
PORT=8001
LOG=/tmp/vllm-qwen.log

# 避開 GPU 0（有殘留）與 Gemma 在跑的 2,3；挑最空的兩張
PICKED=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits \
  | awk -F', ' '$1 != 0 {print $1, $2}' | sort -k2 -n | head -2 | awk '{print $1}' | paste -sd,)

case "${1:-fg}" in
  stop)
    pkill -9 -f "vllm serve.*Qwen2.5-Coder" 2>/dev/null && echo "qwen stopped" || echo "(nothing to stop)"
    pkill -9 -f "served-model-name qwen-coder" 2>/dev/null
    ;;
  bg)
    source "$VENV/bin/activate"
    echo "Using GPU(s): $PICKED, port $PORT"
    : > "$LOG"
    CUDA_VISIBLE_DEVICES="$PICKED" nohup vllm serve "$MODEL_ID" \
      --served-model-name qwen-coder \
      --tensor-parallel-size 2 \
      --gpu-memory-utilization 0.85 \
      --max-model-len 30000 \
      --dtype bfloat16 \
      --port "$PORT" \
      --host 127.0.0.1 \
      --enable-auto-tool-choice \
      --tool-call-parser hermes \
      > "$LOG" 2>&1 &
    echo "PID $!, log $LOG"
    echo "Wait ~3 min, then: curl localhost:$PORT/v1/models"
    ;;
  fg|*)
    source "$VENV/bin/activate"
    echo "Using GPU(s): $PICKED, port $PORT"
    CUDA_VISIBLE_DEVICES="$PICKED" vllm serve "$MODEL_ID" \
      --served-model-name qwen-coder \
      --tensor-parallel-size 2 \
      --gpu-memory-utilization 0.85 \
      --max-model-len 30000 \
      --dtype bfloat16 \
      --port "$PORT" \
      --host 127.0.0.1 \
      --enable-auto-tool-choice \
      --tool-call-parser hermes
    ;;
esac
