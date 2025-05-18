// Performance monitoring for Mono Editor
// This script helps track and optimize performance

class PerformanceMonitor {
  constructor() {
    this.metrics = {
      startTime: performance.now(),
      loadEvents: [],
      componentInitTimes: {},
      resourceLoadTimes: {}
    };

    this.initialized = false;
    this.initializeMonitoring();
  }

  /**
   * Initialize performance monitoring
   */
  initializeMonitoring() {
    if (this.initialized) return;

    console.log('Initializing performance monitoring...');

    // Track page load events
    this.trackLoadEvents();

    // Monitor resource loading
    this.monitorResourceLoading();

    // Track component initialization
    this.trackComponentInit();

    this.initialized = true;
  }

  /**
   * Track page load events
   */
  trackLoadEvents() {
    // Record DOMContentLoaded time
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        this.recordEvent('DOMContentLoaded');
      });
    } else {
      this.recordEvent('DOMContentLoaded (already fired)');
    }

    // Record load time
    window.addEventListener('load', () => {
      this.recordEvent('window.load');

      // Report initial metrics after a short delay
      setTimeout(() => {
        this.reportMetrics();
      }, 1000);
    });
  }

  /**
   * Monitor resource loading
   */
  monitorResourceLoading() {
    // Use Performance Observer to monitor resource loading
    if (window.PerformanceObserver) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach(entry => {
          if (entry.entryType === 'resource') {
            try {
              // Safely set the property using the metrics object
              this.metrics.resourceLoadTimes[entry.name] = {
                duration: entry.duration,
                size: entry.transferSize || 'unknown',
                type: entry.initiatorType
              };
            } catch (error) {
              console.warn('Error recording resource timing:', error);
            }
          }
        });
      });

      try {
        observer.observe({ entryTypes: ['resource'] });
      } catch (error) {
        console.warn('Error observing resource timing:', error);
      }
    }
  }

  /**
   * Track component initialization
   */
  trackComponentInit() {
    // Create proxies for key component initializations
    window.addEventListener('monaco-ready', () => {
      this.recordComponentInit('Monaco Editor');
    });

    // Track other components as they initialize
    const originalEditorManager = window.EditorManager;
    if (originalEditorManager) {
      window.EditorManager = function(...args) {
        const instance = new originalEditorManager(...args);
        performanceMonitor.recordComponentInit('EditorManager');
        return instance;
      };
    }
  }

  /**
   * Record a load event
   * @param {string} eventName - Name of the event
   */
  recordEvent(eventName) {
    const time = performance.now();
    const timeFromStart = time - this.metrics.startTime;

    this.metrics.loadEvents.push({
      name: eventName,
      time: time,
      timeFromStart: timeFromStart
    });

    console.log(`Performance: ${eventName} at ${timeFromStart.toFixed(2)}ms`);
  }

  /**
   * Record component initialization
   * @param {string} componentName - Name of the component
   */
  recordComponentInit(componentName) {
    const time = performance.now();
    const timeFromStart = time - this.metrics.startTime;

    this.metrics.componentInitTimes[componentName] = {
      time: time,
      timeFromStart: timeFromStart
    };

    console.log(`Performance: ${componentName} initialized at ${timeFromStart.toFixed(2)}ms`);
  }

  /**
   * Report performance metrics
   */
  reportMetrics() {
    console.group('Mono Editor Performance Metrics');

    // Report load events
    console.log('Load Events:');
    this.metrics.loadEvents.forEach(event => {
      console.log(`  ${event.name}: ${event.timeFromStart.toFixed(2)}ms`);
    });

    // Report component initialization times
    console.log('Component Initialization:');
    Object.entries(this.metrics.componentInitTimes).forEach(([component, timing]) => {
      console.log(`  ${component}: ${timing.timeFromStart.toFixed(2)}ms`);
    });

    // Report slow resource loads (over 500ms)
    console.log('Slow Resources (>500ms):');
    Object.entries(this.metrics.resourceLoadTimes)
      .filter(([_, timing]) => timing.duration > 500)
      .sort((a, b) => b[1].duration - a[1].duration)
      .forEach(([resource, timing]) => {
        console.log(`  ${resource.split('/').pop()}: ${timing.duration.toFixed(2)}ms (${timing.type})`);
      });

    console.groupEnd();
  }

  /**
   * Get optimization suggestions
   * @returns {Array<string>} List of optimization suggestions
   */
  getOptimizationSuggestions() {
    const suggestions = [];

    // Check for slow resource loads
    const slowResources = Object.entries(this.metrics.resourceLoadTimes)
      .filter(([_, timing]) => timing.duration > 1000);

    if (slowResources.length > 0) {
      suggestions.push(`Consider optimizing ${slowResources.length} slow resources`);

      // Check for large JS files
      const largeJsFiles = slowResources
        .filter(([resource, _]) => resource.endsWith('.js'))
        .map(([resource, _]) => resource.split('/').pop());

      if (largeJsFiles.length > 0) {
        suggestions.push(`Consider code splitting for large JS files: ${largeJsFiles.join(', ')}`);
      }
    }

    // Check for late component initialization
    const lateComponents = Object.entries(this.metrics.componentInitTimes)
      .filter(([_, timing]) => timing.timeFromStart > 2000)
      .map(([component, _]) => component);

    if (lateComponents.length > 0) {
      suggestions.push(`Optimize initialization of late components: ${lateComponents.join(', ')}`);
    }

    return suggestions;
  }
}

// Create a singleton instance
const performanceMonitor = new PerformanceMonitor();

// Export the monitor
window.performanceMonitor = performanceMonitor;
