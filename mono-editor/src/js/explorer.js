// File Explorer for Mono Editor

// Path module for handling file paths
const path = {
  // Normalize path separators to forward slashes
  normalize: (filePath) => {
    if (!filePath) return '';
    // Replace backslashes with forward slashes
    return filePath.replace(/\\/g, '/');
  },

  // Join path segments, handling both forward and backslashes
  join: (...parts) => {
    if (!parts || parts.length === 0) return '';

    // Filter out empty parts
    const filteredParts = parts.filter(part => part && part.trim() !== '');
    if (filteredParts.length === 0) return '';

    // Normalize each part and join with forward slashes
    const normalized = filteredParts.map(part => part.replace(/^\/+|\/+$/g, ''));
    return normalized.join('/').replace(/\/+/g, '/');
  },

  // Get the last part of a path (filename or directory name)
  basename: (filePath) => {
    if (!filePath) return '';

    // Normalize path and split by slashes
    const normalized = filePath.replace(/\\/g, '/');
    const parts = normalized.split('/').filter(Boolean);

    return parts.length > 0 ? parts[parts.length - 1] : '';
  },

  // Get the directory part of a path
  dirname: (filePath) => {
    if (!filePath) return '';

    // Normalize path and split by slashes
    const normalized = filePath.replace(/\\/g, '/');
    const parts = normalized.split('/').filter(Boolean);

    // If there's only one part, return empty string or root
    if (parts.length <= 1) {
      return normalized.startsWith('/') ? '/' : '';
    }

    // Remove the last part and join the rest
    parts.pop();
    const result = parts.join('/');

    // Preserve leading slash if it was present
    return normalized.startsWith('/') ? `/${result}` : result;
  },

  // Check if a path is absolute
  isAbsolute: (filePath) => {
    if (!filePath) return false;

    // Normalize path
    const normalized = filePath.replace(/\\/g, '/');

    // Check if it starts with a slash or drive letter (Windows)
    return normalized.startsWith('/') || /^[A-Za-z]:/.test(normalized);
  }
};

class FileExplorer {
  constructor() {
    console.log('Initializing FileExplorer...');
    this.explorerElement = document.getElementById('file-explorer');
    if (!this.explorerElement) {
      console.error('File explorer element not found in the DOM');
      throw new Error('File explorer element not found');
    }

    this.currentFolder = null;
    this.fileTree = null;
    this.initialized = false;

    // Initialize event listeners
    this.initEventListeners();
    console.log('FileExplorer initialized');
    this.initialized = true;
  }

  initEventListeners() {
    try {
      console.log('Setting up FileExplorer event listeners...');

      // Open folder button in the sidebar
      const openFolderBtn = document.getElementById('open-folder-btn');
      if (openFolderBtn) {
        openFolderBtn.addEventListener('click', () => {
          console.log('Open folder button clicked');
          this.openFolder();
        });
      } else {
        console.warn('Open folder button not found in the DOM');
      }

      // Open folder button in empty explorer
      const emptyBtn = document.getElementById('open-folder-empty-btn');
      if (emptyBtn) {
        emptyBtn.addEventListener('click', () => {
          console.log('Empty explorer open folder button clicked');
          this.openFolder();
        });
      } else {
        console.warn('Empty explorer open folder button not found in the DOM');
      }

      // Collapse all button
      const collapseAllBtn = document.getElementById('collapse-all-btn');
      if (collapseAllBtn) {
        collapseAllBtn.addEventListener('click', () => {
          console.log('Collapse all button clicked');
          this.collapseAll();
        });
      } else {
        console.warn('Collapse all button not found in the DOM');
      }

      // Add event listener for welcome screen open folder button
      const welcomeOpenFolder = document.getElementById('welcome-open-folder');
      if (welcomeOpenFolder) {
        welcomeOpenFolder.addEventListener('click', () => {
          console.log('Welcome screen open folder button clicked');
          this.openFolder();
        });
      }

      console.log('FileExplorer event listeners set up successfully');
    } catch (error) {
      console.error('Error setting up FileExplorer event listeners:', error);
    }
  }

  async openFolder() {
    console.log('EXPLORER: openFolder method called');

    // Return a promise to allow better integration with app.js
    return new Promise(async (resolve, reject) => {
      try {
        // Check if the explorer is initialized
        if (!this.initialized) {
          console.error('EXPLORER: FileExplorer not fully initialized');
          reject(new Error('File explorer is not fully initialized. Please try again in a moment.'));
          return;
        }

        // Show loading indicator early to provide feedback
        this.showLoadingIndicator();

        // Verify API availability with more detailed logging
        if (!window.api) {
          console.error('EXPLORER: window.api is undefined');
          console.log('EXPLORER: window object keys:', Object.keys(window));
          throw new Error('API not available. The application may not be fully initialized.');
        }

        // Log all available API methods for debugging
        console.log('EXPLORER: Available API methods:', Object.keys(window.api));

        // Verify openFolder method exists
        if (typeof window.api.openFolder !== 'function') {
          console.error('EXPLORER: window.api.openFolder is not a function', window.api);
          throw new Error('openFolder function not available. The application may not be fully initialized.');
        }

        // Test API connection before proceeding
        try {
          const apiTest = await window.api.testApi();
          console.log('EXPLORER: API test result:', apiTest);
          if (!apiTest.success) {
            throw new Error(`API test failed: ${apiTest.message}`);
          }
        } catch (testError) {
          console.error('EXPLORER: API test failed:', testError);
          // Continue anyway, as the test might fail but the API could still work
        }

        // Call openFolder with timeout and retry logic
        console.log('EXPLORER: Calling window.api.openFolder()...');

        // Create a promise with timeout
        const folderPathPromise = new Promise(async (resolveFolder, rejectFolder) => {
          try {
            const result = await window.api.openFolder();
            resolveFolder(result);
          } catch (err) {
            console.error('EXPLORER: Error in openFolder call:', err);
            rejectFolder(err);
          }
        });

        // Add timeout to the promise
        const timeoutPromise = new Promise((_, rejectTimeout) => {
          setTimeout(() => rejectTimeout(new Error('Folder selection timed out after 30 seconds')), 30000);
        });

        // Race the promises
        const folderPath = await Promise.race([folderPathPromise, timeoutPromise]);
        console.log('EXPLORER: openFolder result:', folderPath);

        if (!folderPath) {
          console.log('EXPLORER: User cancelled folder selection or no result returned');
          this.hideLoadingIndicator();
          resolve(); // User cancelled or no result, but not an error
          return;
        }

        // Normalize the folder path
        this.currentFolder = path.normalize(folderPath);
        console.log('EXPLORER: Normalized folder path:', this.currentFolder);

        // Refresh the file tree
        console.log('EXPLORER: Refreshing file tree...');
        await this.refreshFileTree();
        console.log('EXPLORER: File tree refreshed successfully');

        // Hide loading indicator
        this.hideLoadingIndicator();

        // Update status to indicate success
        const statusBar = document.querySelector('.status-left');
        if (statusBar) {
          const statusElement = document.createElement('span');
          statusElement.id = 'status-folder';
          statusElement.textContent = `Folder: ${this.getShortPath(this.currentFolder)}`;
          statusElement.title = this.currentFolder;

          // Remove existing folder status if any
          const existingStatus = document.getElementById('status-folder');
          if (existingStatus) {
            existingStatus.remove();
          }

          statusBar.appendChild(statusElement);
        }

        // Resolve the promise to indicate success
        resolve(this.currentFolder);
      } catch (error) {
        console.error('EXPLORER: Error opening folder:', error);
        this.showError(`Error opening folder: ${error.message}`);
        this.hideLoadingIndicator();

        // Reset the explorer to a clean state
        this.resetExplorer();

        // Reject the promise with the error
        reject(error);
      }
    });
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

  // Reset the explorer to a clean state
  resetExplorer() {
    console.log('Resetting explorer to clean state');
    this.currentFolder = null;

    if (this.explorerElement) {
      this.explorerElement.innerHTML = '';
      const emptyExplorer = document.createElement('div');
      emptyExplorer.className = 'empty-explorer';
      emptyExplorer.innerHTML = `
        <p>No folder opened</p>
        <button id="open-folder-empty-btn">Open Folder</button>
        <div style="margin-top: 20px;">
          <button id="test-api-btn" style="background-color: #007acc;">Test API</button>
          <div id="api-test-result" style="margin-top: 10px; font-size: 12px;"></div>
        </div>
      `;
      this.explorerElement.appendChild(emptyExplorer);

      // Re-add event listener to the button
      const emptyBtn = document.getElementById('open-folder-empty-btn');
      if (emptyBtn) {
        emptyBtn.addEventListener('click', () => {
          this.openFolder();
        });
      }

      // Add test API button event listener
      const testApiBtn = document.getElementById('test-api-btn');
      if (testApiBtn) {
        testApiBtn.addEventListener('click', () => {
          this.testApi();
        });
      }
    }
  }

  // Test API function to help diagnose issues
  async testApi() {
    console.log('EXPLORER: Testing API...');
    const resultDiv = document.getElementById('api-test-result');
    if (!resultDiv) return;

    resultDiv.innerHTML = 'Testing API...';

    try {
      // Check if window.api exists
      if (!window.api) {
        resultDiv.innerHTML = 'ERROR: window.api is undefined';
        return;
      }

      // Log available API methods
      const apiMethods = Object.keys(window.api);
      console.log('EXPLORER: Available API methods:', apiMethods);

      // Check if openFolder method exists
      if (typeof window.api.openFolder !== 'function') {
        resultDiv.innerHTML = 'ERROR: window.api.openFolder is not a function';
        return;
      }

      // Try to call the openFolder method
      resultDiv.innerHTML = 'Calling window.api.openFolder()...';
      const result = await window.api.openFolder();

      if (result) {
        resultDiv.innerHTML = `SUCCESS: Selected folder: ${result}`;
      } else {
        resultDiv.innerHTML = 'INFO: No folder selected or dialog canceled';
      }
    } catch (error) {
      console.error('EXPLORER: Error testing API:', error);
      resultDiv.innerHTML = `ERROR: ${error.message}`;
    }
  }

  showLoadingIndicator() {
    // Remove any existing loading indicator
    this.hideLoadingIndicator();

    // Create loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'explorer-loading';
    loadingIndicator.innerHTML = `
      <div class="spinner"></div>
      <div class="loading-text">Loading...</div>
    `;

    // Add to explorer
    this.explorerElement.appendChild(loadingIndicator);
  }

  hideLoadingIndicator() {
    const loadingIndicator = this.explorerElement.querySelector('.explorer-loading');
    if (loadingIndicator) {
      loadingIndicator.remove();
    }
  }

  showError(message) {
    // Create error message element
    const errorElement = document.createElement('div');
    errorElement.className = 'explorer-error';
    errorElement.innerHTML = `
      <div class="error-icon">⚠️</div>
      <div class="error-message">${message}</div>
      <button class="error-dismiss">Dismiss</button>
    `;

    // Add dismiss button handler
    errorElement.querySelector('.error-dismiss').addEventListener('click', () => {
      errorElement.remove();
    });

    // Add to explorer
    this.explorerElement.appendChild(errorElement);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      if (errorElement.parentNode) {
        errorElement.remove();
      }
    }, 5000);
  }

  async refreshFileTree() {
    console.log('refreshFileTree called');

    if (!this.currentFolder) {
      console.warn('No current folder set, cannot refresh file tree');
      return;
    }

    if (!this.explorerElement) {
      console.error('Explorer element not found');
      return;
    }

    try {
      console.log(`Reading directory: ${this.currentFolder}`);

      // Check if API is available
      if (!window.api || typeof window.api.readDirectory !== 'function') {
        throw new Error('API not available or readDirectory function missing');
      }

      // Read the directory
      const items = await window.api.readDirectory(this.currentFolder);
      console.log(`Found ${items.length} items in directory`);

      // Clear the explorer
      this.explorerElement.innerHTML = '';

      // Create the file tree
      this.fileTree = document.createElement('ul');
      this.fileTree.className = 'file-tree';

      // Add folder path display
      const pathDisplay = document.createElement('div');
      pathDisplay.className = 'folder-path-display';
      pathDisplay.textContent = this.currentFolder;
      pathDisplay.title = this.currentFolder;

      // Add refresh button
      const refreshButton = document.createElement('button');
      refreshButton.className = 'refresh-button';
      refreshButton.innerHTML = '↻';
      refreshButton.title = 'Refresh';
      refreshButton.addEventListener('click', async (e) => {
        e.preventDefault();
        console.log('Refresh button clicked');
        this.showLoadingIndicator();
        await this.refreshFileTree();
        this.hideLoadingIndicator();
      });

      // Add path container
      const pathContainer = document.createElement('div');
      pathContainer.className = 'folder-path-container';
      pathContainer.appendChild(pathDisplay);
      pathContainer.appendChild(refreshButton);

      this.explorerElement.appendChild(pathContainer);
      this.explorerElement.appendChild(this.fileTree);

      // Sort items: directories first, then files
      items.sort((a, b) => {
        if (a.isDirectory && !b.isDirectory) return -1;
        if (!a.isDirectory && b.isDirectory) return 1;
        return a.name.localeCompare(b.name);
      });

      // Process items to ensure paths are normalized
      const processedItems = items.map(item => ({
        ...item,
        path: path.normalize(item.path),
        name: path.basename(item.path)
      }));

      console.log(`Processed ${processedItems.length} items`);

      // Add items to the tree
      if (processedItems.length === 0) {
        // Show empty folder message
        const emptyMessage = document.createElement('div');
        emptyMessage.className = 'empty-folder-message';
        emptyMessage.textContent = 'This folder is empty';
        this.explorerElement.appendChild(emptyMessage);
        console.log('Folder is empty');
      } else {
        console.log('Adding items to tree...');
        for (const item of processedItems) {
          await this.addItemToTree(this.fileTree, item);
        }
        console.log('All items added to tree');
      }
    } catch (error) {
      console.error('Error refreshing file tree:', error);
      this.showError(`Error refreshing file tree: ${error.message}`);

      // Reset to empty explorer view
      this.resetExplorer();
    }
  }

  async addItemToTree(parentElement, item) {
    const li = document.createElement('li');
    li.className = 'file-tree-item';
    li.dataset.path = item.path;

    if (item.isDirectory) {
      li.classList.add('directory');
    }

    const itemContent = document.createElement('div');
    itemContent.className = 'file-tree-item-content';

    if (item.isDirectory) {
      // Add expander for directories
      const expander = document.createElement('span');
      expander.className = 'file-tree-item-expander';
      expander.addEventListener('click', async (e) => {
        e.stopPropagation();
        await this.toggleDirectory(li, item);
      });
      itemContent.appendChild(expander);

      // Add icon
      const icon = document.createElement('span');
      icon.className = 'file-tree-item-icon folder';
      itemContent.appendChild(icon);

      // Add name
      const name = document.createElement('span');
      name.className = 'file-tree-item-name';
      name.textContent = item.name;
      itemContent.appendChild(name);

      // Add context menu
      this.addContextMenu(itemContent, item, true);

      // Add click handler to expand/collapse
      itemContent.addEventListener('click', async (e) => {
        e.stopPropagation();
        await this.toggleDirectory(li, item);
      });

      // Add children container
      const children = document.createElement('ul');
      children.className = 'file-tree-item-children';
      li.appendChild(children);
    } else {
      // Add spacer for files (to align with directories)
      const spacer = document.createElement('span');
      spacer.className = 'file-tree-item-expander';
      spacer.style.visibility = 'hidden';
      itemContent.appendChild(spacer);

      // Add icon based on file extension
      const icon = document.createElement('span');
      icon.className = this.getFileIconClass(item.name);
      itemContent.appendChild(icon);

      // Add name
      const name = document.createElement('span');
      name.className = 'file-tree-item-name';
      name.textContent = item.name;
      itemContent.appendChild(name);

      // Add context menu
      this.addContextMenu(itemContent, item, false);

      // Add click handler to open file
      itemContent.addEventListener('click', (e) => {
        e.stopPropagation();
        this.openFile(item, itemContent);
      });
    }

    li.appendChild(itemContent);
    parentElement.appendChild(li);
  }

  async toggleDirectory(li, item) {
    console.log(`Toggling directory: ${item.path}`);

    // Toggle expanded state
    const wasExpanded = li.classList.contains('expanded');
    li.classList.toggle('expanded');
    const isNowExpanded = li.classList.contains('expanded');

    console.log(`Directory was ${wasExpanded ? 'expanded' : 'collapsed'}, now ${isNowExpanded ? 'expanded' : 'collapsed'}`);

    // Update icon
    const icon = li.querySelector('.file-tree-item-icon');
    if (icon) {
      icon.className = isNowExpanded
        ? 'file-tree-item-icon folder-open'
        : 'file-tree-item-icon folder';
    }

    // Load children if not already loaded and directory is being expanded
    const children = li.querySelector('.file-tree-item-children');
    if (children && children.children.length === 0 && isNowExpanded) {
      console.log(`Loading children for directory: ${item.path}`);

      // Add loading indicator to the directory item
      const loadingIndicator = document.createElement('div');
      loadingIndicator.className = 'directory-loading-indicator';
      loadingIndicator.innerHTML = '<div class="spinner small"></div>';
      li.appendChild(loadingIndicator);

      try {
        // Check if API is available
        if (!window.api || typeof window.api.readDirectory !== 'function') {
          throw new Error('API not available or readDirectory function missing');
        }

        const childItems = await window.api.readDirectory(item.path);
        console.log(`Found ${childItems.length} items in directory: ${item.path}`);

        // Sort items: directories first, then files
        childItems.sort((a, b) => {
          if (a.isDirectory && !b.isDirectory) return -1;
          if (!a.isDirectory && b.isDirectory) return 1;
          return a.name.localeCompare(b.name);
        });

        // Add child items
        for (const childItem of childItems) {
          await this.addItemToTree(children, childItem);
        }

        // If no children were found, show an empty message
        if (childItems.length === 0) {
          const emptyMessage = document.createElement('li');
          emptyMessage.className = 'empty-directory-message';
          emptyMessage.textContent = 'Empty folder';
          children.appendChild(emptyMessage);
        }

        console.log(`Successfully loaded children for directory: ${item.path}`);
      } catch (error) {
        console.error(`Error loading directory ${item.path}:`, error);

        // Show error message in the directory
        const errorMessage = document.createElement('li');
        errorMessage.className = 'directory-error-message';
        errorMessage.textContent = `Error: ${error.message}`;
        children.appendChild(errorMessage);

        // Add a retry button
        const retryButton = document.createElement('button');
        retryButton.className = 'directory-retry-button';
        retryButton.textContent = 'Retry';
        retryButton.addEventListener('click', async (e) => {
          e.stopPropagation();
          // Clear children and try again
          children.innerHTML = '';
          await this.toggleDirectory(li, item);
        });
        errorMessage.appendChild(retryButton);
      } finally {
        // Remove loading indicator
        if (loadingIndicator && loadingIndicator.parentNode) {
          loadingIndicator.parentNode.removeChild(loadingIndicator);
        }
      }
    }
  }

  openFile(item, itemContent) {
    console.log(`Opening file: ${item.path}`);

    // Validate the item path
    if (!item || !item.path) {
      console.error('Invalid file item or path');
      return;
    }

    // Open the file in the editor
    if (window.editorManager) {
      try {
        window.editorManager.openFile(item.path)
          .then(tabId => {
            console.log(`File opened successfully in tab: ${tabId}`);
          })
          .catch(error => {
            console.error(`Error opening file: ${error.message}`);
            alert(`Error opening file: ${error.message}`);
          });
      } catch (error) {
        console.error(`Error calling openFile: ${error.message}`);
        alert(`Error opening file: ${error.message}`);
      }
    } else {
      console.error('Editor manager not available');
      alert('Editor not ready. Please try again in a moment.');
    }

    // Mark as active
    const activeItems = this.fileTree.querySelectorAll('.file-tree-item-content.active');
    activeItems.forEach(el => el.classList.remove('active'));
    itemContent.classList.add('active');
  }

  addContextMenu(element, item, isDirectory) {
    element.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      e.stopPropagation();

      // Remove any existing context menus
      const existingMenu = document.querySelector('.context-menu');
      if (existingMenu) {
        existingMenu.remove();
      }

      // Create context menu
      const contextMenu = document.createElement('div');
      contextMenu.className = 'context-menu';

      // Position the menu
      contextMenu.style.left = `${e.clientX}px`;
      contextMenu.style.top = `${e.clientY}px`;

      // Add menu items
      if (isDirectory) {
        // Directory context menu items
        this.addContextMenuItem(contextMenu, 'New File', () => {
          this.createNewFile(item.path);
        });

        this.addContextMenuItem(contextMenu, 'New Folder', () => {
          this.createNewFolder(item.path);
        });

        this.addContextMenuItem(contextMenu, 'Rename', () => {
          this.renameItem(item.path, isDirectory);
        });

        this.addContextMenuItem(contextMenu, 'Delete', () => {
          this.deleteItem(item.path, isDirectory);
        });
      } else {
        // File context menu items
        this.addContextMenuItem(contextMenu, 'Open', () => {
          this.openFile(item, element);
        });

        this.addContextMenuItem(contextMenu, 'Rename', () => {
          this.renameItem(item.path, isDirectory);
        });

        this.addContextMenuItem(contextMenu, 'Delete', () => {
          this.deleteItem(item.path, isDirectory);
        });
      }

      // Add the menu to the document
      document.body.appendChild(contextMenu);

      // Close the menu when clicking outside
      const closeMenu = (e) => {
        if (!contextMenu.contains(e.target)) {
          contextMenu.remove();
          document.removeEventListener('click', closeMenu);
        }
      };

      // Add a small delay to prevent immediate closing
      setTimeout(() => {
        document.addEventListener('click', closeMenu);
      }, 100);
    });
  }

  addContextMenuItem(menu, label, callback) {
    const item = document.createElement('div');
    item.className = 'context-menu-item';
    item.textContent = label;
    item.addEventListener('click', callback);
    menu.appendChild(item);
  }

  // File operations implementation
  async createNewFile(dirPath) {
    try {
      // Prompt for file name
      const fileName = prompt('Enter file name:', 'new_file.mono');
      if (!fileName) return; // User cancelled

      // Create full path
      const filePath = path.join(dirPath, fileName);

      // Create the file
      await window.api.createFile(filePath, '');

      // Refresh the file tree
      await this.refreshFileTree();

      // Open the new file
      if (editorManager) {
        editorManager.openFile(filePath);
      }
    } catch (error) {
      console.error('Error creating file:', error);
      alert(`Error creating file: ${error.message}`);
    }
  }

  async createNewFolder(dirPath) {
    try {
      // Prompt for folder name
      const folderName = prompt('Enter folder name:', 'new_folder');
      if (!folderName) return; // User cancelled

      // Create full path
      const newDirPath = path.join(dirPath, folderName);

      // Create the directory
      await window.api.createDirectory(newDirPath);

      // Refresh the file tree
      await this.refreshFileTree();
    } catch (error) {
      console.error('Error creating folder:', error);
      alert(`Error creating folder: ${error.message}`);
    }
  }

  async renameItem(itemPath, isDirectory) {
    try {
      // Get the current name
      const currentName = path.basename(itemPath);

      // Prompt for new name
      const newName = prompt('Enter new name:', currentName);
      if (!newName || newName === currentName) return; // User cancelled or no change

      // Create new path
      const dirPath = path.dirname(itemPath);
      const newPath = path.join(dirPath, newName);

      // Rename the item
      await window.api.renameItem(itemPath, newPath);

      // Refresh the file tree
      await this.refreshFileTree();

      // If it's a file and it's open in the editor, update the editor
      if (!isDirectory && editorManager) {
        editorManager.handleFileRenamed(itemPath, newPath);
      }
    } catch (error) {
      console.error('Error renaming item:', error);
      alert(`Error renaming item: ${error.message}`);
    }
  }

  async deleteItem(itemPath, isDirectory) {
    try {
      // Confirm deletion
      const itemType = isDirectory ? 'folder' : 'file';
      const itemName = path.basename(itemPath);
      const confirmed = confirm(`Are you sure you want to delete the ${itemType} "${itemName}"?`);
      if (!confirmed) return;

      // Delete the item
      await window.api.deleteItem(itemPath, isDirectory);

      // Refresh the file tree
      await this.refreshFileTree();

      // If it's a file and it's open in the editor, close the tab
      if (!isDirectory && editorManager) {
        editorManager.handleFileDeleted(itemPath);
      }
    } catch (error) {
      console.error('Error deleting item:', error);
      alert(`Error deleting item: ${error.message}`);
    }
  }

  getFileIconClass(fileName) {
    const extension = fileName.split('.').pop().toLowerCase();

    if (extension === 'mono') {
      return 'file-tree-item-icon file-mono';
    }

    // Add more file type icons as needed
    return 'file-tree-item-icon file';
  }

  collapseAll() {
    if (!this.fileTree) return;

    const expandedItems = this.fileTree.querySelectorAll('.file-tree-item.expanded');
    expandedItems.forEach(item => {
      item.classList.remove('expanded');

      // Update folder icons
      const icon = item.querySelector('.file-tree-item-icon.folder-open');
      if (icon) {
        icon.className = 'file-tree-item-icon folder';
      }
    });
  }
}

// FileExplorer will be initialized in app.js
// Using window.fileExplorer to avoid duplicate declarations
