"""Simple test to verify database registration fix."""
import asyncio
import sys
import os

# Set up path
sys.path.insert(0, os.path.dirname(__file__))

async def main():
    print("="  * 70)
    print("SIMPLE REGISTRATION TEST")
    print("=" * 70)
    print()
    
    try:
        # Import database client only
        from database.supabase_client import get_supabase_client
        import json
        from datetime import datetime
        
        db = get_supabase_client()
        
        # Find 'abc' event
        print("Step 1: Searching for 'abc' event...")
        events = await db.fetch_events(limit=100, date_from=None, only_active=True)
        abc_event = None
        for event in events:
            if 'abc' in event['name'].lower():
                abc_event = event
                break
        
        if not abc_event:
            print("❌ Event 'abc' not found!")
            return
        
        print(f"✅ Found event: {abc_event['name']} (ID: {abc_event['id']})")
        print(f"   Available slots: {abc_event['available_slots']}")
        print()
        
        # Test registration 1
        print("Step 2: Registering User 1 (John Doe with full details)...")
        try:
            reg1 = await db.create_registration(
                event_id=abc_event['id'],
                user_name="John Doe",
                user_email="john@nit.ac.in",
                user_phone="9876543210",
                user_class="IoT",
                user_section="A",
                user_year="2024"
            )
            print(f"✅ Registration successful!")
            print(f"   ID: {reg1.get('id')}")
            print(f"   Name: {reg1.get('user_name')}")
            print(f"   Email: {reg1.get('user_email')}")
            print(f"   Class: {reg1.get('user_class', 'NOT SAVED')}")
            print(f"   Section: {reg1.get('user_section', 'NOT SAVED')}")
            print(f"   Year: {reg1.get('user_year', 'NOT SAVED')}")
        except Exception as e:
            print(f"❌ Registration failed: {str(e)}")
        print()
        
        # Check database
        print("Step 3: Checking database...")
        try:
            response = db.client.table('registrations').select('*').limit(10).execute()
            if response.data:
                print(f"✅ Found {len(response.data)} registration(s) in database:")
                for reg in response.data:
                    print(f"   - {reg.get('user_name')} ({reg.get('user_email')})")
                    if 'user_class' in reg:
                        print(f"     Class: {reg.get('user_class')}, Section: {reg.get('user_section')}, Year: {reg.get('user_year')}")
                    else:
                        print(f"     ⚠️  Student details columns NOT in database")
            else:
                print("❌ No registrations found in database")
        except Exception as e:
            print(f"❌ Error reading database: {str(e)}")
        print()
        
        # Test registration 2 with different user
        print("Step 4: Registering User 2 (John Leo with full details)...")
        try:
            reg2 = await db.create_registration(
                event_id=abc_event['id'],
                user_name="John Leo",
                user_email="john8979@nit.ac.in",
                user_phone="9879543210",
                user_class="IoT",
                user_section="B",
                user_year="2025"
            )
            print(f"✅ Registration successful!")
            print(f"   Name: {reg2.get('user_name')}")
            print(f"   Email: {reg2.get('user_email')}")
        except ValueError as ve:
            if "already registered" in str(ve):
                print(f"ℹ️  User already registered (this is correct behavior)")
            else:
                print(f"❌ Registration failed: {str(ve)}")
        except Exception as e:
            print(f"❌ Registration failed: {str(e)}")
        print()
        
        # Final database check
        print("Step 5: Final database state...")
        try:
            response = db.client.table('registrations').select('*').limit(20).execute()
            print(f"Total registrations in database: {len(response.data) if response.data else 0}")
            
            # Check if new columns exist
            if response.data and len(response.data) > 0:
                first_reg = response.data[0]
                has_new_columns = 'user_class' in first_reg
                print(f"Student detail columns exist: {'✅ YES' if has_new_columns else '❌ NO'}")
                
                if not has_new_columns:
                    print()
                    print("⚠️  ACTION REQUIRED:")
                    print("   Run this SQL in Supabase to add missing columns:")
                    print("   File: backend/add_student_details_columns.sql")
        except Exception as e:
            print(f"Error: {str(e)}")
        print()
        
        print("=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
