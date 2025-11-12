/**
 * Anthropic Example - Agentic Learning SDK
 *
 * This example shows how to use the Agentic Learning SDK with Anthropic's Claude API.
 * The SDK automatically captures conversations and manages persistent memory.
 *
 * Prerequisites:
 *     npm install @letta-ai/agentic-learning @anthropic-ai/sdk
 *     export ANTHROPIC_API_KEY="your-api-key"
 *     export LETTA_API_KEY="your-api-key"
 *
 * Usage:
 *     npx tsx anthropic_example.ts
 */

import Anthropic from "@anthropic-ai/sdk";
import { learning } from "@letta-ai/agentic-learning";

const client = new Anthropic();

async function askClaude(message: string) {
  console.log(`User: ${message}\n`);

  // That's it - wrap your API calls to enable persistent memory
  await learning({ agent: 'anthropic-demo' }, async () => {
    const response = await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      messages: [{ role: "user", content: message }],
    });

    const text = response.content[0].type === "text" ? response.content[0].text : "";
    console.log(`Assistant: ${text}\n`);
  });
}

async function main() {
  // Memory automatically persists across LLM API calls
  await askClaude("My name is Alice.");

  await new Promise((resolve) => setTimeout(resolve, 7000)); // Memory persists during sleep-time

  await askClaude("What's my name?");
}

main();
