// server.js — 教學範例：Express 主程式
//
// 職責：
//   1. 啟動時連接 MCP 服務、建立 LLM client
//   2. 提供 POST /chat：接收 messages 陣列，回傳 {reply, messages}
//   3. 提供靜態網頁 /，載入 web/index.html

import 'dotenv/config';
import express from 'express';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

import { MCPClient } from './mcp-client.js';
import { LLMClient } from './llm-client.js';
import { OpenAILLMClient } from './llm-client-openai.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

// 切到專案根目錄，讓 config.json 裡的相對路徑（例如 "mcp-server-py"）一致可解析。
process.chdir(ROOT);

// 1. 讀 config 並連接所有 MCP server（啟動時一次完成）
const config = JSON.parse(readFileSync(join(ROOT, 'config.json'), 'utf-8'));
const mcp = new MCPClient(config);
await mcp.connect();

// 依環境變數選擇 LLM provider（claude | openai）
// 預設 claude。改用 vLLM/Gemma/本地模型時設 LLM_PROVIDER=openai。
const provider = (process.env.LLM_PROVIDER ?? 'claude').toLowerCase();
const llm = provider === 'openai'
  ? new OpenAILLMClient(mcp)
  : new LLMClient(mcp);

// 2. Express 設定
const app = express();
app.use(express.json({ limit: '1mb' }));
app.use(express.static(join(ROOT, 'web')));

app.post('/chat', async (req, res) => {
  const { messages } = req.body ?? {};
  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: 'messages (array) is required' });
  }

  try {
    const result = await llm.chat(messages);
    res.json(result);
  } catch (err) {
    console.error('[chat error]', err);
    res.status(500).json({ error: err.message });
  }
});

// 3. 啟動
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`→ Mini AI Assistant: http://localhost:${PORT}`);
});
