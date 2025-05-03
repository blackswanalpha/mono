# Thread Management Best Practices in Mono

This case study explores best practices for managing threads in Mono applications. We'll cover common patterns, pitfalls to avoid, and techniques for building efficient concurrent applications.

## Introduction

Mono's concurrency model is designed to make parallel programming safer and more accessible. It provides several primitives for concurrent programming:

- **Component Threads**: Lightweight threads for components
- **Parallel Execution**: The `parallel` keyword for running code in parallel
- **Channels**: For safe communication between threads
- **Mutexes**: For protecting shared resources
- **Thread Pools**: For efficient thread management

However, with great power comes great responsibility. Improper thread management can lead to:

- Race conditions
- Deadlocks
- Resource starvation
- Poor performance
- Memory leaks

This case study will help you avoid these issues and build robust concurrent applications.

## Case Study: Dashboard Application

Let's examine a real-world example: a dashboard application that displays real-time data from multiple sources. The application needs to:

1. Fetch data from multiple APIs concurrently
2. Process and transform the data
3. Update the UI with the processed data
4. Handle user interactions

### Initial Implementation

Here's an initial implementation of our dashboard application:

```mono
component Dashboard {
    state {
        stockData: any = null,
        weatherData: any = null,
        newsData: any = null,
        socialData: any = null,
        isLoading: boolean = true,
        error: string = null
    }
    
    function onMount(): void {
        // Fetch all data sequentially
        this.fetchStockData();
        this.fetchWeatherData();
        this.fetchNewsData();
        this.fetchSocialData();
    }
    
    function fetchStockData(): void {
        // Simulate API call
        sleep(2000);
        this.state.stockData = { symbol: "MONO", price: 123.45 };
    }
    
    function fetchWeatherData(): void {
        // Simulate API call
        sleep(1500);
        this.state.weatherData = { temp: 72, condition: "Sunny" };
    }
    
    function fetchNewsData(): void {
        // Simulate API call
        sleep(3000);
        this.state.newsData = [{ title: "Mono 1.0 Released" }];
    }
    
    function fetchSocialData(): void {
        // Simulate API call
        sleep(1000);
        this.state.socialData = { likes: 1000, shares: 500 };
        this.state.isLoading = false;
    }
    
    function render(): string {
        if (this.state.isLoading) {
            return "<div>Loading...</div>";
        }
        
        if (this.state.error) {
            return "<div>Error: " + this.state.error + "</div>";
        }
        
        return "<div class=\"dashboard\">" +
               "  <div class=\"widget stock\">" + JSON.stringify(this.state.stockData) + "</div>" +
               "  <div class=\"widget weather\">" + JSON.stringify(this.state.weatherData) + "</div>" +
               "  <div class=\"widget news\">" + JSON.stringify(this.state.newsData) + "</div>" +
               "  <div class=\"widget social\">" + JSON.stringify(this.state.socialData) + "</div>" +
               "</div>";
    }
}
```

### Problems with the Initial Implementation

This implementation has several issues:

1. **Sequential Fetching**: The data is fetched sequentially, which means the total loading time is the sum of all individual fetch times (7.5 seconds).
2. **Blocking UI**: The main thread is blocked during data fetching, making the UI unresponsive.
3. **All-or-Nothing Loading**: The UI shows a loading state until all data is fetched, even though some data might be available earlier.
4. **No Error Handling**: If one API call fails, the entire dashboard might fail.

### Improved Implementation with Proper Thread Management

Let's improve our implementation using Mono's concurrency features:

```mono
component Dashboard {
    state {
        stockData: any = null,
        weatherData: any = null,
        newsData: any = null,
        socialData: any = null,
        isLoading: boolean = true,
        loadingWidgets: any = {
            stock: true,
            weather: true,
            news: true,
            social: true
        },
        errors: any = {}
    }
    
    function constructor(): void {
        // Create channels for communication between threads
        this.stockChannel = new Channel();
        this.weatherChannel = new Channel();
        this.newsChannel = new Channel();
        this.socialChannel = new Channel();
    }
    
    function onMount(): void {
        // Fetch all data in parallel
        parallel {
            this.fetchStockData();
        }
        
        parallel {
            this.fetchWeatherData();
        }
        
        parallel {
            this.fetchNewsData();
        }
        
        parallel {
            this.fetchSocialData();
        }
        
        // Set up listeners for the channels
        this.setupChannelListeners();
    }
    
    function setupChannelListeners(): void {
        // Listen for stock data
        parallel {
            var result = this.stockChannel.receive();
            if (result.error) {
                this.handleError("stock", result.error);
            } else {
                this.handleStockData(result.data);
            }
        }
        
        // Listen for weather data
        parallel {
            var result = this.weatherChannel.receive();
            if (result.error) {
                this.handleError("weather", result.error);
            } else {
                this.handleWeatherData(result.data);
            }
        }
        
        // Listen for news data
        parallel {
            var result = this.newsChannel.receive();
            if (result.error) {
                this.handleError("news", result.error);
            } else {
                this.handleNewsData(result.data);
            }
        }
        
        // Listen for social data
        parallel {
            var result = this.socialChannel.receive();
            if (result.error) {
                this.handleError("social", result.error);
            } else {
                this.handleSocialData(result.data);
            }
        }
    }
    
    function fetchStockData(): void {
        try {
            // Simulate API call
            sleep(2000);
            var data = { symbol: "MONO", price: 123.45 };
            this.stockChannel.send({ data: data });
        } catch (error) {
            this.stockChannel.send({ error: error });
        }
    }
    
    function fetchWeatherData(): void {
        try {
            // Simulate API call
            sleep(1500);
            var data = { temp: 72, condition: "Sunny" };
            this.weatherChannel.send({ data: data });
        } catch (error) {
            this.weatherChannel.send({ error: error });
        }
    }
    
    function fetchNewsData(): void {
        try {
            // Simulate API call
            sleep(3000);
            var data = [{ title: "Mono 1.0 Released" }];
            this.newsChannel.send({ data: data });
        } catch (error) {
            this.newsChannel.send({ error: error });
        }
    }
    
    function fetchSocialData(): void {
        try {
            // Simulate API call
            sleep(1000);
            var data = { likes: 1000, shares: 500 };
            this.socialChannel.send({ data: data });
        } catch (error) {
            this.socialChannel.send({ error: error });
        }
    }
    
    function handleStockData(data: any): void {
        this.state.stockData = data;
        this.state.loadingWidgets.stock = false;
        this.checkLoading();
    }
    
    function handleWeatherData(data: any): void {
        this.state.weatherData = data;
        this.state.loadingWidgets.weather = false;
        this.checkLoading();
    }
    
    function handleNewsData(data: any): void {
        this.state.newsData = data;
        this.state.loadingWidgets.news = false;
        this.checkLoading();
    }
    
    function handleSocialData(data: any): void {
        this.state.socialData = data;
        this.state.loadingWidgets.social = false;
        this.checkLoading();
    }
    
    function handleError(widget: string, error: string): void {
        this.state.errors[widget] = error;
        this.state.loadingWidgets[widget] = false;
        this.checkLoading();
    }
    
    function checkLoading(): void {
        // Check if all widgets are loaded
        var isLoading = false;
        for (var widget in this.state.loadingWidgets) {
            if (this.state.loadingWidgets[widget]) {
                isLoading = true;
                break;
            }
        }
        
        this.state.isLoading = isLoading;
    }
    
    function render(): string {
        var html = "<div class=\"dashboard\">";
        
        // Stock widget
        html += "<div class=\"widget stock\">";
        if (this.state.loadingWidgets.stock) {
            html += "<div class=\"loading\">Loading stock data...</div>";
        } else if (this.state.errors.stock) {
            html += "<div class=\"error\">Error: " + this.state.errors.stock + "</div>";
        } else {
            html += "<div class=\"data\">" + JSON.stringify(this.state.stockData) + "</div>";
        }
        html += "</div>";
        
        // Weather widget
        html += "<div class=\"widget weather\">";
        if (this.state.loadingWidgets.weather) {
            html += "<div class=\"loading\">Loading weather data...</div>";
        } else if (this.state.errors.weather) {
            html += "<div class=\"error\">Error: " + this.state.errors.weather + "</div>";
        } else {
            html += "<div class=\"data\">" + JSON.stringify(this.state.weatherData) + "</div>";
        }
        html += "</div>";
        
        // News widget
        html += "<div class=\"widget news\">";
        if (this.state.loadingWidgets.news) {
            html += "<div class=\"loading\">Loading news data...</div>";
        } else if (this.state.errors.news) {
            html += "<div class=\"error\">Error: " + this.state.errors.news + "</div>";
        } else {
            html += "<div class=\"data\">" + JSON.stringify(this.state.newsData) + "</div>";
        }
        html += "</div>";
        
        // Social widget
        html += "<div class=\"widget social\">";
        if (this.state.loadingWidgets.social) {
            html += "<div class=\"loading\">Loading social data...</div>";
        } else if (this.state.errors.social) {
            html += "<div class=\"error\">Error: " + this.state.errors.social + "</div>";
        } else {
            html += "<div class=\"data\">" + JSON.stringify(this.state.socialData) + "</div>";
        }
        html += "</div>";
        
        html += "</div>";
        
        return html;
    }
    
    function onUnmount(): void {
        // Clean up channels
        this.stockChannel.close();
        this.weatherChannel.close();
        this.newsChannel.close();
        this.socialChannel.close();
    }
}
```

### Benefits of the Improved Implementation

The improved implementation offers several benefits:

1. **Parallel Fetching**: Data is fetched in parallel, reducing the total loading time to the duration of the longest fetch (3 seconds instead of 7.5 seconds).
2. **Non-Blocking UI**: The main thread remains responsive during data fetching.
3. **Progressive Loading**: Each widget shows its own loading state and updates independently as data becomes available.
4. **Robust Error Handling**: Errors in one widget don't affect the others.
5. **Proper Resource Cleanup**: Channels are closed when the component is unmounted.

## Best Practices for Thread Management

Based on our case study, here are some best practices for thread management in Mono:

### 1. Use Parallel Execution for Independent Tasks

Use the `parallel` keyword for tasks that can run independently:

```mono
// Good: Run tasks in parallel
parallel {
    this.fetchStockData();
}

parallel {
    this.fetchWeatherData();
}

// Bad: Run tasks sequentially
this.fetchStockData();
this.fetchWeatherData();
```

### 2. Use Channels for Thread Communication

Use channels for safe communication between threads:

```mono
// Good: Use channels for thread communication
this.channel = new Channel();

parallel {
    var result = this.doHeavyComputation();
    this.channel.send(result);
}

var result = this.channel.receive();
this.updateUI(result);

// Bad: Use shared state without synchronization
parallel {
    this.state.result = this.doHeavyComputation();
}

this.updateUI(this.state.result);
```

### 3. Handle Errors in Each Thread

Handle errors within each thread to prevent them from crashing the entire application:

```mono
// Good: Handle errors within the thread
parallel {
    try {
        var result = this.doHeavyComputation();
        this.channel.send({ data: result });
    } catch (error) {
        this.channel.send({ error: error });
    }
}

// Bad: Let errors propagate
parallel {
    var result = this.doHeavyComputation();
    this.channel.send(result);
}
```

### 4. Clean Up Resources

Always clean up resources when they're no longer needed:

```mono
// Good: Clean up resources
function onUnmount(): void {
    this.channel.close();
}

// Bad: Leave resources open
function onUnmount(): void {
    // No cleanup
}
```

### 5. Use Thread Pools for Many Small Tasks

Use thread pools for many small tasks to avoid creating too many threads:

```mono
// Good: Use a thread pool
var pool = new ThreadPool(5);

for (var i = 0; i < 100; i++) {
    pool.submit(function() {
        this.processItem(i);
    });
}

// Bad: Create a new thread for each task
for (var i = 0; i < 100; i++) {
    parallel {
        this.processItem(i);
    }
}
```

### 6. Avoid Shared Mutable State

Avoid shared mutable state between threads, or use mutexes to protect it:

```mono
// Good: Use a mutex to protect shared state
this.mutex = new Mutex();

parallel {
    this.mutex.lock();
    this.sharedCounter++;
    this.mutex.unlock();
}

// Better: Use message passing instead of shared state
this.channel = new Channel();

parallel {
    this.channel.send(1);
}

var value = this.channel.receive();
this.counter += value;

// Bad: Access shared state without synchronization
parallel {
    this.sharedCounter++;
}
```

### 7. Prefer Immutable Data Structures

Use immutable data structures when possible:

```mono
// Good: Use immutable data structures
var immutableList = [1, 2, 3];

parallel {
    var newList = immutableList.concat([4]);
    this.channel.send(newList);
}

// Bad: Modify shared data structures
parallel {
    this.mutableList.push(4);
}
```

### 8. Use Timeouts for Operations That Might Block

Use timeouts to prevent operations from blocking indefinitely:

```mono
// Good: Use timeouts
try {
    var result = this.channel.receive(5000); // 5-second timeout
    this.handleResult(result);
} catch (error) {
    this.handleTimeout();
}

// Bad: Wait indefinitely
var result = this.channel.receive();
this.handleResult(result);
```

### 9. Limit the Number of Concurrent Threads

Limit the number of concurrent threads to avoid overwhelming the system:

```mono
// Good: Limit the number of concurrent threads
var semaphore = new Semaphore(5);

for (var i = 0; i < 100; i++) {
    parallel {
        semaphore.acquire();
        this.processItem(i);
        semaphore.release();
    }
}

// Bad: Create unlimited threads
for (var i = 0; i < 100; i++) {
    parallel {
        this.processItem(i);
    }
}
```

### 10. Monitor Thread Performance

Monitor thread performance to identify bottlenecks:

```mono
// Good: Monitor thread performance
var startTime = Date.now();

parallel {
    this.doHeavyComputation();
    var endTime = Date.now();
    print "Computation took " + (endTime - startTime) + "ms";
}

// Bad: No performance monitoring
parallel {
    this.doHeavyComputation();
}
```

## Conclusion

Proper thread management is essential for building efficient and robust concurrent applications in Mono. By following these best practices, you can avoid common pitfalls and take full advantage of Mono's concurrency features.

Remember:
- Use parallel execution for independent tasks
- Use channels for thread communication
- Handle errors in each thread
- Clean up resources
- Use thread pools for many small tasks
- Avoid shared mutable state
- Prefer immutable data structures
- Use timeouts for operations that might block
- Limit the number of concurrent threads
- Monitor thread performance

With these practices in mind, you'll be well-equipped to build high-performance concurrent applications in Mono.
