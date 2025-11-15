export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  posted_date: string;
  job_url: string;
  scraped_at: string;
  applied: boolean;
  rejected?: boolean;
  easy_apply?: boolean;
  is_new: boolean;
  category?: 'new' | 'last_24h' | 'existing';
  first_seen?: string;
  last_seen_24h?: string;
  country?: string;
  job_type?: 'software' | 'hr' | 'cybersecurity' | 'sales' | 'finance' | 'other';
  experience_level?: 'entry' | 'junior' | 'mid' | 'senior';
}

export interface JobStats {
  total: number;
  new: number;
  existing: number;
  applied: number;
  not_applied: number;
}

export interface FilterState {
  status: 'all' | 'applied' | 'not-applied' | 'rejected' | 'new';
  sort: 'newest' | 'oldest' | 'title' | 'company';
  jobType: 'all' | 'software' | 'hr' | 'cybersecurity' | 'sales' | 'finance';
  country: 'all' | string;
}