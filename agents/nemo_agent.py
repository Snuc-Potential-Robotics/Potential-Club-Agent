"""Nemo AI Agent using LangChain and Google Gemini."""
from typing import List, Dict, Any, Optional, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from database.supabase_client import get_supabase_client
from config.settings import settings
from datetime import datetime
import logging
import json
import re

logger = logging.getLogger(__name__)


class ConversationState(TypedDict):
    """State for conversation tracking."""
    session_id: str
    messages: List[Dict[str, str]]
    intent: Optional[str]
    context: Dict[str, Any]


class NemoAgent:
    """Nemo AI Assistant Agent using LangChain and Gemini - Simplified version without complex agents."""
    
    def __init__(self):
        """Initialize the Nemo agent."""
        self.sessions: Dict[str, ConversationState] = {}
        self.llm = self._initialize_llm()
        self.db = get_supabase_client()
        logger.info("Nemo Agent initialized successfully (simplified mode)")
    
    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        """Initialize Google Gemini LLM."""
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=settings.google_api_key,
                temperature=0.7,
                max_tokens=1024,
                convert_system_message_to_human=True
            )
            logger.info("Google Gemini LLM initialized")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    async def _call_tool(self, tool_name: str, tool_input: str) -> str:
        """Call a tool with the given input."""
        try:
            # Import tools dynamically without 'backend' prefix
            from agents.tools import (
                get_upcoming_events,
                get_event_details,
                register_for_event,
                register_for_event_by_name,
                submit_feedback,
                submit_feedback_by_event_name,
                check_registration_status,
                search_events_by_name,
                parse_registration_message
            )
            
            tool_map = {
                "get_upcoming_events": get_upcoming_events,
                "get_event_details": get_event_details,
                "register_for_event": register_for_event,
                "register_for_event_by_name": register_for_event_by_name,
                "submit_feedback": submit_feedback,
                "submit_feedback_by_event_name": submit_feedback_by_event_name,
                "check_registration_status": check_registration_status,
                "search_events_by_name": search_events_by_name,
                "parse_registration_message": parse_registration_message
            }
            
            if tool_name not in tool_map:
                return f"Error: Unknown tool '{tool_name}'"
            
            tool = tool_map[tool_name]
            result = await tool.ainvoke(tool_input)
            return str(result)
        except Exception as e:
            logger.error(f"Tool call error: {str(e)}")
            return f"Error calling tool: {str(e)}"
    
    def _extract_tool_call(self, llm_response: str) -> tuple:
        """Extract tool name and input from LLM response."""
        # Look for patterns like "use get_upcoming_events with {}" or similar
        patterns = [
            r'use\s+(\w+)\s+with\s+(.+)',
            r'call\s+(\w+)\s+with\s+(.+)',
            r'invoke\s+(\w+)\s+with\s+(.+)',
            r'tool:\s*(\w+)\s*input:\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, llm_response, re.IGNORECASE)
            if match:
                tool_name = match.group(1)
                tool_input = match.group(2).strip()
                return tool_name, tool_input
        
        return None, None
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM."""
        return """You are Nemo, the friendly and intelligent AI assistant for Potential Club at SNUC.
    Built with ❤️ by students of Potential Club, you help students with robotics events, workshops, and competitions with precision and clarity.

    CURRENT DATE/TIME AWARENESS:
    Always be aware of the current date when discussing events. Events are classified as:
    - UPCOMING: Events that haven't happened yet (future dates)
    - ONGOING/TODAY: Events happening today
    - COMPLETED: Events that have already happened (past dates)

    Available Tools:

    1. get_upcoming_events - Get events with intelligent filtering
       Inputs:
       - {} or {"type": "upcoming"} - Shows ONLY upcoming and today's events (DEFAULT)
       - {"type": "today"} - Shows ONLY today's events
       - {"type": "completed"} - Shows ONLY past/completed events
       - {"type": "all"} - Shows ALL events regardless of date
       - {"limit": 10} - Limits results
       - {"category": "robotics"} - Filters by category
       
       Use when:
       - "Show upcoming events" → {"type": "upcoming"}
       - "What events are happening today?" → {"type": "today"}
       - "Show all events" → {"type": "all"}
       - "Show past events" → {"type": "completed"}

    2. search_events_by_name - Search for specific events by name or keyword
       Input: event name or keyword as string (e.g., "Robotics Workshop", "soccer", "workshop")
       Searches in: event name, description, and category
       
       Use when:
       - User mentions a specific event name
       - User asks about a particular topic (e.g., "robotics events")
       - User wants to find events related to a keyword

    3. get_event_details - Get comprehensive details about a specific event by UUID
       Input: event_id as string
       Returns: Full event info including timing status, registration availability, feedback options
       
       Use when: You have an event ID and need detailed information

    4. register_for_event_by_name - 🌟 PRIMARY REGISTRATION TOOL
       Input: {
         "event_name": "Workshop name (e.g., 'abc', 'robotics workshop')",
         "user_name": "Full name",
         "user_email": "Email address",
         "user_phone": "Phone number (optional)",
         "user_class": "IoT/AIDS/Cyber (optional)",
         "user_section": "A/B (optional)",
         "user_year": "2023/2024/2025/2026 (optional)"
       }
       
       ⭐ ALWAYS USE THIS TOOL FOR REGISTRATION - Users provide event NAME, not ID
       
       VALIDATION: Can ONLY register for upcoming events or events happening today
       CANNOT register for completed/past events
       
       Use when: User wants to register/sign up for an event
       
       SMART COLLECTION: If user provides all details in one message, use them all.
       If missing, ask for required fields (event_name, user_name, user_email).
       Optional fields can be collected for better record-keeping.

    5. submit_feedback_by_event_name - 🌟 PRIMARY FEEDBACK TOOL
       Input: {
         "event_name": "Event name (e.g., 'abc', 'robotics workshop')",
         "user_email": "Email address",
         "rating": 1-5,
         "comments": "Feedback text (optional)"
       }
       
       ⭐ ALWAYS USE THIS TOOL FOR FEEDBACK - Users provide event NAME, not ID
       
       VALIDATION: Can ONLY give feedback for:
       - Events happening TODAY
       - Recently completed events (within last 7 days)
       CANNOT give feedback for upcoming events or events completed >7 days ago
       
       Use when: User wants to provide feedback/review
       
       SMART COLLECTION: If user provides all details in one message, use them all.
       If missing, ask for required fields (event_name, user_email, rating).

    6. register_for_event - Legacy tool (USE register_for_event_by_name INSTEAD)
       Only use if you somehow have the exact UUID

    7. submit_feedback - Legacy tool (USE submit_feedback_by_event_name INSTEAD)
       Only use if you somehow have the exact UUID

    8. check_registration_status - Check if user is registered for an event
       Input: {"event_id": "uuid", "user_email": "email@example.com"}
       Use when: User wants to check their registration status

    INTELLIGENT INFORMATION COLLECTION:

    When user wants to REGISTER:

    **METHOD 1: DIRECT EXTRACTION (Preferred)**
    1. **ALWAYS extract ALL information from the first message if available**
    2. Look for patterns like "Register for abc - John Doe, john@nit.ac.in, 9876543210, IoT A 2024"
    3. **CRITICAL**: Extract student details from patterns like "IoT A 2024", "AIDS B 2025", "Cyber A 2023"
    4. **IMMEDIATELY call register_for_event_by_name with ALL extracted fields**

    **METHOD 2: PARSING TOOL (If extraction is complex)**
    1. If the message is complex, first call parse_registration_message with the raw message
    2. Then use the extracted data to call register_for_event_by_name

    **EXTRACTION RULES - FOLLOW EXACTLY:**

    From "Register for abc - John Doe, john@nit.ac.in, 9876543210, IoT A 2024":
    - event_name: "abc" 
    - user_name: "John Doe"
    - user_email: "john@nit.ac.in"
    - user_phone: "9876543210"
    - user_class: "IoT" (first word of "IoT A 2024")
    - user_section: "A" (second word of "IoT A 2024") 
    - user_year: "2024" (third word of "IoT A 2024")

    **CALL register_for_event_by_name with this JSON:**
    ```json
    {
      "event_name": "abc",
      "user_name": "John Doe", 
      "user_email": "john@nit.ac.in",
      "user_phone": "9876543210",
      "user_class": "IoT",
      "user_section": "A",
      "user_year": "2024"
    }
    ```

    RESPONSE GUIDELINES:
    - Be friendly, conversational, and helpful
    - Always validate event timing before registration or feedback
    - Extract all available information from user messages
    - Provide clear error messages when actions aren't allowed
    - When showing events, include dates and timing status

    Response Format:
    When you need to use a tool, respond EXACTLY like this:

    TOOL: tool_name
    INPUT: input_string

    Examples:
    User: "Show upcoming events"
    TOOL: get_upcoming_events
    INPUT: {"type": "upcoming"}

    User: "Register me for abc workshop, name John, email john@nit.ac.in"
    TOOL: register_for_event_by_name
    INPUT: {"event_name": "abc workshop", "user_name": "John", "user_email": "john@nit.ac.in"}

    Be friendly, helpful, and precise. Always consider current date when discussing events."""
    
    def _get_or_create_session(self, session_id: str) -> ConversationState:
        """Get existing session or create new one."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "session_id": session_id,
                "messages": [],
                "intent": None,
                "context": {}
            }
            logger.info(f"Created new session: {session_id}")
        return self.sessions[session_id]
    
    def _add_message_to_history(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """Add message to conversation history."""
        session = self._get_or_create_session(session_id)
        session["messages"].append({
            "role": role,
            "content": content
        })
        
        # Keep only last 10 messages for context
        if len(session["messages"]) > 10:
            session["messages"] = session["messages"][-10:]
    
    def _format_chat_history(self, session_id: str) -> List:
        """Format chat history for LangChain."""
        session = self._get_or_create_session(session_id)
        chat_history = []
        
        for msg in session["messages"]:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_history.append(AIMessage(content=msg["content"]))
        
        return chat_history
    
    async def process_message(
        self,
        message: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Process user message and generate response using direct LLM interaction.
        
        Args:
            message: User's message
            session_id: Session identifier
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Add user message to history
            self._add_message_to_history(session_id, "user", message)
            
            # Get chat history
            session = self._get_or_create_session(session_id)
            chat_history_str = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in session["messages"][-6:]  # Last 3 exchanges
            ])
            
            # Prepare prompt for LLM
            system_prompt = self._get_system_prompt()
            full_prompt = f"{system_prompt}\n\nConversation History:\n{chat_history_str}\n\nUser: {message}\n\nNemo:"
            
            # Get LLM response
            from langchain_core.messages import HumanMessage
            llm_response = await self.llm.ainvoke([HumanMessage(content=full_prompt)])
            response_text = llm_response.content
            
            # Check if LLM wants to use a tool
            if "TOOL:" in response_text and "INPUT:" in response_text:
                # Extract tool call
                tool_lines = response_text.split("\n")
                tool_name = None
                tool_input = None
                
                for i, line in enumerate(tool_lines):
                    if line.startswith("TOOL:"):
                        tool_name = line.replace("TOOL:", "").strip()
                    elif line.startswith("INPUT:"):
                        tool_input = line.replace("INPUT:", "").strip()
                
                if tool_name and tool_input is not None:
                    logger.info(f"Tool call detected: {tool_name} with input: {tool_input}")
                    
                    # Call the tool
                    tool_result = await self._call_tool(tool_name, tool_input)
                    
                    # Get final response from LLM with tool result
                    final_prompt = f"{system_prompt}\n\nUser asked: {message}\n\nTool {tool_name} returned:\n{tool_result}\n\nNow provide a friendly response to the user based on these results:"
                    final_response = await self.llm.ainvoke([HumanMessage(content=final_prompt)])
                    response_text = final_response.content
            
            # Add assistant response to history
            self._add_message_to_history(session_id, "assistant", response_text)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(message, response_text)
            
            logger.info(f"Processed message for session {session_id}")
            
            return {
                "response": response_text,
                "session_id": session_id,
                "suggestions": suggestions,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            error_response = (
                "I apologize, but I encountered an error processing your request. "
                "Please try again or rephrase your question."
            )
            
            self._add_message_to_history(session_id, "assistant", error_response)
            
            return {
                "response": error_response,
                "session_id": session_id,
                "suggestions": ["Show upcoming events", "Help"],
                "success": False,
                "error": str(e)
            }
    
    def _generate_suggestions(
        self,
        user_message: str,
        response: str
    ) -> List[str]:
        """Generate contextual suggestions for next user action."""
        suggestions = []
        
        user_lower = user_message.lower()
        response_lower = response.lower()
        
        # Event-related suggestions
        if any(word in user_lower for word in ["event", "workshop", "activity"]):
            if "upcoming" in response_lower or "found" in response_lower:
                suggestions.extend(["Show more details", "Register for event"])
        
        # Registration-related suggestions
        if any(word in user_lower for word in ["register", "sign up", "join"]):
            if "name" in response_lower or "email" in response_lower:
                suggestions.append("Confirm registration")
            else:
                suggestions.extend(["Show upcoming events", "Check registration status"])
        
        # Feedback-related suggestions
        if any(word in user_lower for word in ["feedback", "review", "rating"]):
            if "submitted" in response_lower or "thank" in response_lower:
                suggestions.extend(["Show upcoming events", "Register for event"])
            else:
                suggestions.append("Submit feedback")
        
        # Default suggestions
        if not suggestions:
            suggestions = [
                "Show upcoming events",
                "Register for event",
                "Submit feedback"
            ]
        
        return suggestions[:3]  # Return max 3 suggestions
    
    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session."""
        session = self._get_or_create_session(session_id)
        return session["messages"]
    
    def clear_session(self, session_id: str):
        """Clear session data."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
    
    def get_welcome_message(self) -> Dict[str, Any]:
        """Get welcome message for new users."""
        return {
            "response": (
                "Hi! 👋 I'm Nemo, Potential club assistant. I can help you with:\n\n"
                "• Finding upcoming events\n"
                "• Registering for events\n"
                "• Submitting feedback\n\n"
                "What would you like to know?"
            ),
            "suggestions": [
                "Show upcoming events",
                "How do I register?",
                "Submit feedback"
            ]
        }
