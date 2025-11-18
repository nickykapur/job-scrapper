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
  easy_apply?: boolean; // Deprecated: Use easy_apply_status instead
  easy_apply_status?: 'confirmed' | 'probable' | 'unverified' | 'false';
  easy_apply_verified_at?: string;
  easy_apply_verification_method?: 'detail_page_verified' | 'filter_parameter' | 'card_detection' | 'manual';
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
  quickApply?: 'all' | 'quick_only' | 'non_quick' | 'confirmed_only' | 'probable_only';
}