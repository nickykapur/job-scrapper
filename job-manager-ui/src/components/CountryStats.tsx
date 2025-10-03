import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  LinearProgress,
  Chip,
  Stack,
  Divider,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Public as PublicIcon,
  Work as WorkIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { getCountryFromLocation, getCityFromLocation } from '../utils/countryUtils';

interface CountryStatsProps {
  jobs: Record<string, any>;
}

interface CountryData {
  country: string;
  flag: string;
  color: string;
  newJobs: number;
  last24hJobs: number;
  totalJobs: number;
  successRate?: number;
}

const CountryStats: React.FC<CountryStatsProps> = ({ jobs }) => {
  // Country configuration - Only actively scraped countries
  const countryConfig: Record<string, { flag: string; color: string }> = {
    'Ireland': { flag: '🇮🇪', color: '#4CAF50' },
    'Spain': { flag: '🇪🇸', color: '#FF9800' },
    'Germany': { flag: '🇩🇪', color: '#2196F3' },
    'United Kingdom': { flag: '🇬🇧', color: '#9C27B0' },
  };

  // Extract country statistics from jobs
  const getCountryStats = (): CountryData[] => {
    const jobValues = Object.values(jobs).filter((job: any) =>
      typeof job === 'object' && job !== null && !job.id?.startsWith('_')
    );

    const countryStats: Record<string, CountryData> = {};

    // Initialize countries
    Object.keys(countryConfig).forEach(country => {
      countryStats[country] = {
        country,
        flag: countryConfig[country].flag,
        color: countryConfig[country].color,
        newJobs: 0,
        last24hJobs: 0,
        totalJobs: 0,
      };
    });

    // Count jobs by country and category
    jobValues.forEach((job: any) => {
      const country = job.country || getCountryFromLocation(job.location);

      if (!job.rejected) {
        // Initialize country if not in predefined list
        if (!countryStats[country]) {
          countryStats[country] = {
            country,
            flag: country === 'Unknown' ? '🌍' : '🏁', // Default flag
            color: '#607D8B', // Default color
            newJobs: 0,
            last24hJobs: 0,
            totalJobs: 0,
          };
        }

        // Count total jobs for this country
        countryStats[country].totalJobs++;

        // Count specific categories
        if (job.is_new || job.category === 'new') {
          countryStats[country].newJobs++;
        } else if (job.category === 'last_24h') {
          countryStats[country].last24hJobs++;
        }
      }
    });

    // Add success rate from metadata if available
    const metadata = jobs._metadata;
    if (metadata?.country_daily_stats) {
      Object.keys(countryStats).forEach(country => {
        const dailyStats = metadata.country_daily_stats[country];
        if (dailyStats) {
          countryStats[country].successRate = dailyStats.success_rate;
        }
      });
    }

    // Filter out countries with no jobs and sort by total jobs descending
    return Object.values(countryStats)
      .filter(stats => stats.totalJobs > 0)
      .sort((a, b) => b.totalJobs - a.totalJobs);
  };

  const countryData = getCountryStats();
  const maxJobs = Math.max(...countryData.map(c => c.totalJobs), 1);

  if (countryData.length === 0) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <PublicIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
              Country Statistics
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            No country-specific job data available. Run a multi-country search to see statistics.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const totalNewJobs = countryData.reduce((sum, c) => sum + c.newJobs, 0);
  const totalLast24hJobs = countryData.reduce((sum, c) => sum + c.last24hJobs, 0);
  const totalJobs = totalNewJobs + totalLast24hJobs;

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <PublicIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
            Country Job Statistics
          </Typography>
        </Box>

        {/* Overall Stats */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'action.hover', borderRadius: 2 }}>
              <WorkIcon sx={{ color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
                {totalJobs}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Jobs
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.main', color: 'white', borderRadius: 2, opacity: 0.9 }}>
              <TrendingUpIcon sx={{ mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                {totalNewJobs}
              </Typography>
              <Typography variant="body2">
                New Jobs
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'warning.main', color: 'white', borderRadius: 2, opacity: 0.9 }}>
              <ScheduleIcon sx={{ mb: 1 }} />
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                {totalLast24hJobs}
              </Typography>
              <Typography variant="body2">
                Last 24h
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ mb: 3 }} />

        {/* Country Breakdown */}
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
          Country Breakdown
        </Typography>

        <Stack spacing={2}>
          {countryData.map((countryStats) => (
            <Box key={countryStats.country}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body1" sx={{ mr: 1, fontSize: '1.2em' }}>
                    {countryStats.flag}
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 600, minWidth: 140 }}>
                    {countryStats.country}
                  </Typography>
                </Box>
                <Stack direction="row" spacing={1} alignItems="center">
                  {countryStats.newJobs > 0 && (
                    <Chip
                      label={`${countryStats.newJobs} new`}
                      size="small"
                      sx={{ bgcolor: '#4CAF5020', color: '#4CAF50', fontWeight: 600 }}
                    />
                  )}
                  {countryStats.last24hJobs > 0 && (
                    <Chip
                      label={`${countryStats.last24hJobs} 24h`}
                      size="small"
                      sx={{ bgcolor: '#FF980020', color: '#FF9800', fontWeight: 600 }}
                    />
                  )}
                  <Typography variant="body2" sx={{ fontWeight: 700, minWidth: 40, textAlign: 'right' }}>
                    {countryStats.totalJobs}
                  </Typography>
                  {countryStats.successRate !== undefined && (
                    <Typography variant="body2" color="text.secondary" sx={{ minWidth: 40, textAlign: 'right' }}>
                      ({countryStats.successRate}%)
                    </Typography>
                  )}
                </Stack>
              </Box>
              <LinearProgress
                variant="determinate"
                value={(countryStats.totalJobs / maxJobs) * 100}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: 'action.hover',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: countryStats.color,
                    borderRadius: 4,
                  },
                }}
              />
            </Box>
          ))}
        </Stack>

        {/* Spain City Breakdown - Show Madrid vs Barcelona if both have jobs */}
        {(() => {
          const spainJobs = Object.values(jobs).filter((job: any) =>
            typeof job === 'object' && job !== null && !job.id?.startsWith('_') &&
            !job.rejected && (job.country === 'Spain' || getCountryFromLocation(job.location) === 'Spain')
          );

          if (spainJobs.length > 0) {
            const cityStats: Record<string, number> = {};
            spainJobs.forEach((job: any) => {
              const city = getCityFromLocation(job.location);
              cityStats[city] = (cityStats[city] || 0) + 1;
            });

            const cities = Object.entries(cityStats).filter(([_, count]) => count > 0);

            if (cities.length > 1) {
              return (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                    🇪🇸 Spain City Breakdown
                  </Typography>
                  <Stack spacing={1}>
                    {cities.map(([city, count]) => (
                      <Box key={city} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {city === 'Barcelona' ? '🏛️ Barcelona' : city === 'Madrid' ? '🏰 Madrid' : `🏙️ ${city}`}
                        </Typography>
                        <Chip
                          label={`${count} jobs`}
                          size="small"
                          sx={{ bgcolor: '#FF980020', color: '#FF9800', fontWeight: 600 }}
                        />
                      </Box>
                    ))}
                  </Stack>
                </Box>
              );
            }
          }
          return null;
        })()}

        {/* Best Performing Country */}
        {countryData.length > 0 && (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'primary.main', color: 'white', borderRadius: 2, opacity: 0.9 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              🏆 Top Performing Country Today
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              {countryData[0].flag} {countryData[0].country} - {countryData[0].totalJobs} jobs
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default CountryStats;