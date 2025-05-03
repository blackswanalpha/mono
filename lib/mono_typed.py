"""
Mono Typed - Mono language interpreter with static typing and type inference
"""

import re
import sys
from typing import Dict, List, Set, Optional, Any, Union, Tuple, Callable

from lib.mono_types import (
    MonoType, TypeKind, PrimitiveType, ComponentType, FunctionType, GenericType,
    GenericInstanceType, ArrayType, UnionType, VoidType, AnyType, UnknownType,
    INT_TYPE, FLOAT_TYPE, STRING_TYPE, BOOL_TYPE, VOID_TYPE, ANY_TYPE, UNKNOWN_TYPE,
    TypeRegistry, TypeInferer, TypeChecker
)

class TypedComponent:
    """
    Represents a component in the Typed Mono language.
    """
    def __init__(self, name: str, type_params: List[GenericType] = None):
        self.name = name
        self.type_params = type_params or []
        self.state: Dict[str, Tuple[MonoType, Any]] = {}  # name -> (type, default value)
        self.methods: Dict[str, Tuple[List[Tuple[str, MonoType]], MonoType, str]] = {}  # name -> (params, return_type, body)
        self.component_type: Optional[ComponentType] = None

    def add_state(self, name: str, type_obj: MonoType, default_value: Any = None) -> None:
        """Add a state property to the component."""
        self.state[name] = (type_obj, default_value)

    def add_method(self, name: str, params: List[Tuple[str, MonoType]], return_type: MonoType, body: str) -> None:
        """Add a method to the component."""
        self.methods[name] = (params, return_type, body)

    def build_component_type(self, registry: TypeRegistry) -> ComponentType:
        """Build a ComponentType for this component."""
        # Create properties dictionary
        properties = {name: type_obj for name, (type_obj, _) in self.state.items()}

        # Create methods dictionary
        methods = {}
        for name, (params, return_type, _) in self.methods.items():
            param_types = [param_type for _, param_type in params]
            methods[name] = FunctionType(param_types, return_type, name)

        # Create the component type
        if self.type_params:
            # This is a generic component
            self.component_type = GenericType(self.name, [])
        else:
            # This is a regular component
            self.component_type = ComponentType(self.name, properties, methods)

        # Register the component type
        registry.register_type(self.component_type)

        return self.component_type

class TypedInstance:
    """
    Represents an instance of a component in the Typed Mono language.
    """
    def __init__(self, component: TypedComponent, interpreter):
        self.component = component
        self.interpreter = interpreter
        self.state = {name: default_value for name, (_, default_value) in component.state.items()}

        # Add methods
        for name, (params, return_type, body) in component.methods.items():
            # Create a closure for each method
            method_body = body  # Create a local copy for the closure
            method_params = params  # Create a local copy for the closure

            def method_factory(body, params):
                def method(*args):
                    return interpreter.execute_method(body, params, self, args)
                return method

            # Bind the method to the instance
            bound_method = method_factory(method_body, method_params)
            setattr(self, name, bound_method)

    def setState(self, new_state: Dict[str, Any]) -> None:
        """
        Update the state of the component instance.
        """
        for key, value in new_state.items():
            if key in self.state:
                self.state[key] = value

class TypedInterpreter:
    """
    Typed Mono language interpreter with static typing and type inference.
    """
    def __init__(self, type_check: bool = False, verbose: bool = False):
        self.components: Dict[str, TypedComponent] = {}
        self.variables: Dict[str, Any] = {}
        self.type_registry = TypeRegistry()
        self.type_inferer = TypeInferer(self.type_registry)
        self.type_checker = TypeChecker(self.type_registry, self.type_inferer)
        self.type_check = type_check
        self.verbose = verbose

    def parse_file(self, filename: str) -> None:
        """
        Parse a Typed Mono script file.
        """
        with open(filename, 'r') as f:
            content = f.read()

        # Remove comments
        content = re.sub(r'//.*', '', content)

        # Find components - use a more robust approach
        component_pattern = r'component\s+(\w+)(?:<([^>]*)>)?\s*{'
        component_starts = [(m.group(1), m.group(2), m.start()) for m in re.finditer(component_pattern, content)]

        for name, type_params_str, start_pos in component_starts:
            # Parse type parameters if any
            type_params = []
            if type_params_str:
                type_param_names = [tp.strip() for tp in type_params_str.split(',')]
                for tp_name in type_param_names:
                    type_param = GenericType(tp_name)
                    type_params.append(type_param)
                    self.type_registry.register_type(type_param)

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

            # Create the component
            component = TypedComponent(name, type_params)
            self.components[name] = component

            # Parse state
            state_match = re.search(r'state\s*{(.*?)}', body, re.DOTALL)
            if state_match:
                state_body = state_match.group(1)
                state_entries = re.finditer(r'(\w+)(?:\s*:\s*(\w+))?\s*(?:=\s*(.*?))?(?:,|\s*$)', state_body, re.DOTALL)

                for entry in state_entries:
                    key = entry.group(1)
                    type_name = entry.group(2)
                    value_str = entry.group(3)

                    # Determine the type
                    if type_name:
                        # Explicit type annotation
                        type_obj = self.type_registry.get_type(type_name) or UNKNOWN_TYPE
                    else:
                        # Type inference based on the value
                        type_obj = UNKNOWN_TYPE

                    # Parse value
                    default_value = None
                    if value_str:
                        value_str = value_str.strip()
                        if value_str.isdigit():
                            default_value = int(value_str)
                            if not type_name:  # Infer type if not explicitly specified
                                type_obj = INT_TYPE
                        elif value_str == 'true':
                            default_value = True
                            if not type_name:
                                type_obj = BOOL_TYPE
                        elif value_str == 'false':
                            default_value = False
                            if not type_name:
                                type_obj = BOOL_TYPE
                        elif value_str.startswith('"') and value_str.endswith('"'):
                            default_value = value_str[1:-1]
                            if not type_name:
                                type_obj = STRING_TYPE
                        else:
                            default_value = value_str

                    # Add the state property
                    component.add_state(key, type_obj, default_value)

            # Parse methods
            method_pattern = r'function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*(\w+))?\s*{'
            method_starts = [(m.group(1), m.group(2), m.group(3), m.start()) for m in re.finditer(method_pattern, body)]

            for method_name, params_str, return_type_name, method_start_pos in method_starts:
                # Parse parameters
                params = []
                if params_str:
                    param_entries = [p.strip() for p in params_str.split(',')]
                    for param_entry in param_entries:
                        param_parts = param_entry.split(':')
                        param_name = param_parts[0].strip()
                        param_type_name = param_parts[1].strip() if len(param_parts) > 1 else None

                        # Determine parameter type
                        if param_type_name:
                            param_type = self.type_registry.get_type(param_type_name) or UNKNOWN_TYPE
                        else:
                            param_type = ANY_TYPE

                        params.append((param_name, param_type))

                # Determine return type
                if return_type_name:
                    return_type = self.type_registry.get_type(return_type_name) or UNKNOWN_TYPE
                else:
                    return_type = VOID_TYPE

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

                # Add the method
                component.add_method(method_name, params, return_type, method_body)

            # Build the component type
            component.build_component_type(self.type_registry)

    def run(self) -> None:
        """
        Run the parsed Typed Mono script.
        """
        if 'Main' not in self.components:
            print("Error: Main component not found")
            return

        # Create Main instance
        main = TypedInstance(self.components['Main'], self)

        # Call start method
        if hasattr(main, 'start'):
            main.start()
        else:
            print("Error: start method not found")

    def execute_method(self, body: str, params: List[Tuple[str, MonoType]], instance: TypedInstance, args: List[Any]) -> Any:
        """
        Execute a method on a component instance.
        """
        # Local variables for this method execution
        local_vars: Dict[str, Any] = {}
        local_types: Dict[str, MonoType] = {}
        return_value = None

        # Add arguments to local variables
        for i, (param_name, param_type) in enumerate(params):
            if i < len(args):
                local_vars[param_name] = args[i]
                local_types[param_name] = param_type

                # Type check if enabled
                if self.type_check and self.verbose:
                    print(f"Type checking argument {param_name}: {param_type}")

        # Split into lines
        lines = body.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Return statement
            return_match = re.match(r'return\s+(.*?);?$', line)
            if return_match:
                expr = return_match.group(1).strip()

                # Evaluate the return expression
                if expr in local_vars:
                    return_value = local_vars[expr]
                elif expr.isdigit():
                    return_value = int(expr)
                elif expr.startswith('"') and expr.endswith('"'):
                    return_value = expr[1:-1]
                elif expr == 'true':
                    return_value = True
                elif expr == 'false':
                    return_value = False
                elif expr.startswith('this.state.'):
                    prop = expr[11:]
                    return_value = instance.state.get(prop)
                else:
                    return_value = expr

                # Type check if enabled
                if self.type_check and self.verbose:
                    print(f"Returning value: {return_value}")

                return return_value

            # Variable declaration
            var_match = re.match(r'var\s+(\w+)(?:\s*:\s*(\w+))?\s*=\s*(.*?);?$', line)
            if var_match:
                var_name = var_match.group(1)
                type_name = var_match.group(2)
                var_expr = var_match.group(3)

                # Determine the variable type
                if type_name:
                    var_type = self.type_registry.get_type(type_name) or UNKNOWN_TYPE
                else:
                    var_type = UNKNOWN_TYPE

                # Component instantiation
                new_match = re.match(r'new\s+(\w+)(?:<([^>]*)>)?\(\)', var_expr)
                if new_match:
                    comp_name = new_match.group(1)
                    type_args_str = new_match.group(2)

                    if comp_name in self.components:
                        comp_instance = TypedInstance(self.components[comp_name], self)
                        local_vars[var_name] = comp_instance

                        # Set the variable type
                        if not type_name:
                            var_type = self.type_registry.get_component_type(comp_name) or UNKNOWN_TYPE

                        local_types[var_name] = var_type
                    else:
                        print(f"Error: Component {comp_name} not found")
                else:
                    # Simple value
                    local_vars[var_name] = var_expr

                    # Infer type if not explicitly specified
                    if not type_name:
                        if var_expr.isdigit():
                            var_type = INT_TYPE
                        elif var_expr == 'true' or var_expr == 'false':
                            var_type = BOOL_TYPE
                        elif var_expr.startswith('"') and var_expr.endswith('"'):
                            var_type = STRING_TYPE

                    local_types[var_name] = var_type

                # Type check if enabled
                if self.type_check and self.verbose:
                    print(f"Variable {var_name} has type {var_type}")

            # Method call - with or without assignment
            method_call_assign = re.match(r'(?:var\s+(\w+)(?:\s*:\s*(\w+))?\s*=\s*)?(\w+)\.(\w+)\(([^)]*)\);?$', line)
            if method_call_assign:
                var_name = method_call_assign.group(1)
                var_type_name = method_call_assign.group(2)
                obj_name = method_call_assign.group(3)
                method_name = method_call_assign.group(4)
                args_str = method_call_assign.group(5)

                if obj_name == 'this':
                    obj = instance
                elif obj_name in local_vars:
                    obj = local_vars[obj_name]
                else:
                    print(f"Error: Object {obj_name} not found")
                    continue

                # Parse arguments
                call_args = []
                if args_str:
                    for arg in args_str.split(','):
                        arg = arg.strip()
                        if arg in local_vars:
                            call_args.append(local_vars[arg])
                        elif arg.isdigit():
                            call_args.append(int(arg))
                        elif arg.startswith('"') and arg.endswith('"'):
                            call_args.append(arg[1:-1])
                        elif '.' in arg:
                            # Handle property access (e.g., counter.state.count)
                            parts = arg.split('.')
                            if parts[0] in local_vars:
                                obj_arg = local_vars[parts[0]]
                                for part in parts[1:]:
                                    if hasattr(obj_arg, part):
                                        obj_arg = getattr(obj_arg, part)
                                    elif isinstance(obj_arg, dict) and part in obj_arg:
                                        obj_arg = obj_arg[part]
                                call_args.append(obj_arg)

                # Type check if enabled
                if self.type_check and self.verbose:
                    print(f"Calling {obj_name}.{method_name} with {len(call_args)} arguments")

                # Call the method
                if hasattr(obj, method_name):
                    method = getattr(obj, method_name)
                    result = method(*call_args)

                    # If this is an assignment, store the result
                    if var_name:
                        local_vars[var_name] = result

                        # Determine the variable type
                        if var_type_name:
                            var_type = self.type_registry.get_type(var_type_name) or UNKNOWN_TYPE
                        else:
                            # Infer type from the result
                            if isinstance(result, int):
                                var_type = INT_TYPE
                            elif isinstance(result, float):
                                var_type = FLOAT_TYPE
                            elif isinstance(result, str):
                                var_type = STRING_TYPE
                            elif isinstance(result, bool):
                                var_type = BOOL_TYPE
                            else:
                                var_type = UNKNOWN_TYPE

                        local_types[var_name] = var_type

                        # Type check if enabled
                        if self.type_check and self.verbose:
                            print(f"Variable {var_name} has type {var_type}")
                else:
                    print(f"Error: Method {method_name} not found on {obj_name}")

            # State update
            state_update = re.match(r'this\.state\.(\w+)\s*=\s*(.*?);?$', line)
            if state_update:
                prop_name = state_update.group(1)
                value_expr = state_update.group(2)

                # Evaluate expression
                if '+' in value_expr:
                    parts = value_expr.split('+')
                    left = parts[0].strip()
                    right = parts[1].strip()

                    left_val = None
                    if left == 'this.state.count':
                        left_val = instance.state.get('count', 0)
                    elif left.isdigit():
                        left_val = int(left)

                    right_val = None
                    if right == 'this.state.count':
                        right_val = instance.state.get('count', 0)
                    elif right.isdigit():
                        right_val = int(right)

                    if left_val is not None and right_val is not None:
                        instance.state[prop_name] = left_val + right_val
                elif '-' in value_expr:
                    parts = value_expr.split('-')
                    left = parts[0].strip()
                    right = parts[1].strip()

                    left_val = None
                    if left == 'this.state.count':
                        left_val = instance.state.get('count', 0)
                    elif left.isdigit():
                        left_val = int(left)

                    right_val = None
                    if right == 'this.state.count':
                        right_val = instance.state.get('count', 0)
                    elif right.isdigit():
                        right_val = int(right)

                    if left_val is not None and right_val is not None:
                        instance.state[prop_name] = left_val - right_val
                else:
                    # Simple value
                    if value_expr.isdigit():
                        instance.state[prop_name] = int(value_expr)
                    elif value_expr in local_vars:
                        instance.state[prop_name] = local_vars[value_expr]
                    else:
                        instance.state[prop_name] = value_expr

                # Type check if enabled
                if self.type_check and self.verbose:
                    print(f"Updated state property {prop_name}")

            # Print statement
            print_match = re.match(r'print\s+(.*?);?$', line)
            if print_match:
                expr = print_match.group(1).strip()

                # String literal
                if expr.startswith('"') and expr.endswith('"'):
                    print(expr[1:-1])
                    continue

                # String concatenation
                if '+' in expr:
                    parts = expr.split('+')
                    result = ''

                    for part in parts:
                        part = part.strip()

                        if part.startswith('"') and part.endswith('"'):
                            result += part[1:-1]
                        elif part == 'this.state.count':
                            result += str(instance.state.get('count', 0))
                        elif part.startswith('this.state.'):
                            prop = part[11:]
                            result += str(instance.state.get(prop, ''))
                        elif '.' in part and not part.startswith('"'):
                            # Handle references to other objects (e.g., counter.state.count)
                            obj_parts = part.split('.')
                            if len(obj_parts) >= 3 and obj_parts[0] in local_vars:
                                obj = local_vars[obj_parts[0]]
                                if obj_parts[1] == 'state' and hasattr(obj, 'state'):
                                    prop = obj_parts[2]
                                    if prop in obj.state:
                                        result += str(obj.state[prop])
                        elif part in local_vars:
                            result += str(local_vars[part])

                    print(result)
                else:
                    # Simple expression
                    if expr == 'this.state.count':
                        print(instance.state.get('count', 0))
                    elif expr.startswith('this.state.'):
                        prop = expr[11:]
                        print(instance.state.get(prop, ''))
                    elif expr in local_vars:
                        print(local_vars[expr])
                    else:
                        print(expr)

        return return_value

def run_mono_file(file_path: str, type_check: bool = False, verbose: bool = False) -> bool:
    """
    Run a Typed Mono script file and display the results.
    """
    try:
        interpreter = TypedInterpreter(type_check, verbose)
        interpreter.parse_file(file_path)

        # Check for type errors if type checking is enabled
        if type_check and interpreter.type_checker.has_errors():
            print("Type errors found:")
            for error in interpreter.type_checker.get_errors():
                print(f"  {error}")
            return False

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
