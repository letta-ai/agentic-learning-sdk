"""Anthropic SDK tests."""

import pytest
from unittest.mock import Mock
from anthropic import Anthropic
from anthropic.resources.messages import Messages
from .base_interceptor_tests import BaseInterceptorTests


_captured_kwargs = {}


@pytest.fixture
def mock_llm_response():
    """Mock Anthropic response."""
    response = Mock()
    response.content = [Mock(type="text", text="Mock response")]
    response.model = "claude-sonnet-4-20250514"
    response.role = "assistant"
    return response


@pytest.fixture
def mock_llm_client(mock_llm_response):
    """Anthropic client with mocked API."""
    original_create = Messages.create

    def mock_create(self_arg, **kwargs):
        _captured_kwargs.clear()
        _captured_kwargs.update(kwargs)
        return mock_llm_response

    Messages.create = mock_create

    yield Anthropic(api_key="fake-key")

    Messages.create = original_create


@pytest.fixture
def make_llm_call():
    """Make Anthropic call."""
    return lambda client, prompt: client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )


@pytest.fixture
def make_llm_call_with_system():
    """Make Anthropic call with system message."""
    return lambda client, system_message, user_message: client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_message,
        messages=[{"role": "user", "content": user_message}]
    )


@pytest.fixture
def get_captured_kwargs():
    """Get kwargs sent to LLM."""
    return lambda: _captured_kwargs.copy()


@pytest.fixture
def expected_model_name():
    """Expected model name after extraction."""
    return "claude-sonnet-4-20250514"


class TestAnthropicInterceptor(BaseInterceptorTests):
    """Anthropic SDK tests - inherits all tests from base."""
    pass
