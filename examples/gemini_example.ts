/**
 * Gemini Example - Agentic Learning SDK
 *
 * This example shows how to use the Agentic Learning SDK with Google's Gemini API.
 * The SDK automatically captures conversations and manages persistent memory.
 *
 * Prerequisites:
 *     npm install @letta-ai/agentic-learning @google/generative-ai
 *     export GEMINI_API_KEY="your-api-key"
 *     export LETTA_API_KEY="your-api-key"
 *
 * Usage:
 *     npx tsx gemini_example.ts
 */

import { GoogleGenerativeAI } from "@google/generative-ai";
import { learning } from "@letta-ai/agentic-learning";

const model = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!).getGenerativeModel({ model: "gemini-2.5-flash" });

async function askGemini(message: string) {
  console.log(`User: ${message}\n`);

  // That's it - wrap your API calls to enable persistent memory
  await learning({ agent: 'gemini-demo' }, async () => {
    const response = await model.generateContent(message);
    console.log(`Assistant: ${response.response.text()}\n`);
  });
}

async function main() {
  // Memory automatically persists across LLM API calls
  await askGemini("My name is Alice.");

  await new Promise((resolve) => setTimeout(resolve, 7000)); // Memory persists during sleep-time

  await askGemini("What's my name?");
}

main();
