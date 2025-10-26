"""
Base Interceptor

Abstract base class for SDK interceptors.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Generator, Literal, Optional
import functools

# Provider type - expand as new providers are added
Provider = Literal["gemini", "claude", "anthropic", "openai"]


class BaseInterceptor(ABC):
    """
    Abstract base interceptor for SDK integration.

    Each SDK-specific interceptor should implement these methods to:
    1. Install/uninstall monkey patches
    2. Extract messages from SDK-specific formats
    3. Inject memory context into prompts
    4. Intercept and wrap SDK completion calls
    """

    # Each subclass must define its provider name
    PROVIDER: str

    def __init__(self):
        """Initialize interceptor with storage for original methods."""
        self._original_methods = {}  # Store originals for uninstall

    # =========================================================================
    # Installation
    # =========================================================================

    @abstractmethod
    def install(self):
        """
        Install the interceptor by monkey patching SDK methods.

        Should store original methods in self._original_methods for later restoration.
        """
        pass

    @abstractmethod
    def uninstall(self):
        """
        Uninstall the interceptor and restore original SDK methods.

        Should restore all methods from self._original_methods.
        """
        pass

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """
        Check if this SDK is installed in the current environment.

        Returns:
            True if SDK is available, False otherwise
        """
        pass

    # =========================================================================
    # Message Extraction (Optional - for API-level interceptors)
    # =========================================================================

    def extract_user_messages(self, *args, **kwargs) -> str:
        """
        Extract user message content from SDK call arguments.

        Override this for API-level interceptors that patch SDK methods.
        Transport-level interceptors can use the default implementation.

        Args:
            *args: Positional arguments from SDK call
            **kwargs: Keyword arguments from SDK call

        Returns:
            Combined user message content as string
        """
        return ""

    def extract_assistant_message(self, response: Any) -> str:
        """
        Extract assistant message from non-streaming response.

        Override this for API-level interceptors that patch SDK methods.
        Transport-level interceptors can use the default implementation.

        Args:
            response: SDK response object

        Returns:
            Assistant message content as string
        """
        return ""

    def extract_assistant_message_streaming(self, stream: Generator) -> Generator:
        """
        Wrap streaming response to collect chunks while yielding them.

        Override this for API-level interceptors that need to wrap streaming responses.
        Transport-level interceptors can use the default implementation.

        This should return a generator that:
        1. Yields each chunk to the user (pass-through)
        2. Collects chunks internally
        3. After stream completes, saves conversation turn

        Args:
            stream: Original streaming response generator

        Returns:
            Wrapped generator that collects and yields chunks
        """
        return stream

    async def extract_assistant_message_streaming_async(
        self, stream: AsyncGenerator
    ) -> AsyncGenerator:
        """
        Wrap async streaming response to collect chunks while yielding them.

        Override this for API-level interceptors that need to wrap streaming responses.
        Transport-level interceptors can use the default implementation.

        This should return an async generator that:
        1. Yields each chunk to the user (pass-through)
        2. Collects chunks internally
        3. After stream completes, saves conversation turn

        Args:
            stream: Original async streaming response generator

        Returns:
            Wrapped async generator that collects and yields chunks
        """
        return stream

    # =========================================================================
    # Message Building
    # =========================================================================

    @abstractmethod
    def build_request_messages(self, user_message: str) -> list:
        """
        Build request messages array for Letta from user message.

        Args:
            user_message: User message content extracted from SDK call

        Returns:
            List of message dicts in Letta format (e.g., [{"role": "user", "content": "..."}])
        """
        pass

    @abstractmethod
    def build_response_dict(self, response: Any) -> dict:
        """
        Build response dict for Letta from SDK response.

        Args:
            response: SDK response object

        Returns:
            Message dict in Letta format (e.g., {"role": "assistant", "content": "..."})
        """
        pass

    # =========================================================================
    # Memory Injection (Optional - for API-level interceptors)
    # =========================================================================

    def inject_memory_context(self, messages: Any, context: str) -> Any:
        """
        Inject memory context into messages in SDK-specific format.

        Override this for API-level interceptors that need to inject memory
        into SDK method arguments. Transport-level interceptors can use the
        default implementation.

        Args:
            messages: SDK-specific messages format
            context: Memory context string to inject

        Returns:
            Modified messages with memory context injected
        """
        return messages

    # =========================================================================
    # Core Interception Logic (Optional - for API-level interceptors)
    # =========================================================================

    def intercept(self, original_method):
        """
        Return wrapped version of SDK method (sync).

        Override this for API-level interceptors that patch SDK methods.
        Transport-level interceptors can use the default implementation.

        The wrapper should:
        1. Check if learning context is active
        2. Get memory context if not capture_only
        3. Inject context into messages
        4. Extract user message
        5. Call original method
        6. Handle response (streaming or not)
        7. Extract assistant message
        8. Save conversation turn to Letta

        Args:
            original_method: Original SDK method to wrap

        Returns:
            Wrapped method that includes learning integration
        """
        return original_method

    def intercept_async(self, original_method):
        """
        Return wrapped version of SDK method (async).

        Override this for API-level interceptors that patch SDK methods.
        Transport-level interceptors can use the default implementation.

        The wrapper should:
        1. Check if learning context is active
        2. Get memory context if not capture_only
        3. Inject context into messages
        4. Extract user message
        5. Call original method (with await)
        6. Handle response (streaming or not)
        7. Extract assistant message
        8. Save conversation turn to Letta

        Args:
            original_method: Original async SDK method to wrap

        Returns:
            Wrapped async method that includes learning integration
        """
        return original_method


# =============================================================================
# Base API Interceptor (for HTTP request-level interceptors)
# =============================================================================


class BaseAPIInterceptor(BaseInterceptor):
    """
    Base class for API-level interceptors that patch HTTP request methods.

    This class provides common intercept logic for SDKs that use HTTP APIs
    (OpenAI, Anthropic, Gemini, etc). Subclasses only need to implement
    SDK-specific message extraction and formatting methods.

    Transport-level interceptors (like Claude Agent SDK) should extend
    BaseInterceptor directly instead.
    """

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _retrieve_and_inject_memory(self, config: Dict, kwargs: Dict) -> Dict:
        """
        Retrieve memory context and inject into kwargs if enabled.

        Args:
            config: Current learning context configuration
            kwargs: SDK method kwargs to inject memory into

        Returns:
            Modified kwargs with memory injected (or unchanged if disabled)
        """
        if config.get('capture_only', False):
            return kwargs

        client = config.get('client')
        agent_name = config.get('agent_name')

        if not client or not agent_name:
            return kwargs

        try:
            memory_context = client.memory.context.retrieve(agent=agent_name)
            if memory_context:
                kwargs = self.inject_memory_context(kwargs, memory_context)
        except Exception as e:
            # Log error but don't crash
            import sys
            print(f"[Warning] Memory injection failed: {e}", file=sys.stderr)

        return kwargs

    async def _retrieve_and_inject_memory_async(self, config: Dict, kwargs: Dict) -> Dict:
        """
        Retrieve memory context and inject into kwargs if enabled (async version).

        Args:
            config: Current learning context configuration
            kwargs: SDK method kwargs to inject memory into

        Returns:
            Modified kwargs with memory injected (or unchanged if disabled)
        """
        if config.get('capture_only', False):
            return kwargs

        client = config.get('client')
        agent_name = config.get('agent_name')

        if not client or not agent_name:
            return kwargs

        try:
            memory_context = await client.memory.context.retrieve(agent=agent_name)
            if memory_context:
                kwargs = self.inject_memory_context(kwargs, memory_context)
        except Exception as e:
            # Log error but don't crash
            import sys
            print(f"[Warning] Memory injection failed: {e}", file=sys.stderr)

        return kwargs

    def _save_streaming_turn_base(self, chunks: list, user_message: str, model_name: str):
        """
        Common streaming save logic for sync methods.

        Args:
            chunks: List of streaming chunks collected
            user_message: User message content
            model_name: Model identifier
        """
        if not user_message:
            return

        response = self._build_response_from_chunks(chunks)

        from ..core import _save_conversation_turn
        try:
            _save_conversation_turn(
                provider=self.PROVIDER,
                model=model_name,
                request_messages=self.build_request_messages(user_message),
                response_dict=self.build_response_dict(response=response)
            )
        except Exception as e:
            import sys
            print(f"[Warning] Failed to save streaming conversation: {e}", file=sys.stderr)

    async def _save_streaming_turn_base_async(self, chunks: list, user_message: str, model_name: str):
        """
        Common streaming save logic for async methods.

        Args:
            chunks: List of streaming chunks collected
            user_message: User message content
            model_name: Model identifier
        """
        if not user_message:
            return

        response = self._build_response_from_chunks(chunks)

        from ..core import _save_conversation_turn_async
        try:
            await _save_conversation_turn_async(
                provider=self.PROVIDER,
                model=model_name,
                request_messages=self.build_request_messages(user_message),
                response_dict=self.build_response_dict(response=response)
            )
        except Exception as e:
            import sys
            print(f"[Warning] Failed to save streaming conversation: {e}", file=sys.stderr)

    @abstractmethod
    def _build_response_from_chunks(self, chunks: list) -> Any:
        """
        Build a complete response object from streaming chunks.

        Subclasses must implement this to reconstruct a response object
        from accumulated streaming chunks in their SDK-specific format.

        Args:
            chunks: List of streaming chunks collected

        Returns:
            Complete response object that can be passed to build_response_dict()
        """
        pass

    @abstractmethod
    def extract_model_name(self, response: Any = None, model_self: Any = None) -> str:
        """
        Extract model name from SDK response or model instance.

        Args:
            response: SDK response object (used by OpenAI, Anthropic, etc.)
            model_self: Model/client instance (used by Gemini, etc.)

        Returns:
            Model name/identifier
        """
        pass

    # =========================================================================
    # Common Intercept Logic
    # =========================================================================

    def intercept(self, original_method):
        """
        Wrap SDK method for sync calls.

        Implements common interception logic:
        1. Check if learning context is active
        2. Extract user message from args
        3. Inject memory context if enabled
        4. Call original method
        5. Handle streaming vs non-streaming responses
        6. Save conversation to Letta
        """
        interceptor = self

        @functools.wraps(original_method)
        def wrapper(self_arg, *args, **kwargs):
            from ..core import get_current_config

            config = get_current_config()
            if not config:
                # No learning context active - pass through
                return original_method(self_arg, *args, **kwargs)

            # Extract user message
            user_message = interceptor.extract_user_messages(*args, **kwargs)

            # Inject memory context if enabled
            kwargs = interceptor._retrieve_and_inject_memory(config, kwargs)

            # Check if streaming
            is_streaming = kwargs.get('stream', False)

            # Call original method
            response = original_method(self_arg, *args, **kwargs)

            # Handle response
            if is_streaming:
                # Attach metadata for streaming wrapper
                response._learning_user_message = user_message
                response._learning_model_name = kwargs.get('model', interceptor.extract_model_name(response=response, model_self=self_arg) if hasattr(response, 'model') or hasattr(self_arg, 'model_name') or hasattr(self_arg, '_model_name') else 'unknown')
                return interceptor.extract_assistant_message_streaming(response)
            else:
                # Non-streaming - extract and save immediately
                model_name = interceptor.extract_model_name(response=response, model_self=self_arg)

                from ..core import _save_conversation_turn
                try:
                    _save_conversation_turn(
                        provider=interceptor.PROVIDER,
                        model=model_name,
                        request_messages=interceptor.build_request_messages(user_message),
                        response_dict=interceptor.build_response_dict(response=response)
                    )
                except Exception as e:
                    import sys
                    print(f"[Warning] Failed to save conversation: {e}", file=sys.stderr)

                return response

        return wrapper

    def intercept_async(self, original_method):
        """
        Wrap SDK method for async calls.

        Implements common interception logic for async methods:
        1. Check if learning context is active
        2. Extract user message from args
        3. Inject memory context if enabled
        4. Call original method with await
        5. Handle streaming vs non-streaming responses
        6. Save conversation to Letta
        """
        interceptor = self

        @functools.wraps(original_method)
        async def wrapper(self_arg, *args, **kwargs):
            from ..core import get_current_config

            config = get_current_config()
            if not config:
                # No learning context active - pass through
                return await original_method(self_arg, *args, **kwargs)

            # Extract user message
            user_message = interceptor.extract_user_messages(*args, **kwargs)

            # Inject memory context if enabled (async)
            kwargs = await interceptor._retrieve_and_inject_memory_async(config, kwargs)

            # Check if streaming
            is_streaming = kwargs.get('stream', False)

            # Call original method
            response = await original_method(self_arg, *args, **kwargs)

            # Handle response
            if is_streaming:
                # Attach metadata for streaming wrapper
                response._learning_user_message = user_message
                response._learning_model_name = kwargs.get('model', interceptor.extract_model_name(response=response, model_self=self_arg) if hasattr(response, 'model') or hasattr(self_arg, 'model_name') or hasattr(self_arg, '_model_name') else 'unknown')
                return interceptor.extract_assistant_message_streaming_async(response)
            else:
                # Non-streaming - extract and save immediately
                model_name = interceptor.extract_model_name(response=response, model_self=self_arg)

                from ..core import _save_conversation_turn_async
                try:
                    await _save_conversation_turn_async(
                        provider=interceptor.PROVIDER,
                        model=model_name,
                        request_messages=interceptor.build_request_messages(user_message),
                        response_dict=interceptor.build_response_dict(response=response)
                    )
                except Exception as e:
                    import sys
                    print(f"[Warning] Failed to save conversation: {e}", file=sys.stderr)

                return response

        return wrapper
