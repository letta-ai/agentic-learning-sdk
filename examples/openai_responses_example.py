"""
OpenAI Responses API Example - Agentic Learning SDK

This example shows how to use the Agentic Learning SDK with OpenAI's Responses API.
The Responses API is OpenAI's new unified API (released March 2025) that combines
the best of Chat Completions and Assistants APIs with built-in tools.

Prerequisites:
    pip install agentic-learning openai
    export OPENAI_API_KEY="your-api-key"
    export LETTA_API_KEY="your-api-key"

Usage:
    python3 openai_responses_example.py
"""

import time
from openai import OpenAI
from agentic_learning import learning


def get_text_from_output(output):
    """Extract text from Responses API output for display."""
    if isinstance(output, str):
        return output
    elif isinstance(output, list):
        texts = []
        for message in output:
            if hasattr(message, 'content'):
                for content_item in message.content:
                    if hasattr(content_item, 'text'):
                        texts.append(content_item.text)
        return ' '.join(texts) if texts else str(output)
    return str(output)


client = OpenAI()

def ask_gpt(message: str):
    print(f"User: {message}\n")

    # That's it - wrap your API calls to enable persistent memory
    with learning(agent="openai-responses-demo"):
        response = client.responses.create(
            model="gpt-5",
            input=message
        )
        print(f"Assistant: {get_text_from_output(response.output)}\n")

# Memory automatically persists across LLM API calls
ask_gpt("My name is Alice.")

time.sleep(7) # Memory persists during sleep-time

ask_gpt("What's my name?")
