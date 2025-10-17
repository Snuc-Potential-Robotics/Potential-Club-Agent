#!/usr/bin/env python3
"""
Test the improved student details extraction.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.tools import extract_student_details_from_message

def test_extraction():
    """Test extraction with various patterns."""
    
    test_cases = [
        "Register for abc - John Doe, john@nit.ac.in, 9876543210, IoT A 2024",
        "john@nit.ac.in, 9876543210, AIDS B 2025", 
        "Name: John, Email: john@nit.ac.in, Class: Cyber, Section: A, Year: 2023",
        "IoT A 2024",
        "AIDS B 2025",
        "Cyber A 2023",
        "IoT, A, 2024",
        "AIDS, B, 2025",
        "John Doe john@nit.ac.in 9876543210 IoT A 2024",
        "Just IoT",
        "Just A",
        "Just 2024",
        "IoT 2024",  # Missing section
        "A 2024",    # Missing class
    ]
    
    print("🧪 Testing Student Details Extraction\n")
    
    for i, test_case in enumerate(test_cases, 1):
        result = extract_student_details_from_message(test_case)
        print(f"Test {i}: {test_case}")
        print(f"Result: {result}")
        
        # Show what was extracted
        class_val = result.get('user_class', 'None')
        section_val = result.get('user_section', 'None') 
        year_val = result.get('user_year', 'None')
        print(f"Extracted → Class: {class_val}, Section: {section_val}, Year: {year_val}")
        print()
    
    print("✅ Extraction tests completed!")

if __name__ == "__main__":
    test_extraction()