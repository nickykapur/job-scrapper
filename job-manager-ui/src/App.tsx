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
  School as TrainingIcon,
  Architecture as SystemDesignIcon,
} from '@mui/icons-material';
import { JobCard } from './components/JobCard';
import { StatsCards } from './components/StatsCards';
import { FilterControls } from './components/FilterControls';
import { JobLoadingInfo } from './components/JobLoadingInfo';
import { JobSections } from './components/JobSections';
import { Training } from './components/Training';
import { SystemDesign } from './components/SystemDesign';
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
  const [notification, setNotification] = useState<{
    message: string;
    severity: 'success' | 'error' | 'info';
  } | null>(null);
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'training' | 'system-design'>('dashboard');
  
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
      // Try to reject job via API
      await jobApi.rejectJob(jobId);
      showNotification('Job marked as rejected', 'info');
    } catch (err) {
      // If API fails, keep the job as rejected locally but show warning
      console.warn('API reject failed, keeping local state:', err);
      showNotification('Job rejected (saved locally)', 'info');
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
              secondary={Object.keys(cleanJobs).length}
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
              secondary={stats.applied}
              primaryTypographyProps={{ fontSize: '0.875rem' }}
              secondaryTypographyProps={{ fontSize: '0.75rem', fontWeight: 600, color: 'success.main' }}
            />
          </ListItem>
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
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
                  onClick={() => setDrawerOpen(true)}
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
                    label={`${Object.keys(cleanJobs).length}`}
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
                onClick={() => setDarkMode(!darkMode)}
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
                  {/* Stats Dashboard */}
                  <StatsCards stats={stats} />

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
