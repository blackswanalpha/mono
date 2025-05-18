// File Operations for Mono Editor

/**
 * File Operations class for handling file-related operations
 */
class FileOperations {
  constructor() {
    this.pendingOperations = new Map();
    this.operationTimeouts = new Map();
    this.maxRetries = 3;
    this.retryDelay = 500; // ms
    this.operationTimeout = 10000; // 10 seconds
    
    // Initialize the file operations when the DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initialize());
    } else {
      this.initialize();
    }
  }
  
  /**
   * Initialize the file operations
   */
  initialize() {
    console.log('Initializing File Operations...');
    
    // Add event listeners
    this.addEventListeners();
    
    console.log('File Operations initialized');
  }
  
  /**
   * Add event listeners
   */
  addEventListeners() {
    // Listen for window unload to cancel pending operations
    window.addEventListener('beforeunload', () => {
      this.cancelAllOperations();
    });
  }
  
  /**
   * Read a file with error handling and retries
   * @param {string} filePath - The file path
   * @param {Object} options - Options for reading the file
   * @returns {Promise<string>} The file content
   */
  async readFile(filePath, options = {}) {
    const operationId = `read-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    try {
      console.log(`Reading file: ${filePath} (Operation ID: ${operationId})`);
      
      // Check if API is available
      if (!window.api || typeof window.api.readFile !== 'function') {
        throw new Error('API not available or readFile function missing');
      }
      
      // Create a promise that will be resolved or rejected
      const operationPromise = new Promise((resolve, reject) => {
        this.pendingOperations.set(operationId, { resolve, reject });
      });
      
      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        const timeoutId = setTimeout(() => {
          reject(new Error(`File read operation timed out after ${this.operationTimeout / 1000} seconds`));
          this.pendingOperations.delete(operationId);
        }, this.operationTimeout);
        
        this.operationTimeouts.set(operationId, timeoutId);
      });
      
      // Start the read operation with retries
      this.readFileWithRetry(filePath, operationId, 0, options);
      
      // Wait for the operation to complete or timeout
      const result = await Promise.race([operationPromise, timeoutPromise]);
      
      // Clean up
      this.cleanupOperation(operationId);
      
      return result;
    } catch (error) {
      console.error(`Error reading file: ${filePath}`, error);
      
      // Clean up
      this.cleanupOperation(operationId);
      
      // Dispatch error event
      this.dispatchErrorEvent('read', filePath, error);
      
      throw error;
    }
  }
  
  /**
   * Read a file with retry logic
   * @param {string} filePath - The file path
   * @param {string} operationId - The operation ID
   * @param {number} retryCount - The current retry count
   * @param {Object} options - Options for reading the file
   */
  async readFileWithRetry(filePath, operationId, retryCount, options) {
    try {
      // Check if the operation was cancelled
      if (!this.pendingOperations.has(operationId)) {
        return;
      }
      
      // Read the file
      const content = await window.api.readFile(filePath);
      
      // Resolve the operation
      const operation = this.pendingOperations.get(operationId);
      if (operation) {
        operation.resolve(content);
      }
    } catch (error) {
      console.error(`Error reading file (attempt ${retryCount + 1}): ${filePath}`, error);
      
      // Check if we should retry
      if (retryCount < this.maxRetries) {
        console.log(`Retrying read operation (${retryCount + 1}/${this.maxRetries})...`);
        
        // Wait before retrying
        setTimeout(() => {
          this.readFileWithRetry(filePath, operationId, retryCount + 1, options);
        }, this.retryDelay * Math.pow(2, retryCount)); // Exponential backoff
      } else {
        // Max retries reached, reject the operation
        const operation = this.pendingOperations.get(operationId);
        if (operation) {
          operation.reject(error);
        }
      }
    }
  }
  
  /**
   * Write a file with error handling and retries
   * @param {string} filePath - The file path
   * @param {string} content - The file content
   * @param {Object} options - Options for writing the file
   * @returns {Promise<boolean>} True if successful
   */
  async writeFile(filePath, content, options = {}) {
    const operationId = `write-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    try {
      console.log(`Writing file: ${filePath} (Operation ID: ${operationId})`);
      
      // Check if API is available
      if (!window.api || typeof window.api.writeFile !== 'function') {
        throw new Error('API not available or writeFile function missing');
      }
      
      // Create a promise that will be resolved or rejected
      const operationPromise = new Promise((resolve, reject) => {
        this.pendingOperations.set(operationId, { resolve, reject });
      });
      
      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        const timeoutId = setTimeout(() => {
          reject(new Error(`File write operation timed out after ${this.operationTimeout / 1000} seconds`));
          this.pendingOperations.delete(operationId);
        }, this.operationTimeout);
        
        this.operationTimeouts.set(operationId, timeoutId);
      });
      
      // Start the write operation with retries
      this.writeFileWithRetry(filePath, content, operationId, 0, options);
      
      // Wait for the operation to complete or timeout
      const result = await Promise.race([operationPromise, timeoutPromise]);
      
      // Clean up
      this.cleanupOperation(operationId);
      
      return result;
    } catch (error) {
      console.error(`Error writing file: ${filePath}`, error);
      
      // Clean up
      this.cleanupOperation(operationId);
      
      // Dispatch error event
      this.dispatchErrorEvent('write', filePath, error);
      
      throw error;
    }
  }
  
  /**
   * Write a file with retry logic
   * @param {string} filePath - The file path
   * @param {string} content - The file content
   * @param {string} operationId - The operation ID
   * @param {number} retryCount - The current retry count
   * @param {Object} options - Options for writing the file
   */
  async writeFileWithRetry(filePath, content, operationId, retryCount, options) {
    try {
      // Check if the operation was cancelled
      if (!this.pendingOperations.has(operationId)) {
        return;
      }
      
      // Write the file
      const result = await window.api.writeFile(filePath, content);
      
      // Resolve the operation
      const operation = this.pendingOperations.get(operationId);
      if (operation) {
        operation.resolve(result);
      }
    } catch (error) {
      console.error(`Error writing file (attempt ${retryCount + 1}): ${filePath}`, error);
      
      // Check if we should retry
      if (retryCount < this.maxRetries) {
        console.log(`Retrying write operation (${retryCount + 1}/${this.maxRetries})...`);
        
        // Wait before retrying
        setTimeout(() => {
          this.writeFileWithRetry(filePath, content, operationId, retryCount + 1, options);
        }, this.retryDelay * Math.pow(2, retryCount)); // Exponential backoff
      } else {
        // Max retries reached, reject the operation
        const operation = this.pendingOperations.get(operationId);
        if (operation) {
          operation.reject(error);
        }
      }
    }
  }
  
  /**
   * Read a directory with error handling and retries
   * @param {string} dirPath - The directory path
   * @param {Object} options - Options for reading the directory
   * @returns {Promise<Array>} The directory contents
   */
  async readDirectory(dirPath, options = {}) {
    const operationId = `readdir-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    try {
      console.log(`Reading directory: ${dirPath} (Operation ID: ${operationId})`);
      
      // Check if API is available
      if (!window.api || typeof window.api.readDirectory !== 'function') {
        throw new Error('API not available or readDirectory function missing');
      }
      
      // Create a promise that will be resolved or rejected
      const operationPromise = new Promise((resolve, reject) => {
        this.pendingOperations.set(operationId, { resolve, reject });
      });
      
      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        const timeoutId = setTimeout(() => {
          reject(new Error(`Directory read operation timed out after ${this.operationTimeout / 1000} seconds`));
          this.pendingOperations.delete(operationId);
        }, this.operationTimeout);
        
        this.operationTimeouts.set(operationId, timeoutId);
      });
      
      // Start the read directory operation with retries
      this.readDirectoryWithRetry(dirPath, operationId, 0, options);
      
      // Wait for the operation to complete or timeout
      const result = await Promise.race([operationPromise, timeoutPromise]);
      
      // Clean up
      this.cleanupOperation(operationId);
      
      return result;
    } catch (error) {
      console.error(`Error reading directory: ${dirPath}`, error);
      
      // Clean up
      this.cleanupOperation(operationId);
      
      // Dispatch error event
      this.dispatchErrorEvent('readdir', dirPath, error);
      
      throw error;
    }
  }
  
  /**
   * Read a directory with retry logic
   * @param {string} dirPath - The directory path
   * @param {string} operationId - The operation ID
   * @param {number} retryCount - The current retry count
   * @param {Object} options - Options for reading the directory
   */
  async readDirectoryWithRetry(dirPath, operationId, retryCount, options) {
    try {
      // Check if the operation was cancelled
      if (!this.pendingOperations.has(operationId)) {
        return;
      }
      
      // Read the directory
      const items = await window.api.readDirectory(dirPath);
      
      // Resolve the operation
      const operation = this.pendingOperations.get(operationId);
      if (operation) {
        operation.resolve(items);
      }
    } catch (error) {
      console.error(`Error reading directory (attempt ${retryCount + 1}): ${dirPath}`, error);
      
      // Check if we should retry
      if (retryCount < this.maxRetries) {
        console.log(`Retrying read directory operation (${retryCount + 1}/${this.maxRetries})...`);
        
        // Wait before retrying
        setTimeout(() => {
          this.readDirectoryWithRetry(dirPath, operationId, retryCount + 1, options);
        }, this.retryDelay * Math.pow(2, retryCount)); // Exponential backoff
      } else {
        // Max retries reached, reject the operation
        const operation = this.pendingOperations.get(operationId);
        if (operation) {
          operation.reject(error);
        }
      }
    }
  }
  
  /**
   * Clean up an operation
   * @param {string} operationId - The operation ID
   */
  cleanupOperation(operationId) {
    // Clear timeout
    if (this.operationTimeouts.has(operationId)) {
      clearTimeout(this.operationTimeouts.get(operationId));
      this.operationTimeouts.delete(operationId);
    }
    
    // Remove from pending operations
    this.pendingOperations.delete(operationId);
  }
  
  /**
   * Cancel all pending operations
   */
  cancelAllOperations() {
    for (const [operationId, operation] of this.pendingOperations.entries()) {
      operation.reject(new Error('Operation cancelled'));
      this.cleanupOperation(operationId);
    }
  }
  
  /**
   * Dispatch an error event
   * @param {string} operation - The operation type
   * @param {string} path - The file or directory path
   * @param {Error} error - The error object
   */
  dispatchErrorEvent(operation, path, error) {
    const event = new CustomEvent('file-operation-error', {
      detail: {
        operation,
        path,
        error
      }
    });
    
    document.dispatchEvent(event);
  }
}

// Create and export a singleton instance
const fileOperations = new FileOperations();

// Export the file operations
window.fileOperations = fileOperations;
