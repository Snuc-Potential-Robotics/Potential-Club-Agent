#!/usr/bin/env python3
"""
Test the exact user scenarios to verify the fix works.
"""

import json
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.tools import extract_student_details_from_message

def test_user_scenarios():
    """Test the exact scenarios reported by users."""
    
    print("🎯 Testing User's Exact Scenarios\n")
    
    # User 1 scenario
    user1_message = "Register for abc - John Doe, john@nit.ac.in, 9876543210, IoT A 2024"
    print("👤 User 1 Message:")
    print(f"'{user1_message}'")
    
    result1 = extract_student_details_from_message(user1_message)
    print("📊 Extracted Data:")
    print(json.dumps(result1, indent=2))
    
    expected1 = {"user_class": "IoT", "user_section": "A", "user_year": "2024"}
    success1 = result1 == expected1
    print(f"✅ Success: {success1}")
    print()
    
    # User 2 scenario  
    user2_message = "Register for abc - John leo john8979@nit.ac.in, 9879543210, IoT B 2025"
    print("👤 User 2 Message:")
    print(f"'{user2_message}'")
    
    result2 = extract_student_details_from_message(user2_message)
    print("📊 Extracted Data:")
    print(json.dumps(result2, indent=2))
    
    expected2 = {"user_class": "IoT", "user_section": "B", "user_year": "2025"}
    success2 = result2 == expected2
    print(f"✅ Success: {success2}")
    print()
    
    # Test what agent should generate for User 1
    print("🤖 What Agent Should Generate for User 1:")
    agent_json = {
        "event_name": "abc",
        "user_name": "John Doe",
        "user_email": "john@nit.ac.in",
        "user_phone": "9876543210",
        "user_class": "IoT",
        "user_section": "A", 
        "user_year": "2024"
    }
    print(json.dumps(agent_json, indent=2))
    print()
    
    # Test what agent should generate for User 2
    print("🤖 What Agent Should Generate for User 2:")
    agent_json2 = {
        "event_name": "abc",
        "user_name": "John leo",
        "user_email": "john8979@nit.ac.in",
        "user_phone": "9879543210",
        "user_class": "IoT",
        "user_section": "B",
        "user_year": "2025"
    }
    print(json.dumps(agent_json2, indent=2))
    print()
    
    overall_success = success1 and success2
    print(f"🎯 Overall Test Result: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    
    if overall_success:
        print("\n🎉 The extraction fix should resolve the registration issue!")
        print("Both users should now get consistent successful registrations.")
    else:
        print("\n⚠️ There may still be issues with the extraction logic.")
    
    return overall_success

if __name__ == "__main__":
    test_user_scenarios()