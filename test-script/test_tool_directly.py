"""Test tool directly."""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.tools import get_upcoming_events

async def test_tool():
    """Test the get_upcoming_events tool directly."""
    print("Testing get_upcoming_events tool...")
    result = await get_upcoming_events.ainvoke("{}")
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_tool())
