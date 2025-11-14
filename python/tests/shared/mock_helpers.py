"""
Mock helpers for provider tests.

Provides utilities for mocking LLM API calls and capturing request parameters.
"""

from unittest.mock import Mock


def create_captured_kwargs_store():
    """
    Create a dictionary for capturing kwargs sent to mocked LLM APIs.

    Returns a dict that can be cleared and updated by mock functions.
    Used by test fixtures to capture API call parameters.

    Usage:
        _captured_kwargs = create_captured_kwargs_store()

        def mock_create(self_arg, **kwargs):
            _captured_kwargs.clear()
            _captured_kwargs.update(kwargs)
            return mock_response
    """
    return {}


def create_mock_text_response(text, model_name, role="assistant"):
    """
    Create a generic mock response with text content.

    Args:
        text: Response text
        model_name: Model identifier
        role: Response role (default: "assistant")

    Returns:
        Mock object with common response attributes
    """
    response = Mock()
    response.content = text
    response.model = model_name
    response.role = role
    return response


def create_openai_mock_response(text="Mock response", model="gpt-5"):
    """Create mock OpenAI chat completion response."""
    response = Mock()
    response.choices = [Mock(message=Mock(content=text, role="assistant"))]
    response.model = model
    return response


def create_anthropic_mock_response(text="Mock response", model="claude-sonnet-4-20250514"):
    """Create mock Anthropic messages response."""
    response = Mock()
    response.content = [Mock(type="text", text=text)]
    response.model = model
    response.role = "assistant"
    return response


def create_gemini_mock_response(text="Mock response"):
    """Create mock Gemini response."""
    response = Mock()
    response.text = text
    # Gemini returns model info differently
    response.model = None
    return response
