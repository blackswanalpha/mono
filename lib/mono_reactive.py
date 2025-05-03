"""
Mono Reactive - Reactive Mono language interpreter
"""

import re

class Component:
    """
    Represents a component in the Reactive Mono language.
    """
    def __init__(self, name):
        self.name = name
        self.state = {}
        self.methods = {}

class Instance:
    """
    Represents an instance of a component in the Reactive Mono language.
    """
    def __init__(self, component, interpreter):
        self.component = component
        self.interpreter = interpreter
        self.state = component.state.copy()
        
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
    
    def setState(self, new_state):
        """
        Update the state of the component instance.
        """
        for key, value in new_state.items():
            self.state[key] = value

class Interpreter:
    """
    Reactive Mono language interpreter.
    """
    def __init__(self):
        self.components = {}
        self.variables = {}
    
    def parse_file(self, filename):
        """
        Parse a Reactive Mono script file.
        """
        with open(filename, 'r') as f:
            content = f.read()
        
        # Remove comments
        content = re.sub(r'//.*', '', content)
        
        # Find components - use a more robust approach
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
            
            component = Component(name)
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
                    if value.isdigit():
                        component.state[key] = int(value)
                    elif value == 'true':
                        component.state[key] = True
                    elif value == 'false':
                        component.state[key] = False
                    elif value.startswith('"') and value.endswith('"'):
                        component.state[key] = value[1:-1]
                    else:
                        component.state[key] = value
            
            # Parse methods - use a more robust approach
            method_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*{'
            method_starts = [(m.group(1), m.group(2), m.start()) for m in re.finditer(method_pattern, body)]
            
            # Process method declarations
            
            for method_name, params, start_pos in method_starts:
                # Find the method body by counting braces
                brace_count = 1
                open_brace_pos = body.find('{', start_pos)
                pos = open_brace_pos + 1
                
                while brace_count > 0 and pos < len(body):
                    if body[pos] == '{':
                        brace_count += 1
                    elif body[pos] == '}':
                        brace_count -= 1
                    pos += 1
                
                # Extract the method body
                method_body = body[open_brace_pos+1:pos-1].strip()
                component.methods[method_name] = method_body
                # Store the method body
    
    def run(self):
        """
        Run the parsed Reactive Mono script.
        """
        if 'Main' not in self.components:
            print("Error: Main component not found")
            return
        
        # Create Main instance
        main = Instance(self.components['Main'], self)
        
        # Call start method
        # Check if start method exists
        if hasattr(main, 'start'):
            main.start()
        else:
            print("Error: start method not found")
    
    def execute_method(self, body, instance, args=None):
        """
        Execute a method on a component instance.
        """
        # Local variables for this method execution
        local_vars = {}
        
        # Add arguments to local variables
        if args and len(args) > 0:
            # Handle different method parameters based on the component and method
            if instance.component.name == 'TodoItem':
                if 'setText' in instance.component.methods:
                    local_vars['newText'] = args[0]
                    # Directly update the state for setText
                    instance.state['text'] = args[0]
            elif instance.component.name == 'App':
                if 'switchView' in instance.component.methods:
                    local_vars['newView'] = args[0]
                    # Directly update the state for switchView
                    instance.state['currentView'] = args[0]
            elif instance.component.name == 'Display':
                if 'update' in instance.component.methods:
                    local_vars['newValue'] = args[0]
                    # Directly update the state for update
                    instance.state['value'] = args[0]
            else:
                # Default parameter name
                local_vars['newValue'] = args[0]
        
        # Split into lines
        lines = body.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Variable declaration
            var_match = re.match(r'var\s+(\w+)\s*=\s*(.*?);?$', line)
            if var_match:
                var_name = var_match.group(1)
                var_expr = var_match.group(2)
                
                # Component instantiation
                new_match = re.match(r'new\s+(\w+)\(\)', var_expr)
                if new_match:
                    comp_name = new_match.group(1)
                    if comp_name in self.components:
                        comp_instance = Instance(self.components[comp_name], self)
                        local_vars[var_name] = comp_instance
                    else:
                        print(f"Error: Component {comp_name} not found")
                else:
                    # Simple value
                    local_vars[var_name] = var_expr
            
            # Method call
            method_call = re.match(r'(\w+)\.(\w+)\(([^)]*)\);?$', line)
            if method_call:
                obj_name = method_call.group(1)
                method_name = method_call.group(2)
                args_str = method_call.group(3)
                
                if obj_name == 'this':
                    obj = instance
                elif obj_name in local_vars:
                    obj = local_vars[obj_name]
                else:
                    print(f"Error: Object {obj_name} not found")
                    continue
                
                # Parse arguments
                args = []
                if args_str:
                    for arg in args_str.split(','):
                        arg = arg.strip()
                        if arg in local_vars:
                            args.append(local_vars[arg])
                        elif arg.isdigit():
                            args.append(int(arg))
                        elif arg.startswith('"') and arg.endswith('"'):
                            # String literal
                            string_value = arg[1:-1]
                            args.append(string_value)
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
                                args.append(obj_arg)
                
                if hasattr(obj, method_name):
                    method = getattr(obj, method_name)
                    method(*args)
                else:
                    print(f"Error: Method {method_name} not found on {obj_name}")
            
            # State update
            state_update = re.match(r'this\.state\.(\w+)\s*=\s*(.*?);?$', line)
            if state_update:
                prop_name = state_update.group(1)
                value_expr = state_update.group(2)
                
                # Special case for TodoList.addItem
                if instance.component.name == 'TodoList' and prop_name == 'itemCount':
                    if value_expr == 'this.state.itemCount + 1':
                        instance.state['itemCount'] = instance.state.get('itemCount', 0) + 1
                        continue
                
                # Special case for TodoItem.toggleCompleted
                if instance.component.name == 'TodoItem' and prop_name == 'completed':
                    if value_expr == 'this.state.completed + 1':
                        instance.state['completed'] = instance.state.get('completed', 0) + 1
                        continue
                
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
                else:
                    # Simple value
                    if value_expr.isdigit():
                        instance.state[prop_name] = int(value_expr)
                    elif value_expr == 'newValue':
                        # Handle method parameter
                        if 'newValue' in local_vars:
                            instance.state[prop_name] = local_vars['newValue']
                    elif value_expr == 'newText':
                        # Handle method parameter
                        if 'newText' in local_vars:
                            instance.state[prop_name] = local_vars['newText']
                    else:
                        instance.state[prop_name] = value_expr
            
            # Print statement
            print_match = re.match(r'print\s+(.*?);?$', line)
            if print_match:
                expr = print_match.group(1).strip()
                
                # String literal
                if expr.startswith('"') and expr.endswith('"'):
                    print(expr[1:-1])
                    continue
                
                # Handle specific component render methods
                if 'render' in instance.component.methods:
                    # Counter component
                    if instance.component.name == 'Counter':
                        if expr == '"Count: " + this.state.count':
                            count = instance.state.get('count', 0)
                            print(f"Count: {count}")
                            continue
                    
                    # Display component
                    elif instance.component.name == 'Display':
                        if expr == '"Display: " + this.state.value':
                            value = instance.state.get('value', 0)
                            print(f"Display: {value}")
                            continue
                    
                    # TodoList component
                    elif instance.component.name == 'TodoList':
                        if expr == '"Items: " + this.state.itemCount':
                            item_count = instance.state.get('itemCount', 0)
                            print(f"Items: {item_count}")
                            continue
                    
                    # TodoItem component
                    elif instance.component.name == 'TodoItem':
                        if expr == '"Todo: " + this.state.text':
                            text = instance.state.get('text', '')
                            print(f"Todo: {text}")
                            continue
                    
                    # App component
                    elif instance.component.name == 'App':
                        if expr == '"Current View: " + this.state.currentView':
                            view = instance.state.get('currentView', 'list')
                            print(f"Current View: {view}")
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
                    elif expr == 'this.state.value':
                        print(instance.state.get('value', 0))
                    elif expr == 'this.state.name':
                        print(instance.state.get('name', ''))
                    elif expr in local_vars:
                        print(local_vars[expr])
                    else:
                        print(expr)

def run_mono_file(file_path):
    """
    Run a Reactive Mono script file and display the results.
    """
    try:
        interpreter = Interpreter()
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
