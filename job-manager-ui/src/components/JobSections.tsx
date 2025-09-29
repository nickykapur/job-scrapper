import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Stack,
  Chip,
  ToggleButton,
  ToggleButtonGroup,
  Divider,
} from '@mui/material';
import {
  ViewList as ListViewIcon,
  ViewModule as GridViewIcon,
  TableRows as CompactViewIcon,
  Schedule as TimeViewIcon,
  Public as CountryViewIcon,
} from '@mui/icons-material';
import type { Job } from '../types';
import { JobCard } from './JobCard';

interface JobSectionsProps {
  jobs: Record<string, Job>;
  onApplyAndOpen: (jobId: string, jobUrl: string) => void;
  onRejectJob: (jobId: string) => void;
  updatingJobs: Set<string>;
}

type ViewMode = 'grid' | 'list' | 'compact';
type OrganizationMode = 'time' | 'country';

export const JobSections: React.FC<JobSectionsProps> = ({
  jobs,
  onApplyAndOpen,
  onRejectJob,
  updatingJobs,
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [organizationMode, setOrganizationMode] = useState<OrganizationMode>('time');
  // Function to check if job was posted within last 24 hours
  const isWithin24Hours = (postedDate: string): boolean => {
    if (!postedDate) return false;

    const normalizedDate = postedDate.toLowerCase().trim();

    // Handle "X hours ago" - these are definitely within 24 hours
    if (normalizedDate.includes('hour') && normalizedDate.includes('ago')) {
      return true;
    }

    // Handle "1 day ago" - this is exactly 24 hours
    if (normalizedDate === '1 day ago') {
      return true;
    }

    // Handle "X days ago" - anything more than 1 day is outside 24 hours
    if (normalizedDate.includes('day') && normalizedDate.includes('ago')) {
      const match = normalizedDate.match(/(\d+)\s+days?\s+ago/);
      if (match) {
        const days = parseInt(match[1]);
        return days <= 1;
      }
    }

    // Handle "today" or similar
    if (normalizedDate.includes('today') || normalizedDate.includes('now')) {
      return true;
    }

    // Default to false for unparseable dates
    return false;
  };

  // Filter out metadata and categorize jobs, then filter by 24 hours
  const jobEntries = Object.entries(jobs).filter(([key]) => !key.startsWith('_'));
  const allJobValues = jobEntries.map(([, job]) => job);

  // Filter to show only jobs posted in last 24 hours
  const jobValues = allJobValues.filter(job => isWithin24Hours(job.posted_date));

  const newJobs = jobValues.filter(job => job.category === 'new');
  const last24hJobs = jobValues.filter(job => job.category === 'last_24h');
  const otherJobs = jobValues.filter(job => !job.category || job.category === 'existing');

  const SectionHeader = ({ title, count, color = '#2196F3' }: { title: string; count: number; color?: string }) => (
    <Box sx={{ mb: 2 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between">
        <Stack direction="row" alignItems="center" spacing={2}>
          <Typography
            variant="h5"
            sx={{
              fontWeight: 700,
              color: 'text.primary',
              fontSize: '1.25rem',
            }}
          >
            {title}
          </Typography>
          <Chip
            label={`${count} ${count === 1 ? 'job' : 'jobs'}`}
            size="small"
            sx={{
              bgcolor: `${color}20`,
              color: color,
              fontWeight: 600
            }}
          />
        </Stack>
      </Stack>
    </Box>
  );

  const getGridProps = () => {
    switch (viewMode) {
      case 'grid':
        return { xs: 12, sm: 6, lg: 4 };
      case 'list':
        return { xs: 12 };
      case 'compact':
        return { xs: 12, sm: 6, md: 4, lg: 3 };
      default:
        return { xs: 12, sm: 6 };
    }
  };

  const renderJobGrid = (jobList: Job[]) => (
    <Grid container spacing={viewMode === 'compact' ? 1.5 : 2}>
      {jobList.map((job) => (
        <Grid item {...getGridProps()} key={job.id}>
          <JobCard
            job={job}
            onApplyAndOpen={onApplyAndOpen}
            onRejectJob={onRejectJob}
            isUpdating={updatingJobs.has(job.id)}
          />
        </Grid>
      ))}
    </Grid>
  );

  // Filter out rejected jobs from all categories
  const displayNewJobs = newJobs.filter(job => !job.rejected);
  const displayLast24hJobs = last24hJobs.filter(job => !job.rejected);
  const displayOtherJobs = otherJobs.filter(job => !job.rejected);
  const allDisplayJobs = [...displayNewJobs, ...displayLast24hJobs, ...displayOtherJobs];

  // Organize jobs by country
  const jobsByCountry = allDisplayJobs.reduce((acc, job) => {
    const country = job.country || 'Unknown';
    if (!acc[country]) {
      acc[country] = [];
    }
    acc[country].push(job);
    return acc;
  }, {} as Record<string, Job[]>);

  // Country flag mapping
  const countryFlags: Record<string, string> = {
    'Ireland': '🇮🇪',
    'Spain': '🇪🇸',
    'Germany': '🇩🇪',
    'Switzerland': '🇨🇭',
    'United Kingdom': '🇬🇧',
    'Netherlands': '🇳🇱',
    'France': '🇫🇷',
    'Italy': '🇮🇹',
    'Unknown': '🌍'
  };

  // Country colors
  const countryColors: Record<string, string> = {
    'Ireland': '#4CAF50',
    'Spain': '#FF9800',
    'Germany': '#2196F3',
    'Switzerland': '#E91E63',
    'United Kingdom': '#9C27B0',
    'Netherlands': '#FF5722',
    'France': '#3F51B5',
    'Italy': '#795548',
    'Unknown': '#607D8B'
  };

  const handleViewModeChange = (_: React.MouseEvent<HTMLElement>, newMode: ViewMode) => {
    if (newMode !== null) {
      setViewMode(newMode);
    }
  };

  const handleOrganizationModeChange = (_: React.MouseEvent<HTMLElement>, newMode: OrganizationMode) => {
    if (newMode !== null) {
      setOrganizationMode(newMode);
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {allDisplayJobs.length > 0 ? (
        <>
          {/* Header with View Controls */}
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontSize: '1.75rem',
              }}
            >
              Job Listings
            </Typography>

            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              {/* Organization Mode Toggle */}
              <ToggleButtonGroup
                value={organizationMode}
                exclusive
                onChange={handleOrganizationModeChange}
                size="small"
                sx={{ bgcolor: 'background.paper', boxShadow: 1 }}
              >
                <ToggleButton value="time" aria-label="organize by time">
                  <TimeViewIcon fontSize="small" />
                </ToggleButton>
                <ToggleButton value="country" aria-label="organize by country">
                  <CountryViewIcon fontSize="small" />
                </ToggleButton>
              </ToggleButtonGroup>

              {/* View Mode Toggle */}
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={handleViewModeChange}
                size="small"
                sx={{ bgcolor: 'background.paper', boxShadow: 1 }}
              >
                <ToggleButton value="grid" aria-label="grid view">
                  <GridViewIcon fontSize="small" />
                </ToggleButton>
                <ToggleButton value="list" aria-label="list view">
                  <ListViewIcon fontSize="small" />
                </ToggleButton>
                <ToggleButton value="compact" aria-label="compact view">
                  <CompactViewIcon fontSize="small" />
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
          </Box>

          <Stack spacing={4}>
            {organizationMode === 'time' ? (
              <>
                {/* Time-based organization */}
                {displayNewJobs.length > 0 && (
                  <Box>
                    <SectionHeader title="🆕 New Jobs" count={displayNewJobs.length} color="#4CAF50" />
                    {renderJobGrid(displayNewJobs)}
                  </Box>
                )}

                {displayLast24hJobs.length > 0 && (
                  <Box>
                    <SectionHeader title="⏰ Posted Today" count={displayLast24hJobs.length} color="#FF9800" />
                    {renderJobGrid(displayLast24hJobs)}
                  </Box>
                )}

                {displayOtherJobs.length > 0 && (
                  <Box>
                    <SectionHeader title="📋 Other Positions" count={displayOtherJobs.length} color="#9C27B0" />
                    {renderJobGrid(displayOtherJobs)}
                  </Box>
                )}
              </>
            ) : (
              <>
                {/* Country-based organization */}
                {Object.entries(jobsByCountry)
                  .sort(([a], [b]) => a.localeCompare(b))
                  .map(([country, countryJobs]) => (
                    <Box key={country}>
                      <SectionHeader
                        title={`${countryFlags[country] || '🌍'} ${country}`}
                        count={countryJobs.length}
                        color={countryColors[country] || '#607D8B'}
                      />
                      {renderJobGrid(countryJobs)}
                    </Box>
                  ))}
              </>
            )}
          </Stack>
        </>
      ) : (
        /* Empty State */
        <Paper
          sx={{
            p: 8,
            textAlign: 'center',
            borderRadius: 3,
            background: (theme) => theme.palette.mode === 'dark'
              ? 'linear-gradient(135deg, #1e293b 0%, #334155 100%)'
              : 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
            border: '2px dashed',
            borderColor: (theme) => theme.palette.mode === 'dark' ? '#475569' : '#cbd5e1',
          }}
        >
          <Typography variant="h5" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
            No Recent Positions Found
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {allJobValues.length > 0
              ? `${allJobValues.length} total positions in database, but none posted within 24 hours`
              : 'No job listings available. Try running the job search to populate your database.'
            }
          </Typography>
        </Paper>
      )}
    </Box>
  );
};