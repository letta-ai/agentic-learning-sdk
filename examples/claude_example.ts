/**
 * Claude Agent SDK Example - Agentic Learning SDK
 *
 * IMPORTANT: Claude Agent SDK requires dynamic import (require() inside learning callback)
 * for memory injection to work. The SDK spawns a subprocess at construction time, so it
 * must be patched before loading via a require hook. Don't use top-level imports!
 *
 * Prerequisites:
 *     npm install @letta-ai/agentic-learning @anthropic-ai/claude-agent-sdk
 *     export ANTHROPIC_API_KEY="your-api-key"
 *     export LETTA_API_KEY="your-api-key"
 *
 * Usage:
 *     npx tsx claude_example.ts
 */

import { learning } from "@letta-ai/agentic-learning";

async function askClaude(message: string) {
  console.log(`User: ${message}\n`);
  process.stdout.write("Assistant: ");

  // That's it - wrap your API calls to enable persistent memory
  await learning({ agent: 'claude-demo' }, async () => {
    // IMPORTANT: Use require() here (not import at top) for memory injection to work
    const { query } = require("@anthropic-ai/claude-agent-sdk");

    const conversation = query({
      prompt: message,
      options: {}
    });

    for await (const msg of conversation) {
      if (msg.type === "assistant" && msg.message?.content) {
        for (const block of msg.message.content) {
          if (block.type === "text") {
            process.stdout.write(block.text);
          }
        }
      }
    }
    console.log("\n");
  });
}

async function main() {
  // Memory automatically persists across LLM API calls
  await askClaude("My name is Alice.");

  await new Promise((resolve) => setTimeout(resolve, 7000)); // Memory persists during sleep-time

  await askClaude("What's my name?");
}

main();
