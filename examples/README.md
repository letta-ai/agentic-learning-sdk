# Agentic Learning SDK - Examples

Examples for using the Agentic Learning SDK with different LLM providers.

## Quick Start

### Python

```bash
pip install agentic-learning openai
export OPENAI_API_KEY="your-api-key"
cd examples
python3 openai_example.py
```

### TypeScript

```bash
cd examples
npm install
export OPENAI_API_KEY="your-api-key"
npm run openai
```

## Available Examples

### Python
- `openai_example.py` - OpenAI Chat Completions
- `openai_responses_example.py` - OpenAI Responses API
- `anthropic_example.py` - Anthropic Claude
- `gemini_example.py` - Google Gemini
- `claude_example.py` - Claude Agent SDK
- `claude_example_interactive.py` - Interactive CLI with Claude

### TypeScript
- `openai_example.ts` - OpenAI integration

## What the Examples Show

Each example demonstrates:
1. **Memory Storage** - Agents remember information across messages
2. **Streaming** - Real-time token-by-token output
3. **Capture-Only Mode** - Store conversations without memory injection
4. **Memory Recall** - Search and retrieve stored memories
