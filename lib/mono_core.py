"""
Mono Core - Basic Mono language interpreter
"""

import re

class MonoComponent:
    """
    Represents a component in the Mono language.
    """
    def __init__(self, name):
        self.name = name
        self.vars = {}
        self.methods = {}

class MonoInterpreter:
    """
    Basic Mono language interpreter.
    """
    def __init__(self):
        self.components = {}
        self.current_component = None

    def parse(self, script):
        """
        Parse a Mono script and extract components, variables, and methods.
        """
        # First, clean up the script by removing comments and normalizing whitespace
        script = re.sub(r'//.*$', '', script, flags=re.MULTILINE)  # Remove single-line comments
        
        # Split the script into component blocks
        components = re.findall(r'component\s+(\w+)\s*{([^}]*)}', script, re.DOTALL)
        
        for comp_name, comp_body in components:
            # Create the component
            self.current_component = MonoComponent(comp_name)
            self.components[comp_name] = self.current_component
            
            # Process component body line by line
            lines = comp_body.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                i += 1
                
                if not line:
                    continue
                
                # Variable declaration
                if line.startswith('var '):
                    var_decl = re.match(r'var\s+(\w+)\s*=\s*(.*?)\s*;?$', line)
                    if var_decl:
                        var_name = var_decl.group(1)
                        var_value = var_decl.group(2)
                        
                        # Handle numeric values
                        if var_value.isdigit():
                            value = int(var_value)
                        elif var_value.replace('.', '', 1).isdigit() and var_value.count('.') <= 1:
                            value = float(var_value)
                        else:
                            # For other values, try to evaluate or use as string
                            try:
                                value = eval(var_value)
                            except:
                                value = var_value
                        
                        self.current_component.vars[var_name] = value
                
                # Function declaration
                elif line.startswith('function '):
                    func_match = re.match(r'function\s+(\w+)\s*\(([^)]*)\)', line)
                    if func_match:
                        func_name = func_match.group(1)
                        params = func_match.group(2).split(',') if func_match.group(2) else []
                        params = [p.strip() for p in params]
                        
                        # Find function body
                        body_lines = []
                        # Skip the opening brace
                        while i < len(lines) and '{' not in lines[i-1]:
                            i += 1
                        
                        # Collect body lines until closing brace
                        brace_count = 1
                        while i < len(lines):
                            body_line = lines[i].strip()
                            
                            if '{' in body_line:
                                brace_count += 1
                            if '}' in body_line:
                                brace_count -= 1
                                if brace_count == 0:
                                    break
                                    
                            if body_line:
                                body_lines.append(body_line)
                            i += 1
                        
                        self.current_component.methods[func_name] = {
                            'params': params,
                            'body': body_lines
                        }

    def execute(self):
        """
        Execute the parsed Mono script.
        """
        main = self.components['Main']
        
        # Create the Main component instance
        main_instance = self.create_component_instance('Main')
        
        # Execute the start method
        self.execute_method(main_instance, 'start', [])

    def create_component_instance(self, component_name):
        """
        Create an instance of a component.
        """
        if component_name not in self.components:
            raise ValueError(f"Component {component_name} not found")
        
        component = self.components[component_name]
        
        # Create a new instance object
        instance = type('MonoInstance', (), {
            'component_name': component_name,
            'vars': {},
            'methods': {}
        })
        
        # Add methods
        for method_name, method_info in component.methods.items():
            # Create a method that executes the body
            def create_method(name):
                def method(*args):
                    return self.execute_method(instance, name, args)
                return method
            
            instance.methods[method_name] = create_method(method_name)
            setattr(instance, method_name, instance.methods[method_name])
        
        return instance

    def execute_method(self, instance, method_name, args):
        """
        Execute a method on a component instance.
        """
        if method_name not in self.components[instance.component_name].methods:
            raise ValueError(f"Method {method_name} not found in component {instance.component_name}")
        
        method_info = self.components[instance.component_name].methods[method_name]
        
        # Create local variables for the method parameters
        local_vars = {}
        for i, param_name in enumerate(method_info['params']):
            if i < len(args):
                local_vars[param_name] = args[i]
        
        # Execute each line in the method body
        result = None
        i = 0
        while i < len(method_info['body']):
            line = method_info['body'][i]
            i += 1
            
            # Variable declaration
            var_match = re.match(r'var\s+(\w+)\s*=\s*(.*?)\s*;?$', line)
            if var_match:
                var_name = var_match.group(1)
                var_expr = var_match.group(2)
                
                # Handle component instantiation
                new_match = re.search(r'new\s+(\w+)\(\)', var_expr)
                if new_match:
                    comp_name = new_match.group(1)
                    local_vars[var_name] = self.create_component_instance(comp_name)
                else:
                    # Regular variable assignment
                    try:
                        # Try to evaluate the expression
                        value = self.evaluate_expression(var_expr, instance, local_vars)
                        local_vars[var_name] = value
                    except:
                        local_vars[var_name] = var_expr
            
            # Method call
            elif '.' in line and '(' in line:
                method_call_match = re.search(r'(\w+)\.(\w+)\((.*?)\)', line)
                if method_call_match:
                    obj_name = method_call_match.group(1)
                    method_name = method_call_match.group(2)
                    args_str = method_call_match.group(3)
                    
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
                                    value = self.evaluate_expression(arg, instance, local_vars)
                                    args.append(value)
                                except:
                                    args.append(arg)
                        
                        # Call the method
                        if hasattr(obj, method_name):
                            method = getattr(obj, method_name)
                            method(*args)
            
            # Print statement
            elif line.startswith('print '):
                expr = line[6:].strip()
                if expr.endswith(';'):
                    expr = expr[:-1]
                
                # Evaluate the expression
                try:
                    value = self.evaluate_expression(expr, instance, local_vars)
                    print(value)
                except Exception as e:
                    print(f"Error evaluating expression: {expr}")
                    print(e)
        
        return result

    def evaluate_expression(self, expr, instance, local_vars):
        """
        Evaluate a Mono expression in the context of an instance and local variables.
        """
        # Handle string literals
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        
        # Handle numeric literals
        if expr.isdigit():
            return int(expr)
        if expr.replace('.', '', 1).isdigit() and expr.count('.') <= 1:
            return float(expr)
        
        # Handle boolean literals
        if expr.lower() == 'true':
            return True
        if expr.lower() == 'false':
            return False
        
        # Handle local variables
        if expr in local_vars:
            return local_vars[expr]
        
        # Handle binary operations
        if '+' in expr:
            parts = expr.split('+', 1)
            left = self.evaluate_expression(parts[0].strip(), instance, local_vars)
            right = self.evaluate_expression(parts[1].strip(), instance, local_vars)
            return left + right
        if '-' in expr:
            parts = expr.split('-', 1)
            left = self.evaluate_expression(parts[0].strip(), instance, local_vars)
            right = self.evaluate_expression(parts[1].strip(), instance, local_vars)
            return left - right
        if '*' in expr:
            parts = expr.split('*', 1)
            left = self.evaluate_expression(parts[0].strip(), instance, local_vars)
            right = self.evaluate_expression(parts[1].strip(), instance, local_vars)
            return left * right
        if '/' in expr:
            parts = expr.split('/', 1)
            left = self.evaluate_expression(parts[0].strip(), instance, local_vars)
            right = self.evaluate_expression(parts[1].strip(), instance, local_vars)
            return left / right
        
        # If all else fails, return the expression as is
        return expr

def run_mono_file(file_path):
    """
    Run a Mono script file and display the results.
    """
    try:
        with open(file_path) as f:
            script = f.read()
        
        interpreter = MonoInterpreter()
        interpreter.parse(script)
        interpreter.execute()
        return True
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return False
    except Exception as e:
        print(f"Error executing Mono script: {e}")
        import traceback
        traceback.print_exc()
        return False
