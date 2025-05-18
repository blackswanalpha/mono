// Project Manager for Mono Editor

/**
 * Project Manager class for managing Mono projects
 */
class ProjectManager {
  constructor() {
    this.projectsElement = null;
    this.projectListElement = null;
    this.currentProject = null;
    this.projects = [];
    this.isVisible = false;
    
    // Initialize the project manager when the DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initialize());
    } else {
      this.initialize();
    }
  }
  
  /**
   * Initialize the project manager
   */
  initialize() {
    console.log('Initializing Project Manager...');
    
    // Create project manager UI if it doesn't exist
    this.createProjectManagerUI();
    
    // Add event listeners
    this.addEventListeners();
    
    // Load projects from local storage
    this.loadProjects();
    
    console.log('Project Manager initialized');
  }
  
  /**
   * Create the project manager UI
   */
  createProjectManagerUI() {
    // Check if project manager already exists
    const existingProjects = document.getElementById('project-manager');
    if (existingProjects) {
      this.projectsElement = existingProjects;
      this.projectListElement = existingProjects.querySelector('.project-list');
      return;
    }
    
    // Create project manager container
    this.projectsElement = document.createElement('div');
    this.projectsElement.id = 'project-manager';
    this.projectsElement.className = 'project-manager';
    this.projectsElement.style.display = 'none'; // Hidden by default
    
    // Create project manager header
    const header = document.createElement('div');
    header.className = 'project-manager-header';
    header.innerHTML = `
      <h2>Project Manager</h2>
      <div class="project-manager-controls">
        <button id="new-project-btn" class="new-project-btn">New Project</button>
        <button id="import-project-btn" class="import-project-btn">Import Project</button>
        <button id="close-project-manager-btn" class="close-project-manager-btn">×</button>
      </div>
    `;
    
    // Create project list
    this.projectListElement = document.createElement('div');
    this.projectListElement.className = 'project-list';
    
    // Create empty state
    const emptyState = document.createElement('div');
    emptyState.className = 'empty-projects';
    emptyState.innerHTML = `
      <p>No projects yet</p>
      <p>Create a new project or import an existing one</p>
    `;
    this.emptyStateElement = emptyState;
    
    // Assemble the project manager
    this.projectsElement.appendChild(header);
    this.projectsElement.appendChild(this.projectListElement);
    this.projectsElement.appendChild(emptyState);
    
    // Add to the document
    document.body.appendChild(this.projectsElement);
  }
  
  /**
   * Add event listeners to project manager elements
   */
  addEventListeners() {
    // Close button
    const closeButton = document.getElementById('close-project-manager-btn');
    if (closeButton) {
      closeButton.addEventListener('click', () => this.hide());
    }
    
    // New project button
    const newProjectButton = document.getElementById('new-project-btn');
    if (newProjectButton) {
      newProjectButton.addEventListener('click', () => this.showNewProjectDialog());
    }
    
    // Import project button
    const importProjectButton = document.getElementById('import-project-btn');
    if (importProjectButton) {
      importProjectButton.addEventListener('click', () => this.importProject());
    }
  }
  
  /**
   * Show the project manager
   */
  show() {
    if (!this.projectsElement) {
      this.createProjectManagerUI();
    }
    
    this.projectsElement.style.display = 'block';
    this.isVisible = true;
  }
  
  /**
   * Hide the project manager
   */
  hide() {
    if (this.projectsElement) {
      this.projectsElement.style.display = 'none';
    }
    this.isVisible = false;
  }
  
  /**
   * Toggle the project manager visibility
   */
  toggle() {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show();
    }
  }
  
  /**
   * Load projects from local storage
   */
  loadProjects() {
    try {
      const storedProjects = localStorage.getItem('mono-projects');
      if (storedProjects) {
        this.projects = JSON.parse(storedProjects);
        this.renderProjects();
      }
    } catch (error) {
      console.error('Error loading projects:', error);
      this.projects = [];
    }
  }
  
  /**
   * Save projects to local storage
   */
  saveProjects() {
    localStorage.setItem('mono-projects', JSON.stringify(this.projects));
  }
  
  /**
   * Render the project list
   */
  renderProjects() {
    if (!this.projectListElement) return;
    
    this.projectListElement.innerHTML = '';
    
    if (this.projects.length === 0) {
      if (this.emptyStateElement) {
        this.emptyStateElement.style.display = 'block';
      }
      return;
    }
    
    if (this.emptyStateElement) {
      this.emptyStateElement.style.display = 'none';
    }
    
    for (const project of this.projects) {
      const projectElement = this.createProjectElement(project);
      this.projectListElement.appendChild(projectElement);
    }
  }
  
  /**
   * Create a project element
   * @param {Object} project - The project data
   * @returns {HTMLElement} The project element
   */
  createProjectElement(project) {
    const projectElement = document.createElement('div');
    projectElement.className = `project-item ${project.id === this.currentProject?.id ? 'active' : ''}`;
    projectElement.dataset.projectId = project.id;
    
    projectElement.innerHTML = `
      <div class="project-icon">
        <img src="${project.icon || '../assets/icons/mono-logo.svg'}" alt="${project.name}">
      </div>
      <div class="project-info">
        <h3 class="project-name">${project.name}</h3>
        <p class="project-path">${project.path}</p>
        <div class="project-meta">
          <span class="project-last-opened">Last opened: ${this.formatDate(project.lastOpened)}</span>
        </div>
      </div>
      <div class="project-actions">
        <button class="project-open-btn">Open</button>
        <button class="project-settings-btn">⚙️</button>
        <button class="project-delete-btn">🗑️</button>
      </div>
    `;
    
    // Add event listeners
    const openButton = projectElement.querySelector('.project-open-btn');
    if (openButton) {
      openButton.addEventListener('click', () => this.openProject(project.id));
    }
    
    const settingsButton = projectElement.querySelector('.project-settings-btn');
    if (settingsButton) {
      settingsButton.addEventListener('click', (e) => {
        e.stopPropagation();
        this.showProjectSettings(project.id);
      });
    }
    
    const deleteButton = projectElement.querySelector('.project-delete-btn');
    if (deleteButton) {
      deleteButton.addEventListener('click', (e) => {
        e.stopPropagation();
        this.confirmDeleteProject(project.id);
      });
    }
    
    // Open project on click
    projectElement.addEventListener('click', () => this.openProject(project.id));
    
    return projectElement;
  }
  
  /**
   * Format a date for display
   * @param {string} dateString - The date string
   * @returns {string} The formatted date
   */
  formatDate(dateString) {
    if (!dateString) return 'Never';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  }
  
  /**
   * Show the new project dialog
   */
  showNewProjectDialog() {
    // Create dialog element
    const dialog = document.createElement('div');
    dialog.className = 'project-dialog';
    dialog.innerHTML = `
      <div class="project-dialog-content">
        <div class="project-dialog-header">
          <h3>Create New Project</h3>
          <button class="project-dialog-close">×</button>
        </div>
        <div class="project-dialog-body">
          <div class="project-form-group">
            <label for="project-name">Project Name</label>
            <input type="text" id="project-name" placeholder="My Mono Project">
          </div>
          <div class="project-form-group">
            <label for="project-location">Location</label>
            <div class="project-location-input">
              <input type="text" id="project-location" placeholder="Select a folder" readonly>
              <button id="browse-location-btn">Browse</button>
            </div>
          </div>
          <div class="project-form-group">
            <label for="project-template">Template</label>
            <select id="project-template">
              <option value="empty">Empty Project</option>
              <option value="basic">Basic Mono App</option>
              <option value="component-library">Component Library</option>
            </select>
          </div>
        </div>
        <div class="project-dialog-footer">
          <button class="project-dialog-cancel">Cancel</button>
          <button class="project-dialog-create">Create Project</button>
        </div>
      </div>
    `;
    
    // Add to document
    document.body.appendChild(dialog);
    
    // Add event listeners
    const closeButton = dialog.querySelector('.project-dialog-close');
    closeButton.addEventListener('click', () => {
      dialog.remove();
    });
    
    const cancelButton = dialog.querySelector('.project-dialog-cancel');
    cancelButton.addEventListener('click', () => {
      dialog.remove();
    });
    
    const browseButton = dialog.querySelector('#browse-location-btn');
    browseButton.addEventListener('click', async () => {
      try {
        const folderPath = await window.api.openFolder();
        if (folderPath) {
          dialog.querySelector('#project-location').value = folderPath;
        }
      } catch (error) {
        console.error('Error selecting folder:', error);
        alert('Error selecting folder: ' + error.message);
      }
    });
    
    const createButton = dialog.querySelector('.project-dialog-create');
    createButton.addEventListener('click', async () => {
      const name = dialog.querySelector('#project-name').value.trim();
      const location = dialog.querySelector('#project-location').value.trim();
      const template = dialog.querySelector('#project-template').value;
      
      if (!name) {
        alert('Please enter a project name');
        return;
      }
      
      if (!location) {
        alert('Please select a project location');
        return;
      }
      
      try {
        await this.createProject(name, location, template);
        dialog.remove();
      } catch (error) {
        console.error('Error creating project:', error);
        alert('Error creating project: ' + error.message);
      }
    });
  }
  
  /**
   * Create a new project
   * @param {string} name - The project name
   * @param {string} location - The project location
   * @param {string} template - The project template
   */
  async createProject(name, location, template) {
    try {
      console.log(`Creating project: ${name} at ${location} with template ${template}`);
      
      // Generate a unique ID
      const id = 'project_' + Date.now();
      
      // Create project object
      const project = {
        id,
        name,
        path: location,
        template,
        created: new Date().toISOString(),
        lastOpened: new Date().toISOString()
      };
      
      // Create project directory structure
      await this.createProjectStructure(project, template);
      
      // Add to projects list
      this.projects.push(project);
      
      // Save projects
      this.saveProjects();
      
      // Render projects
      this.renderProjects();
      
      // Open the new project
      this.openProject(id);
      
      return project;
    } catch (error) {
      console.error('Error creating project:', error);
      throw error;
    }
  }
  
  /**
   * Create project directory structure
   * @param {Object} project - The project data
   * @param {string} template - The project template
   */
  async createProjectStructure(project, template) {
    try {
      // Ensure the project directory exists
      await window.api.ensureDir(project.path);
      
      // Create project.json file
      const projectConfig = {
        name: project.name,
        id: project.id,
        template,
        created: project.created
      };
      
      await window.api.writeFile(
        `${project.path}/project.json`,
        JSON.stringify(projectConfig, null, 2)
      );
      
      // Create directories based on template
      switch (template) {
        case 'empty':
          // Just create a basic structure
          await window.api.ensureDir(`${project.path}/src`);
          await window.api.ensureDir(`${project.path}/assets`);
          break;
          
        case 'basic':
          // Create a basic Mono app structure
          await window.api.ensureDir(`${project.path}/src`);
          await window.api.ensureDir(`${project.path}/assets`);
          await window.api.ensureDir(`${project.path}/components`);
          
          // Create a sample component
          await window.api.writeFile(
            `${project.path}/components/Button.mono`,
            `component Button {
  state {
    text: string = "Click me";
    clicked: boolean = false;
  }

  function handleClick() {
    this.clicked = !this.clicked;
  }

  render {
    <button onClick={this.handleClick}>
      {this.clicked ? "Clicked!" : this.text}
    </button>
  }
}`
          );
          
          // Create a main file
          await window.api.writeFile(
            `${project.path}/src/main.mono`,
            `import Button from "../components/Button.mono";

component App {
  render {
    <div>
      <h1>My Mono App</h1>
      <Button />
    </div>
  }
}`
          );
          break;
          
        case 'component-library':
          // Create a component library structure
          await window.api.ensureDir(`${project.path}/src`);
          await window.api.ensureDir(`${project.path}/assets`);
          await window.api.ensureDir(`${project.path}/components`);
          await window.api.ensureDir(`${project.path}/components/buttons`);
          await window.api.ensureDir(`${project.path}/components/inputs`);
          await window.api.ensureDir(`${project.path}/components/layout`);
          
          // Create sample components
          await window.api.writeFile(
            `${project.path}/components/buttons/Button.mono`,
            `component Button {
  props {
    text: string = "Button";
    variant: string = "primary"; // primary, secondary, danger
    size: string = "medium"; // small, medium, large
    disabled: boolean = false;
    onClick: function = () => {};
  }

  function handleClick() {
    if (!this.props.disabled) {
      this.props.onClick();
    }
  }

  render {
    <button 
      class={\`btn btn-\${this.props.variant} btn-\${this.props.size} \${this.props.disabled ? 'disabled' : ''}\`}
      onClick={this.handleClick}
    >
      {this.props.text}
    </button>
  }
}`
          );
          
          // Create a main file
          await window.api.writeFile(
            `${project.path}/src/main.mono`,
            `import Button from "../components/buttons/Button.mono";

component ComponentLibrary {
  render {
    <div>
      <h1>Component Library</h1>
      <div class="component-demo">
        <h2>Buttons</h2>
        <div class="component-row">
          <Button text="Primary" variant="primary" />
          <Button text="Secondary" variant="secondary" />
          <Button text="Danger" variant="danger" />
        </div>
        <div class="component-row">
          <Button text="Small" size="small" />
          <Button text="Medium" size="medium" />
          <Button text="Large" size="large" />
        </div>
        <div class="component-row">
          <Button text="Disabled" disabled={true} />
        </div>
      </div>
    </div>
  }
}`
          );
          break;
      }
      
      console.log(`Project structure created for ${project.name}`);
    } catch (error) {
      console.error('Error creating project structure:', error);
      throw error;
    }
  }
  
  /**
   * Import an existing project
   */
  async importProject() {
    try {
      // Open folder dialog
      const folderPath = await window.api.openFolder();
      if (!folderPath) return;
      
      // Check if project.json exists
      let projectConfig;
      try {
        const projectJsonContent = await window.api.readFile(`${folderPath}/project.json`);
        projectConfig = JSON.parse(projectJsonContent);
      } catch (error) {
        // No project.json, create a new one
        projectConfig = {
          name: folderPath.split(/[/\\]/).pop(), // Get the folder name
          id: 'project_' + Date.now(),
          template: 'imported',
          created: new Date().toISOString()
        };
        
        // Save the project.json
        await window.api.writeFile(
          `${folderPath}/project.json`,
          JSON.stringify(projectConfig, null, 2)
        );
      }
      
      // Create project object
      const project = {
        id: projectConfig.id,
        name: projectConfig.name,
        path: folderPath,
        template: projectConfig.template,
        created: projectConfig.created,
        lastOpened: new Date().toISOString()
      };
      
      // Check if project already exists
      const existingIndex = this.projects.findIndex(p => p.id === project.id);
      if (existingIndex >= 0) {
        // Update existing project
        this.projects[existingIndex] = project;
      } else {
        // Add to projects list
        this.projects.push(project);
      }
      
      // Save projects
      this.saveProjects();
      
      // Render projects
      this.renderProjects();
      
      // Open the imported project
      this.openProject(project.id);
      
      return project;
    } catch (error) {
      console.error('Error importing project:', error);
      alert('Error importing project: ' + error.message);
    }
  }
  
  /**
   * Open a project
   * @param {string} projectId - The project ID
   */
  async openProject(projectId) {
    try {
      console.log(`Opening project: ${projectId}`);
      
      // Find the project
      const project = this.projects.find(p => p.id === projectId);
      if (!project) {
        throw new Error(`Project not found: ${projectId}`);
      }
      
      // Update last opened
      project.lastOpened = new Date().toISOString();
      this.saveProjects();
      
      // Set as current project
      this.currentProject = project;
      
      // Update UI
      this.renderProjects();
      
      // Open the project folder in the file explorer
      if (window.fileExplorer && typeof window.fileExplorer.openFolder === 'function') {
        await window.fileExplorer.openFolder(project.path);
      }
      
      // Hide the project manager
      this.hide();
      
      // Dispatch event
      const event = new CustomEvent('project-opened', { detail: project });
      document.dispatchEvent(event);
      
      return project;
    } catch (error) {
      console.error('Error opening project:', error);
      alert('Error opening project: ' + error.message);
    }
  }
  
  /**
   * Show project settings
   * @param {string} projectId - The project ID
   */
  showProjectSettings(projectId) {
    // Find the project
    const project = this.projects.find(p => p.id === projectId);
    if (!project) {
      console.error(`Project not found: ${projectId}`);
      return;
    }
    
    console.log(`Showing settings for project: ${project.name}`);
    
    // TODO: Implement project settings dialog
    alert(`Project settings for ${project.name} (Not implemented yet)`);
  }
  
  /**
   * Confirm project deletion
   * @param {string} projectId - The project ID
   */
  confirmDeleteProject(projectId) {
    // Find the project
    const project = this.projects.find(p => p.id === projectId);
    if (!project) {
      console.error(`Project not found: ${projectId}`);
      return;
    }
    
    if (confirm(`Are you sure you want to remove "${project.name}" from the project list? This will not delete the project files.`)) {
      this.deleteProject(projectId);
    }
  }
  
  /**
   * Delete a project
   * @param {string} projectId - The project ID
   */
  deleteProject(projectId) {
    try {
      console.log(`Deleting project: ${projectId}`);
      
      // Remove from projects list
      this.projects = this.projects.filter(p => p.id !== projectId);
      
      // If it was the current project, clear current project
      if (this.currentProject && this.currentProject.id === projectId) {
        this.currentProject = null;
      }
      
      // Save projects
      this.saveProjects();
      
      // Render projects
      this.renderProjects();
      
      // Dispatch event
      const event = new CustomEvent('project-deleted', { detail: { projectId } });
      document.dispatchEvent(event);
    } catch (error) {
      console.error('Error deleting project:', error);
      alert('Error deleting project: ' + error.message);
    }
  }
}

// Create and export a singleton instance
const projectManager = new ProjectManager();

// Export the project manager
window.projectManager = projectManager;
