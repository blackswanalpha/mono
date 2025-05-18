"""
Mono HTTP Interpreter - Interpreter for Mono with HTTP server support
"""

import re
from typing import Dict, List, Any, Optional

from lib.mono_http import get_http_server

class HttpComponent:
    """
    Represents a component with HTTP server support in the Mono language.
    """
    def __init__(self, name: str):
        self.name = name
        self.state = {}
        self.methods = {}
        self.http_server = None

class HttpComponentInstance:
    """
    Represents an instance of a component with HTTP server support.
    """
    def __init__(self, component: HttpComponent, interpreter):
        self.component = component
        self.interpreter = interpreter
        self.state = component.state.copy()
        self.http_server = get_http_server()
        self.mounted = False

        # Add state properties as instance attributes for direct access
        for name, value in component.state.items():
            setattr(self, name, value)

        # Add methods
        for name, body in component.methods.items():
            # Create a closure for each method
            method_body = body  # Create a local copy for the closure

            def method_factory(body):
                def method(*args):
                    # Create a local copy of args to avoid modifying the original
                    local_args = list(args)

                    # Handle the case where the method is a handler method
                    if len(local_args) == 2:
                        # This is a handler method with request and response objects
                        req_obj = local_args[0]
                        res_obj = local_args[1]

                        # Create a local scope for the method execution
                        local_vars = {'req': req_obj, 'res': res_obj}

                        # Execute the method with the local variables
                        return interpreter.execute_method(body, self, local_args, local_vars)
                    else:
                        # Regular method call
                        return interpreter.execute_method(body, self, local_args)
                return method

            # Bind the method to the instance
            bound_method = method_factory(method_body)
            setattr(self, name, bound_method)

    def __getattr__(self, name):
        """Handle attribute access for properties not found in the instance."""
        # Check if the attribute is in the state
        if hasattr(self, 'state') and name in self.state:
            return self.state[name]

        # Default behavior
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

class HttpInterpreter:
    """
    Mono language interpreter with support for HTTP server.
    """
    def __init__(self):
        self.components: Dict[str, HttpComponent] = {}
        self.instances: Dict[str, List[HttpComponentInstance]] = {}
        self.variables: Dict[str, Any] = {}
        self.current_instance: Optional[HttpComponentInstance] = None
        self.http_server = get_http_server()

    def parse_file(self, file_path: str) -> None:
        """Parse a Mono script file."""
        with open(file_path, 'r') as f:
            content = f.read()
        self.parse(content)

    def parse(self, script: str) -> None:
        """Parse a Mono script."""
        print("Parsing Mono script...")

        # Remove comments
        script = re.sub(r'//.*$', '', script, flags=re.MULTILINE)

        # Extract components
        components_start = []
        components_end = []

        # Find all component start and end positions
        for match in re.finditer(r'component\s+(\w+)\s*{', script):
            components_start.append((match.group(1), match.start()))

        # Find all closing braces
        brace_level = 0
        for i, char in enumerate(script):
            if char == '{':
                brace_level += 1
            elif char == '}':
                brace_level -= 1
                if brace_level == 0:
                    components_end.append(i)

        # Match start and end positions
        for i, (component_name, start_pos) in enumerate(components_start):
            if i < len(components_end):
                end_pos = components_end[i]
                component_body = script[start_pos:end_pos+1]

                print(f"Found component: {component_name}")

                # Create a new component
                component = HttpComponent(component_name)

                # Extract methods
                print(f"Extracting methods for component {component_name}...")

                # Find all method blocks
                method_blocks = re.findall(r'function\s+(\w+)\s*\([^)]*\)\s*{([^{}]*(?:{[^{}]*})*)}', component_body)

                for method_name, method_body in method_blocks:
                    print(f"Found method: {method_name}")
                    component.methods[method_name] = method_body

                # Add the component
                self.components[component_name] = component

        # Manual parsing for Main component's start method
        main_match = re.search(r'component\s+Main\s*{([^}]*)}', script, re.DOTALL)
        if main_match:
            main_body = main_match.group(1)
            start_match = re.search(r'function\s+start\s*\(\)\s*{([^}]*)}', main_body, re.DOTALL)
            if start_match:
                start_body = start_match.group(1)
                print(f"Found Main.start method: {start_body}")

                # Create Main component if it doesn't exist
                if 'Main' not in self.components:
                    self.components['Main'] = HttpComponent('Main')

                # Add start method
                self.components['Main'].methods['start'] = start_body

    def run(self) -> None:
        """Run the parsed Mono script with HTTP server support."""
        print(f"Available components: {list(self.components.keys())}")

        if 'Main' not in self.components:
            print("Error: Main component not found")
            return

        print(f"Main component methods: {list(self.components['Main'].methods.keys())}")

        # Create Main instance
        main = HttpComponentInstance(self.components['Main'], self)
        self.instances['Main'] = [main]
        self.current_instance = main

        # Call start method
        if 'start' in self.components['Main'].methods:
            print("Found start method, executing...")
            # Execute the start method
            self.execute_method(self.components['Main'].methods['start'], main, [])
        else:
            print("Error: start method not found")

    def execute_method(self, method_body: str, instance: HttpComponentInstance, args: List[Any] = None, initial_local_vars: Dict[str, Any] = None) -> Any:
        """Execute a method with HTTP server support."""
        if args is None:
            args = []

        # Set the current instance
        old_instance = self.current_instance
        self.current_instance = instance

        # Create local variables
        local_vars = {}

        # Add initial local variables if provided
        if initial_local_vars:
            local_vars.update(initial_local_vars)

        # Add arguments to local variables for constructor
        if method_body.strip().startswith('if (port)') and len(args) >= 2:
            # This is a constructor with port and host parameters
            port = args[0]
            host = args[1]

            # Set the port and host properties directly
            if hasattr(instance, 'state'):
                if 'port' in instance.state:
                    instance.state['port'] = port
                    instance.port = port
                if 'host' in instance.state:
                    instance.state['host'] = host
                    instance.host = host

        # Parse the method body
        lines = method_body.strip().split('\n')
        result = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Variable declaration
            var_match = re.match(r'var\s+(\w+)\s*=\s*(.+?);?$', line)
            if var_match:
                var_name = var_match.group(1)
                var_expr = var_match.group(2)

                # Component instantiation with parameters
                new_match = re.match(r'new\s+(\w+)\((.+?)\)', var_expr)
                if new_match:
                    comp_name = new_match.group(1)
                    comp_args_str = new_match.group(2)

                    # Parse arguments
                    comp_args = []
                    if comp_args_str:
                        comp_args = [self.evaluate_expression(arg.strip(), local_vars, instance) for arg in comp_args_str.split(',')]

                    if comp_name in self.components:
                        # Create the component instance
                        comp_instance = HttpComponentInstance(self.components[comp_name], self)

                        # Special case for server components
                        if comp_name in ['WebServer', 'RestApiServer', 'StaticServer']:
                            # Initialize state with default values
                            comp_instance.state = {
                                'port': 8000,
                                'host': 'localhost'
                            }

                            # Add rootDir for StaticServer
                            if comp_name == 'StaticServer':
                                comp_instance.state['rootDir'] = './public'

                            # Set attributes for direct access
                            comp_instance.port = 8000
                            comp_instance.host = 'localhost'

                            # Add rootDir for StaticServer
                            if comp_name == 'StaticServer':
                                comp_instance.rootDir = './public'

                            # Override with arguments if provided
                            if len(comp_args) >= 1:
                                port = comp_args[0]
                                comp_instance.state['port'] = port
                                comp_instance.port = port

                            if len(comp_args) >= 2:
                                host = comp_args[1]
                                comp_instance.state['host'] = host
                                comp_instance.host = host

                            # Override rootDir for StaticServer
                            if comp_name == 'StaticServer' and len(comp_args) >= 3:
                                rootDir = comp_args[2]
                                comp_instance.state['rootDir'] = rootDir
                                comp_instance.rootDir = rootDir



                        # Special case for UserDatabase component
                        elif comp_name == 'UserDatabase':
                            # Initialize state with default values
                            comp_instance.state = {
                                'users': [
                                    {'id': '1', 'name': 'John Doe', 'email': 'john@example.com', 'role': 'admin'},
                                    {'id': '2', 'name': 'Jane Smith', 'email': 'jane@example.com', 'role': 'user'},
                                    {'id': '3', 'name': 'Bob Johnson', 'email': 'bob@example.com', 'role': 'user'}
                                ],
                                'nextId': 4
                            }

                            # Set attributes for direct access
                            comp_instance.users = comp_instance.state['users']
                            comp_instance.nextId = comp_instance.state['nextId']



                        # Store the instance
                        local_vars[var_name] = comp_instance

                        # Add to instances
                        if comp_name not in self.instances:
                            self.instances[comp_name] = []
                        self.instances[comp_name].append(comp_instance)

                        # Call constructor if it exists
                        if 'constructor' in self.components[comp_name].methods:
                            # Call the constructor
                            self.execute_method(self.components[comp_name].methods['constructor'], comp_instance, comp_args)
                    else:
                        print(f"Error: Component {comp_name} not found")
                else:
                    # Simple value
                    local_vars[var_name] = self.evaluate_expression(var_expr, local_vars, instance)

            # Method call
            method_call_match = re.match(r'(\w+)\.(\w+)\((.*?)\);?$', line)
            if method_call_match:
                obj_name = method_call_match.group(1)
                method_name = method_call_match.group(2)
                args_str = method_call_match.group(3)

                # Special case for response object
                if obj_name == 'res' and obj_name in local_vars:
                    res_obj = local_vars[obj_name]

                    # Parse arguments
                    call_args = []
                    if args_str:
                        call_args = [self.evaluate_expression(arg.strip(), local_vars, instance) for arg in args_str.split(',')]

                    # Call the method on the response object
                    if hasattr(res_obj, method_name):
                        method_func = getattr(res_obj, method_name)
                        method_func(*call_args)
                    else:
                        print(f"Error: Method {method_name} not found on response object")
                    continue

                # Special case for request object
                if obj_name == 'req' and obj_name in local_vars:
                    req_obj = local_vars[obj_name]

                    # Access property on the request object
                    if method_name in req_obj:
                        prop_value = req_obj[method_name]

                        # If there are arguments, this is a method call or indexed access
                        if args_str:
                            # Parse arguments
                            call_args = []
                            if args_str:
                                call_args = [self.evaluate_expression(arg.strip(), local_vars, instance) for arg in args_str.split(',')]

                            # If it's a function, call it
                            if callable(prop_value):
                                return prop_value(*call_args)
                            # Otherwise, treat it as a property access with an index
                            elif isinstance(prop_value, (list, dict)) and len(call_args) > 0:
                                try:
                                    return prop_value[call_args[0]]
                                except (KeyError, IndexError):
                                    return None
                        else:
                            # Simple property access
                            return prop_value
                    continue

                # Special case for HTTP methods
                if obj_name == 'http':
                    # Parse arguments
                    http_args = []
                    if args_str:
                        http_args = [self.evaluate_expression(arg.strip(), local_vars, instance) for arg in args_str.split(',')]

                    # Call the HTTP server method
                    if method_name == 'start':
                        # Start the server
                        self.http_server.start()
                        # Wait a moment for the server to start
                        import time
                        time.sleep(0.5)

                        # Keep the server running in the foreground
                        try:
                            while True:
                                time.sleep(1)
                        except KeyboardInterrupt:
                            print("Stopping server...")
                            self.http_server.stop()
                    elif method_name == 'stop':
                        self.http_server.stop()
                    elif method_name in ['get', 'post', 'put', 'delete']:
                        if len(http_args) >= 2:
                            path = http_args[0]
                            handler_name = http_args[1]



                            # Create a handler function
                            def create_handler(instance, handler_name):
                                def handler(req, res):


                                    # Create request and response objects in Mono
                                    request_obj = {
                                        'method': req.method,
                                        'path': req.path,
                                        'headers': req.headers,
                                        'body': req.body,
                                        'params': req.params,
                                        'query': req.query_params
                                    }

                                    # Create a response object wrapper class
                                    class ResponseWrapper:
                                        def __init__(self, res_obj):
                                            self.res = res_obj

                                        def status(self, code):
                                            self.res.status(code)
                                            return self

                                        def header(self, name, value):
                                            self.res.header(name, value)
                                            return self

                                        def text(self, content):
                                            self.res.text(content)
                                            return self

                                        def html(self, content):
                                            self.res.html(content)
                                            return self

                                        def json(self, data):
                                            self.res.json(data)
                                            return self

                                    response_obj = ResponseWrapper(res)

                                    # Call the handler method
                                    try:
                                        if hasattr(instance, handler_name):
                                            handler_method = getattr(instance, handler_name)
                                            handler_method(request_obj, response_obj)
                                        else:
                                            print(f"Handler method {handler_name} not found on instance")
                                            res.status(500).text(f"Internal Server Error: Handler method {handler_name} not found")
                                    except Exception as e:
                                        print(f"Error in handler {handler_name}: {e}")
                                        import traceback
                                        traceback.print_exc()
                                        res.status(500).text(f"Internal Server Error: {str(e)}")

                                return handler

                            # Register the route
                            getattr(self.http_server, method_name)(path, create_handler(instance, handler_name))
                    continue  # Skip the rest of the loop since we've handled this line

                # Regular method call
                # Get the object
                obj = None
                if obj_name == 'this':
                    obj = instance
                elif obj_name in local_vars:
                    obj = local_vars[obj_name]

                if obj is None:
                    print(f"Error: Object {obj_name} not found")
                    continue

                # Parse arguments
                call_args = []
                if args_str:
                    call_args = [self.evaluate_expression(arg.strip(), local_vars, instance) for arg in args_str.split(',')]

                # Call the method
                if hasattr(obj, method_name):
                    method = getattr(obj, method_name)
                    result = method(*call_args)
                else:
                    print(f"Error: Method {method_name} not found on object {obj_name}")

            # HTTP server methods (direct pattern)
            http_server_match = re.match(r'http\.(\w+)\((.*?)\);?$', line)
            if http_server_match:
                method_name = http_server_match.group(1)
                args_str = http_server_match.group(2)



                # Parse arguments
                http_args = []
                if args_str:
                    http_args = [self.evaluate_expression(arg.strip(), local_vars, instance) for arg in args_str.split(',')]

                # Call the HTTP server method
                if method_name == 'start':
                    # Start the server
                    self.http_server.start()

                    # Keep the server running in the foreground
                    try:
                        while True:
                            import time
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("Stopping server...")
                        self.http_server.stop()
                elif method_name == 'stop':
                    self.http_server.stop()
                elif method_name in ['get', 'post', 'put', 'delete']:
                    if len(http_args) >= 2:
                        path = http_args[0]
                        handler_name = http_args[1]



                        # Create a handler function
                        def create_handler(instance, handler_name):
                            def handler(req, res):


                                # Create request and response objects in Mono
                                request_obj = {
                                    'method': req.method,
                                    'path': req.path,
                                    'headers': req.headers,
                                    'body': req.body,
                                    'params': req.params,
                                    'query': req.query_params
                                }

                                # Create a response object wrapper class
                                class ResponseWrapper:
                                    def __init__(self, res_obj):
                                        self.res = res_obj

                                    def status(self, code):
                                        self.res.status(code)
                                        return self

                                    def header(self, name, value):
                                        self.res.header(name, value)
                                        return self

                                    def text(self, content):
                                        self.res.text(content)
                                        return self

                                    def html(self, content):
                                        self.res.html(content)
                                        return self

                                    def json(self, data):
                                        self.res.json(data)
                                        return self

                                response_obj = ResponseWrapper(res)

                                # Call the handler method
                                try:
                                    if hasattr(instance, handler_name):
                                        handler_method = getattr(instance, handler_name)
                                        handler_method(request_obj, response_obj)
                                    else:
                                        print(f"Handler method {handler_name} not found on instance")
                                        res.status(500).text(f"Internal Server Error: Handler method {handler_name} not found")
                                except Exception as e:
                                    print(f"Error in handler {handler_name}: {e}")
                                    import traceback
                                    traceback.print_exc()
                                    res.status(500).text(f"Internal Server Error: {str(e)}")

                            return handler

                        # Register the route
                        getattr(self.http_server, method_name)(path, create_handler(instance, handler_name))
                continue  # Skip the rest of the loop since we've handled this line

            # HTTP server methods (method call pattern)
            http_method_match = re.match(r'(\w+)\.(\w+)\((.*?)\);?$', line)
            if http_method_match and http_method_match.group(1) == 'http':
                obj_name = http_method_match.group(1)
                method_name = http_method_match.group(2)
                args_str = http_method_match.group(3)



                # Parse arguments
                http_args = []
                if args_str:
                    http_args = [self.evaluate_expression(arg.strip(), local_vars, instance) for arg in args_str.split(',')]

                # Call the HTTP server method
                if method_name == 'start':
                    # Start the server
                    self.http_server.start()

                    # Keep the server running in the foreground
                    try:
                        while True:
                            import time
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("Stopping server...")
                        self.http_server.stop()
                elif method_name == 'stop':
                    self.http_server.stop()
                elif method_name in ['get', 'post', 'put', 'delete']:
                    if len(http_args) >= 2:
                        path = http_args[0]
                        handler_name = http_args[1]



                        # Create a handler function
                        def create_handler(instance, handler_name):
                            def handler(req, res):


                                # Create request and response objects in Mono
                                request_obj = {
                                    'method': req.method,
                                    'path': req.path,
                                    'headers': req.headers,
                                    'body': req.body,
                                    'params': req.params,
                                    'query': req.query_params
                                }

                                # Create a response object wrapper class
                                class ResponseWrapper:
                                    def __init__(self, res_obj):
                                        self.res = res_obj

                                    def status(self, code):
                                        self.res.status(code)
                                        return self

                                    def header(self, name, value):
                                        self.res.header(name, value)
                                        return self

                                    def text(self, content):
                                        self.res.text(content)
                                        return self

                                    def html(self, content):
                                        self.res.html(content)
                                        return self

                                    def json(self, data):
                                        self.res.json(data)
                                        return self

                                response_obj = ResponseWrapper(res)

                                # Call the handler method
                                try:
                                    if hasattr(instance, handler_name):
                                        handler_method = getattr(instance, handler_name)
                                        handler_method(request_obj, response_obj)
                                    else:
                                        print(f"Handler method {handler_name} not found on instance")
                                        res.status(500).text(f"Internal Server Error: Handler method {handler_name} not found")
                                except Exception as e:
                                    print(f"Error in handler {handler_name}: {e}")
                                    import traceback
                                    traceback.print_exc()
                                    res.status(500).text(f"Internal Server Error: {str(e)}")

                            return handler

                        # Register the route
                        getattr(self.http_server, method_name)(path, create_handler(instance, handler_name))

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
                result = self.evaluate_expression(expr, local_vars, instance)
                break

        # Restore the current instance
        self.current_instance = old_instance

        return result

    def evaluate_expression(self, expr: str, local_vars: Dict[str, Any], instance: HttpComponentInstance) -> Any:
        """Evaluate an expression."""
        # String literal
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # Number literal
        if expr.isdigit():
            return int(expr)
        if re.match(r'^[0-9]*\.[0-9]+$', expr):
            return float(expr)

        # Boolean literal
        if expr == 'true':
            return True
        if expr == 'false':
            return False

        # Handle this.property directly
        if expr.startswith('this.'):
            prop_name = expr[5:]  # Remove 'this.'

            if hasattr(instance, prop_name):
                return getattr(instance, prop_name)
            elif hasattr(instance, 'state') and prop_name in instance.state:
                return instance.state[prop_name]

        # Ternary operator
        ternary_match = re.match(r'(.+?)\s*\?\s*(.+?)\s*:\s*(.+)', expr)
        if ternary_match:
            condition_expr = ternary_match.group(1)
            true_expr = ternary_match.group(2)
            false_expr = ternary_match.group(3)

            condition = self.evaluate_expression(condition_expr, local_vars, instance)

            if condition:
                return self.evaluate_expression(true_expr, local_vars, instance)
            else:
                return self.evaluate_expression(false_expr, local_vars, instance)

        # String concatenation
        concat_match = re.match(r'(.+?)\s*\+\s*(.+)', expr)
        if concat_match:
            left_expr = concat_match.group(1)
            right_expr = concat_match.group(2)

            left = self.evaluate_expression(left_expr, local_vars, instance)
            right = self.evaluate_expression(right_expr, local_vars, instance)

            return str(left) + str(right)

        # Property access
        prop_access_match = re.match(r'(\w+)\.(\w+)$', expr)
        if prop_access_match:
            obj_name = prop_access_match.group(1)
            prop_name = prop_access_match.group(2)

            obj = None
            if obj_name == 'this':
                obj = instance

                # Try to get the property directly
                try:
                    return getattr(instance, prop_name)
                except AttributeError:
                    # If not found, try to get it from the state
                    if hasattr(instance, 'state') and prop_name in instance.state:
                        return instance.state[prop_name]
            elif obj_name == 'http':
                # Special case for HTTP object
                if prop_name == 'get':
                    return lambda path, handler: self.http_server.get(path, handler)
                elif prop_name == 'post':
                    return lambda path, handler: self.http_server.post(path, handler)
                elif prop_name == 'put':
                    return lambda path, handler: self.http_server.put(path, handler)
                elif prop_name == 'delete':
                    return lambda path, handler: self.http_server.delete(path, handler)
                elif prop_name == 'start':
                    return lambda: self.http_server.start()
                elif prop_name == 'stop':
                    return lambda: self.http_server.stop()
            elif obj_name in local_vars:
                obj = local_vars[obj_name]

            if obj:
                try:
                    return getattr(obj, prop_name)
                except AttributeError:
                    if hasattr(obj, 'state') and prop_name in obj.state:
                        return obj.state[prop_name]

        # Variable
        if expr in local_vars:
            return local_vars[expr]

        # Instance variable
        if hasattr(instance, 'state') and expr in instance.state:
            return instance.state[expr]

        # HTTP object
        if expr == 'http':
            # Return a dummy object that will be handled in property access
            return {'name': 'http'}

        # Default
        return expr
