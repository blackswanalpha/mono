"""
Optimized Code Intelligence for Spark Editor

This module provides optimized intelligent code features for the Spark Editor:
- Incremental analysis to avoid re-analyzing entire files on small changes
- Caching mechanisms for faster symbol lookup
- Fuzzy search for more flexible symbol matching
- Support for searching by symbol properties
"""

import re
import os
import time
import difflib
import hashlib
from typing import List, Dict, Tuple, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from functools import lru_cache
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer

from .code_intelligence import MonoSymbol, MonoCodeAnalyzer, MONO_KEYWORDS, MONO_TYPES, MONO_METHODS

# Maximum number of entries to keep in the cache
MAX_CACHE_SIZE = 100

# Minimum similarity score for fuzzy matching (0.0 to 1.0)
FUZZY_MATCH_THRESHOLD = 0.6

@dataclass
class CodeBlock:
    """Represents a block of code with its hash and symbols"""
    start_line: int
    end_line: int
    code: str
    hash: str
    symbols: Dict[str, MonoSymbol] = field(default_factory=dict)

    @staticmethod
    def compute_hash(code: str) -> str:
        """Compute a hash for a block of code"""
        return hashlib.md5(code.encode('utf-8')).hexdigest()

@dataclass
class AnalysisCache:
    """Cache for code analysis results"""
    code_hash: str
    symbols: Dict[str, MonoSymbol]
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    timestamp: float

class OptimizedMonoCodeAnalyzer(MonoCodeAnalyzer):
    """Optimized analyzer for Mono code with incremental analysis and caching"""

    def __init__(self):
        super().__init__()

        # Cache of analysis results
        self.analysis_cache: Dict[str, AnalysisCache] = {}

        # Code blocks for incremental analysis
        self.code_blocks: List[CodeBlock] = []

        # Symbol index for fast lookup
        self.symbol_index: Dict[str, List[MonoSymbol]] = {}

        # Last analyzed code for incremental analysis
        self.last_code: Optional[str] = None

    def analyze(self, code: str, file_path: Optional[str] = None) -> None:
        """Analyze Mono code with optimizations"""
        # Check if the code is the same as the last analysis
        if code == self.last_code and file_path == self.current_file:
            return

        # Compute hash of the code
        code_hash = CodeBlock.compute_hash(code)

        # Check if we have a cached analysis for this code
        if code_hash in self.analysis_cache:
            cache = self.analysis_cache[code_hash]
            self.symbols = cache.symbols.copy()
            self.errors = cache.errors.copy()
            self.warnings = cache.warnings.copy()
            self.current_file = file_path
            self.code = code
            self.last_code = code
            return

        # If the code is similar to the last analysis, use incremental analysis
        if self.last_code and self._similarity(code, self.last_code) > 0.8:
            self._incremental_analyze(code, file_path)
        else:
            # Perform full analysis
            super().analyze(code, file_path)
            self.last_code = code

            # Update code blocks
            self._update_code_blocks()

            # Update symbol index
            self._update_symbol_index()

        # Cache the analysis results
        self._cache_analysis(code_hash)

    def _similarity(self, code1: str, code2: str) -> float:
        """Calculate the similarity between two code strings"""
        # Use difflib to calculate similarity
        return difflib.SequenceMatcher(None, code1, code2).ratio()

    def _incremental_analyze(self, code: str, file_path: Optional[str] = None) -> None:
        """Perform incremental analysis of the code"""
        self.code = code
        self.current_file = file_path

        # Split the code into lines
        new_lines = code.split('\n')
        old_lines = self.last_code.split('\n')

        # Find the changed lines
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        changed_blocks = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ('replace', 'insert', 'delete'):
                # Add some context lines for better analysis
                start = max(0, j1 - 5)
                end = min(len(new_lines), j2 + 5)
                changed_blocks.append((start, end))

        # Merge overlapping blocks
        merged_blocks = []
        for start, end in sorted(changed_blocks):
            if merged_blocks and start <= merged_blocks[-1][1]:
                merged_blocks[-1] = (merged_blocks[-1][0], max(merged_blocks[-1][1], end))
            else:
                merged_blocks.append((start, end))

        # Analyze each changed block
        for start, end in merged_blocks:
            block_code = '\n'.join(new_lines[start:end])
            block_hash = CodeBlock.compute_hash(block_code)

            # Check if we have this block in our code blocks
            existing_block = None
            for block in self.code_blocks:
                if block.hash == block_hash:
                    existing_block = block
                    break

            if existing_block:
                # Reuse the symbols from the existing block
                for symbol_name, symbol in existing_block.symbols.items():
                    # Adjust the line numbers
                    adjusted_symbol = MonoSymbol(
                        name=symbol.name,
                        symbol_type=symbol.symbol_type,
                        scope=symbol.scope,
                        line=symbol.line + start - existing_block.start_line,
                        column=symbol.column,
                        details=symbol.details.copy()
                    )
                    self.symbols[symbol_name] = adjusted_symbol
            else:
                # Analyze the block
                temp_analyzer = MonoCodeAnalyzer()
                temp_analyzer.analyze(block_code)

                # Adjust the line numbers and add the symbols
                for symbol_name, symbol in temp_analyzer.symbols.items():
                    adjusted_symbol = MonoSymbol(
                        name=symbol.name,
                        symbol_type=symbol.symbol_type,
                        scope=symbol.scope,
                        line=symbol.line + start,
                        column=symbol.column,
                        details=symbol.details.copy()
                    )
                    self.symbols[symbol_name] = adjusted_symbol

                # Add the block to our code blocks
                new_block = CodeBlock(
                    start_line=start,
                    end_line=end,
                    code=block_code,
                    hash=block_hash,
                    symbols={name: symbol for name, symbol in temp_analyzer.symbols.items()}
                )
                self.code_blocks.append(new_block)

        # Update the last code
        self.last_code = code

        # Update symbol index
        self._update_symbol_index()

        # Detect errors and warnings
        self._detect_errors()
        self._detect_warnings()

    def _update_code_blocks(self) -> None:
        """Update the code blocks based on the current code"""
        # Split the code into logical blocks (components, functions, etc.)
        self.code_blocks = []

        # Extract components
        component_pattern = r'component\s+(\w+)\s*{'
        for match in re.finditer(component_pattern, self.code):
            component_name = match.group(1)
            start_pos = match.start()
            line = self.code[:start_pos].count('\n') + 1

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
                        body_end = i + 1
                        break

            # Get the component code
            component_code = self.code[start_pos:body_end]
            component_hash = CodeBlock.compute_hash(component_code)

            # Get the symbols for this component
            component_symbols = {}
            for name, symbol in self.symbols.items():
                if symbol.symbol_type == "component" and symbol.name == component_name:
                    component_symbols[name] = symbol
                elif symbol.scope == component_name:
                    component_symbols[name] = symbol

            # Add the component block
            end_line = line + component_code.count('\n')
            self.code_blocks.append(CodeBlock(
                start_line=line,
                end_line=end_line,
                code=component_code,
                hash=component_hash,
                symbols=component_symbols
            ))

    def _update_symbol_index(self) -> None:
        """Update the symbol index for fast lookup"""
        self.symbol_index = {}

        # Index symbols by name (lowercase for case-insensitive search)
        for name, symbol in self.symbols.items():
            key = symbol.name.lower()
            if key not in self.symbol_index:
                self.symbol_index[key] = []
            self.symbol_index[key].append(symbol)

            # Also index by partial name (for prefix search)
            for i in range(1, len(key)):
                prefix = key[:i]
                if prefix not in self.symbol_index:
                    self.symbol_index[prefix] = []
                self.symbol_index[prefix].append(symbol)

    def _cache_analysis(self, code_hash: str) -> None:
        """Cache the analysis results"""
        # Create a cache entry
        cache = AnalysisCache(
            code_hash=code_hash,
            symbols=self.symbols.copy(),
            errors=self.errors.copy(),
            warnings=self.warnings.copy(),
            timestamp=time.time()
        )

        # Add to cache
        self.analysis_cache[code_hash] = cache

        # Limit cache size
        if len(self.analysis_cache) > MAX_CACHE_SIZE:
            # Remove the oldest entries
            oldest_hashes = sorted(
                self.analysis_cache.keys(),
                key=lambda h: self.analysis_cache[h].timestamp
            )[:len(self.analysis_cache) - MAX_CACHE_SIZE]

            for old_hash in oldest_hashes:
                del self.analysis_cache[old_hash]

    @lru_cache(maxsize=100)
    def fuzzy_search(self, query: str, min_score: float = FUZZY_MATCH_THRESHOLD) -> List[MonoSymbol]:
        """Search for symbols using fuzzy matching"""
        results = []
        query = query.lower()

        # First, try to find exact matches
        if query in self.symbol_index:
            results.extend(self.symbol_index[query])

        # Then, try prefix matches
        for key, symbols in self.symbol_index.items():
            if key.startswith(query) and key != query:
                for symbol in symbols:
                    if symbol not in results:
                        results.append(symbol)

        # Finally, try fuzzy matches
        for name, symbol in self.symbols.items():
            score = self._fuzzy_match_score(query, symbol.name.lower())
            if score >= min_score and symbol not in results:
                results.append(symbol)

        return results

    def _fuzzy_match_score(self, query: str, text: str) -> float:
        """Calculate a fuzzy match score between a query and text"""
        # Use difflib's SequenceMatcher for fuzzy matching
        return difflib.SequenceMatcher(None, query, text).ratio()

    def search_by_property(self, property_name: str, property_value: Any) -> List[MonoSymbol]:
        """Search for symbols by a specific property"""
        results = []

        for symbol in self.symbols.values():
            # Check symbol properties
            if property_name == "type" and symbol.symbol_type == property_value:
                results.append(symbol)
            elif property_name == "scope" and symbol.scope == property_value:
                results.append(symbol)
            elif property_name == "line" and symbol.line == property_value:
                results.append(symbol)
            elif property_name == "column" and symbol.column == property_value:
                results.append(symbol)
            # Check details properties
            elif property_name in symbol.details:
                if symbol.details[property_name] == property_value:
                    results.append(symbol)
            # Check for function return type
            elif property_name == "return_type" and symbol.symbol_type == "function":
                if "return_type" in symbol.details and symbol.details["return_type"] == property_value:
                    results.append(symbol)
            # Check for function parameters
            elif property_name == "parameter_type" and symbol.symbol_type == "function":
                if "parameters" in symbol.details:
                    for param in symbol.details["parameters"]:
                        if param.get("type") == property_value:
                            results.append(symbol)
                            break

        return results

    def get_completions(self, line: int, column: int, prefix: str) -> List[Dict[str, Any]]:
        """Get completion suggestions with fuzzy matching"""
        completions = []

        # Add keywords (exact match only for keywords)
        for keyword in MONO_KEYWORDS:
            if keyword.lower().startswith(prefix.lower()):
                completions.append({
                    "text": keyword,
                    "type": "keyword",
                    "score": 1.0 if keyword.lower() == prefix.lower() else 0.9
                })

        # Add types (exact match only for types)
        for type_name in MONO_TYPES:
            if type_name.lower().startswith(prefix.lower()):
                completions.append({
                    "text": type_name,
                    "type": "type",
                    "score": 1.0 if type_name.lower() == prefix.lower() else 0.9
                })

        # Add symbols with fuzzy matching
        symbols = self.get_symbols_at_position(line, column)
        for symbol in symbols:
            score = self._fuzzy_match_score(prefix.lower(), symbol.name.lower())
            if score >= FUZZY_MATCH_THRESHOLD:
                completions.append({
                    "text": symbol.name,
                    "type": symbol.symbol_type,
                    "detail": symbol.get_signature(),
                    "score": score
                })

        # Sort by score (highest first)
        completions.sort(key=lambda c: c.get("score", 0.0), reverse=True)

        # Remove the score field before returning
        for completion in completions:
            if "score" in completion:
                del completion["score"]

        return completions

class OptimizedCodeIntelligenceManager(QObject):
    """Optimized manager for code intelligence features"""

    # Signals
    completionsUpdated = pyqtSignal()
    diagnosticsUpdated = pyqtSignal()
    symbolsUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analyzer = OptimizedMonoCodeAnalyzer()

        # Set up a timer for delayed analysis
        self.analysis_timer = QTimer(self)
        self.analysis_timer.setSingleShot(True)
        self.analysis_timer.timeout.connect(self._perform_analysis)

        # Set up a timer for incremental updates
        self.incremental_timer = QTimer(self)
        self.incremental_timer.setSingleShot(True)
        self.incremental_timer.timeout.connect(self._perform_incremental_update)

        # Current state
        self.current_code = ""
        self.current_file = None
        self.current_line = 0
        self.current_column = 0
        self.current_prefix = ""

        # Last update time
        self.last_update_time = 0

        # Pending changes
        self.pending_changes = False

    def set_code(self, code: str, file_path: Optional[str] = None) -> None:
        """Set the code to analyze"""
        # Check if the code has changed
        if code == self.current_code:
            return

        self.current_code = code
        self.current_file = file_path
        self.pending_changes = True

        # Calculate the time since the last update
        current_time = time.time()
        time_since_last_update = current_time - self.last_update_time

        # If it's been a while since the last update, do a full analysis
        if time_since_last_update > 5.0:  # 5 seconds
            self.analysis_timer.start(100)  # Quick analysis
        else:
            # Otherwise, schedule an incremental update
            self.incremental_timer.start(300)  # Delay for typing

    def set_cursor_position(self, line: int, column: int) -> None:
        """Set the current cursor position"""
        self.current_line = line
        self.current_column = column

    def set_completion_prefix(self, prefix: str) -> None:
        """Set the current completion prefix"""
        self.current_prefix = prefix
        self._update_completions()

    def _perform_analysis(self) -> None:
        """Perform a full code analysis"""
        self.analyzer.analyze(self.current_code, self.current_file)
        self._update_diagnostics()
        self._update_completions()
        self.symbolsUpdated.emit()

        # Update the last update time
        self.last_update_time = time.time()
        self.pending_changes = False

    def _perform_incremental_update(self) -> None:
        """Perform an incremental update"""
        if not self.pending_changes:
            return

        self.analyzer.analyze(self.current_code, self.current_file)
        self._update_diagnostics()
        self._update_completions()
        self.symbolsUpdated.emit()

        # Update the last update time
        self.last_update_time = time.time()
        self.pending_changes = False

    def _update_completions(self) -> None:
        """Update completion suggestions"""
        # Make sure we have the latest analysis
        if self.pending_changes:
            self._perform_incremental_update()

        self.completionsUpdated.emit()

    def _update_diagnostics(self) -> None:
        """Update diagnostics"""
        self.diagnosticsUpdated.emit()

    def get_completions(self) -> List[Dict[str, Any]]:
        """Get the current completion suggestions"""
        return self.analyzer.get_completions(self.current_line, self.current_column, self.current_prefix)

    def get_diagnostics(self) -> List[Dict[str, Any]]:
        """Get the current diagnostics"""
        return self.analyzer.get_diagnostics()

    def get_definition(self, line: int, column: int) -> Optional[MonoSymbol]:
        """Get the definition of the symbol at the given position"""
        return self.analyzer.get_definition(line, column)

    def get_symbols(self) -> Dict[str, MonoSymbol]:
        """Get all symbols in the current file"""
        return self.analyzer.symbols

    def fuzzy_search(self, query: str) -> List[MonoSymbol]:
        """Search for symbols using fuzzy matching"""
        return self.analyzer.fuzzy_search(query)

    def search_by_property(self, property_name: str, property_value: Any) -> List[MonoSymbol]:
        """Search for symbols by a specific property"""
        return self.analyzer.search_by_property(property_name, property_value)

    def get_completions(self, line: int, column: int, prefix: str) -> List[Dict[str, Any]]:
        """Get completion suggestions with fuzzy matching"""
        completions = []

        # Add keywords (exact match only for keywords)
        for keyword in MONO_KEYWORDS:
            if keyword.lower().startswith(prefix.lower()):
                completions.append({
                    "text": keyword,
                    "type": "keyword",
                    "score": 1.0 if keyword.lower() == prefix.lower() else 0.9
                })

        # Add types (exact match only for types)
        for type_name in MONO_TYPES:
            if type_name.lower().startswith(prefix.lower()):
                completions.append({
                    "text": type_name,
                    "type": "type",
                    "score": 1.0 if type_name.lower() == prefix.lower() else 0.9
                })

        # Add symbols with fuzzy matching
        symbols = self.get_symbols_at_position(line, column)
        for symbol in symbols:
            score = self._fuzzy_match_score(prefix.lower(), symbol.name.lower())
            if score >= FUZZY_MATCH_THRESHOLD:
                completions.append({
                    "text": symbol.name,
                    "type": symbol.symbol_type,
                    "detail": symbol.get_signature(),
                    "score": score
                })

        # Sort by score (highest first)
        completions.sort(key=lambda c: c.get("score", 0.0), reverse=True)

        # Remove the score field before returning
        for completion in completions:
            if "score" in completion:
                del completion["score"]

        return completions

class OptimizedCodeIntelligenceManager(QObject):
    """Optimized manager for code intelligence features"""

    # Signals
    completionsUpdated = pyqtSignal()
    diagnosticsUpdated = pyqtSignal()
    symbolsUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analyzer = OptimizedMonoCodeAnalyzer()

        # Set up a timer for delayed analysis
        self.analysis_timer = QTimer(self)
        self.analysis_timer.setSingleShot(True)
        self.analysis_timer.timeout.connect(self._perform_analysis)

        # Set up a timer for incremental updates
        self.incremental_timer = QTimer(self)
        self.incremental_timer.setSingleShot(True)
        self.incremental_timer.timeout.connect(self._perform_incremental_update)

        # Current state
        self.current_code = ""
        self.current_file = None
        self.current_line = 0
        self.current_column = 0
        self.current_prefix = ""

        # Last update time
        self.last_update_time = 0

        # Pending changes
        self.pending_changes = False

    def set_code(self, code: str, file_path: Optional[str] = None) -> None:
        """Set the code to analyze"""
        # Check if the code has changed
        if code == self.current_code:
            return

        self.current_code = code
        self.current_file = file_path
        self.pending_changes = True

        # Calculate the time since the last update
        current_time = time.time()
        time_since_last_update = current_time - self.last_update_time

        # If it's been a while since the last update, do a full analysis
        if time_since_last_update > 5.0:  # 5 seconds
            self.analysis_timer.start(100)  # Quick analysis
        else:
            # Otherwise, schedule an incremental update
            self.incremental_timer.start(300)  # Delay for typing

    def set_cursor_position(self, line: int, column: int) -> None:
        """Set the current cursor position"""
        self.current_line = line
        self.current_column = column

    def set_completion_prefix(self, prefix: str) -> None:
        """Set the current completion prefix"""
        self.current_prefix = prefix
        self._update_completions()

    def _perform_analysis(self) -> None:
        """Perform a full code analysis"""
        self.analyzer.analyze(self.current_code, self.current_file)
        self._update_diagnostics()
        self._update_completions()
        self.symbolsUpdated.emit()

        # Update the last update time
        self.last_update_time = time.time()
        self.pending_changes = False

    def _perform_incremental_update(self) -> None:
        """Perform an incremental update"""
        if not self.pending_changes:
            return

        self.analyzer.analyze(self.current_code, self.current_file)
        self._update_diagnostics()
        self._update_completions()
        self.symbolsUpdated.emit()

        # Update the last update time
        self.last_update_time = time.time()
        self.pending_changes = False

    def _update_completions(self) -> None:
        """Update completion suggestions"""
        # Make sure we have the latest analysis
        # NOTE: This was causing infinite recursion - removed to fix typing errors
        # if self.pending_changes:
        #     self._perform_incremental_update()

        self.completionsUpdated.emit()

    def _update_diagnostics(self) -> None:
        """Update diagnostics"""
        self.diagnosticsUpdated.emit()

    def get_completions(self) -> List[Dict[str, Any]]:
        """Get the current completion suggestions"""
        return self.analyzer.get_completions(self.current_line, self.current_column, self.current_prefix)

    def get_diagnostics(self) -> List[Dict[str, Any]]:
        """Get the current diagnostics"""
        return self.analyzer.get_diagnostics()

    def get_definition(self, line: int, column: int) -> Optional[MonoSymbol]:
        """Get the definition of the symbol at the given position"""
        return self.analyzer.get_definition(line, column)

    def get_symbols(self) -> Dict[str, MonoSymbol]:
        """Get all symbols in the current file"""
        return self.analyzer.symbols

    def fuzzy_search(self, query: str) -> List[MonoSymbol]:
        """Search for symbols using fuzzy matching"""
        return self.analyzer.fuzzy_search(query)

    def search_by_property(self, property_name: str, property_value: Any) -> List[MonoSymbol]:
        """Search for symbols by a specific property"""
        return self.analyzer.search_by_property(property_name, property_value)
