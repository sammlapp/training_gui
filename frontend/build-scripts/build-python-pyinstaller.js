const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..', '..');
const BACKEND_DIR = path.join(PROJECT_ROOT, 'backend');
const FRONTEND_DIR = path.join(PROJECT_ROOT, 'frontend');
const DIST_DIR = path.join(FRONTEND_DIR, 'python-dist');

console.log('Building Python backend with PyInstaller...');

function runCommand(command, cwd = BACKEND_DIR) {
    console.log(`Running: ${command}`);
    try {
        execSync(command, { 
            stdio: 'inherit', 
            cwd: cwd,
            env: { ...process.env }
        });
    } catch (error) {
        console.error(`Command failed: ${command}`);
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}

function createVirtualEnv() {
    console.log('Creating virtual environment for PyInstaller...');
    
    // Clean up existing venv
    const venvPath = path.join(BACKEND_DIR, 'pyinstaller-venv');
    if (fs.existsSync(venvPath)) {
        console.log('Removing existing virtual environment...');
        fs.rmSync(venvPath, { recursive: true, force: true });
    }
    
    // Create new venv
    runCommand('python -m venv pyinstaller-venv');
    
    // Activate and install requirements
    const activateScript = process.platform === 'win32' 
        ? path.join(venvPath, 'Scripts', 'activate.bat')
        : path.join(venvPath, 'bin', 'activate');
    
    const pythonExe = process.platform === 'win32'
        ? path.join(venvPath, 'Scripts', 'python.exe')
        : path.join(venvPath, 'bin', 'python');
    
    const pipExe = process.platform === 'win32'
        ? path.join(venvPath, 'Scripts', 'pip.exe')
        : path.join(venvPath, 'bin', 'pip');
    
    console.log('Installing requirements...');
    runCommand(`"${pipExe}" install --upgrade pip setuptools wheel`);
    runCommand(`"${pipExe}" install -r requirements-pyinstaller.txt`);
    
    return { pythonExe, pipExe, venvPath };
}

function buildWithPyInstaller(pythonExe, venvPath) {
    console.log('Building executable with PyInstaller...');
    
    const pyinstallerExe = process.platform === 'win32'
        ? path.join(venvPath, 'Scripts', 'pyinstaller.exe')
        : path.join(venvPath, 'bin', 'pyinstaller');
    
    // Clean previous build
    const buildDir = path.join(BACKEND_DIR, 'build');
    const distDir = path.join(BACKEND_DIR, 'dist');
    
    if (fs.existsSync(buildDir)) {
        fs.rmSync(buildDir, { recursive: true, force: true });
    }
    if (fs.existsSync(distDir)) {
        fs.rmSync(distDir, { recursive: true, force: true });
    }
    
    // Build with PyInstaller
    runCommand(`"${pyinstallerExe}" --clean --noconfirm http_server.spec`);
    
    // Copy to frontend directory
    console.log('Copying executable to frontend directory...');
    if (fs.existsSync(DIST_DIR)) {
        fs.rmSync(DIST_DIR, { recursive: true, force: true });
    }
    fs.mkdirSync(DIST_DIR, { recursive: true });
    
    const sourceDistDir = path.join(BACKEND_DIR, 'dist', 'http_server');
    fs.cpSync(sourceDistDir, DIST_DIR, { recursive: true });
    
    console.log('PyInstaller build completed successfully!');
}

function main() {
    try {
        console.log('Starting PyInstaller build process...');
        
        // Check if Python is available
        try {
            execSync('python --version', { stdio: 'pipe' });
        } catch (error) {
            console.error('Python not found. Please install Python 3.8 or higher.');
            process.exit(1);
        }
        
        // Create virtual environment and install dependencies
        const { pythonExe, pipExe, venvPath } = createVirtualEnv();
        
        // Build with PyInstaller
        buildWithPyInstaller(pythonExe, venvPath);
        
        console.log('✅ Python backend built successfully with PyInstaller!');
        console.log(`📦 Executable located at: ${DIST_DIR}`);
        
    } catch (error) {
        console.error('❌ Build failed:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { main };