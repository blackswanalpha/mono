// Preload script runs in the renderer process but has access to Node.js APIs
const { contextBridge, ipcRenderer } = require('electron');
const path = require('path');
const os = require('os');

// Log preload script initialization
console.log('PRELOAD: Preload script executing...');
console.log('PRELOAD: Node version:', process.versions.node);
console.log('PRELOAD: Electron version:', process.versions.electron);
console.log('PRELOAD: Chrome version:', process.versions.chrome);
console.log('PRELOAD: Platform:', process.platform);
console.log('PRELOAD: Architecture:', process.arch);

// Validate that required APIs are available
if (!contextBridge) {
  console.error('PRELOAD: contextBridge is undefined');
  throw new Error('Context bridge is not available');
}

if (!ipcRenderer) {
  console.error('PRELOAD: ipcRenderer is undefined');
  throw new Error('IPC renderer is not available');
}

// Function to safely wrap IPC calls with error handling
const safeIpcInvoke = async (channel, ...args) => {
  try {
    console.log(`PRELOAD: Invoking IPC channel: ${channel}`, args);
    const result = await ipcRenderer.invoke(channel, ...args);
    console.log(`PRELOAD: IPC channel ${channel} returned:`, result);
    return result;
  } catch (error) {
    console.error(`PRELOAD: Error in IPC channel ${channel}:`, error);
    throw error;
  }
};

// Define the API to expose to the renderer process
const api = {
  // System information
  getSystemInfo: () => ({
    nodeVersion: process.versions.node,
    electronVersion: process.versions.electron,
    chromeVersion: process.versions.chrome,
    platform: process.platform,
    arch: process.arch,
    tempDir: os.tmpdir()
  }),

  // DevTools API
  toggleDevTools: () => {
    try {
      return ipcRenderer.invoke('toggle-dev-tools');
    } catch (error) {
      console.error('Error toggling DevTools:', error);
      return Promise.reject(error);
    }
  },

  // File operations
  openFile: () => safeIpcInvoke('show-open-file-dialog'),
  openFolder: () => safeIpcInvoke('show-open-folder-dialog'),
  saveFileAs: (defaultPath) => safeIpcInvoke('show-save-file-dialog', defaultPath),
  readFile: (filePath) => safeIpcInvoke('read-file', filePath),
  writeFile: (filePath, content) => safeIpcInvoke('write-file', filePath, content),
  readDirectory: (dirPath) => safeIpcInvoke('read-directory', dirPath),
  createFile: (filePath, content) => safeIpcInvoke('create-file', filePath, content),
  createDirectory: (dirPath) => safeIpcInvoke('create-directory', dirPath),
  renameItem: (oldPath, newPath) => safeIpcInvoke('rename-item', oldPath, newPath),
  deleteItem: (itemPath, isDirectory) => safeIpcInvoke('delete-item', itemPath, isDirectory),
  getCurrentDirectory: () => safeIpcInvoke('get-current-directory'),

  // Mono operations
  runMonoFile: (filePath) => safeIpcInvoke('run-mono-file', filePath),
  stopProcess: (processId) => safeIpcInvoke('stop-process', processId),
  writeToProcess: (processId, data) => safeIpcInvoke('write-to-process', processId, data),

  // Process event listeners
  onProcessOutput: (callback) => {
    const listener = (_, data) => callback(data);
    ipcRenderer.on('process-output', listener);
    return () => ipcRenderer.removeListener('process-output', listener);
  },

  onProcessExit: (callback) => {
    const listener = (_, data) => callback(data);
    ipcRenderer.on('process-exit', listener);
    return () => ipcRenderer.removeListener('process-exit', listener);
  },

  // Menu event listeners
  onMenuEvent: (channel, callback) => {
    const validChannels = [
      'menu-new-file',
      'menu-open-file',
      'menu-open-folder',
      'menu-save',
      'menu-save-as',
      'menu-toggle-explorer',
      'menu-toggle-terminal',
      'menu-toggle-ai',
      'menu-enhanced-ai',
      'menu-zoom-in',
      'menu-zoom-out',
      'menu-zoom-reset',
      'menu-run-file',
      'menu-stop-program',
      'menu-format-document',
      'menu-theme-dark',
      'menu-theme-light',
      'menu-theme-nord',
      'menu-settings',
      'menu-package-manager',
      'menu-plugin-manager',
      'menu-project-manager',
      'menu-theme-editor',
      'menu-about',
      'menu-debug-start',
      'menu-debug-stop',
      'menu-debug-restart',
      'menu-debug-continue',
      'menu-debug-step-over',
      'menu-debug-step-into',
      'menu-debug-step-out',
      'menu-debug-toggle-breakpoint',
      'menu-debug-clear-breakpoints'
    ];

    if (validChannels.includes(channel)) {
      const listener = (_, ...args) => callback(...args);
      ipcRenderer.on(channel, listener);
      return () => ipcRenderer.removeListener(channel, listener);
    } else {
      console.error(`PRELOAD: Invalid channel: ${channel}`);
      return null;
    }
  },

  // Debug operations
  startDebugSession: (filePath, breakpoints) =>
    safeIpcInvoke('start-debug-session', filePath, breakpoints),
  stopDebugSession: (sessionId) =>
    safeIpcInvoke('stop-debug-session', sessionId),
  continueDebugSession: (sessionId) =>
    safeIpcInvoke('continue-debug-session', sessionId),
  stepOverDebugSession: (sessionId) =>
    safeIpcInvoke('step-over-debug-session', sessionId),
  stepIntoDebugSession: (sessionId) =>
    safeIpcInvoke('step-into-debug-session', sessionId),
  stepOutDebugSession: (sessionId) =>
    safeIpcInvoke('step-out-debug-session', sessionId),
  updateBreakpoints: (sessionId, breakpoints) =>
    safeIpcInvoke('update-breakpoints', sessionId, breakpoints),
  getVariables: (sessionId) =>
    safeIpcInvoke('get-variables', sessionId),
  getCallStack: (sessionId) =>
    safeIpcInvoke('get-call-stack', sessionId),
  getVariablesForFrame: (sessionId, frameIndex) =>
    safeIpcInvoke('get-variables-for-frame', sessionId, frameIndex),
  evaluateExpression: (sessionId, expression) =>
    safeIpcInvoke('evaluate-expression', sessionId, expression),

  // Debug event listeners
  onDebugEvent: (callback) => {
    const listener = (_, data) => callback(data);
    ipcRenderer.on('debug-event', listener);
    return () => ipcRenderer.removeListener('debug-event', listener);
  },

  // Error notification listener
  onErrorNotification: (callback) => {
    const listener = (_, data) => callback(data);
    ipcRenderer.on('error-notification', listener);
    return () => ipcRenderer.removeListener('error-notification', listener);
  },

  // Package manager operations
  getUserDataPath: () => safeIpcInvoke('get-user-data-path'),
  ensureDir: (dirPath) => safeIpcInvoke('ensure-dir', dirPath),
  readDir: (dirPath) => safeIpcInvoke('read-dir', dirPath),
  // Use existing file operations for reading and writing files
  // readFile is already defined above
  // writeFile is already defined above
  removeDir: (dirPath) => safeIpcInvoke('remove-dir', dirPath),

  // Testing API
  testApi: async () => {
    try {
      console.log('PRELOAD: Testing API...');
      const result = await safeIpcInvoke('test-ipc');
      return {
        success: true,
        message: 'API test successful',
        result
      };
    } catch (error) {
      console.error('PRELOAD: API test failed:', error);
      return {
        success: false,
        message: 'API test failed',
        error: error.message
      };
    }
  }
};

// Expose the API to the renderer process
try {
  console.log('PRELOAD: Exposing API to renderer process...');
  contextBridge.exposeInMainWorld('api', api);
  console.log('PRELOAD: API successfully exposed to renderer process');
} catch (error) {
  console.error('PRELOAD: Error exposing API to renderer process:', error);
  throw error;
}

// Log completion
console.log('PRELOAD: Preload script completed');
