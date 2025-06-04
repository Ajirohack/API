"""
Interface Adapters Module for Core Integration
- Provides adapters for various interfaces (conversational, visual, etc.)
- Handles message routing and transformations
"""
from typing import Dict, Any, Optional, List, Callable
import asyncio
import time
import uuid
import logging
from core.enhanced_event_bus import EventBus

logger = logging.getLogger(__name__)

class BaseAdapter:
    """Base adapter class providing common functionality"""
    
    def __init__(self, event_bus: EventBus):
        """
        Initialize the adapter with an event bus.
        
        Args:
            event_bus: Event bus for messaging
        """
        self.event_bus = event_bus
        self.adapter_id = str(uuid.uuid4())
        self.last_activity = time.time()
    
    async def send_event(self, topic: str, data: Dict[str, Any]) -> None:
        """
        Send an event to the event bus.
        
        Args:
            topic: Topic to publish to
            data: Event data
        """
        self.last_activity = time.time()
        await self.event_bus.publish(topic, data)
    
    def send_event_sync(self, topic: str, data: Dict[str, Any]) -> None:
        """
        Synchronous version of send_event.
        
        Args:
            topic: Topic to publish to
            data: Event data
        """
        self.last_activity = time.time()
        self.event_bus.publish_sync(topic, data)


class ConversationalAdapter(BaseAdapter):
    """
    Adapter for conversational interfaces (chat, voice, etc.)
    Handles routing messages between UI and backend components.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialize the conversational adapter.
        
        Args:
            event_bus: Event bus for messaging
        """
        super().__init__(event_bus)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        
        # Register default event handlers
        asyncio.create_task(self._register_handlers())
    
    async def _register_handlers(self) -> None:
        """Register event handlers for incoming messages"""
        await self.event_bus.subscribe('engine.response', self._handle_engine_response)
        await self.event_bus.subscribe('interface.command', self._handle_command)
    
    async def _handle_engine_response(self, event: Dict[str, Any]) -> None:
        """
        Handle responses from processing engines.
        
        Args:
            event: Response event
        """
        # Route engine responses to interface.outgoing
        session_id = event.get('session_id')
        if session_id and session_id in self.sessions:
            # Attach session info
            event['user_id'] = self.sessions[session_id].get('user_id')
            
        # Send to UI via outgoing topic
        await self.event_bus.publish('interface.outgoing', {
            'type': event.get('type', 'text'),
            'content': event.get('content', ''),
            'session_id': session_id,
            'metadata': event.get('metadata', {})
        })
    
    async def _handle_command(self, event: Dict[str, Any]) -> None:
        """
        Handle command events for the interface.
        
        Args:
            event: Command event
        """
        command = event.get('command')
        if command == 'clear_history':
            session_id = event.get('session_id')
            if session_id and session_id in self.sessions:
                self.sessions[session_id]['history'] = []
                await self.event_bus.publish('interface.outgoing', {
                    'type': 'status',
                    'content': 'History cleared',
                    'session_id': session_id
                })
    
    def receive(self, message: str, user_id: Optional[str] = None, 
                session_id: Optional[str] = None) -> str:
        """
        Receive a message from a user interface.
        
        Args:
            message: User message
            user_id: User identifier
            session_id: Session identifier (creates new if None)
            
        Returns:
            Session ID (created or existing)
        """
        # Create or get session
        if not session_id:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {
                'created_at': time.time(),
                'user_id': user_id or 'anonymous',
                'history': []
            }
        elif session_id not in self.sessions:
            self.sessions[session_id] = {
                'created_at': time.time(),
                'user_id': user_id or 'anonymous',
                'history': []
            }
        
        # Update session
        session = self.sessions[session_id]
        session['last_activity'] = time.time()
        session['history'].append({
            'role': 'user',
            'content': message,
            'timestamp': time.time()
        })
        
        # Send to event bus
        self.send_event_sync('interface.incoming', {
            'type': 'text',
            'content': message,
            'user_id': user_id,
            'session_id': session_id,
            'history': session['history']
        })
        
        return session_id
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        Register a callback for specific event types.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        """
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
    
    def send_response(self, session_id: str, response: str, 
                      response_type: str = 'text') -> None:
        """
        Send a response to the user interface.
        
        Args:
            session_id: Session identifier
            response: Response content
            response_type: Type of response (text, image, etc.)
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session['history'].append({
                'role': 'assistant',
                'content': response,
                'timestamp': time.time()
            })
            
            # Send to event bus
            self.send_event_sync('interface.outgoing', {
                'type': response_type,
                'content': response,
                'session_id': session_id,
                'user_id': session.get('user_id')
            })
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get message history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message objects in the session
        """
        if session_id in self.sessions:
            return self.sessions[session_id].get('history', [])
        return []
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear a session from memory.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was cleared, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


class VisualAdapter(BaseAdapter):
    """
    Adapter for visual interfaces (dashboards, graphs, etc.)
    Placeholder implementation.
    """
    
    def __init__(self, event_bus: EventBus):
        """Initialize the visual adapter."""
        super().__init__(event_bus)
        
    def update_dashboard(self, dashboard_id: str, data: Dict[str, Any]) -> None:
        """
        Update a dashboard with new data.
        
        Args:
            dashboard_id: Dashboard identifier
            data: Dashboard data to update
        """
        self.send_event_sync('visual.update', {
            'dashboard_id': dashboard_id,
            'data': data,
            'timestamp': time.time()
        })
