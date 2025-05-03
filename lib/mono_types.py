"""
Mono Type System - Static typing with type inference for Mono language
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Any, Union, Tuple, Callable

class TypeKind(Enum):
    """Enum representing different kinds of types in Mono."""
    PRIMITIVE = 1
    COMPONENT = 2
    FUNCTION = 3
    GENERIC = 4
    GENERIC_INSTANCE = 5
    ARRAY = 6
    UNION = 7
    VOID = 8
    ANY = 9
    UNKNOWN = 10

class MonoType:
    """Base class for all types in Mono."""
    def __init__(self, name: str, kind: TypeKind):
        self.name = name
        self.kind = kind
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, MonoType):
            return False
        return self.name == other.name and self.kind == other.kind
    
    def is_assignable_from(self, other: 'MonoType') -> bool:
        """Check if a value of type 'other' can be assigned to a variable of this type."""
        # Any type can be assigned to itself
        if self == other:
            return True
        
        # Any type can be assigned to Any
        if self.kind == TypeKind.ANY:
            return True
        
        # Unknown type can't be assigned to anything except Any
        if other.kind == TypeKind.UNKNOWN:
            return self.kind == TypeKind.ANY
        
        # Specific type compatibility rules will be implemented in subclasses
        return False

class PrimitiveType(MonoType):
    """Represents primitive types like int, float, string, bool."""
    def __init__(self, name: str):
        super().__init__(name, TypeKind.PRIMITIVE)
    
    def is_assignable_from(self, other: MonoType) -> bool:
        if super().is_assignable_from(other):
            return True
        
        # Special case: int can be assigned to float
        if self.name == "float" and other.name == "int":
            return True
        
        return False

class ComponentType(MonoType):
    """Represents a component type."""
    def __init__(self, name: str, properties: Dict[str, MonoType] = None, methods: Dict[str, 'FunctionType'] = None):
        super().__init__(name, TypeKind.COMPONENT)
        self.properties = properties or {}
        self.methods = methods or {}
    
    def is_assignable_from(self, other: MonoType) -> bool:
        if super().is_assignable_from(other):
            return True
        
        # A component can be assigned from another component if they have the same name
        # This is a simplification; in a real type system, we might check structural compatibility
        if other.kind == TypeKind.COMPONENT:
            return self.name == other.name
        
        return False

class FunctionType(MonoType):
    """Represents a function type with parameter types and return type."""
    def __init__(self, param_types: List[MonoType], return_type: MonoType, name: str = "function"):
        super().__init__(name, TypeKind.FUNCTION)
        self.param_types = param_types
        self.return_type = return_type
    
    def __str__(self) -> str:
        params_str = ", ".join(str(t) for t in self.param_types)
        return f"{self.name}({params_str}) -> {self.return_type}"
    
    def is_assignable_from(self, other: MonoType) -> bool:
        if super().is_assignable_from(other):
            return True
        
        # Function types are compatible if parameter types and return type are compatible
        if other.kind == TypeKind.FUNCTION:
            other_func = other
            
            # Check if parameter counts match
            if len(self.param_types) != len(other_func.param_types):
                return False
            
            # Check if parameter types are compatible (contravariant)
            for i, param_type in enumerate(self.param_types):
                if not other_func.param_types[i].is_assignable_from(param_type):
                    return False
            
            # Check if return type is compatible (covariant)
            if not self.return_type.is_assignable_from(other_func.return_type):
                return False
            
            return True
        
        return False

class GenericType(MonoType):
    """Represents a generic type parameter."""
    def __init__(self, name: str, constraints: List[MonoType] = None):
        super().__init__(name, TypeKind.GENERIC)
        self.constraints = constraints or []
    
    def __str__(self) -> str:
        if not self.constraints:
            return self.name
        constraints_str = ", ".join(str(c) for c in self.constraints)
        return f"{self.name} extends {constraints_str}"
    
    def is_assignable_from(self, other: MonoType) -> bool:
        if super().is_assignable_from(other):
            return True
        
        # A generic type can accept any type that satisfies its constraints
        for constraint in self.constraints:
            if not constraint.is_assignable_from(other):
                return False
        
        return True

class GenericInstanceType(MonoType):
    """Represents an instantiation of a generic type with concrete type arguments."""
    def __init__(self, base_type: MonoType, type_args: List[MonoType], name: str = None):
        name = name or f"{base_type}<{', '.join(str(arg) for arg in type_args)}>"
        super().__init__(name, TypeKind.GENERIC_INSTANCE)
        self.base_type = base_type
        self.type_args = type_args
    
    def is_assignable_from(self, other: MonoType) -> bool:
        if super().is_assignable_from(other):
            return True
        
        # Generic instances are compatible if they have the same base type and compatible type arguments
        if other.kind == TypeKind.GENERIC_INSTANCE:
            other_generic = other
            
            # Check if base types are the same
            if self.base_type != other_generic.base_type:
                return False
            
            # Check if type argument counts match
            if len(self.type_args) != len(other_generic.type_args):
                return False
            
            # Check if type arguments are compatible (invariant for simplicity)
            for i, type_arg in enumerate(self.type_args):
                if not type_arg == other_generic.type_args[i]:
                    return False
            
            return True
        
        return False

class ArrayType(MonoType):
    """Represents an array type."""
    def __init__(self, element_type: MonoType):
        super().__init__(f"{element_type}[]", TypeKind.ARRAY)
        self.element_type = element_type
    
    def is_assignable_from(self, other: MonoType) -> bool:
        if super().is_assignable_from(other):
            return True
        
        # Arrays are compatible if their element types are compatible (covariant)
        if other.kind == TypeKind.ARRAY:
            other_array = other
            return self.element_type.is_assignable_from(other_array.element_type)
        
        return False

class UnionType(MonoType):
    """Represents a union type (A | B)."""
    def __init__(self, types: List[MonoType]):
        type_names = " | ".join(t.name for t in types)
        super().__init__(type_names, TypeKind.UNION)
        self.types = types
    
    def is_assignable_from(self, other: MonoType) -> bool:
        if super().is_assignable_from(other):
            return True
        
        # A union type can accept any type that is compatible with at least one of its member types
        for type_option in self.types:
            if type_option.is_assignable_from(other):
                return True
        
        return False

class VoidType(MonoType):
    """Represents the void type (no value)."""
    def __init__(self):
        super().__init__("void", TypeKind.VOID)
    
    def is_assignable_from(self, other: MonoType) -> bool:
        # Only void can be assigned to void
        return other.kind == TypeKind.VOID

class AnyType(MonoType):
    """Represents the any type (can be any type)."""
    def __init__(self):
        super().__init__("any", TypeKind.ANY)
    
    def is_assignable_from(self, other: MonoType) -> bool:
        # Any type can be assigned to any
        return True

class UnknownType(MonoType):
    """Represents an unknown type (used during type inference)."""
    def __init__(self):
        super().__init__("unknown", TypeKind.UNKNOWN)
    
    def is_assignable_from(self, other: MonoType) -> bool:
        # Unknown can only be assigned to any
        return False

# Built-in types
INT_TYPE = PrimitiveType("int")
FLOAT_TYPE = PrimitiveType("float")
STRING_TYPE = PrimitiveType("string")
BOOL_TYPE = PrimitiveType("bool")
VOID_TYPE = VoidType()
ANY_TYPE = AnyType()
UNKNOWN_TYPE = UnknownType()

# Type registry
class TypeRegistry:
    """Registry for all types in a Mono program."""
    def __init__(self):
        self.types: Dict[str, MonoType] = {
            "int": INT_TYPE,
            "float": FLOAT_TYPE,
            "string": STRING_TYPE,
            "bool": BOOL_TYPE,
            "void": VOID_TYPE,
            "any": ANY_TYPE,
            "unknown": UNKNOWN_TYPE
        }
        self.component_types: Dict[str, ComponentType] = {}
    
    def register_type(self, type_obj: MonoType) -> None:
        """Register a type in the registry."""
        self.types[type_obj.name] = type_obj
        if type_obj.kind == TypeKind.COMPONENT:
            self.component_types[type_obj.name] = type_obj
    
    def get_type(self, name: str) -> Optional[MonoType]:
        """Get a type by name."""
        return self.types.get(name)
    
    def get_component_type(self, name: str) -> Optional[ComponentType]:
        """Get a component type by name."""
        return self.component_types.get(name)

# Type inference
class TypeInferer:
    """Infers types for expressions and statements in Mono."""
    def __init__(self, registry: TypeRegistry):
        self.registry = registry
        self.current_scope: Dict[str, MonoType] = {}
    
    def infer_literal_type(self, value: Any) -> MonoType:
        """Infer the type of a literal value."""
        if isinstance(value, int):
            return INT_TYPE
        elif isinstance(value, float):
            return FLOAT_TYPE
        elif isinstance(value, str):
            return STRING_TYPE
        elif isinstance(value, bool):
            return BOOL_TYPE
        elif value is None:
            return VOID_TYPE
        else:
            return UNKNOWN_TYPE
    
    def infer_binary_op_type(self, left_type: MonoType, right_type: MonoType, op: str) -> MonoType:
        """Infer the result type of a binary operation."""
        # Arithmetic operations
        if op in ['+', '-', '*', '/']:
            # String concatenation
            if op == '+' and (left_type == STRING_TYPE or right_type == STRING_TYPE):
                return STRING_TYPE
            
            # Numeric operations
            if left_type == FLOAT_TYPE or right_type == FLOAT_TYPE:
                return FLOAT_TYPE
            elif left_type == INT_TYPE and right_type == INT_TYPE:
                return INT_TYPE
        
        # Comparison operations
        elif op in ['==', '!=', '<', '>', '<=', '>=']:
            return BOOL_TYPE
        
        # Logical operations
        elif op in ['&&', '||']:
            if left_type == BOOL_TYPE and right_type == BOOL_TYPE:
                return BOOL_TYPE
        
        return UNKNOWN_TYPE
    
    def infer_variable_type(self, var_name: str) -> MonoType:
        """Infer the type of a variable."""
        return self.current_scope.get(var_name, UNKNOWN_TYPE)
    
    def infer_function_call_type(self, func_type: MonoType, arg_types: List[MonoType]) -> MonoType:
        """Infer the return type of a function call."""
        if func_type.kind != TypeKind.FUNCTION:
            return UNKNOWN_TYPE
        
        # Check if argument types are compatible with parameter types
        if len(arg_types) != len(func_type.param_types):
            return UNKNOWN_TYPE
        
        for i, param_type in enumerate(func_type.param_types):
            if not param_type.is_assignable_from(arg_types[i]):
                return UNKNOWN_TYPE
        
        return func_type.return_type
    
    def infer_property_access_type(self, obj_type: MonoType, prop_name: str) -> MonoType:
        """Infer the type of a property access."""
        if obj_type.kind == TypeKind.COMPONENT:
            return obj_type.properties.get(prop_name, UNKNOWN_TYPE)
        
        return UNKNOWN_TYPE
    
    def infer_method_call_type(self, obj_type: MonoType, method_name: str, arg_types: List[MonoType]) -> MonoType:
        """Infer the return type of a method call."""
        if obj_type.kind == TypeKind.COMPONENT:
            method_type = obj_type.methods.get(method_name)
            if method_type:
                return self.infer_function_call_type(method_type, arg_types)
        
        return UNKNOWN_TYPE

# Type checker
class TypeChecker:
    """Checks types in Mono programs."""
    def __init__(self, registry: TypeRegistry, inferer: TypeInferer):
        self.registry = registry
        self.inferer = inferer
        self.errors: List[str] = []
    
    def check_assignment(self, target_type: MonoType, value_type: MonoType, location: str) -> bool:
        """Check if an assignment is type-safe."""
        if not target_type.is_assignable_from(value_type):
            self.errors.append(f"Type error at {location}: Cannot assign {value_type} to {target_type}")
            return False
        return True
    
    def check_binary_op(self, left_type: MonoType, right_type: MonoType, op: str, location: str) -> MonoType:
        """Check if a binary operation is type-safe and return the result type."""
        result_type = self.inferer.infer_binary_op_type(left_type, right_type, op)
        if result_type == UNKNOWN_TYPE:
            self.errors.append(f"Type error at {location}: Invalid operation {left_type} {op} {right_type}")
        return result_type
    
    def check_function_call(self, func_type: MonoType, arg_types: List[MonoType], location: str) -> MonoType:
        """Check if a function call is type-safe and return the result type."""
        if func_type.kind != TypeKind.FUNCTION:
            self.errors.append(f"Type error at {location}: {func_type} is not callable")
            return UNKNOWN_TYPE
        
        if len(arg_types) != len(func_type.param_types):
            self.errors.append(
                f"Type error at {location}: Expected {len(func_type.param_types)} arguments, got {len(arg_types)}"
            )
            return UNKNOWN_TYPE
        
        for i, (param_type, arg_type) in enumerate(zip(func_type.param_types, arg_types)):
            if not param_type.is_assignable_from(arg_type):
                self.errors.append(
                    f"Type error at {location}: Argument {i+1} expected {param_type}, got {arg_type}"
                )
        
        return func_type.return_type
    
    def check_property_access(self, obj_type: MonoType, prop_name: str, location: str) -> MonoType:
        """Check if a property access is type-safe and return the property type."""
        if obj_type.kind != TypeKind.COMPONENT:
            self.errors.append(f"Type error at {location}: {obj_type} has no properties")
            return UNKNOWN_TYPE
        
        prop_type = obj_type.properties.get(prop_name)
        if not prop_type:
            self.errors.append(f"Type error at {location}: {obj_type} has no property '{prop_name}'")
            return UNKNOWN_TYPE
        
        return prop_type
    
    def check_method_call(self, obj_type: MonoType, method_name: str, arg_types: List[MonoType], location: str) -> MonoType:
        """Check if a method call is type-safe and return the result type."""
        if obj_type.kind != TypeKind.COMPONENT:
            self.errors.append(f"Type error at {location}: {obj_type} has no methods")
            return UNKNOWN_TYPE
        
        method_type = obj_type.methods.get(method_name)
        if not method_type:
            self.errors.append(f"Type error at {location}: {obj_type} has no method '{method_name}'")
            return UNKNOWN_TYPE
        
        return self.check_function_call(method_type, arg_types, location)
    
    def has_errors(self) -> bool:
        """Check if there are any type errors."""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[str]:
        """Get all type errors."""
        return self.errors

# Generic type instantiation
def instantiate_generic_type(generic_type: GenericType, type_args: List[MonoType]) -> MonoType:
    """Instantiate a generic type with concrete type arguments."""
    if len(type_args) != 1:  # For simplicity, we only support one type parameter
        return UNKNOWN_TYPE
    
    # Check if type arguments satisfy constraints
    for constraint in generic_type.constraints:
        if not constraint.is_assignable_from(type_args[0]):
            return UNKNOWN_TYPE
    
    return GenericInstanceType(generic_type, type_args)

# Example of a generic component type
def create_generic_list(registry: TypeRegistry) -> None:
    """Create and register a generic List<T> component type."""
    # Create a generic type parameter T
    t_param = GenericType("T")
    
    # Create methods for List<T>
    add_method = FunctionType([t_param], VOID_TYPE, "add")
    get_method = FunctionType([INT_TYPE], t_param, "get")
    size_method = FunctionType([], INT_TYPE, "size")
    
    # Create the generic List component
    list_methods = {
        "add": add_method,
        "get": get_method,
        "size": size_method
    }
    list_properties = {
        "length": INT_TYPE
    }
    list_component = ComponentType("List", list_properties, list_methods)
    
    # Register the generic component
    registry.register_type(list_component)

# Example usage
def example_usage():
    """Example usage of the type system."""
    registry = TypeRegistry()
    inferer = TypeInferer(registry)
    checker = TypeChecker(registry, inferer)
    
    # Create and register a Counter component type
    counter_methods = {
        "increment": FunctionType([], VOID_TYPE, "increment"),
        "decrement": FunctionType([], VOID_TYPE, "decrement"),
        "getValue": FunctionType([], INT_TYPE, "getValue")
    }
    counter_properties = {
        "count": INT_TYPE
    }
    counter_component = ComponentType("Counter", counter_properties, counter_methods)
    registry.register_type(counter_component)
    
    # Create a generic List component
    create_generic_list(registry)
    
    # Check some type assignments
    checker.check_assignment(INT_TYPE, INT_TYPE, "line 1")  # Valid
    checker.check_assignment(FLOAT_TYPE, INT_TYPE, "line 2")  # Valid (int can be assigned to float)
    checker.check_assignment(INT_TYPE, FLOAT_TYPE, "line 3")  # Invalid
    
    # Check some binary operations
    checker.check_binary_op(INT_TYPE, INT_TYPE, "+", "line 4")  # Valid, returns INT_TYPE
    checker.check_binary_op(INT_TYPE, FLOAT_TYPE, "*", "line 5")  # Valid, returns FLOAT_TYPE
    checker.check_binary_op(STRING_TYPE, INT_TYPE, "+", "line 6")  # Valid, returns STRING_TYPE
    checker.check_binary_op(BOOL_TYPE, INT_TYPE, "+", "line 7")  # Invalid
    
    # Check some function calls
    increment_type = counter_component.methods["increment"]
    checker.check_function_call(increment_type, [], "line 8")  # Valid
    checker.check_function_call(increment_type, [INT_TYPE], "line 9")  # Invalid (too many arguments)
    
    # Print any errors
    for error in checker.get_errors():
        print(error)

if __name__ == "__main__":
    example_usage()
