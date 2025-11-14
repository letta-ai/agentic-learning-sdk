"""
Unit tests for OpenAI Responses API interceptor.

These tests use real OpenAI SDK with mocked create method (no real HTTP calls).
"""

import pytest
from unittest.mock import Mock
from openai import OpenAI
from openai.resources.responses import Responses

from agentic_learning.core import learning
from tests.shared import test_runners


_captured_kwargs = {}


@pytest.mark.unit
@pytest.mark.openai_responses
class TestOpenAIResponsesUnit:
    """OpenAI Responses API unit tests with mocked SDK."""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock OpenAI Responses response."""
        response = Mock()
        response.output = "Mock response"
        response.model = "gpt-5"
        return response

    @pytest.fixture
    def openai_client(self, mock_llm_response):
        """OpenAI client with mocked create method."""
        original_create = Responses.create

        def mock_create(self_arg, **kwargs):
            _captured_kwargs.clear()
            _captured_kwargs.update(kwargs)
            return mock_llm_response

        Responses.create = mock_create

        yield OpenAI(api_key="fake-key")

        # Restore original
        Responses.create = original_create

    @pytest.fixture
    def make_llm_call(self, openai_client):
        """Function to make OpenAI responses calls."""
        def _make_call(prompt: str):
            response = openai_client.responses.create(
                model="gpt-5",
                input=prompt,
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
