/**
 * Switch UI Kit - Slider Component
 * 
 * A customizable slider component for the Switch UI Kit.
 */

(function(global) {
    'use strict';
    
    // Create the SwitchUIKit namespace if it doesn't exist
    global.SwitchUIKit = global.SwitchUIKit || {};
    
    // Create the Components namespace if it doesn't exist
    global.SwitchUIKit.Components = global.SwitchUIKit.Components || {};
    
    // Create the SwitchComponents namespace for easier access
    global.SwitchComponents = global.SwitchComponents || {};
    
    /**
     * Slider Component
     */
    class Slider {
        /**
         * Create a new Slider
         * @param {Object} options - Slider options
         * @returns {Slider} - The Slider instance
         */
        constructor(options = {}) {
            // Default options
            this.options = Object.assign({
                min: 0,
                max: 100,
                value: 50,
                step: 1,
                disabled: false,
                showValue: true,
                showLabels: true,
                showTicks: false,
                tickInterval: 10,
                vertical: false,
                height: '200px', // Only used when vertical is true
                onChange: null,
                onInput: null,
                attributes: {}
            }, options);
            
            // Validate options
            this._validateOptions();
            
            // Create the element
            this.element = this._createElement();
            
            // Attach event listeners
            this._attachEventListeners();
            
            return this;
        }
        
        /**
         * Validate options
         * @private
         */
        _validateOptions() {
            // Ensure min is less than max
            if (this.options.min >= this.options.max) {
                console.warn('Slider: min must be less than max. Setting min to 0 and max to 100.');
                this.options.min = 0;
                this.options.max = 100;
            }
            
            // Ensure value is within range
            if (this.options.value < this.options.min) {
                this.options.value = this.options.min;
            } else if (this.options.value > this.options.max) {
                this.options.value = this.options.max;
            }
            
            // Ensure step is positive
            if (this.options.step <= 0) {
                console.warn('Slider: step must be positive. Setting step to 1.');
                this.options.step = 1;
            }
            
            // Ensure tickInterval is positive
            if (this.options.tickInterval <= 0) {
                console.warn('Slider: tickInterval must be positive. Setting tickInterval to 10.');
                this.options.tickInterval = 10;
            }
        }
        
        /**
         * Create the slider element
         * @returns {HTMLElement} - The slider element
         * @private
         */
        _createElement() {
            // Create the container
            const container = document.createElement('div');
            container.classList.add('switch-slider-container');
            
            if (this.options.vertical) {
                container.classList.add('switch-slider-vertical');
                container.style.height = this.options.height;
            }
            
            // Create the slider wrapper
            const wrapper = document.createElement('div');
            wrapper.classList.add('switch-slider-wrapper');
            
            // Create the slider
            const slider = document.createElement('input');
            slider.type = 'range';
            slider.classList.add('switch-slider');
            slider.min = this.options.min;
            slider.max = this.options.max;
            slider.value = this.options.value;
            slider.step = this.options.step;
            slider.disabled = this.options.disabled;
            
            // Add custom attributes
            if (this.options.attributes) {
                for (const [key, value] of Object.entries(this.options.attributes)) {
                    slider.setAttribute(key, value);
                }
            }
            
            // Create the track
            const track = document.createElement('div');
            track.classList.add('switch-slider-track');
            
            // Create the fill
            const fill = document.createElement('div');
            fill.classList.add('switch-slider-fill');
            
            // Set the initial fill width/height
            const percent = ((this.options.value - this.options.min) / (this.options.max - this.options.min)) * 100;
            if (this.options.vertical) {
                fill.style.height = `${percent}%`;
            } else {
                fill.style.width = `${percent}%`;
            }
            
            // Create the thumb
            const thumb = document.createElement('div');
            thumb.classList.add('switch-slider-thumb');
            
            // Add elements to the wrapper
            track.appendChild(fill);
            wrapper.appendChild(track);
            wrapper.appendChild(slider);
            wrapper.appendChild(thumb);
            
            // Add wrapper to the container
            container.appendChild(wrapper);
            
            // Add labels if enabled
            if (this.options.showLabels) {
                const labels = document.createElement('div');
                labels.classList.add('switch-slider-labels');
                
                const minLabel = document.createElement('span');
                minLabel.classList.add('switch-slider-label', 'switch-slider-label-min');
                minLabel.textContent = this.options.min;
                
                const maxLabel = document.createElement('span');
                maxLabel.classList.add('switch-slider-label', 'switch-slider-label-max');
                maxLabel.textContent = this.options.max;
                
                labels.appendChild(minLabel);
                labels.appendChild(maxLabel);
                
                container.appendChild(labels);
            }
            
            // Add ticks if enabled
            if (this.options.showTicks) {
                const ticks = document.createElement('div');
                ticks.classList.add('switch-slider-ticks');
                
                const range = this.options.max - this.options.min;
                const tickCount = Math.floor(range / this.options.tickInterval) + 1;
                
                for (let i = 0; i < tickCount; i++) {
                    const tick = document.createElement('div');
                    tick.classList.add('switch-slider-tick');
                    
                    const tickValue = this.options.min + (i * this.options.tickInterval);
                    const tickPercent = ((tickValue - this.options.min) / range) * 100;
                    
                    if (this.options.vertical) {
                        tick.style.bottom = `${tickPercent}%`;
                    } else {
                        tick.style.left = `${tickPercent}%`;
                    }
                    
                    ticks.appendChild(tick);
                }
                
                container.appendChild(ticks);
            }
            
            // Add value display if enabled
            if (this.options.showValue) {
                const valueDisplay = document.createElement('div');
                valueDisplay.classList.add('switch-slider-value');
                valueDisplay.textContent = this.options.value;
                
                container.appendChild(valueDisplay);
                
                // Store reference to value display
                this.valueDisplay = valueDisplay;
            }
            
            // Store references
            this.container = container;
            this.slider = slider;
            this.fill = fill;
            this.thumb = thumb;
            
            return container;
        }
        
        /**
         * Attach event listeners
         * @private
         */
        _attachEventListeners() {
            // Update fill and value display on input
            this.slider.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value);
                const percent = ((value - this.options.min) / (this.options.max - this.options.min)) * 100;
                
                if (this.options.vertical) {
                    this.fill.style.height = `${percent}%`;
                } else {
                    this.fill.style.width = `${percent}%`;
                }
                
                if (this.options.showValue && this.valueDisplay) {
                    this.valueDisplay.textContent = value;
                }
                
                // Call the onInput callback
                if (this.options.onInput && typeof this.options.onInput === 'function') {
                    this.options.onInput(value);
                }
            });
            
            // Call onChange when the value changes
            this.slider.addEventListener('change', (e) => {
                const value = parseFloat(e.target.value);
                
                // Call the onChange callback
                if (this.options.onChange && typeof this.options.onChange === 'function') {
                    this.options.onChange(value);
                }
            });
        }
        
        /**
         * Render the slider
         * @returns {string} - The slider HTML
         */
        render() {
            return this.element.outerHTML;
        }
        
        /**
         * Get the slider element
         * @returns {HTMLElement} - The slider element
         */
        getElement() {
            return this.element;
        }
        
        /**
         * Get the current value
         * @returns {number} - The current value
         */
        getValue() {
            return parseFloat(this.slider.value);
        }
        
        /**
         * Set the value
         * @param {number} value - The new value
         * @returns {Slider} - The Slider instance
         */
        setValue(value) {
            // Ensure value is within range
            if (value < this.options.min) {
                value = this.options.min;
            } else if (value > this.options.max) {
                value = this.options.max;
            }
            
            // Update the slider value
            this.slider.value = value;
            
            // Update the fill
            const percent = ((value - this.options.min) / (this.options.max - this.options.min)) * 100;
            if (this.options.vertical) {
                this.fill.style.height = `${percent}%`;
            } else {
                this.fill.style.width = `${percent}%`;
            }
            
            // Update the value display
            if (this.options.showValue && this.valueDisplay) {
                this.valueDisplay.textContent = value;
            }
            
            return this;
        }
        
        /**
         * Enable the slider
         * @returns {Slider} - The Slider instance
         */
        enable() {
            this.slider.disabled = false;
            this.container.classList.remove('switch-slider-disabled');
            return this;
        }
        
        /**
         * Disable the slider
         * @returns {Slider} - The Slider instance
         */
        disable() {
            this.slider.disabled = true;
            this.container.classList.add('switch-slider-disabled');
            return this;
        }
    }
    
    // Factory function to create a new Slider
    function createSlider(options) {
        return new Slider(options);
    }
    
    // Export the Slider component
    global.SwitchUIKit.Components.Slider = Slider;
    global.SwitchUIKit.Components.createSlider = createSlider;
    
    // Export to SwitchComponents for easier access
    global.SwitchComponents.Slider = Slider;
    global.SwitchComponents.Slider.create = createSlider;
    
})(typeof window !== 'undefined' ? window : this);
