// llm-client.js — Claude tool-calling loop（mirror mini-project，多了 system prompt 支援）
//
// Claude 回覆兩種：
//   (A) stop_reason === 'end_turn'   → 結束，回傳文字
//   (B) stop_reason === 'tool_use'   → 呼叫 MCP 工具，結果塞回 messages 再問

import Anthropic from '@anthropic-ai/sdk';

export class LLMClient {
  constructor(mcpClient, {
    model = process.env.CLAUDE_MODEL ?? 'claude-haiku-4-5',
    maxTokens = 2048,
    system = undefined,
    timeout = 60_000,         // 每次 HTTP attempt 上限；配合 maxRetries=1 → 單次 .create() 最多 ~120s
  } = {}) {
    this.anthropic = new Anthropic({ timeout, maxRetries: 1 });
    this.mcp = mcpClient;
    this.model = model;
    this.maxTokens = maxTokens;
    this.system = system;
    console.log(`[LLM] Anthropic Claude (model=${model}, timeout=${timeout}ms${system ? ', system prompt set' : ''})`);
  }

  async chat(messages, { maxIterations = 5 } = {}) {   // 5 已足夠正常 Q&A，更高只是放大攻擊面
    const history = [...messages];

    for (let i = 0; i < maxIterations; i++) {
      const resp = await this.anthropic.messages.create({
        model: this.model,
        max_tokens: this.maxTokens,
        tools: this.mcp.getAnthropicTools(),
        messages: history,
        ...(this.system && { system: this.system }),
      });

      history.push({ role: 'assistant', content: resp.content });

      if (resp.stop_reason !== 'tool_use') {
        const text = resp.content
          .filter(b => b.type === 'text')
          .map(b => b.text)
          .join('');
        return { reply: text, messages: history };
      }

      const toolUses = resp.content.filter(b => b.type === 'tool_use');
      console.log(`  [tool_use] ${toolUses.map(t => t.name).join(', ')}`);

      const toolResults = await Promise.all(
        toolUses.map(async tc => {
          try {
            const output = await this.mcp.callTool(tc.name, tc.input);
            return { type: 'tool_result', tool_use_id: tc.id, content: output };
          } catch (e) {
            return {
              type: 'tool_result',
              tool_use_id: tc.id,
              content: `Error: ${e.message}`,
              is_error: true,
            };
          }
        }),
      );

      history.push({ role: 'user', content: toolResults });
    }

    throw new Error(`Tool-calling exceeded ${maxIterations} iterations`);
  }
}
