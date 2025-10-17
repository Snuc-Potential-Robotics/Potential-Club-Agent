# Nemo AI Assistant - Backend

FastAPI backend for Nemo, an AI-powered assistant for club management using LangChain, LangGraph, and Google Gemini 2.5 Flash.

## Features

- 🤖 AI-powered conversation agent using Google Gemini
- 🔧 LangChain tools for event management
- 🔌 WebSocket support for real-time chat
- 🗄️ PostgreSQL database via Supabase
- 📝 Comprehensive logging and error handling
- 🔒 Input validation with Pydantic
- ⚡ Async/await for optimal performance

## Prerequisites

- Python 3.9+
- Supabase account
- Google AI Studio API key

## Installation

### 1. Create Virtual Environment

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
.\venv\Scripts\Activate

# On Linux/Mac
# source venv/bin/activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GOOGLE_API_KEY=your_gemini_api_key
ENVIRONMENT=development
```

### 4. Set Up Database

Run the SQL migrations in your Supabase SQL Editor (see `database_schema.sql`).

## Running the Server

### Development Mode (with auto-reload)

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### REST Endpoints

#### Health Check
```http
GET /health
```

#### Chat (REST fallback)
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Show me upcoming events",
  "session_id": "optional-session-id"
}
```

#### Get Session History
```http
GET /api/sessions/{session_id}/history
```

#### Clear Session
```http
DELETE /api/sessions/{session_id}
```

### WebSocket Endpoint

```
ws://localhost:8000/ws/chat/{session_id}
```

**Message Format:**

Incoming (from client):
```json
{
  "type": "message",
  "content": "Show upcoming events"
}
```

Outgoing (to client):
```json
{
  "type": "response",
  "content": "I found 3 upcoming events...",
  "suggestions": ["Register for event", "Show more details"],
  "timestamp": "2025-10-04T10:30:00Z"
}
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── agents/
│   ├── __init__.py
│   ├── nemo_agent.py      # Main AI agent logic
│   └── tools.py           # LangChain tools
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic models
├── database/
│   ├── __init__.py
│   └── supabase_client.py # Database client
└── config/
    ├── __init__.py
    └── settings.py        # Configuration management
```

## Agent Capabilities

Nemo can help users with:

1. **Event Queries**
   - Show upcoming events
   - Get event details
   - Check event availability

2. **Event Registration**
   - Register users for events
   - Collect name, email, phone
   - Confirm registration status

3. **Feedback Collection**
   - Submit event feedback
   - Rate events (1-5 stars)
   - Add comments

4. **Status Checks**
   - Check registration status
   - View user's registered events

## LangChain Tools

The agent has access to these tools:

- `get_upcoming_events`: Fetch upcoming events from database
- `get_event_details`: Get detailed info about a specific event
- `register_for_event`: Register user for an event
- `submit_feedback`: Submit feedback for completed events
- `check_registration_status`: Check if user is registered

## Testing

### Test with cURL

```powershell
# Health check
curl http://localhost:8000/health

# Send chat message
curl -X POST http://localhost:8000/api/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "Show upcoming events"}'
```

### Test WebSocket

Use a WebSocket client or the frontend application to test real-time chat.

## Logging

Logs are output to console with the following format:
```
2025-10-04 10:30:00 - nemo_agent - INFO - Processed message for session abc123
```

## Error Handling

The API includes comprehensive error handling:
- Input validation errors (400)
- Service unavailable (503)
- Internal server errors (500)
- WebSocket disconnect handling
- Database connection retries

## Security Considerations

- API keys stored in environment variables
- Input validation with Pydantic
- SQL injection prevention (parameterized queries)
- CORS configuration for allowed origins
- Rate limiting ready (configuration in settings)

## Performance Optimization

- Async/await throughout
- Connection pooling with Supabase
- Session cleanup for inactive connections
- Configurable timeouts
- Efficient message history management (last 10 messages)

## Troubleshooting

### Agent not responding
- Check Google API key is valid
- Verify internet connection
- Check logs for specific errors

### Database errors
- Verify Supabase credentials
- Check database tables exist
- Ensure RLS policies are configured

### WebSocket disconnects
- Check timeout settings
- Verify network stability
- Review connection logs

## Development Tips

1. Use `--reload` flag during development
2. Check `/docs` for interactive API documentation
3. Monitor logs for debugging
4. Test tools individually before full integration
5. Use session IDs for conversation tracking

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.
