"""
Unit tests for Google Gemini interceptor.

These tests use real Gemini SDK with mocked generate_content method (no real HTTP calls).
"""

import pytest
from unittest.mock import Mock
import google.generativeai as genai

from agentic_learning.core import learning
from tests.shared import test_runners


_captured_state = {}


@pytest.mark.unit
@pytest.mark.gemini
class TestGeminiUnit:
    """Google Gemini unit tests with mocked SDK."""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock Gemini response."""
        response = Mock()
        response.text = "Mock response"
        return response

    @pytest.fixture
    def gemini_client(self, mock_llm_response):
        """Gemini client with mocked generate_content method."""
        original_generate = genai.GenerativeModel.generate_content

        def mock_generate(self_arg, *args, **kwargs):
            _captured_state.clear()
            # Gemini can receive contents as either positional arg or kwarg
            if args:
                _captured_state['contents'] = args[0]
            if kwargs:
                _captured_state.update(kwargs)
            return mock_llm_response

        genai.GenerativeModel.generate_content = mock_generate

        yield genai.GenerativeModel("gemini-1.5-flash")

        # Restore original
        genai.GenerativeModel.generate_content = original_generate

    @pytest.fixture
    def make_llm_call(self, gemini_client):
        """Function to make Gemini generate_content calls."""
        def _make_call(prompt: str):
            response = gemini_client.generate_content(prompt)
            return response
        return _make_call

    @pytest.fixture
    def get_captured_kwargs(self):
        """Get args/kwargs sent to LLM."""
        return lambda: _captured_state.copy()

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
