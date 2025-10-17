"""Test tools directly to debug datetime issue."""
import asyncio
from agents.tools import search_events_by_name, get_upcoming_events

async def test_tools():
    """Test tools directly."""
    print("Testing search_events_by_name...")
    result = await search_events_by_name.ainvoke("Robo Soccer")
    print(f"Search result: {result}")
    
    print("\nTesting get_upcoming_events...")
    result = await get_upcoming_events.ainvoke('{"show_all": true}')
    print(f"Events result: {result}")

if __name__ == "__main__":
    asyncio.run(test_tools())