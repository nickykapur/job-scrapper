import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
// Optimized imports to reduce bundle size
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import toast, { Toaster } from 'react-hot-toast';
import Container from '@mui/material/Container';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';
import IconButton from '@mui/material/IconButton';
import Chip from '@mui/material/Chip';
import Button from '@mui/material/Button';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import useMediaQuery from '@mui/material/useMediaQuery';
import Avatar from '@mui/material/Avatar';
import Divider from '@mui/material/Divider';
// Optimized icon imports to reduce bundle size
import WorkIcon from '@mui/icons-material/Work';
import DarkIcon from '@mui/icons-material/Brightness4';
import LightIcon from '@mui/icons-material/Brightness7';
import SyncIcon from '@mui/icons-material/CloudSync';
import DatabaseIcon from '@mui/icons-material/Storage';
import DashboardIcon from '@mui/icons-material/Dashboard';
import BookmarkIcon from '@mui/icons-material/BookmarkBorder';
import SettingsIcon from '@mui/icons-material/Settings';
import MenuIcon from '@mui/icons-material/Menu';
import TrainingIcon from '@mui/icons-material/School';
import SystemDesignIcon from '@mui/icons-material/Architecture';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import LogoutIcon from '@mui/icons-material/Logout';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import { JobCard } from './components/JobCard';
import { StatsCards } from './components/StatsCards';
import { FilterControls } from './components/FilterControls';
import { JobLoadingInfo } from './components/JobLoadingInfo';
import { JobSections } from './components/JobSections';
import { Training } from './components/Training';
import { SystemDesign } from './components/SystemDesign';
import { Analytics } from './components/Analytics';
import JobSearch from './components/JobSearch';
import CountryStats from './components/CountryStats';
import { jobApi } from './services/api';
import { useAuth } from './contexts/AuthContext';
import type { Job, JobStats, FilterState } from './types';

const createAppTheme = (mode: 'light' | 'dark') => createTheme({
  palette: {
    mode,
    primary: {
      main: mode === 'dark' ? '#90caf9' : '#1976d2',
      light: mode === 'dark' ? '#bbdefb' : '#42a5f5',
      dark: mode === 'dark' ? '#64b5f6' : '#115293',
    },
    secondary: {
      main: mode === 'dark' ? '#f48fb1' : '#9c27b0',
      light: mode === 'dark' ? '#f8bbd9' : '#ba68c8',
      dark: mode === 'dark' ? '#f06292' : '#7b1fa2',
    },
    background: {
      default: mode === 'dark' ? '#121212' : '#fafafa',
      paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
    },
    text: {
      primary: mode === 'dark' ? '#ffffff' : '#212121',
      secondary: mode === 'dark' ? '#aaaaaa' : '#757575',
    },
    success: {
      main: '#4caf50',
      light: '#81c784',
      dark: '#388e3c',
    },
    warning: {
      main: '#ff9800',
      light: '#ffb74d',
      dark: '#f57c00',
    },
    error: {
      main: '#f44336',
      light: '#ef5350',
      dark: '#d32f2f',
    },
    info: {
      main: mode === 'dark' ? '#29b6f6' : '#0288d1',
      light: mode === 'dark' ? '#4fc3f7' : '#03a9f4',
      dark: mode === 'dark' ? '#0277bd' : '#01579b',
    },
    divider: mode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
      fontSize: 'clamp(1.5rem, 4vw, 2rem)',
    },
    h5: {
      fontWeight: 600,
      fontSize: 'clamp(1.25rem, 3vw, 1.5rem)',
    },
    h6: {
      fontWeight: 600,
      fontSize: 'clamp(1.1rem, 2.5vw, 1.25rem)',
    },
    subtitle1: {
      fontWeight: 500,
      fontSize: 'clamp(1rem, 2vw, 1.1rem)',
    },
    body1: {
      fontSize: 'clamp(0.875rem, 1.5vw, 0.95rem)',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: 'clamp(0.8rem, 1.5vw, 0.85rem)',
      lineHeight: 1.5,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          transition: 'all 0.2s ease-in-out',
          border: '1px solid',
          borderColor: mode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          backgroundImage: 'none',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
          textTransform: 'none',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          fontWeight: 500,
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: '1px solid',
          borderColor: mode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
        },
      },
    },
  },
});

const AUTO_REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

const DRAWER_WIDTH = 280;

function App() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [darkMode, setDarkMode] = useState(true); // Default to dark mode
  const [jobs, setJobs] = useState<Record<string, Job>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingJobs, setUpdatingJobs] = useState<Set<string>>(new Set());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [localRejectedCount, setLocalRejectedCount] = useState(0);
  const [notification, setNotification] = useState<{
    message: string;
    severity: 'success' | 'error' | 'info';
  } | null>(null);
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'training' | 'system-design' | 'analytics'>('dashboard');

  // Check if current user is software_admin or has admin access
  const hasAnalyticsAccess = user?.username === 'software_admin' || user?.username === 'admin' || user?.is_admin === true;
  
  // Lazy theme creation to avoid heavy computation on every render
  const theme = useMemo(() => {
    console.log(`[THEME] Creating ${darkMode ? 'dark' : 'light'} theme`);
    return createAppTheme(darkMode ? 'dark' : 'light');
  }, [darkMode]);
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  
  const [filters, setFilters] = useState<FilterState>({
    status: 'all',
    search: '',
    sort: 'newest',
    jobType: 'all',
  });


  const showNotification = (message: string, severity: 'success' | 'error' | 'info' = 'info') => {
    // Use react-hot-toast for better animations
    if (severity === 'success') {
      toast.success(message, {
        duration: 3000,
        position: 'bottom-right',
        style: {
          background: darkMode ? '#1e1e1e' : '#fff',
          color: darkMode ? '#fff' : '#000',
          border: `1px solid ${darkMode ? '#4caf50' : '#4caf50'}`,
        },
        iconTheme: {
          primary: '#4caf50',
          secondary: '#fff',
        },
      });
    } else if (severity === 'error') {
      toast.error(message, {
        duration: 4000,
        position: 'bottom-right',
        style: {
          background: darkMode ? '#1e1e1e' : '#fff',
          color: darkMode ? '#fff' : '#000',
          border: `1px solid ${darkMode ? '#f44336' : '#f44336'}`,
        },
        iconTheme: {
          primary: '#f44336',
          secondary: '#fff',
        },
      });
    } else {
      toast(message, {
        duration: 3000,
        position: 'bottom-right',
        style: {
          background: darkMode ? '#1e1e1e' : '#fff',
          color: darkMode ? '#fff' : '#000',
          border: `1px solid ${darkMode ? '#90caf9' : '#1976d2'}`,
        },
      });
    }
    // Also set for old system compatibility
    setNotification({ message, severity });
  };

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  const toggleDrawer = (open: boolean) => {
    setDrawerOpen(open);
  };

  const loadJobs = useCallback(async (silent = false) => {
    if (!silent) setIsRefreshing(true);
    try {
      console.log('[API] Loading jobs...');
      const jobsData = await jobApi.getJobs();
      console.log('[API] Jobs loaded:', Object.keys(jobsData).length, 'total');

      // Check for rejected jobs in the data
      const rejectedJobs = Object.entries(jobsData).filter(([key, job]) =>
        !key.startsWith('_') && job.rejected === true
      );
      console.log(`[DEBUG] Found ${rejectedJobs.length} rejected jobs in API response`);
      console.log(`[DEBUG] Rejected jobs will be hidden unless viewing 'rejected' filter`);
      if (rejectedJobs.length > 0) {
        console.log('[DEBUG] Rejected jobs:', rejectedJobs.map(([id, job]) => ({
          id,
          title: job.title,
          rejected: job.rejected
        })));
      }

      console.log('[DATA] Jobs data received:', jobsData);

      // Check first job's country data
      const firstJobId = Object.keys(jobsData).find(k => !k.startsWith('_'));
      if (firstJobId) {
        const firstJob = jobsData[firstJobId];
        console.log('[DEBUG] First job data:');
        console.log('  ID:', firstJobId);
        console.log('  Title:', firstJob.title);
        console.log('  Location:', firstJob.location);
        console.log('  Country field:', firstJob.country);
        console.log('  Has country:', !!firstJob.country);
        console.log('  Full job object:', firstJob);
      }

      setJobs(prevJobs => {
        const oldCount = Object.keys(prevJobs).length;
        const newCount = Object.keys(jobsData).length;

        if (!silent && newCount > oldCount && oldCount > 0) {
          showNotification(`${newCount - oldCount} new jobs loaded!`, 'success');
        }

        return jobsData;
      });
      setError(null);
    } catch (err: any) {
      console.error('Failed to load jobs:', err);

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
  }, []);

  const applyAndOpenJob = async (jobId: string, jobUrl: string) => {
    const job = jobs[jobId];
    if (!job) return;

    // Open job URL in new tab
    window.open(jobUrl, '_blank', 'noopener,noreferrer');

    // Mark as applied if not already applied
    if (!job.applied) {
      setUpdatingJobs(prev => new Set(prev).add(jobId));

      // Optimistic update - update UI immediately
      setJobs(prev => ({
        ...prev,
        [jobId]: { ...prev[jobId], applied: true, rejected: false },
      }));

      try {
        await jobApi.updateJob(jobId, true);
        showNotification('Job marked as applied!', 'success');
        // No need to reload - optimistic update already done
      } catch (err) {
        // Revert the optimistic update on error
        setJobs(prev => ({
          ...prev,
          [jobId]: { ...prev[jobId], applied: false },
        }));
        showNotification('Failed to update job status', 'error');
      } finally {
        setUpdatingJobs(prev => {
          const newSet = new Set(prev);
          newSet.delete(jobId);
          return newSet;
        });
      }
    }
  };

  const rejectJob = async (jobId: string) => {
    const job = jobs[jobId];
    if (!job) return;

    setUpdatingJobs(prev => new Set(prev).add(jobId));

    // Optimistic update - update UI immediately
    setJobs(prev => ({
      ...prev,
      [jobId]: { ...prev[jobId], rejected: true, applied: false },
    }));

    try {
      console.log(`[REJECT] Rejecting job ${jobId}...`);
      console.log(`[REJECT] Job data before reject:`, job);

      // Try to reject job via cloud API first
      await jobApi.rejectJob(jobId);

      console.log(`[REJECT] Job ${jobId} rejected successfully via API`);
      showNotification('Job rejected and saved to cloud', 'success');

      // No need to reload - optimistic update already done
    } catch (err) {
      // If cloud API fails, revert the optimistic update
      console.error('[ERROR] Cloud API reject failed:', err);
      console.log(`[REJECT] Reverting optimistic update for job ${jobId}`);

      // Revert the optimistic update
      setJobs(prev => ({
        ...prev,
        [jobId]: { ...prev[jobId], rejected: false },
      }));

      showNotification('Failed to reject job - please try again', 'error');
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
      showNotification('No applied jobs to remove', 'info');
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
      showNotification(`Removed ${appliedJobs.length} applied jobs`, 'success');
    } catch (err) {
      // Update locally even if server fails
      setJobs(newJobsData);
      showNotification(
        `Removed ${appliedJobs.length} applied jobs (local only)`,
        'success'
      );
    }
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
        if (filters.status === 'not-applied' && (job.applied || job.rejected)) return false;
        if (filters.status === 'rejected' && !job.rejected) return false;
        if (filters.status === 'new' && !job.is_new) return false;

        // IMPORTANT: Hide rejected jobs by default unless specifically viewing rejected jobs
        if (filters.status !== 'rejected' && job.rejected) return false;

        // Job type filter
        if (filters.jobType && filters.jobType !== 'all' && job.job_type !== filters.jobType) return false;

        // Search filter
        if (filters.search) {
          const searchTerm = filters.search.toLowerCase();
          const searchFields = [job.title, job.company, job.location].join(' ').toLowerCase();
          if (!searchFields.includes(searchTerm)) return false;
        }

        return true;
      })
    );

    return filtered;
  }, [jobs, filters]);

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

  // Update local rejected count
  const updateLocalRejectedCount = () => {
    const localRejectedJobs = JSON.parse(localStorage.getItem('locally-rejected-jobs') || '[]');
    setLocalRejectedCount(localRejectedJobs.length);
  };

  // Manual sync function
  const manualSyncRejectedJobs = async () => {
    const localRejectedJobs = JSON.parse(localStorage.getItem('locally-rejected-jobs') || '[]');
    if (localRejectedJobs.length === 0) {
      showNotification('No local rejected jobs to sync', 'info');
      return;
    }

    try {
      await jobApi.syncRejectedJobs(localRejectedJobs);
      localStorage.removeItem('locally-rejected-jobs');
      updateLocalRejectedCount();
      showNotification(`Synced ${localRejectedJobs.length} rejected jobs to cloud`, 'success');
    } catch (error) {
      showNotification('Failed to sync rejected jobs to cloud', 'error');
    }
  };

  // Load jobs and sync rejected jobs on component mount
  useEffect(() => {
    loadJobs();
    syncRejectedJobsFromCloud();
    updateLocalRejectedCount();
  }, []);

  // Sync rejected jobs from cloud and merge with local storage
  const syncRejectedJobsFromCloud = async () => {
    try {
      // Get rejected jobs from cloud
      const cloudRejectedJobs = await jobApi.getRejectedJobs();

      // Get locally stored rejected jobs
      const localRejectedJobs = JSON.parse(localStorage.getItem('locally-rejected-jobs') || '[]');

      // Merge cloud and local rejected jobs
      const allRejectedJobs = [...new Set([...cloudRejectedJobs, ...localRejectedJobs])];

      // If we have locally rejected jobs that aren't in the cloud, sync them
      const localOnlyJobs = localRejectedJobs.filter((jobId: string) => !cloudRejectedJobs.includes(jobId));
      if (localOnlyJobs.length > 0) {
        try {
          await jobApi.syncRejectedJobs(localOnlyJobs);
          // Clear local storage since they're now in the cloud
          localStorage.removeItem('locally-rejected-jobs');
          updateLocalRejectedCount();
          showNotification(`Synced ${localOnlyJobs.length} locally rejected jobs to cloud`, 'success');
        } catch (error) {
          console.warn('Failed to sync local rejected jobs to cloud:', error);
        }
      }

      // Update jobs state to reflect rejected status
      if (allRejectedJobs.length > 0) {
        setJobs(prevJobs => {
          const updatedJobs = { ...prevJobs };
          allRejectedJobs.forEach(jobId => {
            if (updatedJobs[jobId]) {
              updatedJobs[jobId] = { ...updatedJobs[jobId], rejected: true };
            }
          });
          return updatedJobs;
        });
      }
    } catch (error) {
      console.warn('Failed to sync rejected jobs from cloud:', error);
    }
  };

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

  const drawerContent = (
    <Box sx={{ width: DRAWER_WIDTH, height: '100%', bgcolor: 'background.paper', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Typography
          variant="h5"
          sx={{
            fontWeight: 800,
            background: (theme) => theme.palette.mode === 'dark'
              ? 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%)'
              : 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '-0.02em',
            mb: 0.5
          }}
        >
          JobHunt
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
          Application Tracker
        </Typography>
      </Box>

      {/* User Info */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', bgcolor: 'action.hover' }}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <Avatar sx={{ width: 40, height: 40, bgcolor: 'primary.main' }}>
            <AccountCircleIcon />
          </Avatar>
          <Box flex={1} minWidth={0}>
            <Typography variant="subtitle2" fontWeight={600} noWrap>
              {user?.username || 'User'}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {user?.email || ''}
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Navigation */}
      <Box sx={{ flex: 1, py: 2 }}>
        <List sx={{ px: 2 }}>
          <ListItem
            button
            selected={currentTab === 'dashboard'}
            onClick={() => setCurrentTab('dashboard')}
            sx={{
              borderRadius: 2,
              mb: 1,
              py: 1.25,
              '&.Mui-selected': {
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(59, 130, 246, 0.1)',
                borderLeft: '3px solid',
                borderColor: 'primary.main',
                '&:hover': {
                  bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(59, 130, 246, 0.15)',
                },
              },
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <ListItemText
              primary="Jobs"
              primaryTypographyProps={{ fontWeight: 600, fontSize: '0.9375rem' }}
            />
          </ListItem>

          <ListItem
            button
            selected={currentTab === 'training'}
            onClick={() => setCurrentTab('training')}
            sx={{
              borderRadius: 2,
              mb: 1,
              py: 1.25,
              '&.Mui-selected': {
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(59, 130, 246, 0.1)',
                borderLeft: '3px solid',
                borderColor: 'primary.main',
                '&:hover': {
                  bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(59, 130, 246, 0.15)',
                },
              },
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <ListItemText
              primary="DSA Training"
              primaryTypographyProps={{ fontWeight: 600, fontSize: '0.9375rem' }}
            />
          </ListItem>

          <ListItem
            button
            selected={currentTab === 'system-design'}
            onClick={() => setCurrentTab('system-design')}
            sx={{
              borderRadius: 2,
              mb: 1,
              py: 1.25,
              '&.Mui-selected': {
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(59, 130, 246, 0.1)',
                borderLeft: '3px solid',
                borderColor: 'primary.main',
                '&:hover': {
                  bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(59, 130, 246, 0.15)',
                },
              },
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <ListItemText
              primary="System Design"
              primaryTypographyProps={{ fontWeight: 600, fontSize: '0.9375rem' }}
            />
          </ListItem>

          {/* Analytics - only for software_admin */}
          {hasAnalyticsAccess && (
            <ListItem
              button
              selected={currentTab === 'analytics'}
              onClick={() => setCurrentTab('analytics')}
              sx={{
                borderRadius: 2,
                mb: 1,
                py: 1.25,
                '&.Mui-selected': {
                  bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(139, 92, 246, 0.15)' : 'rgba(139, 92, 246, 0.1)',
                  borderLeft: '3px solid',
                  borderColor: 'secondary.main',
                  '&:hover': {
                    bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(139, 92, 246, 0.2)' : 'rgba(139, 92, 246, 0.15)',
                  },
                },
                '&:hover': {
                  bgcolor: 'action.hover',
                },
              }}
            >
              <ListItemIcon>
                <AnalyticsIcon sx={{ color: currentTab === 'analytics' ? 'secondary.main' : 'text.secondary' }} />
              </ListItemIcon>
              <ListItemText
                primary="Analytics"
                primaryTypographyProps={{ fontWeight: 600, fontSize: '0.9375rem' }}
              />
              <Chip
                label="Admin"
                size="small"
                sx={{
                  height: 20,
                  fontSize: '0.65rem',
                  bgcolor: 'secondary.main',
                  color: 'white',
                }}
              />
            </ListItem>
          )}
        </List>

        <Divider sx={{ my: 2, mx: 2 }} />

        <Box sx={{ px: 3, py: 2 }}>
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Overview
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Total Jobs
            </Typography>
            <Typography variant="body2" fontWeight={700} color="text.primary">
              {Object.keys(cleanJobs).length}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="text.secondary">
              Applied
            </Typography>
            <Typography variant="body2" fontWeight={700} color="success.main">
              {stats.applied}
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        {/* Sync Button - only show if there are local rejected jobs */}
        {localRejectedCount > 0 && (
          <Button
            fullWidth
            variant="outlined"
            onClick={manualSyncRejectedJobs}
            sx={{
              mb: 1.5,
              borderRadius: 2,
              py: 1,
              borderColor: 'warning.main',
              color: 'warning.main',
              fontWeight: 600,
              fontSize: '0.875rem',
              textTransform: 'none',
              '&:hover': {
                borderColor: 'warning.dark',
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255, 152, 0, 0.1)' : 'rgba(255, 152, 0, 0.05)',
              },
            }}
          >
            Sync {localRejectedCount} Jobs
          </Button>
        )}

        <Button
          fullWidth
          variant="text"
          onClick={() => navigate('/settings')}
          sx={{
            mb: 1,
            borderRadius: 2,
            py: 1,
            fontWeight: 500,
            fontSize: '0.875rem',
            textTransform: 'none',
            justifyContent: 'flex-start',
            color: 'text.primary',
            '&:hover': {
              bgcolor: 'action.hover',
            },
          }}
        >
          Settings
        </Button>

        <Button
          fullWidth
          variant="text"
          onClick={async () => {
            await logout();
            navigate('/login');
          }}
          sx={{
            borderRadius: 2,
            py: 1,
            fontWeight: 500,
            fontSize: '0.875rem',
            textTransform: 'none',
            justifyContent: 'flex-start',
            color: 'text.secondary',
            '&:hover': {
              bgcolor: 'action.hover',
              color: 'error.main',
            },
          }}
        >
          Sign out
        </Button>
      </Box>
    </Box>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
        {/* Navigation Drawer */}
        <Drawer
          variant={isMobile ? 'temporary' : 'persistent'}
          anchor="left"
          open={isMobile ? drawerOpen : true}
          onClose={() => toggleDrawer(false)}
          sx={{
            width: isMobile ? 0 : DRAWER_WIDTH,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: DRAWER_WIDTH,
              boxSizing: 'border-box',
              borderRight: '1px solid',
              borderColor: 'divider',
              position: 'relative',
              height: '100vh',
              overflow: 'auto',
            },
          }}
        >
          {drawerContent}
        </Drawer>

        {/* Main Content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            width: isMobile ? '100%' : `calc(100vw - ${DRAWER_WIDTH}px)`,
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'auto',
          }}
        >
          {/* Top App Bar */}
          <AppBar
            position="static"
            elevation={1}
            sx={{
              width: '100%',
              zIndex: theme.zIndex.drawer - 1,
              bgcolor: 'background.paper',
              color: 'text.primary',
              borderBottom: 1,
              borderColor: 'divider',
            }}
          >
            <Toolbar sx={{ px: 3, py: 1 }}>
              {isMobile && (
                <IconButton
                  edge="start"
                  color="inherit"
                  onClick={() => toggleDrawer(true)}
                  sx={{ mr: 2 }}
                >
                  <MenuIcon />
                </IconButton>
              )}

              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h6" component="div" sx={{ fontWeight: 700, fontSize: '1.125rem' }}>
                  {currentTab === 'dashboard' ? 'Jobs' :
                   currentTab === 'training' ? 'DSA Training' :
                   currentTab === 'system-design' ? 'System Design' : 'Analytics'}
                </Typography>
                {currentTab === 'dashboard' && (
                  <Typography variant="caption" color="text.secondary">
                    {Object.keys(cleanJobs).length} active opportunities
                  </Typography>
                )}
                {currentTab === 'analytics' && (
                  <Typography variant="caption" color="text.secondary">
                    Multi-user insights & statistics
                  </Typography>
                )}
              </Box>

              {/* Theme Toggle */}
              <IconButton
                onClick={toggleDarkMode}
                color="inherit"
                size="medium"
                title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 2,
                  '&:hover': {
                    bgcolor: 'action.hover',
                    borderColor: 'primary.main',
                  },
                }}
              >
                {darkMode ? <LightIcon fontSize="small" /> : <DarkIcon fontSize="small" />}
              </IconButton>
            </Toolbar>
          </AppBar>

          {/* Content Area */}
          <Box sx={{ flexGrow: 1, bgcolor: 'background.default', width: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box
              sx={{
                p: { xs: 1.5, sm: 2, md: 3 },
                flex: 1,
                width: '100%',
                height: '100%',
              }}
            >
              {error && (
                <Alert
                  severity="error"
                  sx={{
                    mb: 3,
                    borderRadius: 2,
                    boxShadow: '0 2px 8px rgba(244,67,54,0.15)'
                  }}
                >
                  {error}
                </Alert>
              )}

              {/* Conditional Content Based on Current Tab */}
              {currentTab === 'dashboard' && (
                <>
                  {/* Job Search */}
                  <JobSearch onSearchComplete={(newJobs) => {
                    if (newJobs > 0) {
                      // Refresh jobs after successful search
                      loadJobs();
                      setNotification({
                        message: `Found ${newJobs} new jobs! Refreshing list...`,
                        severity: 'success'
                      });
                    }
                  }} />

                  {/* Stats Dashboard */}
                  <StatsCards stats={stats} />

                  {/* Country Statistics */}
                  <CountryStats jobs={jobs} />

                  {/* Job Listings */}
                  <JobSections
                    jobs={jobs}
                    onApplyAndOpen={applyAndOpenJob}
                    onRejectJob={rejectJob}
                    updatingJobs={updatingJobs}
                  />
                </>
              )}

              {currentTab === 'training' && <Training />}

              {currentTab === 'system-design' && <SystemDesign />}

              {currentTab === 'analytics' && hasAnalyticsAccess && <Analytics />}
            </Box>
          </Box>
        </Box>

        {/* Notification Snackbar */}
        <Snackbar
          open={!!notification}
          autoHideDuration={4000}
          onClose={() => setNotification(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            onClose={() => setNotification(null)}
            severity={notification?.severity}
            sx={{
              width: '100%',
              borderRadius: 2,
              boxShadow: '0 4px 16px rgba(0,0,0,0.15)'
            }}
          >
            {notification?.message}
          </Alert>
        </Snackbar>

        {/* React Hot Toast Container */}
        <Toaster
          position="bottom-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: darkMode ? '#1e1e1e' : '#fff',
              color: darkMode ? '#fff' : '#000',
              borderRadius: '8px',
              padding: '16px',
              fontSize: '14px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            },
            success: {
              iconTheme: {
                primary: '#4caf50',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#f44336',
                secondary: '#fff',
              },
            },
          }}
        />
      </Box>
    </ThemeProvider>
  );
}

export default App;
