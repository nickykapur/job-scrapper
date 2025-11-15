import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Menu,
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
  X,
} from 'lucide-react';
import { JobCard } from './components/JobCard';
import { StatsCards } from './components/StatsCards';
import { FilterControls } from './components/FilterControls';
// import { JobLoadingInfo } from './components/JobLoadingInfo';
// import { JobSections } from './components/JobSections';
// import { Training } from './components/Training';
// import { SystemDesign } from './components/SystemDesign';
import { Analytics } from './components/Analytics';
// import JobSearch from './components/JobSearch';
// import CountryStats from './components/CountryStats';
import { jobApi } from './services/api';
import { useAuth } from './contexts/AuthContext';
import { useDarkMode } from './hooks/use-dark-mode';
import type { Job, JobStats, FilterState } from './types';

const App: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { darkMode, toggleDarkMode } = useDarkMode();

  // State
  const [jobs, setJobs] = useState<Record<string, Job>>({});
  const [updatingJobs, setUpdatingJobs] = useState<Set<string>>(new Set());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [localRejectedCount, setLocalRejectedCount] = useState(0);
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'training' | 'system-design' | 'analytics'>('dashboard');
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  // Check if current user is software_admin or has admin access
  const hasAnalyticsAccess = user?.username === 'software_admin' || user?.username === 'admin' || user?.is_admin === true;

  const [filters, setFilters] = useState<FilterState>({
    status: 'all',
    sort: 'newest',
    jobType: 'all',
    country: 'all',
  });

  // Responsive handler
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const showNotification = (message: string, severity: 'success' | 'error' | 'info' = 'info') => {
    if (severity === 'success') {
      toast.success(message);
    } else if (severity === 'error') {
      toast.error(message);
    } else {
      toast(message);
    }
  };

  const toggleDrawer = () => setDrawerOpen(!drawerOpen);

  const loadJobs = useCallback(async (silent = false) => {
    if (!silent) setIsRefreshing(true);
    try {
      const jobsData = await jobApi.getJobs();
      setJobs(jobsData);

      const rejectedJobs = Object.entries(jobsData).filter(([key, job]) =>
        !key.startsWith('_') && job.rejected === true
      );
      setLocalRejectedCount(rejectedJobs.length);

      if (!silent) showNotification('Jobs refreshed successfully', 'success');
    } catch (error) {
      console.error('Failed to load jobs:', error);
      showNotification('Failed to load jobs', 'error');
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
    try {
      setUpdatingJobs(prev => new Set(prev).add(jobId));
      await jobApi.updateJob(jobId, true);
      window.open(jobUrl, '_blank');
      setJobs(prev => ({
        ...prev,
        [jobId]: { ...prev[jobId], applied: true }
      }));
      showNotification('Marked as applied', 'success');
    } catch (error) {
      showNotification('Failed to update job status', 'error');
    } finally {
      setUpdatingJobs(prev => {
        const next = new Set(prev);
        next.delete(jobId);
        return next;
      });
    }
  };

  const handleRejectJob = async (jobId: string) => {
    try {
      setUpdatingJobs(prev => new Set(prev).add(jobId));
      await jobApi.rejectJob(jobId);
      setJobs(prev => ({
        ...prev,
        [jobId]: { ...prev[jobId], rejected: true }
      }));
      setLocalRejectedCount(prev => prev + 1);
      showNotification('Job rejected', 'info');
    } catch (error) {
      showNotification('Failed to reject job', 'error');
    } finally {
      setUpdatingJobs(prev => {
        const next = new Set(prev);
        next.delete(jobId);
        return next;
      });
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Filter and sort jobs
  const cleanJobs = useMemo(() => {
    const filtered: Record<string, Job> = {};
    Object.entries(jobs).forEach(([id, job]) => {
      if (id.startsWith('_')) return;

      // Status filter
      if (filters.status === 'applied' && !job.applied) return;
      if (filters.status === 'not_applied' && (job.applied || job.rejected)) return;
      if (filters.status === 'new' && !job.is_new) return;
      if (filters.status === 'rejected' && !job.rejected) return;

      // Job type filter
      if (filters.jobType !== 'all' && job.job_type !== filters.jobType) return;

      // Country filter
      if (filters.country !== 'all' && job.country !== filters.country) return;

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
          onClick={() => { setCurrentTab('dashboard'); if (isMobile) setDrawerOpen(false); }}
        >
          <LayoutDashboard className="mr-3 h-4 w-4" />
          Dashboard
        </Button>

        {/* Temporarily disabled - MUI migration pending
        <Button
          variant={currentTab === 'training' ? 'secondary' : 'ghost'}
          className="w-full justify-start"
          onClick={() => { setCurrentTab('training'); if (isMobile) setDrawerOpen(false); }}
        >
          <GraduationCap className="mr-3 h-4 w-4" />
          DSA Training
        </Button>

        <Button
          variant={currentTab === 'system-design' ? 'secondary' : 'ghost'}
          className="w-full justify-start"
          onClick={() => { setCurrentTab('system-design'); if (isMobile) setDrawerOpen(false); }}
        >
          <Building2 className="mr-3 h-4 w-4" />
          System Design
        </Button>
        */}

        {hasAnalyticsAccess && (
          <Button
            variant={currentTab === 'analytics' ? 'secondary' : 'ghost'}
            className="w-full justify-start"
            onClick={() => { setCurrentTab('analytics'); if (isMobile) setDrawerOpen(false); }}
          >
            <BarChart3 className="mr-3 h-4 w-4" />
            Analytics
            <Badge variant="secondary" className="ml-auto">Admin</Badge>
          </Button>
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

      {/* Sidebar - Mobile */}
      {isMobile && drawerOpen && (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/50" onClick={() => setDrawerOpen(false)} />
          <aside className="absolute left-0 top-0 bottom-0 w-64 bg-card border-r">
            <div className="absolute right-4 top-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setDrawerOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            {sidebarContent}
          </aside>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="border-b bg-card px-6 py-4">
          <div className="flex items-center justify-between">
            {isMobile && (
              <Button variant="ghost" size="icon" onClick={toggleDrawer}>
                <Menu className="h-5 w-5" />
              </Button>
            )}

            <div className="flex-1">
              <h2 className="text-lg font-bold">
                {currentTab === 'dashboard' ? 'Jobs' :
                 currentTab === 'training' ? 'DSA Training' :
                 currentTab === 'system-design' ? 'System Design' : 'Analytics'}
              </h2>
              {currentTab === 'dashboard' && (
                <p className="text-sm text-muted-foreground">
                  {Object.keys(cleanJobs).length} active opportunities
                </p>
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
          <div className="container mx-auto px-6 py-6">
            {currentTab === 'dashboard' && (
              <>
                <StatsCards stats={stats} />

                <FilterControls
                  filters={filters}
                  onFiltersChange={setFilters}
                />

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(cleanJobs).map(([id, job]) => (
                    <JobCard
                      key={id}
                      job={job}
                      onApplyAndOpen={handleApplyAndOpen}
                      onRejectJob={handleRejectJob}
                      isUpdating={updatingJobs.has(id)}
                    />
                  ))}
                </div>

                {Object.keys(cleanJobs).length === 0 && (
                  <div className="text-center py-12">
                    <p className="text-muted-foreground">No jobs found matching your filters</p>
                  </div>
                )}
              </>
            )}

            {/* Temporarily disabled - MUI migration pending
            {currentTab === 'training' && <Training />}
            {currentTab === 'system-design' && <SystemDesign />}
            */}
            {currentTab === 'analytics' && hasAnalyticsAccess && <Analytics />}
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
