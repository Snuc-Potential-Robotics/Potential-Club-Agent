"""
Simple test to verify registration parsing logic
"""
import json
import re

def extract_registration_info(message):
    """
    Extract registration information from user message.
    This simulates what the agent should be doing.
    """
    result = {}
    
    # Extract event name (everything before the dash)
    if " - " in message:
        parts = message.split(" - ")
        # Look for registration words in first part
        if any(word in parts[0].lower() for word in ["register", "signup", "sign up"]):
            # Try to extract event name from "Register for EVENT_NAME"
            event_match = re.search(r'(?:register|signup|sign up)\s+(?:for\s+)?(.+)', parts[0], re.IGNORECASE)
            if event_match:
                result["event_name"] = event_match.group(1).strip()
        else:
            result["event_name"] = parts[0].strip()
        
        # Parse the user details from the second part
        user_details = parts[1].strip()
    else:
        # Try other formats
        event_match = re.search(r'(?:register|signup|sign up)\s+(?:for\s+)?(.+?)(?:\.|,|$)', message, re.IGNORECASE)
        if event_match:
            result["event_name"] = event_match.group(1).strip()
        user_details = message
    
    # Extract email (must contain @)
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_details)
    if email_match:
        result["user_email"] = email_match.group()
    
    # Extract phone (10 digits)
    phone_match = re.search(r'\b\d{10}\b', user_details)
    if phone_match:
        result["user_phone"] = phone_match.group()
    
    # Extract name (first word sequence before email or phone)
    # Remove email and phone from string first
    name_text = user_details
    if email_match:
        name_text = name_text.replace(email_match.group(), "")
    if phone_match:
        name_text = name_text.replace(phone_match.group(), "")
    
    # Clean up commas and extract name
    name_text = re.sub(r',+', ' ', name_text).strip()
    name_words = []
    
    # Extract words that look like names (not class codes)
    words = name_text.split()
    for word in words:
        word = word.strip(",. ")
        if word and not word.upper() in ["IOT", "AIDS", "CYBER", "A", "B"] and not word.isdigit():
            name_words.append(word)
        else:
            break  # Stop at first non-name word
    
    if name_words:
        result["user_name"] = " ".join(name_words)
    
    # Extract class, section, year pattern
    # Look for pattern like "IoT A 2024", "AIDS B 2025", "Cyber A 2023"
    class_pattern = re.search(r'\b(IoT|AIDS|Cyber)\s+([AB])\s+(202[3-6])\b', user_details, re.IGNORECASE)
    if class_pattern:
        result["user_class"] = class_pattern.group(1)
        result["user_section"] = class_pattern.group(2).upper()
        result["user_year"] = class_pattern.group(3)
    
    return result

def test_extraction():
    """Test the extraction logic"""
    test_cases = [
        "Register for abc - John Doe, john@nit.ac.in, 9876543210, IoT A 2024",
        "Register for abc - John leo john8979@nit.ac.in, 9879543210, IoT B 2025",
        "abc workshop - Jane Smith, jane@nit.ac.in, AIDS B 2025",
        "Register me for robotics workshop. Name: Sarah Connor, Email: sarah@nit.ac.in, Phone: 9988776655, Class: Cyber, Section: A, Year: 2023"
    ]
    
    print("🧪 Testing Registration Information Extraction")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case}")
        print("-" * 50)
        
        extracted = extract_registration_info(test_case)
        
        print("📋 Extracted Information:")
        for key, value in extracted.items():
            print(f"   {key}: {value}")
        
        # Convert to JSON format that tool expects
        json_data = json.dumps(extracted, indent=2)
        print(f"\n📤 JSON for tool:")
        print(json_data)
        
        # Check completeness
        required_fields = ["event_name", "user_name", "user_email"]
        missing_fields = [f for f in required_fields if f not in extracted]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
        else:
            print("✅ All required fields present")
        
        optional_fields = ["user_phone", "user_class", "user_section", "user_year"]
        present_optional = [f for f in optional_fields if f in extracted and extracted[f]]
        
        if present_optional:
            print(f"🎓 Optional fields present: {present_optional}")
        
        print("\n" + "="*70)

if __name__ == "__main__":
    test_extraction()