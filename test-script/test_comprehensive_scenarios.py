"""
Comprehensive Test Suite for Event Management System
Tests various user queries and edge cases to ensure proper handling.
"""

import asyncio
import json
from datetime import datetime
from agents.nemo_agent import NemoAgent
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveTestSuite:
    """Test suite for comprehensive scenario testing."""
    
    def __init__(self):
        self.agent = None
        self.test_results = []
        self.session_id = "test_session_comprehensive"
    
    async def setup(self):
        """Initialize the agent."""
        logger.info("Setting up test agent...")
        self.agent = NemoAgent()
        logger.info("Agent initialized successfully")
    
    async def run_test(self, test_name: str, query: str, expected_behavior: str):
        """
        Run a single test case.
        
        Args:
            test_name: Name of the test
            query: User query to test
            expected_behavior: Expected behavior description
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: {test_name}")
        logger.info(f"QUERY: {query}")
        logger.info(f"EXPECTED: {expected_behavior}")
        logger.info(f"{'='*80}")
        
        try:
            response = await self.agent.process_message(query, self.session_id)
            
            logger.info(f"\nRESPONSE:")
            logger.info(f"{response['response']}")
            
            if response.get('success', False):
                self.test_results.append({
                    "test": test_name,
                    "query": query,
                    "status": "PASSED",
                    "response": response['response'][:200]
                })
            else:
                self.test_results.append({
                    "test": test_name,
                    "query": query,
                    "status": "FAILED",
                    "error": response.get('error', 'Unknown error')
                })
            
            # Wait a bit between tests
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Test failed with exception: {str(e)}")
            self.test_results.append({
                "test": test_name,
                "query": query,
                "status": "ERROR",
                "error": str(e)
            })
    
    async def run_all_tests(self):
        """Run all comprehensive test scenarios."""
        
        # Test Category 1: Upcoming Events Queries
        logger.info("\n" + "="*80)
        logger.info("CATEGORY 1: UPCOMING EVENTS QUERIES")
        logger.info("="*80)
        
        await self.run_test(
            "Test 1.1: Basic Upcoming Events",
            "Show me upcoming events",
            "Should show ONLY upcoming and today's events, NOT completed events"
        )
        
        await self.run_test(
            "Test 1.2: Events Happening Today",
            "What events are happening today?",
            "Should show ONLY events scheduled for today"
        )
        
        await self.run_test(
            "Test 1.3: All Events Request",
            "Show me all events",
            "Should show all events including past, present, and future"
        )
        
        await self.run_test(
            "Test 1.4: Past/Completed Events",
            "What events have already happened?",
            "Should show ONLY completed/past events"
        )
        
        # Test Category 2: Specific Event Search
        logger.info("\n" + "="*80)
        logger.info("CATEGORY 2: SPECIFIC EVENT SEARCH")
        logger.info("="*80)
        
        await self.run_test(
            "Test 2.1: Search by Event Name",
            "Tell me about robotics workshop",
            "Should search for events matching 'robotics workshop' in name, description, or category"
        )
        
        await self.run_test(
            "Test 2.2: Search by Category",
            "What robotics events do you have?",
            "Should find all robotics-related events"
        )
        
        await self.run_test(
            "Test 2.3: Search Non-existent Event",
            "Tell me about quantum computing event",
            "Should clearly state no events found and suggest alternatives"
        )
        
        await self.run_test(
            "Test 2.4: Partial Name Search",
            "Any soccer events?",
            "Should find events with 'soccer' in name or description"
        )
        
        # Test Category 3: Event Registration Edge Cases
        logger.info("\n" + "="*80)
        logger.info("CATEGORY 3: EVENT REGISTRATION EDGE CASES")
        logger.info("="*80)
        
        await self.run_test(
            "Test 3.1: Register for Upcoming Event",
            "I want to register for the next upcoming robotics event",
            "Should allow registration for upcoming events with available slots"
        )
        
        await self.run_test(
            "Test 3.2: Register for Completed Event",
            "Can I register for events that happened last month?",
            "Should explain that registration is NOT allowed for completed events"
        )
        
        await self.run_test(
            "Test 3.3: Register for Today's Event",
            "I want to register for today's event",
            "Should allow registration for events happening today"
        )
        
        await self.run_test(
            "Test 3.4: Check Registration Requirements",
            "What do I need to register for an event?",
            "Should explain registration process and required information"
        )
        
        # Test Category 4: Feedback Submission Edge Cases
        logger.info("\n" + "="*80)
        logger.info("CATEGORY 4: FEEDBACK SUBMISSION EDGE CASES")
        logger.info("="*80)
        
        await self.run_test(
            "Test 4.1: Feedback for Upcoming Event",
            "I want to give feedback for the upcoming robotics workshop",
            "Should explain that feedback CANNOT be given for upcoming events"
        )
        
        await self.run_test(
            "Test 4.2: Feedback for Today's Event",
            "Can I give feedback for today's event?",
            "Should confirm that feedback CAN be given for today's events"
        )
        
        await self.run_test(
            "Test 4.3: Feedback for Recent Completed Event",
            "I want to give feedback for the event from 3 days ago",
            "Should allow feedback for recently completed events (within 7 days)"
        )
        
        await self.run_test(
            "Test 4.4: Feedback for Old Completed Event",
            "Can I give feedback for an event from 2 months ago?",
            "Should explain that feedback period has ended (>7 days old)"
        )
        
        # Test Category 5: Complex Queries
        logger.info("\n" + "="*80)
        logger.info("CATEGORY 5: COMPLEX QUERIES")
        logger.info("="*80)
        
        await self.run_test(
            "Test 5.1: Multiple Intent Query",
            "Show me upcoming robotics events and help me register",
            "Should handle multiple intents: show events AND explain registration"
        )
        
        await self.run_test(
            "Test 5.2: Event Details with Actions",
            "Tell me about the next workshop and what I can do",
            "Should show event details AND explain available actions (register/feedback)"
        )
        
        await self.run_test(
            "Test 5.3: Date-specific Query",
            "Are there any events this week?",
            "Should interpret time context and show relevant events"
        )
        
        await self.run_test(
            "Test 5.4: Availability Check",
            "Which events still have slots available?",
            "Should filter and show only events with available registration slots"
        )
        
        # Test Category 6: Edge Cases and Error Handling
        logger.info("\n" + "="*80)
        logger.info("CATEGORY 6: EDGE CASES AND ERROR HANDLING")
        logger.info("="*80)
        
        await self.run_test(
            "Test 6.1: Empty Database Scenario",
            "Show me all events",
            "Should gracefully handle case when no events exist"
        )
        
        await self.run_test(
            "Test 6.2: Ambiguous Query",
            "Events",
            "Should intelligently interpret and show appropriate events (likely upcoming)"
        )
        
        await self.run_test(
            "Test 6.3: Invalid Action Request",
            "Delete an event",
            "Should explain that deletion is not available and suggest valid actions"
        )
        
        await self.run_test(
            "Test 6.4: Help Query",
            "What can you help me with?",
            "Should explain capabilities and provide examples"
        )
    
    def generate_report(self):
        """Generate test report summary."""
        logger.info("\n" + "="*80)
        logger.info("TEST EXECUTION SUMMARY")
        logger.info("="*80)
        
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['status'] == 'PASSED')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAILED')
        errors = sum(1 for r in self.test_results if r['status'] == 'ERROR')
        
        logger.info(f"\nTotal Tests: {total_tests}")
        logger.info(f"Passed: {passed} ({passed/total_tests*100:.1f}%)")
        logger.info(f"Failed: {failed} ({failed/total_tests*100:.1f}%)")
        logger.info(f"Errors: {errors} ({errors/total_tests*100:.1f}%)")
        
        if failed > 0 or errors > 0:
            logger.info("\n" + "="*80)
            logger.info("FAILED/ERROR TESTS:")
            logger.info("="*80)
            for result in self.test_results:
                if result['status'] in ['FAILED', 'ERROR']:
                    logger.info(f"\n{result['test']}")
                    logger.info(f"Query: {result['query']}")
                    logger.info(f"Error: {result.get('error', 'Unknown')}")
        
        logger.info("\n" + "="*80)
        logger.info("TEST SUITE COMPLETED")
        logger.info("="*80)
        
        # Save detailed report
        report_file = "test_report_comprehensive.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total_tests,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors
                },
                "results": self.test_results
            }, f, indent=2)
        
        logger.info(f"\nDetailed report saved to: {report_file}")


async def main():
    """Main test execution function."""
    logger.info("Starting Comprehensive Test Suite...")
    logger.info(f"Test Date/Time: {datetime.now().isoformat()}")
    
    test_suite = ComprehensiveTestSuite()
    
    try:
        await test_suite.setup()
        await test_suite.run_all_tests()
        test_suite.generate_report()
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
