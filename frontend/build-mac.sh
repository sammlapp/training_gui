#!/bin/bash

# Bioacoustics Training GUI - Mac Build Script
# This script builds a distributable macOS app with bundled Python environment

set -e

echo "🚀 Building Bioacoustics Training GUI for macOS..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is for macOS builds only"
    exit 1
fi

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js first."
    exit 1
fi

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ conda is not installed. Please install Miniconda or Anaconda first."
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

echo "🏗️  Building React application..."
npm run build

echo "⚙️  Building Electron files..."
npm run build:electron

echo "🐍 Building Python environment..."
# Only build if it doesn't exist
if [ ! -d "python-env" ]; then
    npm run build:python-env
else
    echo "Python environment already exists, skipping..."
fi

echo "📱 Building macOS application..."
npm run dist:mac

echo "✅ Build complete!"
echo "📁 Find your app in the ../dist directory"

# Show build output
if [ -d "../dist" ]; then
    echo ""
    echo "Build artifacts:"
    ls -la ../dist/
fi

echo ""
echo "You can now distribute the .dmg file to users."