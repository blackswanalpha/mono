// Package Manager UI for Mono Editor

class PackageUI {
  constructor() {
    // Package manager instance
    this.packageManager = window.packageManager;

    // UI elements
    this.packageContainer = null;
    this.packageList = null;
    this.packageDetails = null;
    this.searchInput = null;
    this.filterSelect = null;

    // Initialize the UI
    this.initialize();
  }

  /**
   * Initialize the package manager UI
   */
  initialize() {
    console.log('Initializing package manager UI...');

    // Create the package manager UI
    this.createUI();

    // Add event listeners
    this.addEventListeners();

    // Load packages
    this.loadPackages();

    console.log('Package manager UI initialized');
  }

  /**
   * Create the package manager UI
   */
  createUI() {
    // Create the package manager container
    this.packageContainer = document.createElement('div');
    this.packageContainer.className = 'package-container';

    // Create the package manager header
    const header = document.createElement('div');
    header.className = 'package-header';

    // Create the search input
    const searchContainer = document.createElement('div');
    searchContainer.className = 'package-search-container';

    this.searchInput = document.createElement('input');
    this.searchInput.type = 'text';
    this.searchInput.className = 'package-search-input';
    this.searchInput.placeholder = 'Search packages...';

    searchContainer.appendChild(this.searchInput);

    // Create the filter select
    const filterContainer = document.createElement('div');
    filterContainer.className = 'package-filter-container';

    const filterLabel = document.createElement('label');
    filterLabel.textContent = 'Show: ';

    this.filterSelect = document.createElement('select');
    this.filterSelect.className = 'package-filter-select';

    const filterOptions = [
      { value: 'all', text: 'All Packages' },
      { value: 'installed', text: 'Installed' },
      { value: 'available', text: 'Available' }
    ];

    filterOptions.forEach(option => {
      const optionElement = document.createElement('option');
      optionElement.value = option.value;
      optionElement.textContent = option.text;
      this.filterSelect.appendChild(optionElement);
    });

    filterContainer.appendChild(filterLabel);
    filterContainer.appendChild(this.filterSelect);

    // Add the search and filter to the header
    header.appendChild(searchContainer);
    header.appendChild(filterContainer);

    // Create the package list
    this.packageList = document.createElement('div');
    this.packageList.className = 'package-list';

    // Create the package details
    this.packageDetails = document.createElement('div');
    this.packageDetails.className = 'package-details';
    this.packageDetails.innerHTML = '<div class="package-details-placeholder">Select a package to view details</div>';

    // Add the header, list, and details to the container
    this.packageContainer.appendChild(header);
    this.packageContainer.appendChild(this.packageList);
    this.packageContainer.appendChild(this.packageDetails);

    // Add the container to the packages panel
    const packagesPanel = document.getElementById('packages-panel');
    if (packagesPanel) {
      // Clear any existing content (like loading message)
      packagesPanel.innerHTML = '';

      // Add the package container to the panel
      packagesPanel.appendChild(this.packageContainer);
    }
  }

  /**
   * Add event listeners
   */
  addEventListeners() {
    // Search input
    this.searchInput.addEventListener('input', () => {
      this.filterPackages();
    });

    // Filter select
    this.filterSelect.addEventListener('change', () => {
      this.filterPackages();
    });
  }

  /**
   * Load packages
   */
  loadPackages() {
    // Clear the package list
    this.packageList.innerHTML = '';

    // Get installed packages
    const installedPackages = this.packageManager.getInstalledPackages();

    // Get available packages
    const availablePackages = this.packageManager.getAvailablePackages();

    // Create a set of all package names
    const allPackageNames = new Set([
      ...installedPackages.keys(),
      ...availablePackages.keys()
    ]);

    // Create a package item for each package
    allPackageNames.forEach(packageName => {
      const isInstalled = installedPackages.has(packageName);
      const packageInfo = isInstalled ? installedPackages.get(packageName) : availablePackages.get(packageName);

      if (packageInfo) {
        this.createPackageItem(packageInfo, isInstalled);
      }
    });
  }

  /**
   * Create a package item
   * @param {object} packageInfo - Package information
   * @param {boolean} isInstalled - Whether the package is installed
   */
  createPackageItem(packageInfo, isInstalled) {
    // Create the package item
    const packageItem = document.createElement('div');
    packageItem.className = 'package-item';
    packageItem.setAttribute('data-package', packageInfo.name);
    packageItem.setAttribute('data-installed', isInstalled.toString());

    // Create the package name
    const packageName = document.createElement('div');
    packageName.className = 'package-name';
    packageName.textContent = packageInfo.name;

    // Create the package version
    const packageVersion = document.createElement('div');
    packageVersion.className = 'package-version';
    packageVersion.textContent = packageInfo.version;

    // Create the package status
    const packageStatus = document.createElement('div');
    packageStatus.className = 'package-status';
    packageStatus.textContent = isInstalled ? 'Installed' : 'Available';

    // Add the name, version, and status to the item
    packageItem.appendChild(packageName);
    packageItem.appendChild(packageVersion);
    packageItem.appendChild(packageStatus);

    // Add click event listener
    packageItem.addEventListener('click', () => {
      this.showPackageDetails(packageInfo, isInstalled);
    });

    // Add the item to the list
    this.packageList.appendChild(packageItem);
  }

  /**
   * Show package details
   * @param {object} packageInfo - Package information
   * @param {boolean} isInstalled - Whether the package is installed
   */
  showPackageDetails(packageInfo, isInstalled) {
    // Clear the details
    this.packageDetails.innerHTML = '';

    // Create the package details header
    const header = document.createElement('div');
    header.className = 'package-details-header';

    // Create the package name
    const packageName = document.createElement('h2');
    packageName.className = 'package-details-name';
    packageName.textContent = packageInfo.name;

    // Create the package version
    const packageVersion = document.createElement('div');
    packageVersion.className = 'package-details-version';
    packageVersion.textContent = `v${packageInfo.version}`;

    // Add the name and version to the header
    header.appendChild(packageName);
    header.appendChild(packageVersion);

    // Create the package description
    const packageDescription = document.createElement('div');
    packageDescription.className = 'package-details-description';
    packageDescription.textContent = packageInfo.description || 'No description available';

    // Create the package actions
    const packageActions = document.createElement('div');
    packageActions.className = 'package-details-actions';

    if (isInstalled) {
      // Create the uninstall button
      const uninstallButton = document.createElement('button');
      uninstallButton.className = 'package-action-btn package-uninstall-btn';
      uninstallButton.textContent = 'Uninstall';
      uninstallButton.addEventListener('click', () => {
        this.uninstallPackage(packageInfo.name);
      });

      // Create the update button
      const updateButton = document.createElement('button');
      updateButton.className = 'package-action-btn package-update-btn';
      updateButton.textContent = 'Update';
      updateButton.addEventListener('click', () => {
        this.updatePackage(packageInfo.name);
      });

      // Add the buttons to the actions
      packageActions.appendChild(uninstallButton);
      packageActions.appendChild(updateButton);
    } else {
      // Create the install button
      const installButton = document.createElement('button');
      installButton.className = 'package-action-btn package-install-btn';
      installButton.textContent = 'Install';
      installButton.addEventListener('click', () => {
        this.installPackage(packageInfo.name);
      });

      // Add the button to the actions
      packageActions.appendChild(installButton);
    }

    // Add the header, description, and actions to the details
    this.packageDetails.appendChild(header);
    this.packageDetails.appendChild(packageDescription);
    this.packageDetails.appendChild(packageActions);
  }

  /**
   * Filter packages
   */
  filterPackages() {
    const searchTerm = this.searchInput.value.toLowerCase();
    const filterValue = this.filterSelect.value;

    // Get all package items
    const packageItems = this.packageList.querySelectorAll('.package-item');

    // Filter the items
    packageItems.forEach(item => {
      const packageName = item.getAttribute('data-package').toLowerCase();
      const isInstalled = item.getAttribute('data-installed') === 'true';

      // Check if the package matches the search term
      const matchesSearch = packageName.includes(searchTerm);

      // Check if the package matches the filter
      let matchesFilter = true;
      if (filterValue === 'installed') {
        matchesFilter = isInstalled;
      } else if (filterValue === 'available') {
        matchesFilter = !isInstalled;
      }

      // Show or hide the item
      item.style.display = matchesSearch && matchesFilter ? 'flex' : 'none';
    });
  }

  /**
   * Install a package
   * @param {string} packageName - Name of the package to install
   */
  async installPackage(packageName) {
    // Show loading state
    this.showLoading(`Installing ${packageName}...`);

    // Install the package
    const success = await this.packageManager.installPackage(packageName);

    // Reload packages
    this.loadPackages();

    // Show result
    if (success) {
      this.showSuccess(`Package ${packageName} installed successfully`);
    } else {
      this.showError(`Failed to install package ${packageName}`);
    }
  }

  /**
   * Uninstall a package
   * @param {string} packageName - Name of the package to uninstall
   */
  async uninstallPackage(packageName) {
    // Show loading state
    this.showLoading(`Uninstalling ${packageName}...`);

    // Uninstall the package
    const success = await this.packageManager.uninstallPackage(packageName);

    // Reload packages
    this.loadPackages();

    // Show result
    if (success) {
      this.showSuccess(`Package ${packageName} uninstalled successfully`);
    } else {
      this.showError(`Failed to uninstall package ${packageName}`);
    }
  }

  /**
   * Update a package
   * @param {string} packageName - Name of the package to update
   */
  async updatePackage(packageName) {
    // Show loading state
    this.showLoading(`Updating ${packageName}...`);

    // Update the package
    const success = await this.packageManager.updatePackage(packageName);

    // Reload packages
    this.loadPackages();

    // Show result
    if (success) {
      this.showSuccess(`Package ${packageName} updated successfully`);
    } else {
      this.showError(`Failed to update package ${packageName}`);
    }
  }

  /**
   * Show loading state
   * @param {string} message - Loading message
   */
  showLoading(message) {
    // TODO: Implement loading state
    console.log(message);
  }

  /**
   * Show success message
   * @param {string} message - Success message
   */
  showSuccess(message) {
    // TODO: Implement success message
    console.log(message);
  }

  /**
   * Show error message
   * @param {string} message - Error message
   */
  showError(message) {
    // TODO: Implement error message
    console.error(message);
  }
}

// Initialize the package UI when the page loads
let packageUI;
document.addEventListener('DOMContentLoaded', () => {
  // Wait for the package manager to be initialized
  setTimeout(() => {
    packageUI = new PackageUI();

    // Make it globally available
    window.packageUI = packageUI;
  }, 1000);
});

// Export the PackageUI class to window object
// Using window object instead of module.exports for browser compatibility
window.PackageUI = PackageUI;
