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
  Avatar,
  Button,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  useMediaQuery,
} from '@mui/material';
import { 
  Work as WorkIcon, 
  Brightness4 as DarkIcon,
  Brightness7 as LightIcon,
  CloudSync as SyncIcon,
  Storage as DatabaseIcon,
  Dashboard as DashboardIcon,
  BookmarkBorder as BookmarkIcon,
  Settings as SettingsIcon,
  Person as PersonIcon,
  Menu as MenuIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { JobCard } from './components/JobCard';
import { StatsCards } from './components/StatsCards';
import { FilterControls } from './components/FilterControls';
import { JobLoadingInfo } from './components/JobLoadingInfo';
import { JobSections } from './components/JobSections';
import { jobApi } from './services/api';
import type { Job, JobStats, FilterState } from './types';

const createAppTheme = (mode: 'light' | 'dark') => createTheme({
  palette: {
    mode,
    primary: {
      main: mode === 'dark' ? '#1976d2' : '#0066cc',
      light: mode === 'dark' ? '#42a5f5' : '#3399ff',
      dark: mode === 'dark' ? '#115293' : '#004499',
    },
    secondary: {
      main: '#00bcd4',
      light: '#4dd0e1',
      dark: '#0097a7',
    },
    background: {
      default: mode === 'dark' ? '#121212' : '#f5f7fa',
      paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
    },
    text: {
      primary: mode === 'dark' ? '#ffffff' : '#2c3e50',
      secondary: mode === 'dark' ? '#b0bec5' : '#546e7a',
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
          backgroundColor: mode === 'dark' ? '#1e1e1e' : '#ffffff',
          borderRadius: 12,
          border: mode === 'dark' ? '1px solid #333333' : '1px solid #e0e0e0',
          transition: 'all 0.3s ease-in-out',
          boxShadow: mode === 'dark' 
            ? '0 4px 20px rgba(0,0,0,0.3)' 
            : '0 2px 12px rgba(0,0,0,0.08)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: mode === 'dark'
              ? '0 8px 32px rgba(0,0,0,0.4)'
              : '0 4px 24px rgba(0,0,0,0.12)',
          },
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
          borderRadius: 8,
          fontWeight: 600,
          textTransform: 'none',
          padding: '8px 16px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: mode === 'dark' 
              ? '0 4px 12px rgba(25,118,210,0.3)' 
              : '0 4px 12px rgba(0,102,204,0.2)',
          },
        },
        containedPrimary: {
          background: mode === 'dark' 
            ? 'linear-gradient(45deg, #1976d2, #42a5f5)' 
            : 'linear-gradient(45deg, #0066cc, #3399ff)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: mode === 'dark' ? '#1e1e1e' : '#ffffff',
          color: mode === 'dark' ? '#ffffff' : '#2c3e50',
          boxShadow: mode === 'dark' 
            ? '0 2px 8px rgba(0, 0, 0, 0.4)' 
            : '0 1px 4px rgba(0, 0, 0, 0.1)',
          borderBottom: mode === 'dark' ? '1px solid #333333' : '1px solid #e0e0e0',
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
  const [notification, setNotification] = useState<{
    message: string;
    severity: 'success' | 'error' | 'info';
  } | null>(null);
  
  const theme = useMemo(() => createAppTheme(darkMode ? 'dark' : 'light'), [darkMode]);
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [filters, setFilters] = useState<FilterState>({
    status: 'all',
    search: '',
    sort: 'newest',
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
        showNotification(`${newCount - oldCount} new jobs loaded!`, 'success');
      }
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
  }, [jobs]);

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
      await jobApi.rejectJob(jobId);
      showNotification('Job marked as rejected', 'info');
    } catch (err) {
      // Revert the optimistic update on error
      setJobs(prev => ({
        ...prev,
        [jobId]: { ...prev[jobId], rejected: false },
      }));
      showNotification('Failed to reject job', 'error');
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

  const drawerContent = (
    <Box sx={{ width: DRAWER_WIDTH, height: '100%', bgcolor: 'background.paper' }}>
      <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
            <PersonIcon />
          </Avatar>
          <Box>
            <Typography variant="subtitle1" fontWeight="600">
              Professional
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Software Engineer
            </Typography>
          </Box>
        </Box>
      </Box>

      <List sx={{ py: 1 }}>
        <ListItem button selected>
          <ListItemIcon>
            <DashboardIcon color="primary" />
          </ListItemIcon>
          <ListItemText 
            primary="Dashboard" 
            primaryTypographyProps={{ fontWeight: 600 }}
          />
        </ListItem>
        
        <ListItem button>
          <ListItemIcon>
            <WorkIcon />
          </ListItemIcon>
          <ListItemText primary="All Jobs" />
          <Chip label={Object.keys(cleanJobs).length} size="small" />
        </ListItem>
        
        <ListItem button>
          <ListItemIcon>
            <BookmarkIcon />
          </ListItemIcon>
          <ListItemText primary="Applied" />
          <Chip label={stats.applied} size="small" color="success" />
        </ListItem>
        
        <Divider sx={{ my: 1 }} />
        
        <ListItem button>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem>
      </List>
    </Box>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', minHeight: '100vh', width: '100vw', overflow: 'hidden' }}>
        {/* Navigation Drawer */}
        <Drawer
          variant={isMobile ? 'temporary' : 'persistent'}
          anchor="left"
          open={isMobile ? drawerOpen : true}
          onClose={() => setDrawerOpen(false)}
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
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'auto',
          }}
        >
          {/* Top App Bar */}
          <AppBar 
            position="static" 
            elevation={0}
            sx={{ 
              width: '100%',
              zIndex: theme.zIndex.drawer - 1,
            }}
          >
            <Toolbar sx={{ px: 3 }}>
              {isMobile && (
                <IconButton
                  edge="start"
                  color="inherit"
                  onClick={() => setDrawerOpen(true)}
                  sx={{ mr: 2 }}
                >
                  <MenuIcon />
                </IconButton>
              )}
              
              <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 700 }}>
                Career Portal
              </Typography>
              
              {/* Status Indicators */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mr: 2 }}>
                <Chip
                  icon={<DatabaseIcon />}
                  label={`${Object.keys(cleanJobs).length} Positions`}
                  variant="outlined"
                  size="small"
                  color="primary"
                />
                <Chip
                  icon={<SyncIcon />}
                  label={stats.new > 0 ? `${stats.new} New` : 'Updated'}
                  color={stats.new > 0 ? 'success' : 'info'}
                  variant="outlined"
                  size="small"
                />
              </Box>
              
              {/* Theme Toggle */}
              <IconButton 
                onClick={() => setDarkMode(!darkMode)} 
                color="inherit"
                size="large"
                title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}
                sx={{
                  border: '1px solid',
                  borderColor: 'rgba(255,255,255,0.2)',
                  '&:hover': {
                    borderColor: 'rgba(255,255,255,0.4)',
                  }
                }}
              >
                {darkMode ? <LightIcon /> : <DarkIcon />}
              </IconButton>
            </Toolbar>
          </AppBar>

          {/* Content Area */}
          <Box sx={{ flexGrow: 1, bgcolor: 'background.default', width: '100%' }}>
            <Box
              sx={{ 
                py: 3,
                px: 3,
                minHeight: 'calc(100vh - 64px)',
                width: '100%',
                maxWidth: 'none',
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

              {/* Stats Dashboard */}
              <StatsCards stats={stats} />


              {/* Job Listings */}
              <JobSections
                jobs={jobs}
                onApplyAndOpen={applyAndOpenJob}
                onRejectJob={rejectJob}
                updatingJobs={updatingJobs}
              />
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
