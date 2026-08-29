import { useState, useEffect, useCallback } from 'react';
import { getHealth } from '../services/api';

/**
 * Hook for managing async API calls with loading, error, and refetch states
 */
export function useApi(apiFunc, autoFetch = true, params = null) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(autoFetch);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (execParams = params) => {
      setLoading(true);
      setError(null);
      try {
        const result = await apiFunc(execParams);
        setData(result);
        return result;
      } catch (err) {
        setError(err.message || 'An unexpected error occurred.');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunc, params]
  );

  useEffect(() => {
    if (autoFetch) {
      execute();
    }
  }, [autoFetch, execute]);

  return { data, loading, error, refetch: execute, execute, setData };
}

/**
 * Hook to poll backend health and provide live connection status
 */
export function useHealth(pollIntervalMs = 15000) {
  const [status, setStatus] = useState('checking'); // 'connected' | 'offline' | 'checking'
  const [lastCheck, setLastCheck] = useState(null);

  const checkHealth = useCallback(async () => {
    try {
      const res = await getHealth();
      if (res && res.status === 'healthy') {
        setStatus('connected');
      } else {
        setStatus('offline');
      }
    } catch {
      setStatus('offline');
    } finally {
      setLastCheck(new Date());
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, pollIntervalMs);
    return () => clearInterval(interval);
  }, [checkHealth, pollIntervalMs]);

  return { status, lastCheck, checkNow: checkHealth };
}
