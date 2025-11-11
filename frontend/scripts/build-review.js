#!/usr/bin/env node

/**
 * Build script for the review-only app
 * Temporarily modifies package.json to point to main-review.js,
 * runs electron-builder, then restores the original package.json
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PACKAGE_JSON_PATH = path.join(__dirname, '..', 'package.json');
const BACKUP_PATH = path.join(__dirname, '..', 'package.json.backup');

function main() {
  console.log('Building review-only app...\n');

  // Read original package.json
  const originalContent = fs.readFileSync(PACKAGE_JSON_PATH, 'utf8');
  const packageJson = JSON.parse(originalContent);

  // Backup original package.json
  fs.writeFileSync(BACKUP_PATH, originalContent);
  console.log('✓ Backed up package.json');

  try {
    // Modify main entry point
    packageJson.main = 'src/main-review.js';
    fs.writeFileSync(PACKAGE_JSON_PATH, JSON.stringify(packageJson, null, 2) + '\n');
    console.log('✓ Modified package.json to use main-review.js\n');

    // Get platform argument if provided
    const platform = process.argv[2] || '--mac';

    // Run electron-builder
    console.log(`Running electron-builder ${platform}...\n`);
    execSync(
      `npx electron-builder ${platform} --config electron-builder-review.json`,
      { stdio: 'inherit', cwd: path.join(__dirname, '..') }
    );

    console.log('\n✓ Build completed successfully');

  } catch (error) {
    console.error('\n✗ Build failed:', error.message);
    process.exitCode = 1;
  } finally {
    // Restore original package.json
    fs.copyFileSync(BACKUP_PATH, PACKAGE_JSON_PATH);
    fs.unlinkSync(BACKUP_PATH);
    console.log('✓ Restored package.json');
  }
}

main();
