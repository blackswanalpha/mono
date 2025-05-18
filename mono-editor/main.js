const { app, BrowserWindow, ipcMain, dialog, Menu, shell } = require('electron');
const path = require('path');
const fs = require('fs-extra');
const { spawn } = require('child_process');
const os = require('os');

// Keep a global reference of the window object to avoid garbage collection
let mainWindow;
let splashWindow;
let isDevMode = process.argv.includes('--dev');

// Add command line switches to help with rendering issues
app.commandLine.appendSwitch('disable-gpu-vsync');
app.commandLine.appendSwitch('disable-frame-rate-limit');
app.commandLine.appendSwitch('disable-gpu-compositing');
app.commandLine.appendSwitch('disable-software-rasterizer');

// Create the main application window
function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false, // Keep Node.js isolated from the renderer for security
      contextIsolation: true, // Enable context isolation for security
      enableRemoteModule: false, // Disable remote module as it's deprecated
      preload: path.join(__dirname, 'preload.js'),
      // Add GPU-related settings to help with rendering issues
      offscreen: false,
      backgroundThrottling: false,
      // Disable sandbox to allow Node.js modules in preload script
      sandbox: false,
      // Allow the preload script to access Node.js APIs
      worldSafeExecuteJavaScript: true
    },
    // Add GPU-related settings to help with rendering issues
    paintWhenInitiallyHidden: true,
    icon: path.join(__dirname, 'assets/icons/png/512x512.png'),
    show: false, // Don't show until ready-to-show
    backgroundColor: '#1e1e1e' // Dark background to prevent white flash
  });

  console.log('Main process: Main window created with preload script:', path.join(__dirname, 'preload.js'));

  // Disable frame rate limiting
  mainWindow.webContents.setFrameRate(60);

  // Load the index.html file
  mainWindow.loadFile('src/index.html');

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create application menu
  createMenu();
}

// Create the application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New File',
          accelerator: 'CmdOrCtrl+N',
          click: () => mainWindow.webContents.send('menu-new-file')
        },
        {
          label: 'Open File...',
          accelerator: 'CmdOrCtrl+O',
          click: () => mainWindow.webContents.send('menu-open-file')
        },
        {
          label: 'Open Folder...',
          accelerator: 'CmdOrCtrl+Shift+O',
          click: () => mainWindow.webContents.send('menu-open-folder')
        },
        { type: 'separator' },
        {
          label: 'Save',
          accelerator: 'CmdOrCtrl+S',
          click: () => mainWindow.webContents.send('menu-save')
        },
        {
          label: 'Save As...',
          accelerator: 'CmdOrCtrl+Shift+S',
          click: () => mainWindow.webContents.send('menu-save-as')
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: 'Alt+F4',
          click: () => app.quit()
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'delete' },
        { type: 'separator' },
        { role: 'selectAll' }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Toggle File Explorer',
          accelerator: 'CmdOrCtrl+B',
          click: () => mainWindow.webContents.send('menu-toggle-explorer')
        },
        {
          label: 'Toggle Terminal',
          accelerator: 'CmdOrCtrl+`',
          click: () => mainWindow.webContents.send('menu-toggle-terminal')
        },
        {
          label: 'Toggle AI Assistant',
          accelerator: 'CmdOrCtrl+Shift+A',
          click: () => mainWindow.webContents.send('menu-toggle-ai')
        },
        {
          label: 'Toggle Enhanced AI Assistant',
          accelerator: 'CmdOrCtrl+Alt+A',
          click: () => mainWindow.webContents.send('menu-enhanced-ai')
        },
        { type: 'separator' },
        {
          label: 'Toggle Developer Tools',
          accelerator: 'F12',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.toggleDevTools();
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Zoom In',
          accelerator: 'CmdOrCtrl+Plus',
          click: () => mainWindow.webContents.send('menu-zoom-in')
        },
        {
          label: 'Zoom Out',
          accelerator: 'CmdOrCtrl+-',
          click: () => mainWindow.webContents.send('menu-zoom-out')
        },
        {
          label: 'Reset Zoom',
          accelerator: 'CmdOrCtrl+0',
          click: () => mainWindow.webContents.send('menu-zoom-reset')
        },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Mono',
      submenu: [
        {
          label: 'Run Current File',
          accelerator: 'Ctrl+F5',
          click: () => mainWindow.webContents.send('menu-run-file')
        },
        {
          label: 'Stop Running Program',
          accelerator: 'Shift+F5',
          click: () => mainWindow.webContents.send('menu-stop-program')
        },
        { type: 'separator' },
        {
          label: 'Format Document',
          accelerator: 'Shift+Alt+F',
          click: () => mainWindow.webContents.send('menu-format-document')
        }
      ]
    },
    {
      label: 'Debug',
      submenu: [
        {
          label: 'Start Debugging',
          accelerator: 'F5',
          click: () => mainWindow.webContents.send('menu-debug-start')
        },
        {
          label: 'Stop Debugging',
          accelerator: 'Shift+F5',
          click: () => mainWindow.webContents.send('menu-debug-stop')
        },
        {
          label: 'Restart Debugging',
          accelerator: 'Ctrl+Shift+F5',
          click: () => mainWindow.webContents.send('menu-debug-restart')
        },
        { type: 'separator' },
        {
          label: 'Continue',
          accelerator: 'F5',
          click: () => mainWindow.webContents.send('menu-debug-continue')
        },
        {
          label: 'Step Over',
          accelerator: 'F10',
          click: () => mainWindow.webContents.send('menu-debug-step-over')
        },
        {
          label: 'Step Into',
          accelerator: 'F11',
          click: () => mainWindow.webContents.send('menu-debug-step-into')
        },
        {
          label: 'Step Out',
          accelerator: 'Shift+F11',
          click: () => mainWindow.webContents.send('menu-debug-step-out')
        },
        { type: 'separator' },
        {
          label: 'Toggle Breakpoint',
          accelerator: 'F9',
          click: () => mainWindow.webContents.send('menu-debug-toggle-breakpoint')
        },
        {
          label: 'Clear All Breakpoints',
          click: () => mainWindow.webContents.send('menu-debug-clear-breakpoints')
        }
      ]
    },
    {
      label: 'Theme',
      submenu: [
        {
          label: 'Dark',
          click: () => mainWindow.webContents.send('menu-theme-dark')
        },
        {
          label: 'Light',
          click: () => mainWindow.webContents.send('menu-theme-light')
        },
        {
          label: 'Nord',
          click: () => mainWindow.webContents.send('menu-theme-nord')
        }
      ]
    },
    {
      label: 'Settings',
      submenu: [
        {
          label: 'Preferences',
          accelerator: 'CmdOrCtrl+,',
          click: () => mainWindow.webContents.send('menu-settings')
        },
        {
          label: 'Package Manager',
          accelerator: 'CmdOrCtrl+Shift+P',
          click: () => mainWindow.webContents.send('menu-package-manager')
        },
        { type: 'separator' },
        {
          label: 'Plugin Manager',
          click: () => mainWindow.webContents.send('menu-plugin-manager')
        },
        {
          label: 'Project Manager',
          accelerator: 'CmdOrCtrl+Alt+P',
          click: () => mainWindow.webContents.send('menu-project-manager')
        },
        {
          label: 'Theme Editor',
          click: () => mainWindow.webContents.send('menu-theme-editor')
        }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: () => shell.openExternal('https://github.com/blackswanalpha/mono')
        },
        {
          label: 'Report Issue',
          click: () => shell.openExternal('https://github.com/blackswanalpha/mono/issues')
        },
        { type: 'separator' },
        {
          label: 'About Mono Editor',
          click: () => mainWindow.webContents.send('menu-about')
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Create splash window
function createSplashWindow() {
  console.log('Main process: Creating splash window...');

  splashWindow = new BrowserWindow({
    width: 400,
    height: 400,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true, // Enable context isolation for security
      // Add GPU-related settings to help with rendering issues
      offscreen: false,
      backgroundThrottling: false,
      // Disable sandbox to allow Node.js modules in preload script
      sandbox: false,
      // Use a simple preload script for the splash window
      preload: path.join(__dirname, 'splash-preload.js')
    },
    // Add GPU-related settings to help with rendering issues
    paintWhenInitiallyHidden: true,
    icon: path.join(__dirname, 'assets/icons/png/512x512.png')
  });

  console.log('Main process: Splash window created');

  // Load splash screen HTML
  splashWindow.loadFile('src/splash.html');

  // Hide splash window when closed
  splashWindow.on('closed', () => {
    splashWindow = null;
  });

  return splashWindow;
}

// Disable hardware acceleration to avoid some graphics issues
app.disableHardwareAcceleration();

// Initialize the app when ready
app.whenReady().then(() => {
  // Create and show splash window
  createSplashWindow();

  // Create main window after a delay to show splash screen
  setTimeout(() => {
    createWindow();

    // Close splash window when main window is ready
    mainWindow.once('ready-to-show', () => {
      if (splashWindow) {
        splashWindow.close();
      }
      mainWindow.show();

      // Always open DevTools for debugging
      mainWindow.webContents.openDevTools();
    });
  }, 1500); // Show splash for 1.5 seconds

  // On macOS, recreate window when dock icon is clicked and no windows are open
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Handle file open dialog
ipcMain.handle('show-open-file-dialog', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Mono Files', extensions: ['mono'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });

  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

// Handle folder open dialog with improved error handling and recovery
ipcMain.handle('show-open-folder-dialog', async () => {
  console.log('Main process: show-open-folder-dialog handler called');

  try {
    // Check if mainWindow exists
    if (!mainWindow) {
      console.error('Main process: mainWindow is undefined in show-open-folder-dialog');

      // Try to recover by creating a new window if app is ready
      if (app.isReady()) {
        console.log('Main process: Attempting to recover by creating a new main window');
        createWindow();

        // Wait for the window to be ready
        await new Promise(resolve => setTimeout(resolve, 1000));

        if (!mainWindow) {
          throw new Error('Failed to recover: Could not create main window');
        }
      } else {
        throw new Error('Main window is not available and app is not ready');
      }
    }

    console.log('Main process: Showing open folder dialog...');

    // Use a timeout promise to prevent hanging
    const dialogPromise = dialog.showOpenDialog({
      properties: ['openDirectory'],
      title: 'Select a folder',
      buttonLabel: 'Open Folder'
    });

    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Folder selection dialog timed out after 30 seconds')), 30000);
    });

    const result = await Promise.race([dialogPromise, timeoutPromise]);
    console.log('Main process: Dialog result:', result);

    if (!result.canceled && result.filePaths.length > 0) {
      console.log('Main process: Selected folder:', result.filePaths[0]);

      // Verify the folder exists and is readable
      try {
        await fs.access(result.filePaths[0], fs.constants.R_OK);
      } catch (accessError) {
        console.error('Main process: Cannot access selected folder:', accessError);
        throw new Error(`Cannot access the selected folder: ${accessError.message}`);
      }

      return result.filePaths[0];
    }

    console.log('Main process: No folder selected or dialog canceled');
    return null;
  } catch (error) {
    console.error('Main process: Error in show-open-folder-dialog:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Folder Open Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Add a simple test IPC handler
ipcMain.handle('test-ipc', async () => {
  console.log('Main process: test-ipc handler called');
  return {
    success: true,
    message: 'IPC is working',
    timestamp: new Date().toISOString()
  };
});

// Handle getting the current working directory
ipcMain.handle('get-current-directory', () => {
  console.log('Main process: get-current-directory handler called');
  return process.cwd();
});

// DevTools IPC handler
ipcMain.handle('toggle-dev-tools', async () => {
  console.log('Main process: toggle-dev-tools handler called');

  try {
    if (!mainWindow) {
      throw new Error('Main window is not available');
    }

    mainWindow.webContents.toggleDevTools();

    return {
      success: true,
      isOpen: mainWindow.webContents.isDevToolsOpened()
    };
  } catch (error) {
    console.error('Main process: Error toggling DevTools:', error);
    throw error;
  }
});



// Package manager IPC handlers
ipcMain.handle('get-user-data-path', async () => {
  return app.getPath('userData');
});

ipcMain.handle('ensure-dir', async (_, dirPath) => {
  try {
    await fs.ensureDir(dirPath);
    return true;
  } catch (error) {
    console.error('Error ensuring directory:', error);
    throw error;
  }
});

ipcMain.handle('read-dir', async (_, dirPath) => {
  try {
    const files = await fs.readdir(dirPath);
    return files;
  } catch (error) {
    console.error('Error reading directory:', error);
    throw error;
  }
});

// These handlers are already defined below with more robust error handling

ipcMain.handle('remove-dir', async (_, dirPath) => {
  try {
    await fs.remove(dirPath);
    return true;
  } catch (error) {
    console.error('Error removing directory:', error);
    throw error;
  }
});

// Handle file save dialog
ipcMain.handle('show-save-file-dialog', async (_, defaultPath) => {
  try {
    console.log('Main process: show-save-file-dialog handler called');

    // Check if mainWindow exists
    if (!mainWindow) {
      console.error('Main process: mainWindow is undefined in show-save-file-dialog');
      throw new Error('Main window is not available');
    }

    console.log('Main process: Showing save file dialog...');

    // Use a timeout promise to prevent hanging
    const dialogPromise = dialog.showSaveDialog(mainWindow, {
      defaultPath: defaultPath,
      filters: [
        { name: 'Mono Files', extensions: ['mono'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Save file dialog timed out after 30 seconds')), 30000);
    });

    const result = await Promise.race([dialogPromise, timeoutPromise]);
    console.log('Main process: Save dialog result:', result);

    if (!result.canceled && result.filePath) {
      console.log('Main process: Selected file path:', result.filePath);
      return result.filePath;
    }

    console.log('Main process: No file selected or dialog canceled');
    return null;
  } catch (error) {
    console.error('Main process: Error in show-save-file-dialog:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Save File Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Handle file read with improved error handling
ipcMain.handle('read-file', async (_, filePath) => {
  console.log('Main process: read-file handler called for', filePath);

  try {
    // Validate file path
    if (!filePath) {
      throw new Error('No file path provided');
    }

    // Check if file exists and is readable
    try {
      await fs.access(filePath, fs.constants.R_OK);
    } catch (accessError) {
      console.error('Main process: Cannot access file:', accessError);
      throw new Error(`Cannot access the file: ${accessError.message}`);
    }

    // Read file with timeout handling
    const readPromise = fs.readFile(filePath, 'utf8');
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('File read operation timed out after 10 seconds')), 10000);
    });

    const content = await Promise.race([readPromise, timeoutPromise]);
    console.log('Main process: File read successfully');

    return content;
  } catch (error) {
    console.error('Main process: Error reading file:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'File Read Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Handle file write with improved error handling
ipcMain.handle('write-file', async (_, filePath, content) => {
  console.log('Main process: write-file handler called for', filePath);

  try {
    // Validate parameters
    if (!filePath) {
      throw new Error('No file path provided');
    }

    if (content === undefined) {
      throw new Error('No content provided');
    }

    // Ensure directory exists
    const dirPath = path.dirname(filePath);
    await fs.ensureDir(dirPath);

    // Write file with timeout handling
    const writePromise = fs.writeFile(filePath, content, 'utf8');
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('File write operation timed out after 10 seconds')), 10000);
    });

    await Promise.race([writePromise, timeoutPromise]);
    console.log('Main process: File written successfully');

    return true;
  } catch (error) {
    console.error('Main process: Error writing file:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'File Write Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Handle directory read with improved error handling
ipcMain.handle('read-directory', async (_, dirPath) => {
  console.log('Main process: read-directory handler called for', dirPath);

  try {
    // Validate directory path
    if (!dirPath) {
      throw new Error('No directory path provided');
    }

    // Check if directory exists and is readable
    try {
      await fs.access(dirPath, fs.constants.R_OK);
    } catch (accessError) {
      console.error('Main process: Cannot access directory:', accessError);
      throw new Error(`Cannot access the directory: ${accessError.message}`);
    }

    // Check if it's actually a directory
    const stats = await fs.stat(dirPath);
    if (!stats.isDirectory()) {
      throw new Error('The specified path is not a directory');
    }

    // Read directory with timeout handling
    const readPromise = fs.readdir(dirPath, { withFileTypes: true });
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Directory read operation timed out after 10 seconds')), 10000);
    });

    const items = await Promise.race([readPromise, timeoutPromise]);
    console.log(`Main process: Directory read successfully, found ${items.length} items`);

    // Process items
    const result = items.map(item => {
      return {
        name: item.name,
        isDirectory: item.isDirectory(),
        path: path.join(dirPath, item.name)
      };
    });

    return result;
  } catch (error) {
    console.error('Main process: Error reading directory:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Directory Read Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Store active processes
const activeProcesses = new Map();

// Store active debug sessions
const activeDebugSessions = new Map();

// Handle running Mono file with improved error handling
ipcMain.handle('run-mono-file', async (_, filePath) => {
  console.log('Main process: run-mono-file handler called for', filePath);

  try {
    // Validate file path
    if (!filePath) {
      throw new Error('No file path provided');
    }

    // Check if file exists and is readable
    try {
      await fs.access(filePath, fs.constants.R_OK);
    } catch (accessError) {
      console.error('Main process: Cannot access file:', accessError);
      throw new Error(`Cannot access the file: ${accessError.message}`);
    }

    // Determine the mono interpreter path
    // First check if './mono' exists in the current directory
    let monoInterpreterPath;

    // Try to find the mono interpreter in different locations
    const possiblePaths = [
      path.join(__dirname, 'bin', 'mono'),  // Default location in bin directory
      path.join(process.cwd(), 'mono'),     // Current working directory
      './mono',                             // Relative to cwd
      'mono'                                // In PATH
    ];

    let interpreterFound = false;

    for (const testPath of possiblePaths) {
      try {
        await fs.access(testPath, fs.constants.X_OK);
        monoInterpreterPath = testPath;
        interpreterFound = true;
        console.log(`Main process: Found mono interpreter at: ${monoInterpreterPath}`);
        break;
      } catch (error) {
        console.log(`Main process: Mono interpreter not found at: ${testPath}`);
      }
    }

    if (!interpreterFound) {
      console.error('Main process: Cannot find mono interpreter in any location');
      throw new Error('Cannot find the mono interpreter. Make sure it is installed and executable.');
    }

    console.log(`Main process: Spawning process with interpreter: ${monoInterpreterPath}`);

    // Create a process to run the mono file
    // Use the current working directory of the file for better relative path handling
    const fileDir = path.dirname(filePath);

    // Log the execution details
    console.log(`Main process: Running mono with:
      - Interpreter: ${monoInterpreterPath}
      - File: ${filePath}
      - Working directory: ${fileDir}
    `);

    // Create the process with appropriate options
    const childProcess = spawn(monoInterpreterPath, [filePath], {
      shell: true,
      cwd: fileDir,
      env: {
        ...process.env,
        MONO_PATH: fileDir  // Set MONO_PATH to help with module imports
      }
    });

    // Store the process
    const processId = childProcess.pid.toString();
    activeProcesses.set(processId, childProcess);
    console.log(`Main process: Process started with ID: ${processId}`);

    // Set up event listeners for the process
    childProcess.stdout.on('data', (data) => {
      if (mainWindow) {
        mainWindow.webContents.send('process-output', {
          id: processId,
          type: 'stdout',
          data: data.toString()
        });
      }
    });

    childProcess.stderr.on('data', (data) => {
      if (mainWindow) {
        mainWindow.webContents.send('process-output', {
          id: processId,
          type: 'stderr',
          data: data.toString()
        });
      }
    });

    childProcess.on('error', (error) => {
      console.error(`Main process: Process error for ID ${processId}:`, error);
      if (mainWindow) {
        mainWindow.webContents.send('process-output', {
          id: processId,
          type: 'stderr',
          data: `Process error: ${error.message}`
        });

        mainWindow.webContents.send('process-exit', {
          id: processId,
          code: 1,
          error: error.message
        });
      }

      // Remove the process from the active processes map
      activeProcesses.delete(processId);
    });

    childProcess.on('close', (code) => {
      console.log(`Main process: Process closed with code ${code} for ID ${processId}`);
      if (mainWindow) {
        mainWindow.webContents.send('process-exit', {
          id: processId,
          code: code
        });
      }

      // Remove the process from the active processes map
      activeProcesses.delete(processId);
    });

    // Return the process ID so the renderer can communicate with it
    return processId;
  } catch (error) {
    console.error('Main process: Error running Mono file:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Run File Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Handle stopping a process with improved error handling
ipcMain.handle('stop-process', async (_, processId) => {
  console.log(`Main process: stop-process handler called for process ID: ${processId}`);

  try {
    // Validate process ID
    if (!processId) {
      throw new Error('No process ID provided');
    }

    const process = activeProcesses.get(processId);
    if (!process) {
      console.log(`Main process: Process with ID ${processId} not found`);
      return false;
    }

    console.log(`Main process: Killing process with ID ${processId}`);

    // Kill the process
    try {
      process.kill();
      console.log(`Main process: Process with ID ${processId} killed successfully`);

      // Remove from active processes map
      activeProcesses.delete(processId);

      return true;
    } catch (killError) {
      console.error(`Main process: Error killing process with ID ${processId}:`, killError);
      throw new Error(`Failed to kill process: ${killError.message}`);
    }
  } catch (error) {
    console.error('Main process: Error stopping process:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Process Stop Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Handle writing to a process stdin with improved error handling
ipcMain.handle('write-to-process', async (_, processId, data) => {
  console.log(`Main process: write-to-process handler called for process ID: ${processId}`);

  try {
    // Validate parameters
    if (!processId) {
      throw new Error('No process ID provided');
    }

    if (data === undefined) {
      throw new Error('No data provided');
    }

    const process = activeProcesses.get(processId);
    if (!process) {
      console.log(`Main process: Process with ID ${processId} not found`);
      return false;
    }

    // Check if stdin is writable
    if (!process.stdin || !process.stdin.writable) {
      throw new Error('Process stdin is not writable');
    }

    console.log(`Main process: Writing data to process with ID ${processId}`);

    // Write to the process stdin
    try {
      process.stdin.write(data);
      console.log(`Main process: Data written to process with ID ${processId} successfully`);
      return true;
    } catch (writeError) {
      console.error(`Main process: Error writing to process with ID ${processId}:`, writeError);
      throw new Error(`Failed to write to process: ${writeError.message}`);
    }
  } catch (error) {
    console.error('Main process: Error writing to process:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Process Write Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Handle creating a new file with improved error handling
ipcMain.handle('create-file', async (_, filePath, content = '') => {
  console.log(`Main process: create-file handler called for ${filePath}`);

  try {
    // Validate file path
    if (!filePath) {
      throw new Error('No file path provided');
    }

    // Check if file already exists
    if (await fs.pathExists(filePath)) {
      throw new Error(`File already exists: ${filePath}`);
    }

    // Ensure directory exists
    const dirPath = path.dirname(filePath);
    await fs.ensureDir(dirPath);

    console.log(`Main process: Creating file at ${filePath}`);

    // Create the file with the given content with timeout handling
    const writePromise = fs.writeFile(filePath, content, 'utf8');
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('File creation timed out after 10 seconds')), 10000);
    });

    await Promise.race([writePromise, timeoutPromise]);
    console.log(`Main process: File created successfully at ${filePath}`);

    return true;
  } catch (error) {
    console.error('Main process: Error creating file:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'File Creation Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Handle creating a new directory with improved error handling
ipcMain.handle('create-directory', async (_, dirPath) => {
  console.log(`Main process: create-directory handler called for ${dirPath}`);

  try {
    // Validate directory path
    if (!dirPath) {
      throw new Error('No directory path provided');
    }

    // Check if directory already exists
    if (await fs.pathExists(dirPath)) {
      throw new Error(`Directory already exists: ${dirPath}`);
    }

    console.log(`Main process: Creating directory at ${dirPath}`);

    // Create the directory with timeout handling
    const mkdirPromise = fs.mkdir(dirPath, { recursive: true });
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Directory creation timed out after 10 seconds')), 10000);
    });

    await Promise.race([mkdirPromise, timeoutPromise]);
    console.log(`Main process: Directory created successfully at ${dirPath}`);

    return true;
  } catch (error) {
    console.error('Main process: Error creating directory:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Directory Creation Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Handle renaming a file or directory with improved error handling
ipcMain.handle('rename-item', async (_, oldPath, newPath) => {
  console.log(`Main process: rename-item handler called from ${oldPath} to ${newPath}`);

  try {
    // Validate paths
    if (!oldPath) {
      throw new Error('No source path provided');
    }

    if (!newPath) {
      throw new Error('No destination path provided');
    }

    // Check if source exists
    if (!(await fs.pathExists(oldPath))) {
      throw new Error(`Source does not exist: ${oldPath}`);
    }

    // Check if target already exists
    if (await fs.pathExists(newPath)) {
      throw new Error(`Target already exists: ${newPath}`);
    }

    console.log(`Main process: Renaming from ${oldPath} to ${newPath}`);

    // Rename the file or directory with timeout handling
    const renamePromise = fs.rename(oldPath, newPath);
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Rename operation timed out after 10 seconds')), 10000);
    });

    await Promise.race([renamePromise, timeoutPromise]);
    console.log(`Main process: Renamed successfully from ${oldPath} to ${newPath}`);

    return true;
  } catch (error) {
    console.error('Main process: Error renaming item:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Rename Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Handle deleting a file or directory with improved error handling
ipcMain.handle('delete-item', async (_, itemPath, isDirectory) => {
  console.log(`Main process: delete-item handler called for ${itemPath} (isDirectory: ${isDirectory})`);

  try {
    // Validate path
    if (!itemPath) {
      throw new Error('No path provided');
    }

    // Check if item exists
    if (!(await fs.pathExists(itemPath))) {
      throw new Error(`Item does not exist: ${itemPath}`);
    }

    console.log(`Main process: Deleting ${isDirectory ? 'directory' : 'file'} at ${itemPath}`);

    // Delete the file or directory with timeout handling
    let deletePromise;
    if (isDirectory) {
      deletePromise = fs.rmdir(itemPath, { recursive: true });
    } else {
      deletePromise = fs.unlink(itemPath);
    }

    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Delete operation timed out after 10 seconds')), 10000);
    });

    await Promise.race([deletePromise, timeoutPromise]);
    console.log(`Main process: Deleted ${isDirectory ? 'directory' : 'file'} successfully at ${itemPath}`);

    return true;
  } catch (error) {
    console.error('Main process: Error deleting item:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Delete Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Debug API handlers

// Start a debug session with improved error handling
ipcMain.handle('start-debug-session', async (_, filePath, breakpoints) => {
  console.log('Main process: start-debug-session handler called for', filePath);

  try {
    // Validate parameters
    if (!filePath) {
      throw new Error('No file path provided');
    }

    // Check if file exists
    try {
      await fs.access(filePath, fs.constants.R_OK);
    } catch (accessError) {
      console.error('Main process: Cannot access file for debugging:', accessError);
      throw new Error(`Cannot access the file for debugging: ${accessError.message}`);
    }

    console.log('Main process: Starting debug session for:', filePath);
    console.log('Main process: Breakpoints:', breakpoints);

    // For now, we'll simulate a debug session
    // In a real implementation, this would start a debug adapter process
    const sessionId = Date.now().toString();
    console.log(`Main process: Created debug session with ID: ${sessionId}`);

    // Store session info
    activeDebugSessions.set(sessionId, {
      filePath,
      breakpoints,
      paused: false,
      variables: [],
      callStack: [],
      startTime: new Date()
    });

    // Simulate starting the debug session
    setTimeout(() => {
      if (mainWindow && activeDebugSessions.has(sessionId)) {
        // Simulate hitting a breakpoint
        const firstBreakpoint = breakpoints && breakpoints.length > 0 ?
          breakpoints[0] : [filePath, 1];

        console.log(`Main process: Debug session ${sessionId} paused at breakpoint:`, firstBreakpoint);

        mainWindow.webContents.send('debug-event', {
          sessionId,
          type: 'paused',
          reason: 'breakpoint',
          filePath: firstBreakpoint[0],
          line: firstBreakpoint[1] || 1
        });

        // Update session state
        const session = activeDebugSessions.get(sessionId);
        session.paused = true;
        session.currentLine = firstBreakpoint[1] || 1;
        activeDebugSessions.set(sessionId, session);
      }
    }, 500);

    return sessionId;
  } catch (error) {
    console.error('Main process: Error starting debug session:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Debug Session Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Stop a debug session with improved error handling
ipcMain.handle('stop-debug-session', async (_, sessionId) => {
  console.log('Main process: stop-debug-session handler called for', sessionId);

  try {
    // Validate session ID
    if (!sessionId) {
      throw new Error('No debug session ID provided');
    }

    console.log('Main process: Stopping debug session:', sessionId);

    if (!activeDebugSessions.has(sessionId)) {
      console.log(`Main process: Debug session ${sessionId} not found`);
      return false;
    }

    // Get session info for logging
    const session = activeDebugSessions.get(sessionId);
    console.log(`Main process: Terminating debug session for file: ${session.filePath}`);

    // Clean up session
    activeDebugSessions.delete(sessionId);
    console.log(`Main process: Debug session ${sessionId} terminated`);

    // Notify renderer
    if (mainWindow) {
      mainWindow.webContents.send('debug-event', {
        sessionId,
        type: 'terminated'
      });
    }

    return true;
  } catch (error) {
    console.error('Main process: Error stopping debug session:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Debug Stop Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Continue execution with improved error handling
ipcMain.handle('continue-debug-session', async (_, sessionId) => {
  console.log('Main process: continue-debug-session handler called for', sessionId);

  try {
    // Validate session ID
    if (!sessionId) {
      throw new Error('No debug session ID provided');
    }

    console.log('Main process: Continuing debug session:', sessionId);

    if (!activeDebugSessions.has(sessionId)) {
      console.log(`Main process: Debug session ${sessionId} not found`);
      return false;
    }

    // Get session info
    const session = activeDebugSessions.get(sessionId);

    // Check if session is paused
    if (!session.paused) {
      console.log(`Main process: Debug session ${sessionId} is not paused, cannot continue`);
      throw new Error('Debug session is not paused');
    }

    // Update session state
    session.paused = false;
    activeDebugSessions.set(sessionId, session);
    console.log(`Main process: Debug session ${sessionId} resumed`);

    // Notify renderer
    if (mainWindow) {
      mainWindow.webContents.send('debug-event', {
        sessionId,
        type: 'resumed'
      });
    }

    // Simulate running until next breakpoint
    simulateRunUntilBreakpoint(sessionId);
    console.log(`Main process: Debug session ${sessionId} running until next breakpoint`);

    return true;
  } catch (error) {
    console.error('Main process: Error continuing debug session:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Debug Continue Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Step over with improved error handling
ipcMain.handle('step-over-debug-session', async (_, sessionId) => {
  console.log('Main process: step-over-debug-session handler called for', sessionId);

  try {
    // Validate session ID
    if (!sessionId) {
      throw new Error('No debug session ID provided');
    }

    console.log('Main process: Step over in debug session:', sessionId);

    if (!activeDebugSessions.has(sessionId)) {
      console.log(`Main process: Debug session ${sessionId} not found`);
      return false;
    }

    // Get session info
    const session = activeDebugSessions.get(sessionId);

    // Check if session is paused
    if (!session.paused) {
      console.log(`Main process: Debug session ${sessionId} is not paused, cannot step over`);
      throw new Error('Debug session is not paused');
    }

    // Simulate stepping over
    simulateStep(sessionId, 'stepOver');
    console.log(`Main process: Stepping over in debug session ${sessionId}`);

    return true;
  } catch (error) {
    console.error('Main process: Error stepping over in debug session:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Debug Step Over Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Step into with improved error handling
ipcMain.handle('step-into-debug-session', async (_, sessionId) => {
  console.log('Main process: step-into-debug-session handler called for', sessionId);

  try {
    // Validate session ID
    if (!sessionId) {
      throw new Error('No debug session ID provided');
    }

    console.log('Main process: Step into in debug session:', sessionId);

    if (!activeDebugSessions.has(sessionId)) {
      console.log(`Main process: Debug session ${sessionId} not found`);
      return false;
    }

    // Get session info
    const session = activeDebugSessions.get(sessionId);

    // Check if session is paused
    if (!session.paused) {
      console.log(`Main process: Debug session ${sessionId} is not paused, cannot step into`);
      throw new Error('Debug session is not paused');
    }

    // Simulate stepping into
    simulateStep(sessionId, 'stepInto');
    console.log(`Main process: Stepping into in debug session ${sessionId}`);

    return true;
  } catch (error) {
    console.error('Main process: Error stepping into in debug session:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Debug Step Into Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Step out with improved error handling
ipcMain.handle('step-out-debug-session', async (_, sessionId) => {
  console.log('Main process: step-out-debug-session handler called for', sessionId);

  try {
    // Validate session ID
    if (!sessionId) {
      throw new Error('No debug session ID provided');
    }

    console.log('Main process: Step out in debug session:', sessionId);

    if (!activeDebugSessions.has(sessionId)) {
      console.log(`Main process: Debug session ${sessionId} not found`);
      return false;
    }

    // Get session info
    const session = activeDebugSessions.get(sessionId);

    // Check if session is paused
    if (!session.paused) {
      console.log(`Main process: Debug session ${sessionId} is not paused, cannot step out`);
      throw new Error('Debug session is not paused');
    }

    // Simulate stepping out
    simulateStep(sessionId, 'stepOut');
    console.log(`Main process: Stepping out in debug session ${sessionId}`);

    return true;
  } catch (error) {
    console.error('Main process: Error stepping out in debug session:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Debug Step Out Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Update breakpoints with improved error handling
ipcMain.handle('update-breakpoints', async (_, sessionId, breakpoints) => {
  console.log('Main process: update-breakpoints handler called for', sessionId);

  try {
    // Validate parameters
    if (!sessionId) {
      throw new Error('No debug session ID provided');
    }

    if (!breakpoints || !Array.isArray(breakpoints)) {
      throw new Error('Invalid breakpoints data');
    }

    console.log('Main process: Updating breakpoints in debug session:', sessionId);
    console.log('Main process: New breakpoints:', breakpoints);

    if (!activeDebugSessions.has(sessionId)) {
      console.log(`Main process: Debug session ${sessionId} not found`);
      return false;
    }

    // Update session breakpoints
    const session = activeDebugSessions.get(sessionId);
    session.breakpoints = breakpoints;
    activeDebugSessions.set(sessionId, session);
    console.log(`Main process: Breakpoints updated for debug session ${sessionId}`);

    return true;
  } catch (error) {
    console.error('Main process: Error updating breakpoints in debug session:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Update Breakpoints Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Get variables with improved error handling
ipcMain.handle('get-variables', async (_, sessionId) => {
  console.log('Main process: get-variables handler called for', sessionId);

  try {
    // Validate session ID
    if (!sessionId) {
      throw new Error('No debug session ID provided');
    }

    console.log('Main process: Getting variables for debug session:', sessionId);

    if (!activeDebugSessions.has(sessionId)) {
      console.log(`Main process: Debug session ${sessionId} not found`);
      return [];
    }

    // Get session info
    const session = activeDebugSessions.get(sessionId);

    // Check if session is paused
    if (!session.paused) {
      console.log(`Main process: Debug session ${sessionId} is not paused, cannot get variables`);
      throw new Error('Debug session is not paused');
    }

    // Simulate getting variables
    const variables = simulateGetVariables();
    console.log(`Main process: Retrieved ${variables.length} variables for debug session ${sessionId}`);

    // Notify renderer
    if (mainWindow) {
      mainWindow.webContents.send('debug-event', {
        sessionId,
        type: 'variables',
        variables
      });
    }

    return variables;
  } catch (error) {
    console.error('Main process: Error getting variables for debug session:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Get Variables Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Get call stack with improved error handling
ipcMain.handle('get-call-stack', async (_, sessionId) => {
  console.log('Main process: get-call-stack handler called for', sessionId);

  try {
    // Validate session ID
    if (!sessionId) {
      throw new Error('No debug session ID provided');
    }

    console.log('Main process: Getting call stack for debug session:', sessionId);

    if (!activeDebugSessions.has(sessionId)) {
      console.log(`Main process: Debug session ${sessionId} not found`);
      return [];
    }

    // Get session info
    const session = activeDebugSessions.get(sessionId);

    // Check if session is paused
    if (!session.paused) {
      console.log(`Main process: Debug session ${sessionId} is not paused, cannot get call stack`);
      throw new Error('Debug session is not paused');
    }

    // Simulate getting call stack
    const callStack = simulateGetCallStack(sessionId);
    console.log(`Main process: Retrieved ${callStack.length} call stack frames for debug session ${sessionId}`);

    // Notify renderer
    if (mainWindow) {
      mainWindow.webContents.send('debug-event', {
        sessionId,
        type: 'callStack',
        callStack
      });
    }

    return callStack;
  } catch (error) {
    console.error('Main process: Error getting call stack for debug session:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Get Call Stack Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Get variables for a specific stack frame with improved error handling
ipcMain.handle('get-variables-for-frame', async (_, sessionId, frameIndex) => {
  console.log('Main process: get-variables-for-frame handler called for', sessionId, 'frame', frameIndex);

  try {
    // Validate parameters
    if (!sessionId) {
      throw new Error('No debug session ID provided');
    }

    if (frameIndex === undefined || frameIndex === null) {
      throw new Error('No frame index provided');
    }

    console.log('Main process: Getting variables for frame in debug session:', sessionId, frameIndex);

    if (!activeDebugSessions.has(sessionId)) {
      console.log(`Main process: Debug session ${sessionId} not found`);
      return [];
    }

    // Get session info
    const session = activeDebugSessions.get(sessionId);

    // Check if session is paused
    if (!session.paused) {
      console.log(`Main process: Debug session ${sessionId} is not paused, cannot get frame variables`);
      throw new Error('Debug session is not paused');
    }

    // Simulate getting variables for a specific frame
    const variables = simulateGetVariablesForFrame(frameIndex);
    console.log(`Main process: Retrieved ${variables.length} variables for frame ${frameIndex} in debug session ${sessionId}`);

    // Notify renderer
    if (mainWindow) {
      mainWindow.webContents.send('debug-event', {
        sessionId,
        type: 'frameVariables',
        frameIndex,
        variables
      });
    }

    return variables;
  } catch (error) {
    console.error('Main process: Error getting variables for frame in debug session:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Get Frame Variables Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Evaluate expression with improved error handling
ipcMain.handle('evaluate-expression', async (_, sessionId, expression) => {
  console.log('Main process: evaluate-expression handler called for', sessionId);

  try {
    // Validate parameters
    if (!sessionId) {
      throw new Error('No debug session ID provided');
    }

    if (!expression) {
      throw new Error('No expression provided');
    }

    console.log('Main process: Evaluating expression in debug session:', sessionId, expression);

    if (!activeDebugSessions.has(sessionId)) {
      console.log(`Main process: Debug session ${sessionId} not found`);
      throw new Error('Debug session not found');
    }

    // Get session info
    const session = activeDebugSessions.get(sessionId);

    // Check if session is paused
    if (!session.paused) {
      console.log(`Main process: Debug session ${sessionId} is not paused, cannot evaluate expression`);
      throw new Error('Debug session is not paused');
    }

    // Simulate evaluating an expression
    const result = simulateEvaluateExpression(expression);
    console.log(`Main process: Evaluated expression "${expression}" in debug session ${sessionId}, result:`, result);

    // Notify renderer
    if (mainWindow) {
      mainWindow.webContents.send('debug-event', {
        sessionId,
        type: 'evaluateResult',
        expression,
        result
      });
    }

    return result;
  } catch (error) {
    console.error('Main process: Error evaluating expression in debug session:', error);

    // Send error to renderer for display
    if (mainWindow) {
      mainWindow.webContents.send('error-notification', {
        title: 'Expression Evaluation Error',
        message: error.message
      });
    }

    throw error;
  }
});

// Helper functions for debug simulation

function simulateRunUntilBreakpoint(sessionId) {
  setTimeout(() => {
    if (mainWindow && activeDebugSessions.has(sessionId)) {
      const session = activeDebugSessions.get(sessionId);

      // Check if we have breakpoints
      if (session.breakpoints && session.breakpoints.length > 0) {
        // Simulate hitting a random breakpoint
        const randomIndex = Math.floor(Math.random() * session.breakpoints.length);
        const breakpoint = session.breakpoints[randomIndex];

        // Update session state
        session.paused = true;
        activeDebugSessions.set(sessionId, session);

        // Notify renderer
        mainWindow.webContents.send('debug-event', {
          type: 'paused',
          reason: 'breakpoint',
          filePath: breakpoint[0],
          line: breakpoint[1]
        });
      } else {
        // Simulate program termination
        activeDebugSessions.delete(sessionId);

        // Notify renderer
        mainWindow.webContents.send('debug-event', {
          type: 'terminated'
        });
      }
    }
  }, 500);
}

function simulateStep(sessionId, stepType) {
  if (mainWindow && activeDebugSessions.has(sessionId)) {
    const session = activeDebugSessions.get(sessionId);

    // Notify renderer that we're resuming
    mainWindow.webContents.send('debug-event', {
      type: 'resumed'
    });

    // Simulate a short delay for the step
    setTimeout(() => {
      if (mainWindow && activeDebugSessions.has(sessionId)) {
        // Get the current file path
        const filePath = session.filePath;

        // Calculate new line based on step type
        let line = 1;
        if (session.currentLine) {
          if (stepType === 'stepOver' || stepType === 'stepInto') {
            line = session.currentLine + 1;
          } else if (stepType === 'stepOut') {
            line = Math.max(1, session.currentLine - 2);
          }
        }

        // Update session state
        session.paused = true;
        session.currentLine = line;
        activeDebugSessions.set(sessionId, session);

        // Notify renderer
        mainWindow.webContents.send('debug-event', {
          type: 'paused',
          reason: 'step',
          filePath,
          line
        });
      }
    }, 300);
  }
}

function simulateGetVariables() {
  // Return some sample variables
  return [
    { name: 'count', value: '42', type: 'number' },
    { name: 'name', value: '"John"', type: 'string' },
    { name: 'isActive', value: 'true', type: 'boolean' },
    { name: 'items', value: '[1, 2, 3]', type: 'array' }
  ];
}

function simulateGetCallStack(sessionId) {
  if (activeDebugSessions.has(sessionId)) {
    const session = activeDebugSessions.get(sessionId);

    // Return a sample call stack
    return [
      { name: 'main', file: session.filePath, line: session.currentLine || 1 },
      { name: 'calculateTotal', file: session.filePath, line: Math.max(1, (session.currentLine || 10) - 5) },
      { name: 'processItems', file: session.filePath, line: Math.max(1, (session.currentLine || 20) - 15) }
    ];
  }

  return [];
}

function simulateGetVariablesForFrame(frameIndex) {
  // Return different variables based on frame index
  if (frameIndex === 0) {
    return [
      { name: 'count', value: '42', type: 'number' },
      { name: 'name', value: '"John"', type: 'string' },
      { name: 'isActive', value: 'true', type: 'boolean' }
    ];
  } else if (frameIndex === 1) {
    return [
      { name: 'total', value: '100', type: 'number' },
      { name: 'tax', value: '8.5', type: 'number' }
    ];
  } else {
    return [
      { name: 'items', value: '[1, 2, 3]', type: 'array' },
      { name: 'index', value: '0', type: 'number' }
    ];
  }
}

function simulateEvaluateExpression(expression) {
  // Simulate evaluating an expression
  if (expression.includes('+')) {
    return 'Result: ' + (Math.random() * 100).toFixed(2);
  } else if (expression.includes('*')) {
    return 'Result: ' + (Math.random() * 1000).toFixed(2);
  } else if (expression.startsWith('count')) {
    return '42';
  } else if (expression.startsWith('name')) {
    return '"John"';
  } else if (expression.startsWith('items')) {
    return '[1, 2, 3]';
  } else {
    return 'undefined';
  }
}
