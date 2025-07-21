const fs = require('fs');
const path = require('path');

// Create dist-electron directory if it doesn't exist
const distElectronDir = path.join(__dirname, '../dist-electron');
if (!fs.existsSync(distElectronDir)) {
  fs.mkdirSync(distElectronDir, { recursive: true });
}

// Copy main.js and preload.js to dist-electron
const srcDir = path.join(__dirname, '../src');
const filesToCopy = ['main.js', 'preload.js'];

filesToCopy.forEach(file => {
  const srcPath = path.join(srcDir, file);
  const destPath = path.join(distElectronDir, file);
  
  if (fs.existsSync(srcPath)) {
    fs.copyFileSync(srcPath, destPath);
    console.log(`Copied ${file} to dist-electron/`);
  } else {
    console.warn(`Warning: ${file} not found in src/`);
  }
});

console.log('Electron files prepared successfully!');