"""Debug database query."""
import asyncio
from database.supabase_client import get_supabase_client
from datetime import datetime

async def debug_query():
    """Debug the database query."""
    db = get_supabase_client()
    
    # Try fetching all events without date filter
    print("Fetching all events (no date filter)...")
    query = db.client.table('events').select('*').order('event_date', desc=False)
    response = query.execute()
    
    print(f"\nTotal events in DB: {len(response.data)}")
    for event in response.data:
        print(f"  - {event['title']}: {event['event_date']} (status: {event['status']})")
    
    # Now try with date filter
    print(f"\nCurrent time: {datetime.now().isoformat()}")
    print("\nFetching upcoming events (with date filter)...")
    query2 = db.client.table('events').select('*').gte('event_date', datetime.now().isoformat()).order('event_date', desc=False)
    response2 = query2.execute()
    
    print(f"\nUpcoming events: {len(response2.data)}")
    for event in response2.data:
        print(f"  - {event['title']}: {event['event_date']}")

if __name__ == "__main__":
    asyncio.run(debug_query())
