// Main application script for Mono Editor

class MonoEditor {
  constructor() {
    // Initialize jQuery
    this.initJQuery();

    // Initialize components
    this.initComponents();

    // Initialize event listeners
    this.initEventListeners();

    // Initialize menu event handlers
    this.initMenuEventHandlers();

    // Create error modal
    this.createErrorModal();

    // Log initialization
    console.log('MonoEditor initialized with jQuery support');
  }

  // Initialize jQuery
  initJQuery() {
    // Check if jQuery is available
    if (typeof window.jQuery === 'undefined') {
      console.error('jQuery is not available. Some features may not work correctly.');
      // Create a simple fallback
      window.$ = function(selector) {
        if (typeof selector === 'string') {
          return document.querySelector(selector);
        }
        return selector;
      };
      window.jQuery = window.$;

      // Add a minimal jQuery-like API
      window.$.fn = {};
      window.$.fn.jquery = 'fallback';
    } else {
      console.log('jQuery version:', window.jQuery.fn.jquery);

      // Ensure $ is defined as an alias to jQuery
      if (typeof window.$ === 'undefined') {
        window.$ = window.jQuery;
      }
    }

    // Check if MonoJQueryUtils is available
    if (window.MonoJQueryUtils) {
      console.log('MonoJQueryUtils is available');
    } else {
      console.warn('MonoJQueryUtils is not available. Creating fallback utilities.');
      this.createFallbackUtils();
    }
  }

  // Create fallback utilities if MonoJQueryUtils is not available
  createFallbackUtils() {
    window.MonoJQueryUtils = {
      showStatusMessage: (message, type) => {
        console.log(`Status message: ${message} (${type})`);
        this.showStatusMessage(message, type);
      },
      showError: (message, error, isCritical) => {
        console.error(message, error);
        this.showError(message, error);
      },
      createErrorModal: () => {
        this.createErrorModal();
      },
      init: () => {
        console.log('Fallback MonoJQueryUtils initialized');
      }
    };
  }

  initComponents() {
    // Components are initialized in their respective files
    // This method is for any additional initialization

    // Use MonoJQueryUtils if available, otherwise use direct jQuery
    if (window.MonoJQueryUtils) {
      // MonoJQueryUtils handles initialization in its own init method
      // which is called on document ready
    } else {
      // Fallback to direct jQuery initialization
      $('.dialog').addClass('modal-content');
      $('.dialog-header').addClass('modal-header');
      $('.dialog-content').addClass('modal-body');
      $('.dialog-footer').addClass('modal-footer');
      $('.dialog-btn').addClass('btn');
      $('.dialog-btn-primary').addClass('btn-primary');

      // Add tooltips to buttons
      $('[title]').tooltip({
        placement: 'bottom',
        trigger: 'hover'
      });
    }

    // Initialize our new components
    this.initNewComponents();
  }

  // Initialize new components
  async initNewComponents() {
    try {
      console.log('Initializing new components...');

      // Initialize file operations
      if (window.fileOperations) {
        console.log('File operations already initialized');
      } else {
        console.log('Creating new file operations instance');
        window.fileOperations = new FileOperations();
      }

      // Initialize scrolling manager
      if (window.scrollingManager) {
        console.log('Scrolling manager already initialized');
      } else {
        console.log('Creating new scrolling manager instance');
        window.scrollingManager = new ScrollingManager();
      }

      // Initialize plugin system
      if (window.pluginManager) {
        console.log('Plugin manager already initialized');
        await window.pluginManager.initialize();
      } else if (typeof PluginManager !== 'undefined') {
        console.log('Creating new plugin manager instance');
        window.pluginManager = new PluginManager();
        await window.pluginManager.initialize();
      } else {
        console.error('PluginManager class is not defined');
      }

      // Initialize plugin marketplace
      if (window.pluginMarketplace) {
        console.log('Plugin marketplace already initialized');
      } else if (typeof PluginMarketplace !== 'undefined') {
        console.log('Creating new plugin marketplace instance');
        window.pluginMarketplace = new PluginMarketplace();
      } else {
        console.error('PluginMarketplace class is not defined');
      }

      // Initialize project manager
      if (window.projectManager) {
        console.log('Project manager already initialized');
      } else if (typeof ProjectManager !== 'undefined') {
        console.log('Creating new project manager instance');
        window.projectManager = new ProjectManager();
      } else {
        console.error('ProjectManager class is not defined');
      }

      // Initialize theme editor
      if (window.themeEditor) {
        console.log('Theme editor already initialized');
      } else if (typeof ThemeEditor !== 'undefined') {
        console.log('Creating new theme editor instance');
        window.themeEditor = new ThemeEditor();
      } else {
        console.error('ThemeEditor class is not defined');
      }

      // Initialize enhanced AI assistant
      if (window.enhancedAIAssistant) {
        console.log('Enhanced AI assistant already initialized');
      } else if (typeof EnhancedAIAssistant !== 'undefined') {
        console.log('Creating new enhanced AI assistant instance');
        window.enhancedAIAssistant = new EnhancedAIAssistant();
      } else {
        console.error('EnhancedAIAssistant class is not defined');
      }

      console.log('New components initialized successfully');
    } catch (error) {
      console.error('Error initializing new components:', error);
    }
  }

  initEventListeners() {
    // Use jQuery for event delegation on welcome screen buttons
    $('.welcome-screen').on('click', 'button', (e) => {
      const buttonId = $(e.currentTarget).attr('id');

      switch (buttonId) {
        case 'welcome-new-file':
          this.newFile();
          break;
        case 'welcome-open-file':
          this.openFile();
          break;
        case 'welcome-open-folder':
          this.openFolder();
          break;
        case 'welcome-docs':
          window.open('https://github.com/blackswanalpha/mono', '_blank');
          break;
        case 'welcome-samples':
          this.showStatusMessage('Sample projects coming soon!', 'info');
          break;
      }
    });

    // Use jQuery for event delegation on sidebar actions
    $('.sidebar-actions').on('click', 'button', (e) => {
      const $button = $(e.currentTarget);
      const buttonId = $button.attr('id');

      if ($button.prop('disabled')) return;

      // Add visual feedback by temporarily disabling the button
      const originalTitle = $button.attr('title');
      $button.prop('disabled', true);

      switch (buttonId) {
        case 'new-file-btn':
          this.newFile();
          break;
        case 'open-file-btn':
          this.openFile();
          break;
        case 'open-folder-btn':
          this.openFolder();
          break;
      }

      // Re-enable the button after a short delay
      setTimeout(() => {
        $button.prop('disabled', false);
        $button.attr('title', originalTitle);
      }, 300);
    });

    // Add ARIA attributes to buttons for better accessibility
    this.enhanceToolbarAccessibility();

    // Dialog close buttons using jQuery
    $('.dialog-close-btn, .dialog-btn').on('click', () => {
      $('#dialog-overlay').removeClass('visible');
    });

    // Add error handling for all button clicks
    $(document).on('click', 'button', (e) => {
      try {
        // This is just a global error handler, the actual click handling is done above
        console.log(`Button clicked: ${e.currentTarget.id || 'unnamed button'}`);
      } catch (error) {
        console.error('Error handling button click:', error);
        this.showError('Error handling button click', error);
      }
    });
  }

  // Enhance toolbar accessibility using jQuery
  enhanceToolbarAccessibility() {
    $('.sidebar-actions button, #toggle-ai-btn').each((_, button) => {
      const $button = $(button);

      // Make sure buttons have proper aria attributes
      if ($button.attr('title') && !$button.attr('aria-label')) {
        $button.attr('aria-label', $button.attr('title'));
      }

      // Add keyboard event listeners
      $button.on('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          $button.trigger('click');
        }
      });
    });
  }

  initMenuEventHandlers() {
    // File menu
    window.api.onMenuEvent('menu-new-file', () => this.newFile());
    window.api.onMenuEvent('menu-open-file', () => this.openFile());
    window.api.onMenuEvent('menu-open-folder', () => this.openFolder());
    window.api.onMenuEvent('menu-save', () => this.saveFile());
    window.api.onMenuEvent('menu-save-as', () => this.saveFileAs());

    // View menu
    window.api.onMenuEvent('menu-toggle-explorer', () => this.toggleExplorer());
    window.api.onMenuEvent('menu-toggle-terminal', () => this.toggleTerminal());
    window.api.onMenuEvent('menu-toggle-debug', () => this.toggleDebug());
    window.api.onMenuEvent('menu-toggle-ai', () => this.toggleAI());
    window.api.onMenuEvent('menu-zoom-in', () => this.zoomIn());
    window.api.onMenuEvent('menu-zoom-out', () => this.zoomOut());
    window.api.onMenuEvent('menu-zoom-reset', () => this.zoomReset());

    // Mono menu
    window.api.onMenuEvent('menu-run-file', () => this.runFile());
    window.api.onMenuEvent('menu-stop-program', () => this.stopProgram());
    window.api.onMenuEvent('menu-format-document', () => this.formatDocument());

    // Debug menu
    window.api.onMenuEvent('menu-debug-start', () => this.startDebugging());
    window.api.onMenuEvent('menu-debug-stop', () => this.stopDebugging());
    window.api.onMenuEvent('menu-debug-restart', () => this.restartDebugging());
    window.api.onMenuEvent('menu-debug-continue', () => this.continueDebugging());
    window.api.onMenuEvent('menu-debug-step-over', () => this.stepOver());
    window.api.onMenuEvent('menu-debug-step-into', () => this.stepInto());
    window.api.onMenuEvent('menu-debug-step-out', () => this.stepOut());
    window.api.onMenuEvent('menu-debug-toggle-breakpoint', () => this.toggleBreakpoint());
    window.api.onMenuEvent('menu-debug-clear-breakpoints', () => this.clearBreakpoints());

    // Theme menu
    window.api.onMenuEvent('menu-theme-dark', () => this.setTheme('dark'));
    window.api.onMenuEvent('menu-theme-light', () => this.setTheme('light'));
    window.api.onMenuEvent('menu-theme-nord', () => this.setTheme('nord'));

    // Settings menu
    window.api.onMenuEvent('menu-settings', () => this.showSettings());
    window.api.onMenuEvent('menu-package-manager', () => this.showPackageManager());

    // New components menu events
    window.api.onMenuEvent('menu-plugin-manager', () => this.showPluginManager());
    window.api.onMenuEvent('menu-project-manager', () => this.showProjectManager());
    window.api.onMenuEvent('menu-theme-editor', () => this.showThemeEditor());
    window.api.onMenuEvent('menu-enhanced-ai', () => this.toggleEnhancedAI());

    // Help menu
    window.api.onMenuEvent('menu-about', () => this.showAboutDialog());
  }

  newFile() {
    console.log('newFile method called');

    let $newFileBtn;
    let originalContent;

    try {
      // Check if editorManager is initialized
      if (typeof window.editorManager === 'undefined' || !window.editorManager) {
        console.error('Editor manager is not initialized');
        this.showError('Error creating new file', { message: 'Editor manager is not initialized. The application may not be fully initialized.' });
        return;
      }

      // Disable the button to prevent multiple clicks
      try {
        $newFileBtn = $('#new-file-btn');
        if ($newFileBtn.length) {
          $newFileBtn.prop('disabled', true);
          $newFileBtn.attr('title', 'Creating new file...');

          // Add a loading spinner to the button
          originalContent = $newFileBtn.html();
          $newFileBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating...');
        } else {
          console.warn('New file button not found');
        }
      } catch (buttonError) {
        console.error('Error updating button state:', buttonError);
      }

      try {
        if (window.editorManager && typeof window.editorManager.createEditor === 'function' && typeof window.editorManager.activateTab === 'function') {
          console.log('Creating new file');
          const tabId = 'tab-' + Date.now();
          window.editorManager.createEditor(tabId);
          window.editorManager.activateTab(tabId);
          this.showStatusMessage('New file created', 'success');
        } else {
          console.error('editorManager methods are not properly defined');
          this.showError('Error creating new file', { message: 'Editor manager is not properly initialized.' });
        }
      } catch (error) {
        console.error('Error creating new file:', error);
        this.showError('Error creating new file', error);
      } finally {
        // Re-enable the button
        try {
          if ($newFileBtn && $newFileBtn.length) {
            setTimeout(() => {
              $newFileBtn.prop('disabled', false);
              $newFileBtn.attr('title', 'New File');
              if (originalContent) {
                $newFileBtn.html(originalContent);
              }
            }, 300);
          }
        } catch (buttonError) {
          console.error('Error restoring button state:', buttonError);
        }
      }
    } catch (error) {
      console.error('Unhandled error in newFile:', error);
      this.showError('Unhandled error creating new file', error);

      // Make sure the button is re-enabled
      try {
        if ($newFileBtn && $newFileBtn.length) {
          $newFileBtn.prop('disabled', false);
          $newFileBtn.attr('title', 'New File');
          if (originalContent) {
            $newFileBtn.html(originalContent);
          }
        } else {
          $('#new-file-btn').prop('disabled', false)
                           .attr('title', 'New File')
                           .html('<i class="icon icon-new-file"></i>');
        }
      } catch (buttonError) {
        console.error('Error restoring button state after unhandled error:', buttonError);
      }
    }
  }

  async openFile() {
    console.log('openFile method called');

    let $openFileBtn;
    let originalContent;

    try {
      // Check if window.api is available
      if (!window.api || typeof window.api.openFile !== 'function') {
        console.error('API not available or openFile function missing');
        this.showError('Error opening file', { message: 'API not available. The application may not be fully initialized.' });
        return;
      }

      // Check if editorManager is initialized
      if (typeof window.editorManager === 'undefined' || !window.editorManager) {
        console.error('Editor manager is not initialized');
        this.showError('Error opening file', { message: 'Editor manager is not initialized. The application may not be fully initialized.' });
        return;
      }

      // Disable the button to prevent multiple clicks
      try {
        $openFileBtn = $('#open-file-btn');
        if ($openFileBtn.length) {
          $openFileBtn.prop('disabled', true);
          $openFileBtn.attr('title', 'Opening file...');

          // Add a loading spinner to the button
          originalContent = $openFileBtn.html();
          $openFileBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Opening...');
        } else {
          console.warn('Open file button not found');
        }
      } catch (buttonError) {
        console.error('Error updating button state:', buttonError);
      }

      try {
        console.log('Calling window.api.openFile');
        const filePath = await window.api.openFile();
        console.log('openFile result:', filePath);

        if (filePath) {
          if (window.editorManager && typeof window.editorManager.openFile === 'function') {
            console.log('Opening file in editor:', filePath);
            await window.editorManager.openFile(filePath);
            this.showStatusMessage(`Opened file: ${this.getFileName(filePath)}`, 'success');
          } else {
            console.error('editorManager.openFile is not a function');
            this.showError('Error opening file', { message: 'Editor manager is not properly initialized.' });
          }
        } else {
          console.log('No file selected or dialog canceled');
        }
      } catch (error) {
        console.error('Error opening file:', error);
        this.showError('Error opening file', error);
      } finally {
        // Re-enable the button
        try {
          if ($openFileBtn && $openFileBtn.length) {
            $openFileBtn.prop('disabled', false);
            $openFileBtn.attr('title', 'Open File');
            if (originalContent) {
              $openFileBtn.html(originalContent);
            }
          }
        } catch (buttonError) {
          console.error('Error restoring button state:', buttonError);
        }
      }
    } catch (error) {
      console.error('Unhandled error in openFile:', error);
      this.showError('Unhandled error opening file', error);

      // Make sure the button is re-enabled
      try {
        if ($openFileBtn && $openFileBtn.length) {
          $openFileBtn.prop('disabled', false);
          $openFileBtn.attr('title', 'Open File');
          if (originalContent) {
            $openFileBtn.html(originalContent);
          }
        } else {
          $('#open-file-btn').prop('disabled', false)
                            .attr('title', 'Open File')
                            .html('<i class="icon icon-open-file"></i>');
        }
      } catch (buttonError) {
        console.error('Error restoring button state after unhandled error:', buttonError);
      }
    }
  }

  // Helper method to get file name from path
  getFileName(filePath) {
    if (!filePath) return '';
    return filePath.split(/[\/\\]/).pop();
  }

  openFolder() {
    console.log('openFolder method called');

    try {
      // Check if window.api is available
      if (!window.api || typeof window.api.openFolder !== 'function') {
        console.error('API not available or openFolder function missing');
        this.showError('Error opening folder', { message: 'API not available. The application may not be fully initialized.' });
        return;
      }

      // Check if FileExplorer class is defined
      if (typeof FileExplorer === 'undefined') {
        console.error('FileExplorer class is not defined');
        this.showError('Error opening folder', { message: 'FileExplorer class is not defined. The application may not be fully initialized.' });
        return;
      }

      // Check if window.fileExplorer is initialized
      if (!window.fileExplorer) {
        console.log('File explorer not initialized, creating new instance');

        // Try to initialize it if possible
        try {
          window.fileExplorer = new FileExplorer();
          this.showStatusMessage('File explorer initialized', 'info');
        } catch (initError) {
          console.error('Failed to initialize file explorer:', initError);
          this.showError('File explorer could not be initialized', initError);
          return;
        }
      }

      if (window.fileExplorer) {
        // Disable the button to prevent multiple clicks
        let $openFolderBtn;
        let originalContent;

        try {
          $openFolderBtn = $('#open-folder-btn');
          if ($openFolderBtn.length) {
            $openFolderBtn.prop('disabled', true);
            $openFolderBtn.attr('title', 'Opening folder...');

            // Add a loading spinner to the button
            originalContent = $openFolderBtn.html();
            $openFolderBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Opening...');
          } else {
            console.warn('Open folder button not found');
          }
        } catch (buttonError) {
          console.error('Error updating button state:', buttonError);
        }

        // Direct API call as fallback if window.fileExplorer.openFolder fails
        const openFolderDirectly = async () => {
          try {
            console.log('Calling window.api.openFolder directly');
            const folderPath = await window.api.openFolder();
            return folderPath;
          } catch (directError) {
            console.error('Error calling window.api.openFolder directly:', directError);
            throw directError;
          }
        };

        // Try to call window.fileExplorer.openFolder, fallback to direct API call
        const openFolderPromise = async () => {
          try {
            if (typeof window.fileExplorer.openFolder === 'function') {
              console.log('Calling window.fileExplorer.openFolder');
              return await window.fileExplorer.openFolder();
            } else {
              console.warn('window.fileExplorer.openFolder is not a function, using direct API call');
              return await openFolderDirectly();
            }
          } catch (error) {
            console.error('Error in openFolder, trying direct API call:', error);
            return await openFolderDirectly();
          }
        };

        // Execute the open folder operation
        openFolderPromise()
          .then((folderPath) => {
            console.log('Open folder operation completed, result:', folderPath);

            // Re-enable the button
            try {
              if ($openFolderBtn && $openFolderBtn.length) {
                $openFolderBtn.prop('disabled', false);
                $openFolderBtn.attr('title', 'Open Folder');
                if (originalContent) {
                  $openFolderBtn.html(originalContent);
                }
              }
            } catch (buttonError) {
              console.error('Error restoring button state:', buttonError);
            }

            // Show success message if a folder was selected
            if (folderPath) {
              this.showStatusMessage(`Opened folder: ${this.getShortPath(folderPath)}`, 'success');
            }
          })
          .catch(error => {
            console.error('Final error in open folder operation:', error);

            // Re-enable the button
            try {
              if ($openFolderBtn && $openFolderBtn.length) {
                $openFolderBtn.prop('disabled', false);
                $openFolderBtn.attr('title', 'Open Folder');
                if (originalContent) {
                  $openFolderBtn.html(originalContent);
                }
              }
            } catch (buttonError) {
              console.error('Error restoring button state on error:', buttonError);
            }

            this.showError('Error opening folder', error);
          });
      }
    } catch (error) {
      console.error('Unhandled error in openFolder:', error);
      this.showError('Unhandled error opening folder', error);

      // Make sure the button is re-enabled
      try {
        $('#open-folder-btn').prop('disabled', false)
                            .attr('title', 'Open Folder')
                            .html('<i class="icon icon-open-folder"></i>');
      } catch (buttonError) {
        console.error('Error restoring button state after unhandled error:', buttonError);
      }
    }
  }

  // Helper method to get a shortened path for display
  getShortPath(fullPath) {
    if (!fullPath) return '';

    const maxLength = 30;
    if (fullPath.length <= maxLength) return fullPath;

    const parts = fullPath.split(/[\/\\]/);
    if (parts.length <= 2) return fullPath;

    const firstPart = parts[0];
    const lastPart = parts[parts.length - 1];
    const secondLastPart = parts[parts.length - 2];

    return `${firstPart}/.../${secondLastPart}/${lastPart}`;
  }

  // Show error message in status bar and console
  showError(message, error) {
    // Use MonoJQueryUtils if available, otherwise use direct implementation
    if (window.MonoJQueryUtils) {
      window.MonoJQueryUtils.showError(message, error, error.critical);
    } else {
      console.error(message, error);

      // Show in status bar instead of alert
      const statusMessage = `${message}: ${error.message || 'Unknown error'}`;
      this.showStatusMessage(statusMessage, 'error');

      // Show alert only for critical errors
      if (error.critical) {
        // Use Bootstrap modal if available, otherwise fallback to alert
        if ($('#error-modal').length) {
          $('#error-modal-title').text('Error');
          $('#error-modal-body').text(`${message}: ${error.message || 'Unknown error'}`);
          $('#error-modal').modal('show');
        } else {
          alert(`${message}: ${error.message || 'Unknown error'}`);
        }
      }
    }
  }

  // Show status message in the status bar using jQuery
  showStatusMessage(message, type = 'info') {
    // Use MonoJQueryUtils if available, otherwise use direct implementation
    if (window.MonoJQueryUtils) {
      window.MonoJQueryUtils.showStatusMessage(message, type);
    } else {
      console.log(`Status message: ${message} (${type})`);

      // Get or create status message element using jQuery
      const $statusBar = $('.status-left');
      if (!$statusBar.length) return;

      let $statusElement = $('#editor-status-message');
      if (!$statusElement.length) {
        $statusElement = $('<span>', {
          id: 'editor-status-message'
        });
        $statusBar.append($statusElement);
      }

      // Set message and style based on type
      $statusElement.text(message);
      $statusElement.removeClass(); // Clear previous classes
      $statusElement.addClass(`status-message status-${type}`);

      // Set color based on type
      const colors = {
        error: '#F44336',
        warning: '#FFC107',
        success: '#4CAF50',
        info: '#2196F3'
      };

      $statusElement.css('color', colors[type] || colors.info);

      // Remove the status after a delay
      setTimeout(() => {
        $statusElement.fadeOut(300, function() {
          $(this).remove();
        });
      }, 5000);
    }
  }

  // Create a Bootstrap modal for error messages
  createErrorModal() {
    // Use MonoJQueryUtils if available, otherwise use direct implementation
    if (window.MonoJQueryUtils) {
      window.MonoJQueryUtils.createErrorModal();
    } else {
      // Only create if it doesn't exist
      if ($('#error-modal').length === 0) {
        const modalHTML = `
          <div class="modal fade" id="error-modal" tabindex="-1" role="dialog" aria-labelledby="error-modal-title" aria-hidden="true">
            <div class="modal-dialog" role="document">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title" id="error-modal-title">Error</h5>
                  <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                  </button>
                </div>
                <div class="modal-body" id="error-modal-body">
                  An error occurred.
                </div>
                <div class="modal-footer">
                  <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                </div>
              </div>
            </div>
          </div>
        `;

        $('body').append(modalHTML);
      }
    }
  }

  saveFile() {
    if (window.editorManager && window.editorManager.activeEditor) {
      window.editorManager.saveFile(window.editorManager.activeEditor);
    }
  }

  saveFileAs() {
    if (window.editorManager && window.editorManager.activeEditor) {
      window.editorManager.saveFileAs(window.editorManager.activeEditor);
    }
  }

  toggleExplorer() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.classList.toggle('collapsed');
    }
  }

  toggleTerminal() {
    if (window.terminalManager) {
      window.terminalManager.toggleTerminal();
    }
  }

  toggleDebug() {
    if (window.debuggerManager) {
      window.debuggerManager.toggleDebugPanel();
    }
  }

  toggleAI() {
    if (window.aiAssistant) {
      window.aiAssistant.toggleAssistant();
    }
  }

  zoomIn() {
    // Implement editor zoom in
    if (window.editorManager && window.editorManager.activeEditor) {
      const editor = window.editorManager.editors[window.editorManager.activeEditor].editor;
      const fontSize = editor.getOption(monaco.editor.EditorOption.fontSize);
      editor.updateOptions({ fontSize: fontSize + 1 });
    }
  }

  zoomOut() {
    // Implement editor zoom out
    if (window.editorManager && window.editorManager.activeEditor) {
      const editor = window.editorManager.editors[window.editorManager.activeEditor].editor;
      const fontSize = editor.getOption(monaco.editor.EditorOption.fontSize);
      if (fontSize > 8) {
        editor.updateOptions({ fontSize: fontSize - 1 });
      }
    }
  }

  zoomReset() {
    // Reset editor zoom
    if (window.editorManager && window.editorManager.activeEditor) {
      const editor = window.editorManager.editors[window.editorManager.activeEditor].editor;
      editor.updateOptions({ fontSize: 14 });
    }
  }

  runFile() {
    if (window.terminalManager) {
      window.terminalManager.showTerminal();

      // Get the active file path
      let filePath = null;
      if (window.editorManager) {
        filePath = window.editorManager.getActiveFilePath();
      }

      // Run the file in the active terminal
      if (window.terminalManager.activeTerminal) {
        window.terminalManager.runMonoFile(window.terminalManager.activeTerminal, filePath);
      }
    }
  }

  stopProgram() {
    // Stop the current running program
    if (window.terminalManager && window.terminalManager.activeTerminal) {
      window.terminalManager.stopProcess(window.terminalManager.activeTerminal);
    }
  }

  formatDocument() {
    if (window.editorManager) {
      window.editorManager.formatDocument();
    }
  }

  setTheme(themeName) {
    if (window.themeManager) {
      window.themeManager.setTheme(themeName);
    }
  }

  showAboutDialog() {
    document.getElementById('dialog-overlay').classList.add('visible');
  }

  showSettings() {
    if (settingsManager) {
      settingsManager.showSettings();
    }
  }

  showPackageManager() {
    if (settingsManager) {
      // Show settings panel
      settingsManager.showSettings();

      // Switch to packages tab
      const packagesTab = document.querySelector('.settings-tab[data-category="packages"]');
      if (packagesTab) {
        packagesTab.click();
      }
    }
  }

  // New component methods

  showPluginManager() {
    console.log('showPluginManager method called');

    try {
      if (window.pluginMarketplace && typeof window.pluginMarketplace.show === 'function') {
        window.pluginMarketplace.show();
      } else {
        console.error('Plugin manager not available');
        this.showError('Plugin Manager', { message: 'Plugin manager is not available.' });
      }
    } catch (error) {
      console.error('Error showing plugin manager:', error);
      this.showError('Error showing plugin manager', error);
    }
  }

  showProjectManager() {
    console.log('showProjectManager method called');

    try {
      if (window.projectManager && typeof window.projectManager.show === 'function') {
        window.projectManager.show();
      } else {
        console.error('Project manager not available');
        this.showError('Project Manager', { message: 'Project manager is not available.' });
      }
    } catch (error) {
      console.error('Error showing project manager:', error);
      this.showError('Error showing project manager', error);
    }
  }

  showThemeEditor() {
    console.log('showThemeEditor method called');

    try {
      if (window.themeEditor && typeof window.themeEditor.show === 'function') {
        window.themeEditor.show();
      } else {
        console.error('Theme editor not available');
        this.showError('Theme Editor', { message: 'Theme editor is not available.' });
      }
    } catch (error) {
      console.error('Error showing theme editor:', error);
      this.showError('Error showing theme editor', error);
    }
  }

  toggleEnhancedAI() {
    console.log('toggleEnhancedAI method called');

    try {
      if (window.enhancedAIAssistant && typeof window.enhancedAIAssistant.toggle === 'function') {
        window.enhancedAIAssistant.toggle();
      } else {
        console.error('Enhanced AI assistant not available');
        this.showError('Enhanced AI Assistant', { message: 'Enhanced AI assistant is not available.' });
      }
    } catch (error) {
      console.error('Error toggling enhanced AI assistant:', error);
      this.showError('Error toggling enhanced AI assistant', error);
    }
  }

  // Debug methods
  startDebugging() {
    if (window.debuggerManager) {
      window.debuggerManager.startDebugging();
    }
  }

  stopDebugging() {
    if (window.debuggerManager) {
      window.debuggerManager.stopDebugging();
    }
  }

  restartDebugging() {
    if (window.debuggerManager) {
      window.debuggerManager.restartDebugging();
    }
  }

  continueDebugging() {
    if (window.debuggerManager) {
      window.debuggerManager.continueExecution();
    }
  }

  stepOver() {
    if (window.debuggerManager) {
      window.debuggerManager.stepOver();
    }
  }

  stepInto() {
    if (window.debuggerManager) {
      window.debuggerManager.stepInto();
    }
  }

  stepOut() {
    if (window.debuggerManager) {
      window.debuggerManager.stepOut();
    }
  }

  toggleBreakpoint() {
    if (window.debuggerManager && window.editorManager) {
      const activeEditor = window.editorManager.getActiveEditor();
      if (activeEditor) {
        const position = activeEditor.editor.getPosition();
        window.debuggerManager.toggleBreakpoint(activeEditor.filePath, position.lineNumber);
      }
    }
  }

  clearBreakpoints() {
    if (window.debuggerManager) {
      window.debuggerManager.clearAllBreakpoints();
    }
  }
}

// Global variables for managers
// Note: We'll use window.editorManager to access the editor manager
// that's already initialized in editor.js
// We're not declaring editorManager here to avoid duplicate declarations
// We're also not declaring terminalManager here as it's already initialized in terminal.js
// We're also not declaring themeManager here as it's already initialized in themes.js
// We're also not declaring fileExplorer here as it's already initialized in explorer.js
// We're also not declaring aiAssistant here as it's already initialized in ai-assistant.js
// We're also not declaring debuggerManager here as it's already initialized in debugger.js
let explorerManager;
let settingsManager;

// Initialize the application when the page loads
let app;
document.addEventListener('DOMContentLoaded', () => {
  // Show splash screen
  const splash = new SplashScreen().show();

  // Function to check if API is ready with more comprehensive checks
  const checkApiReady = async () => {
    console.log('Checking API readiness...');

    // Basic check for API existence
    if (!window.api) {
      console.error('API not available: window.api is undefined');
      return false;
    }

    // Check for required API methods
    const requiredMethods = [
      'openFolder', 'openFile', 'saveFileAs', 'readFile', 'writeFile',
      'readDirectory', 'testApi'
    ];

    const missingMethods = requiredMethods.filter(method => typeof window.api[method] !== 'function');

    if (missingMethods.length > 0) {
      console.error('API not fully available. Missing methods:', missingMethods);
      return false;
    }

    // Try to call the test API function
    try {
      console.log('Testing API connection...');
      const testResult = await window.api.testApi();
      console.log('API test result:', testResult);

      if (!testResult.success) {
        console.error('API test failed:', testResult.message);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error testing API:', error);
      return false;
    }
  };

  // Function to initialize the application with better error handling
  const initializeApp = async () => {
    try {
      console.log('Initializing application...');

      // Add console logs to help debug DOM elements
      console.log('Terminal container:', document.getElementById('terminal-container'));
      console.log('Terminal tabs:', document.getElementById('terminal-tabs'));
      console.log('Terminal view tabs:', document.querySelectorAll('.terminal-view-tab'));

      // Initialize managers in a specific order to handle dependencies
      console.log('Initializing theme manager...');
      // Theme manager is already initialized in themes.js
      if (!window.themeManager && typeof ThemeManager !== 'undefined') {
        console.log('Creating new theme manager instance');
        window.themeManager = new ThemeManager();
      } else if (!window.themeManager) {
        console.error('ThemeManager class is not defined and window.themeManager is not available');
      } else {
        console.log('Using existing theme manager instance');
      }

      console.log('Initializing editor manager...');
      // Use the editorManager from editor.js if available, otherwise create a new one
      if (window.editorManager) {
        console.log('Using existing editor manager instance');
      } else if (typeof EditorManager !== 'undefined') {
        window.editorManager = new EditorManager();
        console.log('Created new editor manager instance');
      } else {
        console.error('EditorManager class is not defined');
      }

      console.log('Initializing file explorer...');
      // Initialize file explorer if not already initialized
      if (!window.fileExplorer && typeof FileExplorer !== 'undefined') {
        console.log('Creating new file explorer instance');
        window.fileExplorer = new FileExplorer();
      } else if (!window.fileExplorer) {
        console.error('FileExplorer class is not defined and window.fileExplorer is not available');
      } else {
        console.log('Using existing file explorer instance');
      }

      console.log('Initializing terminal manager...');
      // Terminal manager is already initialized in terminal.js
      // Use the global window.terminalManager instance
      if (!window.terminalManager && typeof TerminalManager !== 'undefined') {
        console.log('Creating new terminal manager instance');
        window.terminalManager = new TerminalManager();
      } else if (!window.terminalManager) {
        console.error('TerminalManager class is not defined and window.terminalManager is not available');
      } else {
        console.log('Using existing terminal manager instance');
      }

      console.log('Initializing settings manager...');
      settingsManager = new SettingsManager();

      console.log('Initializing debugger manager...');
      // Debugger manager is already initialized in debugger.js
      if (!window.debuggerManager && typeof MonoDebugger !== 'undefined') {
        console.log('Creating new debugger manager instance');
        window.debuggerManager = new MonoDebugger();
      } else if (!window.debuggerManager) {
        console.error('MonoDebugger class is not defined and window.debuggerManager is not available');
      } else {
        console.log('Using existing debugger manager instance');
      }

      console.log('Initializing AI assistant...');
      // AI assistant is already initialized in ai-assistant.js
      if (!window.aiAssistant && typeof AIAssistant !== 'undefined') {
        console.log('Creating new AI assistant instance');
        window.aiAssistant = new AIAssistant();
      } else if (!window.aiAssistant) {
        console.error('AIAssistant class is not defined and window.aiAssistant is not available');
      } else {
        console.log('Using existing AI assistant instance');
      }

      // Initialize the app
      console.log('Initializing main application...');
      app = new MonoEditor();

      // Set up error notification handler
      if (window.api && typeof window.api.onErrorNotification === 'function') {
        window.api.onErrorNotification((data) => {
          console.log('Received error notification:', data);

          // Show error in status bar
          const statusBar = document.querySelector('.status-left');
          if (statusBar) {
            const statusElement = document.createElement('span');
            statusElement.id = 'status-error';
            statusElement.textContent = data.title || 'Error';
            statusElement.style.color = '#F44336';
            statusElement.title = data.message || '';

            // Remove existing error status if any
            const existingStatus = document.getElementById('status-error');
            if (existingStatus) {
              existingStatus.remove();
            }

            statusBar.appendChild(statusElement);

            // Remove the status after 10 seconds
            setTimeout(() => {
              if (statusElement.parentNode) {
                statusElement.remove();
              }
            }, 10000);
          }

          // Show alert for critical errors
          if (data.critical) {
            alert(`${data.title}: ${data.message}`);
          }
        });
        console.log('Error notification handler registered');
      } else {
        console.warn('Error notification API not available');
      }

      // Hide splash screen
      splash.hide();

      console.log('Application initialized successfully');

      // Show a success message in the status bar
      const statusBar = document.querySelector('.status-left');
      if (statusBar) {
        const statusElement = document.createElement('span');
        statusElement.id = 'status-ready';
        statusElement.textContent = 'Ready';
        statusElement.style.color = '#4CAF50';

        // Remove existing status if any
        const existingStatus = document.getElementById('status-ready');
        if (existingStatus) {
          existingStatus.remove();
        }

        statusBar.appendChild(statusElement);

        // Remove the status after 5 seconds
        setTimeout(() => {
          if (statusElement.parentNode) {
            statusElement.remove();
          }
        }, 5000);
      }
    } catch (error) {
      console.error('Error initializing application:', error);

      // Show error in status bar
      const statusBar = document.querySelector('.status-left');
      if (statusBar) {
        const statusElement = document.createElement('span');
        statusElement.id = 'status-error';
        statusElement.textContent = 'Initialization Error';
        statusElement.style.color = '#F44336';
        statusElement.title = error.message;

        // Remove existing status if any
        const existingStatus = document.getElementById('status-error');
        if (existingStatus) {
          existingStatus.remove();
        }

        statusBar.appendChild(statusElement);
      }

      alert(`Error initializing application: ${error.message}. Please restart the application.`);
      splash.hide();
    }
  };

  // Wait for API to be ready with a timeout and better retry logic
  let attempts = 0;
  const maxAttempts = 20; // Increase max attempts
  const checkInterval = 300; // 300ms between checks
  const maxWaitTime = 10000; // 10 seconds total wait time

  const apiReadyCheck = async () => {
    attempts++;
    console.log(`Checking API readiness (attempt ${attempts}/${maxAttempts})...`);

    try {
      const isReady = await checkApiReady();

      if (isReady) {
        console.log('API is ready, initializing application');
        initializeApp();
        return;
      }

      if (attempts >= maxAttempts) {
        console.error('API not available after maximum attempts');
        alert('Application initialization error: API not available. Please restart the application.');
        splash.hide();
        return;
      }

      // Exponential backoff for retries
      const delay = Math.min(checkInterval * Math.pow(1.5, attempts - 1), 2000);
      console.log(`Retrying in ${delay}ms...`);

      setTimeout(apiReadyCheck, delay);
    } catch (error) {
      console.error('Error in API ready check:', error);

      if (attempts >= maxAttempts) {
        alert(`Application initialization error: ${error.message}. Please restart the application.`);
        splash.hide();
        return;
      }

      setTimeout(apiReadyCheck, checkInterval);
    }
  };

  // Start the API ready check
  setTimeout(apiReadyCheck, 500); // Give a little time for the preload script to run
});
