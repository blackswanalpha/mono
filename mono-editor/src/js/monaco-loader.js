// Monaco Editor Loader
// This script loads Monaco Editor directly without AMD/RequireJS

class MonacoLoader {
  constructor() {
    this.loaded = false;
    this.loadingPromise = null;
    this.callbacks = [];

    // Define the base path for Monaco
    this.basePath = '../node_modules/monaco-editor/min';

    // Define the required scripts and CSS
    this.requiredFiles = {
      css: [
        `${this.basePath}/vs/editor/editor.main.css`
      ],
      js: [
        // Basic Monaco dependencies
        `${this.basePath}/vs/loader.js`,
        `${this.basePath}/vs/editor/editor.main.nls.js`,
        `${this.basePath}/vs/editor/editor.main.js`
      ]
    };
  }

  /**
   * Load Monaco Editor
   * @returns {Promise} A promise that resolves when Monaco is loaded
   */
  load() {
    if (this.loaded) {
      console.log('Monaco already loaded, resolving immediately');
      return Promise.resolve();
    }

    if (this.loadingPromise) {
      console.log('Monaco loading in progress, returning existing promise');
      return this.loadingPromise;
    }

    console.log('Starting Monaco Editor loading process...');

    this.loadingPromise = new Promise((resolve, reject) => {
      try {
        // First check if Monaco is already loaded
        if (typeof monaco !== 'undefined' && monaco.editor) {
          console.log('Monaco Editor is already loaded in global scope');
          this.loaded = true;
          window.dispatchEvent(new CustomEvent('monaco-ready'));
          resolve();
          return;
        }

        // Load CSS files first
        this.loadCssFiles();

        // Then load JS files in sequence
        this.loadJsFilesSequentially(0, () => {
          // Check if Monaco is now available
          if (typeof monaco !== 'undefined' && monaco.editor) {
            console.log('Monaco Editor loaded successfully');
            this.loaded = true;

            // Configure Monaco worker paths
            this.configureWorkers();

            // Notify that Monaco is ready
            window.dispatchEvent(new CustomEvent('monaco-ready'));

            // Call all registered callbacks
            this.callbacks.forEach(callback => {
              try {
                callback();
              } catch (error) {
                console.error('Error in Monaco callback:', error);
              }
            });

            resolve();
          } else {
            const error = new Error('Monaco Editor not available after loading all scripts');
            console.error(error);
            reject(error);
          }
        }, (error) => {
          console.error('Error loading Monaco Editor scripts:', error);
          reject(error);
        });
      } catch (error) {
        console.error('Error in Monaco loading process:', error);
        reject(error);
      }
    });

    return this.loadingPromise;
  }

  /**
   * Load CSS files
   */
  loadCssFiles() {
    this.requiredFiles.css.forEach(cssFile => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = cssFile;
      document.head.appendChild(link);
      console.log(`Loaded CSS: ${cssFile}`);
    });
  }

  /**
   * Load JS files sequentially
   * @param {number} index Current script index
   * @param {Function} onComplete Callback when all scripts are loaded
   * @param {Function} onError Callback when an error occurs
   */
  loadJsFilesSequentially(index, onComplete, onError) {
    if (index >= this.requiredFiles.js.length) {
      onComplete();
      return;
    }

    const scriptSrc = this.requiredFiles.js[index];
    const script = document.createElement('script');
    script.src = scriptSrc;
    script.async = false; // Load in order

    script.onload = () => {
      console.log(`Loaded script (${index + 1}/${this.requiredFiles.js.length}): ${scriptSrc}`);

      // Load the next script
      this.loadJsFilesSequentially(index + 1, onComplete, onError);
    };

    script.onerror = (err) => {
      console.error(`Error loading script: ${scriptSrc}`, err);
      onError(new Error(`Failed to load Monaco Editor script: ${scriptSrc}`));
    };

    document.head.appendChild(script);
  }

  /**
   * Configure Monaco Editor workers
   */
  configureWorkers() {
    try {
      console.log('Configuring Monaco Editor workers...');

      // Get the base URL for the workers
      const workerPath = `${this.basePath}/vs`;

      // Configure the worker paths
      self.MonacoEnvironment = {
        getWorkerUrl: function(moduleId, label) {
          console.log(`Getting worker URL for ${moduleId}, label: ${label}`);

          if (label === 'json') {
            return `${workerPath}/language/json/json.worker.js`;
          }
          if (label === 'css' || label === 'scss' || label === 'less') {
            return `${workerPath}/language/css/css.worker.js`;
          }
          if (label === 'html' || label === 'handlebars' || label === 'razor') {
            return `${workerPath}/language/html/html.worker.js`;
          }
          if (label === 'typescript' || label === 'javascript') {
            return `${workerPath}/language/typescript/ts.worker.js`;
          }

          return `${workerPath}/editor/editor.worker.js`;
        }
      };

      console.log('Monaco Editor workers configured successfully');
    } catch (error) {
      console.error('Error configuring Monaco Editor workers:', error);
    }
  }

  /**
   * Register a callback to be called when Monaco is loaded
   * @param {Function} callback The callback function
   */
  onLoad(callback) {
    if (this.loaded) {
      // Monaco already loaded, call the callback immediately
      console.log('Monaco already loaded, calling callback immediately');
      setTimeout(callback, 0);
    } else {
      // Add the callback to the queue
      console.log('Monaco not loaded yet, adding callback to queue');
      this.callbacks.push(callback);
    }
  }
}

// Create a singleton instance
const monacoLoader = new MonacoLoader();

// Export the loader
window.monacoLoader = monacoLoader;

// Load Monaco when the page is ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM content loaded, initializing Monaco loader');
  // Load Monaco after a short delay to ensure the page is ready
  setTimeout(() => {
    monacoLoader.load().catch(error => {
      console.error('Failed to load Monaco Editor:', error);
    });
  }, 500);
});
