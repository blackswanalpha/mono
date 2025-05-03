"""
Mono Elements - Component element system for the Mono language

This module provides support for:
1. Primitive Elements: Built-in elements
2. Composite Elements: Custom elements composed of other components
3. Element Hierarchy: Parent-child relationships with event bubbling/capturing
4. Slots: Placeholders for dynamic content injection
"""

import re
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union

class Element:
    """
    Base class for all elements in the Mono language.
    """
    def __init__(self, tag: str, attributes: Dict[str, Any] = None, children: List['Element'] = None):
        self.tag = tag
        self.attributes = attributes or {}
        self.children = children or []
        self.parent: Optional['Element'] = None
        self.slots: Dict[str, List['Element']] = {"default": []}
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Set parent reference for all children
        for child in self.children:
            child.parent = self
    
    def add_child(self, child: 'Element') -> None:
        """Add a child element."""
        self.children.append(child)
        child.parent = self
    
    def add_to_slot(self, slot_name: str, element: 'Element') -> None:
        """Add an element to a named slot."""
        if slot_name not in self.slots:
            self.slots[slot_name] = []
        self.slots[slot_name].append(element)
        element.parent = self
    
    def add_event_listener(self, event_name: str, handler: Callable) -> None:
        """Add an event listener to this element."""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
    
    def dispatch_event(self, event_name: str, event_data: Any = None, bubble: bool = True) -> None:
        """Dispatch an event on this element."""
        # Handle the event on this element
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                handler(event_data)
        
        # Bubble the event up to the parent if needed
        if bubble and self.parent:
            self.parent.dispatch_event(event_name, event_data, bubble)
    
    def render(self) -> str:
        """Render this element as a string."""
        attrs = " ".join([f'{k}="{v}"' for k, v in self.attributes.items()])
        attrs_str = f" {attrs}" if attrs else ""
        
        if not self.children and not any(self.slots.values()):
            return f"<{self.tag}{attrs_str} />"
        
        # Render children
        children_str = ""
        for child in self.children:
            children_str += child.render()
        
        # Render slots
        for slot_name, elements in self.slots.items():
            if slot_name == "default":
                for element in elements:
                    children_str += element.render()
            else:
                slot_content = ""
                for element in elements:
                    slot_content += element.render()
                if slot_content:
                    children_str += f'<slot name="{slot_name}">{slot_content}</slot>'
        
        return f"<{self.tag}{attrs_str}>{children_str}</{self.tag}>"

class PrimitiveElement(Element):
    """
    Represents a primitive (built-in) element in the Mono language.
    """
    def __init__(self, tag: str, attributes: Dict[str, Any] = None, children: List[Element] = None):
        super().__init__(tag, attributes, children)
        self.is_primitive = True

class CompositeElement(Element):
    """
    Represents a composite element (custom component) in the Mono language.
    """
    def __init__(self, component_name: str, attributes: Dict[str, Any] = None, children: List[Element] = None):
        super().__init__(component_name.lower(), attributes, children)
        self.component_name = component_name
        self.is_primitive = False
        self.component_instance = None
    
    def set_component_instance(self, instance: Any) -> None:
        """Set the component instance for this element."""
        self.component_instance = instance
    
    def render(self) -> str:
        """Render this composite element."""
        if self.component_instance and hasattr(self.component_instance, 'render'):
            # If the component has a render method, use it
            return self.component_instance.render()
        
        # Otherwise, fall back to the default rendering
        return super().render()

class Slot(Element):
    """
    Represents a slot element for content injection.
    """
    def __init__(self, name: str = "default"):
        super().__init__("slot", {"name": name})
        self.slot_name = name
    
    def render(self) -> str:
        """Render this slot with its content."""
        if self.parent and self.slot_name in self.parent.slots:
            content = ""
            for element in self.parent.slots[self.slot_name]:
                content += element.render()
            return content
        return ""

class ElementParser:
    """
    Parser for Mono element templates.
    """
    def __init__(self):
        self.primitive_tags = {
            "div", "span", "p", "h1", "h2", "h3", "h4", "h5", "h6",
            "button", "input", "textarea", "select", "option",
            "ul", "ol", "li", "table", "tr", "td", "th",
            "img", "a", "form", "label"
        }
    
    def parse(self, template: str) -> Element:
        """Parse a template string into an element tree."""
        # Remove whitespace and newlines
        template = re.sub(r'\s+', ' ', template.strip())
        
        # Simple parsing for demonstration purposes
        # In a real implementation, you would use a proper parser
        
        # Check if it's a self-closing tag
        if template.endswith("/>"):
            # Extract tag and attributes
            match = re.match(r'<(\w+)([^>]*)\/>', template)
            if match:
                tag = match.group(1)
                attrs_str = match.group(2).strip()
                attributes = self._parse_attributes(attrs_str)
                
                if tag in self.primitive_tags:
                    return PrimitiveElement(tag, attributes)
                else:
                    return CompositeElement(tag, attributes)
        
        # Regular opening and closing tags
        match = re.match(r'<(\w+)([^>]*)>(.*)<\/\1>', template, re.DOTALL)
        if match:
            tag = match.group(1)
            attrs_str = match.group(2).strip()
            content = match.group(3).strip()
            attributes = self._parse_attributes(attrs_str)
            
            # Parse children
            children = self._parse_children(content)
            
            if tag == "slot":
                slot_name = attributes.get("name", "default")
                return Slot(slot_name)
            elif tag in self.primitive_tags:
                return PrimitiveElement(tag, attributes, children)
            else:
                return CompositeElement(tag, attributes, children)
        
        # If no match, return a text node (represented as a span)
        return PrimitiveElement("span", {"text": template})
    
    def _parse_attributes(self, attrs_str: str) -> Dict[str, Any]:
        """Parse attribute string into a dictionary."""
        attributes = {}
        if not attrs_str:
            return attributes
        
        # Match attribute patterns like key="value" or key='value' or key=value
        attr_pattern = r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|(\w+))'
        for match in re.finditer(attr_pattern, attrs_str):
            key = match.group(1)
            # Get the first non-None value from the capture groups
            value = next((g for g in match.groups()[1:] if g is not None), "")
            attributes[key] = value
        
        return attributes
    
    def _parse_children(self, content: str) -> List[Element]:
        """Parse content string into child elements."""
        children = []
        
        # This is a simplified parser that doesn't handle nested elements correctly
        # In a real implementation, you would use a proper parser
        
        # Find all top-level elements
        elements = re.findall(r'<(\w+)([^>]*)(?:>(.*?)<\/\1>|\/>)', content, re.DOTALL)
        for tag, attrs_str, inner_content in elements:
            if tag == "slot":
                attributes = self._parse_attributes(attrs_str)
                slot_name = attributes.get("name", "default")
                children.append(Slot(slot_name))
            elif tag in self.primitive_tags:
                element = self.parse(f"<{tag}{attrs_str}>{inner_content}</{tag}>")
                children.append(element)
            else:
                element = self.parse(f"<{tag}{attrs_str}>{inner_content}</{tag}>")
                children.append(element)
        
        return children

class ElementInterpreter:
    """
    Interpreter for Mono elements.
    """
    def __init__(self):
        self.parser = ElementParser()
        self.components = {}
        self.instances = {}
    
    def register_component(self, name: str, component: Any) -> None:
        """Register a component with the interpreter."""
        self.components[name] = component
    
    def create_element(self, tag: str, attributes: Dict[str, Any] = None, children: List[Element] = None) -> Element:
        """Create an element with the given tag, attributes, and children."""
        if tag in self.parser.primitive_tags:
            return PrimitiveElement(tag, attributes, children)
        elif tag in self.components:
            element = CompositeElement(tag, attributes, children)
            # Create a component instance and associate it with the element
            component = self.components[tag]
            instance = self._create_component_instance(component)
            element.set_component_instance(instance)
            return element
        else:
            # Unknown tag, treat as a custom element
            return CompositeElement(tag, attributes, children)
    
    def _create_component_instance(self, component: Any) -> Any:
        """Create an instance of a component."""
        # This would depend on your component system
        # For now, just return the component itself
        return component
    
    def parse_template(self, template: str) -> Element:
        """Parse a template string into an element tree."""
        return self.parser.parse(template)
    
    def render_element(self, element: Element) -> str:
        """Render an element to a string."""
        return element.render()
