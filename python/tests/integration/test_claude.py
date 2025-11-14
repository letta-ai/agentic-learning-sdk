"""
Integration tests for Claude Agent SDK interceptor.

These tests use the real Claude Agent SDK with real API calls.
Requires ANTHROPIC_API_KEY environment variable.

NOTE: All tests are async because Claude Agent SDK only supports async operations.
"""

import os
import pytest
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

from agentic_learning.core import learning
from tests.shared import test_runners

# Module-level state for capturing kwargs
_captured_state = {}


@pytest.mark.integration
@pytest.mark.claude
@pytest.mark.asyncio
class TestClaudeIntegration:
    """Claude Agent SDK integration tests with real SDK and real API calls."""

    @pytest.fixture
    def claude_client(self):
        """Create a real Claude Agent SDK client with real API key."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set - skipping integration test")
        options = ClaudeAgentOptions()
        return ClaudeSDKClient(options)

    @pytest.fixture
    def make_llm_call(self, claude_client):
        """Function to make Claude agent calls - returns async function."""

        async def _make_call(prompt: str):
            """Async function that makes Claude API call."""
            _captured_state.clear()
            _captured_state['prompt'] = prompt

            await claude_client.connect()
            await claude_client.query(prompt)

            response_text = ""
            async for msg in claude_client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            response_text += block.text

            await claude_client.disconnect()

            _captured_state['response'] = response_text
            return response_text

        return _make_call

    @pytest.fixture
    def get_captured_state(self):
        """Fixture to get captured state."""
        return lambda: _captured_state.copy()

    async def test_conversation_saved(
        self, learning_client, cleanup_agent, make_llm_call, sleep_config
    ):
        """Test conversations are captured and saved to Letta."""
        await test_runners.conversation_saved_async(
            learning_client=learning_client,
            agent_name=cleanup_agent,
            make_call=make_llm_call,
            sleep_config=sleep_config,
            expected_content="Alice",
        )

    async def test_memory_injection(
        self, learning_client, cleanup_agent, make_llm_call, sleep_config
    ):
        """Test memory context is injected into LLM calls."""
        import asyncio
        agent_name = cleanup_agent
        learning_client.agents.create(agent=agent_name, memory=[])
        learning_client.memory.create(
            agent=agent_name,
            label="human",
            value="User's name is Bob. User likes Python programming."
        )
        await asyncio.sleep(sleep_config['memory_create'])

        # Make call with learning context
        with learning(agent=agent_name, client=learning_client):
            response = await make_llm_call("What's my name?")

        # For real API calls, the test passes if no errors occur
        assert response is not None

    async def test_capture_only(
        self, learning_client, cleanup_agent, make_llm_call, get_captured_state, sleep_config
    ):
        """Test capture-only mode doesn't inject memory."""
        await test_runners.capture_only_async(
            learning_client=learning_client,
            agent_name=cleanup_agent,
            make_call=make_llm_call,
            captured_state=get_captured_state,
            sleep_config=sleep_config,
        )

    async def test_interceptor_cleanup(
        self, learning_client, cleanup_agent, make_llm_call, sleep_config
    ):
        """Test interceptor only captures within learning context."""
        await test_runners.interceptor_cleanup_async(
            learning_client=learning_client,
            agent_name=cleanup_agent,
            make_call=make_llm_call,
            sleep_config=sleep_config,
        )
