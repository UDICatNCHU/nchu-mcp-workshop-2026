// compare-providers.js — Claude vs 本地 vLLM / Gemma 4 並排比對
//
// 用法：
//   cd mini-project
//   # 確保 vLLM serve 於 localhost:8000、ANTHROPIC_API_KEY 在 .env
//   node --env-file=.env scripts/compare-providers.js
//
// 對每個測試題目：
//   - 同時打 Claude 與 OpenAI-兼容端點
//   - 量測 tool 呼叫是否正確、參數是否合理、延遲
//   - 最後輸出成功率對比表

import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

import { MCPClient } from '../backend-node/mcp-client.js';
import { LLMClient } from '../backend-node/llm-client.js';
import { OpenAILLMClient } from '../backend-node/llm-client-openai.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
process.chdir(ROOT);

const config = JSON.parse(readFileSync('config.json', 'utf-8'));
const mcp = new MCPClient(config);
await mcp.connect();

// 測試題組。expected_tool=null 代表「不該呼叫任何工具」（常識/閒聊）。
const TESTS = [
  { q: '英文中心幾點開門？',    expected: 'get_english_center_info' },
  { q: '英文中心的 email？',    expected: 'get_english_center_info' },
  { q: '借用耳機要帶什麼？',    expected: 'get_english_center_info' },
  { q: '英文中心有哪些設備？',  expected: 'get_english_center_info' },
  { q: '你好，今天好嗎？',      expected: null },  // 閒聊
  { q: '1 加 1 等於多少？',     expected: null },  // 純算數
];

function extractToolCalled(messages) {
  // 兩種 history 格式都檢查
  for (const m of messages) {
    if (m.role !== 'assistant') continue;
    // Claude 格式
    if (Array.isArray(m.content)) {
      const tu = m.content.find(b => b.type === 'tool_use');
      if (tu) return tu.name;
    }
    // OpenAI 格式
    if (m.tool_calls?.length) {
      return m.tool_calls[0].function.name;
    }
  }
  return null;
}

async function run(label, client) {
  console.log(`\n──── ${label} ────`);
  const results = [];
  for (const t of TESTS) {
    const started = Date.now();
    let used = null, reply = '', error = null;
    try {
      const res = await client.chat([{ role: 'user', content: t.q }]);
      reply = res.reply;
      used = extractToolCalled(res.messages);
    } catch (e) {
      error = e.message;
    }
    const latency = Date.now() - started;
    const pass = used === t.expected;
    results.push({ q: t.q, expected: t.expected, used, pass, latency, error, reply });
    const mark = pass ? '✅' : '❌';
    const u = used ?? '(none)';
    const e = t.expected ?? '(none)';
    console.log(`  ${mark} [${latency.toString().padStart(5)}ms] "${t.q}"`);
    console.log(`          expected=${e}  used=${u}`);
    if (error) console.log(`          ERROR: ${error}`);
    else if (reply) console.log(`          reply: ${reply.slice(0, 80).replace(/\n/g, ' ')}`);
  }
  const pass = results.filter(r => r.pass).length;
  console.log(`  ◆ Tool-selection accuracy: ${pass}/${results.length} (${((pass/results.length)*100).toFixed(0)}%)`);
  const avgLat = results.reduce((s, r) => s + r.latency, 0) / results.length;
  console.log(`  ◆ Average latency: ${avgLat.toFixed(0)}ms`);
  return { label, results, pass, total: results.length, avgLat };
}

const claude = new LLMClient(mcp);
const openai = new OpenAILLMClient(mcp);

const claudeOut = await run('Claude', claude);
const openaiOut = await run(`${process.env.OPENAI_MODEL ?? 'gemma-4'} via vLLM`, openai);

console.log('\n════ Summary ════');
console.log(`Claude                : ${claudeOut.pass}/${claudeOut.total}  avg ${claudeOut.avgLat.toFixed(0)}ms`);
console.log(`${openaiOut.label.padEnd(22)}: ${openaiOut.pass}/${openaiOut.total}  avg ${openaiOut.avgLat.toFixed(0)}ms`);

process.exit(0);
