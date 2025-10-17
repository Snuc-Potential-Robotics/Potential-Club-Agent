"""Direct test of the Nemo agent."""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.nemo_agent import NemoAgent

async def test_agent():
    """Test the agent with a simple query."""
    print("Initializing Nemo agent...")
    agent = NemoAgent()
    print("Agent initialized successfully!\n")
    
    # Test 1: Ask about upcoming events
    print("="*50)
    print("Test 1: Show me upcoming events")
    print("="*50)
    result = await agent.process_message(
        message="Show me upcoming events",
        session_id="test-session-1"
    )
    print(f"Success: {result['success']}")
    print(f"Response: {result['response']}")
    print(f"Suggestions: {result['suggestions']}")
    if not result['success']:
        print(f"Error: {result.get('error')}")
    print()
    
    # Test 2: Ask about a specific event
    print("="*50)
    print("Test 2: Tell me about the abc event")
    print("="*50)
    result = await agent.process_message(
        message="Tell me about the abc event",
        session_id="test-session-1"
    )
    print(f"Success: {result['success']}")
    print(f"Response: {result['response']}")
    print(f"Suggestions: {result['suggestions']}")
    if not result['success']:
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_agent())
