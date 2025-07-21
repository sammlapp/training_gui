#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Testing Python environment...');

const envPath = path.join(__dirname, 'python-env');
const pythonPath = path.join(envPath, 'bin', 'python');

if (!fs.existsSync(pythonPath)) {
    console.log('❌ Python environment not found. Run npm run build:python-env first.');
    process.exit(1);
}

console.log('✅ Python environment found at:', pythonPath);

// Test Python and import key packages
const testScript = `
import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")

try:
    import torch
    print(f"✅ PyTorch version: {torch.__version__}")
except ImportError:
    print("❌ PyTorch not found")

try:
    import opensoundscape
    print(f"✅ OpenSoundscape version: {opensoundscape.__version__}")
except ImportError:
    print("❌ OpenSoundscape not found")

try:
    import timm
    print(f"✅ timm version: {timm.__version__}")
except ImportError:
    print("❌ timm not found")

try:
    import bioacoustics_model_zoo
    print("✅ bioacoustics_model_zoo imported successfully")
except ImportError:
    print("❌ bioacoustics_model_zoo not found")

try:
    import lightning
    print(f"✅ Lightning version: {lightning.__version__}")
except ImportError:
    print("❌ Lightning not found")

try:
    import aiohttp
    print(f"✅ aiohttp version: {aiohttp.__version__}")
except ImportError:
    print("❌ aiohttp not found")

try:
    import aiohttp_cors
    print("✅ aiohttp-cors imported successfully")
except ImportError:
    print("❌ aiohttp-cors not found")

print("\\n🎉 Python environment test completed!")
`;

const python = spawn(pythonPath, ['-c', testScript]);

python.stdout.on('data', (data) => {
    console.log(data.toString());
});

python.stderr.on('data', (data) => {
    console.error(data.toString());
});

python.on('close', (code) => {
    if (code === 0) {
        console.log('✅ Python environment test passed!');
    } else {
        console.log('❌ Python environment test failed!');
    }
    process.exit(code);
});