/**
 * Switch Store - A state management system for the Switch framework
 * 
 * This module provides a centralized state management system similar to Redux or Vuex.
 * It allows components to share state and react to state changes.
 */

// Create the Switch namespace if it doesn't exist
window.Switch = window.Switch || {};

// Create the Store namespace
Switch.Store = {};

/**
 * Create a new store
 * @param {Object} options - Store options
 * @returns {Object} - The store instance
 */
Switch.Store.createStore = function(options = {}) {
    // Default options
    const defaultOptions = {
        state: {},
        getters: {},
        mutations: {},
        actions: {},
        modules: {},
        plugins: [],
        strict: false
    };
    
    // Merge options
    const mergedOptions = Object.assign({}, defaultOptions, options);
    
    // Create the store
    const store = {
        // State
        _state: mergedOptions.state,
        
        // Getters
        _getters: {},
        
        // Mutations
        _mutations: mergedOptions.mutations,
        
        // Actions
        _actions: mergedOptions.actions,
        
        // Modules
        _modules: {},
        
        // Subscribers
        _subscribers: [],
        
        // Strict mode
        _strict: mergedOptions.strict,
        
        // Is a mutation in progress
        _committing: false,
        
        /**
         * Get the state
         * @returns {Object} - The state
         */
        get state() {
            return this._state;
        },
        
        /**
         * Get a getter
         * @param {string} name - The getter name
         * @returns {*} - The getter value
         */
        getters: {},
        
        /**
         * Commit a mutation
         * @param {string} type - The mutation type
         * @param {*} payload - The mutation payload
         */
        commit(type, payload) {
            // Check if the mutation exists
            if (!this._mutations[type]) {
                console.error(`[Switch.Store] Unknown mutation type: ${type}`);
                return;
            }
            
            // Set committing flag
            const prevCommitting = this._committing;
            this._committing = true;
            
            try {
                // Call the mutation
                this._mutations[type](this._state, payload);
                
                // Notify subscribers
                this._subscribers.forEach(sub => sub({
                    type,
                    payload
                }, this._state));
            } finally {
                // Reset committing flag
                this._committing = prevCommitting;
            }
        },
        
        /**
         * Dispatch an action
         * @param {string} type - The action type
         * @param {*} payload - The action payload
         * @returns {Promise} - A promise that resolves when the action is complete
         */
        dispatch(type, payload) {
            // Check if the action exists
            if (!this._actions[type]) {
                console.error(`[Switch.Store] Unknown action type: ${type}`);
                return Promise.resolve();
            }
            
            // Call the action
            const result = this._actions[type]({
                state: this._state,
                getters: this.getters,
                commit: this.commit.bind(this),
                dispatch: this.dispatch.bind(this)
            }, payload);
            
            // Return a promise
            return Promise.resolve(result);
        },
        
        /**
         * Subscribe to store mutations
         * @param {Function} fn - The subscriber function
         * @returns {Function} - A function to unsubscribe
         */
        subscribe(fn) {
            // Add the subscriber
            this._subscribers.push(fn);
            
            // Return a function to unsubscribe
            return () => {
                const index = this._subscribers.indexOf(fn);
                if (index !== -1) {
                    this._subscribers.splice(index, 1);
                }
            };
        },
        
        /**
         * Watch a getter or state path for changes
         * @param {string|Function} getter - The getter or state path
         * @param {Function} cb - The callback function
         * @param {Object} options - Watch options
         * @returns {Function} - A function to stop watching
         */
        watch(getter, cb, options = {}) {
            // Default options
            const defaultOptions = {
                deep: false,
                immediate: false
            };
            
            // Merge options
            const mergedOptions = Object.assign({}, defaultOptions, options);
            
            // Get the current value
            const getValue = () => {
                if (typeof getter === 'function') {
                    return getter(this._state, this.getters);
                } else if (typeof getter === 'string') {
                    // Split the path
                    const path = getter.split('.');
                    
                    // Get the value
                    let value = this._state;
                    for (const key of path) {
                        value = value[key];
                    }
                    
                    return value;
                } else {
                    console.error('[Switch.Store] Invalid getter type');
                    return undefined;
                }
            };
            
            // Get the initial value
            let oldValue = getValue();
            
            // Call the callback immediately if requested
            if (mergedOptions.immediate) {
                cb(oldValue, oldValue);
            }
            
            // Create the subscriber
            const subscriber = (mutation, state) => {
                // Get the new value
                const newValue = getValue();
                
                // Check if the value has changed
                if (newValue !== oldValue) {
                    // Call the callback
                    cb(newValue, oldValue);
                    
                    // Update the old value
                    oldValue = newValue;
                }
            };
            
            // Subscribe to mutations
            return this.subscribe(subscriber);
        },
        
        /**
         * Register a module
         * @param {string} name - The module name
         * @param {Object} module - The module
         */
        registerModule(name, module) {
            // Add the module
            this._modules[name] = module;
            
            // Add the module state
            this._state[name] = module.state || {};
            
            // Add the module getters
            if (module.getters) {
                for (const [key, getter] of Object.entries(module.getters)) {
                    const fullKey = `${name}/${key}`;
                    this._getters[fullKey] = (state, getters) => {
                        return getter(state[name], getters);
                    };
                    
                    // Add the getter to the getters object
                    Object.defineProperty(this.getters, fullKey, {
                        get: () => this._getters[fullKey](this._state, this.getters),
                        enumerable: true
                    });
                }
            }
            
            // Add the module mutations
            if (module.mutations) {
                for (const [key, mutation] of Object.entries(module.mutations)) {
                    const fullKey = `${name}/${key}`;
                    this._mutations[fullKey] = (state, payload) => {
                        mutation(state[name], payload);
                    };
                }
            }
            
            // Add the module actions
            if (module.actions) {
                for (const [key, action] of Object.entries(module.actions)) {
                    const fullKey = `${name}/${key}`;
                    this._actions[fullKey] = (context, payload) => {
                        const moduleContext = {
                            state: context.state[name],
                            getters: context.getters,
                            commit: (type, payload) => {
                                context.commit(`${name}/${type}`, payload);
                            },
                            dispatch: (type, payload) => {
                                return context.dispatch(`${name}/${type}`, payload);
                            }
                        };
                        
                        return action(moduleContext, payload);
                    };
                }
            }
        },
        
        /**
         * Unregister a module
         * @param {string} name - The module name
         */
        unregisterModule(name) {
            // Check if the module exists
            if (!this._modules[name]) {
                console.error(`[Switch.Store] Module not found: ${name}`);
                return;
            }
            
            // Remove the module state
            delete this._state[name];
            
            // Remove the module getters
            if (this._modules[name].getters) {
                for (const key of Object.keys(this._modules[name].getters)) {
                    const fullKey = `${name}/${key}`;
                    delete this._getters[fullKey];
                    delete this.getters[fullKey];
                }
            }
            
            // Remove the module mutations
            if (this._modules[name].mutations) {
                for (const key of Object.keys(this._modules[name].mutations)) {
                    const fullKey = `${name}/${key}`;
                    delete this._mutations[fullKey];
                }
            }
            
            // Remove the module actions
            if (this._modules[name].actions) {
                for (const key of Object.keys(this._modules[name].actions)) {
                    const fullKey = `${name}/${key}`;
                    delete this._actions[fullKey];
                }
            }
            
            // Remove the module
            delete this._modules[name];
        }
    };
    
    // Initialize getters
    for (const [key, getter] of Object.entries(mergedOptions.getters)) {
        store._getters[key] = getter;
        
        // Add the getter to the getters object
        Object.defineProperty(store.getters, key, {
            get: () => store._getters[key](store._state, store.getters),
            enumerable: true
        });
    }
    
    // Register modules
    for (const [name, module] of Object.entries(mergedOptions.modules)) {
        store.registerModule(name, module);
    }
    
    // Apply plugins
    mergedOptions.plugins.forEach(plugin => plugin(store));
    
    return store;
};

/**
 * Create a plugin that saves the state to localStorage
 * @param {Object} options - Plugin options
 * @returns {Function} - The plugin function
 */
Switch.Store.createLocalStoragePlugin = function(options = {}) {
    // Default options
    const defaultOptions = {
        key: 'switch-store',
        paths: null,
        storage: window.localStorage
    };
    
    // Merge options
    const mergedOptions = Object.assign({}, defaultOptions, options);
    
    // Create the plugin
    return function(store) {
        // Load the state from localStorage
        const data = mergedOptions.storage.getItem(mergedOptions.key);
        if (data) {
            try {
                const state = JSON.parse(data);
                
                // Merge the state
                if (mergedOptions.paths) {
                    mergedOptions.paths.forEach(path => {
                        // Split the path
                        const keys = path.split('.');
                        
                        // Get the value from the saved state
                        let savedValue = state;
                        for (const key of keys) {
                            if (savedValue === undefined) {
                                return;
                            }
                            savedValue = savedValue[key];
                        }
                        
                        // Set the value in the store state
                        let storeState = store.state;
                        for (let i = 0; i < keys.length - 1; i++) {
                            storeState = storeState[keys[i]];
                        }
                        
                        storeState[keys[keys.length - 1]] = savedValue;
                    });
                } else {
                    // Merge the entire state
                    Object.assign(store.state, state);
                }
            } catch (e) {
                console.error('[Switch.Store] Could not load state from localStorage:', e);
            }
        }
        
        // Subscribe to mutations
        store.subscribe((mutation, state) => {
            try {
                // Save the state to localStorage
                if (mergedOptions.paths) {
                    // Save only the specified paths
                    const saveState = {};
                    
                    mergedOptions.paths.forEach(path => {
                        // Split the path
                        const keys = path.split('.');
                        
                        // Get the value from the store state
                        let value = state;
                        for (const key of keys) {
                            if (value === undefined) {
                                return;
                            }
                            value = value[key];
                        }
                        
                        // Set the value in the save state
                        let saveObj = saveState;
                        for (let i = 0; i < keys.length - 1; i++) {
                            if (!saveObj[keys[i]]) {
                                saveObj[keys[i]] = {};
                            }
                            saveObj = saveObj[keys[i]];
                        }
                        
                        saveObj[keys[keys.length - 1]] = value;
                    });
                    
                    mergedOptions.storage.setItem(mergedOptions.key, JSON.stringify(saveState));
                } else {
                    // Save the entire state
                    mergedOptions.storage.setItem(mergedOptions.key, JSON.stringify(state));
                }
            } catch (e) {
                console.error('[Switch.Store] Could not save state to localStorage:', e);
            }
        });
    };
};

// Export the Store namespace
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Switch.Store;
}
