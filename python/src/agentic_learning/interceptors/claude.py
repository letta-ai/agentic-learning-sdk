"""
Claude Interceptor

Interceptor for Claude Agent SDK (ClaudeSDKClient).

This interceptor patches the SubprocessCLITransport layer to capture messages
going in/out of the Claude subprocess.
"""

import asyncio
import json
from typing import Any, AsyncIterator

from ..core import get_current_config
from .base import BaseInterceptor


class ClaudeInterceptor(BaseInterceptor):
    """
    Interceptor for Claude Agent SDK (ClaudeSDKClient).

    Patches SubprocessCLITransport to intercept message flow at the transport layer.
    """

    PROVIDER = "claude"

    @classmethod
    def is_available(cls) -> bool:
        """Check if claude-agent-sdk is installed."""
        try:
            import claude_agent_sdk
            return True
        except ImportError:
            return False

    def install(self):
        """Install interceptor by patching SubprocessCLITransport methods."""
        try:
            from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport
        except ImportError:
            return

        # Store original methods (only once)
        if not hasattr(SubprocessCLITransport, '_original_write'):
            SubprocessCLITransport._original_write = SubprocessCLITransport.write
            SubprocessCLITransport._original_read_messages = SubprocessCLITransport.read_messages

        interceptor = self

        # Patch write() to inject memory and capture outgoing messages
        async def patched_write(self, data: str):
            # Inject memory on first write (before any messages are sent)
            if not hasattr(self, '_memory_injected'):
                config = get_current_config()
                if config:
                    await interceptor._inject_memory_async(self._options, config)
                    self._memory_injected = True

            # Capture user message
            config = get_current_config()
            if config:
                await interceptor._capture_outgoing_message(data, config)

            # Call original write
            return await SubprocessCLITransport._original_write(self, data)

        # Patch read_messages() to capture incoming messages
        def patched_read_messages(self):
            # Get original message iterator
            original_iterator = SubprocessCLITransport._original_read_messages(self)

            # Wrap it if memory is enabled
            config = get_current_config()
            if config:
                return interceptor._wrap_message_iterator(original_iterator, config)
            else:
                return original_iterator

        # Apply patches
        SubprocessCLITransport.write = patched_write
        SubprocessCLITransport.read_messages = patched_read_messages

        # Store for uninstall
        self._original_methods['write'] = SubprocessCLITransport._original_write
        self._original_methods['read_messages'] = SubprocessCLITransport._original_read_messages

    def uninstall(self):
        """Uninstall interceptor and restore original methods."""
        try:
            from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport
        except ImportError:
            return

        if 'write' in self._original_methods:
            SubprocessCLITransport.write = self._original_methods['write']
        if 'read_messages' in self._original_methods:
            SubprocessCLITransport.read_messages = self._original_methods['read_messages']

    # =========================================================================
    # Required abstract method implementations
    # =========================================================================

    def build_request_messages(self, user_message: str) -> list:
        """Build request messages array for Letta."""
        return [{"role": "user", "content": user_message}]

    def build_response_dict(self, response: Any) -> dict:
        """Build response dict for Letta."""
        return {"role": "assistant", "content": ""}

    # =========================================================================
    # Claude SDK-specific helper methods
    # =========================================================================

    async def _inject_memory_async(self, options, config: dict):
        """
        Inject memory into Claude Agent options.

        This is called from patched_write() on first write (during client.connect()).
        Uses the user's client (async or sync) to retrieve memory context.

        Args:
            options: ClaudeAgentOptions instance
            config: Current memory configuration
        """
        # Check if capture_only is enabled
        if config.get('capture_only', False):
            return

        client = config.get('client')
        agent_name = config.get('agent_name')

        if not client or not agent_name:
            return

        try:
            # Retrieve memory context (run sync client in thread pool)
            loop = asyncio.get_event_loop()
            memory_context = await loop.run_in_executor(
                None,
                lambda: client.memory.context.retrieve(agent=agent_name)
            )

            if not memory_context:
                return

            # Inject into system prompt
            if hasattr(options, 'system_prompt'):
                if options.system_prompt:
                    # Append to existing system prompt
                    if isinstance(options.system_prompt, str):
                        options.system_prompt += f"\n\n{memory_context}"
                    elif isinstance(options.system_prompt, dict) and "append" in options.system_prompt:
                        options.system_prompt["append"] += f"\n\n{memory_context}"
                else:
                    # Create new system prompt
                    options.system_prompt = memory_context

        except Exception:
            # Don't crash if memory injection fails
            pass

    async def _capture_outgoing_message(self, data: str, config: dict):
        """
        Capture user messages from outgoing transport data.

        Args:
            data: JSON string being sent to the Claude subprocess
            config: Current memory configuration
        """
        try:
            # Parse the JSON message
            message = json.loads(data)
            msg_type = message.get('type')

            # Buffer user messages for batching
            if msg_type == "user":
                # Structure: {"type": "user", "message": {"role": "user", "content": "..."}}
                user_message = message.get("message", {})
                content = user_message.get("content", "")

                if content:
                    # Buffer the user message instead of saving immediately
                    config["pending_user_message"] = content

        except json.JSONDecodeError:
            pass
        except Exception:
            pass

    async def _wrap_message_iterator(
        self, original_iterator: AsyncIterator[dict], config: dict
    ) -> AsyncIterator[dict]:
        """
        Wrap the message iterator to accumulate and save assistant responses.

        Args:
            original_iterator: Original async iterator from Transport.read_messages()
            config: Current memory configuration

        Yields:
            Same messages as original iterator
        """
        accumulated_text = []

        try:
            async for message in original_iterator:
                msg_type = message.get("type", "unknown")

                # Accumulate assistant text
                if msg_type == "assistant":
                    # Structure: {"type": "assistant", "message": {"content": [{"type": "text", "text": "..."}]}}
                    assistant_message = message.get("message", {})
                    content_blocks = assistant_message.get("content", [])

                    for block in content_blocks:
                        if block.get("type") == "text":
                            text = block.get("text", "")
                            if text:
                                accumulated_text.append(text)

                # Always yield immediately for streaming
                yield message

        finally:
            # Save user message + assistant response to Letta (separately)
            user_message = config.get("pending_user_message")
            assistant_message = "".join(accumulated_text) if accumulated_text else None

            # Only save if we have at least one message
            if user_message or assistant_message:
                # Save conversation turn
                from .utils import _save_conversation_turn_async

                await _save_conversation_turn_async(
                    provider=self.PROVIDER,
                    model="claude",
                    request_messages=self.build_request_messages(user_message) if user_message else [],
                    response_dict={"role": "assistant", "content": assistant_message} if assistant_message else {"role": "assistant", "content": ""},
                    register_task=True,
                )

                # Clear the buffer
                config["pending_user_message"] = None
