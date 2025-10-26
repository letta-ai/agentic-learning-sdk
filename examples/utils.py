"""
Utility functions for examples.

Provides colored terminal output helpers.
"""

from typing import List
from letta_client import LettaMessageUnion


# ANSI color codes for terminal output
YELLOW = "\033[33m"
PURPLE = "\033[35m"
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def print_u(message: str, end: str = "\n", flush: bool = False):
    """Print user message with yellow 'User:' prefix."""
    print(f"{YELLOW}User:{RESET} {message}", end=end, flush=flush)


def print_a(message: str, end: str = "\n", flush: bool = False):
    """Print assistant message with purple 'Assistant:' prefix."""
    print(f"{PURPLE}Assistant:{RESET} {message}", end=end, flush=flush)


def print_g(message: str, end: str = "\n"):
    """Print green success message."""
    print(f"{GREEN}{message}{RESET}", end=end)


def print_r(message: str, end: str = "\n"):
    """Print red message."""
    print(f"{RED}{message}{RESET}", end=end)


def print_messages(messages: List[LettaMessageUnion]):
    for message in messages:
        if message.message_type == "user_message":
            print_u(message.content)
        elif message.message_type == "assistant_message":
            print_a(message.content)
        elif message.message_type == "reasoning_message":
            print_a(message.reasoning)
            
