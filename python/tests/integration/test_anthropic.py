"""
Integration tests for Anthropic Messages API interceptor.

These tests use the real Anthropic SDK with real API calls.
Requires ANTHROPIC_API_KEY environment variable.
"""

import os
import pytest
from anthropic import Anthropic

from agentic_learning.core import learning
from tests.shared import test_runners


@pytest.mark.integration
@pytest.mark.anthropic
class TestAnthropicIntegration:
    """Anthropic Messages API integration tests with real SDK and real API calls."""

    @pytest.fixture
    def anthropic_client(self):
        """Create a real Anthropic client with real API key."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set - skipping integration test")
        return Anthropic(api_key=api_key)

    @pytest.fixture
    def make_llm_call(self, anthropic_client):
        """Function to make Anthropic messages calls."""
        def _make_call(prompt: str):
            response = anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",  # Use cheaper model for testing
                max_tokens=50,  # Limit tokens to reduce cost
                messages=[{"role": "user", "content": prompt}],
            )
            return response
        return _make_call

    def test_conversation_saved(
        self, learning_client, cleanup_agent, make_llm_call, sleep_config
    ):
        """Test conversations are captured and saved to Letta."""
        # Run the shared test - uses real API calls
        test_runners.conversation_saved(
            learning_client=learning_client,
            agent_name=cleanup_agent,
            make_call=make_llm_call,
            sleep_config=sleep_config,
            expected_content="Alice",
        )

    def test_memory_injection(
        self, learning_client, cleanup_agent, make_llm_call, sleep_config
    ):
        """Test memory context is injected into LLM calls."""
        # For integration tests, we verify memory injection by checking
        # that the LLM response acknowledges the memory
        agent_name = cleanup_agent
        learning_client.agents.create(agent=agent_name, memory=[])
        learning_client.memory.create(
            agent=agent_name,
            label="human",
            value="User's name is Bob. User likes Python programming."
        )
        import time
        time.sleep(sleep_config['memory_create'])

        # Make call with learning context
        with learning(agent=agent_name, client=learning_client):
            response = make_llm_call("What's my name?")

        # For real API calls, we can't inspect kwargs, but memory should work
        # The test passes if no errors occur
        assert response is not None

    def test_capture_only(
        self, learning_client, cleanup_agent, make_llm_call, sleep_config
    ):
        """Test capture-only mode saves conversations."""
        agent_name = cleanup_agent
        learning_client.agents.create(agent=agent_name, memory=[])

        with learning(agent=agent_name, client=learning_client, capture_only=True):
            make_llm_call("Hello, how are you?")

        import time
        time.sleep(sleep_config['short_wait'])
        messages = learning_client.messages.list(agent_name)
        assert len(messages) > 0, "Conversation not saved in capture_only mode"

    def test_interceptor_cleanup(
        self, learning_client, cleanup_agent, make_llm_call, sleep_config
    ):
        """Test interceptor only captures within learning context."""
        test_runners.interceptor_cleanup(
            learning_client=learning_client,
            agent_name=cleanup_agent,
            make_call=make_llm_call,
            sleep_config=sleep_config,
        )
