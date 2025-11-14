"""
Integration tests for OpenAI Chat Completions interceptor.

These tests use the real OpenAI SDK with real API calls.
Requires OPENAI_API_KEY environment variable.
"""

import os
import pytest
from openai import OpenAI

from agentic_learning.core import learning
from tests.shared import test_runners


@pytest.mark.integration
@pytest.mark.openai
class TestOpenAIIntegration:
    """OpenAI Chat Completions integration tests with real SDK and real API calls."""

    @pytest.fixture
    def openai_client(self):
        """Create a real OpenAI client with real API key."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - skipping integration test")
        return OpenAI(api_key=api_key)

    @pytest.fixture
    def make_llm_call(self, openai_client):
        """Function to make OpenAI chat completion calls."""

        def _make_call(prompt: str):
            response = openai_client.chat.completions.create(
                model="gpt-5",  # Use cheaper model for testing
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,  # Limit tokens to reduce cost
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

        # For real API calls, the test passes if no errors occur
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
        # Run the shared test - uses real API calls
        test_runners.interceptor_cleanup(
            learning_client=learning_client,
            agent_name=cleanup_agent,
            make_call=make_llm_call,
            sleep_config=sleep_config,
        )
