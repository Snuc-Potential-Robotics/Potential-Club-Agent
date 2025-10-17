"""Test the enhanced agent."""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.nemo_agent import NemoAgent

async def test_enhanced_agent():
    """Test the enhanced agent with specific queries."""
    print("Initializing Enhanced Nemo agent...")
    agent = NemoAgent()
    print("Agent initialized successfully!\n")
    
    # Test 1: Ask about specific event by name
    print("="*50)
    print("Test 1: Tell me about Robo Soccer Competition")
    print("="*50)
    result = await agent.process_message(
        message="Tell me about Robo Soccer Competition",
        session_id="test-session-enhanced"
    )
    print(f"Success: {result['success']}")
    print(f"Response: {result['response']}")
    print(f"Suggestions: {result['suggestions']}")
    if not result['success']:
        print(f"Error: {result.get('error')}")
    print()
    
    # Test 2: Show all events
    print("="*50)
    print("Test 2: Show me all events")
    print("="*50)
    result = await agent.process_message(
        message="Show me all events",
        session_id="test-session-enhanced"
    )
    print(f"Success: {result['success']}")
    print(f"Response: {result['response']}")
    print(f"Suggestions: {result['suggestions']}")
    if not result['success']:
        print(f"Error: {result.get('error')}")
    print()
    
    # Test 3: Search for robotics events
    print("="*50)
    print("Test 3: What robotics events do you have?")
    print("="*50)
    result = await agent.process_message(
        message="What robotics events do you have?",
        session_id="test-session-enhanced"
    )
    print(f"Success: {result['success']}")
    print(f"Response: {result['response']}")
    print(f"Suggestions: {result['suggestions']}")
    if not result['success']:
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_agent())