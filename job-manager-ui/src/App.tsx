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
} from 'lucide-react';
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
  const [updatingJobs, setUpdatingJobs] = useState<Set<string>>(new Set());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [localRejectedCount, setLocalRejectedCount] = useState(0);
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'training' | 'system-design' | 'my-analytics' | 'analytics' | 'country-analytics' | 'rewards' | 'user-management' | 'interview-tracker' | 'monitoring' | 'user-behaviour'>('dashboard');
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
    country: 'Ireland',  // Default to Ireland
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

  const handleApplyAndOpen = async (jobId: string, jobUrl: string) => {
    // Open URL in background tab (doesn't steal focus)
    const link = document.createElement('a');
    link.href = jobUrl;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

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

      // Country filter
      if (filters.country !== 'all' && job.country !== filters.country) return;

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

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center">
            <Database className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold">Job Tracker</h1>
            <p className="text-xs text-muted-foreground">Find your dream job</p>
          </div>
        </div>
      </div>

      <Separator />

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <Button
          variant={currentTab === 'dashboard' ? 'secondary' : 'ghost'}
          className="w-full justify-start"
          onClick={() => handleTabChange('dashboard')}
        >
          <LayoutDashboard className="mr-3 h-4 w-4" />
          Dashboard
        </Button>

        <Button
          variant={currentTab === 'my-analytics' ? 'secondary' : 'ghost'}
          className="w-full justify-start"
          onClick={() => handleTabChange('my-analytics')}
        >
          <BarChart3 className="mr-3 h-4 w-4" />
          My Analytics
        </Button>

        <Button
          variant={currentTab === 'rewards' ? 'secondary' : 'ghost'}
          className="w-full justify-start"
          onClick={() => handleTabChange('rewards')}
        >
          <Trophy className="mr-3 h-4 w-4" />
          Rewards
        </Button>

        <Button
          variant={currentTab === 'interview-tracker' ? 'secondary' : 'ghost'}
          className="w-full justify-start"
          onClick={() => handleTabChange('interview-tracker')}
        >
          <Bookmark className="mr-3 h-4 w-4" />
          Interview Tracker
        </Button>

        {hasSoftwareAccess && (
          <>
            <Button
              variant={currentTab === 'training' ? 'secondary' : 'ghost'}
              className="w-full justify-start"
              onClick={() => handleTabChange('training')}
            >
              <GraduationCap className="mr-3 h-4 w-4" />
              DSA Training
            </Button>

            <Button
              variant={currentTab === 'system-design' ? 'secondary' : 'ghost'}
              className="w-full justify-start"
              onClick={() => handleTabChange('system-design')}
            >
              <Building2 className="mr-3 h-4 w-4" />
              System Design
            </Button>
          </>
        )}

        {hasAdminAccess && (
          <>
            <Button
              variant={currentTab === 'analytics' ? 'secondary' : 'ghost'}
              className="w-full justify-start"
              onClick={() => handleTabChange('analytics')}
            >
              <BarChart3 className="mr-3 h-4 w-4" />
              User Analytics
              <Badge variant="secondary" className="ml-auto">Admin</Badge>
            </Button>

            <Button
              variant={currentTab === 'country-analytics' ? 'secondary' : 'ghost'}
              className="w-full justify-start"
              onClick={() => handleTabChange('country-analytics')}
            >
              <Building2 className="mr-3 h-4 w-4" />
              Country Analytics
              <Badge variant="secondary" className="ml-auto">Admin</Badge>
            </Button>

            <Button
              variant={currentTab === 'user-management' ? 'secondary' : 'ghost'}
              className="w-full justify-start"
              onClick={() => handleTabChange('user-management')}
            >
              <Users className="mr-3 h-4 w-4" />
              User Management
              <Badge variant="secondary" className="ml-auto">Admin</Badge>
            </Button>

            <Button
              variant={currentTab === 'monitoring' ? 'secondary' : 'ghost'}
              className="w-full justify-start"
              onClick={() => handleTabChange('monitoring')}
            >
              <Activity className="mr-3 h-4 w-4" />
              Monitoring
              <Badge variant="secondary" className="ml-auto">Admin</Badge>
            </Button>

            <Button
              variant={currentTab === 'user-behaviour' ? 'secondary' : 'ghost'}
              className="w-full justify-start"
              onClick={() => handleTabChange('user-behaviour')}
            >
              <MousePointerClick className="mr-3 h-4 w-4" />
              User Behaviour
              <Badge variant="secondary" className="ml-auto">Admin</Badge>
            </Button>
          </>
        )}
      </nav>

      <Separator />

      {/* User Section */}
      <div className="p-4 space-y-2">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
            <User className="w-4 h-4 text-primary-foreground" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.username || 'User'}</p>
            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
          </div>
        </div>

        <Button
          variant="ghost"
          className="w-full justify-start text-muted-foreground hover:text-foreground"
          onClick={() => navigate('/settings')}
        >
          <Settings className="mr-3 h-4 w-4" />
          Settings
        </Button>

        <Button
          variant="ghost"
          className="w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10"
          onClick={handleLogout}
        >
          <LogOut className="mr-3 h-4 w-4" />
          Logout
        </Button>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar - Desktop */}
      {!isMobile && (
        <aside className="w-64 border-r bg-card flex-shrink-0">
          {sidebarContent}
        </aside>
      )}

      {/* Mobile Bottom Navigation — Instagram style */}
      {isMobile && (() => {
        const navItems: Array<{ tab: typeof currentTab | '_settings'; label: string; icon: React.ElementType; adminOnly?: boolean; softwareOnly?: boolean }> = [
          { tab: 'dashboard',         label: 'Jobs',       icon: LayoutDashboard },
          { tab: 'my-analytics',      label: 'Analytics',  icon: BarChart3 },
          { tab: 'rewards',           label: 'Rewards',    icon: Trophy },
          { tab: 'interview-tracker', label: 'Interviews', icon: Bookmark },
          ...(hasSoftwareAccess ? [{ tab: 'training' as typeof currentTab, label: 'Training', icon: GraduationCap, softwareOnly: true }] : []),
          ...(hasAdminAccess ? [
            { tab: 'user-management' as typeof currentTab, label: 'Users',   icon: Users,    adminOnly: true },
            { tab: 'monitoring'      as typeof currentTab, label: 'Monitor', icon: Activity, adminOnly: true },
          ] : []),
          { tab: '_settings', label: 'Settings', icon: Settings },
        ];

        return (
          <nav className="fixed bottom-0 left-0 right-0 z-40 bg-card border-t flex items-stretch h-16 overflow-x-auto">
            {navItems.map(({ tab, label, icon: Icon }) => {
              const active = tab !== '_settings' && currentTab === tab;
              return (
                <button
                  key={tab}
                  onClick={() => tab === '_settings' ? navigate('/settings') : handleTabChange(tab as typeof currentTab)}
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

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="border-b bg-card px-6 py-4">
          <div className="flex items-center justify-between">

            <div className="flex-1">
              <h2 className="text-lg font-bold">
                {currentTab === 'dashboard' ? 'Jobs' :
                 currentTab === 'my-analytics' ? 'My Analytics' :
                 currentTab === 'rewards' ? 'Rewards & Achievements' :
                 currentTab === 'interview-tracker' ? 'Interview Tracker' :
                 currentTab === 'training' ? 'DSA Training' :
                 currentTab === 'system-design' ? 'System Design' :
                 currentTab === 'analytics' ? 'User Analytics' :
                 currentTab === 'country-analytics' ? 'Country Analytics' :
                 currentTab === 'user-management' ? 'User Management' :
                 currentTab === 'monitoring' ? 'System Monitoring' :
                 currentTab === 'user-behaviour' ? 'User Behaviour' : 'Dashboard'}
              </h2>
              {currentTab === 'dashboard' && (
                <div className="space-y-0.5">
                  <p className="text-sm text-muted-foreground">
                    {paginatedJobs.totalJobs} active opportunities
                    {paginatedJobs.totalPages > 1 && ` • Page ${currentPage} of ${paginatedJobs.totalPages}`}
                  </p>
                  {timeAgo && (
                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                      <RefreshCw className="h-3 w-3" />
                      Last updated: {timeAgo}
                    </p>
                  )}
                </div>
              )}
            </div>

            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon" onClick={toggleDarkMode}>
                {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </Button>

              {currentTab === 'dashboard' && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => loadJobs()}
                  disabled={isRefreshing}
                >
                  <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
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

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(paginatedJobs.jobs).map(([id, job]) => (
                    <JobCard
                      key={id}
                      job={job}
                      onApplyAndOpen={handleApplyAndOpen}
                      onRejectJob={handleRejectJob}
                      onRefreshJobs={() => loadJobs(true)}
                      isUpdating={updatingJobs.has(id)}
                    />
                  ))}
                </div>

                {paginatedJobs.totalJobs === 0 && (
                  <div className="text-center py-12">
                    <p className="text-muted-foreground">No jobs found matching your filters</p>
                  </div>
                )}

                {/* Pagination Controls */}
                {paginatedJobs.totalPages > 1 && (
                  <div className="flex items-center justify-center gap-2 mt-8">
                    <Button
                      variant="outline"
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </Button>

                    <div className="flex items-center gap-1">
                      {Array.from({ length: paginatedJobs.totalPages }, (_, i) => i + 1)
                        .filter(page => {
                          // Show first page, last page, current page, and pages around current
                          return page === 1 ||
                                 page === paginatedJobs.totalPages ||
                                 Math.abs(page - currentPage) <= 1;
                        })
                        .map((page, idx, arr) => (
                          <React.Fragment key={page}>
                            {idx > 0 && arr[idx - 1] !== page - 1 && (
                              <span className="px-2 text-muted-foreground">...</span>
                            )}
                            <Button
                              variant={currentPage === page ? 'default' : 'outline'}
                              size="sm"
                              onClick={() => setCurrentPage(page)}
                              className="w-10"
                            >
                              {page}
                            </Button>
                          </React.Fragment>
                        ))}
                    </div>

                    <Button
                      variant="outline"
                      onClick={() => setCurrentPage(p => Math.min(paginatedJobs.totalPages, p + 1))}
                      disabled={currentPage === paginatedJobs.totalPages}
                    >
                      Next
                    </Button>
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
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
