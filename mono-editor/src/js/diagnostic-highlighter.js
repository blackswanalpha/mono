// Diagnostic Highlighter for Mono Editor
// Provides functionality to highlight errors, warnings, and other diagnostics in the editor

class DiagnosticHighlighter {
  constructor(editor) {
    this.editor = editor;
    this.diagnosticDecorations = {
      error: [],
      warning: [],
      info: [],
      hint: []
    };
    this.severityClasses = {
      error: 'error-marker',
      warning: 'warning-marker',
      info: 'info-marker',
      hint: 'hint-marker'
    };
    this.severityGlyphClasses = {
      error: 'diagnostic-glyph-error',
      warning: 'diagnostic-glyph-warning',
      info: 'diagnostic-glyph-info',
      hint: 'diagnostic-glyph-hint'
    };
  }

  /**
   * Set diagnostics to be highlighted in the editor
   * @param {Array} diagnostics Array of diagnostic objects
   */
  setDiagnostics(diagnostics) {
    if (!this.editor || !diagnostics) {
      return;
    }

    // Clear existing decorations
    this.clearDiagnostics();

    // Group diagnostics by severity
    const groupedDiagnostics = {
      error: [],
      warning: [],
      info: [],
      hint: []
    };

    // Process each diagnostic
    diagnostics.forEach(diagnostic => {
      const severity = diagnostic.severity || 'info';
      const line = diagnostic.line || 1;
      const startColumn = diagnostic.startColumn || 1;
      const endColumn = diagnostic.endColumn || 1000; // Default to end of line if not specified

      // Create a decoration for this diagnostic
      const decoration = {
        range: new monaco.Range(line, startColumn, line, endColumn),
        options: {
          isWholeLine: endColumn === 1000, // Use whole line if no specific range
          className: this.severityClasses[severity],
          glyphMarginClassName: this.severityGlyphClasses[severity],
          hoverMessage: { value: diagnostic.message || '' },
          inlineClassName: `inline-${this.severityClasses[severity]}`,
          stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
        }
      };

      groupedDiagnostics[severity].push(decoration);
    });

    // Apply decorations by severity
    for (const severity in groupedDiagnostics) {
      if (groupedDiagnostics[severity].length > 0) {
        this.diagnosticDecorations[severity] = this.editor.deltaDecorations(
          this.diagnosticDecorations[severity],
          groupedDiagnostics[severity]
        );
      }
    }
  }

  /**
   * Clear all diagnostic decorations
   */
  clearDiagnostics() {
    if (!this.editor) {
      return;
    }

    // Clear decorations for each severity
    for (const severity in this.diagnosticDecorations) {
      if (this.diagnosticDecorations[severity].length > 0) {
        this.diagnosticDecorations[severity] = this.editor.deltaDecorations(
          this.diagnosticDecorations[severity],
          []
        );
      }
    }
  }

  /**
   * Add a single diagnostic to the editor
   * @param {Object} diagnostic Diagnostic object
   */
  addDiagnostic(diagnostic) {
    if (!this.editor || !diagnostic) {
      return;
    }

    const severity = diagnostic.severity || 'info';
    const line = diagnostic.line || 1;
    const startColumn = diagnostic.startColumn || 1;
    const endColumn = diagnostic.endColumn || 1000;

    // Create a decoration for this diagnostic
    const decoration = {
      range: new monaco.Range(line, startColumn, line, endColumn),
      options: {
        isWholeLine: endColumn === 1000,
        className: this.severityClasses[severity],
        glyphMarginClassName: this.severityGlyphClasses[severity],
        hoverMessage: { value: diagnostic.message || '' },
        inlineClassName: `inline-${this.severityClasses[severity]}`,
        stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
      }
    };

    // Apply the decoration
    this.diagnosticDecorations[severity] = this.editor.deltaDecorations(
      this.diagnosticDecorations[severity],
      [...this.diagnosticDecorations[severity], decoration]
    );
  }

  /**
   * Remove a specific diagnostic
   * @param {Object} diagnostic Diagnostic object to remove
   */
  removeDiagnostic(diagnostic) {
    // This would require tracking each diagnostic individually
    // For simplicity, we'll just clear all diagnostics of the same severity
    if (!this.editor || !diagnostic) {
      return;
    }

    const severity = diagnostic.severity || 'info';
    this.diagnosticDecorations[severity] = this.editor.deltaDecorations(
      this.diagnosticDecorations[severity],
      []
    );
  }
}

// Export the DiagnosticHighlighter
window.DiagnosticHighlighter = DiagnosticHighlighter;
