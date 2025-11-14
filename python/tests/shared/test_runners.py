"""
Reusable test logic for all provider interceptor tests.

Each function encapsulates a single test case that can be called
from provider-specific test files. This approach balances code reuse
with readability - each test file explicitly calls these functions,
making the test structure clear and maintainable.

All test functions follow the same pattern:
1. Accept all necessary fixtures/params as arguments
2. Execute test logic
3. Make assertions
4. No return value (assertions raise on failure)
"""

import time
import asyncio
import inspect
from agentic_learning import learning


def conversation_saved(learning_client, agent_name, make_call, sleep_config, expected_content):
    """
    Test that conversations are captured and saved to Letta.

    Args:
        learning_client: AgenticLearning client fixture
        agent_name: Unique agent name (from cleanup_agent fixture)
        make_call: Function that makes LLM API call - signature: (client, prompt) -> response
        sleep_config: Dict with sleep durations (e.g., {'long_wait': 5.0})
        expected_content: String that should appear in saved messages
    """
    agent = learning_client.agents.create(agent=agent_name)
    assert agent is not None

    # Make call within learning context
    with learning(agent=agent_name, client=learning_client):
        make_call(f"My name is {expected_content}")

    # Wait for async processing
    time.sleep(sleep_config['long_wait'])

    # Verify messages were saved
    messages = learning_client.messages.list(agent_name)
    assert len(messages) > 0, "No messages saved"

    # Check expected content appears in messages
    message_contents = []
    for msg in messages:
        if hasattr(msg, 'content') and isinstance(msg.content, str):
            message_contents.append(msg.content)
        elif hasattr(msg, 'reasoning') and isinstance(msg.reasoning, str):
            message_contents.append(msg.reasoning)

    assert any(expected_content in c for c in message_contents), \
        f"'{expected_content}' not found in messages: {message_contents[:3]}"


def memory_injection(learning_client, agent_name, make_call, captured_state,
                     sleep_config, expected_in_prompt):
    """
    Test that memory is injected into LLM calls.

    Args:
        learning_client: AgenticLearning client fixture
        agent_name: Unique agent name (from cleanup_agent fixture)
        make_call: Function that makes LLM API call - signature: (prompt) -> response
        captured_state: Function that returns captured kwargs/state - signature: () -> dict
        sleep_config: Dict with sleep durations
        expected_in_prompt: String or list of strings that should appear in captured prompt
    """
    learning_client.agents.create(agent=agent_name, memory=[])
    learning_client.memory.create(
        agent=agent_name,
        label="human",
        value=f"User's name is {expected_in_prompt}. User likes Python programming."
    )
    time.sleep(sleep_config['memory_create'])

    # Make call with learning context
    with learning(agent=agent_name, client=learning_client):
        make_call("What's my name?")

    # Verify memory was injected
    captured = captured_state()
    assert captured is not None, "Failed to capture kwargs"

    captured_str = str(captured)

    # Check for either the memory content or memory markers
    expected_strings = [expected_in_prompt] if isinstance(expected_in_prompt, str) else expected_in_prompt
    expected_strings.append("<human>")  # Memory marker

    assert any(exp in captured_str for exp in expected_strings), \
        f"Memory not injected. Expected one of {expected_strings}. Captured: {captured}"


def capture_only(learning_client, agent_name, make_call, captured_state, sleep_config):
    """
    Test that capture_only mode saves conversations but doesn't inject memory.

    Args:
        learning_client: AgenticLearning client fixture
        agent_name: Unique agent name (from cleanup_agent fixture)
        make_call: Function that makes LLM API call - signature: (prompt) -> response
        captured_state: Function that returns captured kwargs/state - signature: () -> dict
        sleep_config: Dict with sleep durations
    """
    secret_info = "Secret information that should not be injected"

    learning_client.agents.create(agent=agent_name, memory=[])
    learning_client.memory.create(
        agent=agent_name,
        label="human",
        value=secret_info
    )
    time.sleep(sleep_config['memory_create'])

    # Make call with capture_only=True
    with learning(agent=agent_name, client=learning_client, capture_only=True):
        make_call("Hello, how are you?")

    # Verify memory was NOT injected
    captured = captured_state()
    captured_str = str(captured)
    assert "Secret information" not in captured_str, \
        "Memory was injected despite capture_only=True"

    # Verify conversation was still saved
    time.sleep(sleep_config['short_wait'])
    messages = learning_client.messages.list(agent_name)
    assert len(messages) > 0, "Conversation not saved in capture_only mode"


def interceptor_cleanup(learning_client, agent_name, make_call, sleep_config):
    """
    Test that interceptor only captures within learning context (not after).

    Args:
        learning_client: AgenticLearning client fixture
        agent_name: Unique agent name (from cleanup_agent fixture)
        make_call: Function that makes LLM API call - signature: (prompt) -> response
        sleep_config: Dict with sleep durations
    """
    # Make call inside learning context
    with learning(agent=agent_name, client=learning_client):
        make_call("Test message")

    # Make call OUTSIDE learning context
    make_call("Uncaptured message")

    time.sleep(sleep_config['short_wait'])

    # Verify only the first message was captured
    messages = learning_client.messages.list(agent_name)
    assert len(messages) > 0, "Learning context didn't capture"

    message_contents = [
        msg.content if hasattr(msg, 'content') else ''
        for msg in messages
    ]
    assert not any("Uncaptured message" in c for c in message_contents), \
        "Captured outside learning context"


# Async versions for Claude Agent SDK and other async providers

async def conversation_saved_async(learning_client, agent_name, make_call, sleep_config, expected_content):
    """
    Async version: Test that conversations are captured and saved to Letta.

    Args:
        learning_client: AgenticLearning client fixture
        agent_name: Unique agent name (from cleanup_agent fixture)
        make_call: Async function that makes LLM API call - signature: async (prompt) -> response
        sleep_config: Dict with sleep durations (e.g., {'long_wait': 5.0})
        expected_content: String that should appear in saved messages
    """
    agent = learning_client.agents.create(agent=agent_name)
    assert agent is not None

    # Make call within learning context
    with learning(agent=agent_name, client=learning_client):
        await make_call(f"My name is {expected_content}")

    # Wait for async processing
    await asyncio.sleep(sleep_config['long_wait'])

    # Verify messages were saved
    messages = learning_client.messages.list(agent_name)
    assert len(messages) > 0, "No messages saved"

    # Check expected content appears in messages
    message_contents = []
    for msg in messages:
        if hasattr(msg, 'content') and isinstance(msg.content, str):
            message_contents.append(msg.content)
        elif hasattr(msg, 'reasoning') and isinstance(msg.reasoning, str):
            message_contents.append(msg.reasoning)

    assert any(expected_content in c for c in message_contents), \
        f"'{expected_content}' not found in messages: {message_contents[:3]}"


async def memory_injection_async(learning_client, agent_name, make_call, captured_state,
                                  sleep_config, expected_in_prompt):
    """
    Async version: Test that memory is injected into LLM calls.

    Args:
        learning_client: AgenticLearning client fixture
        agent_name: Unique agent name (from cleanup_agent fixture)
        make_call: Async function that makes LLM API call - signature: async (prompt) -> response
        captured_state: Function that returns captured kwargs/state - signature: () -> dict
        sleep_config: Dict with sleep durations
        expected_in_prompt: String or list of strings that should appear in captured prompt
    """
    learning_client.agents.create(agent=agent_name, memory=[])
    learning_client.memory.create(
        agent=agent_name,
        label="human",
        value=f"User's name is {expected_in_prompt}. User likes Python programming."
    )
    await asyncio.sleep(sleep_config['memory_create'])

    # Make call with learning context
    with learning(agent=agent_name, client=learning_client):
        await make_call("What's my name?")

    # Verify memory was injected
    captured = captured_state()
    assert captured is not None, "Failed to capture kwargs"

    captured_str = str(captured)

    # Check for either the memory content or memory markers
    expected_strings = [expected_in_prompt] if isinstance(expected_in_prompt, str) else expected_in_prompt
    expected_strings.append("<human>")  # Memory marker

    assert any(exp in captured_str for exp in expected_strings), \
        f"Memory not injected. Expected one of {expected_strings}. Captured: {captured}"


async def capture_only_async(learning_client, agent_name, make_call, captured_state, sleep_config):
    """
    Async version: Test that capture_only mode saves conversations but doesn't inject memory.

    Args:
        learning_client: AgenticLearning client fixture
        agent_name: Unique agent name (from cleanup_agent fixture)
        make_call: Async function that makes LLM API call - signature: async (prompt) -> response
        captured_state: Function that returns captured kwargs/state - signature: () -> dict
        sleep_config: Dict with sleep durations
    """
    secret_info = "Secret information that should not be injected"

    learning_client.agents.create(agent=agent_name, memory=[])
    learning_client.memory.create(
        agent=agent_name,
        label="human",
        value=secret_info
    )
    await asyncio.sleep(sleep_config['memory_create'])

    # Make call with capture_only=True
    with learning(agent=agent_name, client=learning_client, capture_only=True):
        await make_call("Hello, how are you?")

    # Verify memory was NOT injected
    captured = captured_state()
    captured_str = str(captured)
    assert "Secret information" not in captured_str, \
        "Memory was injected despite capture_only=True"

    # Verify conversation was still saved
    await asyncio.sleep(sleep_config['short_wait'])
    messages = learning_client.messages.list(agent_name)
    assert len(messages) > 0, "Conversation not saved in capture_only mode"


async def interceptor_cleanup_async(learning_client, agent_name, make_call, sleep_config):
    """
    Async version: Test that interceptor only captures within learning context (not after).

    Args:
        learning_client: AgenticLearning client fixture
        agent_name: Unique agent name (from cleanup_agent fixture)
        make_call: Async function that makes LLM API call - signature: async (prompt) -> response
        sleep_config: Dict with sleep durations
    """
    # Make call inside learning context
    with learning(agent=agent_name, client=learning_client):
        await make_call("Test message")

    # Make call OUTSIDE learning context
    await make_call("Uncaptured message")

    await asyncio.sleep(sleep_config['short_wait'])

    # Verify only the first message was captured
    messages = learning_client.messages.list(agent_name)
    assert len(messages) > 0, "Learning context didn't capture"

    message_contents = [
        msg.content if hasattr(msg, 'content') else ''
        for msg in messages
    ]
    assert not any("Uncaptured message" in c for c in message_contents), \
        "Captured outside learning context"
