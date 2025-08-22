import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Alert,
  Snackbar,
  IconButton,
  Chip,
} from '@mui/material';
import { 
  Work as WorkIcon, 
  Brightness4 as DarkIcon,
  Brightness7 as LightIcon,
  CloudSync as SyncIcon,
  Storage as DatabaseIcon,
} from '@mui/icons-material';
import { JobCard } from './components/JobCard';
import { StatsCards } from './components/StatsCards';
import { FilterControls } from './components/FilterControls';
import { JobLoadingInfo } from './components/JobLoadingInfo';
import { JobSections } from './components/JobSections';
import { jobApi } from './services/api';
import { Job, JobStats, FilterState } from './types';

const createAppTheme = (mode: 'light' | 'dark') => createTheme({
  palette: {
    mode,
    primary: {
      main: mode === 'dark' ? '#0ea5e9' : '#0077b5',
    },
    secondary: {
      main: '#10b981',
    },
    background: {
      default: mode === 'dark' ? '#0f172a' : '#f8fafc',
      paper: mode === 'dark' ? '#1e293b' : '#ffffff',
    },
    text: {
      primary: mode === 'dark' ? '#f8fafc' : '#1e293b',
      secondary: mode === 'dark' ? '#cbd5e1' : '#64748b',
    },
    success: {
      main: '#10b981',
    },
    warning: {
      main: '#f59e0b',
    },
    error: {
      main: '#ef4444',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: mode === 'dark' ? '#1e293b' : '#ffffff',
          borderRadius: 8,
          border: mode === 'dark' ? '1px solid #334155' : '1px solid #e2e8f0',
          transition: 'all 0.2s ease-in-out',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 600,
          textTransform: 'none',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: mode === 'dark' ? '#1e293b' : '#ffffff',
          color: mode === 'dark' ? '#f8fafc' : '#1e293b',
          boxShadow: mode === 'dark' 
            ? '0 1px 3px rgba(0, 0, 0, 0.3)' 
            : '0 1px 3px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingLeft: '16px !important',
          paddingRight: '16px !important',
        },
      },
    },
  },
});

const EXCLUDED_COMPANIES_KEY = 'excludedCompanies';
const AUTO_REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

function App() {
  const [darkMode, setDarkMode] = useState(true); // Default to dark mode
  const [jobs, setJobs] = useState<Record<string, Job>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingJobs, setUpdatingJobs] = useState<Set<string>>(new Set());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [notification, setNotification] = useState<{
    message: string;
    severity: 'success' | 'error' | 'info';
  } | null>(null);
  
  const theme = useMemo(() => createAppTheme(darkMode ? 'dark' : 'light'), [darkMode]);
  
  const [filters, setFilters] = useState<FilterState>({
    status: 'all',
    search: '',
    sort: 'newest',
  });

  const [excludedCompanies, setExcludedCompanies] = useState<string[]>(() => {
    const saved = localStorage.getItem(EXCLUDED_COMPANIES_KEY);
    return saved ? JSON.parse(saved) : [];
  });

  const showNotification = (message: string, severity: 'success' | 'error' | 'info' = 'info') => {
    setNotification({ message, severity });
  };

  const loadJobs = useCallback(async (silent = false) => {
    if (!silent) setIsRefreshing(true);
    try {
      console.log('🔄 Loading jobs from API...');
      const jobsData = await jobApi.getJobs();
      console.log('✅ Jobs loaded successfully:', Object.keys(jobsData).length, 'jobs');
      
      const oldCount = Object.keys(jobs).length;
      const newCount = Object.keys(jobsData).length;
      
      setJobs(jobsData);
      setError(null);
      
      if (!silent && newCount > oldCount && oldCount > 0) {
        showNotification(`🎆 ${newCount - oldCount} new jobs loaded!`, 'success');
      }
    } catch (err: any) {
      console.error('❌ Failed to load jobs:', err);
      
      let errorMessage = 'Failed to load jobs';
      if (err.response) {
        errorMessage = `API Error: ${err.response.status} - ${err.response.statusText}`;
      } else if (err.request) {
        errorMessage = 'Network Error: Unable to connect to API';
      } else {
        errorMessage = `Error: ${err.message}`;
      }
      
      setError(errorMessage);
      showNotification(errorMessage, 'error');
    } finally {
      setLoading(false);
      if (!silent) setIsRefreshing(false);
    }
  }, [jobs]);

  const toggleJobApplied = async (jobId: string) => {
    const job = jobs[jobId];
    if (!job) return;

    setUpdatingJobs(prev => new Set(prev).add(jobId));
    
    try {
      await jobApi.updateJob(jobId, !job.applied);
      setJobs(prev => ({
        ...prev,
        [jobId]: { ...prev[jobId], applied: !prev[jobId].applied },
      }));
      showNotification(
        `✅ Job marked as ${!job.applied ? 'applied' : 'not applied'}!`,
        'success'
      );
    } catch (err) {
      showNotification('Failed to update job status', 'error');
    } finally {
      setUpdatingJobs(prev => {
        const newSet = new Set(prev);
        newSet.delete(jobId);
        return newSet;
      });
    }
  };

  const removeAppliedJobs = async () => {
    const appliedJobs = Object.values(jobs).filter(job => job.applied);
    
    if (appliedJobs.length === 0) {
      showNotification('📝 No applied jobs to remove', 'info');
      return;
    }

    if (!window.confirm(`Remove ${appliedJobs.length} applied jobs? This cannot be undone.`)) {
      return;
    }

    const newJobsData = Object.fromEntries(
      Object.entries(jobs).filter(([_, job]) => !job.applied)
    );

    try {
      await jobApi.removeAppliedJobs(newJobsData);
      setJobs(newJobsData);
      showNotification(`🗑️ Removed ${appliedJobs.length} applied jobs`, 'success');
    } catch (err) {
      // Update locally even if server fails
      setJobs(newJobsData);
      showNotification(
        `🗑️ Removed ${appliedJobs.length} applied jobs (local only)`,
        'success'
      );
    }
  };

  const searchJobs = async (keywords: string) => {
    setIsSearching(true);
    try {
      const result = await jobApi.searchJobs(keywords);
      showNotification(`🎆 Search completed! Found ${result.new_jobs || 0} new jobs`, 'success');
      await loadJobs(true); // Refresh data silently
    } catch (err) {
      showNotification('❌ Search failed', 'error');
    } finally {
      setIsSearching(false);
    }
  };

  const markAllAsRead = () => {
    const newJobs = Object.values(jobs).filter(job => job.is_new);
    if (newJobs.length === 0) {
      showNotification('📝 No new jobs to mark as read', 'info');
      return;
    }

    const updatedJobs = { ...jobs };
    Object.keys(updatedJobs).forEach(id => {
      if (updatedJobs[id].is_new) {
        updatedJobs[id].is_new = false;
      }
    });

    setJobs(updatedJobs);
    showNotification(`👁️ Marked ${newJobs.length} jobs as read`, 'success');
  };

  const exportData = () => {
    const dataStr = JSON.stringify(jobs, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'jobs_database_export.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  const addExcludedCompany = (company: string) => {
    if (!excludedCompanies.includes(company)) {
      const updated = [...excludedCompanies, company];
      setExcludedCompanies(updated);
      localStorage.setItem(EXCLUDED_COMPANIES_KEY, JSON.stringify(updated));
      showNotification(`🚫 Excluded company: ${company}`, 'success');
    }
  };

  const removeExcludedCompany = (company: string) => {
    const updated = excludedCompanies.filter(c => c !== company);
    setExcludedCompanies(updated);
    localStorage.setItem(EXCLUDED_COMPANIES_KEY, JSON.stringify(updated));
    showNotification(`✅ Removed exclusion for: ${company}`, 'success');
  };

  // Filter out metadata and create clean jobs object
  const cleanJobs = useMemo(() => {
    const filtered = Object.fromEntries(
      Object.entries(jobs).filter(([key, job]) => {
        // Skip metadata entries
        if (key.startsWith('_')) return false;
        
        // Ensure job has required fields
        if (!job.title || !job.company || !job.id) return false;
        
        // Status filter
        if (filters.status === 'applied' && !job.applied) return false;
        if (filters.status === 'not-applied' && job.applied) return false;
        if (filters.status === 'new' && !job.is_new) return false;

        // Search filter
        if (filters.search) {
          const searchTerm = filters.search.toLowerCase();
          const searchFields = [job.title, job.company, job.location].join(' ').toLowerCase();
          if (!searchFields.includes(searchTerm)) return false;
        }

        // Company exclusion filter
        if (excludedCompanies.includes(job.company)) return false;

        return true;
      })
    );
    
    return filtered;
  }, [jobs, filters, excludedCompanies]);

  const stats: JobStats = useMemo(() => {
    const allJobs = Object.values(jobs);
    return {
      total: allJobs.length,
      new: allJobs.filter(job => job.is_new).length,
      existing: allJobs.filter(job => !job.is_new).length,
      applied: allJobs.filter(job => job.applied).length,
      not_applied: allJobs.filter(job => !job.applied).length,
    };
  }, [jobs]);

  // Load jobs on component mount
  useEffect(() => {
    loadJobs();
  }, []);

  // Auto-refresh jobs
  useEffect(() => {
    const interval = setInterval(() => {
      loadJobs(true);
    }, AUTO_REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, [loadJobs]);

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
          <Typography>Loading jobs...</Typography>
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <WorkIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            📊 LinkedIn Job Manager
          </Typography>
          
          {/* Job Loading Status */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mr: 2 }}>
            <Chip
              icon={<DatabaseIcon />}
              label={`${Object.keys(jobs).length} Jobs Loaded`}
              variant="outlined"
              size="small"
            />
            <Chip
              icon={<SyncIcon />}
              label="Database Only"
              color="info"
              variant="outlined"
              size="small"
              title="Jobs loaded from existing database (scraping disabled on Railway)"
            />
          </Box>
          
          {/* Theme Toggle */}
          <IconButton 
            onClick={() => setDarkMode(!darkMode)} 
            color="inherit"
            title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}
          >
            {darkMode ? <LightIcon /> : <DarkIcon />}
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth={false} sx={{ px: 3, py: 2, minHeight: 'calc(100vh - 64px)' }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <StatsCards stats={stats} />

        <JobLoadingInfo jobCount={Object.keys(jobs).length} />

        {/* Debug Info - Remove in production */}
        {process.env.NODE_ENV === 'development' && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              Debug: {Object.keys(jobs).length} total entries, 
              {Object.entries(jobs).filter(([key]) => !key.startsWith('_')).length} jobs,
              API Base: {process.env.REACT_APP_API_URL || 'Same domain'}
            </Typography>
          </Alert>
        )}

        <FilterControls
          filters={filters}
          onFiltersChange={setFilters}
          onRefresh={() => loadJobs()}
          onExport={exportData}
          onMarkAllRead={markAllAsRead}
          onRemoveApplied={removeAppliedJobs}
          onSearch={searchJobs}
          onAddExcludedCompany={addExcludedCompany}
          excludedCompanies={excludedCompanies}
          onRemoveExcludedCompany={removeExcludedCompany}
          isRefreshing={isRefreshing}
          isSearching={isSearching}
        />

        {/* Job Sections with Categories */}
        <JobSections
          jobs={jobs}
          onToggleApplied={toggleJobApplied}
          updatingJobs={updatingJobs}
        />
      </Container>

      <Snackbar
        open={!!notification}
        autoHideDuration={4000}
        onClose={() => setNotification(null)}
      >
        <Alert
          onClose={() => setNotification(null)}
          severity={notification?.severity}
          sx={{ width: '100%' }}
        >
          {notification?.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;
