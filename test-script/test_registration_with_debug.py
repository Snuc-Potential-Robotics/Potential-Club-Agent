#!/usr/bin/env python3
"""
Test registration with debugging to see exactly what's happening.
"""

import json
import asyncio
import sys
import os
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.tools import register_for_event_by_name

async def test_registration_debug():
    """Test registration with debug output to see parsing."""
    
    print("🔍 Testing Registration with Debug Output\n")
    
    # Test the exact scenario from user's example
    print("=== Testing User's Exact Scenario ===")
    
    # What the agent PROBABLY sends (missing student details)
    likely_input = {
        "event_name": "abc",
        "user_name": "John Doe",
        "user_email": "john@nit.ac.in"
        # Missing: user_phone, user_class, user_section, user_year
    }
    
    print("1. Testing LIKELY input (what agent probably sends):")
    print("Input:", json.dumps(likely_input, indent=2))
    
    try:
        result = await register_for_event_by_name(json.dumps(likely_input))
        print("Result:", result)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # What the agent should send with raw_message fallback
    fallback_input = {
        "event_name": "abc",
        "user_name": "John Doe",
        "user_email": "john@nit.ac.in",
        "raw_message": "Register for abc - John Doe, john@nit.ac.in, 9876543210, IoT A 2024"
    }
    
    print("2. Testing FALLBACK input (with raw_message for extraction):")
    print("Input:", json.dumps(fallback_input, indent=2))
    
    try:
        result = await register_for_event_by_name(json.dumps(fallback_input))
        print("Result:", result)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✅ Debug registration tests completed!")

if __name__ == "__main__":
    asyncio.run(test_registration_debug())