"""
Code Intelligence for Spark Editor

This module provides intelligent code features for the Spark Editor:
- Context-aware autocomplete
- Error detection & diagnostics
- Real-time linting
- Code navigation
"""

import re
import os
from typing import List, Dict, Tuple, Set, Optional, Any
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat, QFont

# Mono language keywords
MONO_KEYWORDS = [
    "component", "function", "var", "state", "props", "return",
    "if", "else", "for", "while", "new", "this", "import", "export",
    "true", "false", "null", "undefined", "print", "emit", "on",
    "registerService", "getService", "provideContext", "consumeContext"
]

# Mono primitive types
MONO_TYPES = [
    "int", "float", "string", "bool", "void", "any"
]

# Common Mono methods
MONO_METHODS = [
    "start", "render", "increment", "decrement", "getValue", "getName",
    "add", "remove", "update", "delete", "get", "set", "toggle",
    "initialize", "dispose", "componentDidMount", "componentWillUnmount"
]

class MonoSymbol:
    """Represents a symbol in Mono code (variable, function, component, etc.)"""

    def __init__(self, name: str, symbol_type: str, scope: str = "global",
                 line: int = 0, column: int = 0, details: Dict[str, Any] = None):
        self.name = name
        self.symbol_type = symbol_type  # "component", "function", "variable", "parameter", "type"
        self.scope = scope
        self.line = line
        self.column = column
        self.details = details or {}

    def __str__(self) -> str:
        return f"{self.name} ({self.symbol_type})"

    def get_signature(self) -> str:
        """Get the signature of the symbol (for functions and components)"""
        if self.symbol_type == "function":
            params = self.details.get("parameters", [])
            param_str = ", ".join([f"{p.get('name')}: {p.get('type', 'any')}" for p in params])
            return_type = self.details.get("return_type", "void")
            return f"{self.name}({param_str}): {return_type}"
        elif self.symbol_type == "component":
            return f"component {self.name}"
        else:
            return self.name

class MonoCodeAnalyzer:
    """Analyzes Mono code to extract symbols, detect errors, and provide code intelligence"""

    def __init__(self):
        self.symbols: Dict[str, MonoSymbol] = {}
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.current_file: Optional[str] = None
        self.code: Optional[str] = None

    def analyze(self, code: str, file_path: Optional[str] = None) -> None:
        """Analyze Mono code and extract symbols, errors, and warnings"""
        self.code = code
        self.current_file = file_path
        self.symbols = {}
        self.errors = []
        self.warnings = []

        # Extract components
        self._extract_components()

        # Extract functions
        self._extract_functions()

        # Extract variables
        self._extract_variables()

        # Detect errors
        self._detect_errors()

        # Detect warnings
        self._detect_warnings()

    def _extract_components(self) -> None:
        """Extract component declarations from the code"""
        component_pattern = r'component\s+(\w+)\s*{'
        for match in re.finditer(component_pattern, self.code):
            component_name = match.group(1)
            start_pos = match.start()
            line = self.code[:start_pos].count('\n') + 1
            column = start_pos - self.code[:start_pos].rfind('\n') if '\n' in self.code[:start_pos] else start_pos + 1

            # Find the component body
            open_braces = 1
            body_start = match.end()
            body_end = body_start

            for i in range(body_start, len(self.code)):
                if self.code[i] == '{':
                    open_braces += 1
                elif self.code[i] == '}':
                    open_braces -= 1
                    if open_braces == 0:
                        body_end = i
                        break

            component_body = self.code[body_start:body_end]

            # Add component to symbols
            self.symbols[component_name] = MonoSymbol(
                name=component_name,
                symbol_type="component",
                line=line,
                column=column,
                details={"body": component_body}
            )

            # Extract state if present
            self._extract_state(component_name, component_body)

    def _extract_state(self, component_name: str, component_body: str) -> None:
        """Extract state declarations from a component body"""
        state_pattern = r'state\s*{([^}]*)}'
        state_match = re.search(state_pattern, component_body)

        if state_match:
            state_body = state_match.group(1)
            state_vars = []

            # Extract state variables
            var_pattern = r'(\w+)\s*(?::\s*(\w+))?\s*=\s*([^,;]+)'
            for var_match in re.finditer(var_pattern, state_body):
                var_name = var_match.group(1)
                var_type = var_match.group(2) or "any"
                var_value = var_match.group(3).strip()

                state_vars.append({
                    "name": var_name,
                    "type": var_type,
                    "value": var_value
                })

            # Update component details
            component_symbol = self.symbols.get(component_name)
            if component_symbol:
                component_symbol.details["state"] = state_vars

    def _extract_functions(self) -> None:
        """Extract function declarations from the code"""
        # Find all component scopes first
        component_scopes = {}
        for name, symbol in self.symbols.items():
            if symbol.symbol_type == "component":
                component_scopes[name] = symbol.details.get("body", "")

        # Extract functions within each component
        for component_name, component_body in component_scopes.items():
            function_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*(\w+))?\s*{'
            for match in re.finditer(function_pattern, component_body):
                function_name = match.group(1)
                params_str = match.group(2)
                return_type = match.group(3) or "void"

                # Extract parameters
                params = []
                if params_str.strip():
                    for param in params_str.split(','):
                        param = param.strip()
                        if ':' in param:
                            param_name, param_type = param.split(':', 1)
                            params.append({
                                "name": param_name.strip(),
                                "type": param_type.strip()
                            })
                        else:
                            params.append({
                                "name": param,
                                "type": "any"
                            })

                # Calculate line and column
                start_pos = component_body.find(match.group(0))
                if start_pos != -1:
                    start_pos += component_body.find(component_body)
                    line = self.code[:start_pos].count('\n') + 1
                    column = start_pos - self.code[:start_pos].rfind('\n') if '\n' in self.code[:start_pos] else start_pos + 1
                else:
                    line = 0
                    column = 0

                # Add function to symbols
                function_key = f"{component_name}.{function_name}"
                self.symbols[function_key] = MonoSymbol(
                    name=function_name,
                    symbol_type="function",
                    scope=component_name,
                    line=line,
                    column=column,
                    details={
                        "parameters": params,
                        "return_type": return_type
                    }
                )

    def _extract_variables(self) -> None:
        """Extract variable declarations from the code"""
        # Find all component scopes first
        component_scopes = {}
        for name, symbol in self.symbols.items():
            if symbol.symbol_type == "component":
                component_scopes[name] = symbol.details.get("body", "")

        # Extract variables within each component
        for component_name, component_body in component_scopes.items():
            # Extract var declarations
            var_pattern = r'var\s+(\w+)\s*(?::\s*(\w+))?\s*=\s*([^;]+)'
            for match in re.finditer(var_pattern, component_body):
                var_name = match.group(1)
                var_type = match.group(2) or "any"
                var_value = match.group(3).strip()

                # Calculate line and column
                start_pos = component_body.find(match.group(0))
                if start_pos != -1:
                    start_pos += component_body.find(component_body)
                    line = self.code[:start_pos].count('\n') + 1
                    column = start_pos - self.code[:start_pos].rfind('\n') if '\n' in self.code[:start_pos] else start_pos + 1
                else:
                    line = 0
                    column = 0

                # Add variable to symbols
                var_key = f"{component_name}.{var_name}"
                self.symbols[var_key] = MonoSymbol(
                    name=var_name,
                    symbol_type="variable",
                    scope=component_name,
                    line=line,
                    column=column,
                    details={
                        "type": var_type,
                        "value": var_value
                    }
                )

    def _detect_errors(self) -> None:
        """Detect errors in the code"""
        # Check for missing Main component
        if "Main" not in self.symbols:
            self.errors.append({
                "message": "Missing Main component",
                "line": 1,
                "column": 1,
                "severity": "error"
            })

        # Check for missing start function in Main component
        elif "Main.start" not in self.symbols:
            main_symbol = self.symbols.get("Main")
            if main_symbol:
                self.errors.append({
                    "message": "Missing start function in Main component",
                    "line": main_symbol.line,
                    "column": main_symbol.column,
                    "severity": "error"
                })

        # Check for syntax errors
        self._check_syntax_errors()

        # Check for type errors
        self._check_type_errors()

    def _check_syntax_errors(self) -> None:
        """Check for syntax errors in the code"""
        # Check for unbalanced braces
        open_braces = 0
        for i, char in enumerate(self.code):
            if char == '{':
                open_braces += 1
            elif char == '}':
                open_braces -= 1
                if open_braces < 0:
                    line = self.code[:i].count('\n') + 1
                    column = i - self.code[:i].rfind('\n') if '\n' in self.code[:i] else i + 1
                    self.errors.append({
                        "message": "Unbalanced braces: unexpected '}'",
                        "line": line,
                        "column": column,
                        "severity": "error"
                    })
                    break

        if open_braces > 0:
            self.errors.append({
                "message": f"Unbalanced braces: missing {open_braces} closing '}}' brace(s)",
                "line": self.code.count('\n') + 1,
                "column": len(self.code) - self.code.rfind('\n') if '\n' in self.code else len(self.code),
                "severity": "error"
            })

        # Check for missing semicolons
        lines = self.code.split('\n')
        for i, line in enumerate(lines):
            # Skip comments, empty lines, and lines that end with { or }
            if line.strip().startswith('//') or not line.strip() or line.strip().endswith('{') or line.strip().endswith('}'):
                continue

            # Skip lines that are part of a multi-line statement
            if line.strip().endswith(','):
                continue

            # Check if the line should end with a semicolon
            if not line.strip().endswith(';') and not line.strip().endswith('{') and not line.strip().endswith('}'):
                # Check if this is a function or component declaration
                if not re.search(r'(function|component)\s+\w+', line):
                    self.warnings.append({
                        "message": "Missing semicolon at end of statement",
                        "line": i + 1,
                        "column": len(line.rstrip()) + 1,
                        "severity": "warning"
                    })

    def _check_type_errors(self) -> None:
        """Check for type errors in the code"""
        # Check for type mismatches in variable assignments
        for name, symbol in self.symbols.items():
            if symbol.symbol_type == "variable" and symbol.details.get("type") != "any":
                var_type = symbol.details.get("type")
                var_value = symbol.details.get("value", "")

                # Check if the value matches the type
                if var_type == "int":
                    if not re.match(r'^-?\d+$', var_value) and not self._is_numeric_expression(var_value):
                        self.errors.append({
                            "message": f"Type error: cannot assign non-integer value to variable of type 'int'",
                            "line": symbol.line,
                            "column": symbol.column,
                            "severity": "error"
                        })
                elif var_type == "float":
                    if not re.match(r'^-?\d+(\.\d+)?$', var_value) and not self._is_numeric_expression(var_value):
                        self.errors.append({
                            "message": f"Type error: cannot assign non-numeric value to variable of type 'float'",
                            "line": symbol.line,
                            "column": symbol.column,
                            "severity": "error"
                        })
                elif var_type == "string":
                    if not (var_value.startswith('"') and var_value.endswith('"')) and \
                       not (var_value.startswith("'") and var_value.endswith("'")):
                        self.errors.append({
                            "message": f"Type error: cannot assign non-string value to variable of type 'string'",
                            "line": symbol.line,
                            "column": symbol.column,
                            "severity": "error"
                        })
                elif var_type == "bool":
                    if var_value not in ["true", "false"] and not self._is_boolean_expression(var_value):
                        self.errors.append({
                            "message": f"Type error: cannot assign non-boolean value to variable of type 'bool'",
                            "line": symbol.line,
                            "column": symbol.column,
                            "severity": "error"
                        })

    def _is_numeric_expression(self, expr: str) -> bool:
        """Check if an expression is numeric"""
        # This is a simplified check - a real implementation would need to parse the expression
        return any(op in expr for op in ['+', '-', '*', '/', '%'])

    def _is_boolean_expression(self, expr: str) -> bool:
        """Check if an expression is boolean"""
        # This is a simplified check - a real implementation would need to parse the expression
        return any(op in expr for op in ['==', '!=', '<', '>', '<=', '>=', '&&', '||', '!'])

    def _detect_warnings(self) -> None:
        """Detect warnings in the code"""
        # Check for unused variables
        self._check_unused_variables()

        # Check for inconsistent naming conventions
        self._check_naming_conventions()

    def _check_unused_variables(self) -> None:
        """Check for unused variables in the code"""
        for name, symbol in self.symbols.items():
            if symbol.symbol_type == "variable":
                var_name = symbol.name
                component_name = symbol.scope

                # Skip if this is a state variable
                if component_name in self.symbols:
                    component_symbol = self.symbols[component_name]
                    state_vars = component_symbol.details.get("state", [])
                    if any(var.get("name") == var_name for var in state_vars):
                        continue

                # Check if the variable is used in the component body
                component_body = self.symbols.get(component_name, MonoSymbol("", "")).details.get("body", "")
                var_pattern = r'\b' + re.escape(var_name) + r'\b'
                var_occurrences = re.findall(var_pattern, component_body)

                # If there's only one occurrence (the declaration), it's unused
                if len(var_occurrences) <= 1:
                    self.warnings.append({
                        "message": f"Unused variable: '{var_name}'",
                        "line": symbol.line,
                        "column": symbol.column,
                        "severity": "warning"
                    })

    def _check_naming_conventions(self) -> None:
        """Check for inconsistent naming conventions"""
        # Check component names (should be PascalCase)
        for name, symbol in self.symbols.items():
            if symbol.symbol_type == "component":
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', symbol.name):
                    self.warnings.append({
                        "message": f"Component name '{symbol.name}' should be in PascalCase",
                        "line": symbol.line,
                        "column": symbol.column,
                        "severity": "warning"
                    })

        # Check function names (should be camelCase)
        for name, symbol in self.symbols.items():
            if symbol.symbol_type == "function":
                if not re.match(r'^[a-z][a-zA-Z0-9]*$', symbol.name):
                    self.warnings.append({
                        "message": f"Function name '{symbol.name}' should be in camelCase",
                        "line": symbol.line,
                        "column": symbol.column,
                        "severity": "warning"
                    })

        # Check variable names (should be camelCase)
        for name, symbol in self.symbols.items():
            if symbol.symbol_type == "variable":
                if not re.match(r'^[a-z][a-zA-Z0-9]*$', symbol.name):
                    self.warnings.append({
                        "message": f"Variable name '{symbol.name}' should be in camelCase",
                        "line": symbol.line,
                        "column": symbol.column,
                        "severity": "warning"
                    })

    def get_symbols_at_position(self, line: int, column: int) -> List[MonoSymbol]:
        """Get symbols that are valid at the given position"""
        result = []

        # Determine the current scope
        current_scope = self._get_scope_at_position(line, column)

        # If we're in a component scope, add all symbols from that component
        if current_scope:
            for name, symbol in self.symbols.items():
                if symbol.scope == current_scope or symbol.symbol_type == "component":
                    result.append(symbol)
        else:
            # If we're not in any scope, just return all components
            for name, symbol in self.symbols.items():
                if symbol.symbol_type == "component":
                    result.append(symbol)

        return result

    def _get_scope_at_position(self, line: int, column: int) -> Optional[str]:
        """Determine the component scope at the given position"""
        # Find the component that contains this position
        for name, symbol in self.symbols.items():
            if symbol.symbol_type == "component":
                component_body = symbol.details.get("body", "")
                component_start = self.code.find(component_body)
                component_end = component_start + len(component_body)

                # Calculate the position in the code
                position = 0
                for i in range(line - 1):
                    position = self.code.find('\n', position) + 1
                position += column - 1

                # Check if the position is within this component
                if component_start <= position <= component_end:
                    return name

        return None

    def get_completions(self, line: int, column: int, prefix: str) -> List[Dict[str, Any]]:
        """Get completion suggestions at the given position"""
        completions = []

        # Add keywords
        for keyword in MONO_KEYWORDS:
            if keyword.startswith(prefix):
                completions.append({
                    "text": keyword,
                    "type": "keyword"
                })

        # Add types
        for type_name in MONO_TYPES:
            if type_name.startswith(prefix):
                completions.append({
                    "text": type_name,
                    "type": "type"
                })

        # Add symbols
        symbols = self.get_symbols_at_position(line, column)
        for symbol in symbols:
            if symbol.name.startswith(prefix):
                completions.append({
                    "text": symbol.name,
                    "type": symbol.symbol_type,
                    "detail": symbol.get_signature()
                })

        # If we're in a component context and the prefix starts with 'this.'
        if prefix.startswith('this.'):
            real_prefix = prefix[5:]  # Remove 'this.'
            current_scope = self._get_scope_at_position(line, column)
            if current_scope:
                # Add state variables
                component_symbol = self.symbols.get(current_scope)
                if component_symbol:
                    state_vars = component_symbol.details.get("state", [])
                    for var in state_vars:
                        var_name = var.get("name", "")
                        if var_name.startswith(real_prefix):
                            completions.append({
                                "text": f"this.state.{var_name}",
                                "type": "state",
                                "detail": f"{var_name}: {var.get('type', 'any')}"
                            })

                # Add methods
                for name, symbol in self.symbols.items():
                    if symbol.symbol_type == "function" and symbol.scope == current_scope:
                        if symbol.name.startswith(real_prefix):
                            completions.append({
                                "text": f"this.{symbol.name}",
                                "type": "method",
                                "detail": symbol.get_signature()
                            })

        # If we're in a component context and the prefix starts with 'this.state.'
        elif prefix.startswith('this.state.'):
            real_prefix = prefix[11:]  # Remove 'this.state.'
            current_scope = self._get_scope_at_position(line, column)
            if current_scope:
                # Add state variables
                component_symbol = self.symbols.get(current_scope)
                if component_symbol:
                    state_vars = component_symbol.details.get("state", [])
                    for var in state_vars:
                        var_name = var.get("name", "")
                        if var_name.startswith(real_prefix):
                            completions.append({
                                "text": f"this.state.{var_name}",
                                "type": "state",
                                "detail": f"{var_name}: {var.get('type', 'any')}"
                            })

        return completions

    def get_diagnostics(self) -> List[Dict[str, Any]]:
        """Get all diagnostics (errors and warnings)"""
        return self.errors + self.warnings

    def get_definition(self, line: int, column: int) -> Optional[MonoSymbol]:
        """Get the definition of the symbol at the given position"""
        # Get the word at the cursor position
        word = self._get_word_at_position(line, column)
        if not word:
            return None

        # Check if it's a symbol
        for name, symbol in self.symbols.items():
            if symbol.name == word:
                return symbol

        return None

    def _get_word_at_position(self, line: int, column: int) -> Optional[str]:
        """Get the word at the given position"""
        # Get the line text
        lines = self.code.split('\n')
        if line <= 0 or line > len(lines):
            return None

        line_text = lines[line - 1]
        if column <= 0 or column > len(line_text) + 1:
            return None

        # Find the word boundaries
        start = column - 1
        while start > 0 and (line_text[start - 1].isalnum() or line_text[start - 1] == '_'):
            start -= 1

        end = column - 1
        while end < len(line_text) and (line_text[end].isalnum() or line_text[end] == '_'):
            end += 1

        # Extract the word
        word = line_text[start:end]
        return word if word else None

class CodeCompletionModel:
    """Model for code completion suggestions"""

    def __init__(self, analyzer: MonoCodeAnalyzer):
        self.analyzer = analyzer
        self.completions: List[Dict[str, Any]] = []

    def update_completions(self, line: int, column: int, prefix: str) -> None:
        """Update the completion suggestions for the given position and prefix"""
        self.completions = self.analyzer.get_completions(line, column, prefix)

    def get_completions(self) -> List[Dict[str, Any]]:
        """Get the current completion suggestions"""
        return self.completions

class DiagnosticsModel:
    """Model for code diagnostics (errors and warnings)"""

    def __init__(self, analyzer: MonoCodeAnalyzer):
        self.analyzer = analyzer
        self.diagnostics: List[Dict[str, Any]] = []

    def update_diagnostics(self) -> None:
        """Update the diagnostics"""
        self.diagnostics = self.analyzer.get_diagnostics()

    def get_diagnostics(self) -> List[Dict[str, Any]]:
        """Get the current diagnostics"""
        return self.diagnostics

class CodeIntelligenceManager(QObject):
    """Manager for code intelligence features"""

    # Signals
    completionsUpdated = pyqtSignal()
    diagnosticsUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analyzer = MonoCodeAnalyzer()
        self.completion_model = CodeCompletionModel(self.analyzer)
        self.diagnostics_model = DiagnosticsModel(self.analyzer)

        # Set up a timer for delayed analysis
        self.analysis_timer = QTimer(self)
        self.analysis_timer.setSingleShot(True)
        self.analysis_timer.timeout.connect(self._perform_analysis)

        # Current state
        self.current_code = ""
        self.current_file = None
        self.current_line = 0
        self.current_column = 0
        self.current_prefix = ""
        self.current_context = ""
        self.current_separator = ""

    def set_code(self, code: str, file_path: Optional[str] = None) -> None:
        """Set the code to analyze"""
        self.current_code = code
        self.current_file = file_path
        self.analysis_timer.start(500)  # Delay analysis to avoid analyzing on every keystroke

    def set_cursor_position(self, line: int, column: int) -> None:
        """Set the current cursor position"""
        self.current_line = line
        self.current_column = column

    def set_completion_prefix(self, prefix: str) -> None:
        """Set the current completion prefix"""
        self.current_prefix = prefix
        self._update_completions()

    def set_completion_context(self, context: str, separator: str = '.') -> None:
        """Set the context for completions (e.g., the object before a dot)

        Args:
            context: The context string (e.g., object name before a dot)
            separator: The separator character (default: '.')
        """
        self.current_context = context
        self.current_separator = separator
        # Store the context for use in completions

    def _perform_analysis(self) -> None:
        """Perform code analysis"""
        self.analyzer.analyze(self.current_code, self.current_file)
        self._update_diagnostics()
        self._update_completions()

    def _update_completions(self) -> None:
        """Update completion suggestions"""
        self.completion_model.update_completions(self.current_line, self.current_column, self.current_prefix)
        self.completionsUpdated.emit()

    def _update_diagnostics(self) -> None:
        """Update diagnostics"""
        self.diagnostics_model.update_diagnostics()
        self.diagnosticsUpdated.emit()

    def get_completions(self) -> List[Dict[str, Any]]:
        """Get the current completion suggestions"""
        return self.completion_model.get_completions()

    def get_diagnostics(self) -> List[Dict[str, Any]]:
        """Get the current diagnostics"""
        return self.diagnostics_model.get_diagnostics()

    def get_definition(self, line: int, column: int) -> Optional[MonoSymbol]:
        """Get the definition of the symbol at the given position"""
        return self.analyzer.get_definition(line, column)
