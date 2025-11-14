"""
OpenAI Interceptor

Interceptor for OpenAI SDK (chat.completions and responses APIs).
"""

from typing import Any, AsyncGenerator, Generator

from .base import BaseAPIInterceptor
from .utils import wrap_streaming_generator, wrap_streaming_generator_async


class OpenAIInterceptor(BaseAPIInterceptor):
    """
    Interceptor for OpenAI SDK.

    Intercepts calls to:
    - chat.completions.create() (sync/async)
    - responses.create() (sync/async)
    """

    PROVIDER = "openai"

    @classmethod
    def is_available(cls) -> bool:
        """Check if openai is installed."""
        try:
            import openai
            return True
        except ImportError:
            return False

    def install(self):
        """Install interceptor by patching both Chat Completions and Responses APIs."""
        try:
            from openai.resources.chat.completions import Completions, AsyncCompletions
        except ImportError:
            return

        # Store original methods for Chat Completions
        self._original_methods['completions_create'] = Completions.create
        self._original_methods['async_completions_create'] = AsyncCompletions.create

        # Patch Chat Completions with wrapped versions
        Completions.create = self.intercept(self._original_methods['completions_create'])
        AsyncCompletions.create = self.intercept_async(self._original_methods['async_completions_create'])

        # Try to patch Responses API (available in newer openai SDK versions)
        try:
            from openai.resources.responses import Responses, AsyncResponses

            # Store original methods for Responses API
            self._original_methods['responses_create'] = Responses.create
            self._original_methods['async_responses_create'] = AsyncResponses.create

            # Patch Responses API with wrapped versions
            Responses.create = self.intercept(self._original_methods['responses_create'])
            AsyncResponses.create = self.intercept_async(self._original_methods['async_responses_create'])
        except (ImportError, AttributeError):
            # Responses API not available in this SDK version
            pass

    def uninstall(self):
        """Uninstall interceptor and restore original methods."""
        try:
            from openai.resources.chat.completions import Completions, AsyncCompletions
        except ImportError:
            return

        # Restore Chat Completions methods
        if 'completions_create' in self._original_methods:
            Completions.create = self._original_methods['completions_create']
        if 'async_completions_create' in self._original_methods:
            AsyncCompletions.create = self._original_methods['async_completions_create']

        # Restore Responses API methods if they were patched
        try:
            from openai.resources.responses import Responses, AsyncResponses

            if 'responses_create' in self._original_methods:
                Responses.create = self._original_methods['responses_create']
            if 'async_responses_create' in self._original_methods:
                AsyncResponses.create = self._original_methods['async_responses_create']
        except (ImportError, AttributeError):
            pass

    def extract_user_messages(self, *args, **kwargs) -> str:
        """
        Extract user message from either API format.

        Responses API: input="tell me a joke"
        Chat Completions: messages=[{"role": "user", "content": "..."}]
        """
        # Responses API uses 'input' parameter (simple string)
        if 'input' in kwargs:
            input_value = kwargs.get('input', '')
            if isinstance(input_value, str):
                return input_value
            # Could also be a list of content blocks, handle if needed
            return str(input_value)

        # Chat Completions uses 'messages' parameter
        messages = kwargs.get('messages', [])

        # Get the last user message
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                content = msg.get('content', '')

                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    # Multi-modal content - extract text parts
                    text_parts = [c.get('text', '') for c in content if isinstance(c, dict) and c.get('type') == 'text']
                    return ' '.join(text_parts)

        return ""

    def extract_assistant_message(self, response: Any) -> str:
        """Extract assistant message from non-streaming response (both APIs)."""
        # Responses API format: response.output
        if hasattr(response, 'output'):
            output = response.output
            if isinstance(output, str):
                return output
            # If output is a list of ResponseOutputMessage objects
            elif isinstance(output, list):
                text_parts = []
                for message in output:
                    # Each message has a content attribute with text items
                    if hasattr(message, 'content'):
                        for content_item in message.content:
                            if hasattr(content_item, 'text'):
                                text_parts.append(content_item.text)
                    # Fallback for dict format
                    elif isinstance(message, dict):
                        text_parts.append(message.get('text', ''))
                return ' '.join(text_parts) if text_parts else str(output)

        # Chat Completions format: response.choices[0].message.content
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                return choice.message.content or ""

        return ""

    def build_request_messages(self, user_message: str) -> list:
        """Build request messages array for Letta."""
        return [{"role": "user", "content": user_message}]

    def build_response_dict(self, response: Any) -> dict:
        """Build response dict for Letta from response (both APIs)."""
        # Responses API format
        if hasattr(response, 'output'):
            output = response.output
            if isinstance(output, str):
                return {"role": "assistant", "content": output}
            elif isinstance(output, list):
                text_parts = []
                for message in output:
                    # Each message has a content attribute with text items
                    if hasattr(message, 'content'):
                        for content_item in message.content:
                            if hasattr(content_item, 'text'):
                                text_parts.append(content_item.text)
                    # Fallback for dict format
                    elif isinstance(message, dict):
                        text_parts.append(message.get('text', ''))
                return {"role": "assistant", "content": ' '.join(text_parts) if text_parts else str(output)}

        # Chat Completions format
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                return {"role": "assistant", "content": choice.message.content or ""}

        return {"role": "assistant", "content": ""}

    def extract_model_name(self, response: Any = None, model_self: Any = None) -> str:
        """Extract model name from OpenAI response."""
        if response and hasattr(response, 'model'):
            return response.model
        return 'gpt-5'  # Fallback default

    def _build_response_from_chunks(self, chunks: list) -> Any:
        """
        Build a complete response from streaming chunks (both APIs).

        Chat Completions: chunk.choices[0].delta.content
        Responses API: chunk.output_delta or chunk.delta
        """
        texts = []
        model_name = 'gpt-5'
        is_responses_api = False

        for chunk in chunks:
            # Responses API format: chunk.output_delta or chunk.delta
            if hasattr(chunk, 'output_delta'):
                is_responses_api = True
                output_delta = chunk.output_delta
                if isinstance(output_delta, str):
                    texts.append(output_delta)
                elif isinstance(output_delta, dict) and 'text' in output_delta:
                    texts.append(output_delta['text'])
            elif hasattr(chunk, 'delta') and isinstance(chunk.delta, str):
                # Simple string delta for Responses API
                is_responses_api = True
                texts.append(chunk.delta)
            # Chat Completions format: chunk.choices[0].delta.content
            elif hasattr(chunk, 'choices') and chunk.choices:
                choice = chunk.choices[0]
                if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                    if choice.delta.content is not None:
                        texts.append(choice.delta.content)

            if hasattr(chunk, 'model'):
                model_name = chunk.model

        combined_text = ''.join(texts)

        # Wrap to provide combined text
        class CombinedOpenAIResponse:
            """Wrapper around OpenAI response with combined text."""
            def __init__(self, text, model, is_responses_format):
                self._text = text
                self.model = model
                # For Responses API, include output attribute
                if is_responses_format:
                    self.output = text
                # Also include Chat Completions structure for compatibility
                self.choices = [type('Choice', (), {
                    'message': type('Message', (), {
                        'content': text,
                        'role': 'assistant'
                    })()
                })()]

        return CombinedOpenAIResponse(combined_text, model_name, is_responses_api)

    def extract_assistant_message_streaming(self, stream: Generator) -> Generator:
        """Wrap streaming response to collect chunks."""
        user_message = getattr(stream, '_learning_user_message', None)
        model_name = getattr(stream, '_learning_model_name', 'gpt-5')

        def save_collected(chunks):
            """Callback to save collected chunks."""
            self._save_streaming_turn_base(chunks, user_message, model_name)

        return wrap_streaming_generator(stream, save_collected)

    async def extract_assistant_message_streaming_async(
        self, stream: AsyncGenerator
    ) -> AsyncGenerator:
        """Wrap async streaming response to collect chunks."""
        user_message = getattr(stream, '_learning_user_message', None)
        model_name = getattr(stream, '_learning_model_name', 'gpt-5')

        async def save_collected(chunks):
            """Callback to save collected chunks."""
            await self._save_streaming_turn_base_async(chunks, user_message, model_name)

        return wrap_streaming_generator_async(stream, save_collected)

    def inject_memory_context(self, kwargs: dict, context: str) -> dict:
        """
        Inject memory context into kwargs (both APIs).

        Responses API: Prepends context to 'input' parameter
        Chat Completions: Prepends context as system message
        """
        if not context:
            return kwargs

        # Responses API: inject into 'input' parameter
        if 'input' in kwargs:
            original_input = kwargs['input']
            if isinstance(original_input, str):
                kwargs['input'] = f"{context}\n\n{original_input}"
            return kwargs

        # Chat Completions: inject into messages array as system message
        if 'messages' in kwargs:
            messages = kwargs['messages']

            # Insert memory as system message at the beginning
            memory_message = {
                "role": "system",
                "content": context
            }

            # If there's already a system message, append to it
            if messages and messages[0].get('role') == 'system':
                messages[0]['content'] = f"{context}\n\n{messages[0]['content']}"
            else:
                kwargs['messages'] = [memory_message] + messages

        return kwargs
