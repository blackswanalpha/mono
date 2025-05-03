"""
Mono Frames - Hierarchical component containers for the Mono language

This module provides support for:
1. Frames: Hierarchical component containers
2. Frame Lifecycle: frameWillLoad and frameDidUnload hooks
3. Frame-Scoped State: Shared state accessible only to components within the frame
4. Isolation: Frames run in isolated memory/thread pools
"""

import threading
import queue
import concurrent.futures
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union

from lib.mono_communication import EventEmitter, ServiceRegistry, ContextRegistry

class FrameState:
    """
    Shared state for components within a frame.
    """
    def __init__(self):
        self.state: Dict[str, Any] = {}
        self.lock = threading.RLock()
        self.subscribers: List[Tuple[Any, Callable]] = []
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the frame state.
        
        Args:
            key: The key to get
            default: The default value to return if the key doesn't exist
            
        Returns:
            The value for the key, or the default value if the key doesn't exist
        """
        with self.lock:
            return self.state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the frame state and notify subscribers.
        
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
                        print(f"Error in frame state subscriber: {e}")
    
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

class Frame:
    """
    A hierarchical component container.
    """
    def __init__(self, name: str, parent: Optional['Frame'] = None):
        self.name = name
        self.parent = parent
        self.children: List['Frame'] = []
        self.components: Dict[str, Any] = {}
        self.state = FrameState()
        self.event_emitter = EventEmitter()
        self.service_registry = ServiceRegistry()
        self.context_registry = ContextRegistry()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        self.futures: Dict[str, concurrent.futures.Future] = {}
        self.is_loaded = False
        self.is_unloading = False
        self.lock = threading.RLock()
        
        # Add to parent's children if parent exists
        if parent:
            parent.add_child(self)
    
    def add_child(self, frame: 'Frame') -> None:
        """
        Add a child frame.
        
        Args:
            frame: The frame to add as a child
        """
        with self.lock:
            if frame not in self.children:
                self.children.append(frame)
    
    def remove_child(self, frame: 'Frame') -> None:
        """
        Remove a child frame.
        
        Args:
            frame: The frame to remove
        """
        with self.lock:
            if frame in self.children:
                self.children.remove(frame)
    
    def add_component(self, component_id: str, component: Any) -> None:
        """
        Add a component to the frame.
        
        Args:
            component_id: The ID of the component
            component: The component instance
        """
        with self.lock:
            self.components[component_id] = component
            
            # Set the frame reference on the component
            if hasattr(component, 'frame'):
                component.frame = self
    
    def remove_component(self, component_id: str) -> None:
        """
        Remove a component from the frame.
        
        Args:
            component_id: The ID of the component to remove
        """
        with self.lock:
            if component_id in self.components:
                # Clear the frame reference on the component
                component = self.components[component_id]
                if hasattr(component, 'frame'):
                    component.frame = None
                
                del self.components[component_id]
    
    def get_component(self, component_id: str) -> Optional[Any]:
        """
        Get a component by ID.
        
        Args:
            component_id: The ID of the component to get
            
        Returns:
            The component, or None if it doesn't exist
        """
        with self.lock:
            return self.components.get(component_id)
    
    def load(self) -> None:
        """
        Load the frame and all its components.
        """
        if self.is_loaded:
            return
        
        # Call frameWillLoad hook
        self._call_frame_hook('frameWillLoad')
        
        # Load all components
        for component_id, component in self.components.items():
            if hasattr(component, 'mount'):
                component.mount()
        
        # Mark as loaded
        self.is_loaded = True
        
        # Call frameDidLoad hook
        self._call_frame_hook('frameDidLoad')
    
    def unload(self) -> None:
        """
        Unload the frame and all its components.
        """
        if not self.is_loaded or self.is_unloading:
            return
        
        self.is_unloading = True
        
        # Call frameWillUnload hook
        self._call_frame_hook('frameWillUnload')
        
        # Unload all components
        for component_id, component in self.components.items():
            if hasattr(component, 'unmount'):
                component.unmount()
        
        # Unload all child frames
        for child in self.children:
            child.unload()
        
        # Cancel all futures
        for future_id, future in self.futures.items():
            if not future.done():
                future.cancel()
        
        # Shutdown the executor
        self.executor.shutdown(wait=False)
        
        # Mark as not loaded
        self.is_loaded = False
        self.is_unloading = False
        
        # Call frameDidUnload hook
        self._call_frame_hook('frameDidUnload')
        
        # Remove from parent
        if self.parent:
            self.parent.remove_child(self)
    
    def _call_frame_hook(self, hook_name: str) -> None:
        """
        Call a frame lifecycle hook on all components that support it.
        
        Args:
            hook_name: The name of the hook to call
        """
        for component_id, component in self.components.items():
            if hasattr(component, hook_name):
                try:
                    getattr(component, hook_name)()
                except Exception as e:
                    print(f"Error in {hook_name} hook for component {component_id}: {e}")
    
    def run_in_frame(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """
        Run a function in the frame's thread pool.
        
        Args:
            func: The function to run
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            A Future representing the execution of the function
        """
        future = self.executor.submit(func, *args, **kwargs)
        future_id = str(id(future))
        self.futures[future_id] = future
        
        # Clean up the future when it's done
        def _cleanup_future(f):
            if future_id in self.futures:
                del self.futures[future_id]
        
        future.add_done_callback(_cleanup_future)
        return future
    
    def get_frame_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the frame state.
        
        Args:
            key: The key to get
            default: The default value to return if the key doesn't exist
            
        Returns:
            The value for the key, or the default value if the key doesn't exist
        """
        return self.state.get(key, default)
    
    def set_frame_state(self, key: str, value: Any) -> None:
        """
        Set a value in the frame state.
        
        Args:
            key: The key to set
            value: The value to set
        """
        self.state.set(key, value)
    
    def subscribe_to_frame_state(self, instance: Any, callback: Callable) -> None:
        """
        Subscribe to frame state changes.
        
        Args:
            instance: The component instance that is subscribing
            callback: The callback function to call when the state changes
        """
        self.state.subscribe(instance, callback)
    
    def unsubscribe_from_frame_state(self, instance: Any) -> None:
        """
        Unsubscribe from frame state changes.
        
        Args:
            instance: The component instance that was subscribing
        """
        self.state.unsubscribe(instance)
    
    def emit_event(self, event_name: str, data: Any = None) -> None:
        """
        Emit an event to all listeners in this frame.
        
        Args:
            event_name: The name of the event to emit
            data: The data to pass to the listeners
        """
        self.event_emitter.emit(event_name, data)
    
    def on_event(self, event_name: str, instance: Any, callback: Callable) -> None:
        """
        Register an event listener in this frame.
        
        Args:
            event_name: The name of the event to listen for
            instance: The component instance that is listening
            callback: The callback function to call when the event is emitted
        """
        self.event_emitter.on(event_name, instance, callback)
    
    def off_event(self, event_name: str, instance: Any) -> None:
        """
        Remove an event listener from this frame.
        
        Args:
            event_name: The name of the event to stop listening for
            instance: The component instance that was listening
        """
        self.event_emitter.off(event_name, instance)

class FrameRegistry:
    """
    Registry for frames.
    """
    def __init__(self):
        self.frames: Dict[str, Frame] = {}
        self.lock = threading.RLock()
    
    def create_frame(self, name: str, parent_name: Optional[str] = None) -> Frame:
        """
        Create a new frame.
        
        Args:
            name: The name of the frame
            parent_name: The name of the parent frame, or None if this is a root frame
            
        Returns:
            The created frame
        """
        with self.lock:
            parent = None
            if parent_name and parent_name in self.frames:
                parent = self.frames[parent_name]
            
            frame = Frame(name, parent)
            self.frames[name] = frame
            return frame
    
    def get_frame(self, name: str) -> Optional[Frame]:
        """
        Get a frame by name.
        
        Args:
            name: The name of the frame to get
            
        Returns:
            The frame, or None if it doesn't exist
        """
        with self.lock:
            return self.frames.get(name)
    
    def remove_frame(self, name: str) -> None:
        """
        Remove a frame.
        
        Args:
            name: The name of the frame to remove
        """
        with self.lock:
            if name in self.frames:
                frame = self.frames[name]
                frame.unload()
                del self.frames[name]

# Global frame registry
frame_registry = FrameRegistry()

def get_frame_registry() -> FrameRegistry:
    """Get the global frame registry."""
    return frame_registry
