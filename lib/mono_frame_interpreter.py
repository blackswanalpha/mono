"""
Mono Frame Interpreter - Interpreter for Mono with frame support
"""

import re
import os
import time
import threading
import concurrent.futures
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union

from lib.mono_frames import Frame, FrameRegistry, get_frame_registry
from lib.mono_communication import EventEmitter, ServiceRegistry, ContextRegistry
from lib.mono_communication import get_event_emitter, get_service_registry, get_context_registry

class FrameComponent:
    """
    Represents a component with frame support in the Mono language.
    """
    def __init__(self, name: str):
        self.name = name
        self.state = {}
        self.methods = {}
        self.frame = None

class FrameComponentInstance:
    """
    Represents an instance of a component with frame support.
    """
    def __init__(self, component: FrameComponent, interpreter, frame: Optional[Frame] = None):
        self.component = component
        self.interpreter = interpreter
        self.state = component.state.copy()
        self.frame = frame
        self.mounted = False
        
        # Add methods
        for name, body in component.methods.items():
            # Create a closure for each method
            method_body = body  # Create a local copy for the closure
            
            def method_factory(body):
                def method(*args):
                    return interpreter.execute_method(body, self, args)
                return method
            
            # Bind the method to the instance
            bound_method = method_factory(method_body)
            setattr(self, name, bound_method)
    
    def setState(self, new_state: Dict[str, Any]) -> None:
        """Update the state of the component instance."""
        old_state = self.state.copy()
        for key, value in new_state.items():
            self.state[key] = value
        
        # Call onUpdate lifecycle hook if it exists
        if 'onUpdate' in self.component.methods:
            self.interpreter.execute_method(self.component.methods['onUpdate'], self, [old_state])
    
    def mount(self) -> None:
        """Mount the component instance."""
        if self.mounted:
            return
        
        # Call onMount lifecycle hook if it exists
        if 'onMount' in self.component.methods:
            self.interpreter.execute_method(self.component.methods['onMount'], self)
        
        self.mounted = True
    
    def unmount(self) -> None:
        """Unmount the component instance."""
        if not self.mounted:
            return
        
        # Call onUnmount lifecycle hook if it exists
        if 'onUnmount' in self.component.methods:
            self.interpreter.execute_method(self.component.methods['onUnmount'], self)
        
        self.mounted = False
    
    # Frame-specific methods
    
    def getFrameState(self, key: str, default: Any = None) -> Any:
        """Get a value from the frame state."""
        if self.frame:
            return self.frame.get_frame_state(key, default)
        return default
    
    def setFrameState(self, key: str, value: Any) -> None:
        """Set a value in the frame state."""
        if self.frame:
            self.frame.set_frame_state(key, value)
    
    def subscribeToFrameState(self, callback: Callable) -> None:
        """Subscribe to frame state changes."""
        if self.frame:
            self.frame.subscribe_to_frame_state(self, callback)
    
    def unsubscribeFromFrameState(self) -> None:
        """Unsubscribe from frame state changes."""
        if self.frame:
            self.frame.unsubscribe_from_frame_state(self)
    
    def emitInFrame(self, event_name: str, data: Any = None) -> None:
        """Emit an event within the frame."""
        if self.frame:
            self.frame.emit_event(event_name, data)
    
    def onFrameEvent(self, event_name: str, callback: Callable) -> None:
        """Register an event listener in the frame."""
        if self.frame:
            self.frame.on_event(event_name, self, callback)
    
    def offFrameEvent(self, event_name: str) -> None:
        """Remove an event listener from the frame."""
        if self.frame:
            self.frame.off_event(event_name, self)
    
    def runInFrame(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Run a function in the frame's thread pool."""
        if self.frame:
            return self.frame.run_in_frame(func, *args, **kwargs)
        return None

class FrameInterpreter:
    """
    Mono language interpreter with support for frames.
    """
    def __init__(self):
        self.components: Dict[str, FrameComponent] = {}
        self.instances: Dict[str, List[FrameComponentInstance]] = {}
        self.variables: Dict[str, Any] = {}
        self.current_instance: Optional[FrameComponentInstance] = None
        self.frame_registry = get_frame_registry()
    
    def parse_file(self, file_path: str) -> None:
        """Parse a Mono script file."""
        with open(file_path, 'r') as f:
            content = f.read()
        self.parse(content)
    
    def parse(self, script: str) -> None:
        """Parse a Mono script and extract components with frame support."""
        # First, clean up the script by removing comments
        script = re.sub(r'//.*$', '', script, flags=re.MULTILINE)
        
        # Find all component definitions
        # We need to handle nested braces, so we'll use a different approach
        components = []
        
        # Find all component declarations
        component_matches = re.finditer(r'component\s+(\w+)\s*{', script)
        for comp_match in component_matches:
            comp_name = comp_match.group(1)
            start_pos = comp_match.end()
            
            # Find the matching closing brace
            brace_count = 1
            pos = start_pos
            
            while pos < len(script) and brace_count > 0:
                if script[pos] == '{':
                    brace_count += 1
                elif script[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            if brace_count == 0:
                # Extract the component body
                comp_body = script[start_pos:pos-1]
                components.append((comp_name, comp_body))
        
        # Process each component
        for comp_name, comp_body in components:
            # Create a new component
            component = FrameComponent(comp_name)
            
            # Extract state
            state_pattern = r'state\s*{([^}]*)}'
            state_match = re.search(state_pattern, comp_body)
            if state_match:
                state_body = state_match.group(1)
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
                        
                        component.state[prop_name] = value
                    else:
                        # Simple property without type or default value
                        prop_parts = prop.split(':')
                        if len(prop_parts) == 2:
                            prop_name = prop_parts[0].strip()
                            prop_type = prop_parts[1].strip()
                            component.state[prop_name] = None
                        else:
                            prop_name = prop.strip()
                            component.state[prop_name] = None
            
            # Find all function declarations
            function_matches = re.finditer(r'function\s+(\w+)', comp_body)
            for func_match in function_matches:
                method_name = func_match.group(1)
                
                # Find the opening brace after the function name
                start_pos = func_match.end()
                open_brace_pos = comp_body.find('{', start_pos)
                if open_brace_pos == -1:
                    continue
                
                # Extract parameters and return type
                params_str = comp_body[start_pos:open_brace_pos].strip()
                params = []
                return_type = None
                
                # Check for parameters
                params_match = re.search(r'\(([^)]*)\)', params_str)
                if params_match:
                    params_text = params_match.group(1)
                    if params_text:
                        for param in params_text.split(','):
                            param = param.strip()
                            if param:
                                param_parts = re.split(r'\s*:\s*', param)
                                params.append(param_parts[0])
                
                # Check for return type
                return_match = re.search(r':\s*(\w+)', params_str)
                if return_match:
                    return_type = return_match.group(1)
                
                # Find the matching closing brace
                brace_count = 1
                pos = open_brace_pos + 1
                method_body = ""
                
                while pos < len(comp_body) and brace_count > 0:
                    if comp_body[pos] == '{':
                        brace_count += 1
                    elif comp_body[pos] == '}':
                        brace_count -= 1
                    
                    if brace_count > 0:
                        method_body += comp_body[pos]
                    
                    pos += 1
                
                # Store the method
                component.methods[method_name] = {
                    'params': params,
                    'return_type': return_type,
                    'body': method_body
                }
            
            # Register the component
            self.components[comp_name] = component
    
    def run(self) -> None:
        """Run the parsed Mono script with frame support."""
        if 'Main' not in self.components:
            print("Error: Main component not found")
            return
        
        # Create Main instance
        main = FrameComponentInstance(self.components['Main'], self)
        self.instances['Main'] = [main]
        self.current_instance = main
        
        # Call start method
        if 'start' in self.components['Main'].methods:
            self.execute_method(self.components['Main'].methods['start'], main)
        else:
            print("Error: start method not found")
    
    def execute_method(self, method_info, instance, args=None):
        """Execute a method on a component instance."""
        # Local variables for this method execution
        local_vars = {}
        
        # Add arguments to local variables
        if args and len(args) > 0:
            for i, param_name in enumerate(method_info['params']):
                if i < len(args):
                    local_vars[param_name] = args[i]
        
        # Split into lines
        lines = method_info['body'].split('\n')
        result = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Variable declaration
            var_match = re.match(r'var\s+(\w+)(?:\s*:\s*(\w+))?\s*=\s*(.+?);?$', line)
            if var_match:
                var_name = var_match.group(1)
                var_type = var_match.group(2)  # May be None
                var_expr = var_match.group(3)
                
                # Component instantiation
                new_match = re.match(r'new\s+(\w+)\(\)', var_expr)
                if new_match:
                    comp_name = new_match.group(1)
                    if comp_name in self.components:
                        comp_instance = FrameComponentInstance(self.components[comp_name], self)
                        local_vars[var_name] = comp_instance
                        
                        # Add to instances
                        if comp_name not in self.instances:
                            self.instances[comp_name] = []
                        self.instances[comp_name].append(comp_instance)
                        
                        # Call constructor if it exists
                        if 'constructor' in self.components[comp_name].methods:
                            self.execute_method(self.components[comp_name].methods['constructor'], comp_instance)
                    else:
                        print(f"Error: Component {comp_name} not found")
                else:
                    # Simple value
                    local_vars[var_name] = self.evaluate_expression(var_expr, local_vars, instance)
            
            # Method call
            method_call = re.match(r'(\w+)\.(\w+)\((.*?)\);?$', line)
            if method_call:
                obj_name = method_call.group(1)
                method_name = method_call.group(2)
                args_str = method_call.group(3)
                
                # Get the object
                obj = None
                if obj_name == 'this':
                    obj = instance
                elif obj_name in local_vars:
                    obj = local_vars[obj_name]
                
                if not obj:
                    print(f"Error: Object {obj_name} not found")
                    continue
                
                # Parse arguments
                args = []
                if args_str:
                    for arg in args_str.split(','):
                        arg = arg.strip()
                        if arg.startswith('"') and arg.endswith('"'):
                            args.append(arg[1:-1])
                        elif arg.startswith("'") and arg.endswith("'"):
                            args.append(arg[1:-1])
                        elif arg == 'true':
                            args.append(True)
                        elif arg == 'false':
                            args.append(False)
                        elif arg.isdigit():
                            args.append(int(arg))
                        elif '.' in arg and arg.replace('.', '', 1).isdigit():
                            args.append(float(arg))
                        else:
                            args.append(self.evaluate_expression(arg, local_vars, instance))
                
                # Special methods for frame support
                if obj == instance:
                    if method_name == 'createFrame':
                        frame_name = args[0]
                        parent_name = args[1] if len(args) > 1 else None
                        self.frame_registry.create_frame(frame_name, parent_name)
                        continue
                    elif method_name == 'loadFrame':
                        frame_name = args[0]
                        frame = self.frame_registry.get_frame(frame_name)
                        if frame:
                            frame.load()
                        continue
                    elif method_name == 'unloadFrame':
                        frame_name = args[0]
                        frame = self.frame_registry.get_frame(frame_name)
                        if frame:
                            frame.unload()
                        continue
                    elif method_name == 'addComponentToFrame':
                        frame_name = args[0]
                        component_id = args[1]
                        component = args[2]
                        frame = self.frame_registry.get_frame(frame_name)
                        if frame and isinstance(component, FrameComponentInstance):
                            component.frame = frame
                            frame.add_component(component_id, component)
                        continue
                
                # Call the method
                if hasattr(obj, method_name):
                    method = getattr(obj, method_name)
                    result = method(*args)
            
            # Print statement
            print_match = re.match(r'print\s+(.+?);?$', line)
            if print_match:
                expr = print_match.group(1)
                value = self.evaluate_expression(expr, local_vars, instance)
                print(value)
            
            # Sleep statement
            sleep_match = re.match(r'sleep\s*\((.+?)\);?$', line)
            if sleep_match:
                expr = sleep_match.group(1)
                seconds = self.evaluate_expression(expr, local_vars, instance)
                time.sleep(seconds)
            
            # Return statement
            return_match = re.match(r'return\s+(.+?);?$', line)
            if return_match:
                expr = return_match.group(1)
                result = self.evaluate_expression(expr, local_vars, instance)
                return result
        
        return result
    
    def evaluate_expression(self, expr, local_vars, instance):
        """Evaluate an expression in the context of local variables and instance."""
        expr = expr.strip()
        
        # String literal
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        elif expr.startswith("'") and expr.endswith("'"):
            return expr[1:-1]
        
        # Boolean literal
        if expr == 'true':
            return True
        elif expr == 'false':
            return False
        
        # Numeric literal
        if expr.isdigit():
            return int(expr)
        elif '.' in expr and expr.replace('.', '', 1).isdigit():
            return float(expr)
        
        # Date.now()
        if expr == 'Date.now()':
            return int(time.time() * 1000)
        
        # Property access
        if '.' in expr:
            parts = expr.split('.')
            if parts[0] == 'this' and parts[1] == 'state':
                if instance and hasattr(instance, 'state'):
                    return instance.state.get(parts[2])
            elif parts[0] in local_vars:
                obj = local_vars[parts[0]]
                if hasattr(obj, 'state') and parts[1] == 'state':
                    return obj.state.get(parts[2])
        
        # Method call
        method_call = re.match(r'(\w+)\.(\w+)\((.*?)\)', expr)
        if method_call:
            obj_name = method_call.group(1)
            method_name = method_call.group(2)
            args_str = method_call.group(3)
            
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
                    if arg.startswith('"') and arg.endswith('"'):
                        args.append(arg[1:-1])
                    elif arg.startswith("'") and arg.endswith("'"):
                        args.append(arg[1:-1])
                    elif arg == 'true':
                        args.append(True)
                    elif arg == 'false':
                        args.append(False)
                    elif arg.isdigit():
                        args.append(int(arg))
                    elif '.' in arg and arg.replace('.', '', 1).isdigit():
                        args.append(float(arg))
                    else:
                        args.append(self.evaluate_expression(arg, local_vars, instance))
            
            # Call the method
            if hasattr(obj, method_name):
                method = getattr(obj, method_name)
                return method(*args)
        
        # String concatenation
        if '+' in expr:
            # Handle multi-line string concatenation
            if '\n' in expr:
                # Join all lines and then split by +
                expr = ' '.join([line.strip() for line in expr.split('\n')])
            
            parts = expr.split('+')
            result = ''
            for part in parts:
                part = part.strip()
                # Handle string literals
                if part.startswith('"') and part.endswith('"'):
                    result += part[1:-1]
                elif part.startswith("'") and part.endswith("'"):
                    result += part[1:-1]
                # Handle property access
                elif '.' in part and part.startswith('this.state.'):
                    prop_name = part.split('.')[-1]
                    if instance and hasattr(instance, 'state'):
                        result += str(instance.state.get(prop_name, ''))
                # Handle conditional expressions
                elif '?' in part and ':' in part:
                    # Simple ternary operator
                    cond_parts = part.split('?')
                    condition = cond_parts[0].strip()
                    true_false = cond_parts[1].split(':')
                    true_expr = true_false[0].strip()
                    false_expr = true_false[1].strip()
                    
                    # Evaluate the condition
                    if self.evaluate_expression(condition, local_vars, instance):
                        result += str(self.evaluate_expression(true_expr, local_vars, instance))
                    else:
                        result += str(self.evaluate_expression(false_expr, local_vars, instance))
                else:
                    # Regular expression
                    part_value = self.evaluate_expression(part, local_vars, instance)
                    result += str(part_value)
            return result
        
        # Variable reference
        if expr in local_vars:
            return local_vars[expr]
        
        # If all else fails, return the expression itself
        return expr

def run_mono_file(file_path: str) -> bool:
    """
    Run a Mono script file with frame support and display the results.
    """
    try:
        interpreter = FrameInterpreter()
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
