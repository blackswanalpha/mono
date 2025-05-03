"""
Mono Concurrent - Concurrent Mono language interpreter

This module implements concurrency and parallelism features for the Mono language:
- Component threads (lightweight threads for components)
- Thread safety (immutability and message passing)
- Synchronization (channels and mutexes)
- Parallel execution (parallel keyword)
- Dependency management
"""

import re
import threading
import queue
import concurrent.futures
import time
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union

# Import from collections implementation for advanced data structures
from lib.mono_collections import BOOLEAN_OPERATORS

# Thread-local storage for component instances
thread_local = threading.local()

class Channel:
    """
    A thread-safe communication channel between components.
    """
    def __init__(self, buffer_size: int = 0):
        self.buffer_size = buffer_size
        if buffer_size > 0:
            self.queue = queue.Queue(maxsize=buffer_size)
        else:
            self.queue = queue.Queue()
        self.closed = False

    def send(self, value: Any) -> bool:
        """Send a value to the channel."""
        if self.closed:
            raise ValueError("Cannot send on closed channel")
        self.queue.put(value)
        return True

    def receive(self, timeout: Optional[float] = None) -> Any:
        """Receive a value from the channel."""
        if self.closed and self.queue.empty():
            return None
        try:
            value = self.queue.get(timeout=timeout)
            return value
        except queue.Empty:
            return None

    def close(self) -> None:
        """Close the channel."""
        self.closed = True

    def __str__(self):
        return f"Channel(buffer_size={self.buffer_size}, closed={self.closed})"

class Mutex:
    """
    A mutual exclusion lock for thread synchronization.
    """
    def __init__(self):
        self.lock = threading.RLock()

    def acquire(self) -> bool:
        """Acquire the lock."""
        return self.lock.acquire()

    def release(self) -> None:
        """Release the lock."""
        self.lock.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

class ThreadedInstance:
    """
    Represents a threaded instance of a component in the Concurrent Mono language.
    """
    def __init__(self, component: Dict[str, Any], interpreter: 'ConcurrentInterpreter'):
        self.component = component
        self.interpreter = interpreter
        self.state = component['state'].copy()
        self.state_lock = threading.RLock()
        self.methods = {}
        self.is_parallel = component.get('is_parallel', False)
        self.thread = None
        self.thread_id = None
        self.mailbox = queue.Queue()
        self.channels = {}
        self.mutexes = {}
        self.running = False
        self.error = None

        # Add methods
        for name, method in component['methods'].items():
            # Create a closure for each method
            method_body = method['body']
            params = method['params']

            def method_factory(method_name, body, method_params):
                def method(*args):
                    try:
                        # Create local scope for method execution
                        local_vars = {}

                        # Add parameters to local scope
                        for i, param_name in enumerate(method_params):
                            if i < len(args):
                                local_vars[param_name] = args[i]

                        # Execute the method body
                        return self.interpreter.execute_code(body, self, local_vars)
                    except Exception as e:
                        self.error = str(e)
                        if 'onError' in component['methods']:
                            self.interpreter.execute_lifecycle_hook('onError', self)
                        else:
                            raise
                return method

            # Bind the method to the instance
            bound_method = method_factory(name, method_body, params)
            self.methods[name] = bound_method

        # Add lifecycle hooks if they exist
        if 'constructor' in component['methods']:
            self.interpreter.execute_lifecycle_hook('constructor', self)

    def __getattr__(self, name):
        """Get a method or create a mutex/channel on demand."""
        if name in self.methods:
            return self.methods[name]
        elif name.startswith('mutex_'):
            mutex_name = name[6:]  # Remove 'mutex_' prefix
            if mutex_name not in self.mutexes:
                self.mutexes[mutex_name] = Mutex()
            return self.mutexes[mutex_name]
        elif name.startswith('channel_'):
            channel_name = name[8:]  # Remove 'channel_' prefix
            if channel_name not in self.channels:
                self.channels[channel_name] = Channel()
            return self.channels[channel_name]
        # For debugging
        print(f"Method {name} not found in {self.component['name']}. Available methods: {list(self.methods.keys())}")
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def get_state(self, key: str, default: Any = None) -> Any:
        """Thread-safe state access."""
        with self.state_lock:
            print(f"Getting state {key} from {self.component['name']}, state: {self.state}")
            return self.state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """Thread-safe state update."""
        with self.state_lock:
            old_state = self.state.copy()
            self.state[key] = value
            print(f"Set state {key} to {value} in {self.component['name']}, new state: {self.state}")

            # Call onUpdate lifecycle hook if it exists
            if 'onUpdate' in self.component['methods']:
                self.interpreter.execute_lifecycle_hook('onUpdate', self, old_state)

    def update_state(self, new_state: Dict[str, Any]) -> None:
        """Thread-safe bulk state update."""
        with self.state_lock:
            old_state = self.state.copy()
            for key, value in new_state.items():
                self.state[key] = value
            print(f"Updated state in {self.component['name']}, new state: {self.state}")

            # Call onUpdate lifecycle hook if it exists
            if 'onUpdate' in self.component['methods']:
                self.interpreter.execute_lifecycle_hook('onUpdate', self, old_state)

    def send_message(self, message: Any) -> None:
        """Send a message to this component's mailbox."""
        self.mailbox.put(message)

    def receive_message(self, timeout: Optional[float] = None) -> Tuple[Any, bool]:
        """Receive a message from this component's mailbox."""
        try:
            message = self.mailbox.get(timeout=timeout)
            return message, True
        except queue.Empty:
            return None, False

    def start(self) -> None:
        """Start the component in its own thread."""
        if self.is_parallel and not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()
            self.thread_id = self.thread.ident

    def _run(self) -> None:
        """Main thread function."""
        # Set thread-local instance
        thread_local.instance = self

        # Call onMount lifecycle hook if it exists
        if 'onMount' in self.component['methods']:
            self.interpreter.execute_lifecycle_hook('onMount', self)

        # Call start method if it exists
        if 'start' in self.methods:
            self.methods['start']()

        # Process messages until stopped
        while self.running:
            message, success = self.receive_message(timeout=0.1)
            if success:
                if message == 'stop':
                    self.running = False
                elif isinstance(message, tuple) and len(message) >= 2:
                    method_name, args = message[0], message[1:]
                    if method_name in self.methods:
                        self.methods[method_name](*args)

    def stop(self) -> None:
        """Stop the component thread."""
        if self.running:
            self.send_message('stop')
            self.running = False
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=1.0)

            # Call onUnmount lifecycle hook if it exists
            if 'onUnmount' in self.component['methods']:
                self.interpreter.execute_lifecycle_hook('onUnmount', self)

class ConcurrentInterpreter:
    """
    Concurrent Mono language interpreter with support for concurrency and parallelism.
    """
    def __init__(self):
        self.components = {}
        self.instances = {}
        self.current_instance = None
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        self.global_channels = {}
        self.global_mutexes = {}

    def parse_file(self, filename: str) -> None:
        """
        Parse a Concurrent Mono script file.
        """
        with open(filename, 'r') as f:
            content = f.read()

        print(f"Parsing file: {filename}")

        # Remove comments
        content = re.sub(r'//.*', '', content)

        # Find components
        component_pattern = r'(?:parallel\s+)?component\s+(\w+)\s*{'
        component_starts = [(m.group(1), m.start()) for m in re.finditer(component_pattern, content)]

        print(f"Found components: {[comp_name for comp_name, _ in component_starts]}")

        for i, (comp_name, start_pos) in enumerate(component_starts):
            # Find the end of the component
            # We need to count braces to handle nested components
            brace_count = 1
            pos = content.find('{', start_pos) + 1

            while brace_count > 0 and pos < len(content):
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                pos += 1

            if brace_count > 0:
                raise ValueError(f"Syntax error: Missing closing brace for component {comp_name}")

            end_pos = pos - 1

            # Extract the component body
            comp_body = content[start_pos:end_pos+1]

            # Check if this is a parallel component
            is_parallel = 'parallel component' in comp_body.lower()

            print(f"Parsing component {comp_name} (parallel: {is_parallel})")

            # Parse the component
            self._parse_component(comp_name, comp_body, is_parallel)

    def _parse_component(self, name: str, body: str, is_parallel: bool = False) -> None:
        """
        Parse a component definition.
        """
        component = {
            'name': name,
            'state': {},
            'methods': {},
            'is_parallel': is_parallel
        }

        print(f"Component {name} body length: {len(body)}")

        # Extract state block
        state_match = re.search(r'state\s*{([^}]*)}', body, re.DOTALL)
        if state_match:
            state_block = state_match.group(1).strip()
            for line in state_block.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # Parse state property
                prop_match = re.match(r'(\w+)(?:\s*:\s*(\w+))?\s*(?:=\s*(.+))?', line.rstrip(','))
                if prop_match:
                    prop_name = prop_match.group(1)
                    prop_type = prop_match.group(2)  # May be None
                    prop_value = prop_match.group(3)  # May be None

                    # Set default values based on type
                    if prop_value:
                        # Try to evaluate the value
                        try:
                            value = eval(prop_value)
                        except:
                            value = prop_value
                    else:
                        # Default values based on type
                        if prop_type == 'int':
                            value = 0
                        elif prop_type == 'float':
                            value = 0.0
                        elif prop_type == 'string':
                            value = ""
                        elif prop_type == 'bool':
                            value = False
                        else:
                            value = None

                    component['state'][prop_name] = value

        # Extract methods
        method_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*(\w+))?\s*{'
        method_starts = [(m.group(1), m.group(2), m.group(3), m.start()) for m in re.finditer(method_pattern, body)]

        print(f"Found methods in {name}: {[method[0] for method in method_starts]}")

        for method_name, params_str, return_type, method_start_pos in method_starts:
            # Find the method body
            method_brace_count = 1
            method_open_brace_pos = body.find('{', method_start_pos)
            method_pos = method_open_brace_pos + 1

            while method_brace_count > 0 and method_pos < len(body):
                if body[method_pos] == '{':
                    method_brace_count += 1
                elif body[method_pos] == '}':
                    method_brace_count -= 1
                method_pos += 1

            # Extract the method body
            method_body = body[method_open_brace_pos+1:method_pos-1].strip()

            # Parse parameters
            params = []
            if params_str:
                for param in params_str.split(','):
                    param = param.strip()
                    if param:
                        # Check for type annotations
                        param_parts = param.split(':')
                        param_name = param_parts[0].strip()
                        params.append(param_name)

            component['methods'][method_name] = {
                'params': params,
                'return_type': return_type,
                'body': method_body
            }

        self.components[name] = component

    def create_instance(self, component_name: str) -> ThreadedInstance:
        """
        Create an instance of a component.
        """
        if component_name not in self.components:
            raise ValueError(f"Component {component_name} not found")

        component = self.components[component_name]
        instance = ThreadedInstance(component, self)

        # Store the instance
        if component_name not in self.instances:
            self.instances[component_name] = []
        self.instances[component_name].append(instance)

        return instance

    def execute_lifecycle_hook(self, hook_name: str, instance: ThreadedInstance, *args) -> Any:
        """
        Execute a lifecycle hook on a component instance.
        """
        if hook_name in instance.component['methods']:
            method = instance.methods[hook_name]
            return method(*args)
        return None

    def execute_code(self, code: str, instance: ThreadedInstance, local_vars: Dict[str, Any]) -> Any:
        """
        Execute a block of code.
        """
        # Split the code into lines
        lines = code.split('\n')
        result = None

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            i += 1

            if not line:
                continue

            # Variable declaration
            var_match = re.match(r'var\s+(\w+)(?:\s*:\s*(\w+))?\s*=\s*(.+?);?$', line)
            if var_match:
                var_name = var_match.group(1)
                var_type = var_match.group(2)  # May be None
                var_expr = var_match.group(3)

                # Handle component instantiation
                new_match = re.match(r'new\s+(\w+)\(\)', var_expr)
                if new_match:
                    comp_name = new_match.group(1)
                    local_vars[var_name] = self.create_instance(comp_name)

                    # Start the component if it's parallel
                    if local_vars[var_name].is_parallel:
                        local_vars[var_name].start()
                else:
                    # Handle channel creation
                    channel_match = re.match(r'Channel\((\d*)\)', var_expr)
                    if channel_match:
                        buffer_size = int(channel_match.group(1)) if channel_match.group(1) else 0
                        channel = Channel(buffer_size)
                        # Store the channel in a global dictionary to prevent garbage collection
                        self.global_channels[var_name] = channel
                        local_vars[var_name] = channel
                    # Handle mutex creation
                    elif var_expr.strip() == 'Mutex()':
                        mutex = Mutex()
                        # Store the mutex in a global dictionary to prevent garbage collection
                        self.global_mutexes[var_name] = mutex
                        local_vars[var_name] = mutex
                    # Regular variable assignment
                    else:
                        try:
                            value = self.evaluate_expression(var_expr, local_vars, instance)
                            local_vars[var_name] = value
                        except:
                            local_vars[var_name] = var_expr
                continue

            # Return statement
            return_match = re.match(r'return\s+(.+?);?$', line)
            if return_match:
                expr = return_match.group(1)
                result = self.evaluate_expression(expr, local_vars, instance)
                break

            # If statement
            if_match = re.match(r'if\s*\((.+?)\)\s*{', line)
            if if_match:
                condition = if_match.group(1)
                condition_value = self.evaluate_expression(condition, local_vars, instance)

                # Find the matching closing brace
                if_block = ""
                brace_count = 1
                if_start = i

                while i < len(lines) and brace_count > 0:
                    if_block += lines[i] + '\n'
                    if '{' in lines[i]:
                        brace_count += lines[i].count('{')
                    if '}' in lines[i]:
                        brace_count -= lines[i].count('}')
                    i += 1

                # Remove the last closing brace
                if_block = if_block.rstrip('}\n').strip()

                # Check for else block
                else_block = ""
                if i < len(lines) and lines[i].strip().startswith('else'):
                    i += 1  # Skip the else line

                    # Check if it's a simple else or else if
                    if lines[i-1].strip() == 'else {':
                        # Simple else block
                        brace_count = 1
                        while i < len(lines) and brace_count > 0:
                            else_block += lines[i] + '\n'
                            if '{' in lines[i]:
                                brace_count += lines[i].count('{')
                            if '}' in lines[i]:
                                brace_count -= lines[i].count('}')
                            i += 1

                        # Remove the last closing brace
                        else_block = else_block.rstrip('}\n').strip()

                # Execute the appropriate block
                if condition_value:
                    if if_block:
                        result = self.execute_code(if_block, instance, local_vars)
                else:
                    if else_block:
                        result = self.execute_code(else_block, instance, local_vars)

                continue

            # For loop
            for_match = re.match(r'for\s*\((.+?);(.+?);(.+?)\)\s*{', line)
            if for_match:
                init_stmt = for_match.group(1).strip()
                condition = for_match.group(2).strip()
                update_stmt = for_match.group(3).strip()

                # Find the loop body
                loop_body = ""
                brace_count = 1
                loop_start = i

                while i < len(lines) and brace_count > 0:
                    loop_body += lines[i] + '\n'
                    if '{' in lines[i]:
                        brace_count += lines[i].count('{')
                    if '}' in lines[i]:
                        brace_count -= lines[i].count('}')
                    i += 1

                # Remove the last closing brace
                loop_body = loop_body.rstrip('}\n').strip()

                # Execute the initialization statement
                if init_stmt.startswith('var '):
                    var_match = re.match(r'var\s+(\w+)(?:\s*:\s*(\w+))?\s*=\s*(.+)', init_stmt)
                    if var_match:
                        var_name = var_match.group(1)
                        var_type = var_match.group(2)  # May be None
                        var_expr = var_match.group(3)
                        local_vars[var_name] = self.evaluate_expression(var_expr, local_vars, instance)
                else:
                    # Handle other initialization statements
                    pass

                # Execute the loop
                while self.evaluate_expression(condition, local_vars, instance):
                    # Execute the loop body
                    loop_result = self.execute_code(loop_body, instance, local_vars)

                    # Handle early return from the loop
                    if loop_result is not None:
                        result = loop_result
                        break

                    # Execute the update statement
                    if '=' in update_stmt:
                        # Assignment update
                        update_parts = update_stmt.split('=')
                        var_name = update_parts[0].strip()
                        var_expr = update_parts[1].strip()
                        local_vars[var_name] = self.evaluate_expression(var_expr, local_vars, instance)
                    else:
                        # Increment/decrement update
                        if '+=' in update_stmt:
                            update_parts = update_stmt.split('+=')
                            var_name = update_parts[0].strip()
                            var_expr = update_parts[1].strip()
                            local_vars[var_name] += self.evaluate_expression(var_expr, local_vars, instance)
                        elif '-=' in update_stmt:
                            update_parts = update_stmt.split('-=')
                            var_name = update_parts[0].strip()
                            var_expr = update_parts[1].strip()
                            local_vars[var_name] -= self.evaluate_expression(var_expr, local_vars, instance)
                        elif '++' in update_stmt:
                            var_name = update_stmt.replace('++', '').strip()
                            local_vars[var_name] += 1
                        elif '--' in update_stmt:
                            var_name = update_stmt.replace('--', '').strip()
                            local_vars[var_name] -= 1

                continue

            # While loop
            while_match = re.match(r'while\s*\((.+?)\)\s*{', line)
            if while_match:
                condition = while_match.group(1)

                # Find the loop body
                loop_body = ""
                brace_count = 1
                loop_start = i

                while i < len(lines) and brace_count > 0:
                    loop_body += lines[i] + '\n'
                    if '{' in lines[i]:
                        brace_count += lines[i].count('{')
                    if '}' in lines[i]:
                        brace_count -= lines[i].count('}')
                    i += 1

                # Remove the last closing brace
                loop_body = loop_body.rstrip('}\n').strip()

                # Execute the loop
                while self.evaluate_expression(condition, local_vars, instance):
                    # Execute the loop body
                    loop_result = self.execute_code(loop_body, instance, local_vars)

                    # Handle early return from the loop
                    if loop_result is not None:
                        result = loop_result
                        break

                continue

            # Parallel execution
            parallel_match = re.match(r'parallel\s*\((.+?)\)\s*{', line)
            if parallel_match:
                components_expr = parallel_match.group(1)
                components = [c.strip() for c in components_expr.split(',')]

                # Find the parallel block
                parallel_block = ""
                brace_count = 1
                parallel_start = i

                while i < len(lines) and brace_count > 0:
                    parallel_block += lines[i] + '\n'
                    if '{' in lines[i]:
                        brace_count += lines[i].count('{')
                    if '}' in lines[i]:
                        brace_count -= lines[i].count('}')
                    i += 1

                # Remove the last closing brace
                parallel_block = parallel_block.rstrip('}\n').strip()

                # Execute the parallel block for each component
                futures = []
                for comp_name in components:
                    if comp_name in local_vars:
                        comp_instance = local_vars[comp_name]
                        future = self.thread_pool.submit(
                            self.execute_code,
                            parallel_block,
                            comp_instance,
                            local_vars.copy()
                        )
                        futures.append(future)

                # Wait for all futures to complete
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future_result = future.result()
                        if future_result is not None:
                            result = future_result
                    except Exception as e:
                        print(f"Error in parallel execution: {e}")

                continue

            # Method call
            method_call_match = re.match(r'(\w+)\.(\w+)\(\);?$', line) or re.match(r'(\w+)\.(\w+)\((.*?)\);?$', line)
            if method_call_match:
                obj_name = method_call_match.group(1)
                method_name = method_call_match.group(2)
                args_str = method_call_match.group(3) if method_call_match.lastindex >= 3 else ''
                print(f"Executing method call: {obj_name}.{method_name}({args_str})")

                # Get the object
                obj = None
                if obj_name == 'this':
                    obj = instance
                elif obj_name in local_vars:
                    obj = local_vars[obj_name]

                if obj:
                    # Parse arguments
                    args = []
                    if args_str:
                        # Simple argument parsing
                        for arg in args_str.split(','):
                            arg = arg.strip()
                            try:
                                # Try to evaluate the argument
                                value = self.evaluate_expression(arg, local_vars, instance)
                                args.append(value)
                            except:
                                args.append(arg)

                    # Call the method
                    if hasattr(obj, method_name):
                        method = getattr(obj, method_name)
                        method(*args)
                continue

            # State update
            state_update_match = re.match(r'this\.state\.(\w+)\s*=\s*(.+?);?$', line)
            if state_update_match:
                prop_name = state_update_match.group(1)
                value_expr = state_update_match.group(2)

                # Evaluate the expression
                value = self.evaluate_expression(value_expr, local_vars, instance)

                # Update the state
                instance.set_state(prop_name, value)
                continue

            # Print statement
            print_match = re.match(r'print\s+(.+?);?$', line)
            if print_match:
                expr = print_match.group(1)

                # Check if it's a string literal
                if expr.startswith('"') and expr.endswith('"'):
                    print(expr[1:-1])
                # Handle string concatenation with +
                elif '+' in expr:
                    parts = expr.split(' + ')
                    result = ''
                    for part in parts:
                        part = part.strip()
                        if part.startswith('"') and part.endswith('"'):
                            result += part[1:-1]
                        else:
                            value = self.evaluate_expression(part, local_vars, instance)
                            result += str(value)
                    print(result)
                else:
                    # Evaluate the expression
                    try:
                        value = self.evaluate_expression(expr, local_vars, instance)
                        print(value)
                    except Exception as e:
                        print(f"Error evaluating expression: {expr}")
                        print(e)
                continue

            # Sleep statement
            sleep_match = re.match(r'sleep\s*\((.+?)\);?$', line)
            if sleep_match:
                duration_expr = sleep_match.group(1)
                duration = self.evaluate_expression(duration_expr, local_vars, instance)
                time.sleep(duration)
                continue

        return result

    def evaluate_expression(self, expr: str, local_vars: Dict[str, Any], instance = None) -> Any:
        """
        Evaluate an expression.
        """
        expr = expr.strip()

        # String literal
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]

        # Numeric literal
        if expr.isdigit():
            return int(expr)
        if re.match(r'^-?\d+(\.\d+)?$', expr):
            return float(expr)

        # Boolean literal
        if expr == 'true':
            return True
        if expr == 'false':
            return False

        # Variable reference
        if expr in local_vars:
            return local_vars[expr]

        # Array access
        array_access = re.match(r'(\w+)\[(\d+)\]', expr)
        if array_access:
            array_name = array_access.group(1)
            index = int(array_access.group(2))

            if array_name in local_vars and isinstance(local_vars[array_name], list):
                array = local_vars[array_name]
                if 0 <= index < len(array):
                    return array[index]
                else:
                    print(f"Error: Index {index} out of bounds for array {array_name}")
                    return None
            else:
                print(f"Error: Array {array_name} not found")
                return None

        # Dictionary access
        dict_access = re.match(r'(\w+)\[\"(.*?)\"\]', expr)
        if dict_access:
            dict_name = dict_access.group(1)
            key = dict_access.group(2)

            if dict_name in local_vars and isinstance(local_vars[dict_name], dict):
                dictionary = local_vars[dict_name]
                if key in dictionary:
                    return dictionary[key]
                else:
                    print(f"Error: Key '{key}' not found in dictionary {dict_name}")
                    return None
            else:
                print(f"Error: Dictionary {dict_name} not found")
                return None

        # Arithmetic operations
        if '+' in expr and not expr.startswith('"') and not expr.endswith('"'):
            parts = expr.split('+')
            if len(parts) == 2:
                left = self.evaluate_expression(parts[0].strip(), local_vars, instance)
                right = self.evaluate_expression(parts[1].strip(), local_vars, instance)

                # Handle numeric addition
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                # Handle string concatenation
                elif isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)

        # Property access
        if '.' in expr:
            parts = expr.split('.')
            if parts[0] == 'this' and parts[1] == 'state':
                if instance and hasattr(instance, 'state'):
                    return instance.get_state(parts[2])
            elif parts[0] in local_vars:
                obj = local_vars[parts[0]]
                if isinstance(obj, ThreadedInstance) and parts[1] == 'state':
                    return obj.get_state(parts[2])
                elif isinstance(obj, dict) and 'state' in obj:
                    if parts[2] in obj['state']:
                        return obj['state'][parts[2]]

            # Debug output for property access
            print(f"Property access: {expr}, parts: {parts}")
            if parts[0] in local_vars:
                obj_type = type(local_vars[parts[0]])
                print(f"Object type: {obj_type}")
                if hasattr(local_vars[parts[0]], 'state'):
                    print(f"Object has state: {local_vars[parts[0]].state}")

            # If we can't resolve the property access, just return 0 for now
            return 0

        # Component instantiation
        new_match = re.match(r'new\s+(\w+)\(\)', expr)
        if new_match:
            component_name = new_match.group(1)
            return self.create_instance(component_name)

        # Method call
        print(f"Checking for method call: {expr}")
        method_call = re.match(r'(\w+)\.(\w+)\(\)', expr) or re.match(r'(\w+)\.(\w+)\((.*?)\)', expr)
        if method_call:
            obj_name = method_call.group(1)
            method_name = method_call.group(2)
            args_str = method_call.group(3) if method_call.lastindex >= 3 else ''
            print(f"Found method call: {obj_name}.{method_name}({args_str})")

            # Get the object
            obj = None
            if obj_name == 'this':
                obj = instance
            elif obj_name in local_vars:
                obj = local_vars[obj_name]

            if not obj:
                print(f"Error: Object {obj_name} not found")
                return None

            # Parse arguments
            args = []
            if args_str:
                for arg in args_str.split(','):
                    arg = arg.strip()
                    # Handle nested method calls in arguments
                    if '(' in arg and ')' in arg and '.' in arg:
                        args.append(self.evaluate_expression(arg, local_vars, instance))
                    else:
                        # Convert numeric literals
                        if arg.isdigit():
                            args.append(int(arg))
                        elif re.match(r'^-?\d+(\.\d+)?$', arg):
                            args.append(float(arg))
                        else:
                            args.append(self.evaluate_expression(arg, local_vars, instance))

            # Call the method
            if isinstance(obj, ThreadedInstance):
                if method_name in obj.methods:
                    return obj.methods[method_name](*args)
                else:
                    print(f"Available methods in {obj_name}: {list(obj.methods.keys())}")
                    print(f"Error: Method {method_name} not found in {obj_name}")
                    return None
            elif isinstance(obj, dict) and 'methods' in obj and method_name in obj['methods']:
                return self.execute_method(obj, method_name, args)
            else:
                print(f"Error: Method {method_name} not found in {obj_name} of type {type(obj)}")
                return None

        # Boolean expression
        for op in sorted(BOOLEAN_OPERATORS.keys(), key=len, reverse=True):
            if op in expr:
                parts = expr.split(op, 1)
                left = self.evaluate_expression(parts[0], local_vars, instance)
                right = self.evaluate_expression(parts[1], local_vars, instance)

                # Apply the operator
                try:
                    return BOOLEAN_OPERATORS[op](left, right)
                except Exception as e:
                    print(f"Error in boolean operation: {e}")
                    return False

        # If we can't evaluate the expression, return it as is
        return expr

    def run(self) -> None:
        """
        Run the parsed Concurrent Mono script.
        """
        if 'Main' not in self.components:
            print("Error: Main component not found")
            return

        # Create Main instance
        main = self.create_instance('Main')
        self.current_instance = main

        # Call start method
        if 'start' in main.methods:
            main.methods['start']()
        else:
            print("Error: start method not found")

        # Wait for all parallel components to finish
        for _, instances in self.instances.items():
            for instance in instances:
                if instance.is_parallel and instance.thread and instance.thread.is_alive():
                    instance.stop()

        # Shutdown the thread pool
        self.thread_pool.shutdown(wait=True)

def run_mono_file(file_path: str) -> bool:
    """
    Run a Concurrent Mono script file and display the results.
    """
    try:
        interpreter = ConcurrentInterpreter()
        interpreter.parse_file(file_path)
        interpreter.run()
        return True
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return False
    except Exception as e:
        print(f"Error executing Mono script: {e}")
        import traceback
        traceback.print_exc()
        return False
