// Theme Editor for Mono Editor

/**
 * Theme Editor class for customizing editor themes
 */
class ThemeEditor {
  constructor() {
    this.editorElement = null;
    this.currentTheme = null;
    this.themes = [];
    this.isVisible = false;
    this.unsavedChanges = false;
    
    // Default color categories
    this.colorCategories = [
      {
        name: 'Base Colors',
        description: 'Primary colors used throughout the editor',
        colors: [
          { id: 'background-color', name: 'Background', description: 'Main background color' },
          { id: 'foreground-color', name: 'Foreground', description: 'Main text color' },
          { id: 'accent-color', name: 'Accent', description: 'Highlight and accent color' },
          { id: 'secondary-color', name: 'Secondary', description: 'Secondary accent color' }
        ]
      },
      {
        name: 'UI Elements',
        description: 'Colors for UI components',
        colors: [
          { id: 'panel-background', name: 'Panel Background', description: 'Background color for panels' },
          { id: 'panel-header-background', name: 'Panel Header', description: 'Background color for panel headers' },
          { id: 'panel-header-foreground', name: 'Panel Header Text', description: 'Text color for panel headers' },
          { id: 'border-color', name: 'Border', description: 'Color for borders and dividers' }
        ]
      },
      {
        name: 'Editor',
        description: 'Colors for the code editor',
        colors: [
          { id: 'editor-background', name: 'Editor Background', description: 'Background color for the editor' },
          { id: 'editor-foreground', name: 'Editor Text', description: 'Text color for the editor' },
          { id: 'editor-line-number', name: 'Line Numbers', description: 'Color for line numbers' },
          { id: 'editor-cursor', name: 'Cursor', description: 'Color for the cursor' },
          { id: 'editor-selection-background', name: 'Selection Background', description: 'Background color for selected text' }
        ]
      },
      {
        name: 'Syntax Highlighting',
        description: 'Colors for syntax highlighting',
        colors: [
          { id: 'syntax-keyword', name: 'Keywords', description: 'Color for language keywords' },
          { id: 'syntax-string', name: 'Strings', description: 'Color for string literals' },
          { id: 'syntax-number', name: 'Numbers', description: 'Color for numeric literals' },
          { id: 'syntax-comment', name: 'Comments', description: 'Color for comments' },
          { id: 'syntax-function', name: 'Functions', description: 'Color for function names' },
          { id: 'syntax-variable', name: 'Variables', description: 'Color for variables' },
          { id: 'syntax-type', name: 'Types', description: 'Color for types and classes' }
        ]
      }
    ];
    
    // Initialize the theme editor when the DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initialize());
    } else {
      this.initialize();
    }
  }
  
  /**
   * Initialize the theme editor
   */
  initialize() {
    console.log('Initializing Theme Editor...');
    
    // Load themes
    this.loadThemes();
    
    // Create theme editor UI if it doesn't exist
    this.createThemeEditorUI();
    
    // Add event listeners
    this.addEventListeners();
    
    console.log('Theme Editor initialized');
  }
  
  /**
   * Load themes from local storage and defaults
   */
  loadThemes() {
    try {
      // Default themes
      this.themes = [
        {
          id: 'dark',
          name: 'Dark',
          description: 'Default dark theme',
          isBuiltin: true,
          colors: {
            'background-color': '#1e1e1e',
            'foreground-color': '#d4d4d4',
            'accent-color': '#007acc',
            'secondary-color': '#6a9955',
            'panel-background': '#252526',
            'panel-header-background': '#333333',
            'panel-header-foreground': '#cccccc',
            'border-color': '#454545',
            'editor-background': '#1e1e1e',
            'editor-foreground': '#d4d4d4',
            'editor-line-number': '#858585',
            'editor-cursor': '#a6a6a6',
            'editor-selection-background': '#264f78',
            'syntax-keyword': '#569cd6',
            'syntax-string': '#ce9178',
            'syntax-number': '#b5cea8',
            'syntax-comment': '#6a9955',
            'syntax-function': '#dcdcaa',
            'syntax-variable': '#9cdcfe',
            'syntax-type': '#4ec9b0'
          }
        },
        {
          id: 'light',
          name: 'Light',
          description: 'Default light theme',
          isBuiltin: true,
          colors: {
            'background-color': '#ffffff',
            'foreground-color': '#333333',
            'accent-color': '#0078d7',
            'secondary-color': '#008000',
            'panel-background': '#f3f3f3',
            'panel-header-background': '#e7e7e7',
            'panel-header-foreground': '#333333',
            'border-color': '#cccccc',
            'editor-background': '#ffffff',
            'editor-foreground': '#333333',
            'editor-line-number': '#999999',
            'editor-cursor': '#333333',
            'editor-selection-background': '#add6ff',
            'syntax-keyword': '#0000ff',
            'syntax-string': '#a31515',
            'syntax-number': '#098658',
            'syntax-comment': '#008000',
            'syntax-function': '#795e26',
            'syntax-variable': '#001080',
            'syntax-type': '#267f99'
          }
        },
        {
          id: 'nord',
          name: 'Nord',
          description: 'Arctic-inspired theme',
          isBuiltin: true,
          colors: {
            'background-color': '#2e3440',
            'foreground-color': '#d8dee9',
            'accent-color': '#88c0d0',
            'secondary-color': '#a3be8c',
            'panel-background': '#3b4252',
            'panel-header-background': '#434c5e',
            'panel-header-foreground': '#e5e9f0',
            'border-color': '#4c566a',
            'editor-background': '#2e3440',
            'editor-foreground': '#d8dee9',
            'editor-line-number': '#4c566a',
            'editor-cursor': '#d8dee9',
            'editor-selection-background': '#434c5e',
            'syntax-keyword': '#81a1c1',
            'syntax-string': '#a3be8c',
            'syntax-number': '#b48ead',
            'syntax-comment': '#616e88',
            'syntax-function': '#88c0d0',
            'syntax-variable': '#d8dee9',
            'syntax-type': '#8fbcbb'
          }
        }
      ];
      
      // Load custom themes from local storage
      const customThemes = JSON.parse(localStorage.getItem('mono-custom-themes') || '[]');
      this.themes = [...this.themes, ...customThemes];
      
      // Set current theme
      const currentThemeId = localStorage.getItem('mono-current-theme') || 'dark';
      this.currentTheme = this.themes.find(theme => theme.id === currentThemeId) || this.themes[0];
      
      console.log(`Loaded ${this.themes.length} themes, current theme: ${this.currentTheme.name}`);
    } catch (error) {
      console.error('Error loading themes:', error);
      
      // Fallback to default themes
      this.themes = [
        {
          id: 'dark',
          name: 'Dark',
          description: 'Default dark theme',
          isBuiltin: true,
          colors: {
            'background-color': '#1e1e1e',
            'foreground-color': '#d4d4d4',
            'accent-color': '#007acc'
            // ... other colors would be here
          }
        }
      ];
      this.currentTheme = this.themes[0];
    }
  }
  
  /**
   * Save themes to local storage
   */
  saveThemes() {
    try {
      // Only save custom themes
      const customThemes = this.themes.filter(theme => !theme.isBuiltin);
      localStorage.setItem('mono-custom-themes', JSON.stringify(customThemes));
      
      // Save current theme
      localStorage.setItem('mono-current-theme', this.currentTheme.id);
      
      console.log('Themes saved to local storage');
    } catch (error) {
      console.error('Error saving themes:', error);
    }
  }
  
  /**
   * Create the theme editor UI
   */
  createThemeEditorUI() {
    // Check if theme editor already exists
    const existingEditor = document.getElementById('theme-editor');
    if (existingEditor) {
      this.editorElement = existingEditor;
      return;
    }
    
    // Create theme editor container
    this.editorElement = document.createElement('div');
    this.editorElement.id = 'theme-editor';
    this.editorElement.className = 'theme-editor';
    this.editorElement.style.display = 'none'; // Hidden by default
    
    // Create theme editor header
    const header = document.createElement('div');
    header.className = 'theme-editor-header';
    header.innerHTML = `
      <h2>Theme Editor</h2>
      <div class="theme-editor-controls">
        <select id="theme-selector"></select>
        <button id="new-theme-btn" class="new-theme-btn">New Theme</button>
        <button id="save-theme-btn" class="save-theme-btn">Save</button>
        <button id="export-theme-btn" class="export-theme-btn">Export</button>
        <button id="import-theme-btn" class="import-theme-btn">Import</button>
        <button id="close-theme-editor-btn" class="close-theme-editor-btn">×</button>
      </div>
    `;
    
    // Create theme editor content
    const content = document.createElement('div');
    content.className = 'theme-editor-content';
    
    // Create theme preview
    const preview = document.createElement('div');
    preview.className = 'theme-preview';
    preview.innerHTML = `
      <h3>Preview</h3>
      <div class="preview-container">
        <div class="preview-editor">
          <div class="preview-line-numbers">
            <span>1</span>
            <span>2</span>
            <span>3</span>
            <span>4</span>
            <span>5</span>
          </div>
          <div class="preview-code">
            <pre><code><span class="syntax-keyword">component</span> <span class="syntax-type">Button</span> {
  <span class="syntax-keyword">state</span> {
    <span class="syntax-variable">text</span>: <span class="syntax-type">string</span> = <span class="syntax-string">"Click me"</span>;
    <span class="syntax-variable">clicked</span>: <span class="syntax-type">boolean</span> = <span class="syntax-keyword">false</span>;
  }

  <span class="syntax-keyword">function</span> <span class="syntax-function">handleClick</span>() {
    <span class="syntax-comment">// Toggle the clicked state</span>
    <span class="syntax-keyword">this</span>.<span class="syntax-variable">clicked</span> = !<span class="syntax-keyword">this</span>.<span class="syntax-variable">clicked</span>;
  }

  <span class="syntax-keyword">render</span> {
    <span class="syntax-keyword">&lt;button</span> <span class="syntax-variable">onClick</span>={<span class="syntax-keyword">this</span>.<span class="syntax-function">handleClick</span>}>
      {<span class="syntax-keyword">this</span>.<span class="syntax-variable">clicked</span> ? <span class="syntax-string">"Clicked!"</span> : <span class="syntax-keyword">this</span>.<span class="syntax-variable">text</span>}
    <span class="syntax-keyword">&lt;/button></span>
  }
}</code></pre>
          </div>
        </div>
      </div>
    `;
    
    // Create color editor
    const colorEditor = document.createElement('div');
    colorEditor.className = 'color-editor';
    colorEditor.innerHTML = '<h3>Colors</h3>';
    
    // Create color categories
    const colorCategories = document.createElement('div');
    colorCategories.className = 'color-categories';
    
    // Add color categories and color pickers
    this.colorCategories.forEach(category => {
      const categoryElement = document.createElement('div');
      categoryElement.className = 'color-category';
      
      const categoryHeader = document.createElement('h4');
      categoryHeader.textContent = category.name;
      categoryHeader.title = category.description;
      
      const colorList = document.createElement('div');
      colorList.className = 'color-list';
      
      category.colors.forEach(color => {
        const colorItem = document.createElement('div');
        colorItem.className = 'color-item';
        
        const colorLabel = document.createElement('label');
        colorLabel.textContent = color.name;
        colorLabel.title = color.description;
        colorLabel.htmlFor = `color-${color.id}`;
        
        const colorInput = document.createElement('input');
        colorInput.type = 'color';
        colorInput.id = `color-${color.id}`;
        colorInput.dataset.colorId = color.id;
        colorInput.value = this.currentTheme.colors[color.id] || '#000000';
        
        colorItem.appendChild(colorLabel);
        colorItem.appendChild(colorInput);
        colorList.appendChild(colorItem);
      });
      
      categoryElement.appendChild(categoryHeader);
      categoryElement.appendChild(colorList);
      colorCategories.appendChild(categoryElement);
    });
    
    colorEditor.appendChild(colorCategories);
    
    // Assemble the theme editor
    content.appendChild(preview);
    content.appendChild(colorEditor);
    
    this.editorElement.appendChild(header);
    this.editorElement.appendChild(content);
    
    // Add to the document
    document.body.appendChild(this.editorElement);
    
    // Populate theme selector
    this.populateThemeSelector();
  }
  
  /**
   * Populate the theme selector dropdown
   */
  populateThemeSelector() {
    const selector = document.getElementById('theme-selector');
    if (!selector) return;
    
    // Clear existing options
    selector.innerHTML = '';
    
    // Add themes
    this.themes.forEach(theme => {
      const option = document.createElement('option');
      option.value = theme.id;
      option.textContent = theme.name + (theme.isBuiltin ? ' (Built-in)' : '');
      option.selected = theme.id === this.currentTheme.id;
      selector.appendChild(option);
    });
  }
  
  /**
   * Add event listeners to theme editor elements
   */
  addEventListeners() {
    // Close button
    const closeButton = document.getElementById('close-theme-editor-btn');
    if (closeButton) {
      closeButton.addEventListener('click', () => {
        if (this.unsavedChanges) {
          if (confirm('You have unsaved changes. Are you sure you want to close the theme editor?')) {
            this.hide();
          }
        } else {
          this.hide();
        }
      });
    }
    
    // Theme selector
    const themeSelector = document.getElementById('theme-selector');
    if (themeSelector) {
      themeSelector.addEventListener('change', () => {
        if (this.unsavedChanges) {
          if (confirm('You have unsaved changes. Are you sure you want to switch themes?')) {
            this.selectTheme(themeSelector.value);
          } else {
            // Reset selector to current theme
            themeSelector.value = this.currentTheme.id;
          }
        } else {
          this.selectTheme(themeSelector.value);
        }
      });
    }
    
    // New theme button
    const newThemeButton = document.getElementById('new-theme-btn');
    if (newThemeButton) {
      newThemeButton.addEventListener('click', () => this.createNewTheme());
    }
    
    // Save theme button
    const saveThemeButton = document.getElementById('save-theme-btn');
    if (saveThemeButton) {
      saveThemeButton.addEventListener('click', () => this.saveCurrentTheme());
    }
    
    // Export theme button
    const exportThemeButton = document.getElementById('export-theme-btn');
    if (exportThemeButton) {
      exportThemeButton.addEventListener('click', () => this.exportCurrentTheme());
    }
    
    // Import theme button
    const importThemeButton = document.getElementById('import-theme-btn');
    if (importThemeButton) {
      importThemeButton.addEventListener('click', () => this.importTheme());
    }
    
    // Color inputs
    const colorInputs = document.querySelectorAll('.color-editor input[type="color"]');
    colorInputs.forEach(input => {
      input.addEventListener('change', () => {
        const colorId = input.dataset.colorId;
        const colorValue = input.value;
        this.updateThemeColor(colorId, colorValue);
      });
    });
  }
  
  /**
   * Show the theme editor
   */
  show() {
    if (!this.editorElement) {
      this.createThemeEditorUI();
    }
    
    this.editorElement.style.display = 'block';
    this.isVisible = true;
    
    // Update preview with current theme
    this.updatePreview();
  }
  
  /**
   * Hide the theme editor
   */
  hide() {
    if (this.editorElement) {
      this.editorElement.style.display = 'none';
    }
    this.isVisible = false;
    this.unsavedChanges = false;
  }
  
  /**
   * Toggle the theme editor visibility
   */
  toggle() {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show();
    }
  }
  
  /**
   * Select a theme by ID
   * @param {string} themeId - The theme ID
   */
  selectTheme(themeId) {
    const theme = this.themes.find(t => t.id === themeId);
    if (!theme) {
      console.error(`Theme not found: ${themeId}`);
      return;
    }
    
    this.currentTheme = theme;
    this.unsavedChanges = false;
    
    // Update color inputs
    const colorInputs = document.querySelectorAll('.color-editor input[type="color"]');
    colorInputs.forEach(input => {
      const colorId = input.dataset.colorId;
      input.value = theme.colors[colorId] || '#000000';
    });
    
    // Update preview
    this.updatePreview();
    
    // Save current theme to local storage
    localStorage.setItem('mono-current-theme', themeId);
    
    console.log(`Selected theme: ${theme.name}`);
  }
  
  /**
   * Update a theme color
   * @param {string} colorId - The color ID
   * @param {string} colorValue - The color value
   */
  updateThemeColor(colorId, colorValue) {
    // Don't modify built-in themes directly
    if (this.currentTheme.isBuiltin) {
      // Create a copy of the theme
      const themeCopy = {
        ...this.currentTheme,
        id: `custom-${this.currentTheme.id}`,
        name: `Custom ${this.currentTheme.name}`,
        isBuiltin: false,
        colors: { ...this.currentTheme.colors }
      };
      
      // Add to themes
      this.themes.push(themeCopy);
      
      // Set as current theme
      this.currentTheme = themeCopy;
      
      // Update theme selector
      this.populateThemeSelector();
    }
    
    // Update the color
    this.currentTheme.colors[colorId] = colorValue;
    this.unsavedChanges = true;
    
    // Update preview
    this.updatePreview();
  }
  
  /**
   * Update the theme preview
   */
  updatePreview() {
    const previewContainer = document.querySelector('.preview-container');
    if (!previewContainer) return;
    
    // Apply theme colors to preview
    const colors = this.currentTheme.colors;
    
    // Set CSS variables
    previewContainer.style.setProperty('--background-color', colors['background-color'] || '#1e1e1e');
    previewContainer.style.setProperty('--foreground-color', colors['foreground-color'] || '#d4d4d4');
    previewContainer.style.setProperty('--editor-background', colors['editor-background'] || '#1e1e1e');
    previewContainer.style.setProperty('--editor-foreground', colors['editor-foreground'] || '#d4d4d4');
    previewContainer.style.setProperty('--editor-line-number', colors['editor-line-number'] || '#858585');
    
    // Set syntax highlighting colors
    const syntaxElements = previewContainer.querySelectorAll('[class^="syntax-"]');
    syntaxElements.forEach(element => {
      const syntaxClass = element.className;
      const colorId = syntaxClass;
      element.style.color = colors[colorId] || '';
    });
  }
  
  /**
   * Create a new theme
   */
  createNewTheme() {
    // Prompt for theme name
    const themeName = prompt('Enter a name for the new theme:');
    if (!themeName) return;
    
    // Generate a unique ID
    const themeId = 'theme-' + Date.now();
    
    // Create a new theme based on the current theme
    const newTheme = {
      id: themeId,
      name: themeName,
      description: 'Custom theme',
      isBuiltin: false,
      colors: { ...this.currentTheme.colors }
    };
    
    // Add to themes
    this.themes.push(newTheme);
    
    // Set as current theme
    this.currentTheme = newTheme;
    
    // Update theme selector
    this.populateThemeSelector();
    
    // Save themes
    this.saveThemes();
    
    // Update preview
    this.updatePreview();
    
    console.log(`Created new theme: ${themeName}`);
  }
  
  /**
   * Save the current theme
   */
  saveCurrentTheme() {
    // Don't save built-in themes
    if (this.currentTheme.isBuiltin) {
      alert('Cannot save built-in themes. Create a new theme instead.');
      return;
    }
    
    // Save themes
    this.saveThemes();
    
    // Reset unsaved changes flag
    this.unsavedChanges = false;
    
    console.log(`Saved theme: ${this.currentTheme.name}`);
    
    // Show success message
    alert(`Theme "${this.currentTheme.name}" saved successfully.`);
  }
  
  /**
   * Export the current theme
   */
  exportCurrentTheme() {
    try {
      // Create a JSON string of the theme
      const themeJson = JSON.stringify(this.currentTheme, null, 2);
      
      // Create a blob
      const blob = new Blob([themeJson], { type: 'application/json' });
      
      // Create a download link
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${this.currentTheme.name.toLowerCase().replace(/\s+/g, '-')}.json`;
      
      // Trigger download
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      
      console.log(`Exported theme: ${this.currentTheme.name}`);
    } catch (error) {
      console.error('Error exporting theme:', error);
      alert('Error exporting theme: ' + error.message);
    }
  }
  
  /**
   * Import a theme
   */
  importTheme() {
    // Create a file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    // Handle file selection
    input.addEventListener('change', async (e) => {
      try {
        const file = e.target.files[0];
        if (!file) return;
        
        // Read the file
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            // Parse the JSON
            const theme = JSON.parse(event.target.result);
            
            // Validate the theme
            if (!theme.id || !theme.name || !theme.colors) {
              throw new Error('Invalid theme format');
            }
            
            // Generate a new ID to avoid conflicts
            theme.id = 'imported-' + Date.now();
            theme.isBuiltin = false;
            
            // Add to themes
            this.themes.push(theme);
            
            // Set as current theme
            this.currentTheme = theme;
            
            // Update theme selector
            this.populateThemeSelector();
            
            // Save themes
            this.saveThemes();
            
            // Update preview
            this.updatePreview();
            
            console.log(`Imported theme: ${theme.name}`);
            
            // Show success message
            alert(`Theme "${theme.name}" imported successfully.`);
          } catch (parseError) {
            console.error('Error parsing theme:', parseError);
            alert('Error parsing theme: ' + parseError.message);
          }
        };
        
        reader.readAsText(file);
      } catch (error) {
        console.error('Error importing theme:', error);
        alert('Error importing theme: ' + error.message);
      }
    });
    
    // Trigger file selection
    input.click();
  }
}

// Create and export a singleton instance
const themeEditor = new ThemeEditor();

// Export the theme editor
window.themeEditor = themeEditor;
