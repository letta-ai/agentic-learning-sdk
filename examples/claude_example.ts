/**
 * Claude Agent SDK Example - Agentic Learning SDK
 *
 * This example shows how to use the Agentic Learning SDK with Claude Agent SDK.
 * The SDK automatically captures conversations and manages persistent memory.
 *
 * Prerequisites:
 *     npm install @letta-ai/agentic-learning @anthropic-ai/claude-agent-sdk
 *     export ANTHROPIC_API_KEY="your-api-key"
 *     export LETTA_API_KEY="your-api-key"
 *
 * Usage:
 *     npx tsx claude_example.ts
 */

import { query } from "@anthropic-ai/claude-agent-sdk";
import { learning } from "@letta-ai/agentic-learning";

async function askClaude(message: string) {
  console.log(`User: ${message}\n`);
  process.stdout.write("Assistant: ");

  // That's it - wrap your API calls to enable persistent memory
  await learning({ agent: 'claude-demo' }, async () => {
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
