// Simple preload script for the splash window
const { contextBridge } = require('electron');

console.log('SPLASH-PRELOAD: Splash preload script executing...');

// Expose minimal API for the splash screen
try {
  contextBridge.exposeInMainWorld('splashApi', {
    getVersion: () => process.versions.electron,
    getPlatform: () => process.platform
  });
  console.log('SPLASH-PRELOAD: Splash API exposed successfully');
} catch (error) {
  console.error('SPLASH-PRELOAD: Error exposing splash API:', error);
}

console.log('SPLASH-PRELOAD: Splash preload script completed');
