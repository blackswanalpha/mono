#!/bin/bash

# Install UI Kit to my-switch-app

echo "Installing UI Kit to my-switch-app..."

# Create directories
mkdir -p my-switch-app/src/components/ui
mkdir -p my-switch-app/src/static/css/ui
mkdir -p my-switch-app/src/kits

# Copy components
echo "Copying components..."
cp -r switch-ui-kit/components/* my-switch-app/src/components/ui/

# Copy styles
echo "Copying styles..."
cp -r switch-ui-kit/styles/* my-switch-app/src/static/css/ui/

# Copy kit manifest
echo "Copying kit manifest..."
cp switch-ui-kit/kit.mono my-switch-app/src/kits/ui-kit.mono

echo "Installation complete!"
