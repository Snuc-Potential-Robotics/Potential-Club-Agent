"""Test database connection and check if tables exist."""
import sys
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def test_connection():
    """Test Supabase connection and check tables."""
    print("=" * 60)
    print("Testing Supabase Connection")
    print("=" * 60)
    
    print(f"\n✓ Supabase URL: {SUPABASE_URL}")
    print(f"✓ API Key: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "✗ API Key: Missing")
    
    try:
        from supabase import create_client
        
        # Create client
        print("\nAttempting to create Supabase client...")
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Supabase client created successfully")
        
        # Test 1: Check events table
        print("\n" + "-" * 60)
        print("Test 1: Checking 'events' table...")
        print("-" * 60)
        try:
            response = client.table('events').select('*').limit(5).execute()
            if response.data:
                print(f"✓ Events table exists with {len(response.data)} records")
                for event in response.data:
                    title = event.get('title', event.get('name', 'Unknown'))
                    event_id = event['id'][:8] if 'id' in event else 'no-id'
                    date = event.get('event_date', event.get('date', 'No date'))
                    participants = f"{event.get('current_participants', 0)}/{event.get('max_participants', 'N/A')}"
                    print(f"  - {title}")
                    print(f"    ID: {event_id}... | Date: {date} | Participants: {participants}")
            else:
                print("⚠ Events table exists but is empty")
                print("\n⚠ WARNING: You need to add some events to test properly")
        except Exception as e:
            print(f"✗ Events table error: {str(e)}")
            print("\n✗ ERROR: The 'events' table doesn't exist or has issues!")
            return False
        
        # Test 2: Check registrations table
        print("\n" + "-" * 60)
        print("Test 2: Checking 'registrations' table...")
        print("-" * 60)
        try:
            response = client.table('registrations').select('*').limit(1).execute()
            print(f"✓ Registrations table exists")
        except Exception as e:
            print(f"⚠ Registrations table doesn't exist yet: {str(e)}")
            print("  Run the add_nemo_tables.sql script to create it")
            print("  File: backend/add_nemo_tables.sql")
        
        # Test 3: Check feedback table
        print("\n" + "-" * 60)
        print("Test 3: Checking 'feedback' table...")
        print("-" * 60)
        try:
            response = client.table('feedback').select('*').limit(1).execute()
            print(f"✓ Feedback table exists")
        except Exception as e:
            print(f"⚠ Feedback table doesn't exist yet: {str(e)}")
            print("  Run the add_nemo_tables.sql script to create it")
            print("  File: backend/add_nemo_tables.sql")
        
        print("\n" + "=" * 60)
        print("✓ All database tables exist and are accessible!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Connection failed: {str(e)}")
        print(f"\nError type: {type(e).__name__}")
        
        if "proxy" in str(e).lower():
            print("\n⚠ Supabase version issue detected!")
            print("   Run: pip install --upgrade supabase")
        
        print("\nPossible issues:")
        print("1. Check if SUPABASE_URL and SUPABASE_KEY are correct in .env")
        print("2. Check if your Supabase project is running")
        print("3. Check your internet connection")
        print("4. Try upgrading supabase: pip install --upgrade supabase")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
