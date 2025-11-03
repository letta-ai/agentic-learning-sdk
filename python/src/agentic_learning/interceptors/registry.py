"""
Interceptor Registry

Auto-detection and registration of SDK interceptors.
"""

from typing import List, Type

from .base import BaseInterceptor


# Registry of all available interceptor classes
_INTERCEPTOR_CLASSES: List[Type[BaseInterceptor]] = []

# Store installed interceptor instances
_INSTALLED_INTERCEPTORS: List[BaseInterceptor] = []


def register_interceptor(interceptor_class: Type[BaseInterceptor]):
    """
    Register an interceptor class.

    Args:
        interceptor_class: Interceptor class to register
    """
    if interceptor_class not in _INTERCEPTOR_CLASSES:
        _INTERCEPTOR_CLASSES.append(interceptor_class)


def install() -> List[str]:
    """
    Auto-detect and install available SDK interceptors.

    Checks each registered interceptor to see if its SDK is available,
    and installs it if so.

    Returns:
        List of installed interceptor class names
    """
    global _INSTALLED_INTERCEPTORS

    installed = []
    for interceptor_class in _INTERCEPTOR_CLASSES:
        if interceptor_class.is_available():
            try:
                interceptor = interceptor_class()
                interceptor.install()
                _INSTALLED_INTERCEPTORS.append(interceptor)
                installed.append(interceptor_class.__name__)
            except Exception:
                # Silently skip interceptors that fail to install
                pass

    return installed


def uninstall_all():
    """Uninstall all installed interceptors."""
    global _INSTALLED_INTERCEPTORS

    for interceptor in _INSTALLED_INTERCEPTORS:
        try:
            interceptor.uninstall()
        except Exception:
            # Silently skip interceptors that fail to uninstall
            pass

    _INSTALLED_INTERCEPTORS = []
