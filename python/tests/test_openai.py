"""OpenAI Chat Completions tests."""

import pytest
from unittest.mock import Mock
from openai import OpenAI
from openai.resources.chat.completions import Completions
from .base_interceptor_tests import BaseInterceptorTests


_captured_kwargs = {}


@pytest.fixture
def mock_llm_response():
    """Mock OpenAI response."""
    response = Mock()
    response.choices = [Mock(message=Mock(content="Mock response", role="assistant"))]
    response.model = "gpt-4o"
    return response


@pytest.fixture
def mock_llm_client(mock_llm_response):
    """OpenAI client with mocked API."""
    original_create = Completions.create

    def mock_create(self_arg, **kwargs):
        _captured_kwargs.clear()
        _captured_kwargs.update(kwargs)
        return mock_llm_response

    Completions.create = mock_create

    yield OpenAI(api_key="fake-key")

    Completions.create = original_create


@pytest.fixture
def make_llm_call():
    """Make OpenAI call."""
    return lambda client, prompt: client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )


@pytest.fixture
def make_llm_call_with_system():
    """Make OpenAI call with system message."""
    return lambda client, system_message, user_message: client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )


@pytest.fixture
def get_captured_kwargs():
    """Get kwargs sent to LLM."""
    return lambda: _captured_kwargs.copy()


@pytest.fixture
def expected_model_name():
    """Expected model name after extraction."""
    return "gpt-4o"


class TestOpenAIInterceptor(BaseInterceptorTests):
    """OpenAI Chat Completions tests - inherits all tests from base."""
    pass
