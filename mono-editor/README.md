# Mono Editor

A modern, Electron-based editor for the Mono language.

![Mono Editor Logo](assets/icons/mono-logo.svg)

## Features

- **Modern UI**: Clean, intuitive interface with multiple themes (Dark, Light, Nord)
- **Code Editor**: Edit Mono files with syntax highlighting, line numbers, and auto-indentation
- **Terminal**: Run Mono commands and see output directly in the editor
- **File Explorer**: Navigate through your project files with ease
- **Code Intelligence**: Context-aware code completion, error detection, and diagnostics
- **Themes**: Choose between Dark, Light, and Nord themes

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v14 or later)
- [npm](https://www.npmjs.com/) (v6 or later)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/mono-editor.git
   cd mono-editor
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the application:
   ```
   npm start
   ```

### Building

To build the application for your platform:

```
npm run build
```

For specific platforms:

```
npm run build:win    # Windows
npm run build:mac    # macOS
npm run build:linux  # Linux
```

## Development

### Project Structure

- `main.js` - Main Electron process
- `preload.js` - Preload script for secure IPC communication
- `src/` - Renderer process files
  - `index.html` - Main HTML file
  - `css/` - CSS stylesheets
  - `js/` - JavaScript files
- `assets/` - Icons and other assets

### Development Mode

To run the application in development mode with DevTools:

```
npm run dev
```

## Mono Language

Mono is a component-based language designed for building reactive applications. Key features include:

- Component-based architecture
- Static typing with type inference
- State management
- Event handling
- Concurrency support

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Electron](https://www.electronjs.org/)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)
- [XTerm.js](https://xtermjs.org/)
