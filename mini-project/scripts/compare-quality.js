// compare-quality.js — Claude vs 本地 Gemma 4 的品質對比
//
// 3 個刻意挑的鑑別度情境：
//   E1 推理型     — 從 tool 結果做時間計算，不是純 copy
//   E2 不 hallucinate — 問資料沒有的欄位，看會不會編造
//   E3 多輪 context  — 第二輪應該從歷史拿答案，不該多叫工具
//
// 腳本不做 pass/fail 判定，純粹把兩家 raw 答案並排印出。
//
// 用法：node --env-file=.env scripts/compare-quality.js

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

const EXAMPLES = [
  {
    name: 'E1 ─ 推理題（時間計算，不是純複製）',
    observation: 'JSON 寫 "週一至週五 09:00–17:00"。好的回答要自己算出可停留時數。',
    turns: ['我下午 4 點過去，還能待多久就會關門？'],
  },
  {
    name: 'E2 ─ 資訊不存在時的誠實度（hallucination 測試）',
    observation: 'JSON 沒有 Instagram 欄位。好的回答應明說「沒有」，壞的會編造帳號。',
    turns: ['英文中心的 Instagram 帳號是什麼？'],
  },
  {
    name: 'E3 ─ 多輪 context（不該重複叫工具）',
    observation: '第一輪叫工具拿全部資訊；第二輪的資訊已在歷史，不該再叫工具。',
    turns: ['英文中心 email？', '那電話呢？'],
  },
];

// 用完整 history + 從 messages 掃工具呼叫次數
function countToolCalls(history) {
  let n = 0;
  for (const m of history) {
    if (m.role !== 'assistant') continue;
    // Claude 格式
    if (Array.isArray(m.content)) {
      n += m.content.filter(b => b.type === 'tool_use').length;
    }
    // OpenAI 格式
    if (m.tool_calls?.length) n += m.tool_calls.length;
  }
  return n;
}

async function runOne(client, turns) {
  let history = [];
  const trace = [];
  const startAll = Date.now();
  for (const userMsg of turns) {
    history.push({ role: 'user', content: userMsg });
    const t0 = Date.now();
    const before = countToolCalls(history);
    const res = await client.chat(history);
    history = res.messages;
    const after = countToolCalls(history);
    trace.push({
      user: userMsg,
      assistant: res.reply,
      toolsThisTurn: after - before,
      latencyMs: Date.now() - t0,
    });
  }
  return { trace, totalMs: Date.now() - startAll };
}

function printTrace(label, result) {
  console.log(`  ${label}  (total ${result.totalMs}ms)`);
  for (const [i, t] of result.trace.entries()) {
    console.log(`    T${i+1} user>   ${t.user}`);
    console.log(`    T${i+1} ai  >   ${t.assistant.replace(/\n/g, ' ')}`);
    console.log(`           · tools called this turn: ${t.toolsThisTurn}    · latency: ${t.latencyMs}ms`);
  }
}

const claude = new LLMClient(mcp);
const gemma  = new OpenAILLMClient(mcp);

for (const ex of EXAMPLES) {
  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(ex.name);
  console.log(`  觀察重點: ${ex.observation}`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);

  const claudeOut = await runOne(claude, ex.turns);
  printTrace('【Claude Sonnet 4.5】', claudeOut);

  console.log('');

  const gemmaOut = await runOne(gemma, ex.turns);
  printTrace('【Gemma 4 31B / vLLM】', gemmaOut);
}

console.log('\n═══════════════════════════════════════════════');
process.exit(0);
