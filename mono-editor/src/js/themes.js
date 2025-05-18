// Theme management for Mono Editor

class ThemeManager {
  constructor() {
    this.currentTheme = 'dark'; // Default theme

    // Initialize theme from localStorage if available
    this.initTheme();
  }

  initTheme() {
    // Get theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      this.setTheme(savedTheme);
    } else {
      // Set default theme
      this.setTheme(this.currentTheme);
    }
  }

  setTheme(themeName) {
    // Validate theme name
    if (!['dark', 'light', 'nord'].includes(themeName)) {
      console.error(`Invalid theme: ${themeName}`);
      return;
    }

    // Update current theme
    this.currentTheme = themeName;

    // Update body class
    document.body.className = `theme-${themeName}`;

    // Update localStorage
    localStorage.setItem('theme', themeName);

    // Update status bar
    const statusTheme = document.getElementById('status-theme');
    if (statusTheme) {
      statusTheme.textContent = themeName.charAt(0).toUpperCase() + themeName.slice(1);
    }

    // Update editor theme if available
    if (window.editorManager && typeof window.editorManager.setTheme === 'function') {
      try {
        window.editorManager.setTheme(themeName);
      } catch (error) {
        console.warn('Error setting editor theme:', error);
      }
    }

    // Update terminal theme if available
    if (window.terminalManager && typeof window.terminalManager.setTheme === 'function') {
      try {
        window.terminalManager.setTheme(themeName);
      } catch (error) {
        console.warn('Error setting terminal theme:', error);
      }
    }
  }

  getCurrentTheme() {
    return this.currentTheme;
  }
}

// Initialize the theme manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
  window.themeManager = new ThemeManager();
});
