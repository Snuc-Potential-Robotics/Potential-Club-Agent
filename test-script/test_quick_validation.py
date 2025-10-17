"""
Quick validation test script for event handling
Tests the most critical scenarios to ensure proper functionality
"""

import asyncio
from agents.nemo_agent import NemoAgent
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def test_quick_scenarios():
    """Quick test of critical scenarios."""
    
    logger.info("="*80)
    logger.info("QUICK VALIDATION TEST")
    logger.info("="*80)
    
    agent = NemoAgent()
    session_id = "quick_test"
    
    test_queries = [
        ("Show upcoming events", "Should show ONLY upcoming/today events"),
        ("What events are happening today?", "Should show ONLY today's events"),
        ("Tell me about robotics workshop", "Should search for robotics events"),
        ("I want to register for an upcoming event", "Should help with registration"),
        ("Can I give feedback for upcoming event?", "Should explain feedback rules"),
    ]
    
    for i, (query, expected) in enumerate(test_queries, 1):
        logger.info(f"\n{'-'*80}")
        logger.info(f"Test {i}: {query}")
        logger.info(f"Expected: {expected}")
        logger.info(f"{'-'*80}")
        
        try:
            response = await agent.process_message(query, session_id)
            logger.info(f"\nResponse:\n{response['response']}\n")
            
            if response.get('suggestions'):
                logger.info(f"Suggestions: {', '.join(response['suggestions'])}")
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        
        await asyncio.sleep(0.5)
    
    logger.info("\n" + "="*80)
    logger.info("QUICK TEST COMPLETED")
    logger.info("="*80)


if __name__ == "__main__":
    asyncio.run(test_quick_scenarios())
