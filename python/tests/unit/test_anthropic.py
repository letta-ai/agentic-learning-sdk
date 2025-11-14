"""
Unit tests for Anthropic Messages API interceptor.

These tests use real Anthropic SDK with mocked create method (no real HTTP calls).
"""

import pytest
from unittest.mock import Mock
from anthropic import Anthropic
from anthropic.resources.messages import Messages

from agentic_learning.core import learning
from tests.shared import test_runners


_captured_kwargs = {}


@pytest.mark.unit
@pytest.mark.anthropic
class TestAnthropicUnit:
    """Anthropic Messages API unit tests with mocked SDK."""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock Anthropic response."""
        response = Mock()
        response.content = [Mock(text="Mock response", type="text")]
        response.model = "claude-3-5-sonnet-20241022"
        return response

    @pytest.fixture
    def anthropic_client(self, mock_llm_response):
        """Anthropic client with mocked create method."""
        original_create = Messages.create

        def mock_create(self_arg, **kwargs):
            _captured_kwargs.clear()
            _captured_kwargs.update(kwargs)
            return mock_llm_response

        Messages.create = mock_create

        yield Anthropic(api_key="fake-key")

        # Restore original
        Messages.create = original_create

    @pytest.fixture
    def make_llm_call(self, anthropic_client):
        """Function to make Anthropic messages calls."""
        def _make_call(prompt: str):
            response = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return response
        return _make_call

    @pytest.fixture
    def get_captured_kwargs(self):
        """Get kwargs sent to LLM."""
        return lambda: _captured_kwargs.copy()

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
        self, learning_client, cleanup_agent, make_llm_call, get_captured_kwargs, sleep_config
    ):
        """Test memory context is injected into LLM calls."""
        test_runners.memory_injection(
            learning_client=learning_client,
            agent_name=cleanup_agent,
            make_call=make_llm_call,
            captured_state=get_captured_kwargs,
            sleep_config=sleep_config,
            expected_in_prompt="Bob",
        )

    def test_capture_only(
        self, learning_client, cleanup_agent, make_llm_call, get_captured_kwargs, sleep_config
    ):
        """Test capture-only mode doesn't inject memory."""
        test_runners.capture_only(
            learning_client=learning_client,
            agent_name=cleanup_agent,
            make_call=make_llm_call,
            captured_state=get_captured_kwargs,
            sleep_config=sleep_config,
        )

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
