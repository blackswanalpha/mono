"""
Mono Data Structures - Comprehensive data structure library for Mono

This module provides a unified interface for data structures in Mono, integrating:
1. Layouts for visual arrangement
2. Kits for component collections
3. Frames for isolation and state management

It supports various data structures including:
- Tables (for tabular data)
- Trees (for hierarchical data)
- Graphs (for network data)
- Lists (for linear data)
- Grids (for matrix data)
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable

from lib.mono_layouts import Layout, LayoutBox, parse_layout_file, calculate_layout, render_layout_to_html
from lib.mono_kits import Kit, KitRegistry, KitComponent
from lib.mono_combined_interpreter import run_mono_file

class DataStructure:
    """Base class for all data structures."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.data = None
        self.layout = None
        self.components = {}

    def set_data(self, data: Any) -> None:
        """Set the data for this data structure."""
        self.data = data

    def get_data(self) -> Any:
        """Get the data for this data structure."""
        return self.data

    def set_layout(self, layout: Layout) -> None:
        """Set the layout for this data structure."""
        self.layout = layout

    def get_layout(self) -> Optional[Layout]:
        """Get the layout for this data structure."""
        return self.layout

    def add_component(self, name: str, component: KitComponent) -> None:
        """Add a component to this data structure."""
        self.components[name] = component

    def get_component(self, name: str) -> Optional[KitComponent]:
        """Get a component from this data structure."""
        return self.components.get(name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert this data structure to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "data": self.data,
            "layout": self.layout.to_dict() if self.layout else None,
            "components": {name: component.to_dict() for name, component in self.components.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataStructure':
        """Create a data structure from a dictionary."""
        structure = cls(data["name"], data.get("description", ""))
        structure.data = data.get("data")

        if data.get("layout"):
            structure.layout = Layout.from_dict(data["layout"])

        for name, component_data in data.get("components", {}).items():
            structure.components[name] = KitComponent.from_dict(component_data)

        return structure

class TableStructure(DataStructure):
    """Table data structure for tabular data."""

    def __init__(self, name: str = "Table", description: str = "Tabular data structure"):
        super().__init__(name, description)
        self.columns = []
        self.sort_column = None
        self.sort_direction = "asc"
        self.page_size = 10
        self.current_page = 1

    def set_columns(self, columns: List[Dict[str, str]]) -> None:
        """Set the columns for this table."""
        self.columns = columns

    def get_columns(self) -> List[Dict[str, str]]:
        """Get the columns for this table."""
        return self.columns

    def sort(self, column: str, direction: str = None) -> None:
        """Sort the table by a column."""
        self.sort_column = column

        if direction:
            self.sort_direction = direction
        else:
            # Toggle direction if sorting by the same column
            if self.sort_column == column:
                self.sort_direction = "desc" if self.sort_direction == "asc" else "asc"

        # Sort the data
        if isinstance(self.data, list):
            self.data.sort(key=lambda x: x.get(column, ""), reverse=self.sort_direction == "desc")

    def paginate(self, page_size: int = None, page: int = None) -> List[Any]:
        """Get a page of data."""
        if page_size:
            self.page_size = page_size

        if page:
            self.current_page = page

        if not isinstance(self.data, list):
            return []

        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size

        return self.data[start:end]

    def get_page_count(self) -> int:
        """Get the number of pages."""
        if not isinstance(self.data, list):
            return 0

        return (len(self.data) + self.page_size - 1) // self.page_size

    def to_dict(self) -> Dict[str, Any]:
        """Convert this table to a dictionary."""
        data = super().to_dict()
        data.update({
            "columns": self.columns,
            "sort_column": self.sort_column,
            "sort_direction": self.sort_direction,
            "page_size": self.page_size,
            "current_page": self.current_page
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TableStructure':
        """Create a table from a dictionary."""
        table = super().from_dict(data)
        table.columns = data.get("columns", [])
        table.sort_column = data.get("sort_column")
        table.sort_direction = data.get("sort_direction", "asc")
        table.page_size = data.get("page_size", 10)
        table.current_page = data.get("current_page", 1)
        return table

class TreeStructure(DataStructure):
    """Tree data structure for hierarchical data."""

    def __init__(self, name: str = "Tree", description: str = "Hierarchical data structure"):
        super().__init__(name, description)
        self.expanded_nodes = set()

    def expand_node(self, node_id: str) -> None:
        """Expand a node."""
        self.expanded_nodes.add(node_id)

    def collapse_node(self, node_id: str) -> None:
        """Collapse a node."""
        if node_id in self.expanded_nodes:
            self.expanded_nodes.remove(node_id)

    def toggle_node(self, node_id: str) -> None:
        """Toggle a node's expanded state."""
        if node_id in self.expanded_nodes:
            self.collapse_node(node_id)
        else:
            self.expand_node(node_id)

    def is_expanded(self, node_id: str) -> bool:
        """Check if a node is expanded."""
        return node_id in self.expanded_nodes

    def expand_all(self) -> None:
        """Expand all nodes."""
        def collect_node_ids(node):
            if not node:
                return

            node_id = node.get("id")
            if node_id:
                self.expanded_nodes.add(node_id)

            children = node.get("children", [])
            for child in children:
                collect_node_ids(child)

        collect_node_ids(self.data)

    def collapse_all(self) -> None:
        """Collapse all nodes."""
        self.expanded_nodes.clear()

    def find_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Find a node by ID."""
        def find_node_recursive(node, node_id):
            if not node:
                return None

            if node.get("id") == node_id:
                return node

            children = node.get("children", [])
            for child in children:
                result = find_node_recursive(child, node_id)
                if result:
                    return result

            return None

        return find_node_recursive(self.data, node_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert this tree to a dictionary."""
        data = super().to_dict()
        data.update({
            "expanded_nodes": list(self.expanded_nodes)
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TreeStructure':
        """Create a tree from a dictionary."""
        tree = super().from_dict(data)
        tree.expanded_nodes = set(data.get("expanded_nodes", []))
        return tree

class GraphStructure(DataStructure):
    """Graph data structure for network data."""

    def __init__(self, name: str = "Graph", description: str = "Network data structure"):
        super().__init__(name, description)
        self.nodes = []
        self.edges = []
        self.selected_node = None

    def set_nodes(self, nodes: List[Dict[str, Any]]) -> None:
        """Set the nodes for this graph."""
        self.nodes = nodes

    def set_edges(self, edges: List[Dict[str, Any]]) -> None:
        """Set the edges for this graph."""
        self.edges = edges

    def add_node(self, node: Dict[str, Any]) -> None:
        """Add a node to this graph."""
        self.nodes.append(node)

    def add_edge(self, edge: Dict[str, Any]) -> None:
        """Add an edge to this graph."""
        self.edges.append(edge)

    def select_node(self, node_id: str) -> None:
        """Select a node."""
        self.selected_node = node_id

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID."""
        for node in self.nodes:
            if node.get("id") == node_id:
                return node
        return None

    def get_edges_for_node(self, node_id: str) -> List[Dict[str, Any]]:
        """Get all edges connected to a node."""
        return [edge for edge in self.edges if edge.get("source") == node_id or edge.get("target") == node_id]

    def to_dict(self) -> Dict[str, Any]:
        """Convert this graph to a dictionary."""
        data = super().to_dict()
        data.update({
            "nodes": self.nodes,
            "edges": self.edges,
            "selected_node": self.selected_node
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphStructure':
        """Create a graph from a dictionary."""
        graph = super().from_dict(data)
        graph.nodes = data.get("nodes", [])
        graph.edges = data.get("edges", [])
        graph.selected_node = data.get("selected_node")
        return graph

class ListStructure(DataStructure):
    """List data structure for linear data."""

    def __init__(self, name: str = "List", description: str = "Linear data structure"):
        super().__init__(name, description)
        self.selected_index = -1
        self.sort_key = None
        self.sort_direction = "asc"

    def select_item(self, index: int) -> None:
        """Select an item by index."""
        if isinstance(self.data, list) and 0 <= index < len(self.data):
            self.selected_index = index

    def get_selected_item(self) -> Optional[Any]:
        """Get the selected item."""
        if isinstance(self.data, list) and 0 <= self.selected_index < len(self.data):
            return self.data[self.selected_index]
        return None

    def sort(self, key: str = None, direction: str = None) -> None:
        """Sort the list."""
        if key:
            self.sort_key = key

        if direction:
            self.sort_direction = direction

        if isinstance(self.data, list) and self.sort_key:
            self.data.sort(key=lambda x: x.get(self.sort_key, ""), reverse=self.sort_direction == "desc")

    def to_dict(self) -> Dict[str, Any]:
        """Convert this list to a dictionary."""
        data = super().to_dict()
        data.update({
            "selected_index": self.selected_index,
            "sort_key": self.sort_key,
            "sort_direction": self.sort_direction
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ListStructure':
        """Create a list from a dictionary."""
        list_structure = super().from_dict(data)
        list_structure.selected_index = data.get("selected_index", -1)
        list_structure.sort_key = data.get("sort_key")
        list_structure.sort_direction = data.get("sort_direction", "asc")
        return list_structure

class GridStructure(DataStructure):
    """Grid data structure for matrix data."""

    def __init__(self, name: str = "Grid", description: str = "Matrix data structure"):
        super().__init__(name, description)
        self.rows = 0
        self.columns = 0
        self.selected_cell = None

    def set_dimensions(self, rows: int, columns: int) -> None:
        """Set the dimensions of this grid."""
        self.rows = rows
        self.columns = columns

        # Initialize data if needed
        if not isinstance(self.data, list):
            self.data = []

        # Ensure data has the right dimensions
        while len(self.data) < rows:
            self.data.append([None] * columns)

        for i in range(len(self.data)):
            while len(self.data[i]) < columns:
                self.data[i].append(None)

    def get_cell(self, row: int, column: int) -> Any:
        """Get a cell value."""
        if isinstance(self.data, list) and 0 <= row < len(self.data) and 0 <= column < len(self.data[row]):
            return self.data[row][column]
        return None

    def set_cell(self, row: int, column: int, value: Any) -> None:
        """Set a cell value."""
        if isinstance(self.data, list) and 0 <= row < len(self.data) and 0 <= column < len(self.data[row]):
            self.data[row][column] = value

    def select_cell(self, row: int, column: int) -> None:
        """Select a cell."""
        if 0 <= row < self.rows and 0 <= column < self.columns:
            self.selected_cell = (row, column)

    def to_dict(self) -> Dict[str, Any]:
        """Convert this grid to a dictionary."""
        data = super().to_dict()
        data.update({
            "rows": self.rows,
            "columns": self.columns,
            "selected_cell": self.selected_cell
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GridStructure':
        """Create a grid from a dictionary."""
        grid = super().from_dict(data)
        grid.rows = data.get("rows", 0)
        grid.columns = data.get("columns", 0)
        grid.selected_cell = data.get("selected_cell")
        return grid

class DataStructureManager:
    """Manager for data structures."""

    def __init__(self):
        self.structures = {}
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kits")
        self.kit_registry = KitRegistry(registry_dir)

    def create_structure(self, type_name: str, name: str, description: str = "") -> DataStructure:
        """Create a new data structure."""
        structure = None

        if type_name == "table":
            structure = TableStructure(name, description)
        elif type_name == "tree":
            structure = TreeStructure(name, description)
        elif type_name == "graph":
            structure = GraphStructure(name, description)
        elif type_name == "list":
            structure = ListStructure(name, description)
        elif type_name == "grid":
            structure = GridStructure(name, description)
        else:
            structure = DataStructure(name, description)

        self.structures[name] = structure
        return structure

    def get_structure(self, name: str) -> Optional[DataStructure]:
        """Get a data structure by name."""
        return self.structures.get(name)

    def list_structures(self) -> List[str]:
        """List all data structures."""
        return list(self.structures.keys())

    def delete_structure(self, name: str) -> bool:
        """Delete a data structure."""
        if name in self.structures:
            del self.structures[name]
            return True
        return False

    def save_structure(self, name: str, file_path: str) -> bool:
        """Save a data structure to a file."""
        structure = self.get_structure(name)
        if not structure:
            return False

        try:
            with open(file_path, "w") as f:
                json.dump(structure.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving structure: {e}")
            return False

    def load_structure(self, file_path: str) -> Optional[DataStructure]:
        """Load a data structure from a file."""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            structure_type = data.get("type", "generic")

            if structure_type == "table":
                structure = TableStructure.from_dict(data)
            elif structure_type == "tree":
                structure = TreeStructure.from_dict(data)
            elif structure_type == "graph":
                structure = GraphStructure.from_dict(data)
            elif structure_type == "list":
                structure = ListStructure.from_dict(data)
            elif structure_type == "grid":
                structure = GridStructure.from_dict(data)
            else:
                structure = DataStructure.from_dict(data)

            self.structures[structure.name] = structure
            return structure
        except Exception as e:
            print(f"Error loading structure: {e}")
            return None

    def import_kit(self, kit_file: str) -> bool:
        """Import a kit for data structures."""
        try:
            kit = self.kit_registry.import_kit(kit_file)
            return kit is not None
        except Exception as e:
            print(f"Error importing kit: {e}")
            return False

    def render_structure(self, name: str, format: str = "html") -> Optional[str]:
        """Render a data structure."""
        structure = self.get_structure(name)
        if not structure:
            return None

        # Use the layout if available
        if structure.layout:
            if format == "html":
                return render_layout_to_html(structure.layout)
            else:
                return json.dumps(structure.to_dict(), indent=2)
        else:
            # Fallback to JSON
            return json.dumps(structure.to_dict(), indent=2)

def run_data_structure_demo() -> bool:
    """Run the data structure demo."""
    script_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "data_structure_demo.mono")

    if not os.path.isfile(script_file):
        print(f"Error: Demo file not found at {script_file}")
        return False

    print("Running Mono Data Structure Demo...")
    run_mono_file(script_file)
    return True
