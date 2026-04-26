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

可用工具（請優先使用，不要憑記憶猜測）：
- search_course(query)：模糊問題、不確定哪段時先用這個搜尋
- get_segment(num)：要某一段（1–5）完整內容時用
- get_lab_handout(lab)：'L1'/'L2'/'L3'/'setup'/'benchmark'，學員問 hands-on 細節時用
- read_mini_project_file(path)：學員問程式碼時用，例如 'backend-node/llm-client.js'

回答原則：
1. 永遠用繁體中文。
2. 引用來源（哪一段、哪個檔案的第幾行）。
3. 不知道就說不知道，不要幻想。如果工具回空，直接說「這個資料我們課程裡沒有」。
4. 學員問與課程無關的事（天氣、新聞、私人問題）→ 簡短說「我只負責這門 workshop 的內容」並建議他問什麼。
5. 程式碼解釋盡量對照真實 source code，不要編造 API。`;

const config = JSON.parse(readFileSync(join(ROOT, 'config.json'), 'utf-8'));
const mcp = new MCPClient(config);
await mcp.connect();

const provider = (process.env.LLM_PROVIDER ?? 'claude').toLowerCase();
const llm = provider === 'openai'
  ? new OpenAILLMClient(mcp, { system: SYSTEM_PROMPT })
  : new LLMClient(mcp, { system: SYSTEM_PROMPT });

const app = express();
app.use(express.json({ limit: '32kb' }));   // chat 訊息很小，1mb 是 DoS 放大器
app.use(express.static(join(ROOT, 'web')));

// /chat 是會花錢的端點：每 IP 每分鐘 20 次，防 drive-by 拖垮帳單
app.use('/chat', rateLimit({
  windowMs: 60 * 1000,
  max: 20,
  standardHeaders: true,
  legacyHeaders: false,
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
