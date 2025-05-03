"""
Mono Arithmetic - Enhanced arithmetic operations for the Mono language
"""

import re
import operator
from typing import Dict, List, Any, Optional, Callable, Union, Tuple

# Define arithmetic operators
ARITHMETIC_OPERATORS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '%': operator.mod,
    '**': operator.pow
}

class ArithmeticInterpreter:
    """
    Mono language interpreter with enhanced arithmetic operations.
    """
    def __init__(self):
        self.components = {}
        self.variables = {}
        self.current_component = None

    def parse_file(self, filename: str) -> None:
        """
        Parse a Mono script file.
        """
        with open(filename, 'r') as f:
            content = f.read()

        # Remove comments
        content = re.sub(r'//.*', '', content)

        # Find components
        component_pattern = r'component\s+(\w+)\s*{'
        component_starts = [(m.group(1), m.start()) for m in re.finditer(component_pattern, content)]

        for name, start_pos in component_starts:
            # Find the component body by counting braces
            brace_count = 1
            open_brace_pos = content.find('{', start_pos)
            end_pos = open_brace_pos + 1

            while brace_count > 0 and end_pos < len(content):
                if content[end_pos] == '{':
                    brace_count += 1
                elif content[end_pos] == '}':
                    brace_count -= 1
                end_pos += 1

            # Extract the component body
            body = content[open_brace_pos+1:end_pos-1]

            component = {
                'name': name,
                'state': {},
                'methods': {}
            }
            self.components[name] = component

            # Parse state
            state_match = re.search(r'state\s*{(.*?)}', body, re.DOTALL)
            if state_match:
                state_body = state_match.group(1)
                state_entries = re.finditer(r'(\w+):\s*(.*?)(?:,|\s*$)', state_body, re.DOTALL)

                for entry in state_entries:
                    key = entry.group(1)
                    value = entry.group(2).strip()

                    # Parse value
                    component['state'][key] = self.evaluate_expression(value, {})

            # Parse methods
            method_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*{'
            method_starts = [(m.group(1), m.group(2), m.start()) for m in re.finditer(method_pattern, body)]

            for method_name, params, method_start_pos in method_starts:
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
                param_list = []
                if params:
                    param_list = [p.strip() for p in params.split(',')]

                component['methods'][method_name] = {
                    'params': param_list,
                    'body': method_body
                }

    def run(self) -> None:
        """
        Run the parsed Mono script.
        """
        if 'Main' not in self.components:
            print("Error: Main component not found")
            return

        # Create Main instance
        main_instance = self.create_instance('Main')

        # Call start method
        if 'start' in self.components['Main']['methods']:
            self.execute_method(main_instance, 'start', [])
        else:
            print("Error: start method not found")

    def create_instance(self, component_name: str) -> Dict[str, Any]:
        """
        Create an instance of a component.
        """
        if component_name not in self.components:
            print(f"Error: Component {component_name} not found")
            return {}

        component = self.components[component_name]

        instance = {
            'component': component_name,
            'state': component['state'].copy(),
            'methods': component['methods'],
            'vars': {}
        }

        return instance

    def execute_method(self, instance: Dict[str, Any], method_name: str, args: List[Any]) -> Any:
        """
        Execute a method on a component instance.
        """
        if method_name not in instance['methods']:
            print(f"Error: Method {method_name} not found")
            return None

        method = instance['methods'][method_name]

        # Create local scope for the method
        local_vars = {}

        # Add parameters to local scope
        for i, param_name in enumerate(method['params']):
            if i < len(args):
                local_vars[param_name] = args[i]

        # Execute the method body
        return self.execute_code(method['body'], instance, local_vars)

    def execute_code(self, code: str, instance: Dict[str, Any], local_vars: Dict[str, Any]) -> Any:
        """
        Execute a block of code.
        """
        # Split the code into lines
        lines = code.split('\n')

        # Execute each line
        result = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Variable declaration
            var_match = re.match(r'var\s+(\w+)\s*=\s*(.*?);?$', line)
            if var_match:
                var_name = var_match.group(1)
                var_expr = var_match.group(2)

                # Evaluate the expression
                value = self.evaluate_expression(var_expr, local_vars, instance)
                local_vars[var_name] = value
                continue

            # Assignment
            assign_match = re.match(r'(\w+(?:\.\w+)*)\s*=\s*(.*?);?$', line)
            if assign_match:
                target = assign_match.group(1)
                expr = assign_match.group(2)

                # Evaluate the expression
                value = self.evaluate_expression(expr, local_vars, instance)

                # Assign the value to the target
                if '.' in target:
                    parts = target.split('.')
                    if parts[0] == 'this' and parts[1] == 'state':
                        instance['state'][parts[2]] = value
                    elif parts[0] in local_vars:
                        obj = local_vars[parts[0]]
                        if parts[1] == 'state':
                            obj['state'][parts[2]] = value
                else:
                    local_vars[target] = value
                continue

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
                        args.append(self.evaluate_expression(arg, local_vars, instance))

                # Call the method
                if method_name in obj['methods']:
                    self.execute_method(obj, method_name, args)
                else:
                    print(f"Error: Method {method_name} not found")
                continue

            # Print statement
            print_match = re.match(r'print\s+(.*?);?$', line)
            if print_match:
                expr = print_match.group(1)

                # Handle string concatenation in print statements
                if '+' in expr and (expr.startswith('"') or ' + "' in expr):
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
                    value = self.evaluate_expression(expr, local_vars, instance)
                    print(value)
                continue

            # Return statement
            return_match = re.match(r'return\s+(.*?);?$', line)
            if return_match:
                expr = return_match.group(1)
                result = self.evaluate_expression(expr, local_vars, instance)
                return result

        return result

    def evaluate_expression(self, expr: str, local_vars: Dict[str, Any], instance: Optional[Dict[str, Any]] = None) -> Any:
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

        # Property access
        if '.' in expr:
            parts = expr.split('.')
            if parts[0] == 'this' and parts[1] == 'state':
                if instance and parts[2] in instance['state']:
                    return instance['state'][parts[2]]
            elif parts[0] in local_vars:
                obj = local_vars[parts[0]]
                if parts[1] == 'state':
                    if parts[2] in obj['state']:
                        return obj['state'][parts[2]]

        # Component instantiation
        new_match = re.match(r'new\s+(\w+)\(\)', expr)
        if new_match:
            component_name = new_match.group(1)
            return self.create_instance(component_name)

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
            if method_name in obj['methods']:
                return self.execute_method(obj, method_name, args)
            else:
                print(f"Error: Method {method_name} not found")
                return None

        # Arithmetic expression
        for op in sorted(ARITHMETIC_OPERATORS.keys(), key=len, reverse=True):
            if op in expr:
                parts = expr.split(op, 1)
                left = self.evaluate_expression(parts[0], local_vars, instance)
                right = self.evaluate_expression(parts[1], local_vars, instance)

                # Convert operands to numbers if needed
                if isinstance(left, str):
                    try:
                        left = int(left)
                    except ValueError:
                        try:
                            left = float(left)
                        except ValueError:
                            pass

                if isinstance(right, str):
                    try:
                        right = int(right)
                    except ValueError:
                        try:
                            right = float(right)
                        except ValueError:
                            pass

                # Handle string concatenation for +
                if op == '+' and (isinstance(left, str) or isinstance(right, str)):
                    return str(left) + str(right)

                # Apply the operator with error handling
                try:
                    if op == '/' and right == 0:
                        print("Error: Division by zero")
                        return 0
                    return ARITHMETIC_OPERATORS[op](left, right)
                except Exception as e:
                    print(f"Error in arithmetic operation: {e}")
                    return 0

        # If we can't evaluate the expression, return it as is
        return expr

def run_mono_file(file_path: str) -> bool:
    """
    Run a Mono script file with enhanced arithmetic operations.
    """
    try:
        interpreter = ArithmeticInterpreter()
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
