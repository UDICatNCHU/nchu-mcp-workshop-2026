// verify-all-tools.js — 驗證 3 個 MCP server 都連得上且 Gemma 能正確路由
//
// 問三題，每題應該打不同 tool：
//   Q1 → weather_tool.get_weather
//   Q2 → hello_tool.get_english_center_info
//   Q3 → teachers_tool.search_teachers
//
// 用法：node --env-file=.env scripts/verify-all-tools.js

import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

import { MCPClient } from '../backend-node/mcp-client.js';
import { OpenAILLMClient } from '../backend-node/llm-client-openai.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
process.chdir(ROOT);

const config = JSON.parse(readFileSync('config.json', 'utf-8'));
const mcp = new MCPClient(config);
await mcp.connect();

const llm = new OpenAILLMClient(mcp);

const TESTS = [
  { q: '台北現在天氣如何？',      expected: 'get_weather' },
  { q: '英文中心的 email 是？',    expected: 'get_english_center_info' },
  { q: '有做電腦視覺的老師嗎？',   expected: 'search_teachers' },
];

function toolUsed(messages) {
  for (const m of messages) {
    if (m.role !== 'assistant') continue;
    if (m.tool_calls?.length) return m.tool_calls[0].function.name;
  }
  return null;
}

for (const t of TESTS) {
  const started = Date.now();
  try {
    const res = await llm.chat([{ role: 'user', content: t.q }]);
    const used = toolUsed(res.messages);
    const pass = used === t.expected;
    console.log(`${pass ? '✅' : '❌'} "${t.q}"  (${Date.now() - started}ms)`);
    console.log(`    expected=${t.expected}  used=${used}`);
    console.log(`    reply: ${res.reply.slice(0, 150).replace(/\n/g, ' ')}`);
  } catch (e) {
    console.log(`❌ "${t.q}" — ERROR: ${e.message}`);
  }
}

process.exit(0);
