/**
 * Switch Store - State Management for the Switch Framework
 * 
 * This module provides a centralized store for managing application state.
 * It implements a Redux-like pattern with actions, reducers, and selectors.
 */

(function(global) {
    'use strict';

    // Check if Switch is available
    if (!global.Switch) {
        console.error('Switch framework not found. Make sure to include switch.js before store.js.');
        return;
    }

    /**
     * Store class for managing application state
     */
    class Store {
        /**
         * Create a new store
         * @param {Object} initialState - Initial state
         * @param {Object} reducers - Reducers object
         */
        constructor(initialState = {}, reducers = {}) {
            this.state = initialState;
            this.reducers = reducers;
            this.listeners = [];
            this.middlewares = [];
        }

        /**
         * Get the current state
         * @returns {Object} - Current state
         */
        getState() {
            return this.state;
        }

        /**
         * Dispatch an action
         * @param {Object} action - Action object
         * @returns {Object} - Action object
         */
        dispatch(action) {
            // Check if action is valid
            if (!action || typeof action !== 'object' || !action.type) {
                console.error('Invalid action:', action);
                return action;
            }

            // Apply middlewares
            let middlewareChain = this.middlewares.map(middleware => middleware(this));
            let enhancedDispatch = action => {
                // Apply reducers
                this.state = this.reduce(this.state, action);
                
                // Notify listeners
                this.notifyListeners();
                
                return action;
            };

            // Chain middlewares
            if (middlewareChain.length > 0) {
                enhancedDispatch = middlewareChain.reduce(
                    (composed, middleware) => middleware(composed),
                    enhancedDispatch
                );
            }

            // Dispatch the action
            return enhancedDispatch(action);
        }

        /**
         * Apply reducers to state
         * @param {Object} state - Current state
         * @param {Object} action - Action object
         * @returns {Object} - New state
         */
        reduce(state, action) {
            // Create a new state object
            const newState = {};

            // Apply each reducer
            for (const key in this.reducers) {
                if (Object.prototype.hasOwnProperty.call(this.reducers, key)) {
                    const reducer = this.reducers[key];
                    newState[key] = reducer(state[key], action);
                }
            }

            // Return the new state
            return newState;
        }

        /**
         * Subscribe to state changes
         * @param {Function} listener - Listener function
         * @returns {Function} - Unsubscribe function
         */
        subscribe(listener) {
            if (typeof listener !== 'function') {
                console.error('Listener must be a function');
                return () => {};
            }

            // Add the listener
            this.listeners.push(listener);

            // Return an unsubscribe function
            return () => {
                this.listeners = this.listeners.filter(l => l !== listener);
            };
        }

        /**
         * Notify all listeners of state changes
         */
        notifyListeners() {
            this.listeners.forEach(listener => {
                try {
                    listener(this.state);
                } catch (error) {
                    console.error('Error in store listener:', error);
                }
            });
        }

        /**
         * Apply middleware to the store
         * @param {...Function} middlewares - Middleware functions
         */
        applyMiddleware(...middlewares) {
            this.middlewares = middlewares;
        }
    }

    /**
     * Create a selector function
     * @param {Function} selector - Selector function
     * @returns {Function} - Memoized selector
     */
    function createSelector(selector) {
        let lastState = null;
        let lastResult = null;

        return function(state) {
            if (state === lastState) {
                return lastResult;
            }

            lastState = state;
            lastResult = selector(state);
            return lastResult;
        };
    }

    /**
     * Create an action creator
     * @param {string} type - Action type
     * @returns {Function} - Action creator function
     */
    function createAction(type) {
        return function(payload) {
            return {
                type,
                payload
            };
        };
    }

    /**
     * Create a reducer
     * @param {Object} initialState - Initial state
     * @param {Object} handlers - Action handlers
     * @returns {Function} - Reducer function
     */
    function createReducer(initialState, handlers) {
        return function(state = initialState, action) {
            if (handlers.hasOwnProperty(action.type)) {
                return handlers[action.type](state, action);
            }
            return state;
        };
    }

    /**
     * Combine reducers
     * @param {Object} reducers - Reducers object
     * @returns {Function} - Combined reducer
     */
    function combineReducers(reducers) {
        return function(state = {}, action) {
            const nextState = {};
            let hasChanged = false;

            for (const key in reducers) {
                if (Object.prototype.hasOwnProperty.call(reducers, key)) {
                    const reducer = reducers[key];
                    const previousStateForKey = state[key];
                    const nextStateForKey = reducer(previousStateForKey, action);
                    nextState[key] = nextStateForKey;
                    hasChanged = hasChanged || nextStateForKey !== previousStateForKey;
                }
            }

            return hasChanged ? nextState : state;
        };
    }

    /**
     * Create a store
     * @param {Object} initialState - Initial state
     * @param {Object} reducers - Reducers object
     * @returns {Store} - Store instance
     */
    function createStore(initialState = {}, reducers = {}) {
        return new Store(initialState, reducers);
    }

    // Export the store API
    global.Switch.Store = {
        createStore,
        createSelector,
        createAction,
        createReducer,
        combineReducers
    };

})(typeof window !== 'undefined' ? window : this);
