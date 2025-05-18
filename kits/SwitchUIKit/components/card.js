/**
 * Switch UI Kit - Card Component
 * 
 * A card component with header, body, and footer for the Switch UI Kit.
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
     * Card Component
     */
    class Card {
        /**
         * Create a new Card
         * @param {Object} options - Card options
         * @returns {Card} - The card instance
         */
        constructor(options = {}) {
            // Default options
            this.options = Object.assign({
                title: '',
                content: '',
                footer: '',
                image: null,
                imagePosition: 'top',
                shadow: true,
                border: true,
                rounded: true,
                attributes: {}
            }, options);
            
            // Create the element
            this.element = this._createElement();
            
            return this;
        }
        
        /**
         * Create the card element
         * @returns {HTMLElement} - The card element
         * @private
         */
        _createElement() {
            // Create the card element
            const card = document.createElement('div');
            
            // Add classes
            card.classList.add('switch-card');
            
            // Add shadow class
            if (this.options.shadow) {
                card.classList.add('switch-card-shadow');
            }
            
            // Add border class
            if (this.options.border) {
                card.classList.add('switch-card-border');
            }
            
            // Add rounded class
            if (this.options.rounded) {
                card.classList.add('switch-card-rounded');
            }
            
            // Add custom attributes
            if (this.options.attributes) {
                for (const [key, value] of Object.entries(this.options.attributes)) {
                    card.setAttribute(key, value);
                }
            }
            
            // Add image if provided
            if (this.options.image) {
                const img = document.createElement('img');
                img.src = this.options.image;
                img.alt = this.options.title || 'Card image';
                
                if (this.options.imagePosition === 'top') {
                    img.classList.add('switch-card-img-top');
                    card.appendChild(img);
                } else if (this.options.imagePosition === 'bottom') {
                    img.classList.add('switch-card-img-bottom');
                    // Will be appended after the content
                }
            }
            
            // Add header if title is provided
            if (this.options.title) {
                const header = document.createElement('div');
                header.classList.add('switch-card-header');
                
                const title = document.createElement('h3');
                title.classList.add('switch-card-title');
                title.textContent = this.options.title;
                
                header.appendChild(title);
                card.appendChild(header);
            }
            
            // Add body if content is provided
            if (this.options.content) {
                const body = document.createElement('div');
                body.classList.add('switch-card-body');
                
                // Check if content is HTML or plain text
                if (this.options.content.trim().startsWith('<')) {
                    body.innerHTML = this.options.content;
                } else {
                    const paragraph = document.createElement('p');
                    paragraph.classList.add('switch-card-text');
                    paragraph.textContent = this.options.content;
                    body.appendChild(paragraph);
                }
                
                card.appendChild(body);
            }
            
            // Add image at the bottom if specified
            if (this.options.image && this.options.imagePosition === 'bottom') {
                const img = document.createElement('img');
                img.src = this.options.image;
                img.alt = this.options.title || 'Card image';
                img.classList.add('switch-card-img-bottom');
                card.appendChild(img);
            }
            
            // Add footer if provided
            if (this.options.footer) {
                const footer = document.createElement('div');
                footer.classList.add('switch-card-footer');
                
                // Check if footer is HTML or plain text
                if (this.options.footer.trim().startsWith('<')) {
                    footer.innerHTML = this.options.footer;
                } else {
                    footer.textContent = this.options.footer;
                }
                
                card.appendChild(footer);
            }
            
            return card;
        }
        
        /**
         * Render the card
         * @returns {string} - The card HTML
         */
        render() {
            return this.element.outerHTML;
        }
        
        /**
         * Get the card element
         * @returns {HTMLElement} - The card element
         */
        getElement() {
            return this.element;
        }
        
        /**
         * Set the card title
         * @param {string} title - The card title
         * @returns {Card} - The card instance
         */
        setTitle(title) {
            this.options.title = title;
            
            // Find the title element
            const titleElement = this.element.querySelector('.switch-card-title');
            
            if (titleElement) {
                // Update the existing title
                titleElement.textContent = title;
            } else if (title) {
                // Create a new header and title
                const header = document.createElement('div');
                header.classList.add('switch-card-header');
                
                const titleEl = document.createElement('h3');
                titleEl.classList.add('switch-card-title');
                titleEl.textContent = title;
                
                header.appendChild(titleEl);
                
                // Insert at the beginning or after the image
                const img = this.element.querySelector('.switch-card-img-top');
                if (img) {
                    img.insertAdjacentElement('afterend', header);
                } else {
                    this.element.insertAdjacentElement('afterbegin', header);
                }
            }
            
            return this;
        }
        
        /**
         * Set the card content
         * @param {string} content - The card content
         * @returns {Card} - The card instance
         */
        setContent(content) {
            this.options.content = content;
            
            // Find the body element
            let bodyElement = this.element.querySelector('.switch-card-body');
            
            if (bodyElement) {
                // Update the existing body
                if (content.trim().startsWith('<')) {
                    bodyElement.innerHTML = content;
                } else {
                    let textElement = bodyElement.querySelector('.switch-card-text');
                    if (textElement) {
                        textElement.textContent = content;
                    } else {
                        const paragraph = document.createElement('p');
                        paragraph.classList.add('switch-card-text');
                        paragraph.textContent = content;
                        bodyElement.innerHTML = '';
                        bodyElement.appendChild(paragraph);
                    }
                }
            } else if (content) {
                // Create a new body
                const body = document.createElement('div');
                body.classList.add('switch-card-body');
                
                if (content.trim().startsWith('<')) {
                    body.innerHTML = content;
                } else {
                    const paragraph = document.createElement('p');
                    paragraph.classList.add('switch-card-text');
                    paragraph.textContent = content;
                    body.appendChild(paragraph);
                }
                
                // Insert after the header or at the beginning
                const header = this.element.querySelector('.switch-card-header');
                if (header) {
                    header.insertAdjacentElement('afterend', body);
                } else {
                    const img = this.element.querySelector('.switch-card-img-top');
                    if (img) {
                        img.insertAdjacentElement('afterend', body);
                    } else {
                        this.element.insertAdjacentElement('afterbegin', body);
                    }
                }
            }
            
            return this;
        }
    }
    
    // Factory function to create a new Card
    function createCard(options) {
        return new Card(options);
    }
    
    // Export the Card component
    global.SwitchUIKit.Components.Card = Card;
    global.SwitchUIKit.Components.createCard = createCard;
    
    // Export to SwitchComponents for easier access
    global.SwitchComponents.Card = Card;
    global.SwitchComponents.Card.create = createCard;
    
})(typeof window !== 'undefined' ? window : this);
