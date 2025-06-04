"""
Enhanced Event Bus for Asynchronous Communication
- Supports pub/sub pattern for event-driven architecture
- Allows polling for events with filters
- Maintains event history for replay
"""
from typing import List, Dict, Any, Optional, Callable
import time
import asyncio
import uuid
import logging

logger = logging.getLogger(__name__)

class EventBus:
    """
    Enhanced Event Bus for message passing between components.
    Supports topics, filtering, and message history.
    """
    
    def __init__(self, history_size: int = 100):
        """
        Initialize the event bus with specified history size.
        
        Args:
            history_size: Maximum number of events to keep in history per topic
        """
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        self._history_size = history_size
        self._lock = asyncio.Lock()
    
    async def publish(self, topic: str, event: Dict[str, Any]) -> None:
        """
        Publish an event to a topic.
        
        Args:
            topic: Topic to publish to
            event: Event data (dictionary)
        """
        if not isinstance(event, dict):
            event = {"data": event}
            
        # Add metadata if not present
        if "id" not in event:
            event["id"] = str(uuid.uuid4())
        if "timestamp" not in event:
            event["timestamp"] = time.time()
        if "topic" not in event:
            event["topic"] = topic
            
        # Store in history
        async with self._lock:
            if topic not in self._history:
                self._history[topic] = []
            self._history[topic].append(event)
            # Trim history if needed
            if len(self._history[topic]) > self._history_size:
                self._history[topic] = self._history[topic][-self._history_size:]
        
        # Notify subscribers
        if topic in self._subscribers:
            for callback in self._subscribers[topic]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Error in subscriber callback: {str(e)}")
    
    def publish_sync(self, topic: str, event: Dict[str, Any]) -> None:
        """
        Synchronous version of publish for non-async contexts.
        
        Args:
            topic: Topic to publish to
            event: Event data (dictionary)
        """
        asyncio.run(self.publish(topic, event))
    
    async def subscribe(self, topic: str, callback: Callable) -> None:
        """
        Subscribe to a topic with a callback function.
        
        Args:
            topic: Topic to subscribe to
            callback: Async function to call when events are published
        """
        async with self._lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            self._subscribers[topic].append(callback)
    
    def subscribe_sync(self, topic: str, callback: Callable) -> None:
        """
        Synchronous version of subscribe for non-async contexts.
        
        Args:
            topic: Topic to subscribe to
            callback: Function to call when events are published
        """
        asyncio.run(self.subscribe(topic, callback))
    
    async def unsubscribe(self, topic: str, callback: Callable) -> bool:
        """
        Unsubscribe a callback from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            True if callback was removed, False if not found
        """
        async with self._lock:
            if topic in self._subscribers and callback in self._subscribers[topic]:
                self._subscribers[topic].remove(callback)
                return True
        return False
    
    def poll(self, topic: str, since_timestamp: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Poll for events on a topic, optionally since a timestamp.
        
        Args:
            topic: Topic to poll events from
            since_timestamp: Only return events after this timestamp
            
        Returns:
            List of events matching criteria
        """
        if topic not in self._history:
            return []
            
        if since_timestamp is None:
            # Return all events in history
            return self._history[topic].copy()
        else:
            # Filter by timestamp
            return [event for event in self._history[topic] if event.get('timestamp', 0) > since_timestamp]
    
    def clear_history(self, topic: Optional[str] = None) -> None:
        """
        Clear event history for a topic or all topics.
        
        Args:
            topic: Topic to clear. If None, clear all topics.
        """
        if topic:
            if topic in self._history:
                self._history[topic] = []
        else:
            self._history = {}
