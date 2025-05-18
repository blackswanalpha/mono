// Simple DevTools integration for Mono Editor

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
  // Add a small delay to ensure all APIs are loaded
  setTimeout(() => {
    initDevTools();
  }, 500);
});

// Initialize DevTools functionality
function initDevTools() {
  try {
    console.log('Initializing DevTools integration...');

    // Check if window.api is available
    if (!window.api) {
      console.error('API not available. DevTools initialization delayed.');
      // Try again after a delay
      setTimeout(initDevTools, 1000);
      return;
    }

    // Get the DevTools button
    const devToolsBtn = document.getElementById('toggle-devtools-btn');
    if (!devToolsBtn) {
      console.error('DevTools button not found in the DOM');
      return;
    }

    // Add click event listener to the button
    devToolsBtn.addEventListener('click', toggleDevTools);

    // Add keyboard shortcut (F12)
    document.addEventListener('keydown', (e) => {
      if (e.key === 'F12') {
        e.preventDefault();
        toggleDevTools();
      }
    });

    console.log('DevTools integration initialized');
  } catch (error) {
    console.error('Error initializing DevTools:', error);
  }
}

// Toggle DevTools
async function toggleDevTools() {
  console.log('Toggle DevTools requested');

  try {
    // Check if API is available
    if (!window.api || typeof window.api.toggleDevTools !== 'function') {
      console.error('DevTools API not available');
      showDevToolsError('DevTools API not available');
      return;
    }

    // Get the DevTools button
    const devToolsBtn = document.getElementById('toggle-devtools-btn');

    // Toggle DevTools through IPC
    const result = await window.api.toggleDevTools();
    console.log('DevTools toggle result:', result);

    // Update button state
    if (devToolsBtn) {
      if (result.isOpen) {
        devToolsBtn.classList.add('active');
        devToolsBtn.title = 'Close Developer Tools (F12)';
      } else {
        devToolsBtn.classList.remove('active');
        devToolsBtn.title = 'Open Developer Tools (F12)';
      }
    }
  } catch (error) {
    console.error('Error toggling DevTools:', error);
    showDevToolsError(`Error toggling DevTools: ${error.message}`);
  }
}

// Show DevTools error
function showDevToolsError(message) {
  // Try to show error in status bar if available
  try {
    const statusBar = document.querySelector('.status-left');
    if (statusBar) {
      const errorElement = document.createElement('span');
      errorElement.textContent = message;
      errorElement.style.color = '#F44336';
      errorElement.id = 'devtools-error';

      // Remove existing error if any
      const existingError = document.getElementById('devtools-error');
      if (existingError) {
        existingError.remove();
      }

      statusBar.appendChild(errorElement);

      // Remove after 5 seconds
      setTimeout(() => {
        if (errorElement.parentNode) {
          errorElement.remove();
        }
      }, 5000);
    }
  } catch (error) {
    console.error('Error showing DevTools error:', error);
  }
}

// Console utilities for better debugging
window.monoConsole = {
  log: (message, ...args) => {
    console.log(`%c[Mono] ${message}`, 'color: #2196F3; font-weight: bold;', ...args);
  },

  info: (message, ...args) => {
    console.info(`%c[Mono] ${message}`, 'color: #2196F3; font-weight: bold;', ...args);
  },

  warn: (message, ...args) => {
    console.warn(`%c[Mono] ${message}`, 'color: #FFC107; font-weight: bold;', ...args);
  },

  error: (message, ...args) => {
    console.error(`%c[Mono] ${message}`, 'color: #F44336; font-weight: bold;', ...args);
  },

  success: (message, ...args) => {
    console.log(`%c[Mono] ${message}`, 'color: #4CAF50; font-weight: bold;', ...args);
  }
};

// Log a welcome message that will be visible in DevTools
window.monoConsole.info('DevTools integration loaded');
window.monoConsole.info('Press F12 to toggle DevTools');
window.monoConsole.info('Use window.monoConsole for styled logging');
