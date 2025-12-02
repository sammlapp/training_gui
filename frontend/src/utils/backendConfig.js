import { invoke } from '@tauri-apps/api/core';

// Cache for the backend URL
let cachedBackendUrl = null;

/**
 * Get the backend server URL dynamically
 * For Tauri apps, this calls the Rust backend to get the actual port
 * For Electron/browser, falls back to localhost:8000
 */
export async function getBackendUrl() {
  // Return cached value if available
  if (cachedBackendUrl) {
    return cachedBackendUrl;
  }

  // Check if running in Tauri
  const isTauri = typeof window !== 'undefined' &&
                  (window.__TAURI__ || window.__TAURI_INTERNALS__);

  if (isTauri) {
    try {
      console.log('[backendConfig] Invoking get_backend_port from Tauri...');
      // Get the dynamic port from Tauri backend
      const port = await invoke('get_backend_port');
      cachedBackendUrl = `http://localhost:${port}`;
      console.log(`[backendConfig] ✓ Got backend port from Tauri: ${port}`);
      console.log(`[backendConfig] Backend URL: ${cachedBackendUrl}`);
      return cachedBackendUrl;
    } catch (error) {
      console.error('[backendConfig] ✗ Failed to get backend port from Tauri:', error);
      // Fallback to default port
      cachedBackendUrl = 'http://localhost:8000';
      console.warn('[backendConfig] Falling back to default port 8000');
      return cachedBackendUrl;
    }
  }

  // For Electron or browser mode, use default port
  cachedBackendUrl = 'http://localhost:8000';
  return cachedBackendUrl;
}

/**
 * Clear the cached backend URL (useful for testing or reconnection)
 */
export function clearBackendUrlCache() {
  cachedBackendUrl = null;
}
