/**
 * Vercel AI SDK Example - Agentic Learning SDK
 *
 * This example shows how to use the Agentic Learning SDK with Vercel AI SDK.
 * The SDK automatically captures conversations and manages persistent memory.
 *
 * Prerequisites:
 *     npm install @letta-ai/agentic-learning ai @ai-sdk/anthropic
 *     export ANTHROPIC_API_KEY="your-api-key"
 *     export LETTA_API_KEY="your-api-key"
 *
 * Usage:
 *     npx tsx vercel_example.ts
 */

import { generateText } from "ai";
import { anthropic } from "@ai-sdk/anthropic";
import { learning } from "@letta-ai/agentic-learning";

async function askAI(message: string) {
  console.log(`User: ${message}\n`);

  // That's it - wrap your API calls to enable persistent memory
  await learning({ agent: 'vercel-demo' }, async () => {
    const { text } = await generateText({
      model: anthropic("claude-sonnet-4-20250514"),
      prompt: message,
    });

    console.log(`Assistant: ${text}\n`);
  });
}

async function main() {
  // Memory automatically persists across LLM API calls
  await askAI("My name is Alice.");

  await new Promise((resolve) => setTimeout(resolve, 7000)); // Memory persists during sleep-time

  await askAI("What's my name?");
}

main();
