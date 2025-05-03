"""
Mono Communication - Inter-component communication for the Mono language

This module provides support for:
1. Events: Custom events with pub/sub mechanisms
2. Services: Global state management
3. Context API: Pass data through the component tree without explicit props
"""

from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union
import threading

class EventEmitter:
    """
    Event emitter for pub/sub communication between components.
    """
    def __init__(self):
        self.listeners: Dict[str, List[Tuple[Any, Callable]]] = {}
        self.lock = threading.RLock()
    
    def on(self, event_name: str, instance: Any, callback: Callable) -> None:
        """
        Register an event listener.
        
        Args:
            event_name: The name of the event to listen for
            instance: The component instance that is listening
            callback: The callback function to call when the event is emitted
        """
        with self.lock:
            if event_name not in self.listeners:
                self.listeners[event_name] = []
            self.listeners[event_name].append((instance, callback))
    
    def off(self, event_name: str, instance: Any) -> None:
        """
        Remove an event listener.
        
        Args:
            event_name: The name of the event to stop listening for
            instance: The component instance that was listening
        """
        with self.lock:
            if event_name in self.listeners:
                self.listeners[event_name] = [
                    (i, cb) for i, cb in self.listeners[event_name] if i != instance
                ]
    
    def emit(self, event_name: str, data: Any = None) -> None:
        """
        Emit an event to all listeners.
        
        Args:
            event_name: The name of the event to emit
            data: The data to pass to the listeners
        """
        with self.lock:
            if event_name in self.listeners:
                for instance, callback in self.listeners[event_name]:
                    try:
                        callback(data)
                    except Exception as e:
                        print(f"Error in event listener for {event_name}: {e}")

class Service:
    """
    Base class for services that provide global state management.
    """
    def __init__(self, name: str):
        self.name = name
        self.state: Dict[str, Any] = {}
        self.subscribers: List[Tuple[Any, Callable]] = []
        self.lock = threading.RLock()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the service state.
        
        Args:
            key: The key to get
            default: The default value to return if the key doesn't exist
            
        Returns:
            The value for the key, or the default value if the key doesn't exist
        """
        with self.lock:
            return self.state.get(key, default)
    
    def set_state(self, key: str, value: Any) -> None:
        """
        Set a value in the service state and notify subscribers.
        
        Args:
            key: The key to set
            value: The value to set
        """
        with self.lock:
            old_value = self.state.get(key)
            self.state[key] = value
            
            # Notify subscribers if the value changed
            if old_value != value:
                for instance, callback in self.subscribers:
                    try:
                        callback(key, value, old_value)
                    except Exception as e:
                        print(f"Error in service subscriber for {self.name}: {e}")
    
    def subscribe(self, instance: Any, callback: Callable) -> None:
        """
        Subscribe to state changes.
        
        Args:
            instance: The component instance that is subscribing
            callback: The callback function to call when the state changes
        """
        with self.lock:
            self.subscribers.append((instance, callback))
    
    def unsubscribe(self, instance: Any) -> None:
        """
        Unsubscribe from state changes.
        
        Args:
            instance: The component instance that was subscribing
        """
        with self.lock:
            self.subscribers = [
                (i, cb) for i, cb in self.subscribers if i != instance
            ]

class ServiceRegistry:
    """
    Registry for services.
    """
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.lock = threading.RLock()
    
    def register(self, service: Service) -> None:
        """
        Register a service.
        
        Args:
            service: The service to register
        """
        with self.lock:
            self.services[service.name] = service
    
    def get(self, name: str) -> Optional[Service]:
        """
        Get a service by name.
        
        Args:
            name: The name of the service to get
            
        Returns:
            The service, or None if it doesn't exist
        """
        with self.lock:
            return self.services.get(name)
    
    def unregister(self, name: str) -> None:
        """
        Unregister a service.
        
        Args:
            name: The name of the service to unregister
        """
        with self.lock:
            if name in self.services:
                del self.services[name]

class Context:
    """
    Context for passing data through the component tree.
    """
    def __init__(self, name: str, default_value: Any = None):
        self.name = name
        self.default_value = default_value
        self.providers: Dict[Any, Any] = {}  # instance -> value
        self.consumers: Dict[Any, List[Callable]] = {}  # instance -> callbacks
        self.lock = threading.RLock()
    
    def provide(self, instance: Any, value: Any) -> None:
        """
        Provide a value to the context.
        
        Args:
            instance: The component instance that is providing the value
            value: The value to provide
        """
        with self.lock:
            old_value = self.providers.get(instance)
            self.providers[instance] = value
            
            # Notify consumers if the value changed
            if old_value != value:
                for consumer_instance, callbacks in self.consumers.items():
                    # Find the nearest provider in the component tree
                    provider_instance = self._find_nearest_provider(consumer_instance)
                    if provider_instance:
                        provider_value = self.providers[provider_instance]
                        for callback in callbacks:
                            try:
                                callback(provider_value)
                            except Exception as e:
                                print(f"Error in context consumer for {self.name}: {e}")
    
    def consume(self, instance: Any, callback: Callable) -> Any:
        """
        Consume a value from the context.
        
        Args:
            instance: The component instance that is consuming the value
            callback: The callback function to call when the value changes
            
        Returns:
            The current value from the nearest provider, or the default value if no provider exists
        """
        with self.lock:
            if instance not in self.consumers:
                self.consumers[instance] = []
            self.consumers[instance].append(callback)
            
            # Find the nearest provider in the component tree
            provider_instance = self._find_nearest_provider(instance)
            if provider_instance:
                return self.providers[provider_instance]
            return self.default_value
    
    def _find_nearest_provider(self, instance: Any) -> Optional[Any]:
        """
        Find the nearest provider in the component tree.
        
        Args:
            instance: The component instance to start from
            
        Returns:
            The nearest provider instance, or None if no provider exists
        """
        # Start with the current instance
        current = instance
        
        # Traverse up the component tree
        while current:
            if current in self.providers:
                return current
            
            # Move to the parent component
            current = getattr(current, 'parent', None)
        
        return None
    
    def stop_consuming(self, instance: Any) -> None:
        """
        Stop consuming values from the context.
        
        Args:
            instance: The component instance that was consuming values
        """
        with self.lock:
            if instance in self.consumers:
                del self.consumers[instance]

class ContextRegistry:
    """
    Registry for contexts.
    """
    def __init__(self):
        self.contexts: Dict[str, Context] = {}
        self.lock = threading.RLock()
    
    def create(self, name: str, default_value: Any = None) -> Context:
        """
        Create a new context.
        
        Args:
            name: The name of the context
            default_value: The default value for the context
            
        Returns:
            The created context
        """
        with self.lock:
            if name not in self.contexts:
                self.contexts[name] = Context(name, default_value)
            return self.contexts[name]
    
    def get(self, name: str) -> Optional[Context]:
        """
        Get a context by name.
        
        Args:
            name: The name of the context to get
            
        Returns:
            The context, or None if it doesn't exist
        """
        with self.lock:
            return self.contexts.get(name)
    
    def remove(self, name: str) -> None:
        """
        Remove a context.
        
        Args:
            name: The name of the context to remove
        """
        with self.lock:
            if name in self.contexts:
                del self.contexts[name]

# Global instances
event_emitter = EventEmitter()
service_registry = ServiceRegistry()
context_registry = ContextRegistry()

def get_event_emitter() -> EventEmitter:
    """Get the global event emitter."""
    return event_emitter

def get_service_registry() -> ServiceRegistry:
    """Get the global service registry."""
    return service_registry

def get_context_registry() -> ContextRegistry:
    """Get the global context registry."""
    return context_registry
