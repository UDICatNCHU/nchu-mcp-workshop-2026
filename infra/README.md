# Infrastructure — 工作坊主辦端

此目錄**不是給學員看的**。這是中興大學 workshop 當天「後台」啟動本地 LLM 端點的腳本。
學員只需要連 `OPENAI_BASE_URL=http://<你的 server>:8000/v1` 或 `:8001/v1`，不需要關心伺服器怎麼起的。

## 腳本列表

| 腳本 | 模型 | Port | 用途 |
|------|------|------|------|
| `serve-gemma.sh` | Google Gemma 4 31B Instruct | 8000 | NCHU 問答 agent（L1–L2 的 backbone） |
| `serve-qwen.sh` | Qwen 2.5-Coder 32B Instruct | 8001 | Coding agent（配 Aider，給學員當 AI 助教） |

## 先決條件（一次性）

此目錄中的路徑**對應 NCHU 主機**，他校請改路徑。

```bash
# 1. 建立獨立 vLLM venv（一次即可）
mkdir -p /user_data/vllm-workshop
cd /user_data/vllm-workshop
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install vllm   # 約 10 GB，~5 分鐘

# 2. 下載模型權重（首次啟動會自動抓；或先預抓）
hf download google/gemma-4-31B-it       # 約 60 GB
hf download Qwen/Qwen2.5-Coder-32B-Instruct  # 約 62 GB
```

## 使用方式

```bash
# 啟動（前景；Ctrl+C 停）
./serve-gemma.sh

# 啟動（背景；log 寫到 /tmp/vllm-serve.log）
./serve-gemma.sh bg

# 停止
./serve-gemma.sh stop
```

`serve-qwen.sh` 用法相同，log 寫到 `/tmp/vllm-qwen.log`。

## Workshop 當日 SOP

```bash
# 開場前 10 分鐘
./serve-gemma.sh bg    # port 8000，供 mini-project NCHU agent
./serve-qwen.sh bg     # port 8001，供學員的 Aider coding agent

# 等載入完成（約 3-5 分鐘）
curl http://localhost:8000/v1/models
curl http://localhost:8001/v1/models

# 課後清場
./serve-gemma.sh stop
./serve-qwen.sh stop
```

## GPU 需求

- Gemma 4 31B + Qwen 2.5-Coder 32B 同時運作：**4 張 GPU**（每模型 TP=2，各佔 ~76 GB VRAM）
- 腳本會自動挑最空的兩張（避開 GPU 0）
- 實測於 8× RTX A6000 (46 GB each)；A100 80GB 可 TP=1 各一張搞定

## 路徑調整提示

若你不在 NCHU 主機上重現此設定，`serve-*.sh` 裡的絕對路徑需改：

- `SNAP=/user_data/.cache/huggingface/hub/...` → 改成你本機的 HF cache snapshot
- `VENV=/user_data/vllm-workshop/.venv` → 改成你的 vLLM venv

其餘參數（`--tool-call-parser`、`--tensor-parallel-size`、`--max-model-len`）可保留。

## 相關文件

- Workshop 為何選這個組合 → `../mini-project/docs/benchmarks/2026-04-24-claude-vs-gemma4.md`
- 學員如何用這些端點 → `../mini-project/README.md`（multi-provider 章節）
