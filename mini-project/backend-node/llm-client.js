// llm-client.js — 教學範例：Claude tool-calling loop
//
// 這是整個系統的核心概念。Claude 回覆可能是：
//   (A) 純文字 (stop_reason === 'end_turn')         → 結束，回傳文字
//   (B) 要求呼叫工具 (stop_reason === 'tool_use')   → 呼叫 MCP 工具後，把結果塞回 messages 再問一次
//
// 迴圈跑到 (A) 為止。最多 maxIterations 輪，避免 Claude 不停呼叫工具。

import Anthropic from '@anthropic-ai/sdk';

export class LLMClient {
  constructor(mcpClient, {
    model = process.env.CLAUDE_MODEL ?? 'claude-sonnet-4-5',
    maxTokens = 2048,
  } = {}) {
    this.anthropic = new Anthropic(); // 會自動讀 ANTHROPIC_API_KEY 環境變數
    this.mcp = mcpClient;
    this.model = model;
    this.maxTokens = maxTokens;
  }

  async chat(messages, { maxIterations = 10 } = {}) {
    const history = [...messages];

    for (let i = 0; i < maxIterations; i++) {
      const resp = await this.anthropic.messages.create({
        model: this.model,
        max_tokens: this.maxTokens,
        tools: this.mcp.getAnthropicTools(),
        messages: history,
      });

      // 永遠把 assistant 回覆 push 進 history（即使是 tool_use，下一輪要看得到）
      history.push({ role: 'assistant', content: resp.content });

      // 情況 (A)：Claude 已經講完話
      if (resp.stop_reason !== 'tool_use') {
        const text = resp.content
          .filter(b => b.type === 'text')
          .map(b => b.text)
          .join('');
        return { reply: text, messages: history };
      }

      // 情況 (B)：Claude 要求呼叫工具。可能同一輪呼叫多支，全部並行執行。
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

      // 把 tool 執行結果當成一則 user 訊息送回給 Claude
      history.push({ role: 'user', content: toolResults });
    }

    throw new Error(`Tool-calling exceeded ${maxIterations} iterations`);
  }
}
