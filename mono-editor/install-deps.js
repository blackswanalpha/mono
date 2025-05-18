// Script to install required dependencies for Mono Editor
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Mono Editor Dependency Installer');
console.log('================================');

// Check if package.json exists
const packageJsonPath = path.join(__dirname, 'package.json');
if (!fs.existsSync(packageJsonPath)) {
  console.error('Error: package.json not found!');
  process.exit(1);
}

// Read package.json
let packageJson;
try {
  packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  console.log('Successfully read package.json');
} catch (error) {
  console.error('Error reading package.json:', error.message);
  process.exit(1);
}

// Get dependencies
const dependencies = packageJson.dependencies || {};
const devDependencies = packageJson.devDependencies || {};

console.log('\nInstalling dependencies...');
console.log('------------------------');

// Install dependencies
try {
  console.log('Installing production dependencies...');
  execSync('npm install', { stdio: 'inherit' });
  
  console.log('\nVerifying jQuery installation...');
  const jqueryPath = path.join(__dirname, 'node_modules', 'jquery', 'dist', 'jquery.min.js');
  if (!fs.existsSync(jqueryPath)) {
    console.log('jQuery not found, installing separately...');
    execSync('npm install jquery@3.7.1', { stdio: 'inherit' });
  } else {
    console.log('jQuery is installed correctly.');
  }
  
  console.log('\nVerifying Bootstrap installation...');
  const bootstrapPath = path.join(__dirname, 'node_modules', 'bootstrap', 'dist', 'js', 'bootstrap.min.js');
  if (!fs.existsSync(bootstrapPath)) {
    console.log('Bootstrap not found, installing separately...');
    execSync('npm install bootstrap@5.3.2', { stdio: 'inherit' });
  } else {
    console.log('Bootstrap is installed correctly.');
  }
  
  console.log('\nVerifying Popper.js installation...');
  const popperPath = path.join(__dirname, 'node_modules', 'popper.js', 'dist', 'umd', 'popper.min.js');
  if (!fs.existsSync(popperPath)) {
    console.log('Popper.js not found, installing separately...');
    execSync('npm install popper.js@1.16.1', { stdio: 'inherit' });
  } else {
    console.log('Popper.js is installed correctly.');
  }
  
  console.log('\nAll dependencies installed successfully!');
} catch (error) {
  console.error('\nError installing dependencies:', error.message);
  console.log('\nTrying to install critical dependencies individually...');
  
  try {
    execSync('npm install jquery@3.7.1 bootstrap@5.3.2 popper.js@1.16.1 electron-store@8.1.0', { stdio: 'inherit' });
    console.log('Critical dependencies installed successfully!');
  } catch (individualError) {
    console.error('Error installing critical dependencies:', individualError.message);
    console.log('\nPlease try to install dependencies manually:');
    console.log('npm install jquery@3.7.1 bootstrap@5.3.2 popper.js@1.16.1 electron-store@8.1.0');
  }
}

console.log('\nSetup complete! You can now run the Mono Editor with:');
console.log('npm start');
