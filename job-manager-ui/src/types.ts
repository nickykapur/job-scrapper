export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  posted_date: string;
  job_url: string;
  scraped_at: string;
  applied: boolean;
  is_new: boolean;
}

export interface JobStats {
  total: number;
  new: number;
  existing: number;
  applied: number;
  not_applied: number;
}

export interface FilterState {
  status: 'all' | 'applied' | 'not-applied' | 'new';
  search: string;
  sort: 'newest' | 'oldest' | 'title' | 'company';
}