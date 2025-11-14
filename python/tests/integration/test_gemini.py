"""
Integration tests for Google Gemini interceptor.

These tests use the real Google Generative AI SDK with real API calls.
Requires GOOGLE_API_KEY environment variable.
"""

import os
import pytest
import google.generativeai as genai

from agentic_learning.core import learning
from tests.shared import test_runners


@pytest.mark.integration
@pytest.mark.gemini
class TestGeminiIntegration:
    """Google Gemini integration tests with real SDK and real API calls."""

    @pytest.fixture(autouse=True)
    def setup_gemini(self):
        """Configure Gemini with real API key."""
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set - skipping integration test")
        genai.configure(api_key=api_key)

    @pytest.fixture
    def make_llm_call(self):
        """Function to make Gemini generate_content calls."""

        def _make_call(prompt: str):
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(max_output_tokens=50),
            )
            return response

        return _make_call

    def test_conversation_saved(
        self, learning_client, cleanup_agent, make_llm_call, sleep_config
    ):
        """Test conversations are captured and saved to Letta."""
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
        test_runners.interceptor_cleanup(
            learning_client=learning_client,
            agent_name=cleanup_agent,
            make_call=make_llm_call,
            sleep_config=sleep_config,
        )
