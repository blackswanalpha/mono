// Standalone API testing functionality
console.log('API Test module loaded');

// Function to test the API
async function testApi() {
  console.log('API-TEST: Testing API...');
  const resultDiv = document.getElementById('api-test-result');
  if (!resultDiv) {
    console.error('API-TEST: Result div not found');
    return;
  }

  resultDiv.innerHTML = 'Testing API...';

  try {
    // Check if window.api exists
    if (!window.api) {
      console.error('API-TEST: window.api is undefined');
      resultDiv.innerHTML += '<br>❌ ERROR: window.api is undefined';
      return;
    }

    // Get system info
    if (typeof window.api.getSystemInfo === 'function') {
      const sysInfo = window.api.getSystemInfo();
      resultDiv.innerHTML += '<br>✅ System info retrieved:';
      resultDiv.innerHTML += `<br>Node: ${sysInfo.nodeVersion}`;
      resultDiv.innerHTML += `<br>Electron: ${sysInfo.electronVersion}`;
      resultDiv.innerHTML += `<br>Chrome: ${sysInfo.chromeVersion}`;
      resultDiv.innerHTML += `<br>Platform: ${sysInfo.platform}`;
      resultDiv.innerHTML += `<br>Architecture: ${sysInfo.arch}`;
    } else {
      resultDiv.innerHTML += '<br>❌ getSystemInfo method not found';
    }

    // Log available API methods
    const apiMethods = Object.keys(window.api);
    console.log('API-TEST: Available API methods:', apiMethods);
    resultDiv.innerHTML += '<br><br>✅ API methods found: ' + apiMethods.join(', ');

    // Test the API's test method
    if (typeof window.api.testApi === 'function') {
      resultDiv.innerHTML += '<br><br>Testing API test method...';
      try {
        const testResult = await window.api.testApi();
        console.log('API-TEST: Test result:', testResult);

        if (testResult.success) {
          resultDiv.innerHTML += '<br>✅ API test successful!';
          if (testResult.result) {
            resultDiv.innerHTML += `<br>Message: ${testResult.result.message}`;
            resultDiv.innerHTML += `<br>Timestamp: ${testResult.result.timestamp}`;
          }
        } else {
          resultDiv.innerHTML += `<br>❌ API test failed: ${testResult.error}`;
        }
      } catch (error) {
        console.error('API-TEST: Error testing API:', error);
        resultDiv.innerHTML += `<br>❌ API test error: ${error.message}`;
      }
    }

    // Check if openFolder method exists
    if (typeof window.api.openFolder !== 'function') {
      console.error('API-TEST: window.api.openFolder is not a function');
      resultDiv.innerHTML += '<br>❌ ERROR: window.api.openFolder is not a function';
      return;
    }

    resultDiv.innerHTML += '<br>✅ openFolder method found';

    // Create test buttons for various API functions
    resultDiv.innerHTML += '<br><br>Test API functions:';
    const buttonContainer = document.createElement('div');
    buttonContainer.style.marginTop = '10px';
    buttonContainer.style.display = 'flex';
    buttonContainer.style.flexDirection = 'column';
    buttonContainer.style.gap = '5px';

    // Add folder dialog test button
    const folderButton = createTestButton('Test Open Folder', async () => {
      try {
        resultDiv.innerHTML += '<br>Calling window.api.openFolder()...';
        const result = await window.api.openFolder();

        if (result) {
          resultDiv.innerHTML += `<br>✅ SUCCESS: Selected folder: ${result}`;
        } else {
          resultDiv.innerHTML += '<br>ℹ️ INFO: No folder selected or dialog canceled';
        }
      } catch (error) {
        console.error('API-TEST: Error calling openFolder:', error);
        resultDiv.innerHTML += `<br>❌ ERROR: ${error.message}`;
      }
    });

    // Add file dialog test button
    const fileButton = createTestButton('Test Open File', async () => {
      try {
        resultDiv.innerHTML += '<br>Calling window.api.openFile()...';
        const result = await window.api.openFile();

        if (result) {
          resultDiv.innerHTML += `<br>✅ SUCCESS: Selected file: ${result}`;
        } else {
          resultDiv.innerHTML += '<br>ℹ️ INFO: No file selected or dialog canceled';
        }
      } catch (error) {
        console.error('API-TEST: Error calling openFile:', error);
        resultDiv.innerHTML += `<br>❌ ERROR: ${error.message}`;
      }
    });

    // Add save dialog test button
    const saveButton = createTestButton('Test Save File As', async () => {
      try {
        resultDiv.innerHTML += '<br>Calling window.api.saveFileAs()...';
        const result = await window.api.saveFileAs('untitled.mono');

        if (result) {
          resultDiv.innerHTML += `<br>✅ SUCCESS: Save path: ${result}`;
        } else {
          resultDiv.innerHTML += '<br>ℹ️ INFO: Save canceled';
        }
      } catch (error) {
        console.error('API-TEST: Error calling saveFileAs:', error);
        resultDiv.innerHTML += `<br>❌ ERROR: ${error.message}`;
      }
    });

    // Add buttons to container
    buttonContainer.appendChild(folderButton);
    buttonContainer.appendChild(fileButton);
    buttonContainer.appendChild(saveButton);

    // Add container to result div
    resultDiv.appendChild(buttonContainer);

  } catch (error) {
    console.error('API-TEST: Error testing API:', error);
    resultDiv.innerHTML += `<br>❌ ERROR: ${error.message}`;
  }
}

// Helper function to create a test button
function createTestButton(text, clickHandler) {
  const button = document.createElement('button');
  button.textContent = text;
  button.style.backgroundColor = '#007acc';
  button.style.color = 'white';
  button.style.border = 'none';
  button.style.padding = '5px 10px';
  button.style.borderRadius = '3px';
  button.style.cursor = 'pointer';
  button.addEventListener('click', clickHandler);
  return button;
}

// Initialize the test button as soon as the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  console.log('API-TEST: Setting up test button event listener');

  // Add event listener to the test API button
  const setupTestButton = () => {
    const testApiBtn = document.getElementById('test-api-btn');
    if (testApiBtn) {
      console.log('API-TEST: Test button found, adding event listener');
      testApiBtn.addEventListener('click', () => {
        console.log('API-TEST: Test button clicked');
        testApi();
      });
    } else {
      console.warn('API-TEST: Test button not found, will retry');
      // Retry after a short delay
      setTimeout(setupTestButton, 500);
    }
  };

  // Start the setup process
  setupTestButton();
});

// Export the test function for use in other modules
window.testApi = testApi;

console.log('API Test module initialization complete');
