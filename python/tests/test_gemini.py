"""Google Gemini SDK tests."""

import pytest
from unittest.mock import Mock
import google.generativeai as genai
from .base_interceptor_tests import BaseInterceptorTests


_captured_kwargs = {}


@pytest.fixture
def mock_llm_response():
    """Mock Gemini response."""
    response = Mock()
    response.text = "Mock response"
    mock_candidate = Mock()
    mock_candidate.content = Mock()
    mock_candidate.content.parts = [Mock(text="Mock response")]
    response.candidates = [mock_candidate]
    return response


@pytest.fixture
def mock_llm_client(mock_llm_response):
    """Gemini client with mocked API."""
    genai.configure(api_key="fake-key")

    original_generate = genai.GenerativeModel.generate_content

    def mock_generate(self_arg, *args, **kwargs):
        _captured_kwargs.clear()
        _captured_kwargs.update(kwargs)
        # First positional arg is the prompt
        if args:
            _captured_kwargs['contents'] = args[0]
        return mock_llm_response

    genai.GenerativeModel.generate_content = mock_generate

    # Create model and ensure it has a proper model_name attribute
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    # Ensure model_name is a string for tests
    if hasattr(model, 'model_name') and not isinstance(model.model_name, str):
        model.model_name = 'models/gemini-2.5-flash'

    yield model

    genai.GenerativeModel.generate_content = original_generate


@pytest.fixture
def make_llm_call():
    """Make Gemini call."""
    return lambda client, prompt: client.generate_content(prompt)


@pytest.fixture
def make_llm_call_with_system():
    """Make Gemini call with system context."""
    return lambda client, system_message, user_message: client.generate_content(
        f"{system_message}\n\n{user_message}"
    )


@pytest.fixture
def get_captured_kwargs():
    """Get kwargs sent to LLM."""
    return lambda: _captured_kwargs.copy()


@pytest.fixture
def expected_model_name():
    """Expected model name after extraction (should have 'models/' prefix stripped)."""
    return "gemini-2.5-flash"


class TestGeminiInterceptor(BaseInterceptorTests):
    """Google Gemini SDK tests - inherits all tests from base."""
    pass
