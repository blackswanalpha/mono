# Layout Templates in Switch

The Switch framework now includes a collection of pre-built layout templates that you can use to structure your applications. These templates provide responsive, accessible, and customizable layouts for different types of applications.

## Available Layout Templates

### App Layout

The App Layout is a general-purpose layout for applications with a header, sidebar, content area, and footer.

```mono
{{ '@/layouts/app-layout.mono' }}

// Use the layout
var layout = SwitchEnhanced.layout.create({
    name: "AppLayout"
});
```

### Dashboard Layout

The Dashboard Layout is designed for admin dashboards and data-heavy applications with a grid system for cards and widgets.

```mono
{{ '@/layouts/dashboard-layout.mono' }}

// Use the layout
var layout = SwitchEnhanced.layout.create({
    name: "DashboardLayout"
});
```

### Documentation Layout

The Documentation Layout is optimized for documentation sites with a navigation sidebar, content area, and table of contents.

```mono
{{ '@/layouts/documentation-layout.mono' }}

// Use the layout
var layout = SwitchEnhanced.layout.create({
    name: "DocumentationLayout"
});
```

### Blog Layout

The Blog Layout is designed for blog sites with featured images, content area, and sidebar for related content.

```mono
{{ '@/layouts/blog-layout.mono' }}

// Use the layout
var layout = SwitchEnhanced.layout.create({
    name: "BlogLayout"
});
```

## Using Layout Templates

### Basic Usage

```mono
// Import the layout
{{ '@/layouts/dashboard-layout.mono' }}

component MyPage {
    function render() {
        // Create the component
        var myPage = SwitchEnhanced.component.create({
            name: "MyPage"
        });
        
        // Create the layout
        var layout = SwitchEnhanced.layout.create({
            name: "DashboardLayout"
        });
        
        // Apply the layout to the component
        myPage.setLayout(layout);
        
        // Return the HTML
        return `
            <div class="my-page">
                <!-- Page content -->
            </div>
        `;
    }
}
```

### Layout States

Layouts can have different states that modify their appearance and behavior:

```mono
// Create the layout
var layout = SwitchEnhanced.layout.create({
    name: "DashboardLayout",
    state: "darkMode" // Apply the dark mode state
});
```

Available states for different layouts:

- **DashboardLayout**: `collapsed`, `darkMode`
- **DocumentationLayout**: `darkMode`, `printMode`
- **BlogLayout**: `darkMode`

### Responsive Behavior

All layout templates are responsive by default and adapt to different screen sizes:

- **Mobile**: Optimized for screens smaller than 768px
- **Tablet**: Optimized for screens between 769px and 1024px
- **Desktop**: Optimized for screens larger than 1024px

### Customizing Layouts

You can customize layouts by modifying their variables:

```mono
// Create the layout with custom variables
var layout = SwitchEnhanced.layout.create({
    name: "DashboardLayout",
    variables: {
        headerHeight: "80px",
        sidebarWidth: "300px",
        footerHeight: "60px"
    }
});
```

## Layout Elements

Each layout defines a set of elements that you can target in your CSS or JavaScript:

### Dashboard Layout Elements

- `header`: The top navigation bar
- `sidebar`: The side navigation panel
- `content`: The main content area
- `footer`: The bottom footer area
- `grid`: The dashboard grid for cards
- `card`: A dashboard card
- `cardHeader`: The header of a card
- `cardBody`: The body of a card
- `cardFooter`: The footer of a card

### Documentation Layout Elements

- `header`: The top navigation bar
- `sidebar`: The side navigation panel
- `content`: The main content area
- `contentContainer`: The container with max width
- `toc`: The table of contents
- `footer`: The bottom footer area
- `section`: A documentation section
- `codeBlock`: A code block
- `note`: A note block
- `warning`: A warning block

### Blog Layout Elements

- `header`: The top navigation bar
- `hero`: The featured image section
- `heroOverlay`: The overlay on the hero image
- `heroContent`: The content in the hero section
- `main`: The main content wrapper
- `content`: The main content area
- `contentContainer`: The container with max width
- `sidebar`: The side panel
- `footer`: The bottom footer area
- `post`: A blog post
- `postHeader`: The header of a post
- `postMeta`: The metadata of a post
- `postContent`: The content of a post
- `postFooter`: The footer of a post
- `postTags`: The tags container
- `postTag`: A single tag
- `comments`: The comments section
- `comment`: A single comment

## Using Layouts with Frames

Layouts work seamlessly with frames to create complex UIs:

```mono
// Import the layout and frame
{{ '@/layouts/dashboard-layout.mono' }}
{{ '@/frames/sidebar-frame.mono' }}

component MyDashboard {
    function render() {
        // Create the component
        var dashboard = SwitchEnhanced.component.create({
            name: "MyDashboard"
        });
        
        // Create the layout
        var layout = SwitchEnhanced.layout.create({
            name: "DashboardLayout"
        });
        
        // Create the sidebar frame
        var sidebar = SwitchEnhanced.frame.create({
            name: "SidebarFrame",
            state: {
                title: "Navigation"
            }
        });
        
        // Apply the layout to the component
        dashboard.setLayout(layout);
        
        // Add the frame to the component
        dashboard.addFrame(sidebar);
        
        // Return the HTML
        return `
            <div class="dashboard">
                <div class="sidebar-container" data-frame="SidebarFrame">
                    <!-- Sidebar will be rendered here -->
                </div>
                
                <div class="dashboard-content">
                    <!-- Dashboard content -->
                </div>
            </div>
        `;
    }
}
```

## Best Practices

1. **Choose the Right Layout**: Select the layout that best fits your application's purpose
2. **Customize Variables**: Adjust layout variables to match your design
3. **Use Layout States**: Leverage states like `darkMode` for different appearances
4. **Combine with Frames**: Use frames within layouts for complex UIs
5. **Test Responsiveness**: Ensure your layout works well on all screen sizes
