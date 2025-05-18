// Editor Tests for Mono Editor
// This script contains tests for the editor functionality

// Import the test framework
const { monoTestFramework, assert } = typeof module !== 'undefined' && module.exports
  ? require('./test-framework')
  : { monoTestFramework: window.monoTestFramework, assert: window.assert };

// Define the editor tests
monoTestFramework.suite('Editor', function() {
  // Setup and teardown
  monoTestFramework.beforeAll(async function() {
    console.log('Setting up editor tests...');

    // Wait for Monaco to be loaded
    if (typeof monaco === 'undefined') {
      return new Promise((resolve) => {
        window.addEventListener('monaco-ready', resolve, { once: true });
      });
    }
  });

  monoTestFramework.afterAll(function() {
    console.log('Cleaning up editor tests...');
  });

  // Test editor initialization
  monoTestFramework.test('Editor Manager Initialization', function() {
    assert.assertDefined(window.editorManager, 'Editor manager should be defined');
    assert.assertTrue(
      typeof window.editorManager.createEditor === 'function',
      'Editor manager should have createEditor method'
    );
    assert.assertTrue(
      typeof window.editorManager.openFile === 'function',
      'Editor manager should have openFile method'
    );
  });

  // Test editor creation
  monoTestFramework.test('Editor Creation', function() {
    const tabId = 'test-tab-' + Date.now();
    window.editorManager.createEditor(tabId);

    assert.assertDefined(
      window.editorManager.editors[tabId],
      'Editor should be created with the given tab ID'
    );
    assert.assertDefined(
      window.editorManager.editors[tabId].editor,
      'Editor instance should be created'
    );

    // Clean up
    window.editorManager.closeTab(tabId);
  });

  // Test editor content
  monoTestFramework.test('Editor Content', function() {
    const tabId = 'test-tab-' + Date.now();
    window.editorManager.createEditor(tabId);
    const editor = window.editorManager.editors[tabId].editor;

    // Set content
    const testContent = 'Test content for Mono editor';
    editor.setValue(testContent);

    // Check content
    assert.assertEqual(
      editor.getValue(),
      testContent,
      'Editor content should match the set value'
    );

    // Clean up
    window.editorManager.closeTab(tabId);
  });

  // Test editor language
  monoTestFramework.test('Editor Language', function() {
    const tabId = 'test-tab-' + Date.now();
    window.editorManager.createEditor(tabId);
    const editor = window.editorManager.editors[tabId].editor;

    // Set language
    const model = editor.getModel();
    monaco.editor.setModelLanguage(model, 'mono');

    // Check language
    assert.assertEqual(
      model.getLanguageId(),
      'mono',
      'Editor language should be set to mono'
    );

    // Clean up
    window.editorManager.closeTab(tabId);
  });

  // Test tab activation
  monoTestFramework.test('Tab Activation', function() {
    const tabId1 = 'test-tab-1-' + Date.now();
    const tabId2 = 'test-tab-2-' + Date.now();

    // Create two tabs
    window.editorManager.createEditor(tabId1);
    window.editorManager.createEditor(tabId2);

    // Activate the first tab
    window.editorManager.activateTab(tabId1);
    assert.assertEqual(
      window.editorManager.activeEditor,
      tabId1,
      'First tab should be active'
    );

    // Activate the second tab
    window.editorManager.activateTab(tabId2);
    assert.assertEqual(
      window.editorManager.activeEditor,
      tabId2,
      'Second tab should be active'
    );

    // Clean up
    window.editorManager.closeTab(tabId1);
    window.editorManager.closeTab(tabId2);
  });

  // Test tab closing
  monoTestFramework.test('Tab Closing', function() {
    const tabId = 'test-tab-' + Date.now();

    // Create a tab
    window.editorManager.createEditor(tabId);
    assert.assertDefined(
      window.editorManager.editors[tabId],
      'Tab should be created'
    );

    // Close the tab
    window.editorManager.closeTab(tabId);
    assert.assertUndefined(
      window.editorManager.editors[tabId],
      'Tab should be closed'
    );
  });

  // Skip this test if file system access is not available
  monoTestFramework.skip('File Operations', function() {
    // This test requires file system access, which may not be available in all environments
    // It's skipped by default
  });
});

// Define the Monaco loader tests
monoTestFramework.suite('Monaco Loader', function() {
  monoTestFramework.test('Monaco Loading', function() {
    assert.assertDefined(window.monaco, 'Monaco should be defined');
    assert.assertDefined(window.monaco.editor, 'Monaco editor should be defined');
    assert.assertTrue(
      typeof window.monaco.editor.create === 'function',
      'Monaco editor should have create method'
    );
  });

  monoTestFramework.test('Monaco Language Registration', function() {
    assert.assertDefined(
      window.monaco.languages.getLanguages().find(lang => lang.id === 'mono'),
      'Mono language should be registered'
    );
  });
});

// Define the error handling tests
monoTestFramework.suite('Error Handling', function() {
  monoTestFramework.test('Error Handler Initialization', function() {
    assert.assertDefined(window.errorHandler, 'Error handler should be defined');
    assert.assertTrue(
      typeof window.errorHandler.handleError === 'function',
      'Error handler should have handleError method'
    );
  });

  monoTestFramework.test('Error Handling', function() {
    const initialErrorCount = window.errorHandler.errors.length;

    // Trigger an error
    window.errorHandler.handleError({
      type: 'test',
      message: 'Test error',
      timestamp: new Date()
    });

    assert.assertEqual(
      window.errorHandler.errors.length,
      initialErrorCount + 1,
      'Error should be added to the error list'
    );

    // Clean up
    window.errorHandler.errors.pop();
  });

  monoTestFramework.test('Error Recovery Strategies', function() {
    // Check that recovery strategies are registered
    assert.assertTrue(
      window.errorHandler.recoveryStrategies instanceof Map,
      'Recovery strategies should be a Map'
    );

    assert.assertTrue(
      window.errorHandler.recoveryStrategies.size > 0,
      'Recovery strategies should be registered'
    );

    // Check specific recovery strategies
    assert.assertTrue(
      window.errorHandler.recoveryStrategies.has('monaco-load-error'),
      'Monaco load error recovery strategy should be registered'
    );

    assert.assertTrue(
      window.errorHandler.recoveryStrategies.has('file-operation-error'),
      'File operation error recovery strategy should be registered'
    );

    assert.assertTrue(
      window.errorHandler.recoveryStrategies.has('terminal-error'),
      'Terminal error recovery strategy should be registered'
    );
  });

  monoTestFramework.test('Error Recovery Recording', function() {
    // Record a recovery attempt
    window.errorHandler.recordRecovery('test-error', true);

    // Check that recovery attempts are recorded
    assert.assertTrue(
      Array.isArray(window.errorHandler.recoveryAttempts),
      'Recovery attempts should be an array'
    );

    assert.assertTrue(
      window.errorHandler.recoveryAttempts.length > 0,
      'Recovery attempts should be recorded'
    );

    // Check recovery statistics
    assert.assertTrue(
      window.errorHandler.recoveryStats instanceof Map,
      'Recovery stats should be a Map'
    );

    assert.assertTrue(
      window.errorHandler.recoveryStats.has('test-error'),
      'Recovery stats should include test error'
    );

    const stats = window.errorHandler.recoveryStats.get('test-error');
    assert.assertEqual(
      stats.attempts,
      1,
      'Recovery stats should record attempts'
    );

    assert.assertEqual(
      stats.successes,
      1,
      'Recovery stats should record successes'
    );

    // Clean up
    window.errorHandler.recoveryAttempts.pop();
    window.errorHandler.recoveryStats.delete('test-error');
  });
});

// Define the performance monitoring tests
monoTestFramework.suite('Performance Monitoring', function() {
  monoTestFramework.test('Performance Monitor Initialization', function() {
    assert.assertDefined(window.performanceMonitor, 'Performance monitor should be defined');
    assert.assertDefined(window.performanceMonitor.metrics, 'Performance metrics should be defined');
  });

  monoTestFramework.test('Performance Metrics Structure', function() {
    const metrics = window.performanceMonitor.metrics;

    assert.assertDefined(metrics.startTime, 'Start time should be defined');
    assert.assertTrue(Array.isArray(metrics.loadEvents), 'Load events should be an array');
    assert.assertDefined(metrics.componentInitTimes, 'Component init times should be defined');
    assert.assertDefined(metrics.resourceLoadTimes, 'Resource load times should be defined');
  });

  monoTestFramework.test('Performance Event Recording', function() {
    const initialEventCount = window.performanceMonitor.metrics.loadEvents.length;

    // Record an event
    window.performanceMonitor.recordEvent('test-event');

    assert.assertEqual(
      window.performanceMonitor.metrics.loadEvents.length,
      initialEventCount + 1,
      'Event should be added to the load events'
    );

    // Check the recorded event
    const lastEvent = window.performanceMonitor.metrics.loadEvents[window.performanceMonitor.metrics.loadEvents.length - 1];
    assert.assertEqual(lastEvent.name, 'test-event', 'Event name should be recorded correctly');
    assert.assertDefined(lastEvent.timeFromStart, 'Event time should be recorded');

    // Clean up
    window.performanceMonitor.metrics.loadEvents.pop();
  });

  monoTestFramework.test('Component Initialization Recording', function() {
    const componentName = 'test-component';

    // Record component initialization
    window.performanceMonitor.recordComponentInit(componentName);

    // Check that the component was recorded
    assert.assertDefined(
      window.performanceMonitor.metrics.componentInitTimes[componentName],
      'Component initialization should be recorded'
    );

    // Check the recorded data
    const componentData = window.performanceMonitor.metrics.componentInitTimes[componentName];
    assert.assertDefined(componentData.time, 'Component init time should be recorded');
    assert.assertDefined(componentData.timeFromStart, 'Component init time from start should be recorded');

    // Clean up
    delete window.performanceMonitor.metrics.componentInitTimes[componentName];
  });

  monoTestFramework.test('Optimization Suggestions', function() {
    // Get optimization suggestions
    const suggestions = window.performanceMonitor.getOptimizationSuggestions();

    // Check that suggestions is an array
    assert.assertTrue(Array.isArray(suggestions), 'Optimization suggestions should be an array');
  });
});

// Define the snippet manager tests
monoTestFramework.suite('Snippet Manager', function() {
  monoTestFramework.test('Snippet Manager Initialization', function() {
    assert.assertDefined(window.snippetManager, 'Snippet manager should be defined');
    assert.assertDefined(window.snippetManager.snippets, 'Snippets should be defined');
    assert.assertTrue(Array.isArray(window.snippetManager.categories), 'Categories should be an array');
  });

  monoTestFramework.test('Default Snippets', function() {
    // Check that default snippets are loaded
    assert.assertTrue(
      Object.keys(window.snippetManager.snippets).length > 0,
      'Default snippets should be loaded'
    );

    // Check that categories are extracted
    assert.assertTrue(
      window.snippetManager.categories.length > 0,
      'Categories should be extracted from snippets'
    );
  });

  monoTestFramework.test('Snippet Retrieval', function() {
    // Get a snippet by prefix
    const componentSnippet = window.snippetManager.getSnippet('component');

    // Check that the snippet exists
    assert.assertDefined(componentSnippet, 'Component snippet should exist');

    // Check snippet properties
    assert.assertEqual(componentSnippet.prefix, 'component', 'Snippet prefix should match');
    assert.assertDefined(componentSnippet.name, 'Snippet name should be defined');
    assert.assertDefined(componentSnippet.description, 'Snippet description should be defined');
    assert.assertDefined(componentSnippet.category, 'Snippet category should be defined');
    assert.assertDefined(componentSnippet.body, 'Snippet body should be defined');
  });

  monoTestFramework.test('Snippet Categories', function() {
    // Get snippets by category
    const monoSnippets = window.snippetManager.getSnippetsByCategory('Mono');

    // Check that snippets are returned
    assert.assertTrue(
      Array.isArray(monoSnippets),
      'getSnippetsByCategory should return an array'
    );

    assert.assertTrue(
      monoSnippets.length > 0,
      'Mono category should have snippets'
    );

    // Check that all snippets have the correct category
    monoSnippets.forEach(snippet => {
      assert.assertEqual(
        snippet.category,
        'Mono',
        'All snippets should have the Mono category'
      );
    });
  });
});

// Export the test suites
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { monoTestFramework };
}
