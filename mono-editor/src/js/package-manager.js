// Package Manager for Mono Editor

class PackageManager {
  constructor() {
    this.packages = new Map(); // Map of installed packages
    this.registry = new Map(); // Map of available packages in the registry
    this.dependencies = new Map(); // Map of package dependencies
    this.localPackagePath = ''; // Path to local packages
    this.remoteRegistryUrl = 'https://registry.mono-lang.org'; // URL to remote registry

    // Initialize the package manager
    this.initialize();
  }

  /**
   * Initialize the package manager
   */
  async initialize() {
    console.log('Initializing package manager...');

    try {
      // Set the local package path
      this.localPackagePath = await this.getLocalPackagePath();

      // Load installed packages
      await this.loadInstalledPackages();

      // Load registry
      await this.loadRegistry();

      console.log('Package manager initialized');
    } catch (error) {
      console.error('Error initializing package manager:', error);
    }
  }

  /**
   * Get the local package path
   * @returns {Promise<string>} The local package path
   */
  async getLocalPackagePath() {
    try {
      // Get the user data path
      const userDataPath = await window.api.getUserDataPath();

      // Create the packages directory if it doesn't exist
      const packagesPath = `${userDataPath}/packages`;
      await window.api.ensureDir(packagesPath);

      return packagesPath;
    } catch (error) {
      console.error('Error getting local package path:', error);
      throw error;
    }
  }

  /**
   * Load installed packages
   */
  async loadInstalledPackages() {
    try {
      // Get the list of installed packages
      const packageDirs = await window.api.readDir(this.localPackagePath);

      // Load each package
      for (const packageDir of packageDirs) {
        const packagePath = `${this.localPackagePath}/${packageDir}`;
        const packageInfo = await this.loadPackageInfo(packagePath);

        if (packageInfo) {
          this.packages.set(packageInfo.name, packageInfo);
        }
      }

      console.log(`Loaded ${this.packages.size} installed packages`);
    } catch (error) {
      console.error('Error loading installed packages:', error);
    }
  }

  /**
   * Load package information
   * @param {string} packagePath - Path to the package
   * @returns {Promise<object|null>} The package information or null if not found
   */
  async loadPackageInfo(packagePath) {
    try {
      // Read the package.json file
      const packageJsonPath = `${packagePath}/package.json`;
      const packageJson = await window.api.readFile(packageJsonPath);

      // Parse the package.json file
      const packageInfo = JSON.parse(packageJson);

      // Add the package path
      packageInfo.path = packagePath;

      return packageInfo;
    } catch (error) {
      console.error(`Error loading package info from ${packagePath}:`, error);
      return null;
    }
  }

  /**
   * Load the package registry
   */
  async loadRegistry() {
    try {
      // In a real implementation, this would fetch from a remote registry
      // For now, we'll use a mock registry
      this.registry = new Map([
        ['mono-core', { name: 'mono-core', version: '1.0.0', description: 'Core library for Mono' }],
        ['mono-ui', { name: 'mono-ui', version: '1.0.0', description: 'UI components for Mono' }],
        ['mono-data', { name: 'mono-data', version: '1.0.0', description: 'Data handling utilities for Mono' }],
        ['mono-net', { name: 'mono-net', version: '1.0.0', description: 'Networking utilities for Mono' }],
        ['mono-math', { name: 'mono-math', version: '1.0.0', description: 'Mathematical utilities for Mono' }]
      ]);

      console.log(`Loaded ${this.registry.size} packages from registry`);
    } catch (error) {
      console.error('Error loading registry:', error);
    }
  }

  /**
   * Get all installed packages
   * @returns {Map<string, object>} Map of installed packages
   */
  getInstalledPackages() {
    return this.packages;
  }

  /**
   * Get all available packages from the registry
   * @returns {Map<string, object>} Map of available packages
   */
  getAvailablePackages() {
    return this.registry;
  }

  /**
   * Install a package
   * @param {string} packageName - Name of the package to install
   * @param {string} version - Version of the package to install
   * @returns {Promise<boolean>} True if the package was installed successfully
   */
  async installPackage(packageName, version = 'latest') {
    try {
      console.log(`Installing package ${packageName}@${version}...`);

      // Check if the package is already installed
      if (this.packages.has(packageName)) {
        console.log(`Package ${packageName} is already installed`);
        return true;
      }

      // Check if the package is available in the registry
      if (!this.registry.has(packageName)) {
        console.error(`Package ${packageName} not found in registry`);
        return false;
      }

      // Get the package info from the registry
      const packageInfo = this.registry.get(packageName);

      // In a real implementation, this would download the package
      // For now, we'll just create a mock package
      const packagePath = `${this.localPackagePath}/${packageName}`;
      await window.api.ensureDir(packagePath);

      // Create a package.json file
      const packageJson = {
        name: packageName,
        version: packageInfo.version,
        description: packageInfo.description
      };

      // Write the package.json file
      await window.api.writeFile(`${packagePath}/package.json`, JSON.stringify(packageJson, null, 2), 'utf8');

      // Add the package to the installed packages
      packageInfo.path = packagePath;
      this.packages.set(packageName, packageInfo);

      console.log(`Package ${packageName} installed successfully`);
      return true;
    } catch (error) {
      console.error(`Error installing package ${packageName}:`, error);
      return false;
    }
  }

  /**
   * Uninstall a package
   * @param {string} packageName - Name of the package to uninstall
   * @returns {Promise<boolean>} True if the package was uninstalled successfully
   */
  async uninstallPackage(packageName) {
    try {
      console.log(`Uninstalling package ${packageName}...`);

      // Check if the package is installed
      if (!this.packages.has(packageName)) {
        console.error(`Package ${packageName} is not installed`);
        return false;
      }

      // Get the package info
      const packageInfo = this.packages.get(packageName);

      // Remove the package directory
      await window.api.removeDir(packageInfo.path);

      // Remove the package from the installed packages
      this.packages.delete(packageName);

      console.log(`Package ${packageName} uninstalled successfully`);
      return true;
    } catch (error) {
      console.error(`Error uninstalling package ${packageName}:`, error);
      return false;
    }
  }

  /**
   * Update a package
   * @param {string} packageName - Name of the package to update
   * @returns {Promise<boolean>} True if the package was updated successfully
   */
  async updatePackage(packageName) {
    try {
      console.log(`Updating package ${packageName}...`);

      // Check if the package is installed
      if (!this.packages.has(packageName)) {
        console.error(`Package ${packageName} is not installed`);
        return false;
      }

      // Uninstall the package
      await this.uninstallPackage(packageName);

      // Install the package
      return await this.installPackage(packageName);
    } catch (error) {
      console.error(`Error updating package ${packageName}:`, error);
      return false;
    }
  }
}

// Initialize the package manager when the page loads
let packageManager;
document.addEventListener('DOMContentLoaded', () => {
  packageManager = new PackageManager();

  // Make it globally available
  window.packageManager = packageManager;
});

// Export the PackageManager class to window object
// Using window object instead of module.exports for browser compatibility
window.PackageManager = PackageManager;
