// Splash screen for Mono Editor
class SplashScreen {
  constructor() {
    this.splashWindow = null;
  }

  // Create and show the splash screen
  show() {
    // Create splash screen element
    this.createSplashElement();
    
    // Add to document
    document.body.appendChild(this.splashElement);
    
    // Animate in
    setTimeout(() => {
      this.splashElement.classList.add('visible');
    }, 10);
    
    return this;
  }
  
  // Hide and remove the splash screen
  hide() {
    if (!this.splashElement) return;
    
    // Animate out
    this.splashElement.classList.remove('visible');
    
    // Remove after animation
    setTimeout(() => {
      if (this.splashElement && this.splashElement.parentNode) {
        this.splashElement.parentNode.removeChild(this.splashElement);
      }
      this.splashElement = null;
    }, 500); // Match the CSS transition duration
  }
  
  // Create the splash screen element
  createSplashElement() {
    this.splashElement = document.createElement('div');
    this.splashElement.className = 'splash-screen';
    
    // Create content
    const content = document.createElement('div');
    content.className = 'splash-content';
    
    // Add logo
    const logo = document.createElement('img');
    logo.src = '../assets/icons/mono-logo.svg';
    logo.alt = 'Mono Logo';
    logo.className = 'splash-logo';
    content.appendChild(logo);
    
    // Add title
    const title = document.createElement('h1');
    title.textContent = 'Mono Editor';
    title.className = 'splash-title';
    content.appendChild(title);
    
    // Add loading indicator
    const loading = document.createElement('div');
    loading.className = 'splash-loading';
    const loadingBar = document.createElement('div');
    loadingBar.className = 'splash-loading-bar';
    loading.appendChild(loadingBar);
    content.appendChild(loading);
    
    // Add version
    const version = document.createElement('div');
    version.className = 'splash-version';
    version.textContent = 'Version 1.0.0';
    content.appendChild(version);
    
    this.splashElement.appendChild(content);
  }
}

// Export the splash screen
window.SplashScreen = SplashScreen;
