# Frame Types in Switch

Frames in the Switch framework are hierarchical component containers with their own lifecycle hooks, scoped state, and isolation. The framework now includes several pre-built frame types for common UI patterns.

## Available Frame Types

### Main Frame

The Main Frame is a general-purpose frame that serves as the root container for your application.

```mono
{{ '@/frames/main-frame.mono' }}

// Use the frame
var frame = SwitchEnhanced.frame.create({
    name: "MainFrame",
    state: {
        title: "My Application"
    }
});
```

### Modal Frame

The Modal Frame provides a dialog box that appears on top of the current page.

```mono
{{ '@/frames/modal-frame.mono' }}

// Use the frame
var modal = SwitchEnhanced.frame.create({
    name: "ModalFrame",
    state: {
        title: "Confirmation",
        isOpen: false
    }
});

// Open the modal
modal.open();
```

### Sidebar Frame

The Sidebar Frame provides a collapsible side navigation panel.

```mono
{{ '@/frames/sidebar-frame.mono' }}

// Use the frame
var sidebar = SwitchEnhanced.frame.create({
    name: "SidebarFrame",
    state: {
        title: "Navigation",
        items: [
            {
                id: "home",
                label: "Home",
                icon: "bi bi-house"
            },
            {
                id: "settings",
                label: "Settings",
                icon: "bi bi-gear"
            }
        ]
    }
});
```

### Tabbed Frame

The Tabbed Frame provides a tabbed interface for organizing content.

```mono
{{ '@/frames/tabbed-frame.mono' }}

// Use the frame
var tabs = SwitchEnhanced.frame.create({
    name: "TabbedFrame",
    state: {
        tabs: [
            {
                id: "home",
                label: "Home",
                icon: "bi bi-house"
            },
            {
                id: "settings",
                label: "Settings",
                icon: "bi bi-gear"
            }
        ],
        activeTab: "home"
    }
});
```

## Frame Lifecycle Hooks

All frames support the following lifecycle hooks:

- `frameWillLoad`: Called before the frame is loaded
- `frameDidLoad`: Called after the frame is loaded
- `frameWillUnload`: Called before the frame is unloaded
- `frameDidUnload`: Called after the frame is unloaded

Example:

```mono
frame MyFrame {
    function frameWillLoad() {
        console.log("Frame will load");
    }
    
    function frameDidLoad() {
        console.log("Frame did load");
    }
    
    function frameWillUnload() {
        console.log("Frame will unload");
    }
    
    function frameDidUnload() {
        console.log("Frame did unload");
    }
}
```

## Frame-Scoped State

Frames have their own state that is isolated from other components:

```mono
frame MyFrame {
    state {
        counter: number = 0
    }
    
    function increment() {
        this.state.counter++;
    }
}
```

## Using Frames

### Basic Usage

```mono
// Import the frame
{{ '@/frames/modal-frame.mono' }}

component MyPage {
    state {
        modalOpen: boolean = false
    }
    
    function openModal() {
        this.state.modalOpen = true;
    }
    
    function render() {
        // Create the component
        var myPage = SwitchEnhanced.component.create({
            name: "MyPage"
        });
        
        // Create the modal frame
        var modal = SwitchEnhanced.frame.create({
            name: "ModalFrame",
            state: {
                title: "Confirmation",
                isOpen: this.state.modalOpen
            }
        });
        
        // Add the frame to the component
        myPage.addFrame(modal);
        
        // Return the HTML
        return `
            <div class="my-page">
                <button data-event="click" data-action="openModal">Open Modal</button>
                
                <div class="modal-container" data-frame="ModalFrame">
                    <!-- Modal will be rendered here -->
                </div>
            </div>
        `;
    }
}
```

### Frame Communication

Frames can communicate with each other and with components using events:

```mono
// In a frame
this.triggerEvent("sidebar:toggle", { isCollapsed: true });

// In a component
function handleSidebarToggle(event) {
    console.log("Sidebar toggled:", event.detail.isCollapsed);
}
```

## Modal Frame

### Properties

- `title`: The title of the modal
- `isOpen`: Whether the modal is open
- `size`: The size of the modal (`small`, `medium`, `large`, `fullscreen`)
- `closeOnEscape`: Whether to close the modal when the escape key is pressed
- `closeOnBackdropClick`: Whether to close the modal when the backdrop is clicked
- `showCloseButton`: Whether to show the close button
- `animation`: The animation to use (`fade`, `slide`, `zoom`, `none`)
- `position`: The position of the modal (`center`, `top`, `bottom`)
- `maxWidth`: The maximum width of the modal
- `zIndex`: The z-index of the modal

### Methods

- `open()`: Open the modal
- `close()`: Close the modal

### Events

- `modal:open`: Triggered when the modal is opened
- `modal:close`: Triggered when the modal is closed

## Sidebar Frame

### Properties

- `title`: The title of the sidebar
- `position`: The position of the sidebar (`left`, `right`)
- `width`: The width of the sidebar
- `collapsedWidth`: The width of the sidebar when collapsed
- `isCollapsed`: Whether the sidebar is collapsed
- `isVisible`: Whether the sidebar is visible
- `isDarkMode`: Whether the sidebar is in dark mode
- `showToggle`: Whether to show the toggle button
- `showHeader`: Whether to show the header
- `showFooter`: Whether to show the footer
- `activeItem`: The ID of the active item
- `items`: An array of items to display

### Methods

- `toggleCollapse()`: Toggle the collapsed state
- `toggleVisibility()`: Toggle the visibility
- `setActiveItem(itemId)`: Set the active item

### Events

- `sidebar:toggle`: Triggered when the sidebar is toggled
- `sidebar:visibility`: Triggered when the visibility is toggled
- `sidebar:activeItem`: Triggered when the active item is changed

## Tabbed Frame

### Properties

- `activeTab`: The ID of the active tab
- `tabs`: An array of tabs to display
- `position`: The position of the tabs (`top`, `bottom`, `left`, `right`)
- `style`: The style of the tabs (`tabs`, `pills`, `underline`, `buttons`)
- `size`: The size of the tabs (`small`, `medium`, `large`)
- `justified`: Whether the tabs should be justified
- `fill`: Whether the tabs should fill the available space
- `vertical`: Whether the tabs should be vertical
- `fade`: Whether to use fade animation
- `lazy`: Whether to use lazy loading for tab content
- `swipeable`: Whether the tabs are swipeable
- `draggable`: Whether the tabs are draggable

### Methods

- `setActiveTab(tabId)`: Set the active tab

### Events

- `tab:change`: Triggered when the active tab is changed
- `tab:loaded`: Triggered when the tabs are loaded

## Best Practices

1. **Use Appropriate Frame Types**: Choose the right frame for your UI pattern
2. **Leverage Lifecycle Hooks**: Use lifecycle hooks for setup and cleanup
3. **Isolate State**: Keep frame-specific state within the frame
4. **Use Events for Communication**: Communicate between frames using events
5. **Combine with Layouts**: Use frames within layouts for complex UIs
