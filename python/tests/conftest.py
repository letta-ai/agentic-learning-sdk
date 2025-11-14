"""
Shared test fixtures for Agentic Learning SDK tests.
"""

import os
import uuid
import pytest
from agentic_learning import AgenticLearning


@pytest.fixture
def learning_client():
    """
    AgenticLearning client - toggles between local and cloud Letta server.

    Set LETTA_ENV environment variable:
    - "cloud" (default): Uses hosted Letta server with LETTA_API_KEY
    - "local": Uses local Letta server at http://localhost:8283
    """
    test_mode = os.getenv("LETTA_ENV", "cloud").lower()

    if test_mode == "local":
        # Use local server
        return AgenticLearning(base_url="http://localhost:8283")
    else:
        # Use cloud with API key (default)
        return AgenticLearning()


@pytest.fixture
def unique_agent_name():
    """Generate unique agent name per test to avoid conflicts."""
    return f"test-agent-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def cleanup_agent(learning_client, unique_agent_name):
    """
    Provide agent name and ensure cleanup after test.

    Usage in tests:
        def test_something(cleanup_agent, learning_client):
            agent_name = cleanup_agent
            # ... use agent_name in test
            # Agent automatically deleted after test
    """
    yield unique_agent_name

    # Teardown: Always delete test agent
    try:
        learning_client.agents.delete(agent=unique_agent_name)
    except Exception as e:
        # Agent may not exist or already deleted - that's ok
        print(f"Warning: Could not cleanup agent {unique_agent_name}: {e}")


@pytest.fixture
def sleep_config():
    """
    Configurable sleep durations for tests.

    Environment variables:
    - TEST_SLEEP_LONG: Long wait after operations (default: 7.0s)
    - TEST_SLEEP_MEMORY: Wait after memory creation (default: 3.0s)
    - TEST_SLEEP_SHORT: Short wait for verification (default: 4.0s)

    Usage in tests:
        def test_something(sleep_config):
            time.sleep(sleep_config['long_wait'])
    """
    return {
        'long_wait': float(os.getenv('TEST_SLEEP_LONG', '7.0')),
        'memory_create': float(os.getenv('TEST_SLEEP_MEMORY', '3.0')),
        'short_wait': float(os.getenv('TEST_SLEEP_SHORT', '4.0')),
    }
