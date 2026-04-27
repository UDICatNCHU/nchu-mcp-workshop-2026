// server.js — Express 主程式（架構刻意 mirror mini-project，差別只在 system prompt 與 PORT 預設）
//
// 職責：
//   1. 啟動時連接 MCP 服務、建立 LLM client（注入 TA 角色 system prompt）
//   2. 提供 POST /chat：接收 messages 陣列，回傳 {reply, messages}
//   3. 提供靜態網頁 /，載入 web/index.html

import 'dotenv/config';
import express from 'express';
import rateLimit from 'express-rate-limit';
import { randomUUID } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import { MCPClient } from './mcp-client.js';
import { LLMClient } from './llm-client.js';
import { OpenAILLMClient } from './llm-client-openai.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

process.chdir(ROOT);

const SYSTEM_PROMPT = `你是 NCHU MCP Workshop 2026 的課程小助教。

你的職責：回答學員關於這門「3 小時 MCP 入門」工作坊的所有疑問 — 課程概念、Lab 操作、mini-project 程式碼細節。

可用工具（**先選最對的一個用，避免連續搜尋多次**）：
- get_segment(num)：直接知道是哪一段時（1–5），優先用這個
- get_lab_handout(lab)：'L1'/'L2'/'L3'/'setup'/'benchmark'，學員問 hands-on 細節時用
- read_mini_project_file(path)：學員問程式碼時用，例如 'backend-node/llm-client.js'
- search_course(query)：**只在前三個都不確定時才用**；用了就別再用 get_segment 重複查

效率規則（**重要**）：
- 一個學員問題盡量只呼叫 1 個工具。
- 工具回傳的內容裡找答案就好，不要再呼叫第二個工具去補充。
- 例外：學員明顯需要程式碼時，可以「get_lab_handout 後再 read_mini_project_file」一次。

準確性規則（**絕對遵守**）：
- 學員提到具體名稱時 → **務必先呼叫工具查證、不可憑記憶回答**：
  - 「Segment N」「第 N 段」「第 N 講」 → 先 get_segment(N)
  - 「L1 / L2 / L3 / setup / benchmark」 → 先 get_lab_handout(...)
  - 任何 .py / .js / .json / .md / .html 檔名 → 先 read_mini_project_file(...)
- 即使問題很短（如「L1 是什麼？一句話」），仍必須先 call tool。
- 沒查就答 = 嚴重錯誤。寧可慢 5 秒，也不要把 L1 講錯。

回答原則：
1. 永遠用繁體中文。
2. **回答精簡：80–250 字為主**。學員是現場聽課中，不要寫長篇。
3. 引用來源（哪一段、哪個檔案的第幾行）。
4. 不知道就說不知道，不要幻想。
5. 學員問與課程無關的事 → 簡短說「我只負責這門 workshop 的內容」。`;

const config = JSON.parse(readFileSync(join(ROOT, 'config.json'), 'utf-8'));
const mcp = new MCPClient(config);
await mcp.connect();

const provider = (process.env.LLM_PROVIDER ?? 'claude').toLowerCase();
const llm = provider === 'openai'
  ? new OpenAILLMClient(mcp, { system: SYSTEM_PROMPT })
  : new LLMClient(mcp, { system: SYSTEM_PROMPT });

const app = express();
// 信任 cloudflared / 本機 reverse proxy 那一跳，讓 req.ip 拿到真實來源
app.set('trust proxy', 'loopback');
app.use(express.json({ limit: '32kb' }));   // chat 訊息很小，1mb 是 DoS 放大器
app.use(express.static(join(ROOT, 'web')));

// /chat 是會花錢的端點：每真實 client IP 每分鐘 20 次
// keyGenerator 優先用 cloudflare 的 cf-connecting-ip（cloudflare edge 設、無法偽造）
// 沒走 cloudflared 時 fall back 到 req.ip（trust proxy 解析後的真實 IP）
app.use('/chat', rateLimit({
  windowMs: 60 * 1000,
  max: 20,
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.headers['cf-connecting-ip'] || req.ip || 'unknown',
  message: { error: 'rate limit exceeded — 一分鐘最多 20 次，請稍候' },
}));

const MAX_HISTORY = 30;

app.post('/chat', async (req, res) => {
  const { messages } = req.body ?? {};
  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: 'messages (array) is required' });
  }
  if (messages.length > MAX_HISTORY) {
    return res.status(400).json({ error: `history too long (max ${MAX_HISTORY} messages)` });
  }
  // 擋掉純空字串訊息（會讓 Claude API throw 500）
  const last = messages[messages.length - 1];
  if (last && typeof last.content === 'string' && last.content.trim() === '') {
    return res.status(400).json({ error: '請輸入內容後再送出' });
  }

  try {
    const result = await llm.chat(messages);
    res.json(result);
  } catch (err) {
    // 不把 err.message 漏給 client（可能含 API key 前綴 / model 名 / 路徑）
    const id = randomUUID();
    console.error(`[chat error ${id}]`, err);
    res.status(500).json({ error: `internal error (id=${id})` });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`→ Course TA Agent: http://localhost:${PORT}`);
});
