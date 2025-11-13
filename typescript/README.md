# Agentic Learning SDK

Add persistent memory to any LLM agent with one line of code. This Agentic Learning SDK automatically captures conversations, manages context, and enables agents to remember information across sessions.

```typescript
await learning({ agent: 'my_agent' }, async () => {
    response = client.chat.completions.create(...) // Memory handled automatically
});
```

[![npm shield](https://img.shields.io/npm/v/@letta-ai/agentic-learning)](https://www.npmjs.com/package/@letta-ai/agentic-learning)

## Get Started

### Installation

```bash
npm install @letta-ai/agentic-learning
```

### Basic Usage

```bash
# Set your API keys
export OPENAI_API_KEY="your-openai-key"
export LETTA_API_KEY="your-letta-key"
```

```typescript
import OpenAI from 'openai';
import { learning } from '@letta-ai/agentic-learning';

const openai = new OpenAI();

// Add memory to your agent with one line
await learning({ agent: 'my-agent' }, async () => {
  // Your LLM call - conversation is automatically captured
  const response = await openai.chat.completions.create({
    model: 'gpt-5',
    messages: [{ role: 'user', content: 'My name is Alice' }],
  });

  // Agent remembers prior context
  const response = await openai.chat.completions.create({
    model: 'gpt-5',
    messages: [{ role: 'user', content: 'What is my name?' }],
  });
  // Returns: "Your name is Alice"
});
```

That's it - this SDK automatically:
- ✅ Captures all conversations
- ✅ Injects relevant memory into prompts
- ✅ Saves to persistent storage (Letta)
- ✅ Recalls information across sessions

## Supported Providers

| Provider | Package | Status | Example |
|----------|---------|--------|---------|
| **Anthropic** | `anthropic` | ✅ Stable | [anthropic_example.ts](examples/anthropic_example.ts) |
| **Claude Agent SDK** | `claude-agent-sdk` | ✅ Stable | [claude_example.ts](examples/claude_example.ts) |
| **OpenAI Chat Completions** | `openai` | ✅ Stable | [openai_example.ts](examples/openai_example.ts) |
| **OpenAI Responses API** | `openai` | ✅ Stable | [openai_responses_example.ts](examples/openai_responses_example.ts) |
| **Gemini** | `google-generativeai` | ✅ Stable | [gemini_example.ts](examples/gemini_example.ts) |
| **Vercel AI SDK** | `ai-sdk` | 🛠️ Experimental | [vercel_example.ts](examples/vercel_example.ts) |

### Examples

See the top-level [`../examples/`](../examples/) directory for examples:

```bash
# Run from examples directory
cd ../examples
npm install
npm run openai
```

## Core concepts in Letta:

Letta is built on the [MemGPT](https://arxiv.org/abs/2310.08560) research paper, which introduced the concept of the "LLM Operating System" for memory management:

1. [**Memory Hierarchy**](https://docs.letta.com/guides/agents/memory): Agents have self-editing memory split between in-context and out-of-context memory
2. [**Memory Blocks**](https://docs.letta.com/guides/agents/memory-blocks): In-context memory is composed of persistent editable blocks
3. [**Agentic Context Engineering**](https://docs.letta.com/guides/agents/context-engineering): Agents control their context window using tools to edit, delete, or search memory
4. [**Perpetual Self-Improving Agents**](https://docs.letta.com/guides/agents/overview): Every agent has a perpetual (infinite) message history


## Local Development

Connect to a local Letta server instead of the cloud:

```typescript
const learningClient = new AgenticLearning({
  baseUrl: "http://localhost:8283"
});

await learning({ agent: 'my-agent', client: learningClient }, async () => {
    // Your LLM call - conversation is automatically captured
});
```

Run Letta locally with Docker:

```bash
docker run \
  -v ~/.letta/.persist/pgdata:/var/lib/postgresql/data \
  -p 8283:8283 \
  -e OPENAI_API_KEY="your_key" \
  letta/letta:latest
```

See the [self-hosting guide](https://docs.letta.com/guides/selfhosting) for more options.

### Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Watch mode
npm run dev
```

## License

Apache-2.0
