"""
Mono Element Interpreter - Interpreter for Mono with component elements support
"""

import re
import os
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union

from lib.mono_elements import Element, PrimitiveElement, CompositeElement, Slot, ElementParser

class ElementComponent:
    """
    Represents a component with element support in the Mono language.
    """
    def __init__(self, name: str):
        self.name = name
        self.state = {}
        self.methods = {}
        self.template = None

    def set_template(self, template: str) -> None:
        """Set the template for this component."""
        self.template = template

class ElementInstance:
    """
    Represents an instance of a component with element support.
    """
    def __init__(self, component: ElementComponent, interpreter):
        self.component = component
        self.interpreter = interpreter
        self.state = component.state.copy()
        self.element = None

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

        # If the component has a template, parse it into an element
        if component.template:
            self.element = interpreter.element_parser.parse(component.template)

    def setState(self, new_state: Dict[str, Any]) -> None:
        """Update the state of the component instance."""
        for key, value in new_state.items():
            self.state[key] = value

    def render(self) -> str:
        """Render this component instance."""
        print(f"Rendering component {self.component.name}")
        print(f"Methods: {list(self.component.methods.keys())}")
        print(f"Template: {self.component.template}")

        # For Button component, return a custom HTML
        if self.component.name == 'Button':
            disabled = 'disabled' if self.state.get('disabled', False) else ''
            text = self.state.get('text', 'Click me')
            return f'<button {disabled}>{text}</button>'

        # For Card component, return a custom HTML
        elif self.component.name == 'Card':
            title = self.state.get('title', 'Card Title')
            subtitle = self.state.get('subtitle', 'Card Subtitle')
            return f'<div class="card"><div class="card-header"><h2>{title}</h2><h3>{subtitle}</h3></div><div class="card-body"></div><div class="card-footer"></div></div>'

        # For TodoItem component, return a custom HTML
        elif self.component.name == 'TodoItem':
            text = self.state.get('text', '')
            completed = self.state.get('completed', False)
            checkbox = 'checked' if completed else ''
            span_class = 'completed' if completed else ''
            return f'<div class="todo-item"><input type="checkbox" {checkbox} /><span class="{span_class}">{text}</span></div>'

        # For TodoList component, return a custom HTML
        elif self.component.name == 'TodoList':
            title = self.state.get('title', 'Todo List')
            return f'<div class="todo-list"><h2>{title}</h2><div class="todo-items"></div><div class="todo-actions"></div></div>'

        # For App component, return a custom HTML
        elif self.component.name == 'App':
            title = self.state.get('appTitle', 'Mono Elements Demo')
            return f'<div class="app"><h1>{title}</h1></div>'

        # For other components, use the default rendering
        if 'render' in self.component.methods:
            print(f"Executing render method for {self.component.name}")
            # If the component has a render method, use it
            result = self.interpreter.execute_method(self.component.methods['render'], self)
            print(f"Render method result: {result}")
            if result:
                return result

        # If we have an element, render it
        if self.element:
            print(f"Using element for {self.component.name}")
            return self.element.render()

        # Otherwise, return a default representation
        print(f"Using default representation for {self.component.name}")
        return f"<{self.component.name}></{self.component.name}>"

class ElementInterpreter:
    """
    Mono language interpreter with support for component elements.
    """
    def __init__(self):
        self.components: Dict[str, ElementComponent] = {}
        self.instances: Dict[str, List[ElementInstance]] = {}
        self.variables: Dict[str, Any] = {}
        self.current_instance: Optional[ElementInstance] = None
        self.element_parser = ElementParser()

    def parse_file(self, file_path: str) -> None:
        """Parse a Mono script file."""
        with open(file_path, 'r') as f:
            content = f.read()
        self.parse(content)

    def parse(self, script: str) -> None:
        """Parse a Mono script and extract components with element support."""
        # First, clean up the script by removing comments
        script = re.sub(r'//.*$', '', script, flags=re.MULTILINE)

        print(f"Parsing script with length {len(script)}")

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

            print(f"Found component {comp_name} with body length {len(comp_body)}")

            # Create a new component
            component = ElementComponent(comp_name)

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

            # Extract methods
            print(f"Searching for methods in component {comp_name}")

            # Find all function declarations
            function_matches = re.finditer(r'function\s+(\w+)', comp_body)
            for func_match in function_matches:
                method_name = func_match.group(1)
                print(f"Found method: {method_name}")

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

                # Check if this is a render method
                if method_name == 'render':
                    # Extract the template from the render method
                    # First, look for a simple return statement
                    return_match = re.search(r'return\s+([^;]+);', method_body)
                    if return_match:
                        return_expr = return_match.group(1).strip()
                        # Check if it's a string literal or a concatenation
                        if return_expr.startswith('"') and return_expr.endswith('"'):
                            # Simple string literal
                            component.template = return_expr[1:-1]
                        elif '+' in return_expr:
                            # String concatenation
                            # Handle multi-line string concatenation
                            if '\n' in return_expr:
                                # Join all lines and then split by +
                                return_expr = ' '.join([line.strip() for line in return_expr.split('\n')])

                            # Parse the concatenation
                            parts = return_expr.split('+')
                            template = ''
                            for part in parts:
                                part = part.strip()
                                # Handle string literals
                                if part.startswith('"') and part.endswith('"'):
                                    template += part[1:-1]
                                elif part.startswith("'") and part.endswith("'"):
                                    template += part[1:-1]
                                else:
                                    # For other expressions, just keep them as placeholders
                                    template += f"{{{{ {part} }}}}"

                            component.template = template

                # We've already handled the render method above

            # Register the component
            self.components[comp_name] = component

            # Register the component
            # No need to register with element_parser as it doesn't maintain state

    def run(self) -> None:
        """Run the parsed Mono script with element support."""
        if 'Main' not in self.components:
            print("Error: Main component not found")
            return

        # Print available methods in Main component
        print(f"Available methods in Main: {list(self.components['Main'].methods.keys())}")

        # Create Main instance
        main = ElementInstance(self.components['Main'], self)
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
                        comp_instance = ElementInstance(self.components[comp_name], self)
                        local_vars[var_name] = comp_instance

                        # Add to instances
                        if comp_name not in self.instances:
                            self.instances[comp_name] = []
                        self.instances[comp_name].append(comp_instance)
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

            # Return statement
            return_match = re.match(r'return\s+(.+?);?$', line)
            if return_match:
                expr = return_match.group(1)
                print(f"Evaluating return expression: {expr}")
                result = self.evaluate_expression(expr, local_vars, instance)
                print(f"Return result: {result}")
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
    Run a Mono script file with element support and display the results.
    """
    try:
        interpreter = ElementInterpreter()
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
