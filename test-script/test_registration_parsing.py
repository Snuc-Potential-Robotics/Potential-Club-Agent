#!/usr/bin/env python3
"""
Test the registration parsing functionality directly.
"""

import json
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.tools import register_for_event_by_name

async def test_registration_parsing():
    """Test registration with different input formats."""
    
    print("🧪 Testing Registration Parsing Logic\n")
    
    # Test 1: Complete data with raw_message fallback
    print("Test 1: Complete data with raw_message")
    test_input_1 = {
        "event_name": "abc",
        "user_name": "John Doe",
        "user_email": "john@nit.ac.in",
        "user_phone": "9876543210",
        "raw_message": "Register for abc - John Doe, john@nit.ac.in, 9876543210, IoT A 2024"
    }
    
    result_1 = await register_for_event_by_name(json.dumps(test_input_1))
    print("Input:", json.dumps(test_input_1, indent=2))
    print("Result:", result_1)
    print()
    
    # Test 2: Data in user_name field
    print("Test 2: Student details in user_name")
    test_input_2 = {
        "event_name": "abc", 
        "user_name": "John Doe IoT A 2024",
        "user_email": "john@nit.ac.in",
        "user_phone": "9876543210"
    }
    
    result_2 = await register_for_event_by_name(json.dumps(test_input_2))
    print("Input:", json.dumps(test_input_2, indent=2))
    print("Result:", result_2)
    print()
    
    # Test 3: Minimal data (should ask for more)
    print("Test 3: Minimal data")
    test_input_3 = {
        "event_name": "abc",
        "user_name": "John Doe", 
        "user_email": "john@nit.ac.in"
    }
    
    result_3 = await register_for_event_by_name(json.dumps(test_input_3))
    print("Input:", json.dumps(test_input_3, indent=2))
    print("Result:", result_3)
    print()
    
    # Test 4: What the agent might actually be sending (based on our debugging)
    print("Test 4: What agent might send")
    test_input_4 = {
        "event_name": "abc",
        "user_name": "John Doe",
        "user_email": "john@nit.ac.in"
        # Missing: user_class, user_section, user_year
    }
    
    result_4 = await register_for_event_by_name(json.dumps(test_input_4))
    print("Input:", json.dumps(test_input_4, indent=2))
    print("Result:", result_4)
    
    print("\n✅ Registration parsing tests completed!")

if __name__ == "__main__":
    asyncio.run(test_registration_parsing())