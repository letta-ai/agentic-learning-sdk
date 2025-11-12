/**
 * Capture Only Example - Agentic Learning SDK
 *
 * This example demonstrates using capture_only mode, where the SDK captures
 * conversations without modifying the LLM behavior. You can then retrieve
 * and search through stored memories separately.
 *
 * Prerequisites:
 *     npm install @letta-ai/agentic-learning @anthropic-ai/sdk
 *     export ANTHROPIC_API_KEY="your-api-key"
 *     export LETTA_API_KEY="your-api-key"
 *
 * Usage:
 *     npx tsx capture_only_example.ts
 */

import Anthropic from "@anthropic-ai/sdk";
import { learning, AgenticLearning } from "@letta-ai/agentic-learning";

const client = new Anthropic();

async function askClaude(message: string) {
  console.log(`User: ${message}\n`);

  // Use capture_only mode to store conversations without modifying LLM behavior
  await learning({ agent: 'capture-only-demo', captureOnly: true }, async () => {
    const response = await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      messages: [{ role: "user", content: message }],
    });

    const text = response.content[0].type === "text" ? response.content[0].text : "";
    console.log(`Assistant: ${text}\n`);
  });
}

const learningClient = new AgenticLearning();

async function memory_search(prompt: string) {
  console.log("\n--- Memory Search ---\n");
  console.log(`Prompt: ${prompt}\n`);

  // Search through stored memories
  const messages = await learningClient.memory.search("capture-only-demo", prompt);
  
  for (const message of messages) {
    if (message.message_type === "user_message") {
      console.log(`User: ${message.content}`);
    } else if (message.message_type === "assistant_message") {
      console.log(`Assistant: ${message.content}`);
    }
  }
}

async function messageHistory() {
  console.log("\n--- Message History ---\n");

  // List message history
  const messages = await learningClient.messages.list("capture-only-demo");
  
  for (const message of messages) {
    if (message.message_type === "user_message") {
      console.log(`User: ${message.content}`);
    } else if (message.message_type === "assistant_message") {
      console.log(`Assistant: ${message.content}`);
    }
  }
}

async function main() {
  await askClaude("My name is Alice.");

  await new Promise((resolve) => setTimeout(resolve, 7000)); // Memory persists during sleep-time

  // Without memory injection, Claude doesn't know about previous context
  await askClaude("What's my name?");

  // Retrieve answer from stored memory
  await memory_search("What's my name?");

  // Retrieve conversation history
  await messageHistory();
}

main();
