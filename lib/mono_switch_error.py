"""
Mono Switch Error - Error handling for the Switch framework

This module provides error handling for the Switch framework.
It includes error classes, error handling middleware, and error reporting.
"""

import os
import sys
import traceback
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union
from .mono_http import Response, Request, HttpStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('switch.log')
    ]
)

# Create a logger
logger = logging.getLogger('switch')

class SwitchError(Exception):
    """Base class for Switch framework errors."""
    def __init__(self, message: str, code: str = 'SWITCH_ERROR', details: Dict[str, Any] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary."""
        return {
            'message': self.message,
            'code': self.code,
            'details': self.details
        }
    
    def to_json(self) -> str:
        """Convert the error to JSON."""
        return json.dumps(self.to_dict())

class SwitchRenderError(SwitchError):
    """Error that occurs during rendering."""
    def __init__(self, message: str, component_name: str = None, component_id: str = None, details: Dict[str, Any] = None):
        super().__init__(message, 'SWITCH_RENDER_ERROR', details)
        self.component_name = component_name
        self.component_id = component_id
        
        if component_name:
            self.details['component_name'] = component_name
        
        if component_id:
            self.details['component_id'] = component_id

class SwitchComponentError(SwitchError):
    """Error that occurs in a component."""
    def __init__(self, message: str, component_name: str = None, component_id: str = None, method_name: str = None, details: Dict[str, Any] = None):
        super().__init__(message, 'SWITCH_COMPONENT_ERROR', details)
        self.component_name = component_name
        self.component_id = component_id
        self.method_name = method_name
        
        if component_name:
            self.details['component_name'] = component_name
        
        if component_id:
            self.details['component_id'] = component_id
        
        if method_name:
            self.details['method_name'] = method_name

class SwitchStateError(SwitchError):
    """Error that occurs in state management."""
    def __init__(self, message: str, state_path: str = None, details: Dict[str, Any] = None):
        super().__init__(message, 'SWITCH_STATE_ERROR', details)
        self.state_path = state_path
        
        if state_path:
            self.details['state_path'] = state_path

class SwitchEventError(SwitchError):
    """Error that occurs in event handling."""
    def __init__(self, message: str, event_type: str = None, event_target: str = None, details: Dict[str, Any] = None):
        super().__init__(message, 'SWITCH_EVENT_ERROR', details)
        self.event_type = event_type
        self.event_target = event_target
        
        if event_type:
            self.details['event_type'] = event_type
        
        if event_target:
            self.details['event_target'] = event_target

class SwitchRouteError(SwitchError):
    """Error that occurs in routing."""
    def __init__(self, message: str, route_path: str = None, details: Dict[str, Any] = None):
        super().__init__(message, 'SWITCH_ROUTE_ERROR', details)
        self.route_path = route_path
        
        if route_path:
            self.details['route_path'] = route_path

class SwitchKitError(SwitchError):
    """Error that occurs in kit handling."""
    def __init__(self, message: str, kit_name: str = None, component_name: str = None, details: Dict[str, Any] = None):
        super().__init__(message, 'SWITCH_KIT_ERROR', details)
        self.kit_name = kit_name
        self.component_name = component_name
        
        if kit_name:
            self.details['kit_name'] = kit_name
        
        if component_name:
            self.details['component_name'] = component_name

class SwitchErrorHandler:
    """Handles errors in the Switch framework."""
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def handle_error(self, error: Exception, req: Optional[Request] = None, res: Optional[Response] = None) -> Optional[Response]:
        """Handle an error."""
        # Log the error
        self.log_error(error)
        
        # If we have a response object, send an error response
        if res:
            return self.create_error_response(error, res)
        
        return None
    
    def log_error(self, error: Exception) -> None:
        """Log an error."""
        if isinstance(error, SwitchError):
            logger.error(f"{error.code}: {error.message}")
            if error.details:
                logger.error(f"Details: {json.dumps(error.details)}")
        else:
            logger.error(f"Unhandled error: {str(error)}")
        
        # Log the stack trace in debug mode
        if self.debug:
            logger.error(traceback.format_exc())
    
    def create_error_response(self, error: Exception, res: Response) -> Response:
        """Create an error response."""
        if isinstance(error, SwitchError):
            # Create a JSON response for Switch errors
            res.status(HttpStatus.INTERNAL_SERVER_ERROR)
            res.header('Content-Type', 'application/json')
            res.text(error.to_json())
        else:
            # Create a generic error response for other errors
            res.status(HttpStatus.INTERNAL_SERVER_ERROR)
            
            if self.debug:
                # Include stack trace in debug mode
                res.text(f"Error: {str(error)}\n\n{traceback.format_exc()}")
            else:
                # Simple error message in production
                res.text(f"Internal Server Error")
        
        return res
    
    def create_error_html(self, error: Exception) -> str:
        """Create an HTML error page."""
        if isinstance(error, SwitchError):
            title = f"Switch Error: {error.code}"
            message = error.message
            details = json.dumps(error.details, indent=2) if error.details else None
        else:
            title = "Unhandled Error"
            message = str(error)
            details = None
        
        # Create the HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.5;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        .error-container {{
            background-color: #fff;
            border-radius: 0.5rem;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
            padding: 2rem;
            margin-top: 2rem;
        }}
        .error-title {{
            color: #e53e3e;
            margin-top: 0;
        }}
        .error-message {{
            font-size: 1.25rem;
            margin-bottom: 1.5rem;
        }}
        .error-details {{
            background-color: #f7fafc;
            border-radius: 0.25rem;
            padding: 1rem;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-x: auto;
        }}
        .error-stack {{
            margin-top: 1.5rem;
            background-color: #f7fafc;
            border-radius: 0.25rem;
            padding: 1rem;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1 class="error-title">{title}</h1>
        <div class="error-message">{message}</div>
        
        {f'<div class="error-details">{details}</div>' if details else ''}
        
        {f'<div class="error-stack">{traceback.format_exc()}</div>' if self.debug else ''}
    </div>
</body>
</html>"""
        
        return html

class SwitchErrorMiddleware:
    """Middleware for handling errors in the Switch framework."""
    def __init__(self, debug: bool = False):
        self.error_handler = SwitchErrorHandler(debug)
    
    def handle(self, req: Request, res: Response, next: Callable) -> None:
        """Handle a request."""
        try:
            # Call the next middleware
            next()
        except Exception as error:
            # Handle the error
            self.error_handler.handle_error(error, req, res)

# Create a global instance of the error handler
error_handler = SwitchErrorHandler()

def get_error_handler() -> SwitchErrorHandler:
    """Get the global error handler instance."""
    return error_handler

# Create a global instance of the error middleware
error_middleware = SwitchErrorMiddleware()

def get_error_middleware() -> SwitchErrorMiddleware:
    """Get the global error middleware instance."""
    return error_middleware

def set_debug_mode(debug: bool) -> None:
    """Set the debug mode for error handling."""
    error_handler.debug = debug
    error_middleware.error_handler.debug = debug
