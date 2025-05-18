# my-switch-app

A web application built with the Switch framework for Mono.

## Overview

my-switch-app is a modern web application that demonstrates the capabilities of the Switch framework. It provides a robust, component-based architecture for building interactive web applications.

## Features

- **Component-based architecture**: Build UIs with reusable components
- **State management**: Centralized store for managing application state
- **Event handling**: Handle user interactions with event handlers
- **Routing**: Navigate between pages without full page reloads
- **Server integration**: Seamlessly integrate with Mono's HTTP server
- **Enhanced DOM manipulation**: Robust DOM operations with error handling
- **UI components**: Reusable UI components with better accessibility
- **Server-side rendering**: Render components on the server for better performance
- **Dark mode**: Toggle between light and dark themes
- **Responsive design**: Adapts to different screen sizes

## Project Structure

- `main.mono`: Entry point for the application
- `app.mono`: Main application component
- `src/`: Source code directory
  - `pages/`: Page components
    - `home.mono`: Home page
    - `about.mono`: About page
    - `packages.mono`: Packages page
    - `kits.mono`: Kits page
  - `components/`: Reusable components
  - `static/`: Static assets
    - `css/`: CSS files
      - `switch.css`: Switch framework styles
      - `ui.css`: UI component styles
      - `app.css`: Application-specific styles
    - `js/`: JavaScript files
      - `dom.js`: DOM manipulation utilities
      - `switch.js`: Core Switch framework
      - `store.js`: State management
      - `components.js`: UI components
      - `ssr.js`: Server-side rendering
      - `ui.js`: Enhanced UI components
      - `app.js`: Application-specific code
    - `img/`: Images
  - `templates/`: HTML templates

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Mono language interpreter

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/my-switch-app.git
cd my-switch-app
```

2. Run the application:

```bash
python3 run.py
```

3. Open your browser and navigate to [http://localhost:8000](http://localhost:8000).

## Development

### Running in Development Mode

To run the application in development mode with hot module replacement and live reloading:

```bash
../bin/run-switch main.mono --dev
```

### Building for Production

To build the application for production:

```bash
../bin/run-switch main.mono --prod
```

## Switch Framework

The Switch framework provides a robust foundation for building modern web applications. It includes:

### Core Features

- **Component-based architecture**: Build UIs with reusable components
- **Virtual DOM**: Efficient updates to the DOM
- **State management**: Centralized store for managing application state
- **Event handling**: Handle user interactions with event handlers
- **Routing**: Navigate between pages without full page reloads

### Enhanced Features

- **DOM manipulation**: Robust DOM operations with error handling
- **UI components**: Reusable UI components with better accessibility
- **Server-side rendering**: Render components on the server for better performance
- **Hot module replacement**: Update components without reloading the page

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The Mono language team for their excellent work
- The Switch framework contributors
- All the open-source projects that made this possible
