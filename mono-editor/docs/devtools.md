# Mono Editor DevTools

This document provides information about the DevTools feature in Mono Editor, which helps developers debug and troubleshoot issues.

## Overview

The DevTools integration in Mono Editor provides access to the Chromium Developer Tools, allowing you to:

- View console logs, warnings, and errors
- Inspect the DOM structure
- Debug JavaScript code
- Monitor network requests
- Analyze performance

## How to Access DevTools

There are several ways to open DevTools in Mono Editor:

1. **Keyboard Shortcut**:
   - Press `F12` to toggle DevTools

2. **Menu**:
   - Go to `View` > `Toggle Developer Tools`

3. **Status Bar**:
   - Click the DevTools button (🔍) in the status bar

## Console Utilities

Mono Editor includes a simple console utility that provides enhanced logging capabilities. This utility is available as a global `monoConsole` object in the renderer process.

### Basic Usage

```javascript
// Log an informational message
monoConsole.log('This is a log message');

// Log an informational message
monoConsole.info('This is an informational message');

// Log a success message
monoConsole.success('Operation completed successfully');

// Log a warning
monoConsole.warn('This is a warning');

// Log an error
monoConsole.error('An error occurred');
```

## Debugging Tips

1. **Console Filters**:
   - Use the dropdown in the console to filter by log level (errors, warnings, etc.)
   - Use the search box to filter logs by content

2. **Breakpoints**:
   - Set breakpoints in your code by clicking on line numbers in the Sources panel
   - Use conditional breakpoints for more complex debugging scenarios

3. **Network Monitoring**:
   - Use the Network tab to monitor API calls and resource loading
   - Filter requests by type (XHR, JS, CSS, etc.)

4. **Performance Analysis**:
   - Use the Performance tab to record and analyze performance issues
   - Look for long tasks and rendering bottlenecks

## Troubleshooting Common Issues

### DevTools Not Opening

If DevTools doesn't open when using the keyboard shortcut or menu option:

1. Check if there are any error messages in the terminal where Mono Editor was launched
2. Try restarting Mono Editor
3. Check if DevTools is already open but in a detached window

### Console Errors

Common console errors and their solutions:

1. **CORS Errors**:
   - These occur when making cross-origin requests
   - Check the server's CORS configuration

2. **Uncaught Exceptions**:
   - Look for the stack trace to identify where the error occurred
   - Check for typos or undefined variables

3. **Failed to Load Resource**:
   - Verify that the resource path is correct
   - Check network connectivity

## Further Reading

- [Chrome DevTools Documentation](https://developers.google.com/web/tools/chrome-devtools)
- [Electron Documentation](https://www.electronjs.org/docs)
- [JavaScript Debugging Techniques](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors)
