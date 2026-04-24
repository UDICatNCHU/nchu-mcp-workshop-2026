// llm-client-openai.js — 對 OpenAI 兼容 endpoint 的 adapter
//
// 適用情境：
//   - 自架 vLLM serve（預設 http://localhost:8000/v1）
//   - Ollama 啟用 OpenAI 相容模式
//   - LiteLLM 代理
//   - 真的 OpenAI / Azure OpenAI
//
// 與 llm-client.js（Claude 版）的差異：
//   1. Tool format：{type:'function', function:{name, description, parameters}}
//      而非 Claude 的 {name, description, input_schema}
//   2. Tool call 在 message.tool_calls（object array），而非 Claude content block
//   3. Tool result 用 role='tool' + tool_call_id，而非 Claude 的 tool_result content block
//   4. 停止條件：!message.tool_calls || finish_reason==='stop'
//
// 這個檔案和 llm-client.js 並存，由 server.js 根據 LLM_PROVIDER 環境變數選擇。

import OpenAI from 'openai';

export class OpenAILLMClient {
  constructor(mcpClient, {
    baseURL = process.env.OPENAI_BASE_URL ?? 'http://localhost:8000/v1',
    apiKey = process.env.OPENAI_API_KEY ?? 'dummy',  // vLLM 不驗證
    model = process.env.OPENAI_MODEL ?? 'gemma-4',
    maxTokens = 2048,
  } = {}) {
    this.openai = new OpenAI({ baseURL, apiKey });
    this.mcp = mcpClient;
    this.model = model;
    this.maxTokens = maxTokens;
    console.log(`[LLM] OpenAI-compatible: ${baseURL} (model=${model})`);
  }

  // 剝除 Gemma 4 的 thinking channel 標記（vLLM 0.19.x parser 尚未處理）
  // 例：  "<|channel>thought <channel|>實際內容"  →  "實際內容"
  _stripThinkingMarkers(text) {
    return text
      .replace(/<\|channel>thought[\s\S]*?<channel\|>/g, '')
      .replace(/<\|channel>final[\s\S]*?<channel\|>/g, '')
      .trim();
  }

  // 把外部傳進來的 messages 正規化成 OpenAI 格式
  // 前端可能傳純文字 {role, content:string}；歷史可能含 tool_calls / role=tool
  _normalize(messages) {
    return messages.map(m => {
      // 若 content 是 array（Claude 格式殘留），抽出文字
      if (Array.isArray(m.content)) {
        const text = m.content
          .filter(b => b && b.type === 'text')
          .map(b => b.text)
          .join('');
        return { role: m.role, content: text };
      }
      return m;
    });
  }

  async chat(messages, { maxIterations = 10 } = {}) {
    const history = this._normalize(messages);

    for (let i = 0; i < maxIterations; i++) {
      const resp = await this.openai.chat.completions.create({
        model: this.model,
        max_tokens: this.maxTokens,
        tools: this.mcp.getOpenAITools(),
        messages: history,
      });

      const msg = resp.choices[0].message;
      history.push(msg);

      // 沒有 tool call → 結束
      if (!msg.tool_calls || msg.tool_calls.length === 0) {
        const clean = this._stripThinkingMarkers(msg.content ?? '');
        return { reply: clean, messages: history };
      }

      console.log(`  [tool_use] ${msg.tool_calls.map(tc => tc.function.name).join(', ')}`);

      // 並行執行所有 tool calls
      const toolResults = await Promise.all(
        msg.tool_calls.map(async tc => {
          let args;
          try {
            args = JSON.parse(tc.function.arguments || '{}');
          } catch (e) {
            return {
              role: 'tool',
              tool_call_id: tc.id,
              content: `Error: model returned invalid JSON arguments: ${e.message}`,
            };
          }

          try {
            const output = await this.mcp.callTool(tc.function.name, args);
            return { role: 'tool', tool_call_id: tc.id, content: output };
          } catch (e) {
            return {
              role: 'tool',
              tool_call_id: tc.id,
              content: `Error: ${e.message}`,
            };
          }
        }),
      );

      history.push(...toolResults);
    }

    throw new Error(`Tool-calling exceeded ${maxIterations} iterations`);
  }
}
