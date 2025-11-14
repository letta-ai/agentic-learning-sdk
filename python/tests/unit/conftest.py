"""
Unit test fixtures and configuration.

This conftest ensures proper test isolation by resetting interceptor state
between tests. Unit tests use MagicMock to avoid HTTP calls entirely.
"""

import pytest


@pytest.fixture(autouse=True)
def reset_interceptors():
    """
    Reset interceptor installation state before each test.

    This ensures interceptors are properly reinstalled even after mock fixtures
    have modified the patched methods. Without this, tests run in sequence
    would fail because:
    1. Test 1 installs interceptor (once)
    2. Test 1 mock fixture restores method (removes interceptor)
    3. Test 2 tries to use interceptor, but it's not reinstalled
    """
    import agentic_learning.core as core

    # Save original state
    original_installed = core._INTERCEPTORS_INSTALLED

    # Reset before test
    core._INTERCEPTORS_INSTALLED = False

    yield

    # Restore state after test (not strictly necessary but good practice)
    core._INTERCEPTORS_INSTALLED = original_installed
