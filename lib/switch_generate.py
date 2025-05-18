"""
Switch Generate - Generate code for Switch applications

This module provides functions for generating code for Switch applications.
It can generate:
1. Components
2. Pages
3. Store modules
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

def generate_component(name: str, directory: str = "components", force: bool = False) -> bool:
    """Generate a new component."""
    # Validate the component name
    if not re.match(r"^[A-Za-z][A-Za-z0-9]*$", name):
        print(f"Error: Invalid component name: {name}")
        print("Component names must start with a letter and contain only letters and numbers.")
        return False
    
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Create the component file
    file_path = os.path.join(directory, f"{name}.mono")
    
    # Check if the file already exists
    if os.path.exists(file_path) and not force:
        print(f"Error: Component already exists: {file_path}")
        print("Use --force to overwrite.")
        return False
    
    # Create the component
    with open(file_path, "w") as f:
        f.write(f"""//  __  __                   
// |  \/  | ___  _ __   ___  
// | |\/| |/ _ \| '_ \ / _ \ 
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/ 
//                           
// {name} Component

component {name} {{
    state {{
        // Component state
    }}
    
    function constructor() {{
        // Initialize the component
    }}
    
    function render() {{
        // Register client-side event handlers
        switch.clientEvent("click", "handleClick");
        
        // Create the component
        var component = switch.component("{name}", {{
            // Component props
        }});
        
        // Return the HTML
        return `
            <div class="{name.lower()}">
                <h2>{name}</h2>
                <p>This is the {name} component.</p>
                <button data-event="click">Click me</button>
            </div>
        `;
    }}
    
    function handleClick(event) {{
        // Handle click events
        console.log("Button clicked");
    }}
}}
""")
    
    print(f"Component created: {file_path}")
    return True

def generate_page(name: str, directory: str = "pages", force: bool = False) -> bool:
    """Generate a new page."""
    # Validate the page name
    if not re.match(r"^[A-Za-z][A-Za-z0-9]*$", name):
        print(f"Error: Invalid page name: {name}")
        print("Page names must start with a letter and contain only letters and numbers.")
        return False
    
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Create the page file
    file_path = os.path.join(directory, f"{name}.mono")
    
    # Check if the file already exists
    if os.path.exists(file_path) and not force:
        print(f"Error: Page already exists: {file_path}")
        print("Use --force to overwrite.")
        return False
    
    # Create the page
    with open(file_path, "w") as f:
        f.write(f"""//  __  __                   
// |  \/  | ___  _ __   ___  
// | |\/| |/ _ \| '_ \ / _ \ 
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/ 
//                           
// {name} Page

component {name}Page {{
    state {{
        title: string = "{name} Page",
        loading: boolean = false
    }}
    
    function constructor() {{
        // Initialize the page
    }}
    
    function render() {{
        // Register client-side event handlers
        switch.clientEvent("click", "handleClick");
        
        // Create the component
        var page = switch.component("{name}Page", {{
            title: this.state.title,
            loading: this.state.loading
        }});
        
        // Return the HTML
        return `
            <div class="page {name.lower()}-page">
                <header class="page-header">
                    <div class="container">
                        <h1>${{this.state.title}}</h1>
                    </div>
                </header>
                
                <main class="page-content">
                    <div class="container">
                        ${{this.state.loading ? '<div class="loading">Loading...</div>' : this.renderContent()}}
                    </div>
                </main>
                
                <footer class="page-footer">
                    <div class="container">
                        <p>&copy; ${{new Date().getFullYear()}} Switch App. All rights reserved.</p>
                    </div>
                </footer>
            </div>
        `;
    }}
    
    function renderContent() {{
        return `
            <div class="content">
                <h2>Welcome to the {name} Page</h2>
                <p>This is the {name} page content.</p>
                <button class="btn btn-primary" data-event="click">Click me</button>
            </div>
        `;
    }}
    
    function handleClick(event) {{
        // Handle click events
        console.log("Button clicked");
    }}
}}

// Export the page component
export {name}Page;
""")
    
    print(f"Page created: {file_path}")
    return True

def generate_store(name: str, directory: str = "store", force: bool = False) -> bool:
    """Generate a store module."""
    # Validate the store name
    if not re.match(r"^[A-Za-z][A-Za-z0-9]*$", name):
        print(f"Error: Invalid store name: {name}")
        print("Store names must start with a letter and contain only letters and numbers.")
        return False
    
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Create the store file
    file_path = os.path.join(directory, f"{name}.mono")
    
    # Check if the file already exists
    if os.path.exists(file_path) and not force:
        print(f"Error: Store already exists: {file_path}")
        print("Use --force to overwrite.")
        return False
    
    # Create the store
    with open(file_path, "w") as f:
        f.write(f"""//  __  __                   
// |  \/  | ___  _ __   ___  
// | |\/| |/ _ \| '_ \ / _ \ 
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/ 
//                           
// {name} Store

// Import the store module
import switch.store;

// Define the state
const {name.lower()}State = {{
    // State properties
    count: 0,
    loading: false,
    error: null,
    data: []
}};

// Define the mutations
const {name.lower()}Mutations = {{
    // Mutations
    increment(state) {{
        state.count += 1;
    }},
    
    decrement(state) {{
        state.count -= 1;
    }},
    
    setLoading(state, loading) {{
        state.loading = loading;
    }},
    
    setError(state, error) {{
        state.error = error;
    }},
    
    setData(state, data) {{
        state.data = data;
    }}
}};

// Define the actions
const {name.lower()}Actions = {{
    // Actions
    incrementAsync(context) {{
        setTimeout(() => {{
            context.commit('increment');
        }}, 1000);
    }},
    
    fetchData(context) {{
        context.commit('setLoading', true);
        context.commit('setError', null);
        
        // Simulate an API call
        setTimeout(() => {{
            try {{
                // Simulate data
                const data = [
                    {{ id: 1, name: 'Item 1' }},
                    {{ id: 2, name: 'Item 2' }},
                    {{ id: 3, name: 'Item 3' }}
                ];
                
                context.commit('setData', data);
                context.commit('setLoading', false);
            }} catch (error) {{
                context.commit('setError', error.message);
                context.commit('setLoading', false);
            }}
        }}, 1000);
    }}
}};

// Define the getters
const {name.lower()}Getters = {{
    // Getters
    doubleCount(state) {{
        return state.count * 2;
    }},
    
    isLoading(state) {{
        return state.loading;
    }},
    
    hasError(state) {{
        return state.error !== null;
    }},
    
    getData(state) {{
        return state.data;
    }}
}};

// Create the store module
const {name.lower()}Store = switch.store.createModule({{
    namespaced: true,
    state: {name.lower()}State,
    mutations: {name.lower()}Mutations,
    actions: {name.lower()}Actions,
    getters: {name.lower()}Getters
}});

// Export the store module
export {name.lower()}Store;
""")
    
    print(f"Store created: {file_path}")
    return True
