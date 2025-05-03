"""
Mono Runtime Environment - Runtime environment for the Mono language

This module provides support for:
1. Scheduler: Manage component threads and prioritize tasks
2. Garbage Collection: Automatically clean up unmounted components
3. Hot Reloading: Update components at runtime without restarting
"""

import os
import re
import sys
import time
import threading
import weakref
import importlib
import inspect
import traceback
import heapq
import logging
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union, TypeVar, Generic
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mono_runtime")

# Type definitions
T = TypeVar('T')
ComponentType = TypeVar('ComponentType')
TaskCallback = Callable[[], Any]
ComponentInstance = Any  # This will be refined later

class TaskPriority(Enum):
    """Priority levels for tasks."""
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()

@dataclass(order=True)
class Task:
    """A task to be executed by the scheduler."""
    priority: TaskPriority = field(compare=True)
    created_at: datetime = field(compare=True, default_factory=datetime.now)
    callback: TaskCallback = field(compare=False, default=None)
    component: Optional[ComponentInstance] = field(compare=False, default=None)
    name: str = field(compare=False, default="")

    def execute(self) -> Any:
        """Execute the task."""
        try:
            return self.callback()
        except Exception as e:
            logger.error(f"Error executing task {self.name}: {e}")
            logger.error(traceback.format_exc())
            return None

class ComponentState(Enum):
    """Possible states of a component."""
    CREATED = auto()
    MOUNTED = auto()
    UPDATED = auto()
    UNMOUNTED = auto()
    GARBAGE_COLLECTED = auto()

class ComponentRef:
    """A reference to a component instance that can be garbage collected."""
    def __init__(self, component: ComponentInstance, state: ComponentState = ComponentState.CREATED):
        self.component = component
        self.state = state
        self.last_accessed = datetime.now()
        self.mount_time: Optional[datetime] = None
        self.unmount_time: Optional[datetime] = None

    def access(self) -> None:
        """Mark the component as accessed."""
        self.last_accessed = datetime.now()

    def mount(self) -> None:
        """Mark the component as mounted."""
        self.state = ComponentState.MOUNTED
        self.mount_time = datetime.now()
        self.access()

    def update(self) -> None:
        """Mark the component as updated."""
        self.state = ComponentState.UPDATED
        self.access()

    def unmount(self) -> None:
        """Mark the component as unmounted."""
        self.state = ComponentState.UNMOUNTED
        self.unmount_time = datetime.now()

    def is_garbage_collectable(self, ttl: timedelta) -> bool:
        """Check if the component can be garbage collected."""
        if self.state == ComponentState.UNMOUNTED:
            return datetime.now() - self.unmount_time > ttl
        return False

class Scheduler:
    """
    Scheduler for managing component threads and prioritizing tasks.
    """
    def __init__(self, max_workers: int = 5):
        self.tasks: List[Task] = []
        self.lock = threading.RLock()
        self.workers: List[threading.Thread] = []
        self.max_workers = max_workers
        self.running = False
        self.stop_event = threading.Event()

    def start(self) -> None:
        """Start the scheduler."""
        with self.lock:
            if self.running:
                return

            self.running = True
            self.stop_event.clear()

            # Create worker threads
            for i in range(self.max_workers):
                worker = threading.Thread(target=self._worker_loop, name=f"MonoWorker-{i}")
                worker.daemon = True
                worker.start()
                self.workers.append(worker)

            logger.info(f"Scheduler started with {self.max_workers} workers")

    def stop(self) -> None:
        """Stop the scheduler."""
        with self.lock:
            if not self.running:
                return

            self.running = False
            self.stop_event.set()

            # Wait for workers to finish
            for worker in self.workers:
                worker.join(timeout=1.0)

            self.workers = []
            logger.info("Scheduler stopped")

    def schedule(self, callback: TaskCallback, priority: TaskPriority = TaskPriority.NORMAL,
                component: Optional[ComponentInstance] = None, name: str = "") -> None:
        """Schedule a task for execution."""
        with self.lock:
            task = Task(priority=priority, callback=callback, component=component, name=name)
            heapq.heappush(self.tasks, task)

    def _worker_loop(self) -> None:
        """Worker thread loop."""
        while not self.stop_event.is_set():
            task = None

            # Get a task from the queue
            with self.lock:
                if self.tasks:
                    task = heapq.heappop(self.tasks)

            # Execute the task
            if task:
                logger.debug(f"Executing task: {task.name}")
                task.execute()
            else:
                # No tasks, sleep for a bit
                time.sleep(0.01)

class GarbageCollector:
    """
    Garbage collector for automatically cleaning up unmounted components.
    """
    def __init__(self, scheduler: Scheduler, ttl: timedelta = timedelta(seconds=30)):
        self.components: Dict[int, ComponentRef] = {}
        self.scheduler = scheduler
        self.ttl = ttl
        self.lock = threading.RLock()
        self.running = False
        self.stop_event = threading.Event()
        self.gc_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the garbage collector."""
        with self.lock:
            if self.running:
                return

            self.running = True
            self.stop_event.clear()

            # Create GC thread
            self.gc_thread = threading.Thread(target=self._gc_loop, name="MonoGC")
            self.gc_thread.daemon = True
            self.gc_thread.start()

            logger.info("Garbage collector started")

    def stop(self) -> None:
        """Stop the garbage collector."""
        with self.lock:
            if not self.running:
                return

            self.running = False
            self.stop_event.set()

            # Wait for GC thread to finish
            if self.gc_thread:
                self.gc_thread.join(timeout=1.0)
                self.gc_thread = None

            logger.info("Garbage collector stopped")

    def register(self, component: ComponentInstance) -> None:
        """Register a component with the garbage collector."""
        with self.lock:
            component_id = id(component)
            self.components[component_id] = ComponentRef(component)
            logger.debug(f"Registered component: {component_id}")

    def mount(self, component: ComponentInstance) -> None:
        """Mark a component as mounted."""
        with self.lock:
            component_id = id(component)
            if component_id in self.components:
                self.components[component_id].mount()
                logger.debug(f"Mounted component: {component_id}")

    def update(self, component: ComponentInstance) -> None:
        """Mark a component as updated."""
        with self.lock:
            component_id = id(component)
            if component_id in self.components:
                self.components[component_id].update()
                logger.debug(f"Updated component: {component_id}")

    def unmount(self, component: ComponentInstance) -> None:
        """Mark a component as unmounted."""
        with self.lock:
            component_id = id(component)
            if component_id in self.components:
                self.components[component_id].unmount()
                logger.debug(f"Unmounted component: {component_id}")

    def _gc_loop(self) -> None:
        """Garbage collection loop."""
        while not self.stop_event.is_set():
            # Sleep for a bit
            time.sleep(1.0)

            # Collect garbage
            self._collect_garbage()

    def _collect_garbage(self) -> None:
        """Collect garbage."""
        with self.lock:
            # Find components that can be garbage collected
            to_collect = []
            for component_id, ref in self.components.items():
                if ref.is_garbage_collectable(self.ttl):
                    to_collect.append(component_id)

            # Garbage collect components
            for component_id in to_collect:
                ref = self.components.pop(component_id)
                ref.state = ComponentState.GARBAGE_COLLECTED

                # Schedule cleanup task
                if hasattr(ref.component, 'cleanup') and callable(getattr(ref.component, 'cleanup')):
                    self.scheduler.schedule(
                        callback=lambda: ref.component.cleanup(),
                        priority=TaskPriority.LOW,
                        name=f"GC-Cleanup-{component_id}"
                    )

                logger.debug(f"Garbage collected component: {component_id}")

            if to_collect:
                logger.info(f"Garbage collected {len(to_collect)} components")

class FileChangeHandler(FileSystemEventHandler):
    """
    Handler for file system events.
    """
    def __init__(self, hot_reloader):
        self.hot_reloader = hot_reloader

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        # Check if the file is a Mono file
        if event.src_path.endswith('.mono'):
            logger.info(f"File modified: {event.src_path}")
            self.hot_reloader.file_changed(event.src_path)

class HotReloader:
    """
    Hot reloader for updating components at runtime without restarting.
    """
    def __init__(self, scheduler: Scheduler):
        self.scheduler = scheduler
        self.observers: List[Observer] = []
        self.watched_paths: Set[str] = set()
        self.components: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        self.running = False

    def start(self) -> None:
        """Start the hot reloader."""
        with self.lock:
            if self.running:
                return

            self.running = True
            logger.info("Hot reloader started")

    def stop(self) -> None:
        """Stop the hot reloader."""
        with self.lock:
            if not self.running:
                return

            self.running = False

            # Stop all observers
            for observer in self.observers:
                observer.stop()
                observer.join()

            self.observers = []
            logger.info("Hot reloader stopped")

    def watch(self, path: str) -> None:
        """Watch a directory for changes."""
        with self.lock:
            if not self.running:
                return

            if path in self.watched_paths:
                return

            # Create an observer for the path
            observer = Observer()
            handler = FileChangeHandler(self)
            observer.schedule(handler, path, recursive=True)
            observer.start()

            self.observers.append(observer)
            self.watched_paths.add(path)

            logger.info(f"Watching directory: {path}")

    def register_component(self, component_class: type, file_path: str) -> None:
        """Register a component class with the hot reloader."""
        with self.lock:
            component_name = component_class.__name__

            if component_name not in self.components:
                self.components[component_name] = {}

            self.components[component_name]['class'] = component_class
            self.components[component_name]['file_path'] = file_path
            self.components[component_name]['instances'] = weakref.WeakSet()

            logger.debug(f"Registered component class: {component_name}")

    def register_instance(self, instance: ComponentInstance) -> None:
        """Register a component instance with the hot reloader."""
        with self.lock:
            component_name = instance.__class__.__name__

            if component_name in self.components:
                self.components[component_name]['instances'].add(instance)
                logger.debug(f"Registered component instance: {component_name}")

    def file_changed(self, file_path: str) -> None:
        """Handle a file change event."""
        with self.lock:
            if not self.running:
                return

            # Find components that use this file
            components_to_update = []
            for component_name, component_info in self.components.items():
                if component_info['file_path'] == file_path:
                    components_to_update.append(component_name)

            if not components_to_update:
                return

            # Schedule a task to reload the components
            self.scheduler.schedule(
                callback=lambda: self._reload_components(file_path, components_to_update),
                priority=TaskPriority.HIGH,
                name=f"HotReload-{os.path.basename(file_path)}"
            )

    def _reload_components(self, file_path: str, component_names: List[str]) -> None:
        """Reload components from a file."""
        try:
            # Parse the file to get the updated component classes
            updated_classes = self._parse_file(file_path)

            # Update each component
            for component_name in component_names:
                if component_name in updated_classes and component_name in self.components:
                    # Get the updated class
                    updated_class = updated_classes[component_name]

                    # Update the class in the registry
                    old_class = self.components[component_name]['class']
                    self.components[component_name]['class'] = updated_class

                    # Update all instances
                    instances = list(self.components[component_name]['instances'])
                    for instance in instances:
                        self._update_instance(instance, old_class, updated_class)

            logger.info(f"Reloaded {len(component_names)} components from {file_path}")
        except Exception as e:
            logger.error(f"Error reloading components from {file_path}: {e}")
            logger.error(traceback.format_exc())

    def _parse_file(self, file_path: str) -> Dict[str, type]:
        """Parse a file to get the component classes."""
        with open(file_path, 'r') as f:
            content = f.read()

        # Extract component definitions
        component_pattern = r'component\s+(\w+)\s*{([^}]*)}'
        components = {}

        for match in re.finditer(component_pattern, content, re.DOTALL):
            component_name = match.group(1)
            component_body = match.group(2)

            # Create a new class dynamically
            class_dict = {
                '__module__': '__dynamic__',
                '__qualname__': component_name,
                '__init__': lambda self: None,
                'state': {},
                'methods': {}
            }

            # Extract state
            state_pattern = r'state\s*{([^}]*)}'
            state_match = re.search(state_pattern, component_body)
            if state_match:
                state_body = state_match.group(1)
                state_dict = {}

                # Parse state properties
                for prop in state_body.split(','):
                    prop = prop.strip()
                    if not prop:
                        continue

                    # Check for type and default value
                    prop_match = re.match(r'(\w+)(?:\s*:\s*(\w+))?\s*=\s*(.+)', prop)
                    if prop_match:
                        prop_name = prop_match.group(1)
                        prop_type = prop_match.group(2)  # May be None
                        prop_value = prop_match.group(3)

                        # Convert value based on type
                        if prop_type == 'int' or prop_value.isdigit():
                            value = int(prop_value)
                        elif prop_type == 'float' or '.' in prop_value and prop_value.replace('.', '', 1).isdigit():
                            value = float(prop_value)
                        elif prop_type == 'boolean' or prop_value in ('true', 'false'):
                            value = prop_value.lower() == 'true'
                        elif prop_value.startswith('"') and prop_value.endswith('"'):
                            value = prop_value[1:-1]
                        else:
                            value = prop_value

                        state_dict[prop_name] = value

                class_dict['state'] = state_dict

            # Extract methods
            method_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*(\w+))?\s*{([^}]*)}'
            for method_match in re.finditer(method_pattern, component_body, re.DOTALL):
                method_name = method_match.group(1)
                method_params = method_match.group(2)
                method_return_type = method_match.group(3)  # May be None
                method_body = method_match.group(4)

                # Create a method function
                method_code = f"def {method_name}(self, {method_params}):\n"
                for line in method_body.split('\n'):
                    method_code += f"    {line}\n"

                # Compile the method
                method_globals = {}
                exec(method_code, method_globals)

                # Add the method to the class
                class_dict[method_name] = method_globals[method_name]

            # Create the class
            components[component_name] = type(component_name, (), class_dict)

        return components

    def _update_instance(self, instance: ComponentInstance, old_class: type, new_class: type) -> None:
        """Update a component instance with a new class."""
        try:
            # Save the state
            old_state = instance.state.copy() if hasattr(instance, 'state') else {}

            # Update the class
            instance.__class__ = new_class

            # Restore the state
            if hasattr(instance, 'state'):
                instance.state.update(old_state)

            # Call onUpdate if it exists
            if hasattr(instance, 'onUpdate') and callable(getattr(instance, 'onUpdate')):
                instance.onUpdate(old_state)

            logger.debug(f"Updated instance of {new_class.__name__}")
        except Exception as e:
            logger.error(f"Error updating instance of {new_class.__name__}: {e}")
            logger.error(traceback.format_exc())

class RuntimeEnvironment:
    """
    Runtime environment for the Mono language.
    """
    def __init__(self, max_workers: int = 5, gc_ttl: timedelta = timedelta(seconds=30)):
        self.scheduler = Scheduler(max_workers=max_workers)
        self.garbage_collector = GarbageCollector(scheduler=self.scheduler, ttl=gc_ttl)
        self.hot_reloader = HotReloader(scheduler=self.scheduler)
        self.running = False

    def start(self) -> None:
        """Start the runtime environment."""
        if self.running:
            return

        self.running = True

        # Start the scheduler
        self.scheduler.start()

        # Start the garbage collector
        self.garbage_collector.start()

        # Start the hot reloader
        self.hot_reloader.start()

        logger.info("Runtime environment started")

    def stop(self) -> None:
        """Stop the runtime environment."""
        if not self.running:
            return

        self.running = False

        # Stop the hot reloader
        self.hot_reloader.stop()

        # Stop the garbage collector
        self.garbage_collector.stop()

        # Stop the scheduler
        self.scheduler.stop()

        logger.info("Runtime environment stopped")

    def register_component(self, component_class: type, file_path: str) -> None:
        """Register a component class with the runtime environment."""
        self.hot_reloader.register_component(component_class, file_path)

    def register_instance(self, instance: ComponentInstance) -> None:
        """Register a component instance with the runtime environment."""
        self.garbage_collector.register(instance)
        self.hot_reloader.register_instance(instance)

    def mount_component(self, instance: ComponentInstance) -> None:
        """Mount a component instance."""
        self.garbage_collector.mount(instance)

        # Call onMount if it exists
        if hasattr(instance, 'onMount') and callable(getattr(instance, 'onMount')):
            self.scheduler.schedule(
                callback=lambda: instance.onMount(),
                priority=TaskPriority.NORMAL,
                component=instance,
                name=f"Mount-{instance.__class__.__name__}"
            )

    def update_component(self, instance: ComponentInstance, old_state: Dict[str, Any]) -> None:
        """Update a component instance."""
        self.garbage_collector.update(instance)

        # Call onUpdate if it exists
        if hasattr(instance, 'onUpdate') and callable(getattr(instance, 'onUpdate')):
            self.scheduler.schedule(
                callback=lambda: instance.onUpdate(old_state),
                priority=TaskPriority.NORMAL,
                component=instance,
                name=f"Update-{instance.__class__.__name__}"
            )

    def unmount_component(self, instance: ComponentInstance) -> None:
        """Unmount a component instance."""
        self.garbage_collector.unmount(instance)

        # Call onUnmount if it exists
        if hasattr(instance, 'onUnmount') and callable(getattr(instance, 'onUnmount')):
            self.scheduler.schedule(
                callback=lambda: instance.onUnmount(),
                priority=TaskPriority.NORMAL,
                component=instance,
                name=f"Unmount-{instance.__class__.__name__}"
            )

    def watch_directory(self, path: str) -> None:
        """Watch a directory for changes."""
        self.hot_reloader.watch(path)

    def schedule_task(self, callback: TaskCallback, priority: TaskPriority = TaskPriority.NORMAL,
                     component: Optional[ComponentInstance] = None, name: str = "") -> None:
        """Schedule a task for execution."""
        self.scheduler.schedule(callback, priority, component, name)

# Global runtime environment
_runtime_env = RuntimeEnvironment()

def get_runtime_environment() -> RuntimeEnvironment:
    """Get the global runtime environment."""
    return _runtime_env

def start_runtime() -> None:
    """Start the global runtime environment."""
    _runtime_env.start()

def stop_runtime() -> None:
    """Stop the global runtime environment."""
    _runtime_env.stop()

def register_component(component_class: type, file_path: str) -> None:
    """Register a component class with the runtime environment."""
    _runtime_env.register_component(component_class, file_path)

def register_instance(instance: ComponentInstance) -> None:
    """Register a component instance with the runtime environment."""
    _runtime_env.register_instance(instance)

def mount_component(instance: ComponentInstance) -> None:
    """Mount a component instance."""
    _runtime_env.mount_component(instance)

def update_component(instance: ComponentInstance, old_state: Dict[str, Any]) -> None:
    """Update a component instance."""
    _runtime_env.update_component(instance, old_state)

def unmount_component(instance: ComponentInstance) -> None:
    """Unmount a component instance."""
    _runtime_env.unmount_component(instance)

def watch_directory(path: str) -> None:
    """Watch a directory for changes."""
    _runtime_env.watch_directory(path)

def schedule_task(callback: TaskCallback, priority: TaskPriority = TaskPriority.NORMAL,
                 component: Optional[ComponentInstance] = None, name: str = "") -> None:
    """Schedule a task for execution."""
    _runtime_env.schedule_task(callback, priority, component, name)
