// Snippet Manager for Mono Editor
// This script provides functionality for managing code snippets

class SnippetManager {
  constructor() {
    this.snippets = {};
    this.categories = [];
    this.initialized = false;

    // Initialize the snippet manager
    this.initialize();
  }

  /**
   * Initialize the snippet manager
   */
  initialize() {
    if (this.initialized) return;

    console.log('Initializing snippet manager...');

    // Load snippets from storage
    this.loadSnippets();

    // Register Monaco completions when Monaco is ready
    if (typeof monaco !== 'undefined') {
      this.registerCompletionProvider();
    } else {
      window.addEventListener('monaco-ready', () => {
        this.registerCompletionProvider();
      });
    }

    // Set up UI
    this.setupUI();

    this.initialized = true;
  }

  /**
   * Load snippets from storage
   */
  loadSnippets() {
    try {
      // Try to load snippets from localStorage
      const savedSnippets = localStorage.getItem('mono-snippets');

      if (savedSnippets) {
        this.snippets = JSON.parse(savedSnippets);
        console.log(`Loaded ${Object.keys(this.snippets).length} snippets from storage`);
      } else {
        // Load default snippets
        this.loadDefaultSnippets();
      }

      // Extract categories
      this.updateCategories();
    } catch (error) {
      console.error('Error loading snippets:', error);

      // Load default snippets as fallback
      this.loadDefaultSnippets();
    }
  }

  /**
   * Load default snippets
   */
  loadDefaultSnippets() {
    console.log('Loading default snippets...');

    this.snippets = {
      'component': {
        prefix: 'component',
        name: 'Component Template',
        description: 'Create a new Mono component',
        category: 'Mono',
        body: [
          'component ${1:ComponentName} {',
          '  prop ${2:propName}: ${3:String} = ${4:"Default value"}',
          '  ',
          '  state ${5:stateName}: ${6:Boolean} = ${7:false}',
          '  ',
          '  on init {',
          '    // Initialization code',
          '    ${8}',
          '  }',
          '  ',
          '  render {',
          '    <div class="${9:component-class}">',
          '      ${10}',
          '    </div>',
          '  }',
          '}'
        ].join('\n')
      },
      'frame': {
        prefix: 'frame',
        name: 'Frame Template',
        description: 'Create a new Mono frame',
        category: 'Mono',
        body: [
          'frame ${1:FrameName} {',
          '  // Frame properties',
          '  title = "${2:Frame Title}"',
          '  width = ${3:800}',
          '  height = ${4:600}',
          '  ',
          '  // Frame content',
          '  content {',
          '    ${5:<ComponentName />}',
          '  }',
          '  ',
          '  // Frame lifecycle hooks',
          '  on load {',
          '    // Code to run when frame loads',
          '    ${6}',
          '  }',
          '  ',
          '  on unload {',
          '    // Code to run when frame unloads',
          '    ${7}',
          '  }',
          '}'
        ].join('\n')
      },
      'event-handler': {
        prefix: 'on',
        name: 'Event Handler',
        description: 'Create an event handler',
        category: 'Mono',
        body: [
          'on ${1:event} {',
          '  ${2:// Event handler code}',
          '}'
        ].join('\n')
      },
      'if-statement': {
        prefix: 'if',
        name: 'If Statement',
        description: 'Create an if statement',
        category: 'Control Flow',
        body: [
          'if (${1:condition}) {',
          '  ${2:// Code to execute if condition is true}',
          '}'
        ].join('\n')
      },
      'if-else-statement': {
        prefix: 'ifelse',
        name: 'If-Else Statement',
        description: 'Create an if-else statement',
        category: 'Control Flow',
        body: [
          'if (${1:condition}) {',
          '  ${2:// Code to execute if condition is true}',
          '} else {',
          '  ${3:// Code to execute if condition is false}',
          '}'
        ].join('\n')
      },
      'for-loop': {
        prefix: 'for',
        name: 'For Loop',
        description: 'Create a for loop',
        category: 'Control Flow',
        body: [
          'for (${1:i} = 0; ${1:i} < ${2:count}; ${1:i}++) {',
          '  ${3:// Loop body}',
          '}'
        ].join('\n')
      },
      'while-loop': {
        prefix: 'while',
        name: 'While Loop',
        description: 'Create a while loop',
        category: 'Control Flow',
        body: [
          'while (${1:condition}) {',
          '  ${2:// Loop body}',
          '}'
        ].join('\n')
      },
      'function': {
        prefix: 'func',
        name: 'Function',
        description: 'Create a function',
        category: 'Functions',
        body: [
          'function ${1:functionName}(${2:parameters}) {',
          '  ${3:// Function body}',
          '  return ${4:result}',
          '}'
        ].join('\n')
      },
      'array': {
        prefix: 'array',
        name: 'Array',
        description: 'Create an array',
        category: 'Data Structures',
        body: 'array ${1:arrayName} = [${2:items}]'
      },
      'dictionary': {
        prefix: 'dict',
        name: 'Dictionary',
        description: 'Create a dictionary',
        category: 'Data Structures',
        body: [
          'dictionary ${1:dictName} = {',
          '  "${2:key}": ${3:value},',
          '  "${4:key}": ${5:value}',
          '}'
        ].join('\n')
      }
    };

    // Save default snippets to storage
    this.saveSnippets();

    // Extract categories
    this.updateCategories();
  }

  /**
   * Update categories based on snippets
   */
  updateCategories() {
    const categoriesSet = new Set();

    // Extract unique categories
    Object.values(this.snippets).forEach(snippet => {
      if (snippet.category) {
        categoriesSet.add(snippet.category);
      }
    });

    // Convert to array and sort
    this.categories = Array.from(categoriesSet).sort();

    console.log(`Snippet categories: ${this.categories.join(', ')}`);
  }

  /**
   * Save snippets to storage
   */
  saveSnippets() {
    try {
      localStorage.setItem('mono-snippets', JSON.stringify(this.snippets));
      console.log(`Saved ${Object.keys(this.snippets).length} snippets to storage`);
    } catch (error) {
      console.error('Error saving snippets:', error);
    }
  }

  /**
   * Register completion provider with Monaco
   */
  registerCompletionProvider() {
    if (!monaco || !monaco.languages) {
      console.error('Monaco not available for registering snippet completion provider');
      return;
    }

    console.log('Registering snippet completion provider...');

    // Register completion provider for Mono language
    monaco.languages.registerCompletionItemProvider('mono', {
      provideCompletionItems: (model, position) => {
        // Get the current line up to the cursor
        const textUntilPosition = model.getValueInRange({
          startLineNumber: position.lineNumber,
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column
        });

        // Create completion items for snippets
        const suggestions = Object.values(this.snippets).map(snippet => {
          return {
            label: snippet.prefix,
            kind: monaco.languages.CompletionItemKind.Snippet,
            documentation: snippet.description,
            insertText: snippet.body,
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            detail: `${snippet.name} (${snippet.category})`
          };
        });

        return { suggestions };
      }
    });

    console.log('Snippet completion provider registered');
  }

  /**
   * Set up the UI for snippet management
   */
  setupUI() {
    // Add snippet manager button to the sidebar
    const sidebarActions = document.querySelector('.sidebar-actions');

    if (sidebarActions) {
      const snippetButton = document.createElement('button');
      snippetButton.id = 'snippet-manager-btn';
      snippetButton.title = 'Snippet Manager';
      snippetButton.innerHTML = '<i class="icon icon-snippet"></i>';
      snippetButton.addEventListener('click', () => this.openSnippetManager());

      sidebarActions.appendChild(snippetButton);
    }

    // Create snippet manager dialog
    this.createSnippetManagerDialog();
  }

  /**
   * Create the snippet manager dialog
   */
  createSnippetManagerDialog() {
    // Create dialog element
    const dialog = document.createElement('div');
    dialog.id = 'snippet-manager-dialog';
    dialog.className = 'dialog';
    dialog.style.display = 'none';

    // Create dialog content
    dialog.innerHTML = `
      <div class="dialog-header">
        <h2>Snippet Manager</h2>
        <button class="dialog-close-btn">&times;</button>
      </div>
      <div class="dialog-content">
        <div class="snippet-manager-container">
          <div class="snippet-list-container">
            <div class="snippet-list-header">
              <h3>Snippets</h3>
              <div class="snippet-list-actions">
                <button id="add-snippet-btn" class="btn btn-sm btn-primary">Add New</button>
                <button id="import-snippets-btn" class="btn btn-sm btn-secondary">Import</button>
                <button id="export-snippets-btn" class="btn btn-sm btn-secondary">Export</button>
              </div>
            </div>
            <div class="snippet-categories">
              <ul id="snippet-categories-list"></ul>
            </div>
            <div class="snippet-list">
              <ul id="snippet-list"></ul>
            </div>
          </div>
          <div class="snippet-editor-container">
            <div class="snippet-editor-header">
              <h3>Edit Snippet</h3>
            </div>
            <div class="snippet-editor-form">
              <div class="form-group">
                <label for="snippet-name">Name</label>
                <input type="text" id="snippet-name" class="form-control">
              </div>
              <div class="form-group">
                <label for="snippet-prefix">Prefix</label>
                <input type="text" id="snippet-prefix" class="form-control">
              </div>
              <div class="form-group">
                <label for="snippet-category">Category</label>
                <input type="text" id="snippet-category" class="form-control" list="snippet-categories">
                <datalist id="snippet-categories"></datalist>
              </div>
              <div class="form-group">
                <label for="snippet-description">Description</label>
                <input type="text" id="snippet-description" class="form-control">
              </div>
              <div class="form-group">
                <label for="snippet-body">Body</label>
                <div id="snippet-body-editor" class="snippet-body-editor"></div>
              </div>
            </div>
            <div class="snippet-editor-actions">
              <button id="save-snippet-btn" class="btn btn-primary">Save</button>
              <button id="delete-snippet-btn" class="btn btn-danger">Delete</button>
            </div>
          </div>
        </div>
      </div>
    `;

    // Add dialog to the page
    const dialogOverlay = document.getElementById('dialog-overlay');
    if (dialogOverlay) {
      dialogOverlay.appendChild(dialog);

      // Set up event listeners
      this.setupDialogEventListeners(dialog);
    } else {
      console.error('Dialog overlay not found');
    }
  }

  /**
   * Set up event listeners for the snippet manager dialog
   * @param {HTMLElement} dialog - The dialog element
   */
  setupDialogEventListeners(dialog) {
    // Close button
    const closeBtn = dialog.querySelector('.dialog-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.closeSnippetManager());
    }

    // Add snippet button
    const addSnippetBtn = dialog.querySelector('#add-snippet-btn');
    if (addSnippetBtn) {
      addSnippetBtn.addEventListener('click', () => this.createNewSnippet());
    }

    // Save snippet button
    const saveSnippetBtn = dialog.querySelector('#save-snippet-btn');
    if (saveSnippetBtn) {
      saveSnippetBtn.addEventListener('click', () => this.saveCurrentSnippet());
    }

    // Delete snippet button
    const deleteSnippetBtn = dialog.querySelector('#delete-snippet-btn');
    if (deleteSnippetBtn) {
      deleteSnippetBtn.addEventListener('click', () => this.deleteCurrentSnippet());
    }

    // Import button
    const importBtn = dialog.querySelector('#import-snippets-btn');
    if (importBtn) {
      importBtn.addEventListener('click', () => this.importSnippets());
    }

    // Export button
    const exportBtn = dialog.querySelector('#export-snippets-btn');
    if (exportBtn) {
      exportBtn.addEventListener('click', () => this.exportSnippets());
    }

    // Set up keyboard shortcuts
    document.addEventListener('keydown', (event) => {
      // Only process shortcuts when the snippet manager is open
      if (dialog.style.display !== 'block') return;

      // Ctrl+S or Cmd+S to save
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        this.saveCurrentSnippet();
      }

      // Ctrl+N or Cmd+N to create new snippet
      if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
        event.preventDefault();
        this.createNewSnippet();
      }

      // Delete or Backspace to delete snippet (with confirmation)
      if (event.key === 'Delete' && event.ctrlKey) {
        event.preventDefault();
        this.deleteCurrentSnippet();
      }

      // Escape to close
      if (event.key === 'Escape') {
        event.preventDefault();
        this.closeSnippetManager();
      }
    });
  }

  /**
   * Open the snippet manager dialog
   */
  openSnippetManager() {
    console.log('Opening snippet manager...');

    // Show dialog overlay
    const dialogOverlay = document.getElementById('dialog-overlay');
    if (dialogOverlay) {
      dialogOverlay.style.display = 'flex';

      // Show snippet manager dialog
      const dialog = document.getElementById('snippet-manager-dialog');
      if (dialog) {
        dialog.style.display = 'block';

        // Populate categories and snippets
        this.populateCategories();
        this.populateSnippets('all');

        // Create snippet body editor if not already created
        this.createSnippetBodyEditor();
      }
    }
  }

  /**
   * Close the snippet manager dialog
   */
  closeSnippetManager() {
    console.log('Closing snippet manager...');

    // Hide dialog overlay
    const dialogOverlay = document.getElementById('dialog-overlay');
    if (dialogOverlay) {
      dialogOverlay.style.display = 'none';

      // Hide snippet manager dialog
      const dialog = document.getElementById('snippet-manager-dialog');
      if (dialog) {
        dialog.style.display = 'none';
      }
    }
  }

  /**
   * Create a new snippet
   */
  createNewSnippet() {
    console.log('Creating new snippet...');

    // Clear form fields
    document.getElementById('snippet-name').value = '';
    document.getElementById('snippet-prefix').value = '';
    document.getElementById('snippet-category').value = 'Mono';
    document.getElementById('snippet-description').value = '';

    // Set default body
    if (this.snippetBodyEditor) {
      this.snippetBodyEditor.setValue('// Enter snippet code here');
    }

    // Set current snippet ID
    this.currentSnippetId = 'new-snippet-' + Date.now();
  }

  /**
   * Save the current snippet
   */
  saveCurrentSnippet() {
    console.log('Saving snippet...');

    // Get form values
    const name = document.getElementById('snippet-name').value;
    const prefix = document.getElementById('snippet-prefix').value;
    const category = document.getElementById('snippet-category').value;
    const description = document.getElementById('snippet-description').value;
    const body = this.snippetBodyEditor ? this.snippetBodyEditor.getValue() : '';

    // Validate form
    if (!name || !prefix || !category || !body) {
      alert('Please fill in all fields');
      return;
    }

    // Create snippet object
    const snippet = {
      name,
      prefix,
      category,
      description,
      body
    };

    // Add or update snippet
    this.snippets[prefix] = snippet;

    // Save snippets to storage
    this.saveSnippets();

    // Update categories
    this.updateCategories();

    // Refresh UI
    this.populateCategories();
    this.populateSnippets(category);

    // Re-register completion provider
    this.registerCompletionProvider();

    // Show success message
    alert('Snippet saved successfully');
  }

  /**
   * Delete the current snippet
   */
  deleteCurrentSnippet() {
    console.log('Deleting snippet...');

    // Get current prefix
    const prefix = document.getElementById('snippet-prefix').value;

    // Confirm deletion
    if (!confirm(`Are you sure you want to delete the snippet "${prefix}"?`)) {
      return;
    }

    // Delete snippet
    if (this.snippets[prefix]) {
      delete this.snippets[prefix];

      // Save snippets to storage
      this.saveSnippets();

      // Update categories
      this.updateCategories();

      // Refresh UI
      this.populateCategories();
      this.populateSnippets('all');

      // Re-register completion provider
      this.registerCompletionProvider();

      // Show success message
      alert('Snippet deleted successfully');

      // Clear form
      this.createNewSnippet();
    }
  }

  /**
   * Create the snippet body editor
   */
  createSnippetBodyEditor() {
    if (this.snippetBodyEditor) {
      return;
    }

    // Check if Monaco is available
    if (!monaco) {
      console.error('Monaco not available for creating snippet body editor');
      return;
    }

    // Create editor
    const editorContainer = document.getElementById('snippet-body-editor');
    if (editorContainer) {
      this.snippetBodyEditor = monaco.editor.create(editorContainer, {
        value: '// Enter snippet code here',
        language: 'mono',
        theme: 'vs-dark',
        minimap: { enabled: false },
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        automaticLayout: true
      });

      console.log('Snippet body editor created');
    }
  }

  /**
   * Populate the categories list
   */
  populateCategories() {
    const categoriesList = document.getElementById('snippet-categories-list');
    const categoriesDatalist = document.getElementById('snippet-categories');

    if (!categoriesList || !categoriesDatalist) {
      return;
    }

    // Clear existing items
    categoriesList.innerHTML = '';
    categoriesDatalist.innerHTML = '';

    // Add "All" category
    const allItem = document.createElement('li');
    allItem.textContent = 'All';
    allItem.dataset.category = 'all';
    allItem.classList.add('active');
    allItem.addEventListener('click', () => {
      // Deactivate all categories
      categoriesList.querySelectorAll('li').forEach(item => {
        item.classList.remove('active');
      });

      // Activate this category
      allItem.classList.add('active');

      // Populate snippets for this category
      this.populateSnippets('all');
    });
    categoriesList.appendChild(allItem);

    // Add categories
    this.categories.forEach(category => {
      // Add to categories list
      const item = document.createElement('li');
      item.textContent = category;
      item.dataset.category = category;
      item.addEventListener('click', () => {
        // Deactivate all categories
        categoriesList.querySelectorAll('li').forEach(item => {
          item.classList.remove('active');
        });

        // Activate this category
        item.classList.add('active');

        // Populate snippets for this category
        this.populateSnippets(category);
      });
      categoriesList.appendChild(item);

      // Add to datalist
      const option = document.createElement('option');
      option.value = category;
      categoriesDatalist.appendChild(option);
    });
  }

  /**
   * Populate the snippets list for a category
   * @param {string} category - The category to show, or 'all' for all categories
   */
  populateSnippets(category) {
    const snippetsList = document.getElementById('snippet-list');

    if (!snippetsList) {
      return;
    }

    // Clear existing items
    snippetsList.innerHTML = '';

    // Filter snippets by category
    const filteredSnippets = Object.values(this.snippets).filter(snippet => {
      return category === 'all' || snippet.category === category;
    });

    // Sort snippets by name
    filteredSnippets.sort((a, b) => a.name.localeCompare(b.name));

    // Add snippets
    filteredSnippets.forEach(snippet => {
      const item = document.createElement('li');
      item.textContent = snippet.name;
      item.title = snippet.description;
      item.dataset.prefix = snippet.prefix;
      item.addEventListener('click', () => {
        // Load snippet into editor
        this.loadSnippetIntoEditor(snippet);
      });
      snippetsList.appendChild(item);
    });
  }

  /**
   * Load a snippet into the editor
   * @param {Object} snippet - The snippet to load
   */
  loadSnippetIntoEditor(snippet) {
    // Set form values
    document.getElementById('snippet-name').value = snippet.name;
    document.getElementById('snippet-prefix').value = snippet.prefix;
    document.getElementById('snippet-category').value = snippet.category;
    document.getElementById('snippet-description').value = snippet.description;

    // Set body
    if (this.snippetBodyEditor) {
      this.snippetBodyEditor.setValue(snippet.body);
    }

    // Set current snippet ID
    this.currentSnippetId = snippet.prefix;
  }

  /**
   * Get a snippet by prefix
   * @param {string} prefix - The snippet prefix
   * @returns {Object|null} The snippet object or null if not found
   */
  getSnippet(prefix) {
    return this.snippets[prefix] || null;
  }

  /**
   * Get all snippets
   * @returns {Object} All snippets
   */
  getAllSnippets() {
    return { ...this.snippets };
  }

  /**
   * Get snippets by category
   * @param {string} category - The category to filter by
   * @returns {Array} Array of snippets in the category
   */
  getSnippetsByCategory(category) {
    return Object.values(this.snippets).filter(snippet =>
      snippet.category === category
    );
  }

  /**
   * Import snippets from a JSON file
   */
  importSnippets() {
    console.log('Importing snippets...');

    // Create a file input element
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);

    // Handle file selection
    fileInput.addEventListener('change', (event) => {
      const file = event.target.files[0];
      if (!file) {
        document.body.removeChild(fileInput);
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const importedSnippets = JSON.parse(e.target.result);

          // Validate imported snippets
          if (typeof importedSnippets !== 'object') {
            throw new Error('Invalid snippet format');
          }

          // Count valid snippets
          let validCount = 0;

          // Process each imported snippet
          for (const [key, snippet] of Object.entries(importedSnippets)) {
            // Validate snippet structure
            if (!snippet.name || !snippet.prefix || !snippet.category || !snippet.body) {
              console.warn(`Skipping invalid snippet: ${key}`);
              continue;
            }

            // Add the snippet
            this.snippets[snippet.prefix] = snippet;
            validCount++;
          }

          // Save snippets to storage
          this.saveSnippets();

          // Update categories
          this.updateCategories();

          // Refresh UI
          this.populateCategories();
          this.populateSnippets('all');

          // Re-register completion provider
          this.registerCompletionProvider();

          // Show success message
          alert(`Successfully imported ${validCount} snippets`);
        } catch (error) {
          console.error('Error importing snippets:', error);
          alert(`Error importing snippets: ${error.message}`);
        } finally {
          document.body.removeChild(fileInput);
        }
      };

      reader.onerror = () => {
        console.error('Error reading file');
        alert('Error reading file');
        document.body.removeChild(fileInput);
      };

      reader.readAsText(file);
    });

    // Trigger file selection
    fileInput.click();
  }

  /**
   * Export snippets to a JSON file
   */
  exportSnippets() {
    console.log('Exporting snippets...');

    try {
      // Convert snippets to JSON
      const snippetsJson = JSON.stringify(this.snippets, null, 2);

      // Create a blob
      const blob = new Blob([snippetsJson], { type: 'application/json' });

      // Create a download link
      const downloadLink = document.createElement('a');
      downloadLink.href = URL.createObjectURL(blob);
      downloadLink.download = 'mono-snippets.json';
      downloadLink.style.display = 'none';
      document.body.appendChild(downloadLink);

      // Trigger download
      downloadLink.click();

      // Clean up
      setTimeout(() => {
        URL.revokeObjectURL(downloadLink.href);
        document.body.removeChild(downloadLink);
      }, 100);

      // Show success message
      alert(`Successfully exported ${Object.keys(this.snippets).length} snippets`);
    } catch (error) {
      console.error('Error exporting snippets:', error);
      alert(`Error exporting snippets: ${error.message}`);
    }
  }

  /**
   * Register keyboard shortcuts for the editor
   */
  registerEditorShortcuts() {
    // Register keyboard shortcuts for the editor
    if (typeof monaco !== 'undefined' && monaco.editor) {
      // Add action for inserting snippets
      monaco.editor.registerCommand('mono.insertSnippet', (accessor, ...args) => {
        const editor = monaco.editor.getActiveEditor();
        if (!editor) return;

        const snippetPrefix = args[0];
        const snippet = this.getSnippet(snippetPrefix);

        if (snippet) {
          // Insert the snippet at the current position
          editor.trigger('keyboard', 'type', { text: snippet.body });
        }
      });

      // Add keyboard shortcut for opening snippet manager
      monaco.editor.addKeybindingRule({
        keybinding: monaco.KeyMod.CtrlCmd | monaco.KeyMod.Alt | monaco.KeyCode.KeyS,
        command: 'mono.openSnippetManager',
        when: 'editorTextFocus'
      });

      // Register command for opening snippet manager
      monaco.editor.registerCommand('mono.openSnippetManager', () => {
        this.openSnippetManager();
      });

      console.log('Registered editor shortcuts for snippets');
    }
  }
}

// Create a singleton instance
const snippetManager = new SnippetManager();

// Export the snippet manager
window.snippetManager = snippetManager;
