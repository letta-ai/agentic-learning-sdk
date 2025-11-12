"""
Claude Interactive Example - Agentic Learning SDK

Interactive CLI session with persistent memory across sessions.
Type 'exit' to quit, 'new' to start a new session, or 'interrupt' to stop current task.

Prerequisites:
    pip install agentic-learning
    pip install claude-agent-sdk
    export ANTHROPIC_API_KEY="your-api-key"

Usage:
    python3 claude_example_interactive.py
"""

import asyncio
import os
import sys
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock
from agentic_learning import learning, AgenticLearning


class InteractiveSession:
    """
    Interactive conversation session with persistent memory.

    All conversations are automatically saved to Letta and will be remembered
    across different sessions when using the same agent name.
    """

    def __init__(self, agent_name: str, learning_client: AgenticLearning, options: ClaudeAgentOptions = None):
        """
        Initialize interactive session.

        Args:
            agent_name: Name of the agent (memory persists across sessions with same name)
            learning_client: Agentic Learning client for memory management
            options: Claude Agent SDK options
        """
        self.agent_name = agent_name
        self.learning_client = learning_client
        self.options = options or ClaudeAgentOptions()
        self.client = None
        self.turn_count = 0

    async def start(self):
        """Start the interactive session."""
        print(f"\n{'=' * 80}")
        print(f"Starting session with agent: {self.agent_name}")
        print(f"{'=' * 80}")
        print("\nCommands:")
        print("  'exit'      - Quit the program")
        print("  'new'       - Start a new session (saves current session)")
        print("  'interrupt' - Stop the current task")
        print("\nAll conversations are saved and will be remembered in future sessions.")
        print(f"{'=' * 80}\n")

        # Wrap entire session in memory context
        async with learning(agent=self.agent_name, client=self.learning_client):
            self.client = ClaudeSDKClient(self.options)
            await self.client.connect()

            while True:
                # Get user input
                try:
                    user_input = input(f"\n[Turn {self.turn_count + 1}] You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n\nSession interrupted. Saving and exiting...")
                    break

                # Handle commands
                if not user_input:
                    continue

                if user_input.lower() == 'exit':
                    print("\nExiting...")
                    break
                elif user_input.lower() == 'new':
                    print("\nStarting new session...")
                    break
                elif user_input.lower() == 'interrupt':
                    await self.client.interrupt()
                    print("❗ Task interrupted!")
                    continue

                # Send message - will be captured by Letta memory
                try:
                    await self.client.query(user_input)
                    self.turn_count += 1

                    # Process response
                    print(f"[Turn {self.turn_count}] Claude: ", end="", flush=True)
                    async for message in self.client.receive_response():
                        if isinstance(message, AssistantMessage):
                            for block in message.content:
                                if isinstance(block, TextBlock):
                                    print(block.text, end="", flush=True)
                    print()  # New line after response

                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    continue

            await self.client.disconnect()

        print(f"\n✅ Session ended after {self.turn_count} turns.")
        print(f"✅ All conversations saved to agent '{self.agent_name}'")

        return user_input.lower() == 'new'  # Return True if user wants a new session


async def main():
    """
    Run interactive Claude sessions with persistent memory.

    Note: Make sure Letta server is running at http://localhost:8283
    """
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please run: export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)

    # Initialize learning client
    learning_client = AgenticLearning(base_url="http://localhost:8283")

    # Display welcome banner
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "Claude Interactive Session with Memory" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    print("This interactive CLI demonstrates persistent memory with Claude Agent SDK.")
    print("Memory automatically persists across sessions using the same agent name.")
    print()

    # Get agent name
    agent_name = input("Enter agent name (default: 'claude-interactive'): ").strip()
    if not agent_name:
        agent_name = "claude-interactive"

    # Set up Claude Agent SDK options
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="acceptEdits"
    )

    # Main loop - allows creating new sessions
    while True:
        session = InteractiveSession(
            agent_name=agent_name,
            learning_client=learning_client,
            options=options
        )

        # Start session and check if user wants a new one
        start_new_session = await session.start()

        if not start_new_session:
            break

        # Wait a moment for memory to be saved
        print("\n⏳ Saving session to memory...")
        await asyncio.sleep(2)

    print("\n" + "=" * 80)
    print("Thank you for using Claude Interactive Session!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Session terminated by user. Goodbye!")
        sys.exit(0)
