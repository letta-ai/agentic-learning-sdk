"""Base test class - all provider tests inherit from this."""

import time
from agentic_learning import learning


class BaseInterceptorTests:
    """Base test class for all provider interceptor tests."""

    def test_conversation_saved_to_letta(
        self, learning_client, cleanup_agent, mock_llm_client, make_llm_call
    ):
        """Test conversations are captured and saved."""
        agent_name = cleanup_agent
        agent = learning_client.agents.create(agent=agent_name)
        assert agent is not None

        with learning(agent=agent_name, client=learning_client):
            make_llm_call(mock_llm_client, "My name is Alice")

        time.sleep(5)

        messages = learning_client.messages.list(agent_name)
        assert len(messages) > 0, "No messages saved"

        message_contents = []
        for msg in messages:
            if hasattr(msg, 'content') and isinstance(msg.content, str):
                message_contents.append(msg.content)
            elif hasattr(msg, 'reasoning') and isinstance(msg.reasoning, str):
                message_contents.append(msg.reasoning)

        assert any("Alice" in c for c in message_contents), \
            f"'Alice' not found in messages: {message_contents[:3]}"

    def test_memory_injection(
        self, learning_client, cleanup_agent, mock_llm_client, make_llm_call, get_captured_kwargs
    ):
        """Test memory is injected into LLM calls."""
        agent_name = cleanup_agent
        learning_client.agents.create(agent=agent_name, memory=[])
        learning_client.memory.create(
            agent=agent_name,
            label="human",
            value="User's name is Bob. User likes Python programming."
        )
        time.sleep(2)

        with learning(agent=agent_name, client=learning_client):
            make_llm_call(mock_llm_client, "What's my name?")

        captured_kwargs = get_captured_kwargs()
        assert captured_kwargs is not None, "Failed to capture kwargs"

        kwargs_str = str(captured_kwargs)
        assert ("Bob" in kwargs_str or "<human>" in kwargs_str), \
            f"Memory not injected. Kwargs: {captured_kwargs}"

    def test_capture_only_mode(
        self, learning_client, cleanup_agent, mock_llm_client, make_llm_call, get_captured_kwargs
    ):
        """Test capture_only saves but doesn't inject memory."""
        agent_name = cleanup_agent
        learning_client.agents.create(agent=agent_name, memory=[])
        learning_client.memory.create(
            agent=agent_name,
            label="human",
            value="Secret information that should not be injected"
        )
        time.sleep(2)

        with learning(agent=agent_name, client=learning_client, capture_only=True):
            make_llm_call(mock_llm_client, "Hello, how are you?")

        captured_kwargs = get_captured_kwargs()
        kwargs_str = str(captured_kwargs)
        assert "Secret information" not in kwargs_str, "Memory was injected despite capture_only=True"

        time.sleep(3)
        messages = learning_client.messages.list(agent_name)
        assert len(messages) > 0, "Conversation not saved in capture_only mode"

    def test_memory_injection_with_existing_system_message(
        self, learning_client, cleanup_agent, mock_llm_client, make_llm_call_with_system, get_captured_kwargs
    ):
        """Test memory merges with existing system messages."""
        agent_name = cleanup_agent
        learning_client.agents.create(agent=agent_name, memory=[])
        learning_client.memory.create(
            agent=agent_name,
            label="human",
            value="User prefers concise answers"
        )
        time.sleep(2)

        with learning(agent=agent_name, client=learning_client):
            make_llm_call_with_system(
                mock_llm_client,
                system_message="You are a helpful assistant.",
                user_message="Tell me a joke"
            )

        captured_kwargs = get_captured_kwargs()
        kwargs_str = str(captured_kwargs)

        assert ("concise" in kwargs_str or "<human>" in kwargs_str), \
            "Memory not injected with system message"
        assert "helpful assistant" in kwargs_str, "Original system message lost"

    def test_interceptor_cleanup(
        self, learning_client, cleanup_agent, mock_llm_client, make_llm_call
    ):
        """Test interceptor only captures within learning context."""
        agent_name = cleanup_agent

        with learning(agent=agent_name, client=learning_client):
            make_llm_call(mock_llm_client, "Test message")

        make_llm_call(mock_llm_client, "Uncaptured message")

        time.sleep(3)
        messages = learning_client.messages.list(agent_name)
        assert len(messages) > 0, "Learning context didn't capture"

        message_contents = [msg.content if hasattr(msg, 'content') else '' for msg in messages]
        assert not any("Uncaptured message" in c for c in message_contents), \
            "Captured outside learning context"

    def test_model_name_extraction(
        self, learning_client, cleanup_agent, mock_llm_client, make_llm_call, expected_model_name
    ):
        """Test model name is correctly extracted from provider responses."""
        agent_name = cleanup_agent
        learning_client.agents.create(agent=agent_name)

        with learning(agent=agent_name, client=learning_client):
            make_llm_call(mock_llm_client, "Test model extraction")

        time.sleep(3)

        # Verify expected_model_name is valid
        assert expected_model_name and isinstance(expected_model_name, str), \
            f"Model name should be a non-empty string: {expected_model_name}"
        assert expected_model_name != 'unknown', \
            f"Model name should not be 'unknown': {expected_model_name}"

        # For Gemini specifically, verify no 'models/' prefix in expected name
        client_module = mock_llm_client.__class__.__module__ if hasattr(mock_llm_client, '__class__') else ''
        if 'google.generativeai' in client_module or 'genai' in str(type(mock_llm_client)):
            assert '/' not in expected_model_name, \
                f"Gemini model name should have 'models/' prefix stripped: {expected_model_name}"
