/**
 * Switch UI Kit - Carousel Component
 * 
 * A customizable carousel component for the Switch UI Kit.
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
     * Carousel Component
     */
    class Carousel {
        /**
         * Create a new Carousel
         * @param {Object} options - Carousel options
         * @returns {Carousel} - The Carousel instance
         */
        constructor(options = {}) {
            // Default options
            this.options = Object.assign({
                items: [],
                autoplay: false,
                autoplayInterval: 5000,
                showControls: true,
                showIndicators: true,
                showCaptions: true,
                infinite: true,
                animation: 'slide', // 'slide' or 'fade'
                animationDuration: 500,
                responsive: true,
                aspectRatio: '16:9',
                onChange: null,
                attributes: {}
            }, options);
            
            // State
            this.currentIndex = 0;
            this.autoplayTimer = null;
            this.isAnimating = false;
            
            // Create the element
            this.element = this._createElement();
            
            // Start autoplay if enabled
            if (this.options.autoplay) {
                this.startAutoplay();
            }
            
            return this;
        }
        
        /**
         * Create the carousel element
         * @returns {HTMLElement} - The carousel element
         * @private
         */
        _createElement() {
            // Create the container
            const container = document.createElement('div');
            container.classList.add('switch-carousel');
            
            // Add animation class
            container.classList.add(`switch-carousel-${this.options.animation}`);
            
            // Add responsive class if enabled
            if (this.options.responsive) {
                container.classList.add('switch-carousel-responsive');
                
                // Set aspect ratio
                if (this.options.aspectRatio) {
                    const [width, height] = this.options.aspectRatio.split(':');
                    const paddingBottom = (height / width) * 100;
                    container.style.setProperty('--switch-carousel-aspect-ratio', `${paddingBottom}%`);
                }
            }
            
            // Add custom attributes
            if (this.options.attributes) {
                for (const [key, value] of Object.entries(this.options.attributes)) {
                    container.setAttribute(key, value);
                }
            }
            
            // Create the track
            const track = document.createElement('div');
            track.classList.add('switch-carousel-track');
            
            // Create the slides
            this.options.items.forEach((item, index) => {
                const slide = document.createElement('div');
                slide.classList.add('switch-carousel-slide');
                
                // Set active class for the first slide
                if (index === 0) {
                    slide.classList.add('switch-carousel-slide-active');
                }
                
                // Create the content
                if (typeof item === 'string') {
                    // If item is a string, assume it's an image URL
                    const img = document.createElement('img');
                    img.src = item;
                    img.alt = `Slide ${index + 1}`;
                    img.classList.add('switch-carousel-image');
                    slide.appendChild(img);
                } else if (typeof item === 'object') {
                    // If item is an object, it can have image, caption, and content properties
                    if (item.image) {
                        const img = document.createElement('img');
                        img.src = item.image;
                        img.alt = item.alt || `Slide ${index + 1}`;
                        img.classList.add('switch-carousel-image');
                        slide.appendChild(img);
                    }
                    
                    if (item.content) {
                        const content = document.createElement('div');
                        content.classList.add('switch-carousel-content');
                        
                        if (typeof item.content === 'string') {
                            content.innerHTML = item.content;
                        } else if (item.content instanceof HTMLElement) {
                            content.appendChild(item.content);
                        }
                        
                        slide.appendChild(content);
                    }
                    
                    if (item.caption && this.options.showCaptions) {
                        const caption = document.createElement('div');
                        caption.classList.add('switch-carousel-caption');
                        caption.innerHTML = item.caption;
                        slide.appendChild(caption);
                    }
                }
                
                track.appendChild(slide);
            });
            
            // Add track to container
            container.appendChild(track);
            
            // Add controls if enabled
            if (this.options.showControls && this.options.items.length > 1) {
                // Create previous button
                const prevButton = document.createElement('button');
                prevButton.type = 'button';
                prevButton.classList.add('switch-carousel-control', 'switch-carousel-control-prev');
                prevButton.innerHTML = '&lsaquo;';
                prevButton.setAttribute('aria-label', 'Previous');
                prevButton.addEventListener('click', () => this.prev());
                
                // Create next button
                const nextButton = document.createElement('button');
                nextButton.type = 'button';
                nextButton.classList.add('switch-carousel-control', 'switch-carousel-control-next');
                nextButton.innerHTML = '&rsaquo;';
                nextButton.setAttribute('aria-label', 'Next');
                nextButton.addEventListener('click', () => this.next());
                
                // Add controls to container
                container.appendChild(prevButton);
                container.appendChild(nextButton);
            }
            
            // Add indicators if enabled
            if (this.options.showIndicators && this.options.items.length > 1) {
                const indicators = document.createElement('div');
                indicators.classList.add('switch-carousel-indicators');
                
                this.options.items.forEach((_, index) => {
                    const indicator = document.createElement('button');
                    indicator.type = 'button';
                    indicator.classList.add('switch-carousel-indicator');
                    
                    if (index === 0) {
                        indicator.classList.add('switch-carousel-indicator-active');
                    }
                    
                    indicator.setAttribute('aria-label', `Slide ${index + 1}`);
                    indicator.addEventListener('click', () => this.goTo(index));
                    
                    indicators.appendChild(indicator);
                });
                
                container.appendChild(indicators);
            }
            
            // Store references
            this.container = container;
            this.track = track;
            this.slides = Array.from(track.querySelectorAll('.switch-carousel-slide'));
            this.indicators = this.options.showIndicators ? Array.from(container.querySelectorAll('.switch-carousel-indicator')) : [];
            
            return container;
        }
        
        /**
         * Go to a specific slide
         * @param {number} index - The index of the slide to go to
         * @returns {Carousel} - The Carousel instance
         */
        goTo(index) {
            // Don't do anything if already at this index or animating
            if (index === this.currentIndex || this.isAnimating) {
                return this;
            }
            
            // Check if index is valid
            if (index < 0 || index >= this.slides.length) {
                // If infinite is enabled, wrap around
                if (this.options.infinite) {
                    if (index < 0) {
                        index = this.slides.length - 1;
                    } else {
                        index = 0;
                    }
                } else {
                    return this;
                }
            }
            
            // Set animating flag
            this.isAnimating = true;
            
            // Get the current and next slides
            const currentSlide = this.slides[this.currentIndex];
            const nextSlide = this.slides[index];
            
            // Determine the direction (for slide animation)
            const direction = index > this.currentIndex ? 'next' : 'prev';
            
            // Add the appropriate classes
            nextSlide.classList.add(`switch-carousel-slide-${direction}`);
            
            // Force a reflow to ensure the class is applied
            void nextSlide.offsetWidth;
            
            // Add the active and moving classes
            currentSlide.classList.add(`switch-carousel-slide-${direction === 'next' ? 'prev' : 'next'}`);
            nextSlide.classList.add('switch-carousel-slide-active');
            
            // Update indicators
            if (this.indicators.length > 0) {
                this.indicators[this.currentIndex].classList.remove('switch-carousel-indicator-active');
                this.indicators[index].classList.add('switch-carousel-indicator-active');
            }
            
            // Wait for the animation to complete
            setTimeout(() => {
                // Remove the direction classes
                currentSlide.classList.remove('switch-carousel-slide-active', 'switch-carousel-slide-prev', 'switch-carousel-slide-next');
                nextSlide.classList.remove('switch-carousel-slide-prev', 'switch-carousel-slide-next');
                
                // Update the current index
                this.currentIndex = index;
                
                // Reset the animating flag
                this.isAnimating = false;
                
                // Call the onChange callback
                if (this.options.onChange && typeof this.options.onChange === 'function') {
                    this.options.onChange(index);
                }
            }, this.options.animationDuration);
            
            return this;
        }
        
        /**
         * Go to the next slide
         * @returns {Carousel} - The Carousel instance
         */
        next() {
            return this.goTo(this.currentIndex + 1);
        }
        
        /**
         * Go to the previous slide
         * @returns {Carousel} - The Carousel instance
         */
        prev() {
            return this.goTo(this.currentIndex - 1);
        }
        
        /**
         * Start autoplay
         * @returns {Carousel} - The Carousel instance
         */
        startAutoplay() {
            if (this.options.autoplay && this.slides.length > 1) {
                this.stopAutoplay(); // Clear any existing timer
                
                this.autoplayTimer = setInterval(() => {
                    this.next();
                }, this.options.autoplayInterval);
            }
            
            return this;
        }
        
        /**
         * Stop autoplay
         * @returns {Carousel} - The Carousel instance
         */
        stopAutoplay() {
            if (this.autoplayTimer) {
                clearInterval(this.autoplayTimer);
                this.autoplayTimer = null;
            }
            
            return this;
        }
        
        /**
         * Render the carousel
         * @returns {string} - The carousel HTML
         */
        render() {
            return this.element.outerHTML;
        }
        
        /**
         * Get the carousel element
         * @returns {HTMLElement} - The carousel element
         */
        getElement() {
            return this.element;
        }
        
        /**
         * Get the current slide index
         * @returns {number} - The current slide index
         */
        getCurrentIndex() {
            return this.currentIndex;
        }
        
        /**
         * Add a new slide
         * @param {string|Object} item - The slide item
         * @param {number} [index] - The index to insert at (defaults to end)
         * @returns {Carousel} - The Carousel instance
         */
        addSlide(item, index = this.slides.length) {
            // Add the item to the options
            this.options.items.splice(index, 0, item);
            
            // Create the slide
            const slide = document.createElement('div');
            slide.classList.add('switch-carousel-slide');
            
            // Create the content
            if (typeof item === 'string') {
                // If item is a string, assume it's an image URL
                const img = document.createElement('img');
                img.src = item;
                img.alt = `Slide ${index + 1}`;
                img.classList.add('switch-carousel-image');
                slide.appendChild(img);
            } else if (typeof item === 'object') {
                // If item is an object, it can have image, caption, and content properties
                if (item.image) {
                    const img = document.createElement('img');
                    img.src = item.image;
                    img.alt = item.alt || `Slide ${index + 1}`;
                    img.classList.add('switch-carousel-image');
                    slide.appendChild(img);
                }
                
                if (item.content) {
                    const content = document.createElement('div');
                    content.classList.add('switch-carousel-content');
                    
                    if (typeof item.content === 'string') {
                        content.innerHTML = item.content;
                    } else if (item.content instanceof HTMLElement) {
                        content.appendChild(item.content);
                    }
                    
                    slide.appendChild(content);
                }
                
                if (item.caption && this.options.showCaptions) {
                    const caption = document.createElement('div');
                    caption.classList.add('switch-carousel-caption');
                    caption.innerHTML = item.caption;
                    slide.appendChild(caption);
                }
            }
            
            // Insert the slide at the specified index
            if (index < this.slides.length) {
                this.track.insertBefore(slide, this.slides[index]);
            } else {
                this.track.appendChild(slide);
            }
            
            // Update the slides array
            this.slides = Array.from(this.track.querySelectorAll('.switch-carousel-slide'));
            
            // Add an indicator if needed
            if (this.options.showIndicators) {
                const indicator = document.createElement('button');
                indicator.type = 'button';
                indicator.classList.add('switch-carousel-indicator');
                indicator.setAttribute('aria-label', `Slide ${this.slides.length}`);
                indicator.addEventListener('click', () => this.goTo(this.slides.length - 1));
                
                const indicators = this.container.querySelector('.switch-carousel-indicators');
                indicators.appendChild(indicator);
                
                // Update the indicators array
                this.indicators = Array.from(this.container.querySelectorAll('.switch-carousel-indicator'));
            }
            
            return this;
        }
        
        /**
         * Remove a slide
         * @param {number} index - The index of the slide to remove
         * @returns {Carousel} - The Carousel instance
         */
        removeSlide(index) {
            // Check if index is valid
            if (index < 0 || index >= this.slides.length) {
                return this;
            }
            
            // Remove the item from the options
            this.options.items.splice(index, 1);
            
            // Remove the slide
            this.track.removeChild(this.slides[index]);
            
            // Update the slides array
            this.slides = Array.from(this.track.querySelectorAll('.switch-carousel-slide'));
            
            // Remove the indicator if needed
            if (this.options.showIndicators && this.indicators.length > 0) {
                const indicators = this.container.querySelector('.switch-carousel-indicators');
                indicators.removeChild(this.indicators[index]);
                
                // Update the indicators array
                this.indicators = Array.from(this.container.querySelectorAll('.switch-carousel-indicator'));
            }
            
            // Adjust the current index if needed
            if (index <= this.currentIndex) {
                this.currentIndex = Math.max(0, this.currentIndex - 1);
                
                // Update the active slide and indicator
                if (this.slides.length > 0) {
                    this.slides.forEach(slide => slide.classList.remove('switch-carousel-slide-active'));
                    this.slides[this.currentIndex].classList.add('switch-carousel-slide-active');
                    
                    if (this.indicators.length > 0) {
                        this.indicators.forEach(indicator => indicator.classList.remove('switch-carousel-indicator-active'));
                        this.indicators[this.currentIndex].classList.add('switch-carousel-indicator-active');
                    }
                }
            }
            
            return this;
        }
    }
    
    // Factory function to create a new Carousel
    function createCarousel(options) {
        return new Carousel(options);
    }
    
    // Export the Carousel component
    global.SwitchUIKit.Components.Carousel = Carousel;
    global.SwitchUIKit.Components.createCarousel = createCarousel;
    
    // Export to SwitchComponents for easier access
    global.SwitchComponents.Carousel = Carousel;
    global.SwitchComponents.Carousel.create = createCarousel;
    
})(typeof window !== 'undefined' ? window : this);
