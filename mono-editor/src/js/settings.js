// Settings Manager for Mono Editor

class SettingsManager {
  constructor() {
    this.settingsContainer = document.getElementById('settings-container');
    this.settingsOverlay = document.getElementById('settings-overlay');
    this.isVisible = false;
    this.settings = {};

    // Default settings
    this.defaultSettings = {
      editor: {
        fontSize: 14,
        fontFamily: 'Consolas, "Courier New", monospace',
        tabSize: 2,
        insertSpaces: true,
        wordWrap: 'off',
        lineNumbers: true,
        minimap: true,
        autoSave: false
      },
      terminal: {
        fontSize: 14,
        fontFamily: 'Consolas, "Courier New", monospace',
        scrollback: 1000
      },
      theme: {
        name: 'dark',
        customCSS: ''
      },
      general: {
        showWelcomeOnStartup: true,
        checkForUpdatesOnStartup: true,
        telemetry: false
      }
    };

    // Initialize settings
    this.loadSettings();

    // Initialize event listeners
    this.initEventListeners();

    // Initialize settings UI
    this.initSettingsUI();
  }

  loadSettings() {
    try {
      // Load settings from localStorage
      const savedSettings = localStorage.getItem('monoEditorSettings');
      if (savedSettings) {
        this.settings = JSON.parse(savedSettings);
      } else {
        // Use default settings if none are saved
        this.settings = JSON.parse(JSON.stringify(this.defaultSettings));
        this.saveSettings();
      }
    } catch (error) {
      console.error('Error loading settings:', error);
      // Use default settings if there's an error
      this.settings = JSON.parse(JSON.stringify(this.defaultSettings));
    }
  }

  saveSettings() {
    try {
      // Save settings to localStorage
      localStorage.setItem('monoEditorSettings', JSON.stringify(this.settings));

      // Apply settings
      this.applySettings();
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  }

  applySettings() {
    // Apply editor settings
    if (window.editorManager && window.editorManager.editors) {
      try {
        for (const editorId in window.editorManager.editors) {
          const editor = window.editorManager.editors[editorId].editor;
          if (editor && typeof editor.updateOptions === 'function') {
            editor.updateOptions({
              fontSize: this.settings.editor.fontSize,
              fontFamily: this.settings.editor.fontFamily,
              tabSize: this.settings.editor.tabSize,
              insertSpaces: this.settings.editor.insertSpaces,
              wordWrap: this.settings.editor.wordWrap,
              lineNumbers: this.settings.editor.lineNumbers ? 'on' : 'off',
              minimap: {
                enabled: this.settings.editor.minimap
              }
            });
          }
        }
      } catch (error) {
        console.warn('Error applying editor settings:', error);
      }
    }

    // Apply terminal settings
    if (window.terminalManager && window.terminalManager.terminals) {
      try {
        for (const terminalId in window.terminalManager.terminals) {
          const terminalObj = window.terminalManager.terminals[terminalId];
          if (terminalObj && terminalObj.terminal) {
            const terminal = terminalObj.terminal;
            if (terminal && terminal.options) {
              terminal.options.fontSize = this.settings.terminal.fontSize;
              terminal.options.fontFamily = this.settings.terminal.fontFamily;
              terminal.options.scrollback = this.settings.terminal.scrollback;
            }

            // Fit the terminal to the container if fitAddon is available
            if (terminalObj.fitAddon && typeof terminalObj.fitAddon.fit === 'function') {
              terminalObj.fitAddon.fit();
            }
          }
        }
      } catch (error) {
        console.warn('Error applying terminal settings:', error);
      }
    }

    // Apply theme settings
    if (window.themeManager && typeof window.themeManager.setTheme === 'function') {
      try {
        window.themeManager.setTheme(this.settings.theme.name);
      } catch (error) {
        console.warn('Error applying theme settings:', error);
      }
    }

    // Dispatch event for other components to listen for
    window.dispatchEvent(new CustomEvent('settingsChanged', { detail: this.settings }));
  }

  initEventListeners() {
    // Close button
    document.getElementById('close-settings-btn').addEventListener('click', () => {
      this.hideSettings();
    });

    // Save button
    document.getElementById('save-settings-btn').addEventListener('click', () => {
      this.saveSettings();
      this.hideSettings();
    });

    // Reset button
    document.getElementById('reset-settings-btn').addEventListener('click', () => {
      if (confirm('Are you sure you want to reset all settings to default?')) {
        this.settings = JSON.parse(JSON.stringify(this.defaultSettings));
        this.saveSettings();
        this.updateSettingsUI();
      }
    });

    // Close when clicking overlay
    this.settingsOverlay.addEventListener('click', (e) => {
      if (e.target === this.settingsOverlay) {
        this.hideSettings();
      }
    });

    // Escape key to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isVisible) {
        this.hideSettings();
      }
    });
  }

  showSettings() {
    this.settingsOverlay.classList.add('visible');
    this.isVisible = true;

    // Update UI with current settings
    this.updateSettingsUI();
  }

  hideSettings() {
    this.settingsOverlay.classList.remove('visible');
    this.isVisible = false;
  }

  toggleSettings() {
    if (this.isVisible) {
      this.hideSettings();
    } else {
      this.showSettings();
    }
  }

  initSettingsUI() {
    // Create settings tabs
    const tabsContainer = document.getElementById('settings-tabs');
    const contentContainer = document.getElementById('settings-content');

    // Create tabs for each settings category
    const categories = ['Editor', 'Terminal', 'Theme', 'General', 'Packages', 'Performance'];

    categories.forEach((category, index) => {
      // Create tab
      const tab = document.createElement('div');
      tab.className = 'settings-tab';
      if (index === 0) tab.classList.add('active');
      tab.textContent = category;
      tab.dataset.category = category.toLowerCase();
      tabsContainer.appendChild(tab);

      // Create content
      const content = document.createElement('div');
      content.className = 'settings-panel';
      if (index === 0) content.classList.add('active');
      content.dataset.category = category.toLowerCase();

      // Add settings for this category
      this.createSettingsPanel(content, category.toLowerCase());

      contentContainer.appendChild(content);

      // Add click handler
      tab.addEventListener('click', () => {
        // Deactivate all tabs and panels
        document.querySelectorAll('.settings-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.settings-panel').forEach(p => p.classList.remove('active'));

        // Activate this tab and panel
        tab.classList.add('active');
        content.classList.add('active');
      });
    });
  }

  createSettingsPanel(container, category) {
    // Create settings controls based on category
    switch (category) {
      case 'editor':
        this.createEditorSettings(container);
        break;
      case 'terminal':
        this.createTerminalSettings(container);
        break;
      case 'theme':
        this.createThemeSettings(container);
        break;
      case 'general':
        this.createGeneralSettings(container);
        break;
      case 'packages':
        this.createPackagesSettings(container);
        break;
      case 'performance':
        this.createPerformanceSettings(container);
        break;
    }
  }

  createPackagesSettings(container) {
    // The package UI is created in package-ui.js
    // We just need to create a container for it
    container.id = 'packages-panel';

    // Add a message to indicate that the package UI will be loaded
    const loadingMessage = document.createElement('div');
    loadingMessage.className = 'package-loading-message';
    loadingMessage.textContent = 'Loading package manager...';
    container.appendChild(loadingMessage);
  }

  createEditorSettings(container) {
    const settings = [
      {
        type: 'number',
        label: 'Font Size',
        setting: 'editor.fontSize',
        min: 8,
        max: 32
      },
      {
        type: 'text',
        label: 'Font Family',
        setting: 'editor.fontFamily'
      },
      {
        type: 'number',
        label: 'Tab Size',
        setting: 'editor.tabSize',
        min: 1,
        max: 8
      },
      {
        type: 'checkbox',
        label: 'Insert Spaces',
        setting: 'editor.insertSpaces'
      },
      {
        type: 'select',
        label: 'Word Wrap',
        setting: 'editor.wordWrap',
        options: [
          { value: 'off', label: 'Off' },
          { value: 'on', label: 'On' },
          { value: 'wordWrapColumn', label: 'Column' },
          { value: 'bounded', label: 'Bounded' }
        ]
      },
      {
        type: 'checkbox',
        label: 'Line Numbers',
        setting: 'editor.lineNumbers'
      },
      {
        type: 'checkbox',
        label: 'Minimap',
        setting: 'editor.minimap'
      },
      {
        type: 'checkbox',
        label: 'Auto Save',
        setting: 'editor.autoSave'
      }
    ];

    this.createSettingsControls(container, settings);
  }

  createTerminalSettings(container) {
    const settings = [
      {
        type: 'number',
        label: 'Font Size',
        setting: 'terminal.fontSize',
        min: 8,
        max: 32
      },
      {
        type: 'text',
        label: 'Font Family',
        setting: 'terminal.fontFamily'
      },
      {
        type: 'number',
        label: 'Scrollback',
        setting: 'terminal.scrollback',
        min: 100,
        max: 10000,
        step: 100
      }
    ];

    this.createSettingsControls(container, settings);
  }

  createThemeSettings(container) {
    const settings = [
      {
        type: 'select',
        label: 'Theme',
        setting: 'theme.name',
        options: [
          { value: 'dark', label: 'Dark' },
          { value: 'light', label: 'Light' },
          { value: 'nord', label: 'Nord' }
        ]
      },
      {
        type: 'textarea',
        label: 'Custom CSS',
        setting: 'theme.customCSS',
        placeholder: 'Add custom CSS here...'
      }
    ];

    this.createSettingsControls(container, settings);
  }

  createGeneralSettings(container) {
    const settings = [
      {
        type: 'checkbox',
        label: 'Show Welcome on Startup',
        setting: 'general.showWelcomeOnStartup'
      },
      {
        type: 'checkbox',
        label: 'Check for Updates on Startup',
        setting: 'general.checkForUpdatesOnStartup'
      },
      {
        type: 'checkbox',
        label: 'Enable Telemetry',
        setting: 'general.telemetry'
      }
    ];

    this.createSettingsControls(container, settings);
  }

  createSettingsControls(container, settings) {
    settings.forEach(setting => {
      const settingContainer = document.createElement('div');
      settingContainer.className = 'setting-item';

      const label = document.createElement('label');
      label.textContent = setting.label;
      settingContainer.appendChild(label);

      let input;

      switch (setting.type) {
        case 'text':
          input = document.createElement('input');
          input.type = 'text';
          break;
        case 'number':
          input = document.createElement('input');
          input.type = 'number';
          if (setting.min !== undefined) input.min = setting.min;
          if (setting.max !== undefined) input.max = setting.max;
          if (setting.step !== undefined) input.step = setting.step;
          break;
        case 'checkbox':
          input = document.createElement('input');
          input.type = 'checkbox';
          break;
        case 'select':
          input = document.createElement('select');
          setting.options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value;
            optionElement.textContent = option.label;
            input.appendChild(optionElement);
          });
          break;
        case 'textarea':
          input = document.createElement('textarea');
          if (setting.placeholder) input.placeholder = setting.placeholder;
          break;
      }

      input.className = 'setting-input';
      input.dataset.setting = setting.setting;

      // Add change handler
      input.addEventListener('change', () => {
        const [category, settingName] = setting.setting.split('.');
        let value;

        if (input.type === 'checkbox') {
          value = input.checked;
        } else if (input.type === 'number') {
          value = parseInt(input.value, 10);
        } else {
          value = input.value;
        }

        this.settings[category][settingName] = value;
      });

      settingContainer.appendChild(input);
      container.appendChild(settingContainer);
    });
  }

  updateSettingsUI() {
    // Update all input values to match current settings
    document.querySelectorAll('[data-setting]').forEach(input => {
      const [category, setting] = input.dataset.setting.split('.');
      const value = this.settings[category][setting];

      if (input.type === 'checkbox') {
        input.checked = value;
      } else if (input.type === 'select-one') {
        input.value = value;
      } else {
        input.value = value;
      }
    });

    // Update performance metrics if the performance panel is active
    if (document.querySelector('.settings-panel[data-category="performance"].active')) {
      this.updatePerformanceMetrics();
    }
  }

  /**
   * Create the performance settings panel
   * @param {HTMLElement} container - The container element
   */
  createPerformanceSettings(container) {
    // Create a container for performance metrics
    const metricsContainer = document.createElement('div');
    metricsContainer.className = 'performance-metrics-container';
    container.appendChild(metricsContainer);

    // Create sections for different types of metrics
    this.createPerformanceSection(metricsContainer, 'Load Times', 'load-times');
    this.createPerformanceSection(metricsContainer, 'Component Initialization', 'component-init');
    this.createPerformanceSection(metricsContainer, 'Resource Usage', 'resource-usage');
    this.createPerformanceSection(metricsContainer, 'Optimization Suggestions', 'optimization-suggestions');

    // Add refresh button
    const refreshButton = document.createElement('button');
    refreshButton.className = 'btn btn-primary';
    refreshButton.textContent = 'Refresh Metrics';
    refreshButton.addEventListener('click', () => {
      this.updatePerformanceMetrics();
    });

    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'performance-button-container';
    buttonContainer.appendChild(refreshButton);
    container.appendChild(buttonContainer);

    // Initial update of metrics
    this.updatePerformanceMetrics();
  }

  /**
   * Create a section in the performance panel
   * @param {HTMLElement} container - The container element
   * @param {string} title - The section title
   * @param {string} id - The section ID
   */
  createPerformanceSection(container, title, id) {
    const section = document.createElement('div');
    section.className = 'performance-section';

    const sectionTitle = document.createElement('h3');
    sectionTitle.textContent = title;
    section.appendChild(sectionTitle);

    const sectionContent = document.createElement('div');
    sectionContent.className = 'performance-section-content';
    sectionContent.id = `performance-${id}`;
    section.appendChild(sectionContent);

    container.appendChild(section);
  }

  /**
   * Update the performance metrics display
   */
  updatePerformanceMetrics() {
    // Check if performance monitor is available
    if (!window.performanceMonitor) {
      console.error('Performance monitor not available');
      return;
    }

    // Update load times
    this.updateLoadTimes();

    // Update component initialization times
    this.updateComponentInitTimes();

    // Update resource usage
    this.updateResourceUsage();

    // Update optimization suggestions
    this.updateOptimizationSuggestions();
  }

  /**
   * Update the load times section
   */
  updateLoadTimes() {
    const container = document.getElementById('performance-load-times');
    if (!container) return;

    // Clear container
    container.innerHTML = '';

    // Get load events from performance monitor
    const loadEvents = window.performanceMonitor.metrics.loadEvents;

    if (loadEvents.length === 0) {
      container.textContent = 'No load events recorded';
      return;
    }

    // Create table
    const table = document.createElement('table');
    table.className = 'performance-table';

    // Create header
    const header = document.createElement('tr');
    header.innerHTML = '<th>Event</th><th>Time (ms)</th>';
    table.appendChild(header);

    // Add rows for each load event
    loadEvents.forEach(event => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${event.name}</td>
        <td>${event.timeFromStart.toFixed(2)}</td>
      `;
      table.appendChild(row);
    });

    container.appendChild(table);
  }

  /**
   * Update the component initialization times section
   */
  updateComponentInitTimes() {
    const container = document.getElementById('performance-component-init');
    if (!container) return;

    // Clear container
    container.innerHTML = '';

    // Get component initialization times from performance monitor
    const componentInitTimes = window.performanceMonitor.metrics.componentInitTimes;

    if (Object.keys(componentInitTimes).length === 0) {
      container.textContent = 'No component initialization events recorded';
      return;
    }

    // Create table
    const table = document.createElement('table');
    table.className = 'performance-table';

    // Create header
    const header = document.createElement('tr');
    header.innerHTML = '<th>Component</th><th>Time (ms)</th>';
    table.appendChild(header);

    // Add rows for each component
    Object.entries(componentInitTimes)
      .sort((a, b) => a[1].timeFromStart - b[1].timeFromStart)
      .forEach(([component, timing]) => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${component}</td>
          <td>${timing.timeFromStart.toFixed(2)}</td>
        `;
        table.appendChild(row);
      });

    container.appendChild(table);
  }

  /**
   * Update the resource usage section
   */
  updateResourceUsage() {
    const container = document.getElementById('performance-resource-usage');
    if (!container) return;

    // Clear container
    container.innerHTML = '';

    // Get resource load times from performance monitor
    const resourceLoadTimes = window.performanceMonitor.metrics.resourceLoadTimes;

    if (Object.keys(resourceLoadTimes).length === 0) {
      container.textContent = 'No resource usage data available';
      return;
    }

    // Create table
    const table = document.createElement('table');
    table.className = 'performance-table';

    // Create header
    const header = document.createElement('tr');
    header.innerHTML = '<th>Resource</th><th>Type</th><th>Size</th><th>Load Time (ms)</th>';
    table.appendChild(header);

    // Add rows for slow resources (>100ms)
    Object.entries(resourceLoadTimes)
      .filter(([_, timing]) => timing.duration > 100)
      .sort((a, b) => b[1].duration - a[1].duration)
      .slice(0, 10) // Show only top 10 slowest resources
      .forEach(([resource, timing]) => {
        const row = document.createElement('tr');
        const resourceName = resource.split('/').pop();
        row.innerHTML = `
          <td title="${resource}">${resourceName}</td>
          <td>${timing.type}</td>
          <td>${typeof timing.size === 'number' ? `${(timing.size / 1024).toFixed(2)} KB` : 'Unknown'}</td>
          <td>${timing.duration.toFixed(2)}</td>
        `;
        table.appendChild(row);
      });

    container.appendChild(table);
  }

  /**
   * Update the optimization suggestions section
   */
  updateOptimizationSuggestions() {
    const container = document.getElementById('performance-optimization-suggestions');
    if (!container) return;

    // Clear container
    container.innerHTML = '';

    // Get optimization suggestions from performance monitor
    const suggestions = window.performanceMonitor.getOptimizationSuggestions();

    if (suggestions.length === 0) {
      container.textContent = 'No optimization suggestions available';
      return;
    }

    // Create list
    const list = document.createElement('ul');
    list.className = 'performance-suggestions-list';

    // Add items for each suggestion
    suggestions.forEach(suggestion => {
      const item = document.createElement('li');
      item.textContent = suggestion;
      list.appendChild(item);
    });

    container.appendChild(list);
  }
}
