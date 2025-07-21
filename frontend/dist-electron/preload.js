const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // File selection
  selectFiles: () => ipcRenderer.invoke('select-files'),
  selectFolder: () => ipcRenderer.invoke('select-folder'),
  selectCSVFiles: () => ipcRenderer.invoke('select-csv-files'),
  saveFile: (defaultName) => ipcRenderer.invoke('save-file', defaultName),
  writeFile: (filePath, content) => ipcRenderer.invoke('write-file', filePath, content),

  // Python script execution
  runPythonScript: (scriptPath, args, processId) => 
    ipcRenderer.invoke('run-python-script', scriptPath, args, processId),
  killPythonProcess: (processId) => 
    ipcRenderer.invoke('kill-python-process', processId),
  testPythonPath: () => ipcRenderer.invoke('test-python-path'),

  // Audio processing
  createAudioClips: (filePath, startTime, endTime, settings) =>
    ipcRenderer.invoke('create-audio-clips', filePath, startTime, endTime, settings),

  // Python output listener
  onPythonOutput: (callback) => {
    ipcRenderer.on('python-output', callback);
  },
  removePythonOutputListener: (callback) => {
    ipcRenderer.removeListener('python-output', callback);
  }
});