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

    Set LETTA_TEST_MODE environment variable:
    - "local" (default): Uses local Letta server at http://localhost:8283
    - "cloud": Uses hosted Letta server with LETTA_API_KEY
    """
    test_mode = os.getenv("LETTA_TEST_MODE", "local").lower()

    if test_mode == "cloud":
        # Use cloud with API key
        return AgenticLearning()
    else:
        # Use local server (default)
        return AgenticLearning(base_url="http://localhost:8283")


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
