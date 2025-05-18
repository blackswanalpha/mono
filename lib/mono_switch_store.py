"""
Switch Store - A state management system for the Switch framework

This module provides a centralized state management system similar to Redux or Vuex.
It allows components to share state and react to state changes.
"""

import json
import copy
import threading
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union

class Store:
    """
    A centralized state management system for the Switch framework.
    """
    def __init__(self, options: Dict[str, Any] = None):
        """
        Create a new store.
        
        Args:
            options: Store options
        """
        options = options or {}
        
        # State
        self._state = options.get('state', {})
        
        # Getters
        self._getters = {}
        self._computed_getters = {}
        
        # Mutations
        self._mutations = options.get('mutations', {})
        
        # Actions
        self._actions = options.get('actions', {})
        
        # Modules
        self._modules = {}
        
        # Subscribers
        self._subscribers = []
        
        # Strict mode
        self._strict = options.get('strict', False)
        
        # Is a mutation in progress
        self._committing = False
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Initialize getters
        for key, getter in options.get('getters', {}).items():
            self._getters[key] = getter
        
        # Register modules
        for name, module in options.get('modules', {}).items():
            self.register_module(name, module)
        
        # Apply plugins
        for plugin in options.get('plugins', []):
            plugin(self)
    
    @property
    def state(self) -> Dict[str, Any]:
        """
        Get the state.
        
        Returns:
            The state
        """
        return self._state
    
    def get_getter(self, name: str) -> Any:
        """
        Get a getter.
        
        Args:
            name: The getter name
            
        Returns:
            The getter value
        """
        # Check if the getter exists
        if name not in self._getters:
            raise KeyError(f"Unknown getter: {name}")
        
        # Check if the getter is already computed
        if name in self._computed_getters:
            return self._computed_getters[name]
        
        # Compute the getter
        with self._lock:
            value = self._getters[name](self._state, self.get_getter)
            self._computed_getters[name] = value
            return value
    
    def commit(self, type: str, payload: Any = None) -> None:
        """
        Commit a mutation.
        
        Args:
            type: The mutation type
            payload: The mutation payload
        """
        # Check if the mutation exists
        if type not in self._mutations:
            raise KeyError(f"Unknown mutation type: {type}")
        
        # Set committing flag
        prev_committing = self._committing
        self._committing = True
        
        try:
            # Call the mutation
            with self._lock:
                self._mutations[type](self._state, payload)
                
                # Clear computed getters
                self._computed_getters = {}
                
                # Notify subscribers
                for sub in self._subscribers:
                    sub({
                        'type': type,
                        'payload': payload
                    }, copy.deepcopy(self._state))
        finally:
            # Reset committing flag
            self._committing = prev_committing
    
    def dispatch(self, type: str, payload: Any = None) -> Any:
        """
        Dispatch an action.
        
        Args:
            type: The action type
            payload: The action payload
            
        Returns:
            The action result
        """
        # Check if the action exists
        if type not in self._actions:
            raise KeyError(f"Unknown action type: {type}")
        
        # Call the action
        context = {
            'state': self._state,
            'getters': self.get_getter,
            'commit': self.commit,
            'dispatch': self.dispatch
        }
        
        return self._actions[type](context, payload)
    
    def subscribe(self, fn: Callable) -> Callable:
        """
        Subscribe to store mutations.
        
        Args:
            fn: The subscriber function
            
        Returns:
            A function to unsubscribe
        """
        # Add the subscriber
        with self._lock:
            self._subscribers.append(fn)
        
        # Return a function to unsubscribe
        def unsubscribe():
            with self._lock:
                if fn in self._subscribers:
                    self._subscribers.remove(fn)
        
        return unsubscribe
    
    def watch(self, getter: Union[str, Callable], cb: Callable, options: Dict[str, Any] = None) -> Callable:
        """
        Watch a getter or state path for changes.
        
        Args:
            getter: The getter or state path
            cb: The callback function
            options: Watch options
            
        Returns:
            A function to stop watching
        """
        options = options or {}
        
        # Default options
        deep = options.get('deep', False)
        immediate = options.get('immediate', False)
        
        # Get the current value
        def get_value():
            if callable(getter):
                return getter(self._state, self.get_getter)
            elif isinstance(getter, str):
                # Split the path
                path = getter.split('.')
                
                # Get the value
                value = self._state
                for key in path:
                    value = value[key]
                
                return value
            else:
                raise TypeError("Invalid getter type")
        
        # Get the initial value
        old_value = get_value()
        
        # Call the callback immediately if requested
        if immediate:
            cb(old_value, old_value)
        
        # Create the subscriber
        def subscriber(mutation, state):
            nonlocal old_value
            
            # Get the new value
            new_value = get_value()
            
            # Check if the value has changed
            if new_value != old_value:
                # Call the callback
                cb(new_value, old_value)
                
                # Update the old value
                old_value = new_value
        
        # Subscribe to mutations
        return self.subscribe(subscriber)
    
    def register_module(self, name: str, module: Dict[str, Any]) -> None:
        """
        Register a module.
        
        Args:
            name: The module name
            module: The module
        """
        # Add the module
        self._modules[name] = module
        
        # Add the module state
        with self._lock:
            self._state[name] = module.get('state', {})
        
        # Add the module getters
        for key, getter in module.get('getters', {}).items():
            full_key = f"{name}/{key}"
            
            def create_getter(getter_fn):
                def wrapper(state, getters):
                    return getter_fn(state[name], getters)
                return wrapper
            
            self._getters[full_key] = create_getter(getter)
        
        # Add the module mutations
        for key, mutation in module.get('mutations', {}).items():
            full_key = f"{name}/{key}"
            
            def create_mutation(mutation_fn):
                def wrapper(state, payload):
                    mutation_fn(state[name], payload)
                return wrapper
            
            self._mutations[full_key] = create_mutation(mutation)
        
        # Add the module actions
        for key, action in module.get('actions', {}).items():
            full_key = f"{name}/{key}"
            
            def create_action(action_fn):
                def wrapper(context, payload):
                    module_context = {
                        'state': context['state'][name],
                        'getters': context['getters'],
                        'commit': lambda type, payload=None: context['commit'](f"{name}/{type}", payload),
                        'dispatch': lambda type, payload=None: context['dispatch'](f"{name}/{type}", payload)
                    }
                    
                    return action_fn(module_context, payload)
                return wrapper
            
            self._actions[full_key] = create_action(action)
    
    def unregister_module(self, name: str) -> None:
        """
        Unregister a module.
        
        Args:
            name: The module name
        """
        # Check if the module exists
        if name not in self._modules:
            raise KeyError(f"Module not found: {name}")
        
        # Remove the module state
        with self._lock:
            del self._state[name]
        
        # Remove the module getters
        for key in list(self._getters.keys()):
            if key.startswith(f"{name}/"):
                del self._getters[key]
        
        # Remove the module mutations
        for key in list(self._mutations.keys()):
            if key.startswith(f"{name}/"):
                del self._mutations[key]
        
        # Remove the module actions
        for key in list(self._actions.keys()):
            if key.startswith(f"{name}/"):
                del self._actions[key]
        
        # Remove the module
        del self._modules[name]
        
        # Clear computed getters
        self._computed_getters = {}
    
    def to_json(self) -> str:
        """
        Convert the store state to JSON.
        
        Returns:
            The JSON string
        """
        return json.dumps(self._state)
    
    @classmethod
    def from_json(cls, json_str: str, options: Dict[str, Any] = None) -> 'Store':
        """
        Create a store from JSON.
        
        Args:
            json_str: The JSON string
            options: Store options
            
        Returns:
            The store
        """
        options = options or {}
        options['state'] = json.loads(json_str)
        return cls(options)


def create_store(options: Dict[str, Any] = None) -> Store:
    """
    Create a new store.
    
    Args:
        options: Store options
        
    Returns:
        The store
    """
    return Store(options)


def create_file_storage_plugin(options: Dict[str, Any] = None) -> Callable:
    """
    Create a plugin that saves the state to a file.
    
    Args:
        options: Plugin options
        
    Returns:
        The plugin function
    """
    options = options or {}
    
    # Default options
    file_path = options.get('file_path', 'store.json')
    paths = options.get('paths', None)
    
    # Create the plugin
    def plugin(store: Store) -> None:
        # Load the state from the file
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)
                
                # Merge the state
                if paths:
                    for path in paths:
                        # Split the path
                        keys = path.split('.')
                        
                        # Get the value from the saved state
                        saved_value = state
                        for key in keys:
                            if saved_value is None:
                                break
                            saved_value = saved_value.get(key)
                        
                        if saved_value is None:
                            continue
                        
                        # Set the value in the store state
                        store_state = store.state
                        for i in range(len(keys) - 1):
                            store_state = store_state.get(keys[i], {})
                        
                        store_state[keys[-1]] = saved_value
                else:
                    # Merge the entire state
                    store._state.update(state)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Subscribe to mutations
        def save_state(mutation, state):
            try:
                # Save the state to the file
                if paths:
                    # Save only the specified paths
                    save_state = {}
                    
                    for path in paths:
                        # Split the path
                        keys = path.split('.')
                        
                        # Get the value from the store state
                        value = state
                        for key in keys:
                            if value is None:
                                break
                            value = value.get(key)
                        
                        if value is None:
                            continue
                        
                        # Set the value in the save state
                        save_obj = save_state
                        for i in range(len(keys) - 1):
                            if keys[i] not in save_obj:
                                save_obj[keys[i]] = {}
                            save_obj = save_obj[keys[i]]
                        
                        save_obj[keys[-1]] = value
                    
                    with open(file_path, 'w') as f:
                        json.dump(save_state, f)
                else:
                    # Save the entire state
                    with open(file_path, 'w') as f:
                        json.dump(state, f)
            except Exception as e:
                print(f"Could not save state to file: {e}")
        
        store.subscribe(save_state)
    
    return plugin
