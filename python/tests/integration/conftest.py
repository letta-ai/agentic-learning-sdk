"""
Integration test fixtures.

Integration tests use real SDK clients with mocked HTTP/subprocess responses.
These fixtures ensure interceptors are properly reset between tests.
"""

import pytest


@pytest.fixture(autouse=True)
def reset_interceptors():
    """
    Reset interceptor installation state before each integration test.

    This is critical for test isolation. Since interceptors are installed
    globally once per process, we need to reset the flag before each test
    to ensure interceptors are reinstalled properly.

    Integration tests use real SDKs (not mocks), but the interceptor installation
    state still needs to be managed between tests.
    """
    import agentic_learning.core as core

    original_installed = core._INTERCEPTORS_INSTALLED
    core._INTERCEPTORS_INSTALLED = False  # Force reinstall
    yield
    core._INTERCEPTORS_INSTALLED = original_installed
