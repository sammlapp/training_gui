import { useState, useEffect } from 'react';
import { getBackendUrl } from '../utils/backendConfig';

/**
 * React hook to get the backend URL
 * Handles the async call and caching properly
 */
export function useBackendUrl() {
  const [backendUrl, setBackendUrl] = useState(null); // Start with null - will be fetched

  useEffect(() => {
    getBackendUrl().then(url => {
      setBackendUrl(url);
    }).catch(error => {
      console.error('Failed to get backend URL:', error);
      // Fallback to default port only if the fetch fails
      setBackendUrl('http://localhost:8000');
    });
  }, []);

  return backendUrl || 'http://localhost:8000'; // Return fallback if still loading
}
