// Module shim for browser compatibility
// This script provides a CommonJS-like module system for the browser

(function() {
  // Create a module system if it doesn't exist
  if (typeof window.module === 'undefined') {
    // Create a simple module object
    window.module = {
      exports: {}
    };
    
    // Create a simple require function
    window.require = function(moduleName) {
      console.log(`Module requested: ${moduleName}`);
      
      // Handle known modules
      switch (moduleName) {
        case './package-manager':
          return { PackageManager: window.PackageManager };
        case './package-ui':
          return { PackageUI: window.PackageUI };
        default:
          console.warn(`Unknown module requested: ${moduleName}`);
          return {};
      }
    };
    
    console.log('Module shim initialized');
  }
})();
