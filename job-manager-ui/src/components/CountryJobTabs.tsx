import React, { useState, useMemo } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Badge,
  Typography,
  Card,
  CardContent,
  Grid,
  Stack,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Work as WorkIcon,
  Check as AppliedIcon,
  Schedule as NewIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';
import type { Job } from '../types';
import JobTable from './JobTable';
import { getCountryFromLocation } from '../utils/countryUtils';

interface CountryJobTabsProps {
  jobs: Record<string, Job>;
  onApplyAndOpen: (jobId: string, jobUrl: string) => void;
  onRejectJob: (jobId: string) => void;
  updatingJobs: Set<string>;
}

interface CountryData {
  country: string;
  flag: string;
  color: string;
  jobs: Job[];
  newJobs: number;
  appliedJobs: number;
  totalJobs: number;
}

const CountryJobTabs: React.FC<CountryJobTabsProps> = ({
  jobs,
  onApplyAndOpen,
  onRejectJob,
  updatingJobs,
}) => {
  const [selectedTab, setSelectedTab] = useState('all');

  // Country configuration - Only actively scraped countries
  const countryConfig: Record<string, { flag: string; color: string }> = {
    'Ireland': { flag: '🇮🇪', color: '#4CAF50' },
    'Spain': { flag: '🇪🇸', color: '#FF9800' },
    'Panama': { flag: '🇵🇦', color: '#2196F3' },
    'Chile': { flag: '🇨🇱', color: '#9C27B0' },
    'Netherlands': { flag: '🇳🇱', color: '#E91E63' },
    'Germany': { flag: '🇩🇪', color: '#FF5722' },
    'Sweden': { flag: '🇸🇪', color: '#00BCD4' },
    'Belgium': { flag: '🇧🇪', color: '#FFC107' },
    'Denmark': { flag: '🇩🇰', color: '#F44336' },
  };

  // Process jobs data
  const { countryData, appliedJobs, allActiveJobs } = useMemo(() => {
    const jobsArray = Object.values(jobs).filter((job: any) =>
      typeof job === 'object' && job !== null && !job.id?.startsWith('_')
    );

    // Separate applied and active jobs
    const applied = jobsArray.filter((job: any) => job.applied && !job.rejected);
    const active = jobsArray.filter((job: any) => !job.rejected && !job.applied);

    // Group active jobs by country
    const countryGroups: Record<string, CountryData> = {};

    Object.keys(countryConfig).forEach(country => {
      const countryJobs = active.filter((job: any) =>
        (job.country || getCountryFromLocation(job.location)) === country
      );

      const appliedCountryJobs = jobsArray.filter((job: any) =>
        (job.country || getCountryFromLocation(job.location)) === country && job.applied
      );

      countryGroups[country] = {
        country,
        flag: countryConfig[country].flag,
        color: countryConfig[country].color,
        jobs: countryJobs,
        newJobs: countryJobs.filter((job: any) => job.is_new || job.category === 'new').length,
        appliedJobs: appliedCountryJobs.length,
        totalJobs: countryJobs.length,
      };
    });

    // Filter out countries with no active jobs to apply
    // Only show countries that have jobs available
    const sortedCountries = Object.values(countryGroups)
      .filter(country => country.totalJobs > 0)
      .sort((a, b) => b.totalJobs - a.totalJobs);

    return {
      countryData: sortedCountries,
      appliedJobs: applied,
      allActiveJobs: active,
    };
  }, [jobs, countryConfig]);

  const handleTabChange = (_: React.SyntheticEvent, newValue: string) => {
    setSelectedTab(newValue);
  };

  const CountryStatCard: React.FC<{ data: CountryData }> = ({ data }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent sx={{ p: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <Typography variant="h3" sx={{ fontSize: '2rem' }}>
            {data.flag}
          </Typography>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
              {data.country}
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: data.color }}>
                    {data.totalJobs}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Available
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#4CAF50' }}>
                    {data.newJobs}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    New
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#2196F3' }}>
                    {data.appliedJobs}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Applied
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#FF9800' }}>
                    {Math.round((data.newJobs / data.totalJobs) * 100) || 0}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Fresh
                  </Typography>
                </Box>
              </Grid>
            </Grid>
            <LinearProgress
              variant="determinate"
              value={(data.totalJobs / Math.max(...countryData.map(c => c.totalJobs))) * 100}
              sx={{
                mt: 2,
                height: 6,
                borderRadius: 3,
                bgcolor: 'action.hover',
                '& .MuiLinearProgress-bar': {
                  bgcolor: data.color,
                  borderRadius: 3,
                },
              }}
            />
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );

  const getTabJobs = () => {
    if (selectedTab === 'all') {
      return allActiveJobs;
    } else if (selectedTab === 'applied') {
      return appliedJobs;
    } else {
      const countryInfo = countryData.find(c => c.country === selectedTab);
      return countryInfo ? countryInfo.jobs : [];
    }
  };

  const createJobsObject = (jobsArray: any[]) => {
    const jobsObj: Record<string, any> = {};
    jobsArray.forEach(job => {
      jobsObj[job.id] = job;
    });
    return jobsObj;
  };

  return (
    <Box>
      {/* Country Statistics Overview */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <TrendingIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              Country Job Statistics
            </Typography>
          </Box>

          <Grid container spacing={2}>
            {countryData.map((data) => (
              <Grid item xs={12} md={6} lg={3} key={data.country}>
                <CountryStatCard data={data} />
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Country Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={selectedTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ px: 2 }}
          >
            {/* All Jobs Tab */}
            <Tab
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <WorkIcon fontSize="small" />
                  <Badge badgeContent={allActiveJobs.length} color="primary">
                    <Typography>All Jobs</Typography>
                  </Badge>
                </Box>
              }
              value="all"
            />

            {/* Applied Jobs Tab */}
            <Tab
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <AppliedIcon fontSize="small" />
                  <Badge badgeContent={appliedJobs.length} color="success">
                    <Typography>Applied</Typography>
                  </Badge>
                </Box>
              }
              value="applied"
            />

            {/* Country Tabs - Only show countries with active jobs */}
            {countryData.map((data) => (
              <Tab
                key={data.country}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography>{data.flag}</Typography>
                    <Badge
                      badgeContent={data.totalJobs}
                      color={data.totalJobs > 0 ? "primary" : "default"}
                      sx={{
                        '& .MuiBadge-badge': {
                          bgcolor: data.totalJobs > 0 ? undefined : '#9e9e9e'
                        }
                      }}
                    >
                      <Typography>{data.country}</Typography>
                    </Badge>
                    {data.newJobs > 0 && (
                      <Chip
                        label={data.newJobs}
                        size="small"
                        sx={{
                          bgcolor: '#4CAF5020',
                          color: '#4CAF50',
                          height: 20,
                          fontSize: '0.7rem',
                          fontWeight: 600,
                        }}
                      />
                    )}
                    {data.appliedJobs > 0 && data.totalJobs === 0 && (
                      <Chip
                        label={`${data.appliedJobs} applied`}
                        size="small"
                        sx={{
                          bgcolor: '#2196F320',
                          color: '#2196F3',
                          height: 20,
                          fontSize: '0.65rem',
                          fontWeight: 600,
                        }}
                      />
                    )}
                  </Box>
                }
                value={data.country}
              />
            ))}
          </Tabs>
        </Box>

        {/* Tab Content */}
        <Box sx={{ p: 3 }}>
          {selectedTab === 'applied' ? (
            <Box>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <AppliedIcon sx={{ mr: 1, color: 'success.main' }} />
                Applied Jobs ({appliedJobs.length})
              </Typography>
              <JobTable
                jobs={createJobsObject(appliedJobs)}
                onApplyAndOpen={onApplyAndOpen}
                onRejectJob={onRejectJob}
                updatingJobs={updatingJobs}
              />
            </Box>
          ) : (
            <Box>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <WorkIcon sx={{ mr: 1, color: 'primary.main' }} />
                {selectedTab === 'all' ? 'All Available Jobs' : `${selectedTab} Jobs`} ({getTabJobs().length})
              </Typography>
              {getTabJobs().length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No active jobs for {selectedTab}. Check the Applied tab to see applied jobs.
                  </Typography>
                </Box>
              ) : (
                <JobTable
                  jobs={createJobsObject(getTabJobs())}
                  onApplyAndOpen={onApplyAndOpen}
                  onRejectJob={onRejectJob}
                  updatingJobs={updatingJobs}
                />
              )}
            </Box>
          )}
        </Box>
      </Card>
    </Box>
  );
};

export default CountryJobTabs;