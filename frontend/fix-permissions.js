#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔧 Fixing Python environment permissions...');

const envPath = path.join(__dirname, 'python-env');

if (!fs.existsSync(envPath)) {
    console.log('✅ Python environment not found, no permissions to fix.');
    process.exit(0);
}

try {
    // Fix permissions on all files in the Python environment
    console.log('📝 Setting read permissions on all files...');
    execSync(`find "${envPath}" -type f -exec chmod 644 {} +`, { stdio: 'inherit' });
    
    console.log('📁 Setting execute permissions on directories...');
    execSync(`find "${envPath}" -type d -exec chmod 755 {} +`, { stdio: 'inherit' });
    
    console.log('🔧 Setting execute permissions on Python binaries...');
    const binPath = path.join(envPath, 'bin');
    if (fs.existsSync(binPath)) {
        execSync(`find "${binPath}" -type f -name "python*" -exec chmod 755 {} +`, { stdio: 'inherit' });
        execSync(`find "${binPath}" -type f -name "pip*" -exec chmod 755 {} +`, { stdio: 'inherit' });
    }
    
    // Remove problematic config files that cause permission issues
    console.log('🗑️  Removing problematic config files...');
    const problematicFiles = [
        'bin/icu-config',
        'bin/krb5-config',
        'bin/pcre-config',
        'bin/pcre2-config',
        'bin/xml2-config',
        'bin/xslt-config',
        'bin/curl-config',
        'bin/libpng-config',
        'bin/freetype-config'
    ];
    
    problematicFiles.forEach(file => {
        const filePath = path.join(envPath, file);
        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
            console.log(`   Removed: ${file}`);
        }
    });
    
    // Remove unnecessary directories that cause issues
    console.log('🗑️  Removing unnecessary directories...');
    const unnecessaryDirs = [
        'share/man',
        'share/doc',
        'share/info',
        'include',
        'ssl/man'
    ];
    
    unnecessaryDirs.forEach(dir => {
        const dirPath = path.join(envPath, dir);
        if (fs.existsSync(dirPath)) {
            fs.rmSync(dirPath, { recursive: true, force: true });
            console.log(`   Removed: ${dir}`);
        }
    });
    
    console.log('✅ Python environment permissions fixed!');
    
} catch (error) {
    console.error('❌ Error fixing permissions:', error);
    process.exit(1);
}