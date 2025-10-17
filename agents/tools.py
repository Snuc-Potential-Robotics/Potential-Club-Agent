"""LangChain tools for the Nemo AI agent."""
from typing import Optional, Dict, Any, List
from langchain.tools import tool
from database.supabase_client import get_supabase_client
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


def classify_event(event_date: datetime, current_time: datetime) -> Dict[str, Any]:
    """
    Classify an event based on its date relative to current time.
    
    Returns:
        Dict with classification: status (completed/ongoing/upcoming), is_today, days_until/days_ago
    """
    # Normalize both dates to start of day for comparison
    event_day = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
    current_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    days_diff = (event_day - current_day).days
    
    # Check if event is today
    is_today = days_diff == 0
    
    # Classify event status
    if days_diff < 0:
        status = "completed"
        time_description = f"{abs(days_diff)} day(s) ago"
    elif days_diff == 0:
        # Event is today - check if it's still ongoing or completed based on time
        if event_date < current_time:
            status = "completed"
            time_description = "earlier today"
        else:
            status = "ongoing"
            time_description = "today"
    else:
        status = "upcoming"
        time_description = f"in {days_diff} day(s)"
    
    return {
        "status": status,
        "is_today": is_today,
        "days_difference": days_diff,
        "time_description": time_description,
        "can_register": status in ["upcoming", "ongoing"],
        "can_give_feedback": status == "ongoing" or (status == "completed" and days_diff >= -7)  # Can give feedback for events up to 7 days old
    }


def extract_student_details_from_message(message: str) -> Dict[str, str]:
    """
    Extract student details (class, section, year) from a raw message.
    
    Handles patterns like:
    - "IoT A 2024"
    - "AIDS B 2025" 
    - "Cyber A 2023"
    - "Class: IoT, Section: A, Year: 2024"
    - "john@nit.ac.in, 9876543210, IoT A 2024"
    """
    import re
    
    result = {}
    
    # Convert to string and clean
    text = str(message).strip()
    
    # Pattern 1: Direct class/section/year pattern (most common)
    # Look for pattern like "IoT A 2024", "AIDS B 2025", "Cyber A 2023"
    class_pattern = re.search(r'\b(IoT|AIDS|Cyber)\s+([AB])\s+(202[3-6])\b', text, re.IGNORECASE)
    if class_pattern:
        result["user_class"] = class_pattern.group(1)
        if result["user_class"].upper() == "IOT":
            result["user_class"] = "IoT"
        result["user_section"] = class_pattern.group(2).upper()
        result["user_year"] = class_pattern.group(3)
        return result
    
    # Pattern 2: Separated by commas - "IoT, A, 2024"
    comma_pattern = re.search(r'\b(IoT|AIDS|Cyber)\s*,\s*([AB])\s*,\s*(202[3-6])\b', text, re.IGNORECASE)
    if comma_pattern:
        result["user_class"] = comma_pattern.group(1)
        if result["user_class"].upper() == "IOT":
            result["user_class"] = "IoT"
        result["user_section"] = comma_pattern.group(2).upper()
        result["user_year"] = comma_pattern.group(3)
        return result
    
    # Pattern 3: Look for individual components if grouped pattern doesn't work
    # Extract class
    class_match = re.search(r'\b(IoT|AIDS|Cyber)\b', text, re.IGNORECASE)
    if class_match:
        result["user_class"] = class_match.group(1)
        if result["user_class"].upper() == "IOT":
            result["user_class"] = "IoT"
    
    # Extract section
    section_match = re.search(r'\b([AB])\b', text)
    if section_match:
        result["user_section"] = section_match.group(1).upper()
    
    # Extract year
    year_match = re.search(r'\b(202[3-6])\b', text)
    if year_match:
        result["user_year"] = year_match.group(1)
    
    return result


@tool
async def parse_registration_message(raw_message: str) -> str:
    """
    Parse a registration message to extract structured data.
    
    Use this tool when user provides registration info in natural language.
    
    Input: Raw user message like "Register for abc - John Doe, john@nit.ac.in, 9876543210, IoT A 2024"
    
    Output: JSON with extracted fields ready for register_for_event_by_name
    """
    import re
    
    result = {}
    message = raw_message.strip()
    
    # Extract event name (everything before the dash or extract from "register for X")
    if " - " in message:
        parts = message.split(" - ", 1)
        # Look for registration words in first part
        event_match = re.search(r'(?:register|signup|sign up)\s+(?:for\s+)?(.+)', parts[0], re.IGNORECASE)
        if event_match:
            result["event_name"] = event_match.group(1).strip()
        else:
            result["event_name"] = parts[0].strip()
        
        # Parse the user details from the second part
        user_details = parts[1].strip()
    else:
        # Try other formats
        event_match = re.search(r'(?:register|signup|sign up)\s+(?:for\s+)?([^.]+?)(?:\.|,|Name:|Email:)', message, re.IGNORECASE)
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
        if word and not word.upper() in ["IOT", "AIDS", "CYBER", "A", "B"] and not word.isdigit() and len(word) > 1:
            name_words.append(word)
        else:
            break  # Stop at first non-name word
    
    if name_words:
        result["user_name"] = " ".join(name_words)
    
    # Extract class, section, year pattern
    student_details = extract_student_details_from_message(user_details)
    result.update(student_details)
    
    return json.dumps({
        "success": True,
        "extracted_data": result,
        "message": "Extracted registration information successfully",
        "next_step": "Use register_for_event_by_name with this extracted data"
    })


@tool
async def get_upcoming_events(query: str = "{}") -> str:
    """
    Get events from the database with intelligent filtering.
    
    Input should be a JSON string with optional parameters:
    - {} or {"type": "upcoming"} - Shows only upcoming events and today's events (DEFAULT)
    - {"type": "today"} - Shows only today's events
    - {"type": "completed"} - Shows only completed/past events
    - {"type": "all"} - Shows all events regardless of date
    - {"limit": 10} - Limits number of results (default: 20)
    - {"category": "robotics"} - Filters by category
    
    Examples:
    - "Show upcoming events" → use {}
    - "What events are happening today?" → use {"type": "today"}
    - "Show all events" → use {"type": "all"}
    """
    try:
        # Parse input parameters
        params = json.loads(query) if query and query != "{}" else {}
        limit = params.get("limit", 20)
        event_type = params.get("type", "upcoming")  # upcoming, today, completed, all
        category = params.get("category")
        
        db = get_supabase_client()
        current_time = datetime.now()
        
        # Fetch all active events (we'll filter by date ourselves)
        events = await db.fetch_events(limit=100, date_from=None, only_active=True)
        
        if not events:
            return json.dumps({
                "success": True,
                "message": "No events found in the database",
                "events": [],
                "query_type": event_type
            })
        
        # Format and classify events
        formatted_events = []
        
        for event in events:
            try:
                # Parse event date
                event_date_str = event['date']
                if event_date_str.endswith('+00:00') or 'Z' in event_date_str:
                    event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                    event_date = event_date.replace(tzinfo=None)
                else:
                    event_date = datetime.fromisoformat(event_date_str.split('.')[0])
                
                # Classify the event
                classification = classify_event(event_date, current_time)
                
                # Apply filtering based on event_type
                if event_type == "upcoming" and classification["status"] not in ["upcoming", "ongoing"]:
                    continue
                elif event_type == "today" and not classification["is_today"]:
                    continue
                elif event_type == "completed" and classification["status"] != "completed":
                    continue
                # "all" type includes everything
                
                # Apply category filter if specified
                if category and event.get('category', '').lower() != category.lower():
                    continue
                
                formatted_events.append({
                    "id": event['id'],
                    "name": event['name'],
                    "date": event['date'],
                    "location": event.get('location', 'TBA'),
                    "description": event.get('description', 'No description available'),
                    "available_slots": event['available_slots'],
                    "total_slots": event['total_slots'],
                    "is_full": event['available_slots'] <= 0,
                    "category": event.get('category', 'general'),
                    # Classification info
                    "event_status": classification["status"],
                    "is_today": classification["is_today"],
                    "time_description": classification["time_description"],
                    "can_register": classification["can_register"] and event['available_slots'] > 0,
                    "can_give_feedback": classification["can_give_feedback"]
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing event date for {event.get('name', 'unknown')}: {str(e)}")
                continue
        
        # Sort by date (ascending for upcoming, descending for completed)
        if event_type == "completed":
            formatted_events.sort(key=lambda x: x['date'], reverse=True)
        else:
            formatted_events.sort(key=lambda x: x['date'])
        
        # Apply limit
        formatted_events = formatted_events[:limit]
        
        # Create appropriate message
        if not formatted_events:
            if event_type == "upcoming":
                message = "No upcoming events found at the moment."
            elif event_type == "today":
                message = "No events are happening today."
            elif event_type == "completed":
                message = "No completed events found."
            else:
                message = "No events found matching your criteria."
        else:
            if event_type == "upcoming":
                message = f"Found {len(formatted_events)} upcoming event(s)"
            elif event_type == "today":
                message = f"Found {len(formatted_events)} event(s) happening today"
            elif event_type == "completed":
                message = f"Found {len(formatted_events)} completed event(s)"
            else:
                message = f"Found {len(formatted_events)} event(s)"
        
        logger.info(f"Retrieved {len(formatted_events)} events (type: {event_type})")
        return json.dumps({
            "success": True,
            "count": len(formatted_events),
            "events": formatted_events,
            "message": message,
            "query_type": event_type,
            "current_date": current_time.isoformat()
        })
        
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "error": "Invalid JSON input. Expected format: {\"type\": \"upcoming|today|completed|all\", \"limit\": 10, \"category\": \"robotics\"}"
        })
    except Exception as e:
        logger.error(f"Error in get_upcoming_events: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to retrieve events: {str(e)}"
        })


@tool
async def search_events_by_name(query: str) -> str:
    """
    Search for events by name, partial name, keyword, or category.
    Input should be the event name, keyword, or search term as a string.
    
    This tool searches in:
    - Event name/title
    - Event description
    - Event category
    
    Examples:
    - "robotics" → finds all robotics-related events
    - "workshop" → finds all workshops
    - "soccer" → finds soccer competitions
    """
    try:
        if not query or query.strip() == "":
            return json.dumps({
                "success": False,
                "error": "Please provide an event name or keyword to search for"
            })
        
        db = get_supabase_client()
        current_time = datetime.now()
        
        # Get all events and search by name, description, and category
        events = await db.fetch_events(limit=100, date_from=None, only_active=True)
        
        # Search for events that match the query (case-insensitive, multi-field search)
        search_term = query.lower().strip()
        search_words = search_term.split()  # Split into words for better matching
        matching_events = []
        
        for event in events:
            event_name = event['name'].lower()
            event_desc = (event.get('description') or '').lower()
            event_category = (event.get('category') or '').lower()
            
            # Check if search term matches in name, description, or category
            matches = False
            
            # Exact or partial match in name
            if search_term in event_name or event_name in search_term:
                matches = True
            # Match in description
            elif search_term in event_desc:
                matches = True
            # Match in category
            elif search_term in event_category:
                matches = True
            # Check if all search words appear somewhere
            elif all(word in event_name or word in event_desc or word in event_category 
                    for word in search_words):
                matches = True
            
            if not matches:
                continue
            
            try:
                # Parse event date
                event_date_str = event['date']
                if event_date_str.endswith('+00:00') or 'Z' in event_date_str:
                    event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                    event_date = event_date.replace(tzinfo=None)
                else:
                    event_date = datetime.fromisoformat(event_date_str.split('.')[0])
                
                # Classify the event
                classification = classify_event(event_date, current_time)
                
                matching_events.append({
                    "id": event['id'],
                    "name": event['name'],
                    "date": event['date'],
                    "location": event.get('location', 'TBA'),
                    "description": event.get('description', 'No description available'),
                    "available_slots": event['available_slots'],
                    "total_slots": event['total_slots'],
                    "is_full": event['available_slots'] <= 0,
                    "category": event.get('category', 'general'),
                    # Classification info
                    "event_status": classification["status"],
                    "is_today": classification["is_today"],
                    "time_description": classification["time_description"],
                    "can_register": classification["can_register"] and event['available_slots'] > 0,
                    "can_give_feedback": classification["can_give_feedback"]
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing event date for {event.get('name', 'unknown')}: {str(e)}")
                continue
        
        if not matching_events:
            return json.dumps({
                "success": True,
                "message": f"No events found matching '{query}'",
                "events": [],
                "search_term": query,
                "suggestion": "Try searching with different keywords or check all available events"
            })
        
        # Sort by relevance (upcoming first, then by date)
        matching_events.sort(key=lambda x: (
            0 if x['event_status'] == 'ongoing' else 1 if x['event_status'] == 'upcoming' else 2,
            x['date']
        ))
        
        logger.info(f"Found {len(matching_events)} events matching '{query}'")
        return json.dumps({
            "success": True,
            "count": len(matching_events),
            "events": matching_events,
            "search_term": query,
            "current_date": current_time.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in search_events_by_name: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to search events: {str(e)}"
        })


@tool
async def get_event_details(event_id: str) -> str:
    """
    Get detailed information about a specific event by its ID.
    Input should be the event UUID as a string.
    
    Returns comprehensive event information including:
    - Event details (name, description, location, date)
    - Registration status (available slots, whether event is full)
    - Event timing status (upcoming, ongoing, completed)
    - What actions user can take (register, give feedback)
    """
    try:
        db = get_supabase_client()
        event = await db.fetch_event_by_id(event_id)
        
        if not event:
            return json.dumps({
                "success": False,
                "error": "Event not found"
            })
        
        current_time = datetime.now()
        
        # Parse event date and classify
        try:
            event_date_str = event['date']
            if event_date_str.endswith('+00:00') or 'Z' in event_date_str:
                event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                event_date = event_date.replace(tzinfo=None)
            else:
                event_date = datetime.fromisoformat(event_date_str.split('.')[0])
            
            classification = classify_event(event_date, current_time)
        except (ValueError, TypeError):
            # Default classification if date parsing fails
            classification = {
                "status": "unknown",
                "is_today": False,
                "time_description": "unknown",
                "can_register": False,
                "can_give_feedback": False
            }
        
        logger.info(f"Retrieved details for event {event_id}")
        return json.dumps({
            "success": True,
            "event": {
                "id": event['id'],
                "name": event['name'],
                "description": event.get('description', 'No description available'),
                "date": event['date'],
                "location": event.get('location', 'TBA'),
                "available_slots": event['available_slots'],
                "total_slots": event['total_slots'],
                "is_full": event['available_slots'] <= 0,
                "is_active": event['is_active'],
                "category": event.get('category', 'general'),
                # Classification info
                "event_status": classification["status"],
                "is_today": classification["is_today"],
                "time_description": classification["time_description"],
                "can_register": classification["can_register"] and event['available_slots'] > 0,
                "can_give_feedback": classification["can_give_feedback"]
            },
            "current_date": current_time.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in get_event_details: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to retrieve event details: {str(e)}"
        })


@tool
async def register_for_event_by_name(registration_data: str) -> str:
    """
    Register a user for an event using EVENT NAME (not ID).
    
    This is the PRIMARY registration tool - use this when user mentions event name.
    
    Input must be JSON string with:
    {
        "event_name": "Workshop name or partial name",
        "user_name": "John Doe",
        "user_email": "john@example.com",
        "user_phone": "1234567890" (optional),
        "user_class": "IoT|AIDS|Cyber" (optional),
        "user_section": "A|B" (optional),
        "user_year": "2023|2024|2025|2026" (optional)
    }
    
    IMPORTANT VALIDATION:
    - Searches for event by name (case-insensitive, partial match)
    - Users can ONLY register for UPCOMING events or events happening TODAY
    - Users CANNOT register for COMPLETED/PAST events
    - Collects additional student details (class, section, year)
    
    Examples:
    - {"event_name": "abc", "user_name": "John", "user_email": "john@nit.ac.in", "user_class": "IoT", "user_section": "A", "user_year": "2024"}
    - {"event_name": "robotics workshop", "user_name": "Jane", "user_email": "jane@nit.ac.in"}
    """
    try:
        # Parse input
        data = json.loads(registration_data)
        
        # DEBUG: Log what the agent sent us
        logger.info(f"🔍 DEBUG - Agent sent registration_data: {registration_data}")
        logger.info(f"🔍 DEBUG - Parsed data: {data}")
        
        # SMART FALLBACK: If student details are missing but might be in the original message,
        # try to extract them from a raw_message field or improve existing data
        if "raw_message" in data and not all(k in data for k in ["user_class", "user_section", "user_year"]):
            extracted = extract_student_details_from_message(data["raw_message"])
            # Only add if not already present
            for key, value in extracted.items():
                if key not in data and value:
                    data[key] = value
        
        # AGGRESSIVE FALLBACK: Try to extract from ALL fields if student details are still missing
        if not all(k in data and data[k] for k in ["user_class", "user_section", "user_year"]):
            # Create a combined text from all available fields to search for patterns
            search_text = ""
            for field in ["user_name", "user_email", "user_phone", "event_name", "raw_message"]:
                if field in data and data[field]:
                    search_text += str(data[field]) + " "
            
            logger.info(f"🔍 DEBUG - Searching for student details in: {search_text}")
            
            # Try to extract from combined text
            if search_text.strip():
                extracted = extract_student_details_from_message(search_text)
                logger.info(f"🔍 DEBUG - Extracted student details: {extracted}")
                
                # Add any extracted details that are missing
                for key, value in extracted.items():
                    if not data.get(key) and value:
                        data[key] = value
                        logger.info(f"🔍 DEBUG - Added {key}: {value}")
        
        # ENHANCED PARSING: Try to extract student details from user_name or other fields if they contain extra info
        if not data.get("user_class") and "user_name" in data:
            # Check if user_name contains extra info like "John Doe IoT A 2024"
            name_parts = data["user_name"].split()
            if len(name_parts) >= 4:  # Name + Class + Section + Year
                # Look for class pattern in name
                import re
                class_match = None
                for i, part in enumerate(name_parts):
                    if part.upper() in ["IOT", "AIDS", "CYBER"]:
                        class_match = i
                        break
                
                if class_match and class_match + 2 < len(name_parts):
                    # Extract class, section, year from name
                    data["user_class"] = name_parts[class_match]
                    data["user_section"] = name_parts[class_match + 1].upper()
                    data["user_year"] = name_parts[class_match + 2]
                    # Clean the name to remove the extracted parts
                    data["user_name"] = " ".join(name_parts[:class_match]).strip()
        
        # Validate required fields
        required_fields = ["event_name", "user_name", "user_email"]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return json.dumps({
                "success": False,
                "error": f"Missing required information: {', '.join(missing_fields)}",
                "required": {
                    "event_name": "Name of the event you want to register for",
                    "user_name": "Your full name",
                    "user_email": "Your email address"
                },
                "optional": {
                    "user_phone": "Your phone number",
                    "user_class": "Your class (IoT, AIDS, or Cyber)",
                    "user_section": "Your section (A or B)",
                    "user_year": "Your year (2023, 2024, 2025, or 2026)"
                }
            })
        
        db = get_supabase_client()
        current_time = datetime.now()
        
        # Search for the event by name
        event_name = data["event_name"].strip()
        events = await db.fetch_events(limit=100, date_from=None, only_active=True)
        
        # Find matching events (case-insensitive, partial match)
        search_term = event_name.lower()
        matching_events = []
        
        for event in events:
            if search_term in event['name'].lower():
                # Parse and classify the event
                try:
                    event_date_str = event['date']
                    if event_date_str.endswith('+00:00') or 'Z' in event_date_str:
                        event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                        event_date = event_date.replace(tzinfo=None)
                    else:
                        event_date = datetime.fromisoformat(event_date_str.split('.')[0])
                    
                    classification = classify_event(event_date, current_time)
                    
                    # Only include events that can be registered for
                    if classification["can_register"] and event['available_slots'] > 0:
                        matching_events.append({
                            "event": event,
                            "classification": classification
                        })
                except (ValueError, TypeError):
                    continue
        
        # Handle no matches
        if not matching_events:
            return json.dumps({
                "success": False,
                "error": f"No available events found matching '{event_name}'",
                "message": "The event might be completed, full, or doesn't exist. Please check the event name.",
                "suggestion": "Use search or list upcoming events to see available events."
            })
        
        # If multiple matches, use the first one (or ask user to be more specific)
        if len(matching_events) > 1:
            event_list = [{"name": e["event"]["name"], "date": e["event"]["date"]} for e in matching_events]
            return json.dumps({
                "success": False,
                "error": "Multiple events found matching your search",
                "matches": event_list,
                "message": "Please specify which event you want to register for by providing the exact name."
            })
        
        # Found exactly one match - proceed with registration
        selected = matching_events[0]
        event = selected["event"]
        classification = selected["classification"]
        event_id = event['id']
        
        # Prepare registration data with additional fields
        registration_info = {
            'event_id': event_id,
            'user_name': data["user_name"],
            'user_email': data["user_email"],
            'user_phone': data.get("user_phone"),
            'user_class': data.get("user_class"),
            'user_section': data.get("user_section"),
            'user_year': data.get("user_year")
        }
        
        # Create registration
        registration = await db.create_registration(**registration_info)
        
        logger.info(f"Registered {data['user_email']} for event {event_id} ({event['name']})")
        
        return json.dumps({
            "success": True,
            "message": f"✅ Successfully registered {data['user_name']} for {event['name']}!",
            "registration": {
                "id": registration['id'],
                "event_id": event_id,
                "event_name": event['name'],
                "event_date": event['date'],
                "event_location": event.get('location', 'TBA'),
                "user_name": registration['user_name'],
                "user_email": registration['user_email'],
                "user_class": registration.get('user_class'),
                "user_section": registration.get('user_section'),
                "user_year": registration.get('user_year'),
                "status": registration['status']
            },
            "event_timing": classification["time_description"],
            "available_slots_remaining": event['available_slots'] - 1
        })
        
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "error": "Invalid input format",
            "expected_format": {
                "event_name": "Event name",
                "user_name": "Your name",
                "user_email": "Your email",
                "user_phone": "Your phone (optional)",
                "user_class": "IoT/AIDS/Cyber (optional)",
                "user_section": "A/B (optional)",
                "user_year": "2023/2024/2025/2026 (optional)"
            }
        })
    except ValueError as ve:
        logger.warning(f"Registration validation error: {str(ve)}")
        return json.dumps({
            "success": False,
            "error": str(ve)
        })
    except Exception as e:
        logger.error(f"Error in register_for_event_by_name: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to register for event: {str(e)}"
        })


@tool
async def register_for_event(registration_data: str) -> str:
    """
    Register a user for an event using EVENT ID (UUID).
    
    ⚠️ DEPRECATED: Use register_for_event_by_name instead for better UX.
    This tool requires exact UUID which users don't typically have.
    
    Input must be JSON string like: 
    {"event_id": "uuid", "user_name": "John Doe", "user_email": "john@example.com", "user_phone": "optional"}
    """
    try:
        # Parse input
        data = json.loads(registration_data)
        
        # Validate required fields
        required_fields = ["event_id", "user_name", "user_email"]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return json.dumps({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            })
        
        db = get_supabase_client()
        current_time = datetime.now()
        
        # First, get event details to check if registration is allowed
        event = await db.fetch_event_by_id(data["event_id"])
        if not event:
            return json.dumps({
                "success": False,
                "error": "Event not found"
            })
        
        # Parse event date and classify
        try:
            event_date_str = event['date']
            if event_date_str.endswith('+00:00') or 'Z' in event_date_str:
                event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                event_date = event_date.replace(tzinfo=None)
            else:
                event_date = datetime.fromisoformat(event_date_str.split('.')[0])
            
            classification = classify_event(event_date, current_time)
            
            # Check if registration is allowed
            if not classification["can_register"]:
                if classification["status"] == "completed":
                    return json.dumps({
                        "success": False,
                        "error": f"Cannot register for completed events. This event took place {classification['time_description']}.",
                        "event_name": event['name'],
                        "event_status": "completed"
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": "Registration is not available for this event at this time.",
                        "event_name": event['name'],
                        "event_status": classification["status"]
                    })
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing event date for registration check: {str(e)}")
            # If we can't parse date, don't allow registration to be safe
            return json.dumps({
                "success": False,
                "error": "Unable to verify event timing. Please try again later."
            })
        
        # Check available slots
        if event['available_slots'] <= 0:
            return json.dumps({
                "success": False,
                "error": "Event is full. No available slots remaining.",
                "event_name": event['name']
            })
        
        # Proceed with registration
        registration = await db.create_registration(
            event_id=data["event_id"],
            user_name=data["user_name"],
            user_email=data["user_email"],
            user_phone=data.get("user_phone")
        )
        
        logger.info(f"Registered {data['user_email']} for event {data['event_id']}")
        return json.dumps({
            "success": True,
            "message": f"Successfully registered {data['user_name']} for {event['name']}!",
            "registration": {
                "id": registration['id'],
                "event_id": registration['event_id'],
                "event_name": event['name'],
                "event_date": event['date'],
                "user_name": registration['user_name'],
                "user_email": registration['user_email'],
                "status": registration['status']
            },
            "event_timing": classification["time_description"]
        })
        
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "error": "Invalid JSON input. Expected format: {\"event_id\": \"...\", \"user_name\": \"...\", \"user_email\": \"...\"}"
        })
    except ValueError as ve:
        logger.warning(f"Registration validation error: {str(ve)}")
        return json.dumps({
            "success": False,
            "error": str(ve)
        })
    except Exception as e:
        logger.error(f"Error in register_for_event: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to register for event: {str(e)}"
        })




@tool
async def submit_feedback_by_event_name(feedback_data: str) -> str:
    """
    Submit feedback for an event using EVENT NAME (not ID).
    
    This is the PRIMARY feedback tool - use this when user mentions event name.
    
    Input must be JSON string with:
    {
        "event_name": "Event name or partial name",
        "user_email": "user@example.com",
        "rating": 5,  // 1-5 stars
        "comments": "Great event!" (optional)
    }
    
    IMPORTANT VALIDATION:
    - Searches for event by name (case-insensitive, partial match)
    - Users can ONLY give feedback for events that are happening TODAY or recently COMPLETED (within 7 days)
    - Users CANNOT give feedback for UPCOMING events (not yet happened)
    - Users CANNOT give feedback for events completed more than 7 days ago
    - Rating must be between 1 and 5
    
    Examples:
    - {"event_name": "abc", "user_email": "john@nit.ac.in", "rating": 5, "comments": "Excellent workshop!"}
    - {"event_name": "robotics workshop", "user_email": "jane@nit.ac.in", "rating": 4}
    """
    try:
        # Parse input
        data = json.loads(feedback_data)
        
        # Validate required fields
        required_fields = ["event_name", "user_email", "rating"]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return json.dumps({
                "success": False,
                "error": f"Missing required information: {', '.join(missing_fields)}",
                "required": {
                    "event_name": "Name of the event you want to give feedback for",
                    "user_email": "Your email address",
                    "rating": "Your rating (1-5 stars)"
                },
                "optional": {
                    "comments": "Your detailed feedback or comments"
                }
            })
        
        rating = int(data["rating"])
        
        # Validate rating
        if not 1 <= rating <= 5:
            return json.dumps({
                "success": False,
                "error": "Rating must be between 1 and 5 stars"
            })
        
        db = get_supabase_client()
        current_time = datetime.now()
        
        # Search for the event by name
        event_name = data["event_name"].strip()
        events = await db.fetch_events(limit=100, date_from=None, only_active=True)
        
        # Find matching events (case-insensitive, partial match)
        search_term = event_name.lower()
        matching_events = []
        
        for event in events:
            if search_term in event['name'].lower():
                # Parse and classify the event
                try:
                    event_date_str = event['date']
                    if event_date_str.endswith('+00:00') or 'Z' in event_date_str:
                        event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                        event_date = event_date.replace(tzinfo=None)
                    else:
                        event_date = datetime.fromisoformat(event_date_str.split('.')[0])
                    
                    classification = classify_event(event_date, current_time)
                    
                    # Only include events that can receive feedback
                    if classification["can_give_feedback"]:
                        matching_events.append({
                            "event": event,
                            "classification": classification
                        })
                except (ValueError, TypeError):
                    continue
        
        # Handle no matches
        if not matching_events:
            return json.dumps({
                "success": False,
                "error": f"No events found matching '{event_name}' that can receive feedback",
                "message": "You can only give feedback for events happening today or recently completed (within 7 days).",
                "suggestion": "Check the event name or wait until the event happens."
            })
        
        # If multiple matches, use the most recent one that can receive feedback
        if len(matching_events) > 1:
            # Sort by date descending (most recent first)
            matching_events.sort(key=lambda x: x["event"]["date"], reverse=True)
            event_list = [{"name": e["event"]["name"], "date": e["event"]["date"], "status": e["classification"]["status"]} for e in matching_events]
            
            return json.dumps({
                "success": False,
                "error": "Multiple events found matching your search",
                "matches": event_list,
                "message": "Please specify which event you want to give feedback for by providing the exact name or date."
            })
        
        # Found exactly one match - proceed with feedback
        selected = matching_events[0]
        event = selected["event"]
        classification = selected["classification"]
        event_id = event['id']
        
        # Create feedback
        feedback = await db.create_feedback(
            event_id=event_id,
            user_email=data["user_email"],
            rating=rating,
            comments=data.get("comments")
        )
        
        logger.info(f"Feedback submitted by {data['user_email']} for event {event_id} ({event['name']})")
        
        return json.dumps({
            "success": True,
            "message": f"✅ Thank you for your feedback on {event['name']}!",
            "feedback": {
                "id": feedback['id'],
                "event_name": event['name'],
                "event_date": event['date'],
                "rating": feedback['rating'],
                "comments": feedback.get('comments'),
                "submitted_at": feedback.get('submitted_at', current_time.isoformat())
            },
            "rating_display": "⭐" * rating
        })
        
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "error": "Invalid input format",
            "expected_format": {
                "event_name": "Event name",
                "user_email": "Your email",
                "rating": "1-5 stars",
                "comments": "Your feedback (optional)"
            }
        })
    except ValueError as ve:
        logger.warning(f"Feedback validation error: {str(ve)}")
        return json.dumps({
            "success": False,
            "error": str(ve)
        })
    except Exception as e:
        logger.error(f"Error in submit_feedback_by_event_name: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to submit feedback: {str(e)}"
        })


@tool
async def submit_feedback(feedback_data: str) -> str:
    """
    Submit feedback for an event using EVENT ID (UUID).
    
    ⚠️ DEPRECATED: Use submit_feedback_by_event_name instead for better UX.
    This tool requires exact UUID which users don't typically have.
    
    IMPORTANT VALIDATION:
    - Users can ONLY give feedback for events that are happening TODAY or recently COMPLETED (within 7 days)
    - Users CANNOT give feedback for UPCOMING events (not yet happened)
    - Users CANNOT give feedback for events completed more than 7 days ago
    
    Input must be JSON string like: 
    {"event_id": "uuid", "user_email": "user@example.com", "rating": 5, "comments": "optional"}
    Rating must be between 1 and 5.
    """
    try:
        # Parse input
        data = json.loads(feedback_data)
        
        # Validate required fields
        required_fields = ["event_id", "user_email", "rating"]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return json.dumps({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            })
        
        rating = int(data["rating"])
        
        # Validate rating
        if not 1 <= rating <= 5:
            return json.dumps({
                "success": False,
                "error": "Rating must be between 1 and 5"
            })
        
        db = get_supabase_client()
        current_time = datetime.now()
        
        # Get event details to check if feedback is allowed
        event = await db.fetch_event_by_id(data["event_id"])
        if not event:
            return json.dumps({
                "success": False,
                "error": "Event not found"
            })
        
        # Parse event date and classify
        try:
            event_date_str = event['date']
            if event_date_str.endswith('+00:00') or 'Z' in event_date_str:
                event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                event_date = event_date.replace(tzinfo=None)
            else:
                event_date = datetime.fromisoformat(event_date_str.split('.')[0])
            
            classification = classify_event(event_date, current_time)
            
            # Check if feedback is allowed
            if not classification["can_give_feedback"]:
                if classification["status"] == "upcoming":
                    return json.dumps({
                        "success": False,
                        "error": f"Cannot submit feedback for upcoming events. This event is scheduled {classification['time_description']}. Please wait until the event happens.",
                        "event_name": event['name'],
                        "event_status": "upcoming",
                        "event_date": event['date']
                    })
                elif classification["status"] == "completed" and classification["days_difference"] < -7:
                    return json.dumps({
                        "success": False,
                        "error": f"Feedback period has ended. This event took place {classification['time_description']} (more than 7 days ago).",
                        "event_name": event['name'],
                        "event_status": "completed"
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": "Feedback is not available for this event at this time.",
                        "event_name": event['name'],
                        "event_status": classification["status"]
                    })
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing event date for feedback check: {str(e)}")
            return json.dumps({
                "success": False,
                "error": "Unable to verify event timing. Please try again later."
            })
        
        # Proceed with feedback submission
        feedback = await db.create_feedback(
            event_id=data["event_id"],
            user_email=data["user_email"],
            rating=rating,
            comments=data.get("comments")
        )
        
        logger.info(f"Feedback submitted by {data['user_email']} for event {data['event_id']}")
        return json.dumps({
            "success": True,
            "message": f"Thank you for your feedback on {event['name']}!",
            "feedback": {
                "id": feedback['id'],
                "event_name": event['name'],
                "rating": feedback['rating'],
                "submitted_at": feedback.get('submitted_at', current_time.isoformat())
            }
        })
        
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "error": "Invalid JSON input. Expected format: {\"event_id\": \"...\", \"user_email\": \"...\", \"rating\": 5}"
        })
    except ValueError as ve:
        logger.warning(f"Feedback validation error: {str(ve)}")
        return json.dumps({
            "success": False,
            "error": str(ve)
        })
    except Exception as e:
        logger.error(f"Error in submit_feedback: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to submit feedback: {str(e)}"
        })


@tool
async def check_registration_status(query: str) -> str:
    """Check if a user is registered for an event. Input must be JSON string like: {"event_id": "uuid", "user_email": "user@example.com"}"""
    try:
        # Parse input
        data = json.loads(query)
        
        # Validate required fields
        required_fields = ["event_id", "user_email"]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return json.dumps({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            })
        
        db = get_supabase_client()
        registration = await db.check_user_registration(data["event_id"], data["user_email"])
        
        if registration:
            logger.info(f"User {data['user_email']} is registered for event {data['event_id']}")
            return json.dumps({
                "success": True,
                "is_registered": True,
                "registration": {
                    "id": registration['id'],
                    "user_name": registration['user_name'],
                    "registration_date": registration['registration_date'],
                    "status": registration['status']
                }
            })
        else:
            logger.info(f"User {data['user_email']} is not registered for event {data['event_id']}")
            return json.dumps({
                "success": True,
                "is_registered": False,
                "message": "You are not registered for this event"
            })
        
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "error": "Invalid JSON input. Expected format: {\"event_id\": \"...\", \"user_email\": \"...\"}"
        })
    except Exception as e:
        logger.error(f"Error in check_registration_status: {str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to check registration status: {str(e)}"
        })


def get_agent_tools() -> List:
    """
    Get all available tools for the agent.
    
    Returns:
        List of LangChain tools
    """
    return [
        get_upcoming_events,
        search_events_by_name,
        get_event_details,
        parse_registration_message,  # HELPER - Parse natural language registration
        register_for_event_by_name,  # PRIMARY - Use event name
        submit_feedback_by_event_name,  # PRIMARY - Use event name
        register_for_event,  # Legacy - Use UUID
        submit_feedback,  # Legacy - Use UUID
        check_registration_status,
    ]
