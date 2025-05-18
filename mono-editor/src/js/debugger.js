// Debugger for Mono Editor

class MonoDebugger {
  constructor() {
    // Initialize after DOM is fully loaded
    this.initialize();
  }

  initialize() {
    // Debug UI elements
    this.variablesContainer = document.getElementById('debug-variables');
    this.callStackContainer = document.getElementById('debug-call-stack');
    this.breakpointsContainer = document.getElementById('debug-breakpoints');
    this.debugConsole = document.getElementById('debug-console');

    // Debug tabs
    this.debugTabs = document.querySelectorAll('.debug-tab');
    this.debugPanels = document.querySelectorAll('.debug-panel');

    // Debug action buttons
    this.startDebugBtn = document.getElementById('start-debug-btn');
    this.stopDebugBtn = document.getElementById('stop-debug-btn');
    this.continueDebugBtn = document.getElementById('continue-debug-btn');
    this.stepOverBtn = document.getElementById('step-over-btn');
    this.stepIntoBtn = document.getElementById('step-into-btn');
    this.stepOutBtn = document.getElementById('step-out-btn');

    // Debug state
    this.isDebugging = false;
    this.isPaused = false;
    this.breakpoints = new Map(); // Map of file paths to line numbers
    this.currentFile = null;
    this.currentLine = null;
    this.variables = [];
    this.callStack = [];
    this.debugProcessId = null;

    // Initialize event listeners
    this.initEventListeners();

    // Initialize debug tabs event listeners
    this.initDebugTabsEventListeners();

    // Listen for debug view activation
    document.addEventListener('debug-view-activated', () => {
      this.onDebugViewActivated();
    });

    console.log('Debugger initialized');
  }

  // Called when DOM is loaded
  onDOMContentLoaded() {
    this.initialize();
  }

  // Initialize debug tabs event listeners
  initDebugTabsEventListeners() {
    this.debugTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const panel = tab.getAttribute('data-panel');
        this.switchPanel(panel);
      });
    });
  }

  // Switch between debug panels (variables, call stack, breakpoints)
  switchPanel(panel) {
    // Update tabs
    this.debugTabs.forEach(tab => {
      if (tab.getAttribute('data-panel') === panel) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });

    // Update panels
    this.debugPanels.forEach(panelElement => {
      if (panelElement.getAttribute('data-panel') === panel) {
        panelElement.classList.add('active');
      } else {
        panelElement.classList.remove('active');
      }
    });
  }

  // Handle debug view activation
  onDebugViewActivated() {
    // Update UI based on current debug state
    this.updateDebugControls();

    // Refresh debug panels if debugging
    if (this.isDebugging) {
      this.refreshDebugPanels();
    }
  }

  initEventListeners() {
    // Debug control buttons
    this.startDebugBtn.addEventListener('click', () => {
      this.startDebugging();
    });

    this.stopDebugBtn.addEventListener('click', () => {
      this.stopDebugging();
    });

    this.continueDebugBtn.addEventListener('click', () => {
      this.continueExecution();
    });

    this.stepOverBtn.addEventListener('click', () => {
      this.stepOver();
    });

    this.stepIntoBtn.addEventListener('click', () => {
      this.stepInto();
    });

    this.stepOutBtn.addEventListener('click', () => {
      this.stepOut();
    });

    // Debug console input
    document.getElementById('debug-console-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.executeConsoleCommand();
      }
    });

    // Debug event listeners
    window.api.onDebugEvent((event) => {
      this.handleDebugEvent(event);
    });

    // Menu event listeners
    window.api.onMenuEvent('menu-debug-start', () => {
      this.startDebugging();
    });

    window.api.onMenuEvent('menu-debug-stop', () => {
      this.stopDebugging();
    });

    window.api.onMenuEvent('menu-debug-continue', () => {
      this.continueExecution();
    });

    window.api.onMenuEvent('menu-debug-step-over', () => {
      this.stepOver();
    });

    window.api.onMenuEvent('menu-debug-step-into', () => {
      this.stepInto();
    });

    window.api.onMenuEvent('menu-debug-step-out', () => {
      this.stepOut();
    });

    window.api.onMenuEvent('menu-debug-toggle-breakpoint', () => {
      if (editorManager && editorManager.activeEditor) {
        const editor = editorManager.editors[editorManager.activeEditor];
        if (editor && editor.editor) {
          const position = editor.editor.getPosition();
          this.toggleBreakpoint(editor.filePath, position.lineNumber);
        }
      }
    });
  }

  activateDebugPanel(panelId) {
    // Deactivate all tabs and panels
    const tabs = document.querySelectorAll('.debug-tab');
    tabs.forEach(tab => tab.classList.remove('active'));

    const panels = document.querySelectorAll('.debug-panel');
    panels.forEach(panel => panel.classList.remove('active'));

    // Activate the selected tab and panel
    const selectedTab = document.querySelector(`.debug-tab[data-panel="${panelId}"]`);
    if (selectedTab) {
      selectedTab.classList.add('active');
    }

    const selectedPanel = document.getElementById(`debug-${panelId}`);
    if (selectedPanel) {
      selectedPanel.classList.add('active');
    }
  }

  showDebugPanel() {
    // Switch to debug view in the terminal container
    if (terminalManager) {
      terminalManager.showDebugView();
    }
    this.updateDebugControls();
  }

  hideDebugPanel() {
    // Switch back to terminal view
    if (terminalManager) {
      terminalManager.showTerminalView();
    }
  }

  toggleDebugPanel() {
    if (terminalManager && terminalManager.activeView === 'debug') {
      this.hideDebugPanel();
    } else {
      this.showDebugPanel();
    }
  }

  // Refresh debug panels with current data
  refreshDebugPanels() {
    this.updateVariablesView();
    this.updateCallStackView();
    this.updateBreakpointsView();
  }

  // Update breakpoints view
  updateBreakpointsView() {
    // Clear current breakpoints
    this.breakpointsContainer.innerHTML = '';

    if (!this.breakpoints || this.breakpoints.size === 0) {
      const emptyMessage = document.createElement('div');
      emptyMessage.className = 'debug-empty-message';
      emptyMessage.textContent = 'No breakpoints';
      this.breakpointsContainer.appendChild(emptyMessage);
      return;
    }

    // Create breakpoints list
    const list = document.createElement('ul');
    list.className = 'debug-breakpoints-list';

    // Add breakpoints
    for (const [filePath, lines] of this.breakpoints.entries()) {
      const fileName = filePath.split('/').pop();

      lines.forEach(line => {
        const item = document.createElement('li');
        item.className = 'debug-breakpoint-item';

        item.innerHTML = `
          <span class="breakpoint-location">${fileName}:${line}</span>
          <button class="breakpoint-remove" title="Remove Breakpoint">×</button>
        `;

        // Add click handler to navigate to breakpoint
        item.querySelector('.breakpoint-location').addEventListener('click', () => {
          if (editorManager) {
            editorManager.openFile(filePath);
            editorManager.goToLine(line);
          }
        });

        // Add click handler to remove breakpoint
        item.querySelector('.breakpoint-remove').addEventListener('click', () => {
          this.toggleBreakpoint(filePath, line);
        });

        list.appendChild(item);
      });
    }

    this.breakpointsContainer.appendChild(list);
  }

  updateDebugControls() {
    // Update button states based on debugging state
    this.startDebugBtn.disabled = this.isDebugging;
    this.stopDebugBtn.disabled = !this.isDebugging;
    this.continueDebugBtn.disabled = !this.isPaused;
    this.stepOverBtn.disabled = !this.isPaused;
    this.stepIntoBtn.disabled = !this.isPaused;
    this.stepOutBtn.disabled = !this.isPaused;

    // Update menu items if available
    if (window.api && typeof window.api.updateMenuState === 'function') {
      window.api.updateMenuState('menu-debug-start', !this.isDebugging);
      window.api.updateMenuState('menu-debug-stop', this.isDebugging);
      window.api.updateMenuState('menu-debug-continue', this.isPaused);
      window.api.updateMenuState('menu-debug-step-over', this.isPaused);
      window.api.updateMenuState('menu-debug-step-into', this.isPaused);
      window.api.updateMenuState('menu-debug-step-out', this.isPaused);
    }
  }

  async startDebugging() {
    try {
      // Get the active file path
      if (!editorManager) {
        this.showError('No active editor');
        return;
      }

      const filePath = editorManager.getActiveFilePath();
      if (!filePath) {
        this.showError('No file is open');
        return;
      }

      // Check if file is a Mono file
      if (!filePath.endsWith('.mono')) {
        this.showError('Only Mono files can be debugged');
        return;
      }

      // Save the file if it has unsaved changes
      const activeEditor = editorManager.getActiveEditor();
      if (activeEditor && activeEditor.isDirty) {
        await editorManager.saveFile(editorManager.activeEditor);
      }

      // Show the debug panel
      this.showDebugPanel();

      // Clear previous debug state
      this.clearDebugState();

      // Set debugging state
      this.isDebugging = true;
      this.isPaused = false;
      this.currentFile = filePath;

      // Update UI
      this.updateDebugControls();
      this.logToConsole('Starting debug session...');

      // Clear the debug console
      this.debugConsole.innerHTML = '';
      this.logToConsole('Debug console initialized.');
      this.logToConsole(`Debugging ${filePath.split('/').pop()}`);

      // Start the debug process
      this.debugProcessId = await window.api.startDebugSession(filePath, Array.from(this.breakpoints.entries()));

      // Log success
      this.logToConsole(`Debug session started for ${filePath}`);

      // Update breakpoints view
      this.updateBreakpointsView();
    } catch (error) {
      console.error('Error starting debugging:', error);
      this.showError(`Error starting debugging: ${error.message}`);
      this.isDebugging = false;
      this.updateDebugControls();
    }
  }

  stopDebugging() {
    if (!this.isDebugging) return;

    try {
      // Stop the debug process
      if (this.debugProcessId) {
        window.api.stopDebugSession(this.debugProcessId);
      }

      // Reset state
      this.clearDebugState();

      // Log
      this.logToConsole('Debug session stopped');
    } catch (error) {
      console.error('Error stopping debugging:', error);
      this.showError(`Error stopping debugging: ${error.message}`);
    }
  }

  clearDebugState() {
    this.isDebugging = false;
    this.isPaused = false;
    this.debugProcessId = null;
    this.variables = [];
    this.callStack = [];
    this.currentLine = null;

    // Clear UI
    this.variablesContainer.innerHTML = '';
    this.callStackContainer.innerHTML = '';
    this.updateDebugControls();

    // Clear editor decorations
    if (editorManager) {
      editorManager.clearDebugDecorations();
    }
  }

  continueExecution() {
    if (!this.isDebugging || !this.isPaused || !this.debugProcessId) return;

    try {
      window.api.continueDebugSession(this.debugProcessId);
      this.isPaused = false;
      this.updateDebugControls();
      this.logToConsole('Continuing execution...');
    } catch (error) {
      console.error('Error continuing execution:', error);
      this.showError(`Error continuing execution: ${error.message}`);
    }
  }

  stepOver() {
    if (!this.isDebugging || !this.isPaused || !this.debugProcessId) return;

    try {
      window.api.stepOverDebugSession(this.debugProcessId);
      this.logToConsole('Stepping over...');
    } catch (error) {
      console.error('Error stepping over:', error);
      this.showError(`Error stepping over: ${error.message}`);
    }
  }

  stepInto() {
    if (!this.isDebugging || !this.isPaused || !this.debugProcessId) return;

    try {
      window.api.stepIntoDebugSession(this.debugProcessId);
      this.logToConsole('Stepping into...');
    } catch (error) {
      console.error('Error stepping into:', error);
      this.showError(`Error stepping into: ${error.message}`);
    }
  }

  stepOut() {
    if (!this.isDebugging || !this.isPaused || !this.debugProcessId) return;

    try {
      window.api.stepOutDebugSession(this.debugProcessId);
      this.logToConsole('Stepping out...');
    } catch (error) {
      console.error('Error stepping out:', error);
      this.showError(`Error stepping out: ${error.message}`);
    }
  }

  restartDebugging() {
    if (!this.isDebugging) return;

    try {
      // Stop current session
      if (this.debugProcessId) {
        window.api.stopDebugSession(this.debugProcessId);
      }

      // Start new session
      this.startDebugging();
    } catch (error) {
      console.error('Error restarting debugging:', error);
      this.showError(`Error restarting debugging: ${error.message}`);
    }
  }

  executeConsoleCommand() {
    const input = document.getElementById('debug-console-input');
    const command = input.value.trim();

    if (!command) return;

    // Log the command
    this.logToConsole(`> ${command}`, 'command');

    // Execute the command
    if (this.isDebugging && this.debugProcessId) {
      window.api.evaluateExpression(this.debugProcessId, command)
        .then(result => {
          this.logToConsole(result, 'result');
        })
        .catch(error => {
          this.logToConsole(`Error: ${error.message}`, 'error');
        });
    } else {
      this.logToConsole('Not debugging', 'error');
    }

    // Clear input
    input.value = '';
  }

  logToConsole(message, type = 'info') {
    const entry = document.createElement('div');
    entry.className = `debug-console-entry ${type}`;
    entry.textContent = message;
    this.debugConsole.appendChild(entry);

    // Scroll to bottom
    this.debugConsole.scrollTop = this.debugConsole.scrollHeight;
  }

  showError(message) {
    this.logToConsole(message, 'error');
  }

  handleDebugEvent(event) {
    switch (event.type) {
      case 'paused':
        this.handlePaused(event);
        break;
      case 'resumed':
        this.handleResumed(event);
        break;
      case 'terminated':
        this.handleTerminated(event);
        break;
      case 'output':
        this.handleOutput(event);
        break;
      case 'variables':
        this.handleVariables(event);
        break;
      case 'callStack':
        this.handleCallStack(event);
        break;
      default:
        console.log('Unknown debug event:', event);
    }
  }

  handlePaused(event) {
    this.isPaused = true;
    this.currentFile = event.filePath;
    this.currentLine = event.line;

    // Update UI
    this.updateDebugControls();
    this.logToConsole(`Paused at ${event.filePath}:${event.line}`);

    // Highlight current line in editor
    if (editorManager) {
      editorManager.openFile(event.filePath);
      editorManager.highlightDebugLine(event.filePath, event.line);
    }

    // Request variables and call stack
    if (this.debugProcessId) {
      window.api.getVariables(this.debugProcessId);
      window.api.getCallStack(this.debugProcessId);
    }
  }

  handleResumed(event) {
    this.isPaused = false;

    // Update UI
    this.updateDebugControls();
    this.logToConsole('Resumed execution');

    // Clear current line highlight
    if (editorManager) {
      editorManager.clearDebugDecorations();
    }
  }

  handleTerminated(event) {
    // Reset debugging state
    this.clearDebugState();

    // Log
    this.logToConsole('Debug session terminated');
  }

  handleOutput(event) {
    // Log output to console
    this.logToConsole(event.output, event.category || 'output');
  }

  handleVariables(event) {
    this.variables = event.variables;

    // Update variables view
    this.updateVariablesView();
  }

  handleCallStack(event) {
    this.callStack = event.callStack;

    // Update call stack view
    this.updateCallStackView();
  }

  updateVariablesView() {
    // Clear current variables
    this.variablesContainer.innerHTML = '';

    if (!this.variables || this.variables.length === 0) {
      const emptyMessage = document.createElement('div');
      emptyMessage.className = 'debug-empty-message';
      emptyMessage.textContent = 'No variables';
      this.variablesContainer.appendChild(emptyMessage);
      return;
    }

    // Create variables table
    const table = document.createElement('table');
    table.className = 'debug-variables-table';

    // Add header
    const header = document.createElement('tr');
    header.innerHTML = `
      <th>Name</th>
      <th>Value</th>
      <th>Type</th>
    `;
    table.appendChild(header);

    // Add variables
    this.variables.forEach(variable => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${variable.name}</td>
        <td>${variable.value}</td>
        <td>${variable.type}</td>
      `;
      table.appendChild(row);
    });

    this.variablesContainer.appendChild(table);
  }

  updateCallStackView() {
    // Clear current call stack
    this.callStackContainer.innerHTML = '';

    if (!this.callStack || this.callStack.length === 0) {
      const emptyMessage = document.createElement('div');
      emptyMessage.className = 'debug-empty-message';
      emptyMessage.textContent = 'No call stack';
      this.callStackContainer.appendChild(emptyMessage);
      return;
    }

    // Create call stack list
    const list = document.createElement('ul');
    list.className = 'debug-call-stack-list';

    // Add frames
    this.callStack.forEach((frame, index) => {
      const item = document.createElement('li');
      item.className = 'debug-call-stack-item';
      if (index === 0) {
        item.classList.add('active');
      }

      item.innerHTML = `
        <span class="frame-name">${frame.name}</span>
        <span class="frame-location">${frame.file}:${frame.line}</span>
      `;

      // Add click handler to navigate to frame
      item.addEventListener('click', () => {
        this.selectCallStackFrame(index);
      });

      list.appendChild(item);
    });

    this.callStackContainer.appendChild(list);
  }

  selectCallStackFrame(index) {
    if (!this.callStack || index >= this.callStack.length) return;

    const frame = this.callStack[index];

    // Highlight the selected frame
    const items = this.callStackContainer.querySelectorAll('.debug-call-stack-item');
    items.forEach((item, i) => {
      if (i === index) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Navigate to the frame location
    if (editorManager) {
      editorManager.openFile(frame.file);
      editorManager.highlightDebugLine(frame.file, frame.line);
    }

    // Request variables for this frame
    if (this.debugProcessId) {
      window.api.getVariablesForFrame(this.debugProcessId, index);
    }
  }

  toggleBreakpoint(filePath, line) {
    // Get breakpoints for this file
    let fileBreakpoints = this.breakpoints.get(filePath) || [];

    // Check if breakpoint already exists
    const index = fileBreakpoints.indexOf(line);

    if (index !== -1) {
      // Remove breakpoint
      fileBreakpoints.splice(index, 1);
    } else {
      // Add breakpoint
      fileBreakpoints.push(line);
    }

    // Update breakpoints map
    if (fileBreakpoints.length > 0) {
      this.breakpoints.set(filePath, fileBreakpoints);
    } else {
      this.breakpoints.delete(filePath);
    }

    // Update breakpoints in editor
    if (editorManager) {
      editorManager.updateBreakpoints(filePath, fileBreakpoints);
    }

    // Update breakpoints in debug session
    if (this.isDebugging && this.debugProcessId) {
      window.api.updateBreakpoints(this.debugProcessId, Array.from(this.breakpoints.entries()));
    }

    // Update breakpoints view
    this.updateBreakpointsView();
  }

  updateBreakpointsView() {
    // Clear current breakpoints
    this.breakpointsContainer.innerHTML = '';

    if (!this.breakpoints || this.breakpoints.size === 0) {
      const emptyMessage = document.createElement('div');
      emptyMessage.className = 'debug-empty-message';
      emptyMessage.textContent = 'No breakpoints';
      this.breakpointsContainer.appendChild(emptyMessage);
      return;
    }

    // Create breakpoints list
    const list = document.createElement('ul');
    list.className = 'debug-breakpoints-list';

    // Add breakpoints
    for (const [filePath, lines] of this.breakpoints.entries()) {
      const fileName = path.basename(filePath);

      lines.forEach(line => {
        const item = document.createElement('li');
        item.className = 'debug-breakpoint-item';

        item.innerHTML = `
          <span class="breakpoint-location">${fileName}:${line}</span>
          <button class="breakpoint-remove" title="Remove Breakpoint">×</button>
        `;

        // Add click handler to navigate to breakpoint
        item.addEventListener('click', () => {
          if (editorManager) {
            editorManager.openFile(filePath);
            editorManager.goToLine(line);
          }
        });

        // Add click handler to remove button
        item.querySelector('.breakpoint-remove').addEventListener('click', (e) => {
          e.stopPropagation();
          this.toggleBreakpoint(filePath, line);
        });

        list.appendChild(item);
      });
    }

    this.breakpointsContainer.appendChild(list);
  }

  clearAllBreakpoints() {
    // Clear all breakpoints
    const allFilePaths = Array.from(this.breakpoints.keys());

    // Clear breakpoints map
    this.breakpoints.clear();

    // Update breakpoints in editor for each file
    if (editorManager) {
      allFilePaths.forEach(filePath => {
        editorManager.updateBreakpoints(filePath, []);
      });
    }

    // Update breakpoints in debug session
    if (this.isDebugging && this.debugProcessId) {
      window.api.updateBreakpoints(this.debugProcessId, []);
    }

    // Update breakpoints view
    this.updateBreakpointsView();
  }
}

// Initialize the debugger manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
  window.debuggerManager = new MonoDebugger();
});
