"""
Mono Layouts - Layout system for the Mono language

This module provides support for:
1. Declarative Layouts: Define component arrangements using JSON/DSL or code
2. Responsive Design: Adapt components to screen sizes or environments
3. Constraint-Based Layouts: Use rules like "center vertically" or "fill 80% width"
4. Z-Ordering: Manage overlapping components
"""

import re
import json
import math
from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable

class LayoutUnit:
    """
    Represents a layout unit (px, %, vh, vw, etc.).
    """
    def __init__(self, value: Union[int, float], unit: str = "px"):
        self.value = value
        self.unit = unit
    
    def __str__(self) -> str:
        return f"{self.value}{self.unit}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "value": self.value,
            "unit": self.unit
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LayoutUnit':
        """Create from dictionary."""
        return cls(
            value=data["value"],
            unit=data.get("unit", "px")
        )
    
    @classmethod
    def parse(cls, value: str) -> 'LayoutUnit':
        """Parse a string into a LayoutUnit."""
        if not value:
            return cls(0, "px")
        
        # Extract the numeric part and unit
        match = re.match(r'([-+]?\d*\.?\d+)([a-zA-Z%]+)?', value)
        if not match:
            return cls(0, "px")
        
        num_value = float(match.group(1))
        unit = match.group(2) or "px"
        
        return cls(num_value, unit)

class LayoutConstraint:
    """
    Represents a layout constraint (e.g., "center", "fill", "start", "end").
    """
    def __init__(self, type: str, value: Optional[LayoutUnit] = None, reference: Optional[str] = None):
        self.type = type  # center, fill, start, end, etc.
        self.value = value  # Optional value (e.g., for margins, padding)
        self.reference = reference  # Optional reference to another element
    
    def __str__(self) -> str:
        if self.value:
            return f"{self.type}({self.value})"
        elif self.reference:
            return f"{self.type}(ref:{self.reference})"
        else:
            return self.type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {"type": self.type}
        if self.value:
            result["value"] = self.value.to_dict()
        if self.reference:
            result["reference"] = self.reference
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LayoutConstraint':
        """Create from dictionary."""
        value = None
        if "value" in data:
            value = LayoutUnit.from_dict(data["value"])
        
        return cls(
            type=data["type"],
            value=value,
            reference=data.get("reference")
        )
    
    @classmethod
    def parse(cls, value: str) -> 'LayoutConstraint':
        """Parse a string into a LayoutConstraint."""
        if not value:
            return cls("none")
        
        # Check for simple constraints
        if value in ["center", "fill", "start", "end", "stretch"]:
            return cls(value)
        
        # Check for constraints with values
        match = re.match(r'(\w+)\((.*?)\)', value)
        if match:
            constraint_type = match.group(1)
            constraint_value = match.group(2)
            
            # Check if it's a reference
            if constraint_value.startswith("ref:"):
                return cls(constraint_type, reference=constraint_value[4:])
            
            # Otherwise, it's a value
            return cls(constraint_type, LayoutUnit.parse(constraint_value))
        
        # Default
        return cls(value)

class LayoutBox:
    """
    Represents a layout box with position, size, and constraints.
    """
    def __init__(self, 
                 width: Optional[LayoutUnit] = None, 
                 height: Optional[LayoutUnit] = None,
                 x: Optional[LayoutUnit] = None,
                 y: Optional[LayoutUnit] = None,
                 z_index: int = 0):
        self.width = width or LayoutUnit(0, "px")
        self.height = height or LayoutUnit(0, "px")
        self.x = x or LayoutUnit(0, "px")
        self.y = y or LayoutUnit(0, "px")
        self.z_index = z_index
        self.constraints: Dict[str, LayoutConstraint] = {}
        self.children: List['LayoutBox'] = []
        self.parent: Optional['LayoutBox'] = None
        self.element_id: Optional[str] = None
    
    def add_constraint(self, name: str, constraint: LayoutConstraint) -> None:
        """Add a constraint to the layout box."""
        self.constraints[name] = constraint
    
    def add_child(self, child: 'LayoutBox') -> None:
        """Add a child layout box."""
        self.children.append(child)
        child.parent = self
    
    def remove_child(self, child: 'LayoutBox') -> None:
        """Remove a child layout box."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "width": self.width.to_dict(),
            "height": self.height.to_dict(),
            "x": self.x.to_dict(),
            "y": self.y.to_dict(),
            "z_index": self.z_index,
            "constraints": {name: constraint.to_dict() for name, constraint in self.constraints.items()},
            "children": [child.to_dict() for child in self.children],
            "element_id": self.element_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LayoutBox':
        """Create from dictionary."""
        box = cls(
            width=LayoutUnit.from_dict(data["width"]),
            height=LayoutUnit.from_dict(data["height"]),
            x=LayoutUnit.from_dict(data["x"]),
            y=LayoutUnit.from_dict(data["y"]),
            z_index=data.get("z_index", 0)
        )
        
        box.element_id = data.get("element_id")
        
        # Add constraints
        for name, constraint_data in data.get("constraints", {}).items():
            box.add_constraint(name, LayoutConstraint.from_dict(constraint_data))
        
        # Add children
        for child_data in data.get("children", []):
            child = LayoutBox.from_dict(child_data)
            box.add_child(child)
        
        return box

class Layout:
    """
    Represents a layout with a root layout box.
    """
    def __init__(self, name: str, root: Optional[LayoutBox] = None):
        self.name = name
        self.root = root or LayoutBox()
        self.media_queries: Dict[str, Dict[str, Any]] = {}
        self.variables: Dict[str, Any] = {}
    
    def add_media_query(self, name: str, condition: str, layout: 'Layout') -> None:
        """Add a media query to the layout."""
        self.media_queries[name] = {
            "condition": condition,
            "layout": layout
        }
    
    def add_variable(self, name: str, value: Any) -> None:
        """Add a variable to the layout."""
        self.variables[name] = value
    
    def find_box_by_id(self, element_id: str) -> Optional[LayoutBox]:
        """Find a layout box by its element ID."""
        return self._find_box_by_id_recursive(self.root, element_id)
    
    def _find_box_by_id_recursive(self, box: LayoutBox, element_id: str) -> Optional[LayoutBox]:
        """Recursively find a layout box by its element ID."""
        if box.element_id == element_id:
            return box
        
        for child in box.children:
            result = self._find_box_by_id_recursive(child, element_id)
            if result:
                return result
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "root": self.root.to_dict(),
            "media_queries": {
                name: {
                    "condition": query["condition"],
                    "layout": query["layout"].to_dict()
                }
                for name, query in self.media_queries.items()
            },
            "variables": self.variables
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Layout':
        """Create from dictionary."""
        layout = cls(
            name=data["name"],
            root=LayoutBox.from_dict(data["root"])
        )
        
        # Add variables
        for name, value in data.get("variables", {}).items():
            layout.add_variable(name, value)
        
        # Add media queries
        for name, query_data in data.get("media_queries", {}).items():
            query_layout = Layout.from_dict(query_data["layout"])
            layout.add_media_query(name, query_data["condition"], query_layout)
        
        return layout

class LayoutParser:
    """
    Parser for layout definition files.
    """
    def __init__(self):
        pass
    
    def parse_file(self, file_path: str) -> Layout:
        """Parse a layout definition file."""
        with open(file_path, "r") as f:
            content = f.read()
        return self.parse(content)
    
    def parse(self, content: str) -> Layout:
        """Parse layout definition content."""
        # Try to parse as JSON first
        try:
            data = json.loads(content)
            return Layout.from_dict(data)
        except json.JSONDecodeError:
            # If not JSON, try to parse as DSL
            return self.parse_dsl(content)
    
    def parse_dsl(self, content: str) -> Layout:
        """Parse layout definition DSL."""
        # Remove comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # Find layout definition
        layout_match = re.search(r'layout\s+(\w+)\s*{([^}]*)}', content, re.DOTALL)
        if not layout_match:
            raise ValueError("No layout definition found")
        
        layout_name = layout_match.group(1)
        layout_body = layout_match.group(2)
        
        # Create the layout
        layout = Layout(layout_name)
        
        # Find variables
        variables_match = re.search(r'variables\s*{([^}]*)}', layout_body)
        if variables_match:
            variables_body = variables_match.group(1)
            for var_match in re.finditer(r'(\w+)\s*:\s*([^;]*);', variables_body):
                var_name = var_match.group(1)
                var_value = var_match.group(2).strip()
                
                # Try to convert to appropriate type
                if var_value.isdigit():
                    var_value = int(var_value)
                elif re.match(r'^[-+]?\d*\.\d+$', var_value):
                    var_value = float(var_value)
                elif var_value.lower() in ('true', 'false'):
                    var_value = var_value.lower() == 'true'
                
                layout.add_variable(var_name, var_value)
        
        # Find root element
        root_match = re.search(r'root\s*{([^}]*)}', layout_body)
        if root_match:
            root_body = root_match.group(1)
            layout.root = self._parse_element(root_body, "root")
        
        # Find media queries
        for media_match in re.finditer(r'media\s+(\w+)\s*\(([^)]*)\)\s*{([^}]*)}', layout_body):
            media_name = media_match.group(1)
            media_condition = media_match.group(2)
            media_body = media_match.group(3)
            
            # Create a new layout for the media query
            media_layout = Layout(f"{layout_name}_{media_name}")
            
            # Parse the media query body
            media_root_match = re.search(r'root\s*{([^}]*)}', media_body)
            if media_root_match:
                media_root_body = media_root_match.group(1)
                media_layout.root = self._parse_element(media_root_body, "root")
            
            # Add the media query to the layout
            layout.add_media_query(media_name, media_condition, media_layout)
        
        return layout
    
    def _parse_element(self, element_body: str, element_id: Optional[str] = None) -> LayoutBox:
        """Parse an element definition."""
        box = LayoutBox()
        box.element_id = element_id
        
        # Find width and height
        width_match = re.search(r'width\s*:\s*([^;]*);', element_body)
        if width_match:
            box.width = LayoutUnit.parse(width_match.group(1).strip())
        
        height_match = re.search(r'height\s*:\s*([^;]*);', element_body)
        if height_match:
            box.height = LayoutUnit.parse(height_match.group(1).strip())
        
        # Find position
        x_match = re.search(r'x\s*:\s*([^;]*);', element_body)
        if x_match:
            box.x = LayoutUnit.parse(x_match.group(1).strip())
        
        y_match = re.search(r'y\s*:\s*([^;]*);', element_body)
        if y_match:
            box.y = LayoutUnit.parse(y_match.group(1).strip())
        
        # Find z-index
        z_index_match = re.search(r'z-index\s*:\s*([^;]*);', element_body)
        if z_index_match:
            box.z_index = int(z_index_match.group(1).strip())
        
        # Find constraints
        for constraint_match in re.finditer(r'constraint\s+(\w+)\s*:\s*([^;]*);', element_body):
            constraint_name = constraint_match.group(1)
            constraint_value = constraint_match.group(2).strip()
            box.add_constraint(constraint_name, LayoutConstraint.parse(constraint_value))
        
        # Find children
        for child_match in re.finditer(r'element\s+(\w+)\s*{([^}]*)}', element_body):
            child_id = child_match.group(1)
            child_body = child_match.group(2)
            child_box = self._parse_element(child_body, child_id)
            box.add_child(child_box)
        
        return box

class LayoutEngine:
    """
    Engine for calculating layout positions and sizes.
    """
    def __init__(self, viewport_width: int = 800, viewport_height: int = 600):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
    
    def set_viewport(self, width: int, height: int) -> None:
        """Set the viewport size."""
        self.viewport_width = width
        self.viewport_height = height
    
    def calculate_layout(self, layout: Layout) -> Layout:
        """Calculate the layout positions and sizes."""
        # Check if any media queries apply
        for name, query in layout.media_queries.items():
            if self._evaluate_media_query(query["condition"]):
                # Merge the media query layout with the base layout
                return self._merge_layouts(layout, query["layout"])
        
        # Calculate the layout for the root box
        self._calculate_box_layout(layout.root, 0, 0, self.viewport_width, self.viewport_height)
        
        return layout
    
    def _evaluate_media_query(self, condition: str) -> bool:
        """Evaluate a media query condition."""
        # Parse the condition
        match = re.match(r'(min-width|max-width|min-height|max-height)\s*:\s*(\d+)(px|%|vh|vw)?', condition)
        if not match:
            return False
        
        query_type = match.group(1)
        query_value = int(match.group(2))
        query_unit = match.group(3) or "px"
        
        # Convert units
        if query_unit == "%":
            if query_type in ("min-width", "max-width"):
                query_value = (query_value / 100) * self.viewport_width
            else:
                query_value = (query_value / 100) * self.viewport_height
        elif query_unit == "vh":
            query_value = (query_value / 100) * self.viewport_height
        elif query_unit == "vw":
            query_value = (query_value / 100) * self.viewport_width
        
        # Evaluate the condition
        if query_type == "min-width":
            return self.viewport_width >= query_value
        elif query_type == "max-width":
            return self.viewport_width <= query_value
        elif query_type == "min-height":
            return self.viewport_height >= query_value
        elif query_type == "max-height":
            return self.viewport_height <= query_value
        
        return False
    
    def _merge_layouts(self, base_layout: Layout, media_layout: Layout) -> Layout:
        """Merge a media query layout with the base layout."""
        # Create a new layout
        merged_layout = Layout(base_layout.name)
        
        # Copy variables from base layout
        for name, value in base_layout.variables.items():
            merged_layout.add_variable(name, value)
        
        # Override with variables from media layout
        for name, value in media_layout.variables.items():
            merged_layout.add_variable(name, value)
        
        # Merge the root boxes
        merged_layout.root = self._merge_boxes(base_layout.root, media_layout.root)
        
        return merged_layout
    
    def _merge_boxes(self, base_box: LayoutBox, media_box: LayoutBox) -> LayoutBox:
        """Merge two layout boxes."""
        # Create a new box with properties from the base box
        merged_box = LayoutBox(
            width=base_box.width,
            height=base_box.height,
            x=base_box.x,
            y=base_box.y,
            z_index=base_box.z_index
        )
        merged_box.element_id = base_box.element_id
        
        # Copy constraints from base box
        for name, constraint in base_box.constraints.items():
            merged_box.add_constraint(name, constraint)
        
        # Override with properties from media box
        if media_box.width.value != 0:
            merged_box.width = media_box.width
        if media_box.height.value != 0:
            merged_box.height = media_box.height
        if media_box.x.value != 0:
            merged_box.x = media_box.x
        if media_box.y.value != 0:
            merged_box.y = media_box.y
        if media_box.z_index != 0:
            merged_box.z_index = media_box.z_index
        
        # Override with constraints from media box
        for name, constraint in media_box.constraints.items():
            merged_box.add_constraint(name, constraint)
        
        # Create a map of base children by ID
        base_children_map = {child.element_id: child for child in base_box.children if child.element_id}
        
        # Create a map of media children by ID
        media_children_map = {child.element_id: child for child in media_box.children if child.element_id}
        
        # Merge children
        for child_id, base_child in base_children_map.items():
            if child_id in media_children_map:
                # Merge the child
                merged_child = self._merge_boxes(base_child, media_children_map[child_id])
                merged_box.add_child(merged_child)
            else:
                # Just copy the base child
                merged_box.add_child(base_child)
        
        # Add any media children that aren't in the base
        for child_id, media_child in media_children_map.items():
            if child_id not in base_children_map:
                merged_box.add_child(media_child)
        
        return merged_box
    
    def _calculate_box_layout(self, box: LayoutBox, parent_x: int, parent_y: int, parent_width: int, parent_height: int) -> None:
        """Calculate the layout for a box and its children."""
        # Calculate width and height
        width = self._calculate_dimension(box.width, parent_width)
        height = self._calculate_dimension(box.height, parent_height)
        
        # Apply constraints
        x = parent_x
        y = parent_y
        
        # Horizontal constraints
        if "left" in box.constraints:
            x = parent_x + self._calculate_constraint_value(box.constraints["left"], parent_width)
        elif "right" in box.constraints:
            right_value = self._calculate_constraint_value(box.constraints["right"], parent_width)
            x = parent_x + parent_width - width - right_value
        elif "centerX" in box.constraints:
            center_value = self._calculate_constraint_value(box.constraints["centerX"], parent_width)
            x = parent_x + (parent_width - width) / 2 + center_value
        
        # Vertical constraints
        if "top" in box.constraints:
            y = parent_y + self._calculate_constraint_value(box.constraints["top"], parent_height)
        elif "bottom" in box.constraints:
            bottom_value = self._calculate_constraint_value(box.constraints["bottom"], parent_height)
            y = parent_y + parent_height - height - bottom_value
        elif "centerY" in box.constraints:
            center_value = self._calculate_constraint_value(box.constraints["centerY"], parent_height)
            y = parent_y + (parent_height - height) / 2 + center_value
        
        # Update the box position and size
        box.x = LayoutUnit(x, "px")
        box.y = LayoutUnit(y, "px")
        box.width = LayoutUnit(width, "px")
        box.height = LayoutUnit(height, "px")
        
        # Calculate layout for children
        for child in box.children:
            self._calculate_box_layout(child, x, y, width, height)
    
    def _calculate_dimension(self, dimension: LayoutUnit, parent_dimension: int) -> int:
        """Calculate a dimension value based on its unit."""
        if dimension.unit == "px":
            return int(dimension.value)
        elif dimension.unit == "%":
            return int((dimension.value / 100) * parent_dimension)
        elif dimension.unit == "vh":
            return int((dimension.value / 100) * self.viewport_height)
        elif dimension.unit == "vw":
            return int((dimension.value / 100) * self.viewport_width)
        else:
            return int(dimension.value)  # Default to pixels
    
    def _calculate_constraint_value(self, constraint: LayoutConstraint, parent_dimension: int) -> int:
        """Calculate a constraint value."""
        if constraint.value:
            return self._calculate_dimension(constraint.value, parent_dimension)
        else:
            return 0

class LayoutRenderer:
    """
    Renderer for layouts.
    """
    def __init__(self):
        pass
    
    def render_to_html(self, layout: Layout) -> str:
        """Render a layout to HTML."""
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append("  <meta charset=\"UTF-8\">")
        html.append("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
        html.append("  <title>Mono Layout</title>")
        html.append("  <style>")
        html.append("    body { margin: 0; padding: 0; }")
        html.append("    .layout-container { position: relative; width: 100%; height: 100vh; }")
        html.append("    .layout-box { position: absolute; box-sizing: border-box; border: 1px solid #ccc; }")
        html.append("  </style>")
        html.append("</head>")
        html.append("<body>")
        html.append("  <div class=\"layout-container\">")
        
        # Render the root box and its children
        self._render_box_html(layout.root, html, 4)
        
        html.append("  </div>")
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)
    
    def _render_box_html(self, box: LayoutBox, html: List[str], indent: int) -> None:
        """Render a layout box to HTML."""
        indent_str = " " * indent
        
        # Start the box
        html.append(f"{indent_str}<div class=\"layout-box\" id=\"{box.element_id or 'box'}\" style=\"")
        html.append(f"{indent_str}  left: {box.x.value}px;")
        html.append(f"{indent_str}  top: {box.y.value}px;")
        html.append(f"{indent_str}  width: {box.width.value}px;")
        html.append(f"{indent_str}  height: {box.height.value}px;")
        html.append(f"{indent_str}  z-index: {box.z_index};")
        html.append(f"{indent_str}\">")
        
        # Add the box ID as content
        if box.element_id:
            html.append(f"{indent_str}  <div style=\"padding: 8px;\">{box.element_id}</div>")
        
        # Render children
        for child in sorted(box.children, key=lambda b: b.z_index):
            self._render_box_html(child, html, indent + 2)
        
        # End the box
        html.append(f"{indent_str}</div>")
    
    def render_to_css(self, layout: Layout) -> str:
        """Render a layout to CSS."""
        css = []
        css.append("/* Mono Layout CSS */")
        css.append("")
        css.append(".layout-container {")
        css.append("  position: relative;")
        css.append("  width: 100%;")
        css.append("  height: 100vh;")
        css.append("}")
        css.append("")
        
        # Render the root box and its children
        self._render_box_css(layout.root, css)
        
        # Add media queries
        for name, query in layout.media_queries.items():
            css.append("")
            css.append(f"@media ({query['condition']}) {{")
            self._render_box_css(query["layout"].root, css, "  ")
            css.append("}")
        
        return "\n".join(css)
    
    def _render_box_css(self, box: LayoutBox, css: List[str], indent: str = "") -> None:
        """Render a layout box to CSS."""
        if not box.element_id:
            return
        
        css.append(f"{indent}#{box.element_id} {{")
        css.append(f"{indent}  position: absolute;")
        css.append(f"{indent}  left: {box.x.value}{box.x.unit};")
        css.append(f"{indent}  top: {box.y.value}{box.y.unit};")
        css.append(f"{indent}  width: {box.width.value}{box.width.unit};")
        css.append(f"{indent}  height: {box.height.value}{box.height.unit};")
        css.append(f"{indent}  z-index: {box.z_index};")
        css.append(f"{indent}}}")
        css.append("")
        
        # Render children
        for child in box.children:
            self._render_box_css(child, css, indent)

def parse_layout_file(file_path: str) -> Layout:
    """
    Parse a layout definition file and return a Layout object.
    """
    parser = LayoutParser()
    return parser.parse_file(file_path)

def calculate_layout(layout: Layout, viewport_width: int = 800, viewport_height: int = 600) -> Layout:
    """
    Calculate the layout positions and sizes.
    """
    engine = LayoutEngine(viewport_width, viewport_height)
    return engine.calculate_layout(layout)

def render_layout_to_html(layout: Layout) -> str:
    """
    Render a layout to HTML.
    """
    renderer = LayoutRenderer()
    return renderer.render_to_html(layout)

def render_layout_to_css(layout: Layout) -> str:
    """
    Render a layout to CSS.
    """
    renderer = LayoutRenderer()
    return renderer.render_to_css(layout)
