"""
Test script to check how the agent is parsing user input for registration.
"""
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.nemo_agent import NemoAgent

async def test_agent_parsing():
    """Test how the agent parses registration messages"""
    
    agent = NemoAgent()
    
    test_messages = [
        "Register for abc - John Doe, john@nit.ac.in, 9876543210, IoT A 2024",
        "Register me for abc workshop. Name: John Doe, Email: john@nit.ac.in, Phone: 9876543210, Class: IoT, Section: A, Year: 2024",
        "abc registration - Jane Smith, jane@nit.ac.in, AIDS B 2025"
    ]
    
    print("🧪 Testing Agent Parsing for Registration")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {message}")
        print("-" * 50)
        
        try:
            response = await agent.process_message(message)
            print(f"📤 Agent Response: {response}")
            
            # Look for tool calls in the response
            if "TOOL:" in response and "INPUT:" in response:
                tool_part = response.split("TOOL:")[1].split("INPUT:")[0].strip()
                input_part = response.split("INPUT:")[1].strip()
                print(f"🔧 Tool: {tool_part}")
                print(f"📋 Input: {input_part}")
                
                # Try to parse the input as JSON
                try:
                    import json
                    parsed_input = json.loads(input_part)
                    print(f"✅ Parsed Input:")
                    for key, value in parsed_input.items():
                        print(f"   {key}: {value}")
                        
                    # Check if student details are extracted
                    student_details = {
                        'user_class': parsed_input.get('user_class'),
                        'user_section': parsed_input.get('user_section'),
                        'user_year': parsed_input.get('user_year')
                    }
                    print(f"🎓 Student Details: {student_details}")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Parse Error: {e}")
            else:
                print("ℹ️  No tool call detected in response")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test_agent_parsing())