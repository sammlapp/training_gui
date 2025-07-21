#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🧪 Building minimal test package...');

function runCommand(command, cwd = '.') {
    console.log(`Running: ${command}`);
    try {
        execSync(command, { 
            stdio: 'inherit', 
            cwd: cwd,
            env: { ...process.env }
        });
    } catch (error) {
        console.error(`❌ Command failed: ${command}`);
        process.exit(1);
    }
}

try {
    console.log('1. Building minimal Python server...');
    runCommand('rm -rf dist build', 'backend');
    runCommand('"/Users/SML161/training_gui/backend/pyinstaller-venv/bin/pyinstaller" --onefile --clean minimal_server.py', 'backend');
    
    console.log('2. Copying to frontend...');
    runCommand('mkdir -p frontend/python-dist');
    runCommand('cp backend/dist/minimal_server frontend/python-dist/');
    
    console.log('3. Building React frontend...');
    runCommand('npm run build', 'frontend');
    
    console.log('4. Building Electron files...');
    runCommand('npm run build:electron', 'frontend');
    
    console.log('5. Building Electron app...');
    runCommand('npx electron-builder --mac', 'frontend');
    
    console.log('✅ Minimal test build completed!');
    console.log('📁 Find your app in: dist/mac-arm64/Electron.app');
    
    // Test if executable exists in built app
    const appPath = 'dist/mac-arm64/Electron.app';
    if (fs.existsSync(appPath)) {
        console.log('\n🔍 Checking app bundle structure...');
        runCommand(`find "${appPath}" -name "minimal_server" -type f || echo "❌ minimal_server not found in app bundle"`);
        runCommand(`find "${appPath}" -name "python-dist" -type d || echo "❌ python-dist not found in app bundle"`);
    }
    
} catch (error) {
    console.error('❌ Build failed:', error.message);
    process.exit(1);
}