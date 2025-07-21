2#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔧 Fixing HTTP server dependencies...');

const envPath = path.join(__dirname, 'python-env');
const pythonPath = path.join(envPath, 'bin', 'python');

if (!fs.existsSync(pythonPath)) {
    console.log('❌ Python environment not found. Run npm run build:python-env first.');
    process.exit(1);
}

console.log('✅ Python environment found, installing HTTP server dependencies...');

try {
    // Install aiohttp and aiohttp-cors directly into the existing environment
    console.log('📦 Installing aiohttp...');
    execSync(`"${pythonPath}" -m pip install aiohttp`, { stdio: 'inherit' });
    
    console.log('📦 Installing aiohttp-cors...');
    execSync(`"${pythonPath}" -m pip install aiohttp-cors`, { stdio: 'inherit' });
    
    console.log('✅ HTTP server dependencies installed successfully!');
    console.log('🧪 Testing imports...');
    
    // Test that the packages can be imported
    const testScript = `
import aiohttp
import aiohttp_cors
print("✅ All HTTP server dependencies are working!")
print(f"aiohttp version: {aiohttp.__version__}")
`;
    
    execSync(`"${pythonPath}" -c "${testScript}"`, { stdio: 'inherit' });
    
    console.log('\n🎉 Fix completed! Audio and spectrograms should now load in the review tab.');
    
} catch (error) {
    console.error('❌ Error installing HTTP server dependencies:', error);
    console.log('\n💡 Try rebuilding the Python environment with:');
    console.log('   rm -rf python-env');
    console.log('   npm run build:python-env-fast');
    process.exit(1);
}