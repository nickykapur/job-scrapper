import { useCallback } from 'react';
import { jobApi } from '../services/api';

export const useActivityTracker = () => {
  const track = useCallback((eventType: string, data?: Record<string, any>) => {
    jobApi.trackActivity(eventType, data);
  }, []);
  return { track };
};
