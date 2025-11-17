import axios from 'axios';
import type { Job } from '../types';

// In production (Railway), the API is served from the same domain
// In development, use localhost:8000 (FastAPI default port)
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add auth token to all requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const jobApi = {
  // Get all jobs from database
  getJobs: async (): Promise<Record<string, Job>> => {
    const response = await api.get('/api/jobs');
    return response.data;
  },

  // Update job status
  updateJob: async (jobId: string, applied: boolean): Promise<any> => {
    const response = await api.post('/api/update_job', {
      job_id: jobId,
      applied: applied,
    });
    return response.data;
  },

  // Reject job - using update_job endpoint
  rejectJob: async (jobId: string): Promise<void> => {
    await api.post('/api/update_job', {
      job_id: jobId,
      rejected: true,
    });
  },

  // Remove applied jobs
  removeAppliedJobs: async (jobsData: Record<string, Job>): Promise<void> => {
    await api.post('/bulk_update', {
      action: 'remove_applied',
      jobs_data: jobsData,
    });
  },

  // Search for new jobs
  searchJobs: async (keywords: string, location?: string): Promise<{ success: boolean; new_jobs: number }> => {
    const response = await api.post('/search_jobs', {
      keywords: keywords,
      location: location || "Dublin, County Dublin, Ireland",
    });
    return response.data;
  },

  // Sync locally rejected jobs to cloud
  syncRejectedJobs: async (rejectedJobIds: string[]): Promise<{ success: boolean; synced_count: number }> => {
    const response = await api.post('/sync_rejected_jobs', {
      rejected_job_ids: rejectedJobIds,
    });
    return response.data;
  },

  // Get rejected jobs from cloud
  getRejectedJobs: async (): Promise<string[]> => {
    const response = await api.get('/rejected_jobs');
    return response.data.rejected_job_ids || [];
  },

  // Get analytics for all users (admin only)
  getAnalytics: async (): Promise<any> => {
    const response = await api.get('/api/admin/analytics');
    return response.data;
  },

  // Get personal analytics for current user
  getPersonalAnalytics: async (): Promise<any> => {
    const response = await api.get('/api/analytics/personal');
    return response.data;
  },

  // Get rewards and gamification data for current user
  getRewards: async (): Promise<any> => {
    const response = await api.get('/api/rewards');
    return response.data;
  },

  // Get personalized job search insights
  getInsights: async (): Promise<any> => {
    const response = await api.get('/api/insights');
    return response.data;
  },
};

export default api;