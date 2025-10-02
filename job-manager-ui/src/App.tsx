import React, { useState, useEffect, useCallback, useMemo } from 'react';
// Optimized imports to reduce bundle size
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
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
import { JobCard } from './components/JobCard';
import { StatsCards } from './components/StatsCards';
import { FilterControls } from './components/FilterControls';
import { JobLoadingInfo } from './components/JobLoadingInfo';
import { JobSections } from './components/JobSections';
import { Training } from './components/Training';
import { SystemDesign } from './components/SystemDesign';
import JobSearch from './components/JobSearch';
import CountryStats from './components/CountryStats';
import { jobApi } from './services/api';
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
      fontSize: '2rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    subtitle1: {
      fontWeight: 500,
      fontSize: '1.1rem',
    },
    body1: {
      fontSize: '0.95rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.85rem',
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
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'training' | 'system-design'>('dashboard');
  
  // Lazy theme creation to avoid heavy computation on every render
  const theme = useMemo(() => {
    console.log(`🎨 Creating ${darkMode ? 'dark' : 'light'} theme`);
    return createAppTheme(darkMode ? 'dark' : 'light');
  }, [darkMode]);
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Memoize drawer stats to avoid recalculating on every render
  const drawerStats = useMemo(() => ({
    totalJobs: Object.keys(cleanJobs).length,
    appliedJobs: stats.applied
  }), [cleanJobs, stats.applied]);
  
  const [filters, setFilters] = useState<FilterState>({
    status: 'all',
    search: '',
    sort: 'newest',
  });


  const showNotification = useCallback((message: string, severity: 'success' | 'error' | 'info' = 'info') => {
    setNotification({ message, severity });
  }, []);

  const toggleDarkMode = useCallback(() => {
    setDarkMode(prev => !prev);
  }, []);

  const toggleDrawer = useCallback((open: boolean) => {
    setDrawerOpen(open);
  }, []);

  const loadJobs = useCallback(async (silent = false) => {
    if (!silent) setIsRefreshing(true);
    try {
      console.log('🔄 Loading jobs from API...');
      const jobsData = await jobApi.getJobs();
      console.log('✅ Jobs loaded successfully:', Object.keys(jobsData).length, 'jobs');

      // DEBUG: Check for rejected jobs in the data
      const rejectedJobs = Object.entries(jobsData).filter(([key, job]) =>
        !key.startsWith('_') && job.rejected === true
      );
      console.log(`🚫 DEBUG: Found ${rejectedJobs.length} rejected jobs in API response`);
      if (rejectedJobs.length > 0) {
        console.log('🚫 DEBUG: Rejected jobs:', rejectedJobs.map(([id, job]) => ({
          id,
          title: job.title,
          rejected: job.rejected
        })));
      }

      console.log('📋 Jobs data received:', jobsData);

      // DEBUG: Check first job's country data
      const firstJobId = Object.keys(jobsData).find(k => !k.startsWith('_'));
      if (firstJobId) {
        const firstJob = jobsData[firstJobId];
        console.log('🔍 DEBUG - First job data:');
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

  const applyAndOpenJob = useCallback(async (jobId: string, jobUrl: string) => {
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
  }, [jobs]);

  const rejectJob = useCallback(async (jobId: string) => {
    const job = jobs[jobId];
    if (!job) return;

    setUpdatingJobs(prev => new Set(prev).add(jobId));

    // Optimistic update - update UI immediately
    setJobs(prev => ({
      ...prev,
      [jobId]: { ...prev[jobId], rejected: true, applied: false },
    }));

    try {
      console.log(`🚫 DEBUG: Rejecting job ${jobId}...`);
      console.log(`🚫 DEBUG: Job data before reject:`, job);

      // Try to reject job via cloud API first
      await jobApi.rejectJob(jobId);

      console.log(`✅ DEBUG: Job ${jobId} rejected successfully via API`);
      showNotification('Job rejected and saved to cloud', 'success');

      // No need to reload - optimistic update already done
    } catch (err) {
      // If cloud API fails, revert the optimistic update
      console.error('❌ DEBUG: Cloud API reject failed:', err);
      console.log(`🔄 DEBUG: Reverting optimistic update for job ${jobId}`);

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
  }, [jobs]);

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



  // Combined filtering and stats calculation for better performance
  const { cleanJobs, stats } = useMemo(() => {
    const searchTerm = filters.search?.toLowerCase();
    const filteredJobs: Record<string, Job> = {};

    // Stats counters
    let totalCount = 0;
    let newCount = 0;
    let appliedCount = 0;
    let filteredCount = 0;

    // Single iteration through all jobs
    for (const [key, job] of Object.entries(jobs)) {
      // Skip metadata entries
      if (key.startsWith('_')) continue;

      // Count for stats (all valid jobs)
      if (job.title && job.company && job.id) {
        totalCount++;
        if (job.is_new) newCount++;
        if (job.applied) appliedCount++;

        // Apply filters
        let passesFilter = true;

        // Status filter
        if (filters.status === 'applied' && !job.applied) passesFilter = false;
        else if (filters.status === 'not-applied' && (job.applied || job.rejected)) passesFilter = false;
        else if (filters.status === 'rejected' && !job.rejected) passesFilter = false;
        else if (filters.status === 'new' && !job.is_new) passesFilter = false;

        // Search filter (only check if we haven't already failed)
        if (passesFilter && searchTerm) {
          const searchFields = `${job.title} ${job.company} ${job.location}`.toLowerCase();
          if (!searchFields.includes(searchTerm)) passesFilter = false;
        }

        if (passesFilter) {
          filteredJobs[key] = job;
          filteredCount++;
        }
      }
    }

    const jobStats: JobStats = {
      total: totalCount,
      new: newCount,
      existing: totalCount - newCount,
      applied: appliedCount,
      not_applied: totalCount - appliedCount,
    };

    console.log(`🔍 Performance: Filtered ${filteredCount}/${totalCount} jobs in single pass`);

    return { cleanJobs: filteredJobs, stats: jobStats };
  }, [jobs, filters]);

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
        <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main', mb: 0.5 }}>
          Career Portal
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Job Management & Training
        </Typography>
      </Box>

      {/* Navigation */}
      <Box sx={{ flex: 1, py: 1 }}>
        <Typography variant="overline" sx={{ px: 3, py: 1, color: 'text.secondary', fontWeight: 600, fontSize: '0.75rem' }}>
          MAIN
        </Typography>

        <List sx={{ px: 1 }}>
          <ListItem
            button
            selected={currentTab === 'dashboard'}
            onClick={() => setCurrentTab('dashboard')}
            sx={{
              borderRadius: 2,
              mb: 0.5,
              mx: 1,
              '&.Mui-selected': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                '& .MuiListItemIcon-root': {
                  color: 'primary.contrastText',
                },
              },
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <DashboardIcon />
            </ListItemIcon>
            <ListItemText
              primary="Dashboard"
              primaryTypographyProps={{ fontWeight: 500, fontSize: '0.875rem' }}
            />
          </ListItem>

          <ListItem
            button
            selected={currentTab === 'training'}
            onClick={() => setCurrentTab('training')}
            sx={{
              borderRadius: 2,
              mb: 0.5,
              mx: 1,
              '&.Mui-selected': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                '& .MuiListItemIcon-root': {
                  color: 'primary.contrastText',
                },
              },
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <TrainingIcon />
            </ListItemIcon>
            <ListItemText
              primary="DSA Training"
              primaryTypographyProps={{ fontWeight: 500, fontSize: '0.875rem' }}
            />
          </ListItem>

          <ListItem
            button
            selected={currentTab === 'system-design'}
            onClick={() => setCurrentTab('system-design')}
            sx={{
              borderRadius: 2,
              mb: 0.5,
              mx: 1,
              '&.Mui-selected': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                '& .MuiListItemIcon-root': {
                  color: 'primary.contrastText',
                },
              },
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <SystemDesignIcon />
            </ListItemIcon>
            <ListItemText
              primary="System Design"
              primaryTypographyProps={{ fontWeight: 500, fontSize: '0.875rem' }}
            />
          </ListItem>
        </List>

        <Typography variant="overline" sx={{ px: 3, py: 1, color: 'text.secondary', fontWeight: 600, fontSize: '0.75rem', mt: 2 }}>
          OVERVIEW
        </Typography>

        <List sx={{ px: 1 }}>
          <ListItem sx={{ borderRadius: 2, mx: 1, py: 1 }}>
            <ListItemIcon sx={{ minWidth: 40 }}>
              <WorkIcon color="action" />
            </ListItemIcon>
            <ListItemText
              primary="Total Jobs"
              secondary={drawerStats.totalJobs}
              primaryTypographyProps={{ fontSize: '0.875rem' }}
              secondaryTypographyProps={{ fontSize: '0.75rem', fontWeight: 600 }}
            />
          </ListItem>

          <ListItem sx={{ borderRadius: 2, mx: 1, py: 1 }}>
            <ListItemIcon sx={{ minWidth: 40 }}>
              <BookmarkIcon color="success" />
            </ListItemIcon>
            <ListItemText
              primary="Applied"
              secondary={drawerStats.appliedJobs}
              primaryTypographyProps={{ fontSize: '0.875rem' }}
              secondaryTypographyProps={{ fontSize: '0.75rem', fontWeight: 600, color: 'success.main' }}
            />
          </ListItem>
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        {/* Sync Button - only show if there are local rejected jobs */}
        {localRejectedCount > 0 && (
          <ListItem
            button
            onClick={manualSyncRejectedJobs}
            sx={{
              borderRadius: 2,
              mb: 1,
              bgcolor: 'warning.light',
              '&:hover': {
                bgcolor: 'warning.main',
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <CloudUploadIcon color="warning" />
            </ListItemIcon>
            <ListItemText
              primary={`Sync ${localRejectedCount} Local Jobs`}
              primaryTypographyProps={{ fontSize: '0.875rem', fontWeight: 600 }}
              secondary="Tap to sync to cloud"
              secondaryTypographyProps={{ fontSize: '0.75rem' }}
            />
          </ListItem>
        )}

        <ListItem
          button
          sx={{
            borderRadius: 2,
            '&:hover': {
              bgcolor: 'action.hover',
            },
          }}
        >
          <ListItemIcon sx={{ minWidth: 40 }}>
            <SettingsIcon color="action" />
          </ListItemIcon>
          <ListItemText
            primary="Settings"
            primaryTypographyProps={{ fontSize: '0.875rem' }}
          />
        </ListItem>
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

              <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
                {currentTab === 'dashboard' ? 'Job Dashboard' :
                 currentTab === 'training' ? 'DSA Training' : 'System Design'}
              </Typography>

              {/* Status Indicators */}
              {currentTab === 'dashboard' && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mr: 2 }}>
                  <Chip
                    icon={<DatabaseIcon />}
                    label={`${drawerStats.totalJobs}`}
                    variant="outlined"
                    size="small"
                    sx={{ height: 24, fontSize: '0.75rem' }}
                  />
                  {stats.new > 0 && (
                    <Chip
                      icon={<SyncIcon />}
                      label={`${stats.new} New`}
                      color="success"
                      variant="filled"
                      size="small"
                      sx={{ height: 24, fontSize: '0.75rem' }}
                    />
                  )}
                </Box>
              )}

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
                p: 3,
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
      </Box>
    </ThemeProvider>
  );
}

export default App;
