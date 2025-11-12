/**
 * Quickstart - Agentic Learning SDK (TypeScript)
 *
 * Get started with persistent memory in 30 seconds.
 *
 * Prerequisites:
 *     npm install @letta-ai/agentic-learning @anthropic-ai/sdk
 *     export ANTHROPIC_API_KEY="your-api-key"
 *     export LETTA_API_KEY="your-api-key"
 *
 * Usage:
 *     npx tsx quickstart.ts
 */

import Anthropic from "@anthropic-ai/sdk";
import { withLearning } from "@letta-ai/agentic-learning";

// Initialize LLM client
const client = new Anthropic();

async function askClaude(message: string) {
  console.log(`User: ${message}\n`);

  // That's it - wrap your API calls to enable persistent memory
  await withLearning({ agent: 'quickstart-ts-demo' }, async () => {
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
  await askClaude("My name is Bob and I love TypeScript.");

  await new Promise((resolve) => setTimeout(resolve, 5000)); // Wait for memory to persist

  await askClaude("What's my name and favorite language?");
}

main();
