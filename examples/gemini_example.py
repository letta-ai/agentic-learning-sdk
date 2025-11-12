"""
Gemini Example - Agentic Learning SDK

This example shows how to use the Agentic Learning SDK with Google's Gemini API.
The SDK automatically captures conversations and manages persistent memory.

Prerequisites:
    pip install agentic-learning google-generativeai
    export GEMINI_API_KEY="your-api-key"
    export LETTA_API_KEY="your-api-key"

Usage:
    python3 gemini_example.py
"""

import time
import google.generativeai as genai
from agentic_learning import learning

model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(message: str):
    print(f"User: {message}\n")

    # That's it - wrap your API calls to enable persistent memory
    with learning(agent="gemini-demo"):
        response = model.generate_content(message)
        print(f"Assistant: {response.text}\n")

# Memory automatically persists across LLM API calls
ask_gemini("My name is Alice.")

time.sleep(7) # Memory persists during sleep-time

ask_gemini("What's my name?")
