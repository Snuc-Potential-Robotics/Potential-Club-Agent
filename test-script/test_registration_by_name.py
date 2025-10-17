"""
Test script for registration by event name functionality
"""

import asyncio
from agents.nemo_agent import NemoAgent
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def test_registration_scenarios():
    """Test different registration scenarios."""
    
    logger.info("="*80)
    logger.info("REGISTRATION BY NAME TEST")
    logger.info("="*80)
    
    agent = NemoAgent()
    session_id = "test_registration"
    
    # Test scenarios
    scenarios = [
        {
            "name": "Complete Registration with All Details",
            "query": "Register me for abc workshop. Name: John Doe, Email: john@nit.ac.in, Phone: 9876543210, Class: IoT, Section: A, Year: 2024",
            "expected": "Should extract all details and register immediately"
        },
        {
            "name": "Registration with Minimal Details",
            "query": "I want to register for abc. My name is Jane Smith and email is jane@nit.ac.in",
            "expected": "Should register with provided details"
        },
        {
            "name": "Registration Request Only",
            "query": "I want to register for abc workshop",
            "expected": "Should ask for required details (name, email)"
        },
        {
            "name": "Feedback with All Details",
            "query": "Feedback for abc event: john@nit.ac.in, 5 stars, excellent workshop!",
            "expected": "Should extract all details and submit feedback immediately"
        },
        {
            "name": "Show Upcoming Events",
            "query": "Show me upcoming events",
            "expected": "Should show only upcoming events"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        logger.info(f"\n{'-'*80}")
        logger.info(f"Test {i}: {scenario['name']}")
        logger.info(f"Query: {scenario['query']}")
        logger.info(f"Expected: {scenario['expected']}")
        logger.info(f"{'-'*80}")
        
        try:
            response = await agent.process_message(scenario['query'], session_id)
            logger.info(f"\n✅ Response:\n{response['response']}\n")
            
            if response.get('suggestions'):
                logger.info(f"💡 Suggestions: {', '.join(response['suggestions'])}")
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
        
        await asyncio.sleep(1)
        
        # Clear session for next test
        agent.clear_session(session_id)
    
    logger.info("\n" + "="*80)
    logger.info("TEST COMPLETED")
    logger.info("="*80)


if __name__ == "__main__":
    asyncio.run(test_registration_scenarios())
