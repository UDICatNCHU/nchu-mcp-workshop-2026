// llm-client-openai.js — OpenAI 兼容 endpoint adapter（mirror mini-project，多了 system 支援）

import OpenAI from 'openai';

export class OpenAILLMClient {
  constructor(mcpClient, {
    baseURL = process.env.OPENAI_BASE_URL ?? 'http://localhost:8000/v1',
    apiKey = process.env.OPENAI_API_KEY ?? 'dummy',
    model = process.env.OPENAI_MODEL ?? 'gemma-4',
    maxTokens = 2048,
    system = undefined,
    timeout = 60_000,
  } = {}) {
    this.openai = new OpenAI({ baseURL, apiKey, timeout });
    this.mcp = mcpClient;
    this.model = model;
    this.maxTokens = maxTokens;
    this.system = system;
    console.log(`[LLM] OpenAI-compatible: ${baseURL} (model=${model}, timeout=${timeout}ms${system ? ', system prompt set' : ''})`);
  }

  // 剝除 Gemma 4 的 thinking channel 標記（vLLM 的 gemma4_tool_parser 暫未處理）
  _stripThinkingMarkers(text) {
    return text
      .replace(/<\|channel>thought[\s\S]*?<channel\|>/g, '')
      .replace(/<\|channel>final[\s\S]*?<channel\|>/g, '')
      .trim();
  }

  _normalize(messages) {
    return messages.map(m => {
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

  async chat(messages, { maxIterations = 5 } = {}) {
    // 剝掉 client 端送回來的 system 訊息（避免 stale prompt 永遠卡在 history）
    // 也避免惡意 client 自塞 system message 篡改角色
    const history = this._normalize(messages).filter(m => m.role !== 'system');

    // OpenAI 的 system 是 messages 第一筆 role=system，不是頂層欄位
    if (this.system) {
      history.unshift({ role: 'system', content: this.system });
    }

    for (let i = 0; i < maxIterations; i++) {
      const resp = await this.openai.chat.completions.create({
        model: this.model,
        max_tokens: this.maxTokens,
        tools: this.mcp.getOpenAITools(),
        messages: history,
      });

      const msg = resp.choices[0].message;
      history.push(msg);

      if (!msg.tool_calls || msg.tool_calls.length === 0) {
        const clean = this._stripThinkingMarkers(msg.content ?? '');
        return { reply: clean, messages: history };
      }

      console.log(`  [tool_use] ${msg.tool_calls.map(tc => tc.function.name).join(', ')}`);

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
