# Haiku Alignment 優化報告

## 一、目標

將基底模型從 **Claude Sonnet** 切換至 **Claude Haiku**，降低 token 開銷，同時透過 few-shot alignment 和格式規範維持回覆品質。

---

## 二、原始流程 vs 新流程

### 請求處理流程

```
【原始流程】
User Query
  → ChatController（注入時間 + 登入狀態）
  → raw-mcp-client.js
  → ClaudeClient (claude-client.js)
  → System Prompt = 靜態 config prompt
  → Claude Sonnet API
  → 回覆直接串流給用戶

【新流程】
User Query
  → ChatController（注入時間 + 登入狀態）
  → raw-mcp-client.js
  → ClaudeClient (claude-client-aligned.js)
  → AlignmentMiddleware.enrichSystemPrompt()
      ├─ 1. 原始 system prompt
      ├─ 2. ALIGNMENT_RULES（工具選擇規則）
      ├─ 3. RESPONSE_FORMAT_RULES（回覆格式規範）
      └─ 4. Top-K few-shot 範例（從 3200+ 筆 trace 檢索）
  → Claude Haiku API
  → 回覆直接串流給用戶
```

### System Prompt 組成對比

| 層次 | 原始 | 新增 |
|------|------|------|
| 基礎角色設定 | config.json 靜態 prompt | 同左（不變） |
| 時間/登入資訊 | ChatController 注入 | 同左（不變） |
| 工具選擇規則 | 無 | `ALIGNMENT_RULES`（4 條核心規則） |
| 回覆格式規範 | prompt 中幾句模糊指示 | `RESPONSE_FORMAT_RULES`（書籍/課程/活動/人員/法規分類模板） |
| Few-shot 範例 | 無 | 從歷史 trace 檢索 top-9 相似範例 |
| 無聊偵測注入 | 有（ChatService） | 同左（不變） |

### 最後一輪提示對比

| | 原始 | 新流程 |
|---|---|---|
| 內容 | 「不要用工具，直接回覆」 | 「不要用工具，整理出結構化 Markdown 回覆」+ 5 點格式要求 |

### 模型與備援配置

| | 原始 | 新流程 |
|---|---|---|
| 主要模型 | Claude Sonnet | Claude Haiku |
| 備援順序 | `ollama → claude` | `claude → ollama` |
| Controllers 模型 | 硬編碼 `claude-sonnet-4-20250514` | `config.claudeModel[0]`（統一控管） |

---

## 三、新增元件

| 元件 | 檔案 | 用途 |
|------|------|------|
| AlignmentMiddleware | `api/alignment-middleware.js` | 從歷史 trace 檢索相似範例，支援 keyword / embedding / hybrid 三種檢索模式 |
| Aligned ClaudeClient | `api/claude-client-aligned.js` | 在每次 API 呼叫前透過 middleware 動態豐富 system prompt |
| 格式規範 | `config/response-format-rules.js` | 定義書籍、課程、活動、人員、法規五大分類的 Markdown 格式模板 |
| Trace 資料 | `data/nchu_traces/*.jsonl` | 3207 筆正例 + 876 筆負例，作為 few-shot 檢索來源 |
| Embedding 快取 | `data/nchu_traces/_embeddings_cache.json` | 預計算的語義向量，避免每次啟動重新計算 |

---

## 四、品質保護機制

```
                    ┌─────────────────────────┐
                    │     User Query          │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Embedding / Keyword     │
                    │  相似度檢索              │
                    │  (3200+ traces)          │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────▼─────────────────┐
              │        Enriched System Prompt       │
              │  ┌──────────────────────────────┐  │
              │  │ ALIGNMENT_RULES              │  │ ← 工具選擇正確性
              │  │ (選對工具、填對參數)          │  │
              │  ├──────────────────────────────┤  │
              │  │ RESPONSE_FORMAT_RULES        │  │ ← 回覆格式品質
              │  │ (Markdown 標題/列表/圖片)    │  │
              │  ├──────────────────────────────┤  │
              │  │ Top-9 Few-shot Examples      │  │ ← 具體示範
              │  │ (query → tool_calls 配對)    │  │
              │  └──────────────────────────────┘  │
              └─────────────────┬──────────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │    Haiku Agentic Loop    │
                    │    (最多 7 輪)           │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  最後一輪格式化提示       │ ← 最終回覆品質把關
                    │  (5 點 Markdown 要求)    │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │     Structured Response   │
                    └──────────────────────────┘
```

---

## 五、成本影響

| 項目 | 估算 |
|------|------|
| Sonnet input | $3.00 / 1M tokens |
| Haiku input | $0.80 / 1M tokens |
| 格式規範額外 token | ~300 tokens/request |
| Few-shot 範例額外 token | ~1,200 tokens/request |
| **每次請求額外成本** | ~$0.0012（可忽略） |
| **整體節省** | 約 **73%** input token 費用 |

---

## 六、已知限制

1. **多語系影響**：Trace 資料和格式規範皆為中文，非中文使用者（英/日/越/泰）的 few-shot 匹配率較低，且中文規則可能影響回覆語言一致性
2. **工具選擇差異**：Haiku 選擇的工具與 Sonnet 不完全一致，但方向通常正確（選了不同但合理的替代工具）
3. **AdminController / QuickQuestionController**：仍使用原版 `claude-client.js`（無 alignment 注入），因其為後台管理功能，不需要 few-shot 引導
