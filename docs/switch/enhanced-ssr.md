# Enhanced Server-Side Rendering in Switch

The Switch framework now includes advanced server-side rendering (SSR) capabilities that improve performance, user experience, and developer productivity.

## Key Features

### Progressive Hydration

Progressive hydration allows you to hydrate components in order of importance, ensuring that critical UI elements become interactive first.

```mono
// Mark a component as critical
component.set_critical(true);

// Set the hydration strategy
component.set_hydration_strategy("eager");
```

### Selective Hydration

Selective hydration lets you choose which components to hydrate, reducing the JavaScript needed for initial interactivity.

```mono
// Enable selective hydration
renderer.enable_selective_hydration(true, ["header", "navigation", "search"]);
```

### Lazy Hydration

Lazy hydration defers the hydration of non-critical components until they're needed, improving initial load performance.

```mono
// Set a component to hydrate when visible
component.set_hydration_strategy("visible");

// Set a component to hydrate on interaction
component.set_hydration_strategy("interactive");
```

### Streaming SSR

Streaming SSR allows the server to send parts of the page as they're rendered, improving perceived performance.

```mono
// Enable streaming SSR
renderer.enable_streaming(true);
```

### Component Caching

Component caching reduces server load by caching rendered components.

```mono
// Enable component caching with a 60-second TTL
renderer.enable_caching(true, 60);
```

## Using Enhanced SSR

### Basic Setup

```mono
// Create an SSR renderer
var renderer = new SSRRenderer("My App");

// Enable enhanced features
renderer.enable_streaming(true);
renderer.enable_selective_hydration(true, ["critical-component"]);
renderer.enable_caching(true, 60);

// Create a component
var component = new MyComponent({
    title: "Hello, World!"
});

// Set hydration strategy
component.set_hydration_strategy("eager");
component.set_critical(true);

// Render the component
var html = renderer.render(component);
```

### With Layouts and Frames

Enhanced SSR works seamlessly with layouts and frames:

```mono
// Create a component
var component = new MyComponent({
    title: "Hello, World!"
});

// Create a layout
var layout = new DashboardLayout();

// Create a frame
var frame = new SidebarFrame({
    title: "Navigation"
});

// Associate the layout and frame with the component
component.set_layout(layout);
component.set_frame(frame);

// Render the component
var html = renderer.render(component);
```

## Client-Side Hydration

The enhanced hydration system on the client automatically handles different hydration strategies:

```html
<!-- Include the enhanced hydration script -->
<script src="/switch/enhanced-hydration.js"></script>

<!-- Hydration happens automatically -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        if (window.SwitchEnhanced && window.SwitchEnhanced.hydration) {
            SwitchEnhanced.hydration.hydrateRoot(
                document.getElementById('switch-root'),
                window.SWITCH_INITIAL_DATA,
                window.SWITCH_HYDRATION_CONFIG
            );
        }
    });
</script>
```

## Performance Benefits

Enhanced SSR provides several performance benefits:

1. **Faster Time to Interactive**: Critical components become interactive sooner
2. **Reduced JavaScript Load**: Only necessary components are hydrated
3. **Improved Perceived Performance**: Content appears faster with streaming
4. **Better Resource Utilization**: Component caching reduces server load
5. **Optimized for Mobile**: Lazy hydration reduces CPU usage on mobile devices

## Best Practices

1. **Identify Critical Components**: Mark components that users interact with immediately as critical
2. **Use Appropriate Hydration Strategies**: Choose the right strategy for each component
3. **Enable Caching for Static Components**: Cache components that don't change frequently
4. **Test on Low-End Devices**: Ensure good performance on mobile and low-end devices
5. **Monitor Performance**: Track metrics like Time to Interactive and First Contentful Paint

## Example: Dashboard with Enhanced SSR

```mono
component Dashboard {
    props {
        title: string = "Dashboard"
    }
    
    function render() {
        // Create the component with SSR support
        var dashboard = SwitchEnhanced.component.create({
            name: "Dashboard",
            props: this.props,
            hydrationStrategy: "eager",
            critical: true
        });
        
        // Create the layout
        var layout = SwitchEnhanced.layout.create({
            name: "DashboardLayout"
        });
        
        // Apply the layout to the component
        dashboard.setLayout(layout);
        
        // Return the HTML
        return `
            <div class="dashboard">
                <div class="dashboard-header">
                    <h1>${this.props.title}</h1>
                </div>
                
                <div class="dashboard-content">
                    <!-- Dashboard content -->
                </div>
            </div>
        `;
    }
}
```

## Conclusion

Enhanced SSR in the Switch framework provides a powerful set of tools for building high-performance web applications. By using progressive hydration, selective hydration, lazy hydration, streaming, and component caching, you can create applications that load quickly and provide a great user experience on all devices.
