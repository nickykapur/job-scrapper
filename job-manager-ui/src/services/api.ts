import axios from 'axios';
import { Job } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const jobApi = {
  // Get all jobs
  getJobs: async (): Promise<Record<string, Job>> => {
    const response = await api.get('/jobs_database.json');
    return response.data;
  },

  // Update job status
  updateJob: async (jobId: string, applied: boolean): Promise<void> => {
    await api.post('/update_job', {
      job_id: jobId,
      applied: applied,
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
  searchJobs: async (keywords: string): Promise<{ success: boolean; new_jobs: number }> => {
    const response = await api.post('/search_jobs', {
      keywords: keywords,
    });
    return response.data;
  },
};

export default api;