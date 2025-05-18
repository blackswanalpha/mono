// Scrolling functionality for Mono Editor

/**
 * Scrolling Manager class for handling scrolling in the editor
 */
class ScrollingManager {
  constructor() {
    this.scrollableElements = new Map();
    this.scrollListeners = new Map();
    this.scrollPositions = new Map();
    this.resizeObserver = null;
    
    // Initialize the scrolling manager when the DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initialize());
    } else {
      this.initialize();
    }
  }
  
  /**
   * Initialize the scrolling manager
   */
  initialize() {
    console.log('Initializing Scrolling Manager...');
    
    // Create resize observer
    this.createResizeObserver();
    
    // Register scrollable elements
    this.registerScrollableElements();
    
    // Add event listeners
    this.addEventListeners();
    
    console.log('Scrolling Manager initialized');
  }
  
  /**
   * Create a resize observer to handle element resizing
   */
  createResizeObserver() {
    if (typeof ResizeObserver === 'undefined') {
      console.warn('ResizeObserver not supported in this browser');
      return;
    }
    
    this.resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        const element = entry.target;
        const id = element.id || element.dataset.scrollId;
        
        if (id && this.scrollableElements.has(id)) {
          this.updateScrollbars(id);
        }
      }
    });
  }
  
  /**
   * Register scrollable elements in the editor
   */
  registerScrollableElements() {
    // Register editor container
    this.registerScrollableElement('editor-container', document.querySelector('.editor-container'));
    
    // Register file explorer
    this.registerScrollableElement('file-explorer', document.getElementById('file-explorer'));
    
    // Register terminal
    this.registerScrollableElement('terminal-container', document.querySelector('.terminal-container'));
    
    // Register AI assistant chat history
    this.registerScrollableElement('ai-chat-history', document.querySelector('.ai-chat-history'));
    
    // Register settings panel
    this.registerScrollableElement('settings-content', document.querySelector('.settings-content'));
    
    // Register any Monaco editor instances
    document.addEventListener('monaco-editor-loaded', (e) => {
      if (e.detail && e.detail.editor && e.detail.id) {
        this.registerMonacoEditor(e.detail.id, e.detail.editor);
      }
    });
  }
  
  /**
   * Register a scrollable element
   * @param {string} id - The element ID
   * @param {HTMLElement} element - The scrollable element
   */
  registerScrollableElement(id, element) {
    if (!element) {
      console.warn(`Element not found for ID: ${id}`);
      return;
    }
    
    console.log(`Registering scrollable element: ${id}`);
    
    // Store the element
    this.scrollableElements.set(id, element);
    
    // Add data attribute for identification
    element.dataset.scrollId = id;
    
    // Add custom scrollbar if needed
    this.addCustomScrollbar(id, element);
    
    // Observe for resize events
    if (this.resizeObserver) {
      this.resizeObserver.observe(element);
    }
    
    // Store initial scroll position
    this.scrollPositions.set(id, {
      top: element.scrollTop,
      left: element.scrollLeft
    });
    
    // Add scroll event listener
    const scrollListener = () => {
      this.handleScroll(id, element);
    };
    
    element.addEventListener('scroll', scrollListener);
    this.scrollListeners.set(id, scrollListener);
  }
  
  /**
   * Register a Monaco editor instance
   * @param {string} id - The editor ID
   * @param {Object} editor - The Monaco editor instance
   */
  registerMonacoEditor(id, editor) {
    console.log(`Registering Monaco editor: ${id}`);
    
    // Store the editor
    this.scrollableElements.set(`monaco-${id}`, editor);
    
    // Add scroll listener
    editor.onDidScrollChange(e => {
      this.handleMonacoScroll(id, editor, e);
    });
  }
  
  /**
   * Add a custom scrollbar to an element
   * @param {string} id - The element ID
   * @param {HTMLElement} element - The scrollable element
   */
  addCustomScrollbar(id, element) {
    // Add custom scrollbar class
    element.classList.add('custom-scrollbar');
    
    // Create vertical scrollbar
    const verticalScrollbar = document.createElement('div');
    verticalScrollbar.className = 'scrollbar-vertical';
    verticalScrollbar.innerHTML = '<div class="scrollbar-thumb"></div>';
    
    // Create horizontal scrollbar
    const horizontalScrollbar = document.createElement('div');
    horizontalScrollbar.className = 'scrollbar-horizontal';
    horizontalScrollbar.innerHTML = '<div class="scrollbar-thumb"></div>';
    
    // Add scrollbars to element
    element.appendChild(verticalScrollbar);
    element.appendChild(horizontalScrollbar);
    
    // Add event listeners for dragging scrollbars
    this.addScrollbarDragListeners(id, element, verticalScrollbar, horizontalScrollbar);
    
    // Update scrollbars
    this.updateScrollbars(id);
  }
  
  /**
   * Add event listeners for dragging scrollbars
   * @param {string} id - The element ID
   * @param {HTMLElement} element - The scrollable element
   * @param {HTMLElement} verticalScrollbar - The vertical scrollbar
   * @param {HTMLElement} horizontalScrollbar - The horizontal scrollbar
   */
  addScrollbarDragListeners(id, element, verticalScrollbar, horizontalScrollbar) {
    const verticalThumb = verticalScrollbar.querySelector('.scrollbar-thumb');
    const horizontalThumb = horizontalScrollbar.querySelector('.scrollbar-thumb');
    
    // Vertical scrollbar drag
    let isDraggingVertical = false;
    let startY = 0;
    let startScrollTop = 0;
    
    verticalThumb.addEventListener('mousedown', (e) => {
      isDraggingVertical = true;
      startY = e.clientY;
      startScrollTop = element.scrollTop;
      document.body.classList.add('no-select');
      e.preventDefault();
    });
    
    // Horizontal scrollbar drag
    let isDraggingHorizontal = false;
    let startX = 0;
    let startScrollLeft = 0;
    
    horizontalThumb.addEventListener('mousedown', (e) => {
      isDraggingHorizontal = true;
      startX = e.clientX;
      startScrollLeft = element.scrollLeft;
      document.body.classList.add('no-select');
      e.preventDefault();
    });
    
    // Mouse move and up events
    document.addEventListener('mousemove', (e) => {
      if (isDraggingVertical) {
        const deltaY = e.clientY - startY;
        const scrollRatio = deltaY / (verticalScrollbar.clientHeight - verticalThumb.clientHeight);
        const scrollDelta = scrollRatio * (element.scrollHeight - element.clientHeight);
        element.scrollTop = startScrollTop + scrollDelta;
      }
      
      if (isDraggingHorizontal) {
        const deltaX = e.clientX - startX;
        const scrollRatio = deltaX / (horizontalScrollbar.clientWidth - horizontalThumb.clientWidth);
        const scrollDelta = scrollRatio * (element.scrollWidth - element.clientWidth);
        element.scrollLeft = startScrollLeft + scrollDelta;
      }
    });
    
    document.addEventListener('mouseup', () => {
      isDraggingVertical = false;
      isDraggingHorizontal = false;
      document.body.classList.remove('no-select');
    });
  }
  
  /**
   * Update scrollbars for an element
   * @param {string} id - The element ID
   */
  updateScrollbars(id) {
    const element = this.scrollableElements.get(id);
    if (!element || !element.classList) return;
    
    const verticalScrollbar = element.querySelector('.scrollbar-vertical');
    const horizontalScrollbar = element.querySelector('.scrollbar-horizontal');
    
    if (!verticalScrollbar || !horizontalScrollbar) return;
    
    const verticalThumb = verticalScrollbar.querySelector('.scrollbar-thumb');
    const horizontalThumb = horizontalScrollbar.querySelector('.scrollbar-thumb');
    
    if (!verticalThumb || !horizontalThumb) return;
    
    // Calculate vertical scrollbar
    const verticalRatio = element.clientHeight / element.scrollHeight;
    const verticalThumbHeight = Math.max(30, verticalRatio * verticalScrollbar.clientHeight);
    const verticalScrollRatio = element.scrollTop / (element.scrollHeight - element.clientHeight);
    const verticalThumbTop = verticalScrollRatio * (verticalScrollbar.clientHeight - verticalThumbHeight);
    
    // Calculate horizontal scrollbar
    const horizontalRatio = element.clientWidth / element.scrollWidth;
    const horizontalThumbWidth = Math.max(30, horizontalRatio * horizontalScrollbar.clientWidth);
    const horizontalScrollRatio = element.scrollLeft / (element.scrollWidth - element.clientWidth);
    const horizontalThumbLeft = horizontalScrollRatio * (horizontalScrollbar.clientWidth - horizontalThumbWidth);
    
    // Update vertical scrollbar
    verticalThumb.style.height = `${verticalThumbHeight}px`;
    verticalThumb.style.top = `${verticalThumbTop}px`;
    
    // Update horizontal scrollbar
    horizontalThumb.style.width = `${horizontalThumbWidth}px`;
    horizontalThumb.style.left = `${horizontalThumbLeft}px`;
    
    // Show/hide scrollbars based on content size
    if (element.scrollHeight <= element.clientHeight) {
      verticalScrollbar.classList.add('hidden');
    } else {
      verticalScrollbar.classList.remove('hidden');
    }
    
    if (element.scrollWidth <= element.clientWidth) {
      horizontalScrollbar.classList.add('hidden');
    } else {
      horizontalScrollbar.classList.remove('hidden');
    }
  }
  
  /**
   * Handle scroll events for an element
   * @param {string} id - The element ID
   * @param {HTMLElement} element - The scrollable element
   */
  handleScroll(id, element) {
    // Update scrollbars
    this.updateScrollbars(id);
    
    // Store scroll position
    this.scrollPositions.set(id, {
      top: element.scrollTop,
      left: element.scrollLeft
    });
  }
  
  /**
   * Handle scroll events for a Monaco editor
   * @param {string} id - The editor ID
   * @param {Object} editor - The Monaco editor instance
   * @param {Object} e - The scroll event
   */
  handleMonacoScroll(id, editor, e) {
    // Store scroll position
    this.scrollPositions.set(`monaco-${id}`, {
      top: e.scrollTop,
      left: e.scrollLeft
    });
  }
  
  /**
   * Add event listeners for scrolling
   */
  addEventListeners() {
    // Listen for mouse wheel events on Monaco editors
    document.addEventListener('wheel', (e) => {
      // Check if the target is inside a Monaco editor
      const editorElement = e.target.closest('.monaco-editor');
      if (editorElement) {
        // Find the editor instance
        const editorId = editorElement.dataset.editorId;
        if (editorId) {
          // Prevent default if Ctrl key is pressed (zoom)
          if (e.ctrlKey) {
            e.preventDefault();
          }
        }
      }
    }, { passive: false });
    
    // Listen for window resize events
    window.addEventListener('resize', () => {
      // Update all scrollbars
      for (const id of this.scrollableElements.keys()) {
        this.updateScrollbars(id);
      }
    });
  }
  
  /**
   * Scroll an element to a specific position
   * @param {string} id - The element ID
   * @param {number} top - The vertical scroll position
   * @param {number} left - The horizontal scroll position
   */
  scrollTo(id, top, left) {
    const element = this.scrollableElements.get(id);
    if (!element) return;
    
    // Check if it's a Monaco editor
    if (id.startsWith('monaco-')) {
      // Monaco editor
      element.setScrollPosition({
        scrollTop: top,
        scrollLeft: left
      });
    } else if (element.scrollTo) {
      // Standard element with scrollTo method
      element.scrollTo({
        top,
        left,
        behavior: 'smooth'
      });
    } else {
      // Fallback
      element.scrollTop = top;
      element.scrollLeft = left;
    }
  }
  
  /**
   * Scroll an element to a specific element
   * @param {string} id - The element ID
   * @param {HTMLElement} targetElement - The element to scroll to
   */
  scrollToElement(id, targetElement) {
    const element = this.scrollableElements.get(id);
    if (!element || !targetElement) return;
    
    // Calculate the position of the target element relative to the scrollable element
    const elementRect = element.getBoundingClientRect();
    const targetRect = targetElement.getBoundingClientRect();
    
    const top = targetRect.top - elementRect.top + element.scrollTop;
    const left = targetRect.left - elementRect.left + element.scrollLeft;
    
    // Scroll to the target element
    this.scrollTo(id, top, left);
  }
  
  /**
   * Get the scroll position of an element
   * @param {string} id - The element ID
   * @returns {Object} The scroll position
   */
  getScrollPosition(id) {
    return this.scrollPositions.get(id) || { top: 0, left: 0 };
  }
  
  /**
   * Restore the scroll position of an element
   * @param {string} id - The element ID
   */
  restoreScrollPosition(id) {
    const position = this.scrollPositions.get(id);
    if (position) {
      this.scrollTo(id, position.top, position.left);
    }
  }
}

// Create and export a singleton instance
const scrollingManager = new ScrollingManager();

// Export the scrolling manager
window.scrollingManager = scrollingManager;
