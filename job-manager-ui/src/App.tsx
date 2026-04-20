import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Moon,
  Sun,
  RefreshCw,
  Database,
  LayoutDashboard,
  Bookmark,
  Settings,
  GraduationCap,
  Building2,
  LogOut,
  User,
  BarChart3,
  Trophy,
  Users,
  Activity,
  MousePointerClick,
  FlaskConical,
} from 'lucide-react';
import {
  Button as FluentButton,
  Text,
  makeStyles,
  tokens,
  Tooltip,
} from '@fluentui/react-components';
import {
  ArrowSyncRegular,
  WeatherMoonRegular,
  WeatherSunnyRegular,
} from '@fluentui/react-icons';
import { JobCard } from './components/JobCard';
import { StatsCards } from './components/StatsCards';
import { FilterControls } from './components/FilterControls';
import { Training } from './components/Training';
import { SystemDesign } from './components/SystemDesign';
import { Analytics } from './components/Analytics';
import { PersonalAnalytics } from './components/PersonalAnalytics';
import { CountryAnalytics } from './components/CountryAnalytics';
import { RewardsRevamped as Rewards } from './components/RewardsRevamped';
import { UserManagement } from './components/UserManagement';
import { MonitoringPage } from './components/MonitoringPage';
import { UserBehaviourPage } from './components/UserBehaviourPage';
import { InterviewTracker } from './components/InterviewTracker';
import { CVPilot } from './components/CVPilot';
import AdminCVUploads from './components/AdminCVUploads';
// import JobSearch from './components/JobSearch';
// import CountryStats from './components/CountryStats';
import { jobApi } from './services/api';
import { useAuth } from './contexts/AuthContext';
import { useDarkMode } from './hooks/use-dark-mode';
import { useActivityTracker } from './hooks/useActivityTracker';
import { ErrorBoundary } from './components/ErrorBoundary';
import type { Job, JobStats, FilterState } from './types';

const App: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { darkMode, toggleDarkMode } = useDarkMode();
  const { track } = useActivityTracker();

  // State
  const [jobs, setJobs] = useState<Record<string, Job>>({});
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [updatingJobs, setUpdatingJobs] = useState<Set<string>>(new Set());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [localRejectedCount, setLocalRejectedCount] = useState(0);
  const [showMobileProfile, setShowMobileProfile] = useState(false);
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'training' | 'system-design' | 'my-analytics' | 'analytics' | 'country-analytics' | 'rewards' | 'user-management' | 'interview-tracker' | 'monitoring' | 'user-behaviour' | 'cv-pilot' | 'cv-uploads'>('dashboard');
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [timeAgo, setTimeAgo] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const jobsPerPage = 12;

  // Check if current user has admin access - strictly based on is_admin flag
  const hasAdminAccess = user?.is_admin === true;

  // Check if current user has software role access
  const hasSoftwareAccess = user?.username === 'software_admin' || user?.username === 'admin' || user?.is_admin === true;

  const [filters, setFilters] = useState<FilterState>({
    status: 'all',
    sort: 'newest',
    jobType: 'all',
    country: 'all',
    city: 'all',
    keyword: '',
    quickApply: 'all',
  });

  // Responsive handler
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Update "time ago" display every minute
  useEffect(() => {
    const updateTimeAgo = () => {
      if (!lastUpdated) {
        setTimeAgo('Never');
        return;
      }

      const seconds = Math.floor((new Date().getTime() - lastUpdated.getTime()) / 1000);

      if (seconds < 60) {
        setTimeAgo('Just now');
      } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        setTimeAgo(`${minutes} min${minutes > 1 ? 's' : ''} ago`);
      } else if (seconds < 86400) {
        const hours = Math.floor(seconds / 3600);
        setTimeAgo(`${hours} hour${hours > 1 ? 's' : ''} ago`);
      } else {
        const days = Math.floor(seconds / 86400);
        setTimeAgo(`${days} day${days > 1 ? 's' : ''} ago`);
      }
    };

    updateTimeAgo();
    const interval = setInterval(updateTimeAgo, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [lastUpdated]);

  const showNotification = (message: string, severity: 'success' | 'error' | 'info' = 'info') => {
    if (severity === 'success') {
      toast.success(message);
    } else if (severity === 'error') {
      toast.error(message);
    } else {
      toast(message);
    }
  };


  const JOBS_CACHE_KEY = 'job_tracker_jobs_cache';
  const JOBS_CACHE_TS_KEY = 'job_tracker_jobs_cache_ts';

  const loadJobs = useCallback(async (silent = false) => {
    if (!silent) setIsRefreshing(true);
    try {
      const jobsData = await jobApi.getJobs();
      setJobs(jobsData);
      setIsInitialLoading(false);

      // Persist to localStorage so users can still see jobs if backend goes down
      try {
        localStorage.setItem(JOBS_CACHE_KEY, JSON.stringify(jobsData));
        localStorage.setItem(JOBS_CACHE_TS_KEY, new Date().toISOString());
      } catch { /* storage full — ignore */ }

      const rejectedJobs = Object.entries(jobsData).filter(([key, job]) =>
        !key.startsWith('_') && job.rejected === true
      );
      setLocalRejectedCount(rejectedJobs.length);

      // Update last refreshed timestamp
      setLastUpdated(new Date());

      if (!silent) showNotification('Jobs refreshed successfully', 'success');
    } catch (error) {
      console.error('Failed to load jobs:', error);

      // Fall back to cached jobs so users aren't left with an empty board
      try {
        const cached = localStorage.getItem(JOBS_CACHE_KEY);
        const cachedTs = localStorage.getItem(JOBS_CACHE_TS_KEY);
        if (cached) {
          const cachedData = JSON.parse(cached);
          setJobs(cachedData);
          const rejectedJobs = Object.entries(cachedData).filter(([key, job]: [string, any]) =>
            !key.startsWith('_') && job.rejected === true
          );
          setLocalRejectedCount(rejectedJobs.length);
          if (cachedTs) setLastUpdated(new Date(cachedTs));
          showNotification('Backend unreachable — showing cached jobs', 'info');
        } else {
          showNotification('Failed to load jobs', 'error');
        }
      } catch {
        showNotification('Failed to load jobs', 'error');
      } finally {
        setIsInitialLoading(false);
      }
    } finally {
      if (!silent) setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadJobs(true);
    const interval = setInterval(() => loadJobs(true), 300000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, [loadJobs]);

  const handleMarkApplied = async (jobId: string) => {
    // OPTIMISTIC UI UPDATE - Update UI immediately for instant feedback
    setJobs(prev => ({
      ...prev,
      [jobId]: { ...prev[jobId], applied: true }
    }));
    showNotification('Marked as applied', 'success');
    track('job_action', { action: 'applied', job_id: jobId });

    // Update backend in background (fire-and-forget with error handling)
    try {
      const response = await jobApi.updateJob(jobId, true);

      // Show encouragement message if available (replace previous notification)
      if (response.encouragement) {
        showNotification(response.encouragement, 'success');
      }
    } catch (error) {
      // Rollback UI change on error
      setJobs(prev => ({
        ...prev,
        [jobId]: { ...prev[jobId], applied: false }
      }));
      showNotification('Failed to update job status - please try again', 'error');
    }
  };

  const handleRejectJob = async (jobId: string) => {
    // OPTIMISTIC UI UPDATE - Update UI immediately for instant feedback
    setJobs(prev => ({
      ...prev,
      [jobId]: { ...prev[jobId], rejected: true }
    }));
    setLocalRejectedCount(prev => prev + 1);
    showNotification('Job rejected', 'info');
    track('job_action', { action: 'rejected', job_id: jobId });

    // Update backend in background (fire-and-forget with error handling)
    try {
      await jobApi.rejectJob(jobId);
    } catch (error) {
      // Rollback UI change on error
      setJobs(prev => ({
        ...prev,
        [jobId]: { ...prev[jobId], rejected: false }
      }));
      setLocalRejectedCount(prev => prev - 1);
      showNotification('Failed to reject job - please try again', 'error');
    }
  };

  const handleTabChange = useCallback((tab: typeof currentTab) => {
    setCurrentTab(tab);
    track('page_view', { page: tab });
  }, [track, isMobile]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Parse LinkedIn's relative date strings ("5 days ago", "2 weeks ago", etc.)
  // into a comparable timestamp. Falls back to scraped_at if unparseable.
  const postedDateToTs = (job: Job): number => {
    const raw = (job.posted_date || '').toLowerCase().replace(/^posted\s+/, '').trim();
    const now = Date.now();
    const m = raw.match(/^(\d+)\s+(second|minute|min|hour|day|week|month)/);
    if (m) {
      const n = parseInt(m[1], 10);
      const unit = m[2];
      const ms: Record<string, number> = {
        second: 1000, minute: 60_000, min: 60_000,
        hour: 3_600_000, day: 86_400_000, week: 604_800_000, month: 2_592_000_000,
      };
      return now - n * (ms[unit] ?? 86_400_000);
    }
    if (raw === 'just now' || raw === 'moments ago') return now;
    // Fall back to scraped_at
    return new Date(job.scraped_at || 0).getTime();
  };

  // Filter and sort jobs
  const cleanJobs = useMemo(() => {
    const filtered: Record<string, Job> = {};
    Object.entries(jobs).forEach(([id, job]) => {
      if (id.startsWith('_')) return;

      // Status filter
      if (filters.status === 'all') {
        // Hide jobs that are already applied to or rejected
        if (job.applied || job.rejected) return;
      } else if (filters.status === 'applied' && !job.applied) return;
      else if (filters.status === 'not_applied' && (job.applied || job.rejected)) return;
      else if (filters.status === 'new' && !job.is_new) return;
      else if (filters.status === 'rejected' && !job.rejected) return;

      // Job type filter
      if (filters.jobType !== 'all' && job.job_type !== filters.jobType) return;

      // Keyword filter — matches title or company name
      if (filters.keyword && filters.keyword.trim()) {
        const kw = filters.keyword.toLowerCase();
        const matchesTitle = job.title?.toLowerCase().includes(kw);
        const matchesCompany = job.company?.toLowerCase().includes(kw);
        if (!matchesTitle && !matchesCompany) return;
      }

      // Country filter
      if (filters.country !== 'all' && job.country !== filters.country) return;

      // City filter
      if (filters.city !== 'all' && job.location !== filters.city) return;

      // Quick Apply filter with verification status support
      if (filters.quickApply === 'confirmed_only' && job.easy_apply_status !== 'confirmed') return;
      if (filters.quickApply === 'probable_only' && job.easy_apply_status !== 'probable') return;
      if (filters.quickApply === 'quick_only') {
        // Show both confirmed and probable, or legacy easy_apply=true
        const hasQuickApply = job.easy_apply_status === 'confirmed' ||
                               job.easy_apply_status === 'probable' ||
                               (job.easy_apply && !job.easy_apply_status);
        if (!hasQuickApply) return;
      }
      if (filters.quickApply === 'non_quick') {
        // Show only non-quick apply jobs
        const isQuickApply = job.easy_apply_status === 'confirmed' ||
                              job.easy_apply_status === 'probable' ||
                              (job.easy_apply && !job.easy_apply_status);
        if (isQuickApply) return;
      }

      // Hide stale jobs — don't apply to applied/rejected views (historical records)
      if (filters.status !== 'applied' && filters.status !== 'rejected') {
        // Hide jobs scraped more than 14 days ago (matches DB retention window).
        if (job.scraped_at) {
          const diffHours = (Date.now() - new Date(job.scraped_at).getTime()) / 3600000;
          if (diffHours > 336) return;
        }
        // Only hide jobs with definitively old posted_date (months/years/weeks old)
        const pd = (job.posted_date || '').toLowerCase().replace(/^posted\s+/, '');
        if (/month|year/.test(pd)) return;
        if (pd.match(/\d+\s+week/)) return;
      }

      filtered[id] = job;
    });

    return filtered;
  }, [jobs, filters]);

  const stats: JobStats = useMemo(() => {
    const jobList = Object.entries(jobs).filter(([key]) => !key.startsWith('_'));
    return {
      total: jobList.length,
      new: jobList.filter(([, job]) => job.is_new).length,
      applied: jobList.filter(([, job]) => job.applied).length,
      not_applied: jobList.filter(([, job]) => !job.applied && !job.rejected).length,
    };
  }, [jobs]);

  // Pagination logic
  const paginatedJobs = useMemo(() => {
    const jobEntries = Object.entries(cleanJobs);

    // Apply sort — use posted_date (parsed) so card dates match the order shown
    jobEntries.sort(([, a], [, b]) => {
      if (filters.sort === 'newest') {
        return postedDateToTs(b) - postedDateToTs(a);
      } else if (filters.sort === 'oldest') {
        return postedDateToTs(a) - postedDateToTs(b);
      }
      return 0;
    });

    const totalPages = Math.ceil(jobEntries.length / jobsPerPage);
    const startIndex = (currentPage - 1) * jobsPerPage;
    const endIndex = startIndex + jobsPerPage;

    return {
      jobs: Object.fromEntries(jobEntries.slice(startIndex, endIndex)),
      totalPages,
      totalJobs: jobEntries.length,
    };
  }, [cleanJobs, currentPage, jobsPerPage, filters.sort]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filters]);

  // Nav item helper
  const NavItem = ({ tab, label, icon: Icon, badge }: { tab: typeof currentTab; label: string; icon: React.ElementType; badge?: string }) => {
    const active = currentTab === tab;
    return (
      <button
        onClick={() => handleTabChange(tab)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          width: '100%',
          padding: '9px 12px',
          borderRadius: '10px',
          border: 'none',
          cursor: 'pointer',
          fontSize: '13.5px',
          fontWeight: active ? 700 : 500,
          background: active ? 'linear-gradient(135deg,rgba(59,130,246,0.15),rgba(99,102,241,0.15))' : 'transparent',
          color: active ? '#3b82f6' : tokens.colorNeutralForeground2,
          transition: 'all 0.15s ease',
          textAlign: 'left',
          position: 'relative',
        }}
        onMouseEnter={e => { if (!active) (e.currentTarget as HTMLElement).style.background = tokens.colorNeutralBackground2; }}
        onMouseLeave={e => { if (!active) (e.currentTarget as HTMLElement).style.background = 'transparent'; }}
      >
        {active && (
          <div style={{ position: 'absolute', left: 0, top: '6px', bottom: '6px', width: '3px', borderRadius: '0 3px 3px 0', background: 'linear-gradient(180deg,#3b82f6,#6366f1)' }} />
        )}
        <Icon style={{ fontSize: '17px', flexShrink: 0 }} />
        <span style={{ flex: 1 }}>{label}</span>
        {badge && (
          <span style={{ fontSize: '10px', fontWeight: 700, background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', color: '#fff', padding: '2px 7px', borderRadius: '10px' }}>
            {badge}
          </span>
        )}
      </button>
    );
  };

  const userInitials = (user?.full_name || user?.username || 'U').split(/\s+/).slice(0, 2).map((w: string) => w[0]?.toUpperCase() ?? '').join('');

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div style={{ padding: '20px 16px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <Database style={{ width: '20px', height: '20px', color: '#fff' }} />
          </div>
          <div>
            <p style={{ fontSize: '15px', fontWeight: 800, lineHeight: 1.2, margin: 0 }}>Job Tracker</p>
            <p style={{ fontSize: '11px', color: tokens.colorNeutralForeground3, margin: 0 }}>Find your next role</p>
          </div>
        </div>
      </div>

      <Separator />

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '12px 8px', display: 'flex', flexDirection: 'column', gap: '2px' }}>
        <NavItem tab="dashboard"         label="Jobs"             icon={LayoutDashboard} />
        <NavItem tab="my-analytics"      label="My Analytics"     icon={BarChart3} />
        <NavItem tab="rewards"           label="Rewards"          icon={Trophy} />
        <NavItem tab="interview-tracker" label="Interviews"       icon={Bookmark} />

        {/* Pilot features */}
        <div style={{ height: '1px', background: tokens.colorNeutralStroke2, margin: '8px 4px' }} />
        <NavItem tab="cv-pilot" label="CV Upload" icon={FlaskConical} badge="Pilot" />

        {hasSoftwareAccess && (
          <>
            <div style={{ height: '1px', background: tokens.colorNeutralStroke2, margin: '8px 4px' }} />
            <NavItem tab="training"      label="DSA Training"     icon={GraduationCap} />
            <NavItem tab="system-design" label="System Design"    icon={Building2} />
          </>
        )}

        {hasAdminAccess && (
          <>
            <div style={{ height: '1px', background: tokens.colorNeutralStroke2, margin: '8px 4px' }} />
            <NavItem tab="analytics"         label="User Analytics"    icon={BarChart3}       badge="Admin" />
            <NavItem tab="country-analytics" label="Country Analytics" icon={Building2}        badge="Admin" />
            <NavItem tab="user-management"   label="User Management"   icon={Users}            badge="Admin" />
            <NavItem tab="cv-uploads"        label="CV Uploads"         icon={FlaskConical}     badge="Admin" />
            <NavItem tab="monitoring"        label="Monitoring"         icon={Activity}         badge="Admin" />
            <NavItem tab="user-behaviour"    label="User Behaviour"     icon={MousePointerClick} badge="Admin" />
          </>
        )}
      </nav>

      <Separator />

      {/* User section */}
      <div style={{ padding: '12px 8px' }}>
        {/* Avatar card */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 12px', borderRadius: '12px', background: tokens.colorNeutralBackground2, marginBottom: '6px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg,#f59e0b,#f97316)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', fontWeight: 800, color: '#fff', flexShrink: 0 }}>
            {userInitials}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <p style={{ fontSize: '13px', fontWeight: 700, margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{user?.full_name || user?.username}</p>
            <p style={{ fontSize: '11px', color: tokens.colorNeutralForeground3, margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{user?.email}</p>
          </div>
        </div>

        <button
          onClick={() => navigate('/settings')}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '100%', padding: '8px 12px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '13px', fontWeight: 500, background: 'transparent', color: tokens.colorNeutralForeground3, textAlign: 'left' }}
          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = tokens.colorNeutralBackground2; }}
          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = 'transparent'; }}
        >
          <Settings style={{ width: '15px', height: '15px' }} />
          Settings
        </button>

        <button
          onClick={handleLogout}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '100%', padding: '8px 12px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '13px', fontWeight: 500, background: 'transparent', color: '#ef4444', textAlign: 'left' }}
          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(239,68,68,0.08)'; }}
          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = 'transparent'; }}
        >
          <LogOut style={{ width: '15px', height: '15px' }} />
          Log out
        </button>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar - Desktop */}
      {!isMobile && (
        <aside style={{ width: '240px', flexShrink: 0, background: '#0d0d10', borderRight: '1px solid rgba(255,255,255,0.06)', display: 'flex', flexDirection: 'column' }}>
          {sidebarContent}
        </aside>
      )}

      {/* Mobile Bottom Navigation — Instagram style */}
      {isMobile && (() => {
        const navItems: Array<{ tab: typeof currentTab | '_profile'; label: string; icon: React.ElementType }> = [
          { tab: 'dashboard',         label: 'Jobs',       icon: LayoutDashboard },
          { tab: 'my-analytics',      label: 'Analytics',  icon: BarChart3 },
          { tab: 'rewards',           label: 'Rewards',    icon: Trophy },
          { tab: 'interview-tracker', label: 'Interviews', icon: Bookmark },
          ...(hasSoftwareAccess ? [{ tab: 'training' as typeof currentTab, label: 'Training', icon: GraduationCap }] : []),
          ...(hasAdminAccess ? [
            { tab: 'user-management' as typeof currentTab, label: 'Users',   icon: Users },
            { tab: 'monitoring'      as typeof currentTab, label: 'Monitor', icon: Activity },
          ] : []),
          { tab: '_profile', label: 'Profile', icon: User },
        ];

        return (
          <nav className="fixed bottom-0 left-0 right-0 z-40 bg-card border-t flex items-stretch h-16 overflow-x-auto">
            {navItems.map(({ tab, label, icon: Icon }) => {
              const active = tab !== '_profile' && currentTab === tab;
              const isProfile = tab === '_profile';
              return (
                <button
                  key={tab}
                  onClick={() => isProfile ? setShowMobileProfile(true) : handleTabChange(tab as typeof currentTab)}
                  className={`flex-1 min-w-[60px] flex flex-col items-center justify-center gap-0.5 transition-colors
                    ${active ? 'text-primary' : 'text-muted-foreground hover:text-foreground'}`}
                >
                  <Icon className={`h-5 w-5 ${active ? 'stroke-[2.5px]' : 'stroke-[1.5px]'}`} />
                  <span className="text-[10px] font-medium leading-none">{label}</span>
                </button>
              );
            })}
          </nav>
        );
      })()}

      {/* Mobile Profile Sheet */}
      {isMobile && showMobileProfile && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setShowMobileProfile(false)}
          />
          {/* Sheet */}
          <div className="relative bg-card rounded-t-2xl border-t border-border pb-safe overflow-hidden">
            {/* Handle */}
            <div className="flex justify-center pt-3 pb-1">
              <div className="w-10 h-1 rounded-full bg-muted-foreground/30" />
            </div>

            {/* User info */}
            <div className="flex items-center gap-3 px-5 py-4 border-b border-border">
              <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center shrink-0">
                <User className="w-6 h-6 text-primary-foreground" />
              </div>
              <div className="min-w-0">
                <p className="font-semibold truncate">{user?.full_name || user?.username}</p>
                <p className="text-sm text-muted-foreground truncate">{user?.email}</p>
              </div>
            </div>

            {/* Actions */}
            <div className="px-4 py-3 space-y-1">
              <button
                onClick={toggleDarkMode}
                className="w-full flex items-center justify-between px-3 py-3 rounded-xl hover:bg-muted/60 transition-colors"
              >
                <span className="flex items-center gap-3 text-sm font-medium">
                  {darkMode
                    ? <Sun className="h-4 w-4 text-muted-foreground" />
                    : <Moon className="h-4 w-4 text-muted-foreground" />}
                  {darkMode ? 'Light mode' : 'Dark mode'}
                </span>
              </button>

              <button
                onClick={async () => { setShowMobileProfile(false); await handleLogout(); }}
                className="w-full flex items-center gap-3 px-3 py-3 rounded-xl text-destructive hover:bg-destructive/10 transition-colors text-sm font-medium"
              >
                <LogOut className="h-4 w-4" />
                Log out
              </button>
            </div>

            {/* Safe area spacer for phones with home indicator */}
            <div className="h-6" />
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header style={{ borderBottom: '1px solid rgba(255,255,255,0.06)', background: '#0d0d10', padding: '14px 24px' }}>
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <Text weight="bold" size={500}>
                {currentTab === 'dashboard' ? 'Job Board' :
                 currentTab === 'my-analytics' ? 'My Analytics' :
                 currentTab === 'rewards' ? 'Rewards & Achievements' :
                 currentTab === 'interview-tracker' ? 'Interview Tracker' :
                 currentTab === 'training' ? 'DSA Training' :
                 currentTab === 'system-design' ? 'System Design' :
                 currentTab === 'analytics' ? 'User Analytics' :
                 currentTab === 'country-analytics' ? 'Country Analytics' :
                 currentTab === 'user-management' ? 'User Management' :
                 currentTab === 'monitoring' ? 'System Monitoring' :
                 currentTab === 'user-behaviour' ? 'User Behaviour' :
                 currentTab === 'cv-pilot' ? 'CV Upload — Auto-Apply Pilot' :
                 currentTab === 'cv-uploads' ? 'CV Uploads — Admin View' : 'Dashboard'}
              </Text>
              {currentTab === 'dashboard' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', marginTop: '2px' }}>
                  <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                    {paginatedJobs.totalJobs} active opportunities
                    {paginatedJobs.totalPages > 1 && ` · Page ${currentPage} of ${paginatedJobs.totalPages}`}
                  </Text>
                  {timeAgo && (
                    <Text size={100} style={{ color: tokens.colorNeutralForeground4, display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <RefreshCw style={{ width: '10px', height: '10px' }} />
                      Updated {timeAgo}
                    </Text>
                  )}
                </div>
              )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Tooltip content={darkMode ? 'Switch to light mode' : 'Switch to dark mode'} relationship="label">
                <FluentButton
                  appearance="subtle"
                  icon={darkMode ? <WeatherSunnyRegular /> : <WeatherMoonRegular />}
                  onClick={toggleDarkMode}
                />
              </Tooltip>

              {currentTab === 'dashboard' && (
                <FluentButton
                  appearance="outline"
                  icon={<ArrowSyncRegular className={isRefreshing ? 'animate-spin' : ''} />}
                  onClick={() => loadJobs()}
                  disabled={isRefreshing}
                >
                  Refresh
                </FluentButton>
              )}
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-auto">
          <div className={`container mx-auto px-6 py-6 ${isMobile ? 'pb-20' : ''}`}>
            {currentTab === 'dashboard' && (
              <>
                <StatsCards stats={stats} />

                <FilterControls
                  filters={filters}
                  onFiltersChange={setFilters}
                  jobs={jobs}
                />

                {/* Loading skeleton */}
                {isInitialLoading && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Array.from({ length: 6 }).map((_, i) => (
                      <div key={i} className="rounded-xl border bg-card overflow-hidden animate-pulse" style={{ height: '280px' }}>
                        <div style={{ height: '4px', background: '#e5e7eb' }} />
                        <div className="p-5 flex flex-col gap-3">
                          <div className="h-3 rounded bg-muted w-1/3" />
                          <div className="h-4 rounded bg-muted w-4/5" />
                          <div className="h-4 rounded bg-muted w-3/5" />
                          <div className="h-3 rounded bg-muted w-2/5 mt-2" />
                          <div className="h-3 rounded bg-muted w-1/4" />
                        </div>
                        <div className="px-5 mt-auto flex flex-col gap-2">
                          <div className="h-10 rounded-lg bg-muted" />
                          <div className="h-8 rounded-lg bg-muted w-2/3" />
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {!isInitialLoading && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(paginatedJobs.jobs).map(([id, job]) => (
                      <JobCard
                        key={id}
                        job={job}
                        onMarkApplied={handleMarkApplied}
                        onRejectJob={handleRejectJob}
                        onRefreshJobs={() => loadJobs(true)}
                        isUpdating={updatingJobs.has(id)}
                      />
                    ))}
                  </div>
                )}

                {!isInitialLoading && paginatedJobs.totalJobs === 0 && (
                  <div style={{ textAlign: 'center', padding: '60px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                    <Text size={400} weight="semibold">No jobs found</Text>
                    <Text size={300} style={{ color: tokens.colorNeutralForeground3 }}>
                      Try adjusting your filters or check back after the next scrape
                    </Text>
                  </div>
                )}

                {/* Pagination */}
                {paginatedJobs.totalPages > 1 && (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginTop: '32px' }}>
                    <FluentButton
                      appearance="outline"
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </FluentButton>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      {Array.from({ length: paginatedJobs.totalPages }, (_, i) => i + 1)
                        .filter(page =>
                          page === 1 ||
                          page === paginatedJobs.totalPages ||
                          Math.abs(page - currentPage) <= 1
                        )
                        .map((page, idx, arr) => (
                          <React.Fragment key={page}>
                            {idx > 0 && arr[idx - 1] !== page - 1 && (
                              <Text style={{ padding: '0 4px', color: tokens.colorNeutralForeground3 }}>…</Text>
                            )}
                            <FluentButton
                              appearance={currentPage === page ? 'primary' : 'outline'}
                              onClick={() => setCurrentPage(page)}
                              style={{ minWidth: '36px', padding: '0 8px' }}
                            >
                              {page}
                            </FluentButton>
                          </React.Fragment>
                        ))}
                    </div>

                    <FluentButton
                      appearance="outline"
                      onClick={() => setCurrentPage(p => Math.min(paginatedJobs.totalPages, p + 1))}
                      disabled={currentPage === paginatedJobs.totalPages}
                    >
                      Next
                    </FluentButton>
                  </div>
                )}
              </>
            )}

            {currentTab === 'my-analytics' && <ErrorBoundary><PersonalAnalytics /></ErrorBoundary>}
            {currentTab === 'rewards' && <ErrorBoundary><Rewards /></ErrorBoundary>}
            {currentTab === 'interview-tracker' && <ErrorBoundary><InterviewTracker /></ErrorBoundary>}
            {currentTab === 'training' && hasSoftwareAccess && <ErrorBoundary><Training /></ErrorBoundary>}
            {currentTab === 'system-design' && hasSoftwareAccess && <ErrorBoundary><SystemDesign /></ErrorBoundary>}
            {currentTab === 'analytics' && hasAdminAccess && <ErrorBoundary><Analytics /></ErrorBoundary>}
            {currentTab === 'country-analytics' && hasAdminAccess && <ErrorBoundary><CountryAnalytics /></ErrorBoundary>}
            {currentTab === 'user-management' && hasAdminAccess && <ErrorBoundary><UserManagement /></ErrorBoundary>}
            {currentTab === 'monitoring' && hasAdminAccess && <ErrorBoundary><MonitoringPage /></ErrorBoundary>}
            {currentTab === 'user-behaviour' && hasAdminAccess && <ErrorBoundary><UserBehaviourPage /></ErrorBoundary>}
            {currentTab === 'cv-pilot' && <ErrorBoundary><CVPilot /></ErrorBoundary>}
            {currentTab === 'cv-uploads' && hasAdminAccess && <ErrorBoundary><AdminCVUploads /></ErrorBoundary>}
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
