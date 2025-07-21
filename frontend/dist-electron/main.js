const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');

// Development/production detection
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

// HTTP Server management
let httpServerProcess = null;
const HTTP_SERVER_PORT = 8000;

let mainWindow;

// Helper function to get backend scripts path
function getBackendScriptsPath() {
  if (isDev) {
    // In development, backend is in the parent directory
    return path.join(__dirname, '../../backend/scripts');
  } else {
    // In production, backend is in resources
    return path.join(process.resourcesPath, 'backend', 'scripts');
  }
}

// Helper function to get bundled Python executable path
function getBundledPythonExecutable(scriptName = 'minimal_server') {
  if (isDev) {
    // In development, check if python-dist exists in the project
    const devExecutablePath = path.join(__dirname, '../python-dist', scriptName);
    if (fs.existsSync(devExecutablePath)) {
      return devExecutablePath;
    }
    // Fallback to backend directory for development
    const devBackendPath = path.join(__dirname, '../../backend/dist', scriptName);
    if (fs.existsSync(devBackendPath)) {
      return devBackendPath;
    }
  } else {
    // In production, Python executables are bundled with the app
    const resourcesPath = process.resourcesPath;
    const executablePath = path.join(resourcesPath, 'python-dist', scriptName);
    
    if (fs.existsSync(executablePath)) {
      return executablePath;
    }
  }
  
  return null;
}

// Helper function to get bundled Python path (legacy)
function getBundledPythonPath() {
  return getBundledPythonExecutable('python');
}

// Helper function to get the best way to run a Python script
function getPythonCommand(scriptName) {
  // Try to get PyInstaller executable first
  const executablePath = getBundledPythonExecutable(scriptName);
  
  if (executablePath && !executablePath.includes('python-env')) {
    // Use PyInstaller executable
    return {
      command: executablePath,
      needsScript: false
    };
  } else {
    // Fallback to Python + script
    const pythonPath = getCondaPythonPath();
    return {
      command: pythonPath,
      needsScript: true,
      scriptPath: path.join(getBackendScriptsPath(), `${scriptName}.py`)
    };
  }
}

// Python path detection
function getCondaPythonPath() {
  // First, try to find bundled Python environment
  const bundledPythonPath = getBundledPythonPath();
  if (bundledPythonPath) {
    console.log(`Using bundled Python at: ${bundledPythonPath}`);
    return bundledPythonPath;
  }
  
  // Fallback to system conda environments
  const homeDir = os.homedir();
  const possiblePaths = [
    // User's exact path (highest priority)
    '/Users/SML161/miniconda3/envs/train_gui/bin/python',
    // Common patterns for train_gui environment
    path.join(homeDir, 'miniconda3', 'envs', 'train_gui', 'bin', 'python'),
    path.join(homeDir, 'anaconda3', 'envs', 'train_gui', 'bin', 'python'),
    path.join(homeDir, 'miniforge3', 'envs', 'train_gui', 'bin', 'python'),
    '/opt/miniconda3/envs/train_gui/bin/python',
    '/opt/anaconda3/envs/train_gui/bin/python',
    // Also try training_gui in case the environment gets renamed
    path.join(homeDir, 'miniconda3', 'envs', 'training_gui', 'bin', 'python'),
    path.join(homeDir, 'anaconda3', 'envs', 'training_gui', 'bin', 'python'),
    path.join(homeDir, 'miniforge3', 'envs', 'training_gui', 'bin', 'python'),
    '/opt/miniconda3/envs/training_gui/bin/python',
    '/opt/anaconda3/envs/training_gui/bin/python',
    'python3' // Fallback to system python
  ];
  
  console.log('Searching for conda python in these paths:');
  for (const pythonPath of possiblePaths) {
    console.log(`  Checking: ${pythonPath}`);
    if (fs.existsSync(pythonPath)) {
      console.log(`  Found Python at: ${pythonPath}`);
      return pythonPath;
    }
  }
  
  console.log('No conda python found, falling back to system python');
  return 'python3'; // Ultimate fallback
}

function createWindow() {
  console.log('=== ELECTRON STARTUP ===');
  console.log('NODE_ENV:', process.env.NODE_ENV);
  console.log('isDev:', isDev);
  console.log('app.isPackaged:', app.isPackaged);
  
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load the app
  const startUrl = isDev 
    ? 'http://localhost:3000' 
    : `file://${path.join(__dirname, '../build/index.html')}`;
  
  console.log('Loading URL:', startUrl);
  mainWindow.loadURL(startUrl);

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Start HTTP server for audio processing
  startHttpServer();
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});


// Start HTTP server for audio processing
function startHttpServer() {
  if (httpServerProcess) {
    console.log('HTTP server already running');
    return;
  }
  try {
    // Try to use PyInstaller executable first (minimal server for testing)
    const minimalServerExecutable = getBundledPythonExecutable('minimal_server');
    let command, args;
    
    if (minimalServerExecutable) {
      // Use minimal PyInstaller executable for testing
      command = minimalServerExecutable;
      args = ['--port', HTTP_SERVER_PORT.toString()];
      console.log(`Starting minimal HTTP server (PyInstaller): ${command} ${args.join(' ')}`);
    } else {
      // Fallback to Python + script
      const pythonPath = getCondaPythonPath();
      const serverScriptPath = path.join(getBackendScriptsPath(), 'http_server.py');
      command = pythonPath;
      args = [serverScriptPath, '--port', HTTP_SERVER_PORT.toString()];
      console.log(`Starting HTTP server (Python): ${command} ${args.join(' ')}`);
    }
    
    httpServerProcess = spawn(command, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: getBackendScriptsPath()
    });
    
    httpServerProcess.stdout.on('data', (data) => {
      console.log(`HTTP Server stdout: ${data}`);
    });
    
    httpServerProcess.stderr.on('data', (data) => {
      console.error(`HTTP Server stderr: ${data}`);
    });
    
    httpServerProcess.on('close', (code) => {
      console.log(`HTTP server process exited with code ${code}`);
      httpServerProcess = null;
    });
    
  } catch (error) {
    console.error('Failed to start HTTP server:', error);
  }
}

// Stop HTTP server
function stopHttpServer() {
  if (httpServerProcess) {
    httpServerProcess.kill();
    httpServerProcess = null;
    console.log('HTTP server stopped');
  }
}

// Clean up on app exit
app.on('before-quit', () => {
  stopHttpServer();
});

// IPC handlers
const pythonProcesses = new Map();

ipcMain.handle('select-files', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: [
      { name: 'Audio Files', extensions: ['wav', 'mp3', 'flac', 'ogg', 'm4a'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result.filePaths;
});

ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  return result.filePaths[0];
});

ipcMain.handle('select-csv-files', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result.filePaths;
});

ipcMain.handle('save-file', async (event, defaultName) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultName,
    filters: [
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result.filePath;
});

ipcMain.handle('run-python-script', async (event, scriptPath, args, processId) => {
  return new Promise((resolve, reject) => {
    // Get script name without extension
    const scriptName = path.basename(scriptPath, '.py');
    const pythonCmd = getPythonCommand(scriptName);
    
    let command, commandArgs;
    if (pythonCmd.needsScript) {
      command = pythonCmd.command;
      commandArgs = [pythonCmd.scriptPath, ...args];
    } else {
      command = pythonCmd.command;
      commandArgs = args;
    }
    
    console.log(`Running: ${command} ${commandArgs.join(' ')}`);
    
    const process = spawn(command, commandArgs);
    pythonProcesses.set(processId, process);
    
    let stdout = '';
    let stderr = '';
    
    process.stdout.on('data', (data) => {
      const output = data.toString();
      stdout += output;
      // Send progress updates to renderer
      mainWindow.webContents.send('python-output', { 
        processId, 
        type: 'stdout', 
        data: output 
      });
    });
    
    process.stderr.on('data', (data) => {
      const output = data.toString();
      stderr += output;
      mainWindow.webContents.send('python-output', { 
        processId, 
        type: 'stderr', 
        data: output 
      });
    });
    
    process.on('close', (code) => {
      pythonProcesses.delete(processId);
      if (code === 0) {
        resolve({ stdout, stderr, code });
      } else {
        reject(new Error(`Python process exited with code ${code}: ${stderr}`));
      }
    });
    
    process.on('error', (error) => {
      pythonProcesses.delete(processId);
      reject(error);
    });
  });
});

ipcMain.handle('kill-python-process', async (event, processId) => {
  const process = pythonProcesses.get(processId);
  if (process) {
    process.kill();
    pythonProcesses.delete(processId);
    return true;
  }
  return false;
});

ipcMain.handle('test-python-path', async () => {
  const pythonPath = getCondaPythonPath();
  return {
    pythonPath: pythonPath,
    exists: fs.existsSync(pythonPath),
    homeDir: os.homedir()
  };
});

ipcMain.handle('create-audio-clips', async (event, filePath, startTime, endTime, settings) => {
  return new Promise((resolve, reject) => {
    const pythonCmd = getPythonCommand('create_audio_clips');
    
    const args = [
      '--file', filePath,
      '--start', startTime.toString(),
      '--end', endTime.toString(),
      '--settings', JSON.stringify(settings)
    ];
    
    let command, commandArgs;
    if (pythonCmd.needsScript) {
      command = pythonCmd.command;
      commandArgs = [pythonCmd.scriptPath, ...args];
    } else {
      command = pythonCmd.command;
      commandArgs = args;
    }
    
    console.log(`Creating audio clips: ${command} ${commandArgs.join(' ')}`);
    
    const process = spawn(command, commandArgs);
    
    let stdout = '';
    let stderr = '';
    
    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    process.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (error) {
          reject(new Error(`Failed to parse audio clip result: ${error.message}`));
        }
      } else {
        reject(new Error(`Audio clip creation failed: ${stderr}`));
      }
    });
    
    process.on('error', (error) => {
      reject(error);
    });
  });
});

ipcMain.handle('write-file', async (event, filePath, content) => {
  try {
    fs.writeFileSync(filePath, content, 'utf8');
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});