#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const FRONTEND_DIR = __dirname;
const BACKEND_DIR = path.join(PROJECT_ROOT, 'backend');
const DIST_DIR = path.join(FRONTEND_DIR, 'python-dist');

console.log('🚀 Building Bioacoustics Training GUI for distribution...');

function runCommand(command, cwd = FRONTEND_DIR) {
    console.log(`Running: ${command}`);
    console.log(`Working directory: ${cwd}`);
    
    try {
        execSync(command, { 
            stdio: 'inherit', 
            cwd: cwd,
            env: { ...process.env }
        });
    } catch (error) {
        console.error(`❌ Command failed: ${command}`);
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}

function buildFrontend() {
    console.log('🏗️  Building React frontend...');
    
    // Install dependencies
    runCommand('npm install');
    
    // Build React app
    runCommand('npm run build');
    
    console.log('✅ Frontend build completed');
}

function buildBackend() {
    console.log('🐍 Building Python backend with PyInstaller...');
    
    // Check if Python is available
    try {
        execSync('python --version', { stdio: 'pipe' });
    } catch (error) {
        console.error('❌ Python not found. Please install Python 3.8 or higher.');
        process.exit(1);
    }
    
    // Clean up existing venv and dist
    const venvPath = path.join(BACKEND_DIR, 'pyinstaller-venv');
    const buildDir = path.join(BACKEND_DIR, 'build');
    const backendDistDir = path.join(BACKEND_DIR, 'dist');
    
    [venvPath, buildDir, backendDistDir, DIST_DIR].forEach(dir => {
        if (fs.existsSync(dir)) {
            console.log(`Cleaning ${dir}...`);
            fs.rmSync(dir, { recursive: true, force: true });
        }
    });
    
    // Create new venv
    console.log('Creating Python virtual environment...');
    runCommand('python -m venv pyinstaller-venv', BACKEND_DIR);
    
    // Install dependencies
    const pythonExe = process.platform === 'win32'
        ? path.join(venvPath, 'Scripts', 'python.exe')
        : path.join(venvPath, 'bin', 'python');
    
    const pipExe = process.platform === 'win32'
        ? path.join(venvPath, 'Scripts', 'pip.exe')
        : path.join(venvPath, 'bin', 'pip');
    
    const pyinstallerExe = process.platform === 'win32'
        ? path.join(venvPath, 'Scripts', 'pyinstaller.exe')
        : path.join(venvPath, 'bin', 'pyinstaller');
    
    console.log('Installing Python dependencies...');
    runCommand(`"${pipExe}" install --upgrade pip setuptools wheel`, BACKEND_DIR);
    runCommand(`"${pipExe}" install pyinstaller`, BACKEND_DIR);
    runCommand(`"${pipExe}" install -r requirements-pyinstaller.txt`, BACKEND_DIR);
    
    // Build with PyInstaller
    console.log('Building executable with PyInstaller...');
    runCommand(`"${pyinstallerExe}" --clean --noconfirm http_server.spec`, BACKEND_DIR);
    
    // Copy to frontend directory
    console.log('Copying executable to frontend directory...');
    fs.mkdirSync(DIST_DIR, { recursive: true });
    
    const sourceDistDir = path.join(BACKEND_DIR, 'dist', 'http_server');
    if (fs.existsSync(sourceDistDir)) {
        fs.cpSync(sourceDistDir, DIST_DIR, { recursive: true });
        console.log('✅ Backend build completed');
    } else {
        console.error('❌ Backend build failed - no output directory found');
        process.exit(1);
    }
}

function buildElectron() {
    console.log('📱 Building Electron application...');
    
    // Build Electron app
    runCommand('npm run electron:build');
    
    console.log('✅ Electron build completed');
}

function main() {
    try {
        console.log('Starting complete build process...');
        
        // Build in sequence: frontend -> backend -> electron
        buildFrontend();
        buildBackend(); 
        buildElectron();
        
        console.log('🎉 Build completed successfully!');
        console.log('📁 Find your app in the ../dist directory');
        
        // Show build output
        const outputDir = path.join(PROJECT_ROOT, 'dist');
        if (fs.existsSync(outputDir)) {
            console.log('\nBuild artifacts:');
            const files = fs.readdirSync(outputDir);
            files.forEach(file => {
                const filePath = path.join(outputDir, file);
                const stats = fs.statSync(filePath);
                const size = stats.isDirectory() ? '[DIR]' : `${(stats.size / 1024 / 1024).toFixed(2)}MB`;
                console.log(`  ${file} ${size}`);
            });
        }
        
    } catch (error) {
        console.error('❌ Build failed:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { main };