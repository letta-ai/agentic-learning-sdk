# Agentic Learning SDK - TypeScript

Automatic memory integration with Letta for TypeScript/JavaScript LLM applications.

## Installation

```bash
npm install @letta-ai/agentic-learning
```

## Quick Start

```typescript
import { AgenticLearning, learning, autoInstall } from '@letta-ai/agentic-learning';
import OpenAI from 'openai';

// Install interceptors
autoInstall();

// Create Letta client
const learningClient = new AgenticLearning({
  baseUrl: 'http://localhost:8283', // or use https://api.letta.com
});

// Create OpenAI client
const openai = new OpenAI();

// Use learning context
const context = learning({
  agent: 'my-agent',
  client: learningClient,
});

try {
  // Your LLM call - conversation is automatically captured!
  const response = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: 'My name is Alice' }],
  });

  console.log(response.choices[0].message.content);
} finally {
  context.exit();
}
```

## Examples

See the top-level [`../examples/`](../examples/) directory for examples:

```bash
# Run from examples directory
cd ../examples
npm install
npm run openai
```

## Development

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

## Key Features

- Async-safe context management using Node.js `AsyncLocalStorage`
- Automatic conversation capture and memory injection
- Support for streaming responses
- Type-safe API with TypeScript
- Currently supports: OpenAI (Chat Completions + Responses API)

## License

Apache-2.0
