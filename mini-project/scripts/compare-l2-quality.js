// compare-l2-quality.js — L2 teachers_tool 的品質對比
//
// 三個刻意挑的鑑別度情境：
//   E1 參數精細度 — "給我 3 位教 ML 的教授" 會不會正確傳 limit=3
//   E2 多工具協作 — 先 search 再 get_detail 才答得完整
//   E3 多次搜尋彙整 — "哪個領域教授最多？" 需要多次呼叫並比較
//
// 比起只印 reply，這支腳本會把每次 tool 呼叫的 name + arguments 都印出來，
// 讓你看到兩家 agent 的實際規劃行為。
//
// 用法：node --env-file=.env scripts/compare-l2-quality.js

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
    name: 'E1 ─ 參數精細度（limit 是否被正確傳）',
    observation: 'ML 領域有 4 位老師。問「3 位」時應傳 limit=3，而不是沿用預設 5。',
    turns: ['幫我找 3 位教機器學習的教授，只要名字和職稱就好。'],
  },
  {
    name: 'E2 ─ 多工具協作（search → get_detail）',
    observation: 'search_teachers 只回領域/辦公室概述；完整 email 需要 get_teacher_detail 才穩。好的 agent 應主動串兩個工具。',
    turns: ['幫我列出做電腦視覺的老師的 email。'],
  },
  {
    name: 'E3 ─ 多次搜尋彙整（agent 規劃能力）',
    observation: '資料中機器學習 4 位、電腦視覺 3 位、LLM 3 位、NLP 2 位。這題需要多次 search 再比較，考驗 agent 的主動規劃。',
    turns: ['資工系裡，機器學習和電腦視覺哪個領域的老師比較多？'],
  },
];

// 從 history 抽出所有 tool_call 細節（name + args）
function extractToolCallHistory(messages) {
  const calls = [];
  for (const m of messages) {
    if (m.role !== 'assistant') continue;
    // Claude 格式
    if (Array.isArray(m.content)) {
      for (const b of m.content) {
        if (b.type === 'tool_use') {
          calls.push({ name: b.name, args: b.input });
        }
      }
    }
    // OpenAI 格式
    if (m.tool_calls?.length) {
      for (const tc of m.tool_calls) {
        let args = {};
        try { args = JSON.parse(tc.function.arguments); } catch {}
        calls.push({ name: tc.function.name, args });
      }
    }
  }
  return calls;
}

async function runOne(client, turns) {
  let history = [];
  const trace = [];
  const startAll = Date.now();
  for (const userMsg of turns) {
    history.push({ role: 'user', content: userMsg });
    const t0 = Date.now();
    const callsBefore = extractToolCallHistory(history).length;
    const res = await client.chat(history);
    history = res.messages;
    const allCalls = extractToolCallHistory(history);
    const newCalls = allCalls.slice(callsBefore);
    trace.push({
      user: userMsg,
      assistant: res.reply,
      calls: newCalls,
      latencyMs: Date.now() - t0,
    });
  }
  return { trace, totalMs: Date.now() - startAll };
}

function fmtArgs(args) {
  const parts = Object.entries(args).map(([k, v]) => {
    const s = typeof v === 'string' ? `"${v}"` : String(v);
    return `${k}=${s}`;
  });
  return parts.join(', ');
}

function printTrace(label, result) {
  console.log(`\n  ${label}  (total ${result.totalMs}ms)`);
  for (const [i, t] of result.trace.entries()) {
    console.log(`    T${i+1} user>  ${t.user}`);
    if (t.calls.length === 0) {
      console.log(`        (no tool calls)`);
    } else {
      for (const c of t.calls) {
        console.log(`        ⚙ ${c.name}(${fmtArgs(c.args)})`);
      }
    }
    const reply = t.assistant.replace(/\n/g, ' ').slice(0, 200);
    console.log(`    T${i+1} ai  >  ${reply}${t.assistant.length > 200 ? '…' : ''}`);
    console.log(`        · latency: ${t.latencyMs}ms, tools this turn: ${t.calls.length}`);
  }
}

const claude = new LLMClient(mcp);
const gemma  = new OpenAILLMClient(mcp);

for (const ex of EXAMPLES) {
  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(ex.name);
  console.log(`  觀察重點: ${ex.observation}`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);

  printTrace('【Claude Sonnet 4.5】', await runOne(claude, ex.turns));
  printTrace('【Gemma 4 31B / vLLM】', await runOne(gemma, ex.turns));
}

console.log('\n═══════════════════════════════════════════════════════════');
process.exit(0);
