// Plugin System for Mono Editor

/**
 * Plugin Manager class for handling plugins in the Mono Editor
 */
class PluginManager {
  constructor() {
    // Initialize plugin storage
    this.plugins = new Map(); // Stores loaded plugins
    this.enabledPlugins = new Set(); // Tracks which plugins are enabled
    this.pluginSettings = new Map(); // Stores plugin settings
    this.pluginRegistry = []; // Registry of available plugins
    this.pluginEventListeners = new Map(); // Event listeners for plugins
    
    // Plugin directories
    this.builtinPluginsDir = 'plugins/builtin';
    this.userPluginsDir = null; // Will be set when user data path is available
    
    // Plugin events
    this.events = {
      PLUGIN_LOADED: 'plugin-loaded',
      PLUGIN_ENABLED: 'plugin-enabled',
      PLUGIN_DISABLED: 'plugin-disabled',
      PLUGIN_UNLOADED: 'plugin-unloaded',
      PLUGIN_ERROR: 'plugin-error',
      PLUGIN_SETTINGS_CHANGED: 'plugin-settings-changed'
    };
    
    // Initialize event listeners
    this.eventListeners = {};
    Object.values(this.events).forEach(event => {
      this.eventListeners[event] = [];
    });
    
    console.log('Plugin Manager initialized');
  }
  
  /**
   * Initialize the plugin system
   */
  async initialize() {
    try {
      console.log('Initializing plugin system...');
      
      // Get user data path for storing plugins
      if (window.api && typeof window.api.getUserDataPath === 'function') {
        const userDataPath = await window.api.getUserDataPath();
        this.userPluginsDir = `${userDataPath}/plugins`;
        
        // Ensure the plugins directory exists
        if (window.api && typeof window.api.ensureDir === 'function') {
          await window.api.ensureDir(this.userPluginsDir);
        }
      } else {
        console.warn('getUserDataPath API not available, using fallback for user plugins');
        this.userPluginsDir = 'plugins/user';
      }
      
      // Load plugin registry
      await this.loadPluginRegistry();
      
      // Load enabled plugins
      await this.loadEnabledPlugins();
      
      console.log('Plugin system initialized successfully');
      return true;
    } catch (error) {
      console.error('Error initializing plugin system:', error);
      return false;
    }
  }
  
  /**
   * Load the plugin registry from local storage and remote sources
   */
  async loadPluginRegistry() {
    try {
      console.log('Loading plugin registry...');
      
      // Load from local storage first
      const storedRegistry = localStorage.getItem('mono-plugin-registry');
      if (storedRegistry) {
        this.pluginRegistry = JSON.parse(storedRegistry);
      }
      
      // TODO: Fetch from remote registry when API is available
      
      console.log(`Loaded ${this.pluginRegistry.length} plugins in registry`);
      return this.pluginRegistry;
    } catch (error) {
      console.error('Error loading plugin registry:', error);
      this.pluginRegistry = [];
      return [];
    }
  }
  
  /**
   * Load plugins that were previously enabled
   */
  async loadEnabledPlugins() {
    try {
      // Get enabled plugins from local storage
      const enabledPluginIds = JSON.parse(localStorage.getItem('mono-enabled-plugins') || '[]');
      console.log(`Found ${enabledPluginIds.length} previously enabled plugins`);
      
      // Load and enable each plugin
      for (const pluginId of enabledPluginIds) {
        try {
          await this.loadPlugin(pluginId);
          await this.enablePlugin(pluginId);
        } catch (pluginError) {
          console.error(`Error loading enabled plugin ${pluginId}:`, pluginError);
          this.triggerEvent(this.events.PLUGIN_ERROR, { 
            pluginId, 
            error: pluginError 
          });
        }
      }
      
      return true;
    } catch (error) {
      console.error('Error loading enabled plugins:', error);
      return false;
    }
  }
  
  /**
   * Load a plugin by ID
   * @param {string} pluginId - The ID of the plugin to load
   */
  async loadPlugin(pluginId) {
    try {
      console.log(`Loading plugin: ${pluginId}`);
      
      // Check if plugin is already loaded
      if (this.plugins.has(pluginId)) {
        console.log(`Plugin ${pluginId} is already loaded`);
        return this.plugins.get(pluginId);
      }
      
      // Find plugin in registry
      const pluginInfo = this.pluginRegistry.find(p => p.id === pluginId);
      if (!pluginInfo) {
        throw new Error(`Plugin ${pluginId} not found in registry`);
      }
      
      // Create plugin instance
      const plugin = {
        id: pluginId,
        name: pluginInfo.name,
        version: pluginInfo.version,
        description: pluginInfo.description,
        author: pluginInfo.author,
        main: pluginInfo.main,
        api: {},
        status: 'loaded',
        settings: this.pluginSettings.get(pluginId) || {}
      };
      
      // Load plugin code
      // In a real implementation, this would dynamically load the plugin's JavaScript
      // For now, we'll just create a placeholder
      
      // Store the plugin
      this.plugins.set(pluginId, plugin);
      
      // Trigger event
      this.triggerEvent(this.events.PLUGIN_LOADED, { plugin });
      
      console.log(`Plugin ${pluginId} loaded successfully`);
      return plugin;
    } catch (error) {
      console.error(`Error loading plugin ${pluginId}:`, error);
      this.triggerEvent(this.events.PLUGIN_ERROR, { 
        pluginId, 
        error 
      });
      throw error;
    }
  }
  
  /**
   * Enable a plugin by ID
   * @param {string} pluginId - The ID of the plugin to enable
   */
  async enablePlugin(pluginId) {
    try {
      console.log(`Enabling plugin: ${pluginId}`);
      
      // Check if plugin is loaded
      if (!this.plugins.has(pluginId)) {
        // Try to load the plugin first
        await this.loadPlugin(pluginId);
      }
      
      const plugin = this.plugins.get(pluginId);
      
      // Check if already enabled
      if (this.enabledPlugins.has(pluginId)) {
        console.log(`Plugin ${pluginId} is already enabled`);
        return true;
      }
      
      // Enable the plugin
      this.enabledPlugins.add(pluginId);
      plugin.status = 'enabled';
      
      // Update local storage
      this.saveEnabledPlugins();
      
      // Trigger event
      this.triggerEvent(this.events.PLUGIN_ENABLED, { plugin });
      
      console.log(`Plugin ${pluginId} enabled successfully`);
      return true;
    } catch (error) {
      console.error(`Error enabling plugin ${pluginId}:`, error);
      this.triggerEvent(this.events.PLUGIN_ERROR, { 
        pluginId, 
        error 
      });
      return false;
    }
  }
  
  /**
   * Disable a plugin by ID
   * @param {string} pluginId - The ID of the plugin to disable
   */
  async disablePlugin(pluginId) {
    try {
      console.log(`Disabling plugin: ${pluginId}`);
      
      // Check if plugin is enabled
      if (!this.enabledPlugins.has(pluginId)) {
        console.log(`Plugin ${pluginId} is not enabled`);
        return true;
      }
      
      const plugin = this.plugins.get(pluginId);
      if (!plugin) {
        throw new Error(`Plugin ${pluginId} is not loaded`);
      }
      
      // Disable the plugin
      this.enabledPlugins.delete(pluginId);
      plugin.status = 'loaded';
      
      // Update local storage
      this.saveEnabledPlugins();
      
      // Trigger event
      this.triggerEvent(this.events.PLUGIN_DISABLED, { plugin });
      
      console.log(`Plugin ${pluginId} disabled successfully`);
      return true;
    } catch (error) {
      console.error(`Error disabling plugin ${pluginId}:`, error);
      this.triggerEvent(this.events.PLUGIN_ERROR, { 
        pluginId, 
        error 
      });
      return false;
    }
  }
  
  /**
   * Save the list of enabled plugins to local storage
   */
  saveEnabledPlugins() {
    localStorage.setItem('mono-enabled-plugins', JSON.stringify([...this.enabledPlugins]));
  }
  
  /**
   * Register an event listener for plugin events
   * @param {string} event - The event to listen for
   * @param {Function} callback - The callback function
   */
  on(event, callback) {
    if (!this.eventListeners[event]) {
      this.eventListeners[event] = [];
    }
    this.eventListeners[event].push(callback);
    
    // Return a function to remove the listener
    return () => {
      this.eventListeners[event] = this.eventListeners[event].filter(cb => cb !== callback);
    };
  }
  
  /**
   * Trigger an event
   * @param {string} event - The event to trigger
   * @param {Object} data - The event data
   */
  triggerEvent(event, data) {
    if (this.eventListeners[event]) {
      this.eventListeners[event].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in plugin event listener for ${event}:`, error);
        }
      });
    }
  }
}

// Create and export a singleton instance
const pluginManager = new PluginManager();

// Export the plugin manager
window.pluginManager = pluginManager;
