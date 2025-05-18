// Test Framework for Mono Editor
// This script provides a comprehensive testing framework for the Mono editor

class MonoTestFramework {
  constructor() {
    this.tests = [];
    this.suites = {};
    this.currentSuite = null;
    this.results = {
      passed: 0,
      failed: 0,
      skipped: 0,
      total: 0
    };
    this.startTime = null;
    this.endTime = null;
  }
  
  /**
   * Create a new test suite
   * @param {string} name - Name of the test suite
   * @param {Function} callback - Function containing the tests
   */
  suite(name, callback) {
    console.log(`Creating test suite: ${name}`);
    
    // Save the previous suite
    const previousSuite = this.currentSuite;
    
    // Create a new suite
    this.currentSuite = name;
    this.suites[name] = {
      name,
      tests: [],
      beforeEach: null,
      afterEach: null,
      beforeAll: null,
      afterAll: null
    };
    
    // Run the callback to define the tests
    callback();
    
    // Restore the previous suite
    this.currentSuite = previousSuite;
  }
  
  /**
   * Add a test to the current suite
   * @param {string} name - Name of the test
   * @param {Function} callback - Test function
   * @param {boolean} skip - Whether to skip this test
   */
  test(name, callback, skip = false) {
    if (!this.currentSuite) {
      throw new Error('Cannot add a test outside of a suite');
    }
    
    const test = {
      name,
      callback,
      skip,
      suite: this.currentSuite
    };
    
    this.suites[this.currentSuite].tests.push(test);
    this.tests.push(test);
  }
  
  /**
   * Skip a test
   * @param {string} name - Name of the test
   * @param {Function} callback - Test function
   */
  skip(name, callback) {
    this.test(name, callback, true);
  }
  
  /**
   * Set up a function to run before each test in the current suite
   * @param {Function} callback - Function to run before each test
   */
  beforeEach(callback) {
    if (!this.currentSuite) {
      throw new Error('Cannot set beforeEach outside of a suite');
    }
    
    this.suites[this.currentSuite].beforeEach = callback;
  }
  
  /**
   * Set up a function to run after each test in the current suite
   * @param {Function} callback - Function to run after each test
   */
  afterEach(callback) {
    if (!this.currentSuite) {
      throw new Error('Cannot set afterEach outside of a suite');
    }
    
    this.suites[this.currentSuite].afterEach = callback;
  }
  
  /**
   * Set up a function to run before all tests in the current suite
   * @param {Function} callback - Function to run before all tests
   */
  beforeAll(callback) {
    if (!this.currentSuite) {
      throw new Error('Cannot set beforeAll outside of a suite');
    }
    
    this.suites[this.currentSuite].beforeAll = callback;
  }
  
  /**
   * Set up a function to run after all tests in the current suite
   * @param {Function} callback - Function to run after all tests
   */
  afterAll(callback) {
    if (!this.currentSuite) {
      throw new Error('Cannot set afterAll outside of a suite');
    }
    
    this.suites[this.currentSuite].afterAll = callback;
  }
  
  /**
   * Run all tests
   * @returns {Promise<Object>} Test results
   */
  async runAll() {
    console.log('Running all tests...');
    
    this.startTime = performance.now();
    this.results = {
      passed: 0,
      failed: 0,
      skipped: 0,
      total: this.tests.length,
      suites: {}
    };
    
    // Run each suite
    for (const suiteName in this.suites) {
      const suite = this.suites[suiteName];
      
      console.group(`Suite: ${suiteName}`);
      
      // Initialize suite results
      this.results.suites[suiteName] = {
        passed: 0,
        failed: 0,
        skipped: 0,
        total: suite.tests.length,
        tests: {}
      };
      
      // Run beforeAll
      if (suite.beforeAll) {
        try {
          await suite.beforeAll();
        } catch (error) {
          console.error(`Error in beforeAll for suite ${suiteName}:`, error);
          // Skip all tests in this suite
          for (const test of suite.tests) {
            this.results.skipped++;
            this.results.suites[suiteName].skipped++;
            this.results.suites[suiteName].tests[test.name] = {
              status: 'skipped',
              error: `Suite setup failed: ${error.message}`
            };
            console.log(`  ⚠️ SKIPPED: ${test.name} (suite setup failed)`);
          }
          continue;
        }
      }
      
      // Run each test in the suite
      for (const test of suite.tests) {
        if (test.skip) {
          this.results.skipped++;
          this.results.suites[suiteName].skipped++;
          this.results.suites[suiteName].tests[test.name] = {
            status: 'skipped'
          };
          console.log(`  ⚠️ SKIPPED: ${test.name}`);
          continue;
        }
        
        // Run beforeEach
        if (suite.beforeEach) {
          try {
            await suite.beforeEach();
          } catch (error) {
            console.error(`Error in beforeEach for test ${test.name}:`, error);
            this.results.failed++;
            this.results.suites[suiteName].failed++;
            this.results.suites[suiteName].tests[test.name] = {
              status: 'failed',
              error: `Test setup failed: ${error.message}`
            };
            console.log(`  ❌ FAILED: ${test.name} (test setup failed)`);
            continue;
          }
        }
        
        // Run the test
        try {
          await test.callback();
          this.results.passed++;
          this.results.suites[suiteName].passed++;
          this.results.suites[suiteName].tests[test.name] = {
            status: 'passed'
          };
          console.log(`  ✅ PASSED: ${test.name}`);
        } catch (error) {
          this.results.failed++;
          this.results.suites[suiteName].failed++;
          this.results.suites[suiteName].tests[test.name] = {
            status: 'failed',
            error: error.message
          };
          console.log(`  ❌ FAILED: ${test.name}`);
          console.error(`    Error: ${error.message}`);
        }
        
        // Run afterEach
        if (suite.afterEach) {
          try {
            await suite.afterEach();
          } catch (error) {
            console.error(`Error in afterEach for test ${test.name}:`, error);
          }
        }
      }
      
      // Run afterAll
      if (suite.afterAll) {
        try {
          await suite.afterAll();
        } catch (error) {
          console.error(`Error in afterAll for suite ${suiteName}:`, error);
        }
      }
      
      console.groupEnd();
    }
    
    this.endTime = performance.now();
    this.results.duration = this.endTime - this.startTime;
    
    // Log the results
    this.logResults();
    
    return this.results;
  }
  
  /**
   * Log the test results
   */
  logResults() {
    console.group('Test Results');
    console.log(`Total: ${this.results.total}`);
    console.log(`Passed: ${this.results.passed}`);
    console.log(`Failed: ${this.results.failed}`);
    console.log(`Skipped: ${this.results.skipped}`);
    console.log(`Duration: ${this.results.duration.toFixed(2)}ms`);
    console.groupEnd();
  }
  
  /**
   * Create assertion functions
   * @returns {Object} Assertion functions
   */
  createAssertions() {
    return {
      /**
       * Assert that a condition is true
       * @param {boolean} condition - The condition to check
       * @param {string} message - Error message if the assertion fails
       */
      assertTrue: (condition, message = 'Expected condition to be true') => {
        if (!condition) {
          throw new Error(message);
        }
      },
      
      /**
       * Assert that a condition is false
       * @param {boolean} condition - The condition to check
       * @param {string} message - Error message if the assertion fails
       */
      assertFalse: (condition, message = 'Expected condition to be false') => {
        if (condition) {
          throw new Error(message);
        }
      },
      
      /**
       * Assert that two values are equal
       * @param {*} actual - The actual value
       * @param {*} expected - The expected value
       * @param {string} message - Error message if the assertion fails
       */
      assertEqual: (actual, expected, message = `Expected ${actual} to equal ${expected}`) => {
        if (actual !== expected) {
          throw new Error(message);
        }
      },
      
      /**
       * Assert that two values are not equal
       * @param {*} actual - The actual value
       * @param {*} expected - The expected value
       * @param {string} message - Error message if the assertion fails
       */
      assertNotEqual: (actual, expected, message = `Expected ${actual} not to equal ${expected}`) => {
        if (actual === expected) {
          throw new Error(message);
        }
      },
      
      /**
       * Assert that a value is defined
       * @param {*} value - The value to check
       * @param {string} message - Error message if the assertion fails
       */
      assertDefined: (value, message = 'Expected value to be defined') => {
        if (value === undefined) {
          throw new Error(message);
        }
      },
      
      /**
       * Assert that a value is undefined
       * @param {*} value - The value to check
       * @param {string} message - Error message if the assertion fails
       */
      assertUndefined: (value, message = 'Expected value to be undefined') => {
        if (value !== undefined) {
          throw new Error(message);
        }
      },
      
      /**
       * Assert that a function throws an error
       * @param {Function} fn - The function to check
       * @param {string} message - Error message if the assertion fails
       */
      assertThrows: (fn, message = 'Expected function to throw an error') => {
        try {
          fn();
          throw new Error(message);
        } catch (error) {
          if (error.message === message) {
            throw error;
          }
        }
      }
    };
  }
}

// Create a singleton instance
const monoTestFramework = new MonoTestFramework();
const assert = monoTestFramework.createAssertions();

// Export the test framework
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { monoTestFramework, assert };
} else {
  window.monoTestFramework = monoTestFramework;
  window.assert = assert;
}
