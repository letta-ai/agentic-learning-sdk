"""OpenAI Responses API tests."""

import pytest
from unittest.mock import Mock
from openai import OpenAI
from .base_interceptor_tests import BaseInterceptorTests


_captured_kwargs = {}


@pytest.fixture
def mock_llm_response():
    """Mock OpenAI Responses API response."""
    response = Mock()
    response.output = "Mock response"
    response.model = "gpt-4o"
    return response


@pytest.fixture
def mock_llm_client(mock_llm_response):
    """OpenAI client with mocked Responses API."""
    try:
        from openai.resources.responses import Responses
    except (ImportError, AttributeError):
        pytest.skip("Responses API not available in this OpenAI SDK version")

    original_create = Responses.create

    def mock_create(self_arg, **kwargs):
        _captured_kwargs.clear()
        _captured_kwargs.update(kwargs)
        return mock_llm_response

    Responses.create = mock_create

    yield OpenAI(api_key="fake-key")

    Responses.create = original_create


@pytest.fixture
def make_llm_call():
    """Make OpenAI Responses API call."""
    return lambda client, prompt: client.responses.create(
        model="gpt-4o",
        input=prompt
    )


@pytest.fixture
def make_llm_call_with_system():
    """Make Responses API call with system context."""
    return lambda client, system_message, user_message: client.responses.create(
        model="gpt-4o",
        input=f"{system_message}\n\n{user_message}"
    )


@pytest.fixture
def get_captured_kwargs():
    """Get kwargs sent to LLM."""
    return lambda: _captured_kwargs.copy()


@pytest.fixture
def expected_model_name():
    """Expected model name after extraction."""
    return "gpt-4o"


class TestOpenAIResponsesInterceptor(BaseInterceptorTests):
    """OpenAI Responses API tests - inherits all tests from base."""
    pass
