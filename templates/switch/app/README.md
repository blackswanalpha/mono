# {{APP_NAME}}

A web application built with the Switch framework for Mono.

## Getting Started

To run the application:

```bash
mono-switch main.mono
```

Then open your browser and navigate to [http://localhost:8000](http://localhost:8000).

## Project Structure

- `main.mono`: Entry point for the application
- `app.mono`: Main application component
- `pages/`: Page components
  - `home.mono`: Home page
  - `about.mono`: About page
- `components/`: Reusable components
- `store/`: State management
  - `index.mono`: Store configuration

## Development

### Creating a New Component

```bash
mono-switch-cli component MyComponent
```

### Creating a New Page

```bash
mono-switch-cli page MyPage
```

### Creating a Store Module

```bash
mono-switch-cli store myModule
```

## Features

- Component-based architecture
- Client-side rendering
- State management
- Event handling
- Routing
- Server integration

## License

This project is licensed under the MIT License.
