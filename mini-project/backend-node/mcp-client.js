// mcp-client.js — 教學範例：用官方 MCP SDK 連線到 stdio MCP server
//
// 這支 class 做三件事：
//   1. connect()          : 依 config 依序啟動每個 MCP server，列出它們的工具
//   2. getAnthropicTools(): 把工具轉成 Claude API 認得的 { name, description, input_schema } 格式
//   3. callTool()         : 呼叫某支工具並回傳文字結果
//
// SDK 幫我們處理了：child_process spawn、stdin/stdout JSON-RPC 收發、
// 逐行緩衝、訊息配對、逾時、錯誤回復。這些細節有興趣可讀 SDK 原始碼。

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

export class MCPClient {
  constructor(config) {
    this.config = config;
    this.tools = [];              // 扁平化的工具清單（所有 server 合併）
    this.toolToClient = new Map(); // tool name → 對應的 SDK Client 實例
  }

  async connect() {
    for (const [serverName, spec] of Object.entries(this.config.mcpServers)) {
      const transport = new StdioClientTransport({
        command: spec.command,
        args: spec.args,
        env: { ...process.env, ...(spec.env ?? {}) },
      });

      const client = new Client(
        { name: 'mini-client', version: '1.0.0' },
        { capabilities: {} },
      );

      await client.connect(transport);
      const { tools } = await client.listTools();

      for (const tool of tools) {
        this.tools.push(tool);
        this.toolToClient.set(tool.name, client);
      }

      console.log(`✓ ${serverName} → ${tools.map(t => t.name).join(', ')}`);
    }
  }

  getAnthropicTools() {
    return this.tools.map(t => ({
      name: t.name,
      description: t.description ?? '',
      input_schema: t.inputSchema ?? { type: 'object', properties: {} },
    }));
  }

  // OpenAI / vLLM / Ollama 共用的 tool 格式（跟 Claude 不同）
  getOpenAITools() {
    return this.tools.map(t => ({
      type: 'function',
      function: {
        name: t.name,
        description: t.description ?? '',
        parameters: t.inputSchema ?? { type: 'object', properties: {} },
      },
    }));
  }

  async callTool(name, args) {
    const client = this.toolToClient.get(name);
    if (!client) throw new Error(`Unknown tool: ${name}`);
    const result = await client.callTool({ name, arguments: args ?? {} });
    // SDK 回傳 { content: [{type:'text', text:'...'}] }；串成一個字串給 LLM。
    return result.content.map(c => c.text ?? JSON.stringify(c)).join('\n');
  }
}
