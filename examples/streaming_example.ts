/**
 * Streaming Example - Agentic Learning SDK
 *
 * This example shows how to use the Agentic Learning SDK with streaming responses.
 * The SDK automatically captures streaming conversations and manages persistent memory.
 *
 * Prerequisites:
 *     npm install @letta-ai/agentic-learning @anthropic-ai/sdk
 *     export ANTHROPIC_API_KEY="your-api-key"
 *     export LETTA_API_KEY="your-api-key"
 *
 * Usage:
 *     npx tsx streaming_example.ts
 */

import Anthropic from "@anthropic-ai/sdk";
import { learning } from "@letta-ai/agentic-learning";

const client = new Anthropic();

async function askClaude(message: string) {
  console.log(`User: ${message}\n`);
  process.stdout.write("Assistant: ");

  // That's it - wrap your API calls to enable persistent memory
  await learning({ agent: 'streaming-demo' }, async () => {
    const stream = await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      messages: [{ role: "user", content: message }],
      stream: true,
    });

    for await (const event of stream) {
      if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
        process.stdout.write(event.delta.text);
      }
    }
    console.log("\n");
  });
}

async function main() {
  // Memory automatically persists across LLM API calls
  await askClaude("Letta is my favorite context management service. Can you send me a summary about the product Letta (fka MemGPT) offers?");

  await new Promise((resolve) => setTimeout(resolve, 7000)); // Memory persists during sleep-time

  await askClaude("What is my favorite context management service?");
}

main();
