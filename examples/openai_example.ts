/**
 * OpenAI Example - Agentic Learning SDK
 *
 * This example shows how to use the Agentic Learning SDK with OpenAI's API.
 * The SDK automatically captures conversations and manages persistent memory.
 *
 * Prerequisites:
 *     npm install @letta-ai/agentic-learning openai
 *     export OPENAI_API_KEY="your-api-key"
 *     export LETTA_API_KEY="your-api-key"
 *
 * Usage:
 *     npx tsx openai_example.ts
 */

import OpenAI from "openai";
import { learning } from "@letta-ai/agentic-learning";

const client = new OpenAI();

async function askGPT(message: string) {
  console.log(`User: ${message}\n`);

  // That's it - wrap your API calls to enable persistent memory
  await learning({ agent: 'openai-demo' }, async () => {
    const response = await client.chat.completions.create({
      model: "gpt-4o",
      messages: [{ role: "user", content: message }],
    });

    console.log(`Assistant: ${response.choices[0].message.content}\n`);
  });
}

async function main() {
  // Memory automatically persists across LLM API calls
  await askGPT("My name is Alice.");

  await new Promise((resolve) => setTimeout(resolve, 7000)); // Memory persists during sleep-time

  await askGPT("What's my name?");
}

main();
