"""
Anthropic Interceptor

Interceptor for Anthropic SDK (messages.create API).
"""

from typing import Any, AsyncGenerator, Generator

from .base import BaseAPIInterceptor
from .utils import wrap_streaming_generator, wrap_streaming_generator_async


class AnthropicInterceptor(BaseAPIInterceptor):
    """
    Interceptor for Anthropic SDK.

    Intercepts calls to Messages.create() (sync) and AsyncMessages.create() (async).
    """

    PROVIDER = "anthropic"

    @classmethod
    def is_available(cls) -> bool:
        """Check if anthropic is installed."""
        try:
            import anthropic
            return True
        except ImportError:
            return False

    def install(self):
        """Install interceptor by patching Messages and AsyncMessages.create methods."""
        try:
            from anthropic.resources.messages import Messages, AsyncMessages
        except ImportError:
            return

        # Store original methods
        self._original_methods['messages_create'] = Messages.create
        self._original_methods['async_messages_create'] = AsyncMessages.create

        # Patch with wrapped versions
        Messages.create = self.intercept(self._original_methods['messages_create'])
        AsyncMessages.create = self.intercept_async(self._original_methods['async_messages_create'])

    def uninstall(self):
        """Uninstall interceptor and restore original methods."""
        try:
            from anthropic.resources.messages import Messages, AsyncMessages
        except ImportError:
            return

        if 'messages_create' in self._original_methods:
            Messages.create = self._original_methods['messages_create']
        if 'async_messages_create' in self._original_methods:
            AsyncMessages.create = self._original_methods['async_messages_create']

    def extract_user_messages(self, *args, **kwargs) -> str:
        """
        Extract user message from messages.create arguments.

        Args structure: messages=[{"role": "user", "content": "..."}]
        """
        messages = kwargs.get('messages', [])

        # Get the last user message
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                content = msg.get('content', '')

                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    # Multi-modal content - extract text parts
                    text_parts = [c.get('text', '') for c in content if c.get('type') == 'text']
                    return ' '.join(text_parts)

        return ""

    def extract_assistant_message(self, response: Any) -> str:
        """Extract assistant message from non-streaming Anthropic response."""
        text_parts = []

        if hasattr(response, 'content'):
            for block in response.content:
                if hasattr(block, 'type') and block.type == 'text':
                    if hasattr(block, 'text'):
                        text_parts.append(block.text)

        return ' '.join(text_parts)

    def build_request_messages(self, user_message: str) -> list:
        """Build request messages array for Letta."""
        return [{"role": "user", "content": user_message}]

    def build_response_dict(self, response: Any) -> dict:
        """Build response dict for Letta from Anthropic response."""
        text_parts = []

        if hasattr(response, 'content'):
            for block in response.content:
                if hasattr(block, 'type') and block.type == 'text':
                    if hasattr(block, 'text'):
                        text_parts.append(block.text)

        return {"role": "assistant", "content": ' '.join(text_parts)}

    def extract_model_name(self, response: Any = None, model_self: Any = None) -> str:
        """Extract model name from Anthropic response."""
        if response and hasattr(response, 'model'):
            return response.model
        return 'claude-3-5-sonnet-20241022'  # Fallback default

    def _build_response_from_chunks(self, chunks: list) -> Any:
        """
        Build a complete response from streaming chunks.

        For Anthropic, we accumulate text deltas from content_block_delta events.
        """
        texts = []
        base_chunk = None

        for chunk in chunks:
            if hasattr(chunk, 'type'):
                if chunk.type == 'content_block_delta':
                    if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                        texts.append(chunk.delta.text)
                elif chunk.type == 'message_start' and hasattr(chunk, 'message'):
                    base_chunk = chunk.message

        combined_text = ''.join(texts)

        # Wrap to provide combined text
        class CombinedAnthropicResponse:
            """Wrapper around Anthropic response with combined text."""
            def __init__(self, text, model='claude-3-5-sonnet-20241022'):
                self._text = text
                self.model = model
                self.content = [type('Content', (), {'type': 'text', 'text': text})()]

        return CombinedAnthropicResponse(combined_text, base_chunk.model if base_chunk and hasattr(base_chunk, 'model') else 'claude-3-5-sonnet-20241022')

    def extract_assistant_message_streaming(self, stream: Generator) -> Generator:
        """Wrap streaming response to collect chunks."""
        user_message = getattr(stream, '_learning_user_message', None)
        model_name = getattr(stream, '_learning_model_name', 'claude-3-5-sonnet-20241022')

        def save_collected(chunks):
            """Callback to save collected chunks."""
            self._save_streaming_turn_base(chunks, user_message, model_name)

        return wrap_streaming_generator(stream, save_collected)

    async def extract_assistant_message_streaming_async(
        self, stream: AsyncGenerator
    ) -> AsyncGenerator:
        """Wrap async streaming response to collect chunks."""
        user_message = getattr(stream, '_learning_user_message', None)
        model_name = getattr(stream, '_learning_model_name', 'claude-3-5-sonnet-20241022')

        async def save_collected(chunks):
            """Callback to save collected chunks."""
            await self._save_streaming_turn_base_async(chunks, user_message, model_name)

        return wrap_streaming_generator_async(stream, save_collected)

    def inject_memory_context(self, kwargs: dict, context: str) -> dict:
        """
        Inject memory context into Anthropic kwargs.

        Prepends context into the system parameter.
        """
        if not context:
            return kwargs

        # Inject into system parameter
        if 'system' in kwargs:
            if isinstance(kwargs['system'], str):
                kwargs['system'] = f"{context}\n\n{kwargs['system']}"
            elif isinstance(kwargs['system'], list):
                # System is a list of content blocks
                kwargs['system'] = [{"type": "text", "text": context}] + kwargs['system']
        else:
            kwargs['system'] = context

        return kwargs
