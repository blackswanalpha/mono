// Editor management for Mono Editor

class EditorManager {
  constructor() {
    this.editors = {}; // Map of editor instances by tab ID
    this.activeEditor = null; // Currently active editor
    this.editorTabs = document.getElementById('editor-tabs');
    this.editorContainer = document.querySelector('.editor-container');
    this.monacoReady = false; // Flag to track if Monaco is ready
    this.pendingOperations = []; // Operations to perform when Monaco is ready

    // Check if Monaco is already loaded
    if (typeof monaco !== 'undefined') {
      this.monacoReady = true;
      console.log('Monaco Editor is already loaded');
    } else {
      // Wait for Monaco to be ready
      window.addEventListener('monaco-ready', () => {
        this.monacoReady = true;
        console.log('Monaco Editor is now ready');

        // Process any pending operations
        this.processPendingOperations();
      });

      // Also register with the Monaco loader if available
      if (window.monacoLoader) {
        window.monacoLoader.onLoad(() => {
          this.monacoReady = true;
          console.log('Monaco Editor is now ready (via loader)');

          // Process any pending operations
          this.processPendingOperations();
        });
      }
    }

    // Initialize event listeners
    this.initEventListeners();
  }

  // Process any operations that were queued while waiting for Monaco to load
  processPendingOperations() {
    console.log(`Processing ${this.pendingOperations.length} pending operations`);

    // Process each operation
    this.pendingOperations.forEach(op => {
      try {
        op();
      } catch (error) {
        console.error('Error processing pending operation:', error);
      }
    });

    // Clear the queue
    this.pendingOperations = [];
  }

  initEventListeners() {
    // Tab click event
    this.editorTabs.addEventListener('click', (e) => {
      const tabElement = e.target.closest('[data-tab-id]');
      if (tabElement) {
        const tabId = tabElement.getAttribute('data-tab-id');
        this.activateTab(tabId);
      }

      // Close button click
      if (e.target.classList.contains('tab-close')) {
        const tabElement = e.target.closest('[data-tab-id]');
        if (tabElement) {
          const tabId = tabElement.getAttribute('data-tab-id');
          this.closeTab(tabId);
          e.stopPropagation(); // Prevent tab activation
        }
      }
    });
  }

  createEditor(tabId, filePath = null, content = '') {
    console.log(`Creating editor for tab ${tabId}`);

    // Create tab element
    const fileName = filePath ? this.getFileName(filePath) : 'Untitled';
    const tabElement = document.createElement('div');
    tabElement.setAttribute('data-tab-id', tabId);
    tabElement.innerHTML = `
      <span>${fileName}</span>
      <div class="tab-close">×</div>
    `;
    this.editorTabs.appendChild(tabElement);

    // Create editor pane
    const editorPane = document.createElement('div');
    editorPane.className = 'editor-pane';
    editorPane.id = `editor-${tabId}`;
    this.editorContainer.appendChild(editorPane);

    // Create Monaco editor instance
    const editorContainer = document.createElement('div');
    editorContainer.className = 'monaco-editor-container';
    editorPane.appendChild(editorContainer);

    // Add a loading message
    editorContainer.innerHTML = '<div class="editor-loading">Loading editor...</div>';

    // Store editor info with null editor for now
    this.editors[tabId] = {
      editor: null,
      filePath: filePath,
      isDirty: false,
      breakpointDecorations: [],
      debugLineDecorations: null,
      currentLineDecorations: null,
      diagnosticHighlighter: null,
      pendingContent: content
    };

    // Function to initialize Monaco editor
    const initMonacoEditor = () => {
      console.log(`Initializing Monaco editor for tab ${tabId}`);

      // Clear any loading message
      editorContainer.innerHTML = '';

      // Initialize Monaco editor
      try {
        if (typeof monaco === 'undefined' || !monaco.editor) {
          throw new Error('Monaco Editor is not available');
        }

        const editor = monaco.editor.create(editorContainer, {
          value: this.editors[tabId].pendingContent || content,
          language: 'mono',
          theme: this.getCurrentTheme(),
          automaticLayout: true,
          minimap: {
            enabled: true
          },
          scrollBeyondLastLine: false,
          renderLineHighlight: 'all',
          lineNumbers: 'on',
          renderIndentGuides: true,
          rulers: [],
          wordWrap: 'off',
          fontSize: 14,
          fontFamily: 'Consolas, "Courier New", monospace',
          tabSize: 2,
          insertSpaces: true,
          glyphMargin: true // Enable glyph margin for breakpoints
        });

        // Update the editor instance
        this.editors[tabId].editor = editor;
        this.editors[tabId].pendingContent = null;

        // Set up change event to track dirty state
        editor.onDidChangeModelContent(() => {
          if (!this.editors[tabId].isDirty) {
            this.editors[tabId].isDirty = true;
            this.updateTabTitle(tabId);
          }
        });

        // Add breakpoint click handler
        editor.onMouseDown((e) => {
          if (e.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
            const lineNumber = e.target.position.lineNumber;
            this.toggleBreakpoint(filePath, lineNumber);
          }
        });

        // Set up cursor position change event
        editor.onDidChangeCursorPosition((e) => {
          if (this.activeEditor === tabId) {
            this.updateStatusBar(e.position);
            this.highlightCurrentLine(tabId);
          }
        });

        // Initialize diagnostic highlighter
        if (typeof DiagnosticHighlighter !== 'undefined') {
          this.editors[tabId].diagnosticHighlighter = new DiagnosticHighlighter(editor);
        } else {
          console.warn('DiagnosticHighlighter not available');
        }

        // Initial current line highlight
        this.highlightCurrentLine(tabId);

        // If this is the active tab, focus the editor
        if (this.activeEditor === tabId) {
          editor.focus();
        }

        console.log(`Monaco editor initialized for tab ${tabId}`);
        return editor;
      } catch (error) {
        console.error(`Error creating Monaco editor for tab ${tabId}:`, error);
        editorContainer.innerHTML = `<div class="editor-error">Error loading editor: ${error.message}</div>`;
        return null;
      }
    };

    // Check if Monaco is ready
    if (this.monacoReady) {
      // Initialize Monaco editor immediately
      initMonacoEditor();
    } else {
      console.log(`Monaco not ready, queueing editor initialization for tab ${tabId}`);

      // Queue the initialization for when Monaco is ready
      this.pendingOperations.push(() => {
        initMonacoEditor();
      });

      // Also try to load Monaco if the loader is available
      if (window.monacoLoader) {
        window.monacoLoader.load().catch(error => {
          console.error('Failed to load Monaco Editor:', error);
        });
      }
    }

    return tabId;
  }

  activateTab(tabId) {
    // Deactivate all tabs
    const tabs = this.editorTabs.querySelectorAll('[data-tab-id]');
    tabs.forEach(tab => tab.classList.remove('active'));

    // Deactivate all editor panes
    const panes = this.editorContainer.querySelectorAll('.editor-pane');
    panes.forEach(pane => pane.classList.remove('active'));

    // Hide welcome pane if it's visible
    const welcomePane = document.getElementById('welcome-pane');
    if (welcomePane) {
      welcomePane.classList.remove('active');
    }

    // Activate the selected tab
    const selectedTab = this.editorTabs.querySelector(`[data-tab-id="${tabId}"]`);
    if (selectedTab) {
      selectedTab.classList.add('active');
    }

    // Activate the selected editor pane
    if (tabId === 'welcome') {
      if (welcomePane) {
        welcomePane.classList.add('active');
      }
    } else {
      const editorPane = document.getElementById(`editor-${tabId}`);
      if (editorPane) {
        editorPane.classList.add('active');
      }

      // Set focus to the editor
      if (this.editors[tabId]) {
        this.editors[tabId].editor.focus();
        this.activeEditor = tabId;

        // Update status bar
        const position = this.editors[tabId].editor.getPosition();
        this.updateStatusBar(position);
      }
    }
  }

  closeTab(tabId) {
    // Check if the tab exists
    if (!this.editors[tabId] && tabId !== 'welcome') {
      return;
    }

    // Check if there are unsaved changes
    if (this.editors[tabId] && this.editors[tabId].isDirty) {
      // TODO: Show confirmation dialog
      const confirmClose = confirm('This file has unsaved changes. Do you want to save before closing?');
      if (confirmClose) {
        this.saveFile(tabId);
      }
    }

    // Remove tab element
    const tabElement = this.editorTabs.querySelector(`[data-tab-id="${tabId}"]`);
    if (tabElement) {
      tabElement.remove();
    }

    // Remove editor pane
    if (tabId !== 'welcome') {
      const editorPane = document.getElementById(`editor-${tabId}`);
      if (editorPane) {
        editorPane.remove();
      }

      // Dispose of the editor instance
      if (this.editors[tabId]) {
        this.editors[tabId].editor.dispose();
        delete this.editors[tabId];
      }
    }

    // Activate another tab if this was the active one
    if (this.activeEditor === tabId) {
      // Find another tab to activate
      const tabs = this.editorTabs.querySelectorAll('[data-tab-id]');
      if (tabs.length > 0) {
        const newTabId = tabs[tabs.length - 1].getAttribute('data-tab-id');
        this.activateTab(newTabId);
      } else {
        // If no tabs left, show welcome screen
        this.showWelcomeScreen();
      }
    }
  }

  showWelcomeScreen() {
    // Create welcome tab if it doesn't exist
    if (!this.editorTabs.querySelector('[data-tab-id="welcome"]')) {
      const welcomeTab = document.createElement('div');
      welcomeTab.className = 'welcome-tab';
      welcomeTab.setAttribute('data-tab-id', 'welcome');
      welcomeTab.innerHTML = '<span>Welcome</span>';
      this.editorTabs.appendChild(welcomeTab);
    }

    this.activateTab('welcome');
    this.activeEditor = null;
  }

  async openFile(filePath) {
    console.log(`Attempting to open file: ${filePath}`);

    // Show status message
    this.showStatusMessage('Opening file...');

    try {
      // Validate file path
      if (!filePath) {
        console.error('Cannot open file: No file path provided');
        this.showStatusMessage('No file path provided', 'error');
        return null;
      }

      // Check if the file is already open
      for (const tabId in this.editors) {
        if (this.editors[tabId].filePath === filePath) {
          console.log(`File already open in tab ${tabId}, activating tab`);
          this.activateTab(tabId);
          this.showStatusMessage('File already open', 'info');
          return tabId;
        }
      }

      // Read the file content with timeout handling
      console.log(`Reading file content from ${filePath}...`);
      let content;
      try {
        // Create a promise with timeout
        const readPromise = window.api.readFile(filePath);
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('File read operation timed out after 10 seconds')), 10000);
        });

        content = await Promise.race([readPromise, timeoutPromise]);
        console.log('File content read successfully');
      } catch (readError) {
        console.error('Error reading file:', readError);
        this.showStatusMessage('Error reading file', 'error');
        throw readError;
      }

      // Create a new editor
      console.log('Creating new editor tab...');
      const tabId = 'tab-' + Date.now();
      this.createEditor(tabId, filePath, content);
      this.activateTab(tabId);

      // Add to recent files
      this.addToRecentFiles(filePath);

      // Show success message
      this.showStatusMessage('File opened successfully', 'success');

      return tabId;
    } catch (error) {
      console.error('Error opening file:', error);
      this.showStatusMessage(`Error opening file: ${error.message}`, 'error');
      alert(`Error opening file: ${error.message}`);
      return null;
    }
  }

  async saveFile(tabId) {
    // If no tabId is provided, use the active editor
    if (!tabId && this.activeEditor) {
      tabId = this.activeEditor;
    }

    if (!this.editors[tabId]) {
      console.error('Cannot save file: No editor found for tab', tabId);
      return false;
    }

    try {
      console.log(`Saving file for tab ${tabId}...`);
      const editor = this.editors[tabId];
      const content = editor.editor.getValue();

      // Show status message
      this.showStatusMessage('Saving file...');

      // If the file doesn't have a path, show save dialog
      if (!editor.filePath) {
        console.log('No file path, showing save dialog...');
        try {
          const filePath = await window.api.saveFileAs();
          console.log('Save dialog result:', filePath);

          if (!filePath) {
            console.log('User cancelled save dialog');
            this.showStatusMessage('Save cancelled', 'warning');
            return false; // User cancelled
          }

          editor.filePath = filePath;
        } catch (dialogError) {
          console.error('Error showing save dialog:', dialogError);
          this.showStatusMessage('Error showing save dialog', 'error');
          throw dialogError;
        }
      }

      // Write the file with timeout handling
      console.log(`Writing file to ${editor.filePath}...`);
      try {
        // Create a promise with timeout
        const writePromise = window.api.writeFile(editor.filePath, content);
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('File save operation timed out after 10 seconds')), 10000);
        });

        await Promise.race([writePromise, timeoutPromise]);
        console.log('File saved successfully');
      } catch (writeError) {
        console.error('Error writing file:', writeError);
        this.showStatusMessage('Error saving file', 'error');
        throw writeError;
      }

      // Update dirty state
      editor.isDirty = false;
      this.updateTabTitle(tabId);

      // Add to recent files
      this.addToRecentFiles(editor.filePath);

      // Show success message
      this.showStatusMessage('File saved successfully', 'success');

      return true;
    } catch (error) {
      console.error('Error saving file:', error);
      alert(`Error saving file: ${error.message}`);
      return false;
    }
  }

  async saveFileAs(tabId) {
    // If no tabId is provided, use the active editor
    if (!tabId && this.activeEditor) {
      tabId = this.activeEditor;
    }

    if (!this.editors[tabId]) {
      console.error('Cannot save file as: No editor found for tab', tabId);
      return false;
    }

    try {
      console.log(`Saving file as for tab ${tabId}...`);
      const editor = this.editors[tabId];
      const content = editor.editor.getValue();

      // Show status message
      this.showStatusMessage('Saving file as...');

      // Show save dialog
      console.log('Showing save dialog...');
      const defaultPath = editor.filePath || '';
      try {
        const filePath = await window.api.saveFileAs(defaultPath);
        console.log('Save dialog result:', filePath);

        if (!filePath) {
          console.log('User cancelled save dialog');
          this.showStatusMessage('Save cancelled', 'warning');
          return false; // User cancelled
        }

        // Write the file with timeout handling
        console.log(`Writing file to ${filePath}...`);
        try {
          // Create a promise with timeout
          const writePromise = window.api.writeFile(filePath, content);
          const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('File save operation timed out after 10 seconds')), 10000);
          });

          await Promise.race([writePromise, timeoutPromise]);
          console.log('File saved successfully');
        } catch (writeError) {
          console.error('Error writing file:', writeError);
          this.showStatusMessage('Error saving file', 'error');
          throw writeError;
        }

        // Update file path and dirty state
        editor.filePath = filePath;
        editor.isDirty = false;
        this.updateTabTitle(tabId);

        // Add to recent files
        this.addToRecentFiles(filePath);

        // Show success message
        this.showStatusMessage('File saved successfully', 'success');

        return true;
      } catch (dialogError) {
        console.error('Error showing save dialog:', dialogError);
        this.showStatusMessage('Error showing save dialog', 'error');
        throw dialogError;
      }
    } catch (error) {
      console.error('Error saving file as:', error);
      alert(`Error saving file: ${error.message}`);
      return false;
    }
  }

  // Helper method to show status messages
  showStatusMessage(message, type = 'info') {
    console.log(`Status message: ${message} (${type})`);

    // Get or create status message element
    const statusBar = document.querySelector('.status-left');
    if (!statusBar) return;

    let statusElement = document.getElementById('editor-status-message');
    if (!statusElement) {
      statusElement = document.createElement('span');
      statusElement.id = 'editor-status-message';
      statusBar.appendChild(statusElement);
    }

    // Set message and style based on type
    statusElement.textContent = message;

    // Remove all type classes
    statusElement.classList.remove('status-info', 'status-success', 'status-warning', 'status-error');

    // Add appropriate class
    switch (type) {
      case 'success':
        statusElement.classList.add('status-success');
        statusElement.style.color = '#4CAF50';
        break;
      case 'warning':
        statusElement.classList.add('status-warning');
        statusElement.style.color = '#FF9800';
        break;
      case 'error':
        statusElement.classList.add('status-error');
        statusElement.style.color = '#F44336';
        break;
      default:
        statusElement.classList.add('status-info');
        statusElement.style.color = '#2196F3';
    }

    // Auto-remove after a delay
    setTimeout(() => {
      if (statusElement.parentNode) {
        statusElement.remove();
      }
    }, 3000);
  }

  updateTabTitle(tabId) {
    const editor = this.editors[tabId];
    if (!editor) return;

    const tabElement = this.editorTabs.querySelector(`[data-tab-id="${tabId}"]`);
    if (!tabElement) return;

    const fileName = editor.filePath ? this.getFileName(editor.filePath) : 'Untitled';
    const dirtyIndicator = editor.isDirty ? '*' : '';

    tabElement.querySelector('span').textContent = `${fileName}${dirtyIndicator}`;
  }

  updateStatusBar(position) {
    const lineNumber = position.lineNumber;
    const column = position.column;

    document.getElementById('status-cursor-position').textContent = `Ln ${lineNumber}, Col ${column}`;
  }

  getFileName(filePath) {
    return filePath.split(/[\\/]/).pop();
  }

  getCurrentTheme() {
    const bodyThemeClass = document.body.className.match(/theme-(\w+)/);
    if (bodyThemeClass && bodyThemeClass[1]) {
      switch (bodyThemeClass[1]) {
        case 'dark':
          return 'vs-dark';
        case 'light':
          return 'vs';
        case 'nord':
          return 'vs-dark'; // Use vs-dark as base for nord
        default:
          return 'vs-dark';
      }
    }
    return 'vs-dark'; // Default to dark theme
  }

  setTheme(themeName) {
    // Update Monaco editor theme
    let monacoTheme = 'vs-dark';
    switch (themeName) {
      case 'light':
        monacoTheme = 'vs';
        break;
      case 'dark':
      case 'nord':
        monacoTheme = 'vs-dark';
        break;
    }

    // Update all editor instances
    for (const tabId in this.editors) {
      monaco.editor.setTheme(monacoTheme);
    }
  }

  addToRecentFiles(filePath) {
    // Get recent files from localStorage
    let recentFiles = JSON.parse(localStorage.getItem('recentFiles') || '[]');

    // Remove if already exists
    recentFiles = recentFiles.filter(path => path !== filePath);

    // Add to the beginning
    recentFiles.unshift(filePath);

    // Limit to 10 recent files
    if (recentFiles.length > 10) {
      recentFiles = recentFiles.slice(0, 10);
    }

    // Save back to localStorage
    localStorage.setItem('recentFiles', JSON.stringify(recentFiles));

    // Update UI if needed
    this.updateRecentFilesUI();
  }

  updateRecentFilesUI() {
    const recentFilesContainer = document.getElementById('recent-files');
    if (!recentFilesContainer) return;

    // Get recent files from localStorage
    const recentFiles = JSON.parse(localStorage.getItem('recentFiles') || '[]');

    // Clear container
    recentFilesContainer.innerHTML = '';

    if (recentFiles.length === 0) {
      recentFilesContainer.innerHTML = '<p class="no-recent">No recent files</p>';
      return;
    }

    // Add recent files to UI
    recentFiles.forEach(filePath => {
      const fileName = this.getFileName(filePath);
      const item = document.createElement('div');
      item.className = 'recent-file-item';
      item.innerHTML = `
        <img src="../assets/icons/file-mono.svg" alt="File">
        <span>${fileName}</span>
      `;
      item.addEventListener('click', () => this.openFile(filePath));
      recentFilesContainer.appendChild(item);
    });
  }

  getActiveEditor() {
    if (!this.activeEditor || !this.editors[this.activeEditor]) {
      return null;
    }
    return this.editors[this.activeEditor];
  }

  getActiveEditorContent() {
    const activeEditor = this.getActiveEditor();
    if (!activeEditor) {
      return null;
    }
    return activeEditor.editor.getValue();
  }

  getActiveFilePath() {
    const activeEditor = this.getActiveEditor();
    if (!activeEditor) {
      return null;
    }
    return activeEditor.filePath;
  }

  formatDocument() {
    const activeEditor = this.getActiveEditor();
    if (!activeEditor) {
      return;
    }
    activeEditor.editor.getAction('editor.action.formatDocument').run();
  }

  // Handle file operations
  handleFileRenamed(oldPath, newPath) {
    // Find any tabs with this file open
    for (const tabId in this.editors) {
      const editor = this.editors[tabId];
      if (editor.filePath === oldPath) {
        // Update the file path
        editor.filePath = newPath;
        // Update the tab title
        this.updateTabTitle(tabId);
      }
    }

    // Update recent files
    this.updateRecentFilesAfterRename(oldPath, newPath);
  }

  handleFileDeleted(filePath) {
    // Find any tabs with this file open
    for (const tabId in this.editors) {
      const editor = this.editors[tabId];
      if (editor.filePath === filePath) {
        // Close the tab
        this.closeTab(tabId);
      }
    }

    // Update recent files
    this.updateRecentFilesAfterDelete(filePath);
  }

  updateRecentFilesAfterRename(oldPath, newPath) {
    // Get recent files from localStorage
    let recentFiles = JSON.parse(localStorage.getItem('recentFiles') || '[]');

    // Replace old path with new path
    recentFiles = recentFiles.map(path => path === oldPath ? newPath : path);

    // Save back to localStorage
    localStorage.setItem('recentFiles', JSON.stringify(recentFiles));

    // Update UI
    this.updateRecentFilesUI();
  }

  updateRecentFilesAfterDelete(filePath) {
    // Get recent files from localStorage
    let recentFiles = JSON.parse(localStorage.getItem('recentFiles') || '[]');

    // Remove deleted file
    recentFiles = recentFiles.filter(path => path !== filePath);

    // Save back to localStorage
    localStorage.setItem('recentFiles', JSON.stringify(recentFiles));

    // Update UI
    this.updateRecentFilesUI();
  }

  // Debugging support
  toggleBreakpoint(filePath, lineNumber) {
    // Call the debugger to toggle the breakpoint
    if (debuggerManager) {
      debuggerManager.toggleBreakpoint(filePath, lineNumber);
    }
  }

  updateBreakpoints(filePath, lineNumbers) {
    // Find the editor for this file
    for (const tabId in this.editors) {
      const editor = this.editors[tabId];
      if (editor.filePath === filePath) {
        // Clear existing breakpoint decorations
        if (editor.breakpointDecorations) {
          editor.editor.deltaDecorations(editor.breakpointDecorations, []);
        }

        // Add new breakpoint decorations
        const decorations = lineNumbers.map(line => ({
          range: new monaco.Range(line, 1, line, 1),
          options: {
            isWholeLine: false,
            glyphMarginClassName: 'debug-breakpoint'
          }
        }));

        editor.breakpointDecorations = editor.editor.deltaDecorations([], decorations);
        break;
      }
    }
  }

  highlightDebugLine(filePath, lineNumber) {
    // Find the editor for this file
    for (const tabId in this.editors) {
      const editor = this.editors[tabId];
      if (editor.filePath === filePath) {
        // Clear existing debug line decorations
        this.clearDebugDecorations();

        // Add new debug line decoration
        const decorations = [{
          range: new monaco.Range(lineNumber, 1, lineNumber, 1),
          options: {
            isWholeLine: true,
            className: 'debug-current-line',
            glyphMarginClassName: 'debug-current-line-glyph'
          }
        }];

        editor.debugLineDecorations = editor.editor.deltaDecorations([], decorations);

        // Reveal the line
        editor.editor.revealLineInCenter(lineNumber);
        break;
      }
    }
  }

  clearDebugDecorations() {
    // Clear debug line decorations in all editors
    for (const tabId in this.editors) {
      const editor = this.editors[tabId];
      if (editor.debugLineDecorations) {
        editor.editor.deltaDecorations(editor.debugLineDecorations, []);
        editor.debugLineDecorations = null;
      }
    }
  }

  goToLine(lineNumber) {
    const activeEditor = this.getActiveEditor();
    if (activeEditor) {
      activeEditor.editor.revealLineInCenter(lineNumber);

      // Set cursor position
      activeEditor.editor.setPosition({
        lineNumber: lineNumber,
        column: 1
      });

      // Focus the editor
      activeEditor.editor.focus();
    }
  }

  /**
   * Highlight the current line in the editor
   * @param {string} tabId The tab ID
   */
  highlightCurrentLine(tabId) {
    const editor = this.editors[tabId];
    if (!editor || !editor.editor) {
      return;
    }

    try {
      // Get current position
      const position = editor.editor.getPosition();
      if (!position) {
        return;
      }

      // Clear existing decorations
      if (editor.currentLineDecorations) {
        editor.editor.deltaDecorations(editor.currentLineDecorations, []);
      }

      // Create decoration for current line
      const decorations = [{
        range: new monaco.Range(position.lineNumber, 1, position.lineNumber, 1),
        options: {
          isWholeLine: true,
          className: 'current-line',
          stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
        }
      }];

      // Apply decorations
      editor.currentLineDecorations = editor.editor.deltaDecorations([], decorations);
    } catch (error) {
      console.error('Error highlighting current line:', error);
    }
  }

  /**
   * Set diagnostics for a specific file
   * @param {string} filePath The file path
   * @param {Array} diagnostics Array of diagnostic objects
   */
  setDiagnostics(filePath, diagnostics) {
    // Find the editor for this file
    for (const tabId in this.editors) {
      const editor = this.editors[tabId];
      if (editor.filePath === filePath && editor.diagnosticHighlighter) {
        editor.diagnosticHighlighter.setDiagnostics(diagnostics);
        break;
      }
    }
  }

  /**
   * Clear all diagnostics for a specific file
   * @param {string} filePath The file path
   */
  clearDiagnostics(filePath) {
    // Find the editor for this file
    for (const tabId in this.editors) {
      const editor = this.editors[tabId];
      if (editor.filePath === filePath && editor.diagnosticHighlighter) {
        editor.diagnosticHighlighter.clearDiagnostics();
        break;
      }
    }
  }
}

// Initialize the editor manager when the page loads
let editorManager;
document.addEventListener('DOMContentLoaded', () => {
  // Wait for Monaco to be loaded
  if (typeof monaco !== 'undefined') {
    editorManager = new EditorManager();

    // Make it globally available
    window.editorManager = editorManager;

    // Update recent files UI
    editorManager.updateRecentFilesUI();
  } else {
    console.error('Monaco editor not loaded');
  }
});
