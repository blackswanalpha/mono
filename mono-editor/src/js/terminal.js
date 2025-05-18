// Terminal for Mono Editor

class TerminalManager {
  constructor() {
    // Initialize after DOM is fully loaded
    // Use a promise to handle async initialization
    this.initPromise = this.initialize().catch(error => {
      console.error('Error initializing terminal manager:', error);
    });
  }

  async initialize() {
    console.log('Initializing terminal manager');

    // Terminal container elements
    this.terminalContainer = document.getElementById('terminal-container');
    this.terminalTabs = document.getElementById('terminal-tabs');
    this.terminalPanes = document.getElementById('terminal-panes');
    this.terminalResizeHandle = document.getElementById('terminal-resize-handle');

    // View tabs
    this.terminalViewTabs = document.querySelectorAll('.terminal-view-tab');
    this.terminalViews = document.querySelectorAll('.terminal-view');
    this.terminalViewActions = document.querySelectorAll('.terminal-view-actions');

    // Terminal state
    this.terminals = {}; // Map of terminal instances by ID
    this.activeTerminal = null; // Currently active terminal ID
    this.isVisible = false;
    this.terminalCounter = 0; // Counter for generating terminal IDs
    this.activeView = 'terminal'; // Current active view (terminal or debug)
    this.scrollLocked = false; // Whether terminal scrolling is locked

    // Current working directory for each terminal
    this.workingDirectories = {}; // Map of working directories by terminal ID

    // Terminal size settings
    this.defaultTerminalHeight = 250; // Default height in pixels
    this.minTerminalHeight = 100; // Minimum height in pixels
    this.maxTerminalHeight = window.innerHeight * 0.8; // Maximum height (80% of window)
    this.terminalHeight = this.loadTerminalHeight() || this.defaultTerminalHeight;

    // Set initial terminal height
    this.setTerminalHeight(this.terminalHeight);

    // Initialize event listeners
    this.initEventListeners();

    // Initialize process event listeners
    this.initProcessEventListeners();

    // Initialize view tabs event listeners
    this.initViewTabsEventListeners();

    // Initialize resize handle
    this.initResizeHandle();

    // Create the first terminal
    try {
      await this.createTerminal();
    } catch (error) {
      console.error('Error creating initial terminal:', error);
      // Set a default working directory in case of error
      this.workingDirectories['terminal-1'] = '/';
    }

    console.log('Terminal manager initialized');
  }

  // Initialize view tabs event listeners
  initViewTabsEventListeners() {
    this.terminalViewTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const view = tab.getAttribute('data-view');
        this.switchView(view);
      });
    });
  }

  // Switch between terminal and debug views
  switchView(view) {
    // Update active view
    this.activeView = view;

    // Update view tabs
    this.terminalViewTabs.forEach(tab => {
      if (tab.getAttribute('data-view') === view) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });

    // Update views
    this.terminalViews.forEach(viewElement => {
      if (viewElement.getAttribute('data-view') === view) {
        viewElement.classList.add('active');
      } else {
        viewElement.classList.remove('active');
      }
    });

    // Update action buttons
    this.terminalViewActions.forEach(actionElement => {
      if (actionElement.getAttribute('data-view') === view) {
        actionElement.classList.remove('hidden');
      } else {
        actionElement.classList.add('hidden');
      }
    });

    // If switching to terminal view, focus the active terminal
    if (view === 'terminal' && this.activeTerminal) {
      const terminalInfo = this.terminals[this.activeTerminal];
      if (terminalInfo) {
        setTimeout(() => {
          terminalInfo.fitAddon.fit();
          terminalInfo.terminal.focus();
        }, 0);
      }
    }

    // If switching to debug view, notify the debugger
    if (view === 'debug' && window.debuggerManager) {
      // This will be handled by the debugger manager
      document.dispatchEvent(new CustomEvent('debug-view-activated'));
    }
  }

  async createTerminal() {
    // Generate a unique terminal ID
    const terminalId = `terminal-${++this.terminalCounter}`;

    // Create tab element
    const tabElement = document.createElement('div');
    tabElement.className = 'terminal-tab';
    tabElement.setAttribute('data-terminal-id', terminalId);
    tabElement.innerHTML = `
      <span>Terminal ${this.terminalCounter}</span>
      <div class="tab-close">×</div>
    `;
    this.terminalTabs.appendChild(tabElement);

    // Create terminal pane
    const paneElement = document.createElement('div');
    paneElement.className = 'terminal-pane';
    paneElement.id = `terminal-pane-${terminalId}`;

    // Create terminal element
    const terminalElement = document.createElement('div');
    terminalElement.className = 'terminal';
    terminalElement.id = `terminal-${terminalId}`;
    paneElement.appendChild(terminalElement);

    this.terminalPanes.appendChild(paneElement);

    // Create XTerm.js terminal with enhanced scrolling
    const terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Consolas, "Courier New", monospace',
      theme: this.getTerminalTheme(),
      scrollback: 5000, // Increased scrollback for better history
      cols: 80,
      rows: 10,
      smoothScrollDuration: 300, // Enable smooth scrolling
      scrollSensitivity: 1.5, // Increase scroll sensitivity
      fastScrollSensitivity: 5, // Fast scroll with modifier keys
      fastScrollModifier: 'alt' // Use Alt key for fast scrolling
    });

    // Create fit addon
    const fitAddon = new FitAddon.FitAddon();
    terminal.loadAddon(fitAddon);

    // Open the terminal
    terminal.open(terminalElement);

    // Fit the terminal to the container
    fitAddon.fit();

    // Write welcome message
    terminal.writeln('Mono Editor Terminal');
    terminal.writeln('Type "help" for available commands');
    terminal.writeln('');
    terminal.write('$ ');

    // Store terminal instance
    this.terminals[terminalId] = {
      terminal: terminal,
      fitAddon: fitAddon,
      element: terminalElement,
      pane: paneElement,
      tab: tabElement,
      commandBuffer: '',
      currentProcessId: null,
      originalOnDataHandler: null
    };

    // Initialize working directory to the project root
    // Use the API to get the current directory if available, otherwise use '/'
    try {
      if (window.api && window.api.getCurrentDirectory) {
        // Await the promise returned by getCurrentDirectory
        const currentDir = await window.api.getCurrentDirectory();
        this.workingDirectories[terminalId] = currentDir || '/';
      } else {
        this.workingDirectories[terminalId] = '/';
      }
    } catch (error) {
      console.error('Error getting current directory:', error);
      this.workingDirectories[terminalId] = '/';
    }

    // Set up command handling
    this.setupCommandHandling(terminalId);

    // Activate the new terminal
    this.activateTerminal(terminalId);

    // Show the terminal container if it's hidden
    if (!this.isVisible) {
      this.showTerminal();
    }

    return terminalId;
  }

  setupCommandHandling(terminalId) {
    const terminalInfo = this.terminals[terminalId];
    if (!terminalInfo) return;

    const terminal = terminalInfo.terminal;

    // Handle terminal input
    terminal.onData(data => {
      // If there's a process running, let the process handler handle it
      if (terminalInfo.currentProcessId) {
        return;
      }

      // Handle special keys
      switch (data) {
        case '\r': // Enter
          terminal.writeln('');
          this.handleCommand(terminalId, terminalInfo.commandBuffer);
          terminalInfo.commandBuffer = '';
          terminal.write('$ ');
          break;
        case '\u007F': // Backspace
          if (terminalInfo.commandBuffer.length > 0) {
            terminalInfo.commandBuffer = terminalInfo.commandBuffer.slice(0, -1);
            terminal.write('\b \b');
          }
          break;
        case '\u0003': // Ctrl+C
          terminal.writeln('^C');
          terminalInfo.commandBuffer = '';
          terminal.write('$ ');
          break;
        default:
          // Only handle printable characters
          if (data >= ' ' || data === '\t') {
            terminalInfo.commandBuffer += data;
            terminal.write(data);
          }
          break;
      }
    });
  }

  initEventListeners() {
    // Terminal toggle button
    document.getElementById('close-terminal-btn').addEventListener('click', () => {
      this.hideTerminal();
    });

    // Clear terminal button
    document.getElementById('clear-terminal-btn').addEventListener('click', () => {
      this.clearActiveTerminal();
    });

    // New terminal button
    document.getElementById('new-terminal-btn').addEventListener('click', () => {
      this.createTerminal().catch(error => {
        console.error('Error creating new terminal:', error);
      });
    });

    // Scroll lock button
    const scrollLockBtn = document.getElementById('scroll-lock-btn');
    if (scrollLockBtn) {
      scrollLockBtn.addEventListener('click', () => {
        this.toggleScrollLock();
      });
    }

    // Terminal tabs click event
    this.terminalTabs.addEventListener('click', (e) => {
      const tabElement = e.target.closest('[data-terminal-id]');
      if (tabElement) {
        const terminalId = tabElement.getAttribute('data-terminal-id');
        this.activateTerminal(terminalId);
      }

      // Close button click
      if (e.target.classList.contains('tab-close')) {
        const tabElement = e.target.closest('[data-terminal-id]');
        if (tabElement) {
          const terminalId = tabElement.getAttribute('data-terminal-id');
          this.closeTerminal(terminalId);
          e.stopPropagation(); // Prevent tab activation
        }
      }
    });

    // Window resize event
    window.addEventListener('resize', () => {
      // Update max terminal height
      this.maxTerminalHeight = window.innerHeight * 0.8;

      // Ensure terminal height is within bounds
      if (this.terminalHeight > this.maxTerminalHeight) {
        this.setTerminalHeight(this.maxTerminalHeight);
      }

      // Resize all terminals
      this.resizeAllTerminals();
    });

    // Register with scrolling manager if available
    if (window.scrollingManager) {
      // Re-register terminal container with scrolling manager
      window.scrollingManager.registerScrollableElement('terminal-container', this.terminalContainer);

      // Register individual terminal panes
      for (const terminalId in this.terminals) {
        const terminalInfo = this.terminals[terminalId];
        if (terminalInfo && terminalInfo.element) {
          window.scrollingManager.registerScrollableElement(`terminal-${terminalId}`, terminalInfo.element);
        }
      }
    }
  }

  activateTerminal(terminalId) {
    // Deactivate all tabs
    const tabs = this.terminalTabs.querySelectorAll('.terminal-tab');
    tabs.forEach(tab => tab.classList.remove('active'));

    // Deactivate all panes
    const panes = this.terminalPanes.querySelectorAll('.terminal-pane');
    panes.forEach(pane => pane.classList.remove('active'));

    // Activate the selected terminal
    const terminalInfo = this.terminals[terminalId];
    if (terminalInfo) {
      terminalInfo.tab.classList.add('active');
      terminalInfo.pane.classList.add('active');

      // Focus the terminal
      setTimeout(() => {
        terminalInfo.fitAddon.fit();
        terminalInfo.terminal.focus();
      }, 0);

      this.activeTerminal = terminalId;
    }
  }

  closeTerminal(terminalId) {
    const terminalInfo = this.terminals[terminalId];
    if (!terminalInfo) return;

    // Check if there's a process running
    if (terminalInfo.currentProcessId) {
      // Stop the process
      this.stopProcess(terminalId);
    }

    // Remove tab and pane elements
    terminalInfo.tab.remove();
    terminalInfo.pane.remove();

    // Dispose of the terminal
    terminalInfo.terminal.dispose();

    // Remove from terminals map
    delete this.terminals[terminalId];

    // If this was the active terminal, activate another one
    if (this.activeTerminal === terminalId) {
      const remainingTerminals = Object.keys(this.terminals);
      if (remainingTerminals.length > 0) {
        this.activateTerminal(remainingTerminals[0]);
      } else {
        // If no terminals left, create a new one
        this.createTerminal().catch(error => {
          console.error('Error creating new terminal after closing last one:', error);
        });
      }
    }
  }

  showTerminal() {
    this.terminalContainer.classList.remove('hidden');
    this.isVisible = true;

    // Fit the active terminal to the container if terminal view is active
    if (this.activeView === 'terminal' && this.activeTerminal && this.terminals[this.activeTerminal]) {
      const terminalInfo = this.terminals[this.activeTerminal];
      setTimeout(() => {
        terminalInfo.fitAddon.fit();
        terminalInfo.terminal.focus();
      }, 0);
    }

    // Notify the debugger if debug view is active
    if (this.activeView === 'debug' && window.debuggerManager) {
      document.dispatchEvent(new CustomEvent('debug-view-activated'));
    }
  }

  hideTerminal() {
    this.terminalContainer.classList.add('hidden');
    this.isVisible = false;
  }

  toggleTerminal() {
    if (this.isVisible) {
      this.hideTerminal();
    } else {
      this.showTerminal();
    }
  }

  // Switch to debug view and show terminal container
  showDebugView() {
    this.switchView('debug');
    this.showTerminal();
  }

  // Switch to terminal view and show terminal container
  showTerminalView() {
    this.switchView('terminal');
    this.showTerminal();
  }

  clearActiveTerminal() {
    if (this.activeTerminal && this.terminals[this.activeTerminal]) {
      this.terminals[this.activeTerminal].terminal.clear();
    }
  }

  resetActiveTerminal() {
    if (this.activeTerminal && this.terminals[this.activeTerminal]) {
      const terminal = this.terminals[this.activeTerminal].terminal;
      terminal.reset();
      terminal.clear();
      terminal.writeln('Mono Editor Terminal');
      terminal.writeln('Type "help" for available commands');
      terminal.writeln('');
      terminal.write('$ ');
    }
  }

  handleCommand(terminalId, command) {
    const terminalInfo = this.terminals[terminalId];
    if (!terminalInfo) return;

    const terminal = terminalInfo.terminal;
    command = command.trim();

    if (!command) {
      return;
    }

    // Get current working directory
    const currentDir = this.workingDirectories[terminalId] || '/';

    // Parse command and arguments
    const parts = command.split(' ');
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);

    // Check for ./mono command pattern
    if (cmd.startsWith('./') && cmd.endsWith('mono')) {
      // This is a direct execution of a Mono file
      if (args.length === 0) {
        terminal.writeln('Error: Missing file path');
        terminal.writeln('Usage: ./mono <file>');
      } else {
        this.runMonoFile(terminalId, args[0]);
      }
      return;
    }

    // Handle built-in commands
    switch (cmd) {
      case 'help':
        terminal.writeln('Available commands:');
        terminal.writeln('  help                - Show this help message');
        terminal.writeln('  clear               - Clear the terminal');
        terminal.writeln('  run <file>          - Run a Mono file');
        terminal.writeln('  ./mono <file>       - Run a Mono file (alternative syntax)');
        terminal.writeln('  pwd                 - Print working directory');
        terminal.writeln('  cd <directory>      - Change directory');
        terminal.writeln('  ls [directory]      - List files in directory');
        terminal.writeln('  mkdir <directory>   - Create a directory');
        terminal.writeln('  cat <file>          - Display file contents');
        terminal.writeln('  exit                - Hide the terminal');
        terminal.writeln('  new                 - Open a new terminal tab');
        break;
      case 'clear':
        terminal.clear();
        break;
      case 'exit':
        this.hideTerminal();
        break;
      case 'new':
        this.createTerminal();
        break;
      case 'run':
        if (args.length === 0) {
          terminal.writeln('Error: Missing file path');
          terminal.writeln('Usage: run <file>');
        } else {
          this.runMonoFile(terminalId, args[0]);
        }
        break;
      case 'pwd':
        terminal.writeln(currentDir);
        break;
      case 'cd':
        this.changeDirectory(terminalId, args[0] || '~');
        break;
      case 'ls':
        this.listDirectory(terminalId, args[0] || '.');
        break;
      case 'mkdir':
        if (args.length === 0) {
          terminal.writeln('Error: Missing directory name');
          terminal.writeln('Usage: mkdir <directory>');
        } else {
          this.makeDirectory(terminalId, args[0]);
        }
        break;
      case 'cat':
        if (args.length === 0) {
          terminal.writeln('Error: Missing file path');
          terminal.writeln('Usage: cat <file>');
        } else {
          this.displayFileContents(terminalId, args[0]);
        }
        break;
      default:
        terminal.writeln(`Command not found: ${cmd}`);
        terminal.writeln('Type "help" for available commands');
        break;
    }
  }

  /**
   * Change the current working directory
   * @param {string} terminalId - The terminal ID
   * @param {string} dirPath - The directory path to change to
   */
  async changeDirectory(terminalId, dirPath) {
    const terminalInfo = this.terminals[terminalId];
    if (!terminalInfo) return;

    const terminal = terminalInfo.terminal;
    const currentDir = this.workingDirectories[terminalId] || '/';

    try {
      // Handle special paths
      if (dirPath === '~') {
        // Home directory
        this.workingDirectories[terminalId] = '/';
        return;
      } else if (dirPath === '..') {
        // Parent directory
        const parentDir = currentDir.split('/').slice(0, -1).join('/') || '/';
        this.workingDirectories[terminalId] = parentDir;
        return;
      } else if (dirPath === '.') {
        // Current directory - no change needed
        return;
      }

      // Resolve the path (absolute or relative)
      let newPath;
      if (dirPath.startsWith('/')) {
        // Absolute path
        newPath = dirPath;
      } else {
        // Relative path
        newPath = currentDir === '/' ? `/${dirPath}` : `${currentDir}/${dirPath}`;
      }

      // Normalize the path (remove double slashes, handle .. and .)
      newPath = this.normalizePath(newPath);

      // Check if directory exists
      try {
        const stats = await window.api.readDirectory(newPath);
        if (stats) {
          this.workingDirectories[terminalId] = newPath;
        }
      } catch (error) {
        terminal.writeln(`cd: ${dirPath}: No such directory`);
      }
    } catch (error) {
      terminal.writeln(`Error changing directory: ${error.message}`);
    }
  }

  /**
   * List files in a directory
   * @param {string} terminalId - The terminal ID
   * @param {string} dirPath - The directory path to list
   */
  async listDirectory(terminalId, dirPath) {
    const terminalInfo = this.terminals[terminalId];
    if (!terminalInfo) return;

    const terminal = terminalInfo.terminal;
    const currentDir = this.workingDirectories[terminalId] || '/';

    try {
      // Resolve the path (absolute or relative)
      let targetPath;
      if (dirPath.startsWith('/')) {
        // Absolute path
        targetPath = dirPath;
      } else {
        // Relative path
        targetPath = currentDir === '/' ? `/${dirPath}` : `${currentDir}/${dirPath}`;
      }

      // Normalize the path
      targetPath = this.normalizePath(targetPath);

      // Read directory contents
      try {
        const files = await window.api.readDirectory(targetPath);

        if (files && files.length > 0) {
          // Sort files and directories
          const sortedFiles = files.sort((a, b) => {
            // Directories first, then files
            if (a.isDirectory && !b.isDirectory) return -1;
            if (!a.isDirectory && b.isDirectory) return 1;
            return a.name.localeCompare(b.name);
          });

          // Display files with colors
          terminal.writeln(`Contents of ${targetPath}:`);

          // Calculate column width for better formatting
          const maxNameLength = Math.max(...sortedFiles.map(file => file.name.length));
          const columnWidth = Math.min(maxNameLength + 2, 30);

          // Display in columns if possible
          let line = '';
          let lineLength = 0;

          for (const file of sortedFiles) {
            let displayName = file.name;

            // Add color and formatting based on file type
            if (file.isDirectory) {
              // Blue for directories
              displayName = `\x1b[34m${displayName}/\x1b[0m`;
            } else if (file.name.endsWith('.mono')) {
              // Green for Mono files
              displayName = `\x1b[32m${displayName}\x1b[0m`;
            } else if (file.name.endsWith('.js') || file.name.endsWith('.py')) {
              // Yellow for script files
              displayName = `\x1b[33m${displayName}\x1b[0m`;
            }

            // Pad the name to align columns
            const paddedName = displayName.padEnd(columnWidth + 10); // Extra padding for color codes

            // Add to current line or start new line
            if (lineLength + columnWidth > terminal.cols) {
              terminal.writeln(line);
              line = paddedName;
              lineLength = columnWidth;
            } else {
              line += paddedName;
              lineLength += columnWidth;
            }
          }

          // Print the last line if not empty
          if (line) {
            terminal.writeln(line);
          }
        } else {
          terminal.writeln(`Directory is empty: ${targetPath}`);
        }
      } catch (error) {
        terminal.writeln(`ls: ${dirPath}: No such directory`);
      }
    } catch (error) {
      terminal.writeln(`Error listing directory: ${error.message}`);
    }
  }

  /**
   * Create a new directory
   * @param {string} terminalId - The terminal ID
   * @param {string} dirPath - The directory path to create
   */
  async makeDirectory(terminalId, dirPath) {
    const terminalInfo = this.terminals[terminalId];
    if (!terminalInfo) return;

    const terminal = terminalInfo.terminal;
    const currentDir = this.workingDirectories[terminalId] || '/';

    try {
      // Resolve the path (absolute or relative)
      let targetPath;
      if (dirPath.startsWith('/')) {
        // Absolute path
        targetPath = dirPath;
      } else {
        // Relative path
        targetPath = currentDir === '/' ? `/${dirPath}` : `${currentDir}/${dirPath}`;
      }

      // Normalize the path
      targetPath = this.normalizePath(targetPath);

      // Create the directory
      try {
        await window.api.createDirectory(targetPath);
        terminal.writeln(`Directory created: ${targetPath}`);
      } catch (error) {
        terminal.writeln(`mkdir: Cannot create directory '${dirPath}': ${error.message}`);
      }
    } catch (error) {
      terminal.writeln(`Error creating directory: ${error.message}`);
    }
  }

  /**
   * Display file contents
   * @param {string} terminalId - The terminal ID
   * @param {string} filePath - The file path to display
   */
  async displayFileContents(terminalId, filePath) {
    const terminalInfo = this.terminals[terminalId];
    if (!terminalInfo) return;

    const terminal = terminalInfo.terminal;
    const currentDir = this.workingDirectories[terminalId] || '/';

    try {
      // Resolve the path (absolute or relative)
      let targetPath;
      if (filePath.startsWith('/')) {
        // Absolute path
        targetPath = filePath;
      } else {
        // Relative path
        targetPath = currentDir === '/' ? `/${filePath}` : `${currentDir}/${filePath}`;
      }

      // Normalize the path
      targetPath = this.normalizePath(targetPath);

      // Read file contents
      try {
        const content = await window.api.readFile(targetPath);

        // Display file contents with syntax highlighting for Mono files
        if (targetPath.endsWith('.mono')) {
          terminal.writeln(`\x1b[1m--- ${targetPath} ---\x1b[0m`);

          // Simple syntax highlighting for Mono files
          const lines = content.split('\n');
          for (const line of lines) {
            // Highlight keywords
            let highlightedLine = line
              .replace(/\b(component|function|var|state|props|return|if|else|for|while)\b/g, '\x1b[34m$1\x1b[0m')
              .replace(/\b(true|false|null|undefined)\b/g, '\x1b[35m$1\x1b[0m')
              .replace(/"([^"]*)"/g, '\x1b[32m"$1"\x1b[0m')
              .replace(/'([^']*)'/g, '\x1b[32m\'$1\'\x1b[0m')
              .replace(/\/\/(.*)/g, '\x1b[90m//$1\x1b[0m');

            terminal.writeln(highlightedLine);
          }
        } else {
          // Regular file display
          terminal.writeln(`\x1b[1m--- ${targetPath} ---\x1b[0m`);
          terminal.writeln(content);
        }
      } catch (error) {
        terminal.writeln(`cat: ${filePath}: No such file or directory`);
      }
    } catch (error) {
      terminal.writeln(`Error displaying file: ${error.message}`);
    }
  }

  /**
   * Normalize a file path
   * @param {string} path - The path to normalize
   * @returns {string} The normalized path
   */
  normalizePath(path) {
    // Split the path into segments
    const segments = path.split('/').filter(segment => segment !== '');
    const normalizedSegments = [];

    // Process each segment
    for (const segment of segments) {
      if (segment === '.') {
        // Current directory - skip
        continue;
      } else if (segment === '..') {
        // Parent directory - remove last segment
        if (normalizedSegments.length > 0) {
          normalizedSegments.pop();
        }
      } else {
        // Regular segment - add to result
        normalizedSegments.push(segment);
      }
    }

    // Join segments and add leading slash
    return '/' + normalizedSegments.join('/');
  }

  async runMonoFile(terminalId, filePath) {
    const terminalInfo = this.terminals[terminalId];
    if (!terminalInfo) {
      console.error(`Terminal with ID ${terminalId} not found`);
      return;
    }

    const terminal = terminalInfo.terminal;
    const currentDir = this.workingDirectories[terminalId] || '/';

    try {
      // If no path is provided, try to use the active editor file
      if (!filePath && window.editorManager) {
        filePath = window.editorManager.getActiveFilePath();
        if (!filePath) {
          terminal.writeln('Error: No file is open');
          return;
        }

        // Save the file if it has unsaved changes
        const activeEditor = window.editorManager.getActiveEditor();
        if (activeEditor && activeEditor.isDirty) {
          terminal.writeln('Saving file before running...');
          try {
            await window.editorManager.saveFile(window.editorManager.activeEditor);
            terminal.writeln('File saved successfully');
          } catch (saveError) {
            terminal.writeln(`Error saving file: ${saveError.message}`);
            // Continue anyway to try running the file
          }
        }
      }

      // Resolve the path (absolute or relative)
      let targetPath;
      if (filePath.startsWith('/')) {
        // Absolute path
        targetPath = filePath;
      } else {
        // Relative path
        targetPath = currentDir === '/' ? `/${filePath}` : `${currentDir}/${filePath}`;
      }

      // Normalize the path
      targetPath = this.normalizePath(targetPath);

      terminal.writeln(`Running Mono file: ${targetPath}`);

      // Validate file path
      if (!targetPath) {
        terminal.writeln('Error: No file path provided');
        return;
      }

      // Check if file exists
      try {
        await window.api.readFile(targetPath);
      } catch (readError) {
        terminal.writeln(`Error: File not found or cannot be read: ${targetPath}`);
        terminal.writeln(`Details: ${readError.message}`);
        return;
      }

      // Run the file
      terminal.writeln(`Executing: ${targetPath}`);
      terminal.writeln('');

      try {
        // Run the Mono interpreter
        const processId = await window.api.runMonoFile(targetPath);
        terminal.writeln(`Process started with PID: ${processId}`);

        // Store the process ID
        terminalInfo.currentProcessId = processId;

        // Set up input handling for the process
        this.setupProcessInputHandling(terminalId);
      } catch (error) {
        terminal.writeln(`Error executing file: ${error.message}`);

        // Provide more helpful error information
        if (error.message.includes('Cannot access the mono interpreter')) {
          terminal.writeln('The Mono interpreter may not be properly installed or configured.');
          terminal.writeln('Please check that the mono script is executable.');
        } else if (error.message.includes('Cannot access the file')) {
          terminal.writeln('The file may not exist or you may not have permission to read it.');
        }
      }
    } catch (error) {
      terminal.writeln(`Error: ${error.message}`);
      console.error('Error running Mono file:', error);
    }
  }

  setupProcessInputHandling(terminalId) {
    const terminalInfo = this.terminals[terminalId];
    if (!terminalInfo) return;

    const terminal = terminalInfo.terminal;

    // Store the original onData handler
    if (!terminalInfo.originalOnDataHandler) {
      terminalInfo.originalOnDataHandler = terminal._core._onData._listeners[0];

      // Remove the original handler
      terminal._core._onData._listeners = [];
    }

    // Add a new handler for process input
    terminal.onData(data => {
      if (terminalInfo.currentProcessId) {
        // Handle special keys
        switch (data) {
          case '\u0003': // Ctrl+C
            terminal.writeln('^C');
            this.stopProcess(terminalId);
            break;
          default:
            // Send the input to the process
            window.api.writeToProcess(terminalInfo.currentProcessId, data);

            // Echo the input to the terminal
            terminal.write(data);
            break;
        }
      } else {
        // If no process is running, use the original command handling
        if (terminalInfo.originalOnDataHandler) {
          terminalInfo.originalOnDataHandler(data);
        }
      }
    });
  }

  stopProcess(terminalId) {
    const terminalInfo = this.terminals[terminalId];
    if (!terminalInfo || !terminalInfo.currentProcessId) return;

    window.api.stopProcess(terminalInfo.currentProcessId);
    terminalInfo.currentProcessId = null;

    // Restore original input handling
    this.restoreOriginalInputHandling(terminalId);
  }

  restoreOriginalInputHandling(terminalId) {
    const terminalInfo = this.terminals[terminalId];
    if (!terminalInfo) return;

    const terminal = terminalInfo.terminal;

    // Remove all current handlers
    terminal._core._onData._listeners = [];

    // Restore the original handler if available
    if (terminalInfo.originalOnDataHandler) {
      terminal.onData(terminalInfo.originalOnDataHandler);
    }
  }

  initProcessEventListeners() {
    // Listen for process output
    window.api.onProcessOutput(data => {
      // Find the terminal with this process ID
      for (const terminalId in this.terminals) {
        const terminalInfo = this.terminals[terminalId];
        if (terminalInfo.currentProcessId === data.id) {
          // Write the output to the terminal
          if (data.type === 'stderr') {
            // Use a different color for stderr
            terminalInfo.terminal.write('\x1b[31m' + data.data + '\x1b[0m');
          } else {
            terminalInfo.terminal.write(data.data);
          }
          break;
        }
      }
    });

    // Listen for process exit
    window.api.onProcessExit(data => {
      // Find the terminal with this process ID
      for (const terminalId in this.terminals) {
        const terminalInfo = this.terminals[terminalId];
        if (terminalInfo.currentProcessId === data.id) {
          const terminal = terminalInfo.terminal;

          // Write the exit code to the terminal
          terminal.writeln('');
          if (data.code === 0) {
            terminal.writeln('\r\nProcess completed successfully.');
          } else {
            terminal.writeln(`\r\nProcess exited with code ${data.code}.`);
          }
          terminal.writeln('');
          terminal.write('$ ');

          // Clear the current process ID
          terminalInfo.currentProcessId = null;

          // Restore original input handling
          this.restoreOriginalInputHandling(terminalId);
          break;
        }
      }
    });
  }

  getTerminalTheme() {
    const bodyThemeClass = document.body.className.match(/theme-(\w+)/);
    if (bodyThemeClass && bodyThemeClass[1]) {
      switch (bodyThemeClass[1]) {
        case 'dark':
          return {
            background: '#1e1e1e',
            foreground: '#cccccc',
            cursor: '#cccccc',
            cursorAccent: '#1e1e1e',
            selection: 'rgba(255, 255, 255, 0.3)',
            black: '#000000',
            red: '#cd3131',
            green: '#0dbc79',
            yellow: '#e5e510',
            blue: '#2472c8',
            magenta: '#bc3fbc',
            cyan: '#11a8cd',
            white: '#e5e5e5',
            brightBlack: '#666666',
            brightRed: '#f14c4c',
            brightGreen: '#23d18b',
            brightYellow: '#f5f543',
            brightBlue: '#3b8eea',
            brightMagenta: '#d670d6',
            brightCyan: '#29b8db',
            brightWhite: '#e5e5e5'
          };
        case 'light':
          return {
            background: '#ffffff',
            foreground: '#333333',
            cursor: '#333333',
            cursorAccent: '#ffffff',
            selection: 'rgba(0, 0, 0, 0.3)',
            black: '#000000',
            red: '#cd3131',
            green: '#00bc00',
            yellow: '#949800',
            blue: '#0451a5',
            magenta: '#bc05bc',
            cyan: '#0598bc',
            white: '#555555',
            brightBlack: '#666666',
            brightRed: '#cd3131',
            brightGreen: '#14ce14',
            brightYellow: '#b5ba00',
            brightBlue: '#0451a5',
            brightMagenta: '#bc05bc',
            brightCyan: '#0598bc',
            brightWhite: '#a5a5a5'
          };
        case 'nord':
          return {
            background: '#2e3440',
            foreground: '#d8dee9',
            cursor: '#d8dee9',
            cursorAccent: '#2e3440',
            selection: 'rgba(216, 222, 233, 0.3)',
            black: '#3b4252',
            red: '#bf616a',
            green: '#a3be8c',
            yellow: '#ebcb8b',
            blue: '#81a1c1',
            magenta: '#b48ead',
            cyan: '#88c0d0',
            white: '#e5e9f0',
            brightBlack: '#4c566a',
            brightRed: '#bf616a',
            brightGreen: '#a3be8c',
            brightYellow: '#ebcb8b',
            brightBlue: '#81a1c1',
            brightMagenta: '#b48ead',
            brightCyan: '#8fbcbb',
            brightWhite: '#eceff4'
          };
        default:
          return {};
      }
    }
    return {};
  }

  setTheme(themeName) {
    // Update terminal theme if terminal is initialized
    if (this.terminal && typeof this.terminal.setOption === 'function') {
      try {
        this.terminal.setOption('theme', this.getTerminalTheme());
      } catch (error) {
        console.warn('Error setting terminal theme:', error);
      }
    }
  }

  /**
   * Initialize the terminal resize handle
   */
  initResizeHandle() {
    if (!this.terminalResizeHandle) return;

    let startY = 0;
    let startHeight = 0;
    let isDragging = false;

    // Mouse down event
    this.terminalResizeHandle.addEventListener('mousedown', (e) => {
      // Start dragging
      isDragging = true;
      startY = e.clientY;
      startHeight = this.terminalHeight;

      // Add dragging class
      this.terminalResizeHandle.classList.add('dragging');

      // Add no-select class to body to prevent text selection during drag
      document.body.classList.add('no-select');

      e.preventDefault();
    });

    // Mouse move event
    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;

      // Calculate new height
      const deltaY = startY - e.clientY;
      let newHeight = startHeight + deltaY;

      // Ensure height is within bounds
      newHeight = Math.max(this.minTerminalHeight, Math.min(newHeight, this.maxTerminalHeight));

      // Set terminal height
      this.setTerminalHeight(newHeight);

      e.preventDefault();
    });

    // Mouse up event
    document.addEventListener('mouseup', () => {
      if (!isDragging) return;

      // Stop dragging
      isDragging = false;

      // Remove dragging class
      this.terminalResizeHandle.classList.remove('dragging');

      // Remove no-select class from body
      document.body.classList.remove('no-select');

      // Save terminal height
      this.saveTerminalHeight();

      // Resize all terminals
      this.resizeAllTerminals();
    });
  }

  /**
   * Set the terminal height
   * @param {number} height - The height in pixels
   */
  setTerminalHeight(height) {
    // Ensure height is within bounds
    height = Math.max(this.minTerminalHeight, Math.min(height, this.maxTerminalHeight));

    // Update terminal height
    this.terminalHeight = height;

    // Set container height
    this.terminalContainer.style.height = `${height}px`;
    this.terminalContainer.classList.add('custom-height');

    // Resize all terminals
    this.resizeAllTerminals();
  }

  /**
   * Resize all terminals to fit the container
   */
  resizeAllTerminals() {
    // Resize all terminals
    for (const terminalId in this.terminals) {
      const terminalInfo = this.terminals[terminalId];
      if (terminalInfo && terminalInfo.fitAddon) {
        try {
          terminalInfo.fitAddon.fit();
        } catch (error) {
          console.warn(`Error resizing terminal ${terminalId}:`, error);
        }
      }
    }
  }

  /**
   * Save terminal height to local storage
   */
  saveTerminalHeight() {
    try {
      localStorage.setItem('mono-terminal-height', this.terminalHeight.toString());
    } catch (error) {
      console.warn('Error saving terminal height:', error);
    }
  }

  /**
   * Load terminal height from local storage
   * @returns {number|null} The saved terminal height or null if not found
   */
  loadTerminalHeight() {
    try {
      const height = localStorage.getItem('mono-terminal-height');
      return height ? parseInt(height, 10) : null;
    } catch (error) {
      console.warn('Error loading terminal height:', error);
      return null;
    }
  }

  /**
   * Toggle scroll lock for the terminal
   */
  toggleScrollLock() {
    this.scrollLocked = !this.scrollLocked;

    // Update scroll lock button
    const scrollLockBtn = document.getElementById('scroll-lock-btn');
    if (scrollLockBtn) {
      if (this.scrollLocked) {
        scrollLockBtn.classList.add('active');
        scrollLockBtn.querySelector('i').classList.remove('icon-scroll-lock');
        scrollLockBtn.querySelector('i').classList.add('icon-scroll-unlock');
        scrollLockBtn.title = 'Scroll Unlock';
      } else {
        scrollLockBtn.classList.remove('active');
        scrollLockBtn.querySelector('i').classList.remove('icon-scroll-unlock');
        scrollLockBtn.querySelector('i').classList.add('icon-scroll-lock');
        scrollLockBtn.title = 'Scroll Lock';
      }
    }

    // Apply scroll lock to active terminal
    if (this.activeTerminal && this.terminals[this.activeTerminal]) {
      const terminalInfo = this.terminals[this.activeTerminal];
      const viewport = terminalInfo.element.querySelector('.xterm-viewport');

      if (viewport) {
        if (this.scrollLocked) {
          viewport.style.overflowY = 'hidden';
        } else {
          viewport.style.overflowY = 'auto';
        }
      }
    }
  }
}

// Initialize the terminal manager when the page loads
let terminalManager;
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded for terminal manager');

  // Wait for XTerm.js to be loaded
  if (typeof Terminal !== 'undefined' && typeof FitAddon !== 'undefined') {
    terminalManager = new TerminalManager();

    // Make it globally available
    window.terminalManager = terminalManager;

    console.log('Terminal manager created');
  } else {
    console.error('XTerm.js not loaded');
  }
});
