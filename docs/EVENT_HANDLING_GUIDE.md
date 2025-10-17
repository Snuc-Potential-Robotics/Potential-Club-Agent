# Event Handling System Guide

## Overview
This document describes how the Nemo AI Agent handles event-related queries with proper date/time awareness and validation.

## Event Classification System

Events are automatically classified based on their date relative to the current date/time:

### Event Status Types

1. **COMPLETED** - Events that have already happened (past dates)
   - Example: Event was on October 1, 2025 and today is October 4, 2025

2. **ONGOING/TODAY** - Events happening today
   - Example: Event is scheduled for October 4, 2025 and today is October 4, 2025

3. **UPCOMING** - Events that haven't happened yet (future dates)
   - Example: Event is on October 10, 2025 and today is October 4, 2025

## User Query Handling

### 1. Showing Events

#### "Show upcoming events"
- **Tool Used**: `get_upcoming_events` with `{"type": "upcoming"}`
- **Behavior**: Returns ONLY upcoming and today's events
- **Does NOT show**: Completed/past events

#### "What events are happening today?"
- **Tool Used**: `get_upcoming_events` with `{"type": "today"}`
- **Behavior**: Returns ONLY events scheduled for today
- **Does NOT show**: Past or future events

#### "Show all events"
- **Tool Used**: `get_upcoming_events` with `{"type": "all"}`
- **Behavior**: Returns ALL events regardless of date
- **Includes**: Past, present, and future events

#### "Show past/completed events"
- **Tool Used**: `get_upcoming_events` with `{"type": "completed"}`
- **Behavior**: Returns ONLY completed events
- **Does NOT show**: Upcoming or today's events

### 2. Searching for Specific Events

#### "Tell me about robotics workshop"
- **Tool Used**: `search_events_by_name` with query "robotics workshop"
- **Search Fields**: Event name, description, category
- **Behavior**: Returns all events matching the search term with proper classification

#### Search Features:
- Case-insensitive matching
- Partial name matching
- Description search
- Category filtering
- Multi-word query support

### 3. Event Registration

#### Registration Rules:
✅ **CAN Register For:**
- Upcoming events (future dates)
- Events happening today
- Events with available slots

❌ **CANNOT Register For:**
- Completed/past events
- Full events (no available slots)

#### Example Validation:
```
User: "I want to register for the workshop from last week"
Response: "Cannot register for completed events. This event took place 7 days ago."
```

### 4. Event Feedback

#### Feedback Rules:
✅ **CAN Give Feedback For:**
- Events happening today
- Recently completed events (within last 7 days)

❌ **CANNOT Give Feedback For:**
- Upcoming events (not yet happened)
- Events completed more than 7 days ago

#### Example Validation:
```
User: "I want to give feedback for the upcoming robotics workshop"
Response: "Cannot submit feedback for upcoming events. This event is scheduled in 5 days. 
Please wait until the event happens."
```

## Tool Reference

### 1. get_upcoming_events

**Purpose**: Retrieve events with intelligent filtering

**Input Parameters**:
```json
{
  "type": "upcoming|today|completed|all",  // Event type filter
  "limit": 10,                             // Maximum results (default: 20)
  "category": "robotics"                   // Category filter (optional)
}
```

**Response Fields**:
- `event_status`: "completed" | "ongoing" | "upcoming"
- `is_today`: boolean
- `time_description`: Human-readable timing (e.g., "in 5 days", "today", "3 days ago")
- `can_register`: boolean (based on event timing and slot availability)
- `can_give_feedback`: boolean (based on event timing rules)

### 2. search_events_by_name

**Purpose**: Search for events by name, keyword, or category

**Input**: String query (e.g., "robotics", "workshop", "soccer")

**Search Behavior**:
- Searches in event name, description, and category
- Case-insensitive
- Supports partial matching
- Multi-word queries

**Response**: Same fields as get_upcoming_events, sorted by relevance

### 3. register_for_event

**Purpose**: Register user for an event

**Input**:
```json
{
  "event_id": "uuid",
  "user_name": "John Doe",
  "user_email": "john@example.com",
  "user_phone": "1234567890"  // optional
}
```

**Validation**:
1. Event exists
2. Event is upcoming or happening today (not completed)
3. Event has available slots
4. User not already registered

### 4. submit_feedback

**Purpose**: Submit feedback for an event

**Input**:
```json
{
  "event_id": "uuid",
  "user_email": "user@example.com",
  "rating": 5,  // 1-5
  "comments": "Great event!"  // optional
}
```

**Validation**:
1. Event exists
2. Event is either:
   - Happening today, OR
   - Completed within last 7 days
3. Rating is between 1-5

## Edge Cases Handled

### 1. Empty Database
- Query: "Show upcoming events"
- Response: "No upcoming events found at the moment."

### 2. No Matching Events
- Query: "Tell me about quantum computing event"
- Response: "No events found matching 'quantum computing'. Try searching with different keywords..."

### 3. Registration for Past Event
- Query: "Can I register for last month's workshop?"
- Response: Clear error explaining registration is only for upcoming/today's events

### 4. Feedback for Future Event
- Query: "I want to give feedback for next week's event"
- Response: Clear error explaining feedback is only for today's or recently completed events

### 5. Full Event Registration
- Detects when event has no available slots
- Provides clear "Event is full" message

## Testing

Run comprehensive test suite:
```bash
cd backend
python test_comprehensive_scenarios.py
```

### Test Categories:
1. **Upcoming Events Queries** - Various ways to request upcoming events
2. **Specific Event Search** - Search by name, category, keywords
3. **Event Registration Edge Cases** - Valid and invalid registration attempts
4. **Feedback Submission Edge Cases** - Valid and invalid feedback scenarios
5. **Complex Queries** - Multi-intent and contextual queries
6. **Edge Cases and Error Handling** - Graceful handling of edge cases

## Best Practices

### For Users:
1. Be specific when asking for events (e.g., "upcoming robotics events")
2. Mention event names or keywords for better search results
3. Check event timing before attempting registration or feedback

### For Developers:
1. Always use the `classify_event()` function for event status determination
2. Validate event timing at the tool layer before database operations
3. Provide clear, user-friendly error messages
4. Include timing context in responses (e.g., "in 5 days", "3 days ago")

## Response Quality Guidelines

### Good Responses:
✅ Include event timing context
✅ Clearly state what actions user can take
✅ Provide relevant suggestions
✅ Use friendly, conversational tone
✅ Be precise about dates and availability

### Example Good Response:
```
Here are the upcoming robotics events:

1. Robo Soccer Competition
   📅 Date: October 10, 2025 (in 6 days)
   📍 Location: Main Arena
   👥 Slots: 15/30 available
   ✅ You can register for this event

2. Arduino Workshop
   📅 Date: Today (October 4, 2025)
   📍 Location: Lab 101
   👥 Slots: 5/20 available
   ✅ You can register for this event
   ✅ You can give feedback after attending
```

## Troubleshooting

### Issue: Events showing in wrong category
**Solution**: Check date parsing in `classify_event()` function

### Issue: Registration not working for today's event
**Solution**: Verify `can_register` logic includes "ongoing" status

### Issue: Agent showing past events for "upcoming" query
**Solution**: Ensure tool is called with correct `{"type": "upcoming"}` parameter

### Issue: Search not finding relevant events
**Solution**: Check if search term matches event name, description, or category fields

## Future Enhancements

1. **Time-based filtering**: Events within next 7 days, this month, etc.
2. **Category browsing**: Show all events by category
3. **User preferences**: Remember user's favorite categories
4. **Reminders**: Notify users about upcoming registered events
5. **Waitlist**: Allow joining waitlist for full events
