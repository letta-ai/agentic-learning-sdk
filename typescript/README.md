# Agentic Learning SDK - AI Memory Layer for Any Application

Add continual learning to any LLM agent with one line of code. This SDK enables agents to learn from every conversation and recall context across sessions—making your agents truly stateful.

```typescript
import OpenAI from 'openai';
import { learning } from '@letta-ai/agentic-learning';

const client = new OpenAI();

await learning({ agent: 'my_agent' }, async () => {
    // LLM is now stateful!
    response = await client.chat.completions.create(...) 
});
```

[![npm shield](https://img.shields.io/npm/v/@letta-ai/agentic-learning)](https://www.npmjs.com/package/@letta-ai/agentic-learning)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](../LICENSE)
[![Tests](https://img.shields.io/badge/tests-40%2F40%20passing-brightgreen)](tests/)

## Installation

```bash
npm install @letta-ai/agentic-learning
```

## Quick Start

```bash
# Set your API keys
export OPENAI_API_KEY="your-openai-key"
export LETTA_API_KEY="your-letta-key"
```

```typescript
import { learning } from '@letta-ai/agentic-learning';
import OpenAI from 'openai';

const client = new OpenAI();

// Add continual learning with one line
await learning({ agent: "my_assistant" }, async () => {
    // All LLM calls inside this block have learning enabled
    const response = await client.chat.completions.create({
        model: "gpt-5",
        messages: [{ role: "user", content: "My name is Alice" }]
    });

    // Agent remembers prior context
    const response2 = await client.chat.completions.create({
        model: "gpt-5",
        messages: [{ role: "user", content: "What's my name?" }]
    });
    // Returns: "Your name is Alice"
});
```

That's it - this SDK automatically:
- ✅ Learns from every conversation
- ✅ Recalls relevant context when needed
- ✅ Remembers across sessions
- ✅ Works with your existing LLM code

## Supported Providers

| Provider | Package | Status | Example |
|----------|---------|--------|---------|
| **OpenAI Chat** | `openai>=4.0.0` | ✅ Stable | [openai_example.ts](../examples/openai_example.ts) |
| **OpenAI Responses** | `openai>=4.0.0` | ✅ Stable | [openai_responses_example.ts](../examples/openai_responses_example.ts) |
| **Anthropic** | `@anthropic-ai/sdk>=0.30.0` | ✅ Stable | [anthropic_example.ts](../examples/anthropic_example.ts) |
| **Claude Agent SDK** | `@anthropic-ai/claude-agent-sdk>=0.1.0` | ✅ Stable | [claude_example.ts](../examples/claude_example.ts) |
| **Gemini** | `@google/generative-ai>=0.21.0` | ✅ Stable | [gemini_example.ts](../examples/gemini_example.ts) |
| **Vercel AI SDK** | `ai>=3.0.0` | ✅ Stable | [vercel_example.ts](../examples/vercel_example.ts) |

[Create an issue](https://github.com/letta-ai/agentic-learning-sdk/issues) to request support for another provider, or contribute a PR.

## How It Works

This SDK adds **stateful memory** to your existing LLM code with zero architectural changes:

**Benefits:**
- 🔌 **Drop-in integration** - Works with your existing LLM Provider SDK code
- 🧠 **Automatic memory** - Relevant context retrieved and injected into prompts
- 💾 **Persistent across sessions** - Conversations remembered even after restarts
- 💰 **Cost-effective** - Only relevant context injected, reducing token usage
- ⚡ **Fast retrieval** - Semantic search powered by Letta's optimized infrastructure
- 🏢 **Production-ready** - Built on Letta's proven memory management platform

**Architecture:**

```
1. 🎯 Wrap      2. 📝 Capture       3. 🔍 Retrieve   4. 🤖 Respond
   your code       conversations      relevant         with full
   in learning     automatically      memories         context

┌─────────────┐
│  Your Code  │
│  learning() │
└──────┬──────┘
       │
       ▼
┌─────────────┐    ┌──────────────┐
│ Interceptor │───▶│ Letta Server │  (Stores conversations,
│  (Inject)   │◀───│  (Memory)    │   retrieves context)
└──────┬──────┘    └──────────────┘
       │
       ▼
┌─────────────┐
│  LLM API    │  (Sees enriched prompts)
│ OpenAI/etc  │
└─────────────┘
```

## Key Features

### Memory Across Sessions
```typescript
// First session
await learning({ agent: "sales_bot" }, async () => {
    const response = await client.chat.completions.create({
        messages: [{ role: "user", content: "I'm interested in Product X" }]
    });
});

// Later session - agent remembers automatically
await learning({ agent: "sales_bot" }, async () => {
    const response = await client.chat.completions.create({
        messages: [{ role: "user", content: "Tell me more about that product" }]
    });
    // Agent knows you're asking about Product X
});
```

### Search Agent Memory
```typescript
import { AgenticLearning } from '@letta-ai/agentic-learning';

const learningClient = new AgenticLearning();

// Search past conversations
const messages = await learningClient.memory.search({
    agent: "my_agent",
    query: "What are my project requirements?"
});
```

## Advanced Features

### Capture-Only Mode
```typescript
// Store conversations without injecting memory (useful for logging)
await learning({ agent: "my_agent", captureOnly: true }, async () => {
    const response = await client.chat.completions.create(...);
});
```

### Custom Memory Blocks
```typescript
// Configure which memory blocks to use
await learning({ agent: "sales_bot", memory: ["customer", "product_preferences"] }, async () => {
    const response = await client.chat.completions.create(...);
});
```

## Local Development

### Using Local Letta Server

```typescript
import { AgenticLearning, learning } from '@letta-ai/agentic-learning';

// Connect to local server
const learningClient = new AgenticLearning({
    baseUrl: "http://localhost:8283"
});

await learning({ agent: 'my_agent', client: learningClient }, async () => {
    const response = await client.chat.completions.create(...);
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

### Development Setup

```bash
# Clone repository
git clone https://github.com/letta-ai/agentic-learning-sdk.git
cd agentic-learning-sdk/typescript

# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Run Claude tests (separate runner)
npm run test:claude

# Watch mode
npm run dev
```

## Examples

See the [`examples/`](../examples/) directory for complete working examples:

```bash
cd ../examples
npm install
npx tsx openai_example.ts
```

## Documentation

- 📖 [Full Documentation](../README.md) - Complete SDK documentation
- 🧪 [Test Suite](tests/README.md) - 40/40 tests passing (100%)
- 🎯 [Examples](../examples/README.md) - Working examples for all providers
- 💬 [Letta Discord](https://discord.gg/letta) - Community support
- 📚 [Letta Docs](https://docs.letta.com/) - Letta platform documentation

## Requirements

- Node.js 18+
- Letta API key (sign up at [letta.com](https://www.letta.com/))
- At least one LLM provider SDK

## License

Apache 2.0 - See [LICENSE](../LICENSE) for details.

Built with [Letta](https://www.letta.com/) - the leading platform for building stateful AI agents with long-term memory.
