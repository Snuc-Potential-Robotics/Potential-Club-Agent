"""Debug script to test registration process and database state."""
import asyncio
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_registration_debug():
    """Test registration and check database state."""
    print("=" * 80)
    print("REGISTRATION DEBUG TEST")
    print("=" * 80)
    print()
    
    try:
        from database.supabase_client import get_supabase_client
        from agents.tools import register_for_event_by_name, search_events_by_name
        
        db = get_supabase_client()
        
        # Test 1: Check if 'abc' event exists
        print("TEST 1: Searching for 'abc' event...")
        print("-" * 80)
        search_result = await search_events_by_name.ainvoke("abc")
        search_data = json.loads(search_result)
        print(f"Search result: {json.dumps(search_data, indent=2)}")
        print()
        
        # Test 2: Try to register User 1
        print("TEST 2: Registering User 1 (John Doe)...")
        print("-" * 80)
        registration_input_1 = {
            "event_name": "abc",
            "user_name": "John Doe",
            "user_email": "john@nit.ac.in",
            "user_phone": "9876543210",
            "user_class": "IoT",
            "user_section": "A",
            "user_year": "2024"
        }
        print(f"Input: {json.dumps(registration_input_1, indent=2)}")
        result_1 = await register_for_event_by_name.ainvoke(json.dumps(registration_input_1))
        result_1_data = json.loads(result_1)
        print(f"Result: {json.dumps(result_1_data, indent=2)}")
        print()
        
        # Test 3: Check database state after first registration
        print("TEST 3: Checking database registrations table...")
        print("-" * 80)
        try:
            response = db.client.table('registrations').select('*').execute()
            if response.data:
                print(f"Found {len(response.data)} registrations in database:")
                for reg in response.data:
                    print(f"  - {reg.get('user_name')} ({reg.get('user_email')})")
            else:
                print("No registrations found in database")
        except Exception as e:
            print(f"Error reading registrations table: {str(e)}")
        print()
        
        # Test 4: Try to register User 2
        print("TEST 4: Registering User 2 (John Leo)...")
        print("-" * 80)
        registration_input_2 = {
            "event_name": "abc",
            "user_name": "John Leo",
            "user_email": "john8979@nit.ac.in",
            "user_phone": "9879543210",
            "user_class": "IoT",
            "user_section": "B",
            "user_year": "2025"
        }
        print(f"Input: {json.dumps(registration_input_2, indent=2)}")
        result_2 = await register_for_event_by_name.ainvoke(json.dumps(registration_input_2))
        result_2_data = json.loads(result_2)
        print(f"Result: {json.dumps(result_2_data, indent=2)}")
        print()
        
        # Test 5: Check database state after second registration
        print("TEST 5: Checking database registrations table again...")
        print("-" * 80)
        try:
            response = db.client.table('registrations').select('*').execute()
            if response.data:
                print(f"Found {len(response.data)} registrations in database:")
                for reg in response.data:
                    print(f"  - {reg.get('user_name')} ({reg.get('user_email')}) - Event: {reg.get('event_id')}")
            else:
                print("No registrations found in database")
        except Exception as e:
            print(f"Error reading registrations table: {str(e)}")
        print()
        
        # Test 6: Check event details
        print("TEST 6: Checking 'abc' event details after registrations...")
        print("-" * 80)
        try:
            response = db.client.table('events').select('*').ilike('name', '%abc%').execute()
            if response.data:
                for event in response.data:
                    print(f"Event: {event.get('name')}")
                    print(f"  Available slots: {event.get('available_slots')}")
                    print(f"  Total slots: {event.get('total_slots')}")
                    print(f"  Current participants: {event.get('current_participants', 0)}")
            else:
                print("Event 'abc' not found")
        except Exception as e:
            print(f"Error reading events table: {str(e)}")
        print()
        
        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"User 1 Registration Success: {result_1_data.get('success', False)}")
        print(f"User 2 Registration Success: {result_2_data.get('success', False)}")
        
        if not result_1_data.get('success'):
            print(f"User 1 Error: {result_1_data.get('error', 'Unknown error')}")
        if not result_2_data.get('success'):
            print(f"User 2 Error: {result_2_data.get('error', 'Unknown error')}")
        
        print()
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_registration_debug())
