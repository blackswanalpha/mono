// Plugin Marketplace for Mono Editor

/**
 * Plugin Marketplace class for browsing and installing plugins
 */
class PluginMarketplace {
  constructor() {
    this.marketplaceElement = null;
    this.pluginListElement = null;
    this.searchInput = null;
    this.categoryFilter = null;
    this.sortOption = null;
    this.isVisible = false;
    this.isLoading = false;
    this.featuredPlugins = [];
    this.allPlugins = [];
    this.filteredPlugins = [];
    
    // Initialize the marketplace when the DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initialize());
    } else {
      this.initialize();
    }
  }
  
  /**
   * Initialize the marketplace
   */
  initialize() {
    console.log('Initializing Plugin Marketplace...');
    
    // Create marketplace UI if it doesn't exist
    this.createMarketplaceUI();
    
    // Add event listeners
    this.addEventListeners();
    
    console.log('Plugin Marketplace initialized');
  }
  
  /**
   * Create the marketplace UI
   */
  createMarketplaceUI() {
    // Check if marketplace already exists
    const existingMarketplace = document.getElementById('plugin-marketplace');
    if (existingMarketplace) {
      this.marketplaceElement = existingMarketplace;
      return;
    }
    
    // Create marketplace container
    this.marketplaceElement = document.createElement('div');
    this.marketplaceElement.id = 'plugin-marketplace';
    this.marketplaceElement.className = 'plugin-marketplace';
    this.marketplaceElement.style.display = 'none'; // Hidden by default
    
    // Create marketplace header
    const header = document.createElement('div');
    header.className = 'marketplace-header';
    header.innerHTML = `
      <h2>Plugin Marketplace</h2>
      <div class="marketplace-controls">
        <div class="search-container">
          <input type="text" id="plugin-search" placeholder="Search plugins...">
          <button id="plugin-search-btn">Search</button>
        </div>
        <div class="filter-container">
          <select id="plugin-category">
            <option value="all">All Categories</option>
            <option value="themes">Themes</option>
            <option value="language">Language Support</option>
            <option value="tools">Tools</option>
            <option value="integration">Integrations</option>
          </select>
          <select id="plugin-sort">
            <option value="popular">Most Popular</option>
            <option value="recent">Recently Updated</option>
            <option value="name">Name</option>
          </select>
        </div>
      </div>
    `;
    
    // Create marketplace content
    const content = document.createElement('div');
    content.className = 'marketplace-content';
    
    // Create featured plugins section
    const featured = document.createElement('div');
    featured.className = 'featured-plugins';
    featured.innerHTML = '<h3>Featured Plugins</h3>';
    this.featuredPluginsElement = document.createElement('div');
    this.featuredPluginsElement.className = 'featured-plugins-list';
    featured.appendChild(this.featuredPluginsElement);
    
    // Create all plugins section
    const allPlugins = document.createElement('div');
    allPlugins.className = 'all-plugins';
    allPlugins.innerHTML = '<h3>All Plugins</h3>';
    this.pluginListElement = document.createElement('div');
    this.pluginListElement.className = 'plugin-list';
    allPlugins.appendChild(this.pluginListElement);
    
    // Create loading indicator
    const loading = document.createElement('div');
    loading.className = 'marketplace-loading';
    loading.innerHTML = '<div class="spinner"></div><p>Loading plugins...</p>';
    loading.style.display = 'none';
    this.loadingElement = loading;
    
    // Assemble the marketplace
    content.appendChild(featured);
    content.appendChild(allPlugins);
    content.appendChild(loading);
    
    this.marketplaceElement.appendChild(header);
    this.marketplaceElement.appendChild(content);
    
    // Add to the document
    document.body.appendChild(this.marketplaceElement);
    
    // Store references to elements
    this.searchInput = document.getElementById('plugin-search');
    this.categoryFilter = document.getElementById('plugin-category');
    this.sortOption = document.getElementById('plugin-sort');
  }
  
  /**
   * Add event listeners to marketplace elements
   */
  addEventListeners() {
    // Search button
    const searchBtn = document.getElementById('plugin-search-btn');
    if (searchBtn) {
      searchBtn.addEventListener('click', () => this.searchPlugins());
    }
    
    // Search input (search on enter)
    if (this.searchInput) {
      this.searchInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
          this.searchPlugins();
        }
      });
    }
    
    // Category filter
    if (this.categoryFilter) {
      this.categoryFilter.addEventListener('change', () => this.filterPlugins());
    }
    
    // Sort option
    if (this.sortOption) {
      this.sortOption.addEventListener('change', () => this.sortPlugins());
    }
  }
  
  /**
   * Show the marketplace
   */
  show() {
    if (!this.marketplaceElement) {
      this.createMarketplaceUI();
    }
    
    this.marketplaceElement.style.display = 'block';
    this.isVisible = true;
    
    // Load plugins if not already loaded
    if (this.allPlugins.length === 0) {
      this.loadPlugins();
    }
  }
  
  /**
   * Hide the marketplace
   */
  hide() {
    if (this.marketplaceElement) {
      this.marketplaceElement.style.display = 'none';
    }
    this.isVisible = false;
  }
  
  /**
   * Toggle the marketplace visibility
   */
  toggle() {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show();
    }
  }
  
  /**
   * Load plugins from the registry
   */
  async loadPlugins() {
    try {
      this.isLoading = true;
      this.showLoading();
      
      // Get plugins from the plugin manager
      if (window.pluginManager) {
        await window.pluginManager.loadPluginRegistry();
        this.allPlugins = window.pluginManager.pluginRegistry;
      } else {
        // Mock data for testing
        this.allPlugins = [
          {
            id: 'theme-editor',
            name: 'Theme Editor',
            description: 'Create and customize themes for Mono Editor',
            author: 'Mono Team',
            version: '1.0.0',
            category: 'themes',
            downloads: 1250,
            rating: 4.8,
            featured: true
          },
          {
            id: 'git-integration',
            name: 'Git Integration',
            description: 'Integrate Git version control into Mono Editor',
            author: 'Mono Team',
            version: '1.0.0',
            category: 'integration',
            downloads: 3200,
            rating: 4.9,
            featured: true
          },
          {
            id: 'code-snippets',
            name: 'Code Snippets',
            description: 'Manage and insert code snippets',
            author: 'Mono Team',
            version: '1.0.0',
            category: 'tools',
            downloads: 980,
            rating: 4.5,
            featured: false
          }
        ];
      }
      
      // Set featured plugins
      this.featuredPlugins = this.allPlugins.filter(plugin => plugin.featured);
      
      // Apply initial filtering and sorting
      this.filteredPlugins = [...this.allPlugins];
      this.sortPlugins();
      
      // Render plugins
      this.renderFeaturedPlugins();
      this.renderPluginList();
      
      this.isLoading = false;
      this.hideLoading();
    } catch (error) {
      console.error('Error loading plugins:', error);
      this.isLoading = false;
      this.hideLoading();
      this.showError('Failed to load plugins. Please try again later.');
    }
  }
  
  /**
   * Render featured plugins
   */
  renderFeaturedPlugins() {
    if (!this.featuredPluginsElement) return;
    
    this.featuredPluginsElement.innerHTML = '';
    
    if (this.featuredPlugins.length === 0) {
      this.featuredPluginsElement.innerHTML = '<p>No featured plugins available</p>';
      return;
    }
    
    for (const plugin of this.featuredPlugins) {
      const pluginElement = this.createPluginElement(plugin, true);
      this.featuredPluginsElement.appendChild(pluginElement);
    }
  }
  
  /**
   * Render the plugin list
   */
  renderPluginList() {
    if (!this.pluginListElement) return;
    
    this.pluginListElement.innerHTML = '';
    
    if (this.filteredPlugins.length === 0) {
      this.pluginListElement.innerHTML = '<p>No plugins found</p>';
      return;
    }
    
    for (const plugin of this.filteredPlugins) {
      const pluginElement = this.createPluginElement(plugin);
      this.pluginListElement.appendChild(pluginElement);
    }
  }
  
  /**
   * Create a plugin element
   * @param {Object} plugin - The plugin data
   * @param {boolean} featured - Whether this is a featured plugin
   * @returns {HTMLElement} The plugin element
   */
  createPluginElement(plugin, featured = false) {
    const pluginElement = document.createElement('div');
    pluginElement.className = `plugin-item ${featured ? 'featured' : ''}`;
    pluginElement.dataset.pluginId = plugin.id;
    
    // Check if plugin is installed
    const isInstalled = window.pluginManager && window.pluginManager.plugins.has(plugin.id);
    const isEnabled = window.pluginManager && window.pluginManager.enabledPlugins.has(plugin.id);
    
    pluginElement.innerHTML = `
      <div class="plugin-header">
        <h4 class="plugin-name">${plugin.name}</h4>
        <span class="plugin-version">v${plugin.version}</span>
      </div>
      <div class="plugin-description">${plugin.description}</div>
      <div class="plugin-meta">
        <span class="plugin-author">By ${plugin.author}</span>
        <span class="plugin-downloads">${plugin.downloads || 0} downloads</span>
        <span class="plugin-rating">${plugin.rating || 0}⭐</span>
      </div>
      <div class="plugin-actions">
        <button class="plugin-install-btn" ${isInstalled ? 'disabled' : ''}>
          ${isInstalled ? 'Installed' : 'Install'}
        </button>
        ${isInstalled ? `
          <button class="plugin-enable-btn" ${isEnabled ? 'disabled' : ''}>
            ${isEnabled ? 'Enabled' : 'Enable'}
          </button>
          <button class="plugin-settings-btn">Settings</button>
        ` : ''}
      </div>
    `;
    
    // Add event listeners
    const installBtn = pluginElement.querySelector('.plugin-install-btn');
    if (installBtn && !isInstalled) {
      installBtn.addEventListener('click', () => this.installPlugin(plugin.id));
    }
    
    const enableBtn = pluginElement.querySelector('.plugin-enable-btn');
    if (enableBtn && isInstalled && !isEnabled) {
      enableBtn.addEventListener('click', () => this.enablePlugin(plugin.id));
    }
    
    const settingsBtn = pluginElement.querySelector('.plugin-settings-btn');
    if (settingsBtn && isInstalled) {
      settingsBtn.addEventListener('click', () => this.openPluginSettings(plugin.id));
    }
    
    return pluginElement;
  }
  
  /**
   * Search plugins based on the search input
   */
  searchPlugins() {
    const searchTerm = this.searchInput.value.toLowerCase().trim();
    
    if (!searchTerm) {
      this.filteredPlugins = [...this.allPlugins];
    } else {
      this.filteredPlugins = this.allPlugins.filter(plugin => {
        return (
          plugin.name.toLowerCase().includes(searchTerm) ||
          plugin.description.toLowerCase().includes(searchTerm) ||
          plugin.author.toLowerCase().includes(searchTerm)
        );
      });
    }
    
    this.filterPlugins(false); // Don't re-filter, just apply category filter
  }
  
  /**
   * Filter plugins based on the category filter
   * @param {boolean} resetSearch - Whether to reset the search input
   */
  filterPlugins(resetSearch = true) {
    const category = this.categoryFilter.value;
    
    if (resetSearch) {
      this.searchInput.value = '';
      this.filteredPlugins = [...this.allPlugins];
    }
    
    if (category !== 'all') {
      this.filteredPlugins = this.filteredPlugins.filter(plugin => {
        return plugin.category === category;
      });
    }
    
    this.sortPlugins(false); // Don't re-sort, just apply current sort
  }
  
  /**
   * Sort plugins based on the sort option
   * @param {boolean} preserveFilters - Whether to preserve current filters
   */
  sortPlugins(preserveFilters = true) {
    if (!preserveFilters) {
      this.filteredPlugins = [...this.allPlugins];
    }
    
    const sortBy = this.sortOption.value;
    
    switch (sortBy) {
      case 'popular':
        this.filteredPlugins.sort((a, b) => (b.downloads || 0) - (a.downloads || 0));
        break;
      case 'recent':
        // Sort by version for now, in a real implementation this would use update date
        this.filteredPlugins.sort((a, b) => b.version.localeCompare(a.version));
        break;
      case 'name':
        this.filteredPlugins.sort((a, b) => a.name.localeCompare(b.name));
        break;
      default:
        // Default to popular
        this.filteredPlugins.sort((a, b) => (b.downloads || 0) - (a.downloads || 0));
    }
    
    this.renderPluginList();
  }
  
  /**
   * Install a plugin
   * @param {string} pluginId - The ID of the plugin to install
   */
  async installPlugin(pluginId) {
    try {
      console.log(`Installing plugin: ${pluginId}`);
      
      if (!window.pluginManager) {
        throw new Error('Plugin manager not available');
      }
      
      // Show loading indicator
      this.showLoading();
      
      // Install the plugin
      await window.pluginManager.loadPlugin(pluginId);
      
      // Enable the plugin
      await window.pluginManager.enablePlugin(pluginId);
      
      // Hide loading indicator
      this.hideLoading();
      
      // Refresh the plugin list
      this.renderPluginList();
      
      // Show success message
      this.showMessage(`Plugin ${pluginId} installed successfully`);
    } catch (error) {
      console.error(`Error installing plugin ${pluginId}:`, error);
      this.hideLoading();
      this.showError(`Failed to install plugin: ${error.message}`);
    }
  }
  
  /**
   * Enable a plugin
   * @param {string} pluginId - The ID of the plugin to enable
   */
  async enablePlugin(pluginId) {
    try {
      console.log(`Enabling plugin: ${pluginId}`);
      
      if (!window.pluginManager) {
        throw new Error('Plugin manager not available');
      }
      
      // Show loading indicator
      this.showLoading();
      
      // Enable the plugin
      await window.pluginManager.enablePlugin(pluginId);
      
      // Hide loading indicator
      this.hideLoading();
      
      // Refresh the plugin list
      this.renderPluginList();
      
      // Show success message
      this.showMessage(`Plugin ${pluginId} enabled successfully`);
    } catch (error) {
      console.error(`Error enabling plugin ${pluginId}:`, error);
      this.hideLoading();
      this.showError(`Failed to enable plugin: ${error.message}`);
    }
  }
  
  /**
   * Open plugin settings
   * @param {string} pluginId - The ID of the plugin to open settings for
   */
  openPluginSettings(pluginId) {
    console.log(`Opening settings for plugin: ${pluginId}`);
    // TODO: Implement plugin settings UI
  }
  
  /**
   * Show loading indicator
   */
  showLoading() {
    if (this.loadingElement) {
      this.loadingElement.style.display = 'flex';
    }
  }
  
  /**
   * Hide loading indicator
   */
  hideLoading() {
    if (this.loadingElement) {
      this.loadingElement.style.display = 'none';
    }
  }
  
  /**
   * Show an error message
   * @param {string} message - The error message
   */
  showError(message) {
    alert(`Error: ${message}`);
    // TODO: Implement a better error UI
  }
  
  /**
   * Show a success message
   * @param {string} message - The success message
   */
  showMessage(message) {
    alert(message);
    // TODO: Implement a better message UI
  }
}

// Create and export a singleton instance
const pluginMarketplace = new PluginMarketplace();

// Export the plugin marketplace
window.pluginMarketplace = pluginMarketplace;
