"""
Gemini Interceptor

Interceptor for Google Generative AI SDK (Gemini).
"""

from typing import Any, AsyncGenerator, Generator

from .base import BaseAPIInterceptor
from .utils import wrap_streaming_generator, wrap_streaming_generator_async


class GeminiInterceptor(BaseAPIInterceptor):
    """
    Interceptor for Google Generative AI SDK (Gemini).

    Intercepts calls to GenerativeModel.generate_content() and
    GenerativeModel.generate_content_async().
    """

    PROVIDER = "gemini"

    @classmethod
    def is_available(cls) -> bool:
        """Check if google.generativeai is installed."""
        try:
            import google.generativeai
            return True
        except ImportError:
            return False

    def install(self):
        """Install interceptor by patching GenerativeModel methods."""
        import google.generativeai as genai

        # Store original methods
        self._original_methods['generate_content'] = genai.GenerativeModel.generate_content
        self._original_methods['generate_content_async'] = genai.GenerativeModel.generate_content_async

        # Patch with wrapped versions
        genai.GenerativeModel.generate_content = self.intercept_gemini(
            self._original_methods['generate_content']
        )
        genai.GenerativeModel.generate_content_async = self.intercept_async(
            self._original_methods['generate_content_async']
        )

    def uninstall(self):
        """Uninstall interceptor and restore original methods."""
        import google.generativeai as genai

        if 'generate_content' in self._original_methods:
            genai.GenerativeModel.generate_content = self._original_methods['generate_content']
        if 'generate_content_async' in self._original_methods:
            genai.GenerativeModel.generate_content_async = self._original_methods['generate_content_async']

    def extract_user_messages(self, *args, **kwargs) -> str:
        """
        Extract user message from generate_content arguments.

        Args can be:
        - Single string prompt
        - List of content parts
        - Contents parameter in kwargs
        """
        # Check positional args first
        if args and len(args) > 1:
            contents = args[1]  # args[0] is self (the model instance)
        elif 'contents' in kwargs:
            contents = kwargs['contents']
        else:
            return ""

        # Handle different content formats
        if isinstance(contents, str):
            return contents
        elif isinstance(contents, list):
            # List of parts or messages
            messages = []
            for item in contents:
                if isinstance(item, str):
                    messages.append(item)
                elif hasattr(item, 'parts'):
                    # Content object with parts
                    for part in item.parts:
                        if hasattr(part, 'text'):
                            messages.append(part.text)
                elif hasattr(item, 'text'):
                    messages.append(item.text)
            return "\n".join(messages)

        return ""

    def extract_assistant_message(self, response: Any) -> str:
        """Extract assistant message from non-streaming Gemini response."""
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                return "\n".join(parts)
        return ""

    def build_request_messages(self, user_message: str) -> list:
        """Build request messages array for Letta."""
        return [{"role": "user", "content": user_message}]

    def build_response_dict(self, response: Any) -> dict:
        """Build response dict for Letta from Gemini response."""
        if hasattr(response, 'text'):
            return {"role": "assistant", "content": response.text}
        elif hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                return {"role": "assistant", "content": "\n".join(parts)}

        return {"role": "assistant", "content": ""}

    def extract_model_name(self, response: Any = None, model_self: Any = None) -> str:
        """Extract model name from Gemini GenerativeModel instance."""
        model_name = 'gemini-2.5-flash' # Fallback default
        if model_self:
            if hasattr(model_self, 'model_name'):
                model_name = model_self.model_name
            elif hasattr(model_self, '_model_name'):
                model_name = model_self._model_name
        # Handle model names with '/' prefix (e.g., 'models/gemini-2.5-flash')
        if isinstance(model_name, str) and '/' in model_name:
            model_name = model_name.split('/')[-1]
        return model_name

    def _build_response_from_chunks(self, chunks: list) -> Any:
        """
        Build a complete response from streaming chunks.

        Uses the first chunk as a base (real Gemini response object) and wraps it
        to provide the combined text from all chunks.
        """
        # Extract text from all chunks
        texts = []
        for chunk in chunks:
            if hasattr(chunk, 'text'):
                texts.append(chunk.text)
            elif hasattr(chunk, 'candidates') and chunk.candidates:
                candidate = chunk.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text'):
                            texts.append(part.text)

        combined_text = "".join(texts)

        # Use the first chunk as base (it's a real Gemini response object)
        if chunks:
            base_chunk = chunks[0]

            # Wrap the real chunk to provide combined text
            class CombinedGeminiResponse:
                """Wrapper around real Gemini chunk with combined text from all chunks."""
                def __init__(self, base, full_text):
                    self._base = base
                    self._full_text = full_text

                @property
                def text(self):
                    return self._full_text

                @property
                def candidates(self):
                    return self._base.candidates if hasattr(self._base, 'candidates') else []

                def __getattr__(self, name):
                    # Delegate all other attributes to the base chunk
                    return getattr(self._base, name)

            return CombinedGeminiResponse(base_chunk, combined_text)

        # Fallback if no chunks (shouldn't happen)
        class EmptyResponse:
            text = ""
        return EmptyResponse()

    def extract_assistant_message_streaming(self, stream: Generator) -> Generator:
        """Wrap streaming response to collect chunks."""
        user_message = getattr(stream, '_learning_user_message', None)
        model_name = getattr(stream, '_learning_model_name', 'gemini-2.5-flash')

        def save_collected(chunks):
            """Callback to save collected chunks."""
            self._save_streaming_turn_base(chunks, user_message, model_name)

        return wrap_streaming_generator(stream, save_collected)

    async def extract_assistant_message_streaming_async(
        self, stream: AsyncGenerator
    ) -> AsyncGenerator:
        """Wrap async streaming response to collect chunks."""
        user_message = getattr(stream, '_learning_user_message', None)
        model_name = getattr(stream, '_learning_model_name', 'gemini-2.5-flash')

        async def save_collected(chunks):
            """Callback to save collected chunks."""
            await self._save_streaming_turn_base_async(chunks, user_message, model_name)

        return wrap_streaming_generator_async(stream, save_collected)

    def inject_memory_context(self, kwargs: dict, context: str) -> dict:
        """
        Inject memory context into Gemini kwargs.

        Prepends context into the contents parameter.
        """
        if not context:
            return kwargs

        # Gemini uses 'contents' parameter (not 'messages')
        if 'contents' in kwargs:
            contents = kwargs['contents']

            # Handle different content formats
            if isinstance(contents, str):
                kwargs['contents'] = f"{context}\n\n{contents}"
            elif isinstance(contents, list):
                kwargs['contents'] = [context] + contents

        return kwargs

    def intercept_gemini(self, original_method):
        """
        Custom intercept for Gemini that handles positional args.

        Gemini's generate_content accepts contents as a positional arg,
        but memory injection modifies kwargs. This wrapper converts
        positional args to kwargs before calling the base intercept.
        """
        import functools

        base_wrapper = self.intercept(original_method)

        @functools.wraps(original_method)
        def wrapper(self_arg, *args, **kwargs):
            # Convert positional contents arg to kwarg
            if args and len(args) > 0:
                # First positional arg after self is 'contents'
                if 'contents' not in kwargs:
                    kwargs['contents'] = args[0]
                    args = args[1:]  # Remove the consumed arg

            # Call the base wrapper with updated kwargs
            return base_wrapper(self_arg, *args, **kwargs)

        return wrapper
