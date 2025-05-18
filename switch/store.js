/**
 * Switch Store - State Management System
 * 
 * A centralized state management system for the Switch framework,
 * inspired by Redux and Vuex.
 */

(function(global) {
    'use strict';
    
    /**
     * Create a new Store
     * @param {Object} options - Store options
     * @returns {Object} - Store instance
     */
    function createStore(options = {}) {
        // Default options
        const defaultOptions = {
            state: {},
            mutations: {},
            actions: {},
            getters: {},
            modules: {},
            strict: false,
            plugins: []
        };
        
        // Merge options
        const mergedOptions = Object.assign({}, defaultOptions, options);
        
        // Store state
        let state = Object.assign({}, mergedOptions.state);
        
        // Store mutations
        const mutations = Object.assign({}, mergedOptions.mutations);
        
        // Store actions
        const actions = Object.assign({}, mergedOptions.actions);
        
        // Store getters
        const getters = {};
        
        // Store modules
        const modules = {};
        
        // Store subscribers
        const subscribers = [];
        
        // Process modules
        if (mergedOptions.modules) {
            Object.keys(mergedOptions.modules).forEach(key => {
                const module = mergedOptions.modules[key];
                modules[key] = module;
                
                // Add module state to store state
                if (module.state) {
                    state[key] = Object.assign({}, module.state);
                }
                
                // Add module mutations to store mutations
                if (module.mutations) {
                    Object.keys(module.mutations).forEach(mutationKey => {
                        const fullKey = `${key}/${mutationKey}`;
                        mutations[fullKey] = module.mutations[mutationKey];
                    });
                }
                
                // Add module actions to store actions
                if (module.actions) {
                    Object.keys(module.actions).forEach(actionKey => {
                        const fullKey = `${key}/${actionKey}`;
                        actions[fullKey] = module.actions[actionKey];
                    });
                }
                
                // Add module getters to store getters
                if (module.getters) {
                    Object.keys(module.getters).forEach(getterKey => {
                        const fullKey = `${key}/${getterKey}`;
                        getters[fullKey] = module.getters[getterKey];
                    });
                }
            });
        }
        
        // Process getters
        Object.keys(mergedOptions.getters || {}).forEach(key => {
            Object.defineProperty(getters, key, {
                get: () => mergedOptions.getters[key](state, getters),
                enumerable: true
            });
        });
        
        // Create the store
        const store = {
            /**
             * Get the current state
             * @returns {Object} - Current state
             */
            getState() {
                return state;
            },
            
            /**
             * Get a specific state value
             * @param {string} path - Path to the state value
             * @returns {*} - State value
             */
            state(path) {
                if (!path) return state;
                
                return path.split('.').reduce((obj, key) => {
                    return obj && obj[key] !== undefined ? obj[key] : undefined;
                }, state);
            },
            
            /**
             * Get a specific getter value
             * @param {string} key - Getter key
             * @returns {*} - Getter value
             */
            getter(key) {
                return getters[key];
            },
            
            /**
             * Commit a mutation
             * @param {string} type - Mutation type
             * @param {*} payload - Mutation payload
             */
            commit(type, payload) {
                // Check if mutation exists
                if (!mutations[type]) {
                    console.error(`[Switch Store] Unknown mutation type: ${type}`);
                    return;
                }
                
                // Create mutation object
                const mutation = {
                    type,
                    payload
                };
                
                // Apply mutation
                const prevState = JSON.parse(JSON.stringify(state));
                mutations[type](state, payload);
                const nextState = state;
                
                // Notify subscribers
                subscribers.forEach(sub => sub(mutation, nextState, prevState));
            },
            
            /**
             * Dispatch an action
             * @param {string} type - Action type
             * @param {*} payload - Action payload
             * @returns {Promise} - Promise that resolves when the action is complete
             */
            dispatch(type, payload) {
                // Check if action exists
                if (!actions[type]) {
                    console.error(`[Switch Store] Unknown action type: ${type}`);
                    return Promise.reject(`Unknown action type: ${type}`);
                }
                
                // Create context
                const context = {
                    state,
                    getters,
                    commit: this.commit.bind(this),
                    dispatch: this.dispatch.bind(this)
                };
                
                // Call action
                try {
                    const result = actions[type](context, payload);
                    return Promise.resolve(result);
                } catch (error) {
                    return Promise.reject(error);
                }
            },
            
            /**
             * Subscribe to store mutations
             * @param {Function} subscriber - Subscriber function
             * @returns {Function} - Unsubscribe function
             */
            subscribe(subscriber) {
                if (typeof subscriber !== 'function') {
                    console.error('[Switch Store] Subscriber must be a function');
                    return;
                }
                
                subscribers.push(subscriber);
                
                // Return unsubscribe function
                return () => {
                    const index = subscribers.indexOf(subscriber);
                    if (index !== -1) {
                        subscribers.splice(index, 1);
                    }
                };
            },
            
            /**
             * Register a module
             * @param {string} key - Module key
             * @param {Object} module - Module definition
             */
            registerModule(key, module) {
                // Add module to modules
                modules[key] = module;
                
                // Add module state to store state
                if (module.state) {
                    state[key] = Object.assign({}, module.state);
                }
                
                // Add module mutations to store mutations
                if (module.mutations) {
                    Object.keys(module.mutations).forEach(mutationKey => {
                        const fullKey = `${key}/${mutationKey}`;
                        mutations[fullKey] = module.mutations[mutationKey];
                    });
                }
                
                // Add module actions to store actions
                if (module.actions) {
                    Object.keys(module.actions).forEach(actionKey => {
                        const fullKey = `${key}/${actionKey}`;
                        actions[fullKey] = module.actions[actionKey];
                    });
                }
                
                // Add module getters to store getters
                if (module.getters) {
                    Object.keys(module.getters).forEach(getterKey => {
                        const fullKey = `${key}/${getterKey}`;
                        Object.defineProperty(getters, fullKey, {
                            get: () => module.getters[getterKey](state[key], getters),
                            enumerable: true
                        });
                    });
                }
            },
            
            /**
             * Unregister a module
             * @param {string} key - Module key
             */
            unregisterModule(key) {
                // Remove module from modules
                delete modules[key];
                
                // Remove module state from store state
                delete state[key];
                
                // Remove module mutations from store mutations
                Object.keys(mutations).forEach(mutationKey => {
                    if (mutationKey.startsWith(`${key}/`)) {
                        delete mutations[mutationKey];
                    }
                });
                
                // Remove module actions from store actions
                Object.keys(actions).forEach(actionKey => {
                    if (actionKey.startsWith(`${key}/`)) {
                        delete actions[actionKey];
                    }
                });
                
                // Remove module getters from store getters
                Object.keys(getters).forEach(getterKey => {
                    if (getterKey.startsWith(`${key}/`)) {
                        delete getters[getterKey];
                    }
                });
            },
            
            /**
             * Reset the store state
             */
            reset() {
                state = Object.assign({}, mergedOptions.state);
                
                // Reset module states
                Object.keys(modules).forEach(key => {
                    if (modules[key].state) {
                        state[key] = Object.assign({}, modules[key].state);
                    }
                });
            }
        };
        
        // Apply plugins
        if (mergedOptions.plugins && Array.isArray(mergedOptions.plugins)) {
            mergedOptions.plugins.forEach(plugin => {
                if (typeof plugin === 'function') {
                    plugin(store);
                }
            });
        }
        
        return store;
    }
    
    /**
     * Create a logger plugin
     * @param {Object} options - Logger options
     * @returns {Function} - Logger plugin
     */
    function createLogger(options = {}) {
        return store => {
            store.subscribe((mutation, state, prevState) => {
                const time = new Date();
                const formattedTime = `${time.getHours()}:${time.getMinutes()}:${time.getSeconds()}`;
                
                console.groupCollapsed(`[Switch Store] mutation ${mutation.type} @ ${formattedTime}`);
                console.log('Prev state:', prevState);
                console.log('Mutation:', mutation);
                console.log('Next state:', state);
                console.groupEnd();
            });
        };
    }
    
    /**
     * Create a persistence plugin
     * @param {Object} options - Persistence options
     * @returns {Function} - Persistence plugin
     */
    function createPersistence(options = {}) {
        const defaultOptions = {
            key: 'switch-store',
            storage: localStorage,
            paths: null
        };
        
        const mergedOptions = Object.assign({}, defaultOptions, options);
        
        return store => {
            // Load state from storage
            try {
                const savedState = mergedOptions.storage.getItem(mergedOptions.key);
                if (savedState) {
                    const state = JSON.parse(savedState);
                    
                    // Apply saved state to store
                    Object.keys(state).forEach(key => {
                        if (!mergedOptions.paths || mergedOptions.paths.includes(key)) {
                            store.commit(`${key}/setState`, state[key]);
                        }
                    });
                }
            } catch (error) {
                console.error('[Switch Store] Error loading state from storage:', error);
            }
            
            // Save state to storage on mutation
            store.subscribe((mutation, state) => {
                try {
                    const saveState = {};
                    
                    // Filter state by paths if provided
                    if (mergedOptions.paths) {
                        mergedOptions.paths.forEach(path => {
                            const value = store.state(path);
                            if (value !== undefined) {
                                saveState[path] = value;
                            }
                        });
                    } else {
                        Object.keys(state).forEach(key => {
                            saveState[key] = state[key];
                        });
                    }
                    
                    mergedOptions.storage.setItem(mergedOptions.key, JSON.stringify(saveState));
                } catch (error) {
                    console.error('[Switch Store] Error saving state to storage:', error);
                }
            });
        };
    }
    
    // Export the store
    global.SwitchStore = {
        createStore,
        createLogger,
        createPersistence
    };
    
})(typeof window !== 'undefined' ? window : this);
