// Error handling system for Mono Editor
// This script provides robust error handling and recovery mechanisms

class ErrorHandler {
  constructor() {
    this.errors = [];
    this.maxErrors = 50; // Maximum number of errors to store
    this.initialized = false;
    this.recoveryStrategies = new Map();

    // Initialize error handling
    this.initialize();
  }

  /**
   * Initialize error handling
   */
  initialize() {
    if (this.initialized) return;

    console.log('Initializing error handling system...');

    // Set up global error handlers
    this.setupGlobalHandlers();

    // Set up component-specific error handlers
    this.setupComponentHandlers();

    // Register recovery strategies
    this.registerRecoveryStrategies();

    this.initialized = true;
  }

  /**
   * Set up global error handlers
   */
  setupGlobalHandlers() {
    // Handle uncaught exceptions
    window.addEventListener('error', (event) => {
      this.handleError({
        type: 'uncaught',
        message: event.message,
        source: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error,
        timestamp: new Date()
      });

      // Prevent default browser error handling
      event.preventDefault();
    });

    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError({
        type: 'unhandledrejection',
        message: event.reason?.message || 'Unhandled Promise rejection',
        error: event.reason,
        timestamp: new Date()
      });

      // Prevent default browser error handling
      event.preventDefault();
    });

    // Override console.error to capture errors
    const originalConsoleError = console.error;
    console.error = (...args) => {
      // Call the original console.error
      originalConsoleError.apply(console, args);

      // Prevent recursive error handling
      if (this._handlingConsoleError) {
        return;
      }

      try {
        this._handlingConsoleError = true;

        // Extract error information
        const errorMessage = args.map(arg => {
          try {
            return typeof arg === 'object' ? JSON.stringify(arg) : String(arg);
          } catch (e) {
            return '[Object conversion error]';
          }
        }).join(' ');

        // Handle the error
        this.handleError({
          type: 'console.error',
          message: errorMessage,
          timestamp: new Date()
        });
      } finally {
        this._handlingConsoleError = false;
      }
    };
  }

  /**
   * Set up component-specific error handlers
   */
  setupComponentHandlers() {
    // Monaco Editor error handling
    window.addEventListener('monaco-ready', () => {
      if (window.monaco) {
        // Handle Monaco Editor errors
        window.monaco.editor.onDidCreateEditor((editor) => {
          editor.onDidChangeModelContent((e) => {
            try {
              // Check for syntax errors in the editor
              const model = editor.getModel();
              if (model) {
                const markers = window.monaco.editor.getModelMarkers({ resource: model.uri });
                if (markers.length > 0) {
                  // Only log severe errors
                  const severeMarkers = markers.filter(marker => marker.severity === window.monaco.MarkerSeverity.Error);
                  if (severeMarkers.length > 0) {
                    this.logWarning('Monaco Editor', `${severeMarkers.length} syntax errors detected`);
                  }
                }
              }
            } catch (error) {
              // Don't handle errors in the error handler to avoid infinite loops
              console.warn('Error in Monaco error handler:', error);
            }
          });
        });
      }
    });
  }

  /**
   * Register recovery strategies for different error types
   */
  registerRecoveryStrategies() {
    // Monaco Editor loading failure
    this.recoveryStrategies.set('monaco-load-error', async () => {
      console.log('Attempting to recover from Monaco loading failure...');

      // Try to reload Monaco
      if (window.monacoLoader) {
        try {
          await window.monacoLoader.load();
          return true;
        } catch (error) {
          console.error('Recovery failed:', error);
          return false;
        }
      }

      return false;
    });

    // File operation errors
    this.recoveryStrategies.set('file-operation-error', async (error) => {
      console.log('Attempting to recover from file operation error:', error.message);

      // Show error message to user
      this.showUserErrorMessage('File Operation Error',
        'There was an error performing a file operation. Please try again.');

      return true; // Consider it recovered after showing the message
    });

    // API connection errors
    this.recoveryStrategies.set('api-connection-error', async () => {
      console.log('Attempting to recover from API connection error...');

      // Try to reconnect to the API
      if (window.api && window.api.testApi) {
        try {
          const result = await window.api.testApi();
          return result.success;
        } catch (error) {
          console.error('API reconnection failed:', error);
          return false;
        }
      }

      return false;
    });

    // Terminal errors
    this.recoveryStrategies.set('terminal-error', async (error) => {
      console.log('Attempting to recover from terminal error:', error.message);

      // Try to restart the terminal
      if (window.terminalManager) {
        try {
          // Get the active terminal ID
          const activeTerminalId = window.terminalManager.activeTerminal;

          if (activeTerminalId) {
            // Close the problematic terminal
            window.terminalManager.closeTerminal(activeTerminalId);

            // Create a new terminal
            const newTerminalId = window.terminalManager.createTerminal();

            // Activate the new terminal
            window.terminalManager.activateTerminal(newTerminalId);

            this.showUserErrorMessage('Terminal Restarted',
              'The terminal encountered an error and has been restarted.');

            return true;
          }
        } catch (recoveryError) {
          console.error('Terminal recovery failed:', recoveryError);
        }
      }

      return false;
    });

    // Memory issues
    this.recoveryStrategies.set('memory-error', async () => {
      console.log('Attempting to recover from memory issues...');

      try {
        // Clear Monaco model cache
        if (window.monaco && window.monaco.editor) {
          const models = window.monaco.editor.getModels();
          models.forEach(model => {
            // Only dispose models that are not currently visible
            const isVisible = Object.values(window.editorManager.editors)
              .some(editor => editor.model === model);

            if (!isVisible) {
              model.dispose();
            }
          });
        }

        // Run garbage collection if available
        if (window.gc) {
          window.gc();
        }

        // Clear performance data
        if (window.performanceMonitor) {
          window.performanceMonitor.metrics.resourceLoadTimes = {};
        }

        this.showUserErrorMessage('Memory Optimized',
          'The application was running low on memory. Some unused resources have been cleared.');

        return true;
      } catch (error) {
        console.error('Memory recovery failed:', error);
        return false;
      }
    });

    // UI rendering errors
    this.recoveryStrategies.set('ui-render-error', async () => {
      console.log('Attempting to recover from UI rendering error...');

      try {
        // Refresh the problematic UI components

        // Refresh editor if available
        if (window.editorManager && window.editorManager.activeEditor) {
          const editor = window.editorManager.editors[window.editorManager.activeEditor].editor;
          if (editor) {
            editor.layout();
          }
        }

        // Refresh terminal if available
        if (window.terminalManager && window.terminalManager.activeTerminal) {
          const terminal = window.terminalManager.terminals[window.terminalManager.activeTerminal];
          if (terminal && terminal.fitAddon) {
            terminal.fitAddon.fit();
          }
        }

        // Refresh file explorer if available
        if (window.explorerManager && typeof window.explorerManager.refreshExplorer === 'function') {
          window.explorerManager.refreshExplorer();
        }

        return true;
      } catch (error) {
        console.error('UI recovery failed:', error);
        return false;
      }
    });

    // Network errors
    this.recoveryStrategies.set('network-error', async (error) => {
      console.log('Attempting to recover from network error:', error.message);

      // Show a message to the user
      this.showUserErrorMessage('Network Error',
        'There was a problem with the network connection. Please check your internet connection and try again.');

      // Set a flag to retry network operations
      window.retryNetworkOperations = true;

      return true;
    });
  }

  /**
   * Handle an error
   * @param {Object} errorInfo - Information about the error
   */
  handleError(errorInfo) {
    // Prevent recursive error handling
    if (this._handlingError) {
      console.warn('Preventing recursive error handling');
      return;
    }

    try {
      this._handlingError = true;

      // Add error to the list
      this.errors.push(errorInfo);

      // Trim the error list if it gets too long
      if (this.errors.length > this.maxErrors) {
        this.errors.shift();
      }

      // Log the error
      this.logError(errorInfo);

      // Attempt recovery based on error type
      this.attemptRecovery(errorInfo);
    } catch (e) {
      // If an error occurs during error handling, log it directly without recursion
      console.warn('Error in error handler:', e);
    } finally {
      this._handlingError = false;
    }
  }

  /**
   * Log an error
   * @param {Object} errorInfo - Information about the error
   */
  logError(errorInfo) {
    try {
      // Safely extract timestamp
      let timestamp = 'unknown';
      try {
        if (errorInfo.timestamp && typeof errorInfo.timestamp.toISOString === 'function') {
          timestamp = errorInfo.timestamp.toISOString();
        } else if (errorInfo.timestamp) {
          timestamp = String(errorInfo.timestamp);
        }
      } catch (e) {
        timestamp = 'invalid-timestamp';
      }

      // Safely extract source and location
      const source = errorInfo.source ? ` in ${errorInfo.source}` : '';
      const location = errorInfo.lineno ? ` at line ${errorInfo.lineno}:${errorInfo.colno || 0}` : '';

      // Log with safe error grouping
      try {
        console.group(`[ERROR] ${timestamp}${source}${location}`);
      } catch (e) {
        // Fallback if grouping fails
        console.error(`[ERROR] ${timestamp}${source}${location}`);
      }

      // Log message
      if (errorInfo.message) {
        console.error(errorInfo.message);
      }

      // Log stack trace if available
      if (errorInfo.error && errorInfo.error.stack) {
        console.error(errorInfo.error.stack);
      }

      // Close group if opened
      try {
        console.groupEnd();
      } catch (e) {
        // Ignore if groupEnd fails
      }
    } catch (e) {
      // Last resort fallback
      console.error('Error in logError:', e);
      console.error('Original error:', errorInfo);
    }
  }

  /**
   * Log a warning
   * @param {string} source - Source of the warning
   * @param {string} message - Warning message
   */
  logWarning(source, message) {
    console.warn(`[WARNING] [${source}] ${message}`);
  }

  /**
   * Attempt to recover from an error
   * @param {Object} errorInfo - Information about the error
   */
  async attemptRecovery(errorInfo) {
    // Prevent recursive recovery attempts
    if (this._attemptingRecovery) {
      console.warn('Already attempting recovery, skipping');
      return;
    }

    try {
      this._attemptingRecovery = true;

      // Determine error type
      let errorType = errorInfo.type || 'unknown';

      // Check for specific error patterns in message
      try {
        if (errorInfo.message && typeof errorInfo.message === 'string') {
          const message = errorInfo.message.toLowerCase();

          // Monaco Editor errors
          if (message.includes('monaco') || (message.includes('editor') && message.includes('load'))) {
            errorType = 'monaco-load-error';
          }
          // File operation errors
          else if (message.includes('file') || message.includes('fs') || message.includes('permission denied') ||
                  message.includes('no such file') || message.includes('enoent')) {
            errorType = 'file-operation-error';
          }
          // API connection errors
          else if (message.includes('api') || message.includes('connection') || message.includes('fetch') ||
                  message.includes('xhr') || message.includes('http')) {
            errorType = 'api-connection-error';
          }
          // Terminal errors
          else if (message.includes('terminal') || message.includes('pty') || message.includes('process') ||
                  message.includes('spawn') || message.includes('exec')) {
            errorType = 'terminal-error';
          }
          // Memory errors
          else if (message.includes('memory') || message.includes('allocation') || message.includes('heap') ||
                  message.includes('out of memory') || message.includes('stack')) {
            errorType = 'memory-error';
          }
          // UI rendering errors
          else if (message.includes('render') || message.includes('dom') || message.includes('element') ||
                  message.includes('layout') || message.includes('style') || message.includes('css')) {
            errorType = 'ui-render-error';
          }
          // Network errors
          else if (message.includes('network') || message.includes('offline') || message.includes('internet') ||
                  message.includes('connection') || message.includes('timeout')) {
            errorType = 'network-error';
          }
        }
      } catch (e) {
        console.warn('Error analyzing error message:', e);
      }

      // Check error stack for additional clues
      try {
        if (errorInfo.error && errorInfo.error.stack && typeof errorInfo.error.stack === 'string') {
          const stack = errorInfo.error.stack.toLowerCase();

          // Look for specific components in the stack trace
          if (stack.includes('monaco') || stack.includes('editor.main.js')) {
            errorType = 'monaco-load-error';
          } else if (stack.includes('terminal') || stack.includes('xterm')) {
            errorType = 'terminal-error';
          } else if (stack.includes('explorer') || stack.includes('file')) {
            errorType = 'file-operation-error';
          }
        }
      } catch (e) {
        console.warn('Error analyzing error stack:', e);
      }

      // Get recovery strategy
      const recoveryStrategy = this.recoveryStrategies.get(errorType);

      if (recoveryStrategy) {
        console.log(`Attempting recovery for error type: ${errorType}`);

        try {
          // Set a timeout to prevent hanging recovery attempts
          const recoveryPromise = recoveryStrategy(errorInfo);
          const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Recovery timeout')), 5000);
          });

          const recovered = await Promise.race([recoveryPromise, timeoutPromise]);

          if (recovered) {
            console.log(`Successfully recovered from ${errorType}`);

            // Record successful recovery
            this.recordRecovery(errorType, true);
          } else {
            console.error(`Failed to recover from ${errorType}`);

            // Record failed recovery
            this.recordRecovery(errorType, false);

            // Show error message to user
            this.showUserErrorMessage('Error Recovery Failed',
              'The application encountered an error and was unable to recover automatically. You may need to reload the page.');
          }
        } catch (recoveryError) {
          console.error('Error during recovery attempt:', recoveryError);

          // Record failed recovery
          this.recordRecovery(errorType, false, recoveryError);
        }
      } else {
        // No specific recovery strategy, show generic error message for significant errors
        // Skip showing messages for resource loading errors to avoid overwhelming the user
        if (errorType !== 'unknown' && !errorInfo.message?.includes('Failed to load resource')) {
          this.showUserErrorMessage('Application Error',
            'The application encountered an unexpected error. Some features may not work correctly.');
        }
      }
    } catch (e) {
      console.error('Critical error in recovery system:', e);
    } finally {
      this._attemptingRecovery = false;
    }
  }

  /**
   * Record a recovery attempt
   * @param {string} errorType - The type of error
   * @param {boolean} successful - Whether the recovery was successful
   * @param {Error} [error] - The error that occurred during recovery, if any
   */
  recordRecovery(errorType, successful, error = null) {
    // Create recovery record
    const recoveryRecord = {
      errorType,
      successful,
      timestamp: new Date(),
      error: error ? {
        message: error.message,
        stack: error.stack
      } : null
    };

    // Store recovery record
    if (!this.recoveryAttempts) {
      this.recoveryAttempts = [];
    }

    this.recoveryAttempts.push(recoveryRecord);

    // Limit the number of records
    if (this.recoveryAttempts.length > 50) {
      this.recoveryAttempts.shift();
    }

    // Update recovery statistics
    this.updateRecoveryStats(errorType, successful);
  }

  /**
   * Update recovery statistics
   * @param {string} errorType - The type of error
   * @param {boolean} successful - Whether the recovery was successful
   */
  updateRecoveryStats(errorType, successful) {
    // Initialize recovery stats if needed
    if (!this.recoveryStats) {
      this.recoveryStats = new Map();
    }

    // Get or create stats for this error type
    let stats = this.recoveryStats.get(errorType);
    if (!stats) {
      stats = {
        attempts: 0,
        successes: 0,
        failures: 0,
        successRate: 0
      };
      this.recoveryStats.set(errorType, stats);
    }

    // Update stats
    stats.attempts++;
    if (successful) {
      stats.successes++;
    } else {
      stats.failures++;
    }

    // Calculate success rate
    stats.successRate = stats.successes / stats.attempts;
  }

  /**
   * Show an error message to the user
   * @param {string} title - Error title
   * @param {string} message - Error message
   */
  showUserErrorMessage(title, message) {
    // Prevent showing too many error messages
    if (this._showingErrorMessage) {
      console.warn('Already showing an error message, skipping');
      return;
    }

    try {
      this._showingErrorMessage = true;

      // Ensure we have valid strings
      const safeTitle = String(title || 'Error');
      const safeMessage = String(message || 'An unknown error occurred');

      // Check if we have a UI error display mechanism
      if (window.MonoJQueryUtils && typeof window.MonoJQueryUtils.showError === 'function') {
        try {
          window.MonoJQueryUtils.showError(safeTitle, { message: safeMessage }, true);
        } catch (e) {
          console.warn('Error using MonoJQueryUtils.showError:', e);
          // Fall through to next method
        }
      }

      // Try Bootstrap modal
      if (window.$ && typeof window.$ === 'function') {
        try {
          const $errorModal = $('#error-modal');
          if ($errorModal.length) {
            $('#error-modal-title').text(safeTitle);
            $('#error-modal-body').text(safeMessage);

            // Check which Bootstrap version is being used
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
              // Bootstrap 5
              const modalElement = document.getElementById('error-modal');
              if (modalElement) {
                const modalInstance = new bootstrap.Modal(modalElement);
                modalInstance.show();
                return; // Successfully shown
              }
            } else if (typeof $.fn.modal === 'function') {
              // Bootstrap 4 or 3
              $errorModal.modal('show');
              return; // Successfully shown
            }
          }
        } catch (e) {
          console.warn('Error showing Bootstrap modal:', e);
          // Fall through to alert
        }
      }

      // Fallback to alert, but only in extreme cases to avoid annoying the user
      // with too many alerts for minor issues like resource loading failures
      if (!safeMessage.includes('Failed to load resource')) {
        alert(`${safeTitle}: ${safeMessage}`);
      } else {
        // Just log to console for resource loading errors
        console.warn(`${safeTitle}: ${safeMessage}`);
      }
    } catch (e) {
      console.error('Error in showUserErrorMessage:', e);
    } finally {
      // Reset after a short delay to prevent message flooding
      setTimeout(() => {
        this._showingErrorMessage = false;
      }, 1000);
    }
  }

  /**
   * Get all recorded errors
   * @returns {Array} List of errors
   */
  getErrors() {
    return [...this.errors];
  }

  /**
   * Clear all recorded errors
   */
  clearErrors() {
    this.errors = [];
  }
}

// Create a singleton instance
const errorHandler = new ErrorHandler();

// Export the error handler
window.errorHandler = errorHandler;
