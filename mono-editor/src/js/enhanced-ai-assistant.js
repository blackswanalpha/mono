// Enhanced AI Assistant for Mono Editor

/**
 * Enhanced AI Assistant class for providing context-aware suggestions and code generation
 */
class EnhancedAIAssistant {
  constructor() {
    this.assistantElement = null;
    this.chatHistoryElement = null;
    this.inputElement = null;
    this.isVisible = false;
    this.isProcessing = false;
    this.chatHistory = [];
    this.contextData = {
      currentFile: null,
      currentCode: null,
      selectedCode: null,
      cursorPosition: null,
      projectStructure: null,
      recentFiles: []
    };
    
    // Initialize the assistant when the DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initialize());
    } else {
      this.initialize();
    }
  }
  
  /**
   * Initialize the AI assistant
   */
  initialize() {
    console.log('Initializing Enhanced AI Assistant...');
    
    // Create assistant UI if it doesn't exist
    this.createAssistantUI();
    
    // Add event listeners
    this.addEventListeners();
    
    // Load chat history from local storage
    this.loadChatHistory();
    
    console.log('Enhanced AI Assistant initialized');
  }
  
  /**
   * Create the assistant UI
   */
  createAssistantUI() {
    // Check if assistant already exists
    const existingAssistant = document.getElementById('ai-assistant-panel');
    if (existingAssistant) {
      this.assistantElement = existingAssistant;
      this.chatHistoryElement = existingAssistant.querySelector('.ai-chat-history');
      this.inputElement = existingAssistant.querySelector('.ai-input-field');
      return;
    }
    
    // Create assistant container
    this.assistantElement = document.createElement('div');
    this.assistantElement.id = 'ai-assistant-panel';
    this.assistantElement.className = 'ai-assistant-panel';
    
    // Create assistant header
    const header = document.createElement('div');
    header.className = 'ai-assistant-header';
    header.innerHTML = `
      <h3>AI Assistant</h3>
      <div class="ai-assistant-controls">
        <button class="ai-assistant-clear" title="Clear chat history">Clear</button>
        <button class="ai-assistant-close" title="Close AI Assistant">×</button>
      </div>
    `;
    
    // Create chat history container
    this.chatHistoryElement = document.createElement('div');
    this.chatHistoryElement.className = 'ai-chat-history';
    
    // Create input container
    const inputContainer = document.createElement('div');
    inputContainer.className = 'ai-input-container';
    
    // Create input field
    this.inputElement = document.createElement('textarea');
    this.inputElement.className = 'ai-input-field';
    this.inputElement.placeholder = 'Ask me anything about Mono...';
    this.inputElement.rows = 2;
    
    // Create send button
    const sendButton = document.createElement('button');
    sendButton.className = 'ai-send-button';
    sendButton.innerHTML = '<span>Send</span>';
    
    // Create suggestion buttons
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'ai-suggestions';
    suggestionsContainer.innerHTML = `
      <button class="ai-suggestion-btn">Explain this code</button>
      <button class="ai-suggestion-btn">Fix this error</button>
      <button class="ai-suggestion-btn">Generate a component</button>
      <button class="ai-suggestion-btn">Optimize this code</button>
    `;
    
    // Assemble the input container
    inputContainer.appendChild(this.inputElement);
    inputContainer.appendChild(sendButton);
    
    // Assemble the assistant
    this.assistantElement.appendChild(header);
    this.assistantElement.appendChild(this.chatHistoryElement);
    this.assistantElement.appendChild(suggestionsContainer);
    this.assistantElement.appendChild(inputContainer);
    
    // Add to the document
    document.body.appendChild(this.assistantElement);
  }
  
  /**
   * Add event listeners to assistant elements
   */
  addEventListeners() {
    // Close button
    const closeButton = this.assistantElement.querySelector('.ai-assistant-close');
    if (closeButton) {
      closeButton.addEventListener('click', () => this.hide());
    }
    
    // Clear button
    const clearButton = this.assistantElement.querySelector('.ai-assistant-clear');
    if (clearButton) {
      clearButton.addEventListener('click', () => this.clearChatHistory());
    }
    
    // Send button
    const sendButton = this.assistantElement.querySelector('.ai-send-button');
    if (sendButton) {
      sendButton.addEventListener('click', () => this.sendMessage());
    }
    
    // Input field (send on Enter, but allow Shift+Enter for new line)
    if (this.inputElement) {
      this.inputElement.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
    }
    
    // Suggestion buttons
    const suggestionButtons = this.assistantElement.querySelectorAll('.ai-suggestion-btn');
    suggestionButtons.forEach(button => {
      button.addEventListener('click', () => {
        this.inputElement.value = button.textContent;
        this.sendMessage();
      });
    });
    
    // Listen for editor events
    document.addEventListener('editor-content-changed', (e) => {
      this.updateContext({
        currentCode: e.detail.content,
        currentFile: e.detail.filePath
      });
    });
    
    document.addEventListener('editor-selection-changed', (e) => {
      this.updateContext({
        selectedCode: e.detail.selectedText,
        cursorPosition: e.detail.position
      });
    });
    
    document.addEventListener('editor-file-opened', (e) => {
      this.updateContext({
        currentFile: e.detail.filePath,
        currentCode: e.detail.content
      });
      
      // Add to recent files
      this.addToRecentFiles(e.detail.filePath);
    });
  }
  
  /**
   * Show the assistant
   */
  show() {
    if (!this.assistantElement) {
      this.createAssistantUI();
    }
    
    this.assistantElement.classList.add('visible');
    this.isVisible = true;
    
    // Focus the input field
    setTimeout(() => {
      this.inputElement.focus();
    }, 100);
  }
  
  /**
   * Hide the assistant
   */
  hide() {
    if (this.assistantElement) {
      this.assistantElement.classList.remove('visible');
    }
    this.isVisible = false;
  }
  
  /**
   * Toggle the assistant visibility
   */
  toggle() {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show();
    }
  }
  
  /**
   * Send a message to the AI assistant
   */
  async sendMessage() {
    // Get the message from the input field
    const message = this.inputElement.value.trim();
    
    // Don't send empty messages
    if (!message || this.isProcessing) {
      return;
    }
    
    // Clear the input field
    this.inputElement.value = '';
    
    // Add the message to the chat history
    this.addMessageToChat('user', message);
    
    // Set processing state
    this.isProcessing = true;
    this.showTypingIndicator();
    
    try {
      // Generate a response
      const response = await this.generateResponse(message);
      
      // Remove typing indicator
      this.removeTypingIndicator();
      
      // Add the response to the chat history
      this.addMessageToChat('assistant', response);
    } catch (error) {
      console.error('Error generating response:', error);
      
      // Remove typing indicator
      this.removeTypingIndicator();
      
      // Add error message to chat
      this.addMessageToChat('assistant', 'Sorry, I encountered an error while processing your request. Please try again.');
    } finally {
      // Reset processing state
      this.isProcessing = false;
    }
  }
  
  /**
   * Generate a response to a user message
   * @param {string} message - The user message
   * @returns {Promise<string>} The AI response
   */
  async generateResponse(message) {
    // In a real implementation, this would call an AI API
    // For now, we'll use a simple rule-based system
    
    // Prepare context for the AI
    const context = this.prepareContext();
    
    // Log the message and context for debugging
    console.log('Generating response for:', message);
    console.log('Context:', context);
    
    // Simple rule-based responses
    if (message.toLowerCase().includes('explain this code')) {
      if (context.selectedCode) {
        return `Here's an explanation of the selected code:\n\n\`\`\`\n${context.selectedCode}\n\`\`\`\n\nThis code appears to be a ${this.detectLanguage(context.selectedCode)} snippet. It ${this.generateCodeExplanation(context.selectedCode)}`;
      } else if (context.currentCode) {
        return `I can see you're working with a ${this.detectLanguage(context.currentCode)} file. To get a more specific explanation, try selecting the part of the code you want me to explain.`;
      } else {
        return `I don't see any code to explain. Please open a file or select some code first.`;
      }
    } else if (message.toLowerCase().includes('fix this error')) {
      if (context.selectedCode) {
        return `Here's a potential fix for the selected code:\n\n\`\`\`\n${this.generateCodeFix(context.selectedCode)}\n\`\`\`\n\nThis addresses the issue by ${this.explainCodeFix(context.selectedCode)}`;
      } else {
        return `I don't see any code with errors to fix. Please select the code containing the error you want me to fix.`;
      }
    } else if (message.toLowerCase().includes('generate a component')) {
      return `Here's a sample Mono component:\n\n\`\`\`\ncomponent Button {\n  state {\n    text: string = "Click me";\n    clicked: boolean = false;\n  }\n\n  function handleClick() {\n    this.clicked = !this.clicked;\n  }\n\n  render {\n    <button onClick={this.handleClick}>\n      {this.clicked ? "Clicked!" : this.text}\n    </button>\n  }\n}\n\`\`\`\n\nYou can customize this component by changing the state properties and the render method.`;
    } else if (message.toLowerCase().includes('optimize this code')) {
      if (context.selectedCode) {
        return `Here's an optimized version of the selected code:\n\n\`\`\`\n${this.generateOptimizedCode(context.selectedCode)}\n\`\`\`\n\nThe optimization improves ${this.explainOptimization(context.selectedCode)}`;
      } else {
        return `I don't see any code to optimize. Please select the code you want me to optimize.`;
      }
    }
    
    // Default response
    return `I'm your AI assistant for Mono development. I can help you with code explanations, error fixing, component generation, and code optimization. What would you like to know about Mono?`;
  }
  
  /**
   * Add a message to the chat history
   * @param {string} role - The role of the message sender ('user' or 'assistant')
   * @param {string} content - The message content
   */
  addMessageToChat(role, content) {
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.className = `ai-message ${role}-message`;
    
    // Create avatar
    const avatar = document.createElement('div');
    avatar.className = 'ai-avatar';
    avatar.innerHTML = role === 'user' ? '<span>You</span>' : '<span>AI</span>';
    
    // Create content
    const messageContent = document.createElement('div');
    messageContent.className = 'ai-message-content';
    
    // Process content for markdown and code blocks
    const processedContent = this.processMessageContent(content);
    messageContent.innerHTML = processedContent;
    
    // Assemble message
    messageElement.appendChild(avatar);
    messageElement.appendChild(messageContent);
    
    // Add to chat history
    this.chatHistoryElement.appendChild(messageElement);
    
    // Scroll to bottom
    this.chatHistoryElement.scrollTop = this.chatHistoryElement.scrollHeight;
    
    // Add to chat history array
    this.chatHistory.push({
      role,
      content,
      timestamp: new Date().toISOString()
    });
    
    // Save chat history to local storage
    this.saveChatHistory();
  }
  
  /**
   * Process message content for markdown and code blocks
   * @param {string} content - The message content
   * @returns {string} The processed content as HTML
   */
  processMessageContent(content) {
    // Replace code blocks
    let processedContent = content.replace(/```([\s\S]*?)```/g, (match, code) => {
      return `<pre><code>${this.escapeHtml(code)}</code></pre>`;
    });
    
    // Replace inline code
    processedContent = processedContent.replace(/`([^`]+)`/g, (match, code) => {
      return `<code class="inline-code">${this.escapeHtml(code)}</code>`;
    });
    
    // Replace newlines with <br>
    processedContent = processedContent.replace(/\n/g, '<br>');
    
    return processedContent;
  }
  
  /**
   * Escape HTML special characters
   * @param {string} html - The HTML string to escape
   * @returns {string} The escaped HTML
   */
  escapeHtml(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
  }
  
  /**
   * Show typing indicator
   */
  showTypingIndicator() {
    // Create typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'ai-message assistant-message typing-indicator';
    typingIndicator.innerHTML = `
      <div class="ai-avatar"><span>AI</span></div>
      <div class="ai-message-content">
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    `;
    
    // Add to chat history
    this.chatHistoryElement.appendChild(typingIndicator);
    
    // Scroll to bottom
    this.chatHistoryElement.scrollTop = this.chatHistoryElement.scrollHeight;
  }
  
  /**
   * Remove typing indicator
   */
  removeTypingIndicator() {
    const typingIndicator = this.chatHistoryElement.querySelector('.typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }
  
  /**
   * Clear the chat history
   */
  clearChatHistory() {
    // Clear chat history element
    this.chatHistoryElement.innerHTML = '';
    
    // Clear chat history array
    this.chatHistory = [];
    
    // Save empty chat history to local storage
    this.saveChatHistory();
    
    // Add welcome message
    this.addMessageToChat('assistant', 'Hi! I\'m your AI assistant for Mono development. How can I help you today?');
  }
  
  /**
   * Save chat history to local storage
   */
  saveChatHistory() {
    localStorage.setItem('mono-ai-chat-history', JSON.stringify(this.chatHistory));
  }
  
  /**
   * Load chat history from local storage
   */
  loadChatHistory() {
    try {
      const storedHistory = localStorage.getItem('mono-ai-chat-history');
      if (storedHistory) {
        this.chatHistory = JSON.parse(storedHistory);
        
        // Render chat history
        this.chatHistoryElement.innerHTML = '';
        this.chatHistory.forEach(message => {
          this.addMessageToChat(message.role, message.content);
        });
      } else {
        // Add welcome message if no history
        this.addMessageToChat('assistant', 'Hi! I\'m your AI assistant for Mono development. How can I help you today?');
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      
      // Add welcome message on error
      this.addMessageToChat('assistant', 'Hi! I\'m your AI assistant for Mono development. How can I help you today?');
    }
  }
  
  /**
   * Update the context data
   * @param {Object} newContext - The new context data
   */
  updateContext(newContext) {
    this.contextData = {
      ...this.contextData,
      ...newContext
    };
  }
  
  /**
   * Add a file to recent files
   * @param {string} filePath - The file path
   */
  addToRecentFiles(filePath) {
    // Remove if already exists
    this.contextData.recentFiles = this.contextData.recentFiles.filter(file => file !== filePath);
    
    // Add to beginning
    this.contextData.recentFiles.unshift(filePath);
    
    // Limit to 10 recent files
    if (this.contextData.recentFiles.length > 10) {
      this.contextData.recentFiles = this.contextData.recentFiles.slice(0, 10);
    }
  }
  
  /**
   * Prepare context for the AI
   * @returns {Object} The prepared context
   */
  prepareContext() {
    return {
      ...this.contextData,
      timestamp: new Date().toISOString(),
      chatHistory: this.chatHistory.slice(-10) // Last 10 messages
    };
  }
  
  /**
   * Detect the programming language of code
   * @param {string} code - The code to detect
   * @returns {string} The detected language
   */
  detectLanguage(code) {
    // Simple language detection based on keywords and syntax
    if (code.includes('component') && code.includes('render')) {
      return 'Mono';
    } else if (code.includes('function') && code.includes('return')) {
      return 'JavaScript';
    } else if (code.includes('def') && code.includes(':')) {
      return 'Python';
    } else if (code.includes('class') && code.includes('{')) {
      return 'Java or C#';
    } else {
      return 'unknown language';
    }
  }
  
  /**
   * Generate a code explanation
   * @param {string} code - The code to explain
   * @returns {string} The explanation
   */
  generateCodeExplanation(code) {
    // This is a placeholder. In a real implementation, this would use an AI model.
    return 'appears to define a function or component that processes data and returns a result. The code uses standard programming patterns for control flow and data manipulation.';
  }
  
  /**
   * Generate a fix for code
   * @param {string} code - The code to fix
   * @returns {string} The fixed code
   */
  generateCodeFix(code) {
    // This is a placeholder. In a real implementation, this would use an AI model.
    return code.replace(/;/g, ';\n').replace(/{/g, '{\n  ').replace(/}/g, '\n}');
  }
  
  /**
   * Explain a code fix
   * @param {string} code - The original code
   * @returns {string} The explanation
   */
  explainCodeFix(code) {
    // This is a placeholder. In a real implementation, this would use an AI model.
    return 'improving code formatting, fixing syntax errors, and ensuring proper variable usage.';
  }
  
  /**
   * Generate optimized code
   * @param {string} code - The code to optimize
   * @returns {string} The optimized code
   */
  generateOptimizedCode(code) {
    // This is a placeholder. In a real implementation, this would use an AI model.
    return code.replace(/for \(/g, 'for(').replace(/if \(/g, 'if(').replace(/\s{2,}/g, ' ');
  }
  
  /**
   * Explain code optimization
   * @param {string} code - The original code
   * @returns {string} The explanation
   */
  explainOptimization(code) {
    // This is a placeholder. In a real implementation, this would use an AI model.
    return 'performance by reducing unnecessary operations, optimizing loops, and improving memory usage.';
  }
}

// Create and export a singleton instance
const enhancedAIAssistant = new EnhancedAIAssistant();

// Export the enhanced AI assistant
window.enhancedAIAssistant = enhancedAIAssistant;
