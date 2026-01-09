import { useState, useEffect } from 'react';
import { getBackendUrl, CONFIGURED_BACKEND_PORT } from '../utils/backendConfig';

/**
 * React hook to get the backend URL
 * Handles the async call and caching properly
 */
export function useBackendUrl() {
  // Start with configured/default port so first render already uses the
  // correct server-mode port (rather than hardcoding 8000).
  const [backendUrl, setBackendUrl] = useState(`http://localhost:${CONFIGURED_BACKEND_PORT}`);

  useEffect(() => {
    getBackendUrl().then(url => {
      setBackendUrl(url);
    }).catch(error => {
      console.error('Failed to get backend URL:', error);
      // Fallback to configured/default port only if the fetch fails
      setBackendUrl(`http://localhost:${CONFIGURED_BACKEND_PORT}`);
    });
  }, []);

  // Always use the resolved or configured/default port (no hardcoded 8000).
  return backendUrl || `http://localhost:${CONFIGURED_BACKEND_PORT}`;
}
