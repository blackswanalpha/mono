// AI Assistant for Mono Editor

class AIAssistant {
  constructor() {
    this.assistantContainer = document.getElementById('ai-assistant-container');
    this.chatContainer = document.getElementById('ai-chat-container');
    this.inputContainer = document.getElementById('ai-input-container');
    this.inputField = document.getElementById('ai-input-field');
    this.sendButton = document.getElementById('ai-send-button');
    this.isVisible = false;

    // Initialize the assistant
    this.initAssistant();

    // Initialize event listeners
    this.initEventListeners();
  }

  initAssistant() {
    // Add welcome message
    this.addMessage('Hello! I\'m your Mono AI Assistant. I can help you with Mono language questions, code examples, and more. How can I help you today?', false);
  }

  initEventListeners() {
    // Send button
    this.sendButton.addEventListener('click', () => {
      this.sendMessage();
    });

    // Input field (Enter key)
    this.inputField.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Toggle button
    document.getElementById('toggle-ai-btn').addEventListener('click', () => {
      this.toggleAssistant();
    });

    // Close button
    document.getElementById('close-ai-btn').addEventListener('click', () => {
      this.hideAssistant();
    });
  }

  showAssistant() {
    this.assistantContainer.classList.remove('hidden');
    this.isVisible = true;
    this.inputField.focus();
  }

  hideAssistant() {
    this.assistantContainer.classList.add('hidden');
    this.isVisible = false;
  }

  toggleAssistant() {
    if (this.isVisible) {
      this.hideAssistant();
    } else {
      this.showAssistant();
    }
  }

  sendMessage() {
    const message = this.inputField.value.trim();
    if (!message) return;

    // Add user message
    this.addMessage(message, true);

    // Clear input field
    this.inputField.value = '';

    // Generate response
    this.generateResponse(message);
  }

  addMessage(message, isUser) {
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.className = isUser ? 'ai-message user' : 'ai-message assistant';

    // Create message content
    const contentElement = document.createElement('div');
    contentElement.className = 'ai-message-content';
    contentElement.textContent = message;

    // Add content to message
    messageElement.appendChild(contentElement);

    // Add message to chat
    this.chatContainer.appendChild(messageElement);

    // Scroll to bottom
    this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
  }

  generateResponse(message) {
    // Simple keyword-based responses
    const responses = {
      'component': 'Components are the basic building blocks in Mono. They can have state, props, and methods. Here\'s a simple example:\n\ncomponent Counter {\n  state count = 0;\n  \n  function increment() {\n    this.count++;\n  }\n  \n  function render() {\n    return <div>{this.count}</div>;\n  }\n}',

      'function': 'Functions in Mono are defined using the "function" keyword inside components. They can access component state and props using "this".',

      'state': 'State in Mono represents the internal mutable data of a component. It\'s defined using the "state" keyword and can be updated, triggering re-renders.',

      'props': 'Props in Mono are immutable inputs passed from parent components. They\'re accessed using "this.props" and cannot be modified by the component.',

      'element': 'Elements in Mono represent UI components that can be rendered. They can be primitive (built-in) or composite (custom components).',

      'frame': 'Frames in Mono are hierarchical component containers with their own lifecycle. They provide isolation and can have frame-scoped state.',

      'kit': 'Kits in Mono are curated collections of components with versioning and tools. They help organize and share reusable components.',

      'layout': 'Layouts in Mono define how components are arranged visually. They support declarative layouts, responsive design, and constraint-based layouts.',

      'concurrency': 'Mono supports concurrency with component threads (lightweight threads for components), thread safety through immutability and message passing, and synchronization using channels and mutexes.',

      'parallel': 'Mono supports parallel execution using the "parallel" keyword, allowing components to run concurrently for better performance.',

      'hello world': 'Here\'s a simple "Hello World" in Mono:\n\ncomponent HelloWorld {\n  function render() {\n    return <div>Hello, World!</div>;\n  }\n}\n\nexport default HelloWorld;',

      'counter': 'Here\'s a simple counter component in Mono:\n\ncomponent Counter {\n  state count = 0;\n  \n  function increment() {\n    this.count++;\n  }\n  \n  function decrement() {\n    if (this.count > 0) {\n      this.count--;\n    }\n  }\n  \n  function render() {\n    return (\n      <div>\n        <h2>Count: {this.count}</h2>\n        <button onClick={this.increment}>+</button>\n        <button onClick={this.decrement}>-</button>\n      </div>\n    );\n  }\n}'
    };

    // Check for keywords in the message
    const lowerMessage = message.toLowerCase();
    let response = null;

    for (const [keyword, resp] of Object.entries(responses)) {
      if (lowerMessage.includes(keyword.toLowerCase())) {
        response = resp;
        break;
      }
    }

    // Default response if no keyword matches
    if (!response) {
      response = "I don't have specific information about that. Try asking about components, functions, state, props, elements, frames, kits, layouts, or concurrency in Mono.";
    }

    // Add assistant message with a slight delay to simulate thinking
    setTimeout(() => {
      this.addMessage(response, false);
    }, 500);
  }
}

// Initialize the AI assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
  window.aiAssistant = new AIAssistant();
});
