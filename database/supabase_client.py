"""Supabase database client for async operations."""
from supabase import create_client, Client
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Singleton Supabase client for database operations."""
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Supabase client."""
        if self._client is None:
            self._client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            logger.info("Supabase client initialized")
    
    @property
    def client(self) -> Client:
        """Get Supabase client."""
        if self._client is None:
            raise RuntimeError("Supabase client not initialized")
        return self._client
    
    async def fetch_events(
        self,
        limit: Optional[int] = None,
        date_from: Optional[datetime] = None,
        only_active: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch events from database.
        
        Args:
            limit: Maximum number of events to return
            date_from: Filter events from this date onwards (if None, shows all events)
            only_active: Only return active events (status != 'cancelled')
            
        Returns:
            List of event dictionaries
        """
        try:
            query = self.client.table('events').select('*')
            
            # Filter by status (not cancelled)
            if only_active:
                query = query.neq('status', 'cancelled')
            
            # Filter by date only if date_from is provided
            if date_from:
                query = query.gte('event_date', date_from.isoformat())
            # If no date_from is provided, show all events (past and future)
            
            # Order by event date
            query = query.order('event_date', desc=False)
            
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            
            # Transform data to match expected format
            events = []
            for event in response.data:
                events.append({
                    'id': event['id'],
                    'name': event['title'],  # Map title to name
                    'description': event['description'],
                    'date': event['event_date'],  # Map event_date to date
                    'location': event.get('location', 'TBA'),
                    'total_slots': event.get('max_participants', 0),
                    'available_slots': event.get('max_participants', 0) - event.get('current_participants', 0),
                    'is_active': event['status'] != 'cancelled',
                    'status': event['status'],
                    'category': event.get('category', 'general'),
                    'image_url': event.get('image_url'),
                    'content': event.get('content')
                })
            
            logger.info(f"Fetched {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"Error fetching events: {str(e)}")
            raise
    
    async def fetch_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch specific event by ID.
        
        Args:
            event_id: UUID of the event
            
        Returns:
            Event dictionary or None if not found
        """
        try:
            response = self.client.table('events').select('*').eq('id', event_id).execute()
            
            if response.data:
                event = response.data[0]
                # Transform to match expected format
                transformed = {
                    'id': event['id'],
                    'name': event['title'],
                    'description': event['description'],
                    'date': event['event_date'],
                    'location': event.get('location', 'TBA'),
                    'total_slots': event.get('max_participants', 0),
                    'available_slots': event.get('max_participants', 0) - event.get('current_participants', 0),
                    'is_active': event['status'] != 'cancelled',
                    'status': event['status'],
                    'category': event.get('category', 'general'),
                    'image_url': event.get('image_url'),
                    'content': event.get('content')
                }
                logger.info(f"Fetched event {event_id}")
                return transformed
            
            logger.warning(f"Event {event_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching event {event_id}: {str(e)}")
            raise
    
    async def create_registration(
        self,
        event_id: str,
        user_name: str,
        user_email: str,
        user_phone: Optional[str] = None,
        user_class: Optional[str] = None,
        user_section: Optional[str] = None,
        user_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new event registration.
        
        Args:
            event_id: UUID of the event
            user_name: Name of the user
            user_email: Email of the user
            user_phone: Phone number of the user (optional)
            user_class: Student class - IoT, AIDS, or Cyber (optional)
            user_section: Student section - A or B (optional)
            user_year: Student year - 2023, 2024, 2025, or 2026 (optional)
            
        Returns:
            Registration data dictionary
            
        Raises:
            Exception: If registration fails
        """
        try:
            # Check if event exists and has available slots
            event = await self.fetch_event_by_id(event_id)
            if not event:
                raise ValueError("Event not found")
            
            # Check available slots
            if event['available_slots'] <= 0:
                raise ValueError("Event is full. No available slots.")
            
            # Check if user already registered (if registrations table exists)
            try:
                existing = await self.check_user_registration(event_id, user_email)
                if existing:
                    raise ValueError("You are already registered for this event")
            except Exception:
                # Registrations table might not exist, continue
                pass
            
            # Create registration record (if table exists)
            # Try with new columns first, fall back to basic columns if they don't exist
            try:
                registration_data = {
                    'event_id': event_id,
                    'user_name': user_name,
                    'user_email': user_email,
                    'user_phone': user_phone,
                    'user_class': user_class,
                    'user_section': user_section,
                    'user_year': user_year,
                    'status': 'confirmed',
                    'registration_date': datetime.now().isoformat()
                }
                
                response = self.client.table('registrations').insert(registration_data).execute()
                
                # Update current_participants count
                current = event.get('total_slots', 0) - event.get('available_slots', 0)
                self.client.table('events').update({
                    'current_participants': current + 1
                }).eq('id', event_id).execute()
                
                logger.info(f"Created registration for {user_email} to event {event_id} with full details")
                return response.data[0]
                
            except Exception as e:
                error_msg = str(e)
                # Check if error is due to missing columns
                if 'user_class' in error_msg or 'user_section' in error_msg or 'user_year' in error_msg or 'PGRST204' in error_msg:
                    logger.warning(f"New columns not found in DB, trying with basic fields only: {error_msg}")
                    try:
                        # Try without the new columns
                        basic_registration_data = {
                            'event_id': event_id,
                            'user_name': user_name,
                            'user_email': user_email,
                            'user_phone': user_phone,
                            'status': 'confirmed',
                            'registration_date': datetime.now().isoformat()
                        }
                        
                        response = self.client.table('registrations').insert(basic_registration_data).execute()
                        
                        # Update current_participants count
                        current = event.get('total_slots', 0) - event.get('available_slots', 0)
                        self.client.table('events').update({
                            'current_participants': current + 1
                        }).eq('id', event_id).execute()
                        
                        logger.info(f"Created registration for {user_email} to event {event_id} (basic fields only)")
                        
                        # Return data with all fields even though some weren't saved
                        result = response.data[0]
                        result['user_class'] = user_class
                        result['user_section'] = user_section
                        result['user_year'] = user_year
                        return result
                        
                    except Exception as e2:
                        logger.error(f"Failed to create registration even with basic fields: {str(e2)}")
                        raise ValueError(f"Unable to create registration: {str(e2)}")
                else:
                    logger.error(f"Could not create registration in DB: {error_msg}")
                    raise ValueError(f"Registration failed: {error_msg}")
            
        except ValueError as ve:
            logger.warning(f"Registration validation error: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error creating registration: {str(e)}")
            raise
    
    async def create_feedback(
        self,
        event_id: str,
        user_email: str,
        rating: int,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit feedback for an event.
        
        Args:
            event_id: UUID of the event
            user_email: Email of the user
            rating: Rating from 1-5
            comments: Optional feedback comments
            
        Returns:
            Feedback data dictionary
            
        Raises:
            ValueError: If event not found or validation fails
        """
        try:
            # Check if event exists
            event = await self.fetch_event_by_id(event_id)
            if not event:
                raise ValueError("Event not found")
            
            # Note: Date validation is handled in tools.py to avoid duplication
            # The tool layer validates timing appropriately
            
            feedback_data = {
                'event_id': event_id,
                'user_email': user_email,
                'rating': rating,
                'comments': comments,
                'submitted_at': datetime.now().isoformat()
            }
            
            try:
                response = self.client.table('feedback').insert(feedback_data).execute()
                
                if response.data:
                    logger.info(f"Created feedback from {user_email} for event {event_id}")
                    return response.data[0]
                
                raise Exception("Failed to create feedback")
            except Exception as e:
                # If feedback table doesn't exist, return mock data
                logger.warning(f"Could not create feedback in DB (table may not exist): {str(e)}")
                return {
                    'id': event_id,
                    'event_id': event_id,
                    'user_email': user_email,
                    'rating': rating,
                    'comments': comments,
                    'submitted_at': datetime.now().isoformat()
                }
            
        except ValueError as ve:
            logger.warning(f"Feedback validation error: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error creating feedback: {str(e)}")
            raise
    
    async def check_user_registration(
        self,
        event_id: str,
        user_email: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check if user is registered for an event.
        
        Args:
            event_id: UUID of the event
            user_email: Email of the user
            
        Returns:
            Registration data or None if not registered
        """
        try:
            response = self.client.table('registrations').select('*').eq(
                'event_id', event_id
            ).eq('user_email', user_email).eq('status', 'confirmed').execute()
            
            if response.data:
                logger.info(f"Found registration for {user_email} in event {event_id}")
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking registration: {str(e)}")
            raise
    
    async def get_user_registrations(self, user_email: str) -> List[Dict[str, Any]]:
        """
        Get all registrations for a user.
        
        Args:
            user_email: Email of the user
            
        Returns:
            List of registration dictionaries
        """
        try:
            response = self.client.table('registrations').select(
                '*, events(*)'
            ).eq('user_email', user_email).eq('status', 'confirmed').execute()
            
            logger.info(f"Fetched {len(response.data)} registrations for {user_email}")
            return response.data
            
        except Exception as e:
            logger.error(f"Error fetching user registrations: {str(e)}")
            raise


# Singleton instance getter
def get_supabase_client() -> SupabaseClient:
    """Get or create Supabase client singleton."""
    return SupabaseClient()
