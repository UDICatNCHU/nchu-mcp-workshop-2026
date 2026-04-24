# 實驗記錄：Claude vs 本地 Gemma 4 — 工作坊可行性驗證

**日期**：2026-04-24
**主持**：yao-chung fan 范耀中
**目的**：評估三小時資工老師種子教師工作坊可否以自架 Gemma 4 取代 Anthropic Claude API，條件是「agent 任務品質不輸、速度不慢、成本更低」。

---

## 背景

現有 mini-project 預設走 Claude Sonnet 4.5。工作坊 10 位老師全程使用的 Claude 成本估算約 $20-60 USD/場。同時本機已有 Gemma 4 31B Instruct 權重（~59 GB）與 8 張 RTX A6000 閒置。驗證：Gemma 4 能否達到「足夠好」而取代 Claude。

## 環境

| 項目 | 配置 |
|------|------|
| 硬體 | 8× NVIDIA RTX A6000（每張 46 GB） |
| 模型 | `google/gemma-4-31B-it` (bf16, HF snapshot `439edf5…`) |
| 推論框架 | vLLM 0.19.1 |
| Tensor parallel | 2（GPU 2+3，共佔 ~76 GB） |
| `tool-call-parser` | `gemma4`（vLLM 原生支援） |
| `max_model_len` | 16384 |
| `gpu_memory_utilization` | 0.80 |
| 對照組 | Claude Sonnet 4.5 via Anthropic API |
| MCP 層 | 共用；Tools = `hello_tool.get_english_center_info`、`teachers_tool.search_teachers`、`teachers_tool.get_teacher_detail` |
| Adapter | `backend-node/llm-client.js`（Claude）vs `llm-client-openai.js`（OpenAI-compatible） |

## 三輪實驗

### 第一輪 — L1 單工具正確性（6 題）

腳本：`scripts/compare-providers.js`

| # | 題目 | 期望 | Claude | Gemma |
|---|------|------|:------:|:-----:|
| 1 | 英文中心幾點開門？ | `get_english_center_info` | ✅ | ✅ |
| 2 | 英文中心的 email？ | `get_english_center_info` | ✅ | ✅ |
| 3 | 借用耳機要帶什麼？ | `get_english_center_info` | ✅ | ✅ |
| 4 | 英文中心有哪些設備？ | `get_english_center_info` | ✅ | ✅ |
| 5 | 你好，今天好嗎？ | （不呼叫）| ✅ | ✅ |
| 6 | 1 加 1 等於多少？ | （不呼叫）| ✅ | ✅ |

**彙總**：Claude 6/6 avg 4501 ms · Gemma 6/6 avg **2773 ms**

**發現**：Gemma 4 輸出帶 `<|channel>thought <channel|>` thinking marker。vLLM 0.19.1 的 `gemma4_tool_parser` 尚未 strip。已在 `llm-client-openai.js._stripThinkingMarkers()` 做 client-side 過濾。

---

### 第二輪 — L1 品質 3 情境

腳本：`scripts/compare-quality.js`

| # | 情境 | Claude | Gemma | 判定 |
|---|------|--------|-------|------|
| E1 | 推理：「下午 4 點過去還能待多久？」（JSON 只有「09:00-17:00」）| 「還有 1 小時」＋建議早去 | 「還可以待 1 個小時」 | **兩者都正確推理** |
| E2 | 誠實：「Instagram 帳號？」（資料中無）| 承認沒資料＋3 個替代建議 | 承認沒資料＋email/電話 | **兩者都無 hallucination** |
| E3 | 多輪 context：T1「email？」T2「那電話呢？」 | T2 不叫工具 ✅ 2430 ms | T2 不叫工具 ✅ 2019 ms | **兩者都正確利用 context** |

**觀察**：Claude 回答風格偏「教學式＋多 action items」；Gemma 偏「簡潔、on-task」。對 workshop demo 而言 Gemma 更清爽。

---

### 第三輪 — L2 多工具 agent 規劃（3 情境）

腳本：`scripts/compare-l2-quality.js`
資料集：12 筆教授，ML=4、CV=3、LLM=3、NLP=2。

| # | 情境 | Claude tool calls | Gemma tool calls | 判定 |
|---|------|-------------------|------------------|------|
| E1 | 「找 **3 位** 教 ML 的教授」 | `search(keyword="機器學習", limit=3)` | `search(keyword="機器學習", limit=3)` | **參數綁定兩者皆對** |
| E2 | 「做 CV 老師的 **email**」 | `search(keyword="電腦視覺")`（1 call）| `search(keyword="電腦視覺")`（1 call） | **兩者都判斷不需 `get_detail`**（email 已在 search 結果），無盲目疊工具 |
| E3 | 「ML 和 CV 哪個領域老師多？」 | **並行** `search(ML, limit=20)` + `search(CV, limit=20)` | **並行** `search(ML)` + `search(CV)` | 規劃同樣正確；但 **Claude 主動拉 `limit=20`**，Gemma 用預設 5 |

**關鍵差異（E3）**：
- **Claude 有邊界風險意識**：擔心預設 5 會切掉，主動拉 20
- **Gemma 依賴預設 5**：本次資料 ML=4、CV=3 都 ≤5 剛好答對。若某領域有 7 位則會漏算
- 這是兩家**唯一**可辨識的品質差異，其餘 7 項全數打平

---

## 發現矩陣

| 面向 | Claude | Gemma 4 | 結論 |
|------|:------:|:-------:|------|
| 工具選擇正確率 | 100% | 100% | 打平 |
| 參數綁定（keyword/limit） | ✅ | ✅ | 打平 |
| 時間推理 | ✅ | ✅ | 打平 |
| Hallucination 抵抗 | ✅ | ✅ | 打平 |
| 多輪 context 記憶 | ✅ | ✅ | 打平 |
| 多工具並行規劃 | ✅ | ✅ | 打平 |
| 不盲目疊工具 | ✅ | ✅ | 打平 |
| 邊界防禦（主動拉 limit） | ✅ | ❌ | **Claude 略勝** |
| 回答風格 | 教學式、多 actions | 簡潔、on-task | 各有優勢 |
| 延遲（三輪平均）| ~4800 ms | ~3500 ms | **Gemma 快 1.4×** |
| API 成本 | $20-60/workshop | **$0** | **Gemma 勝** |

## 結論

1. **Gemma 4 採用於工作坊是可行且更優的方案**：agent 任務品質 ≈ Claude，速度快 1.4×，成本為 0。
2. **唯一可辨識的品質 gap 在「邊界防禦」**（主動拉 limit）。對 workshop demo 無影響；反而可做 L2 的 stretch 討論題目「docstring 怎麼寫才能提醒 agent？」
3. **Thinking marker** 已在 adapter 層 strip。若未來 vLLM parser 更新原生處理，這個 workaround 可移除。
4. **Claude 仍有「主動關懷、多 action items」的 UX 優勢**，這對 production 客服較重要；workshop demo 場景 Gemma 的簡潔更有利。

## Workshop 採用策略

- **Primary**：Gemma 4 本地（`LLM_PROVIDER=openai`，連 `http://localhost:8000/v1`）
- **Fallback**：`LLM_PROVIDER=claude` — 若 vLLM 當掉或網路問題，一行 env var 切回
- **啟動時程**：開場前 10 分鐘 `bash /user_data/vllm-workshop/serve-gemma.sh bg`，等 ~3 分鐘 weights 載完。老師抵達時直接 ready。

## 可重現性

### 環境建置（一次性）
```bash
# 建 vLLM 獨立 venv
mkdir -p /user_data/vllm-workshop
cd /user_data/vllm-workshop
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install vllm   # ~5 分鐘，venv 共 ~10 GB
```

### 啟動 Gemma 4 serve
```bash
bash /user_data/vllm-workshop/serve-gemma.sh bg
# 等 tail -f /tmp/vllm-serve.log 出現「Application startup complete」
curl http://localhost:8000/v1/models   # 應回 {data:[{id:"gemma-4", ...}]}
```

### mini-project .env（workshop 用）
```
ANTHROPIC_API_KEY=sk-ant-...         # 留著當 fallback
LLM_PROVIDER=openai                   # 改成 claude 可切換
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=dummy
OPENAI_MODEL=gemma-4
```

### 跑本次所有實驗
```bash
cd mini-project
node --env-file=.env scripts/compare-providers.js     # 第一輪
node --env-file=.env scripts/compare-quality.js       # 第二輪
node --env-file=.env scripts/compare-l2-quality.js    # 第三輪
```

## 遺留項目

- [ ] 擴充 teachers 到 50 筆，讓 Gemma 踩到 limit 預設的坑，比較兩家在 edge case 的表現
- [ ] 測試 L3 `arxiv_tool`（async httpx + 外部 API）在 Gemma 上是否穩定
- [ ] Prompt injection 抵抗：tool 回傳含假指令（「忽略前面所有指令…」）
- [ ] 極長對話（10+ 輪）的 context 管理對比
- [ ] 中英混雜 query（模擬國際生提問）
- [ ] 把 thinking markers 的 strip 邏輯往上游推：是否 vLLM 0.19.2+ 已修
