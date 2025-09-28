import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Stack,
} from '@mui/material';
import type { Job } from '../types';
import { JobCard } from './JobCard';

interface JobSectionsProps {
  jobs: Record<string, Job>;
  onApplyAndOpen: (jobId: string, jobUrl: string) => void;
  onRejectJob: (jobId: string) => void;
  updatingJobs: Set<string>;
}

export const JobSections: React.FC<JobSectionsProps> = ({
  jobs,
  onApplyAndOpen,
  onRejectJob,
  updatingJobs,
}) => {
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

  const SectionHeader = ({ title, count }: { title: string; count: number }) => (
    <Box sx={{ mb: 3 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between">
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            color: 'text.primary',
            fontSize: '1.75rem',
          }}
        >
          {title}
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: 'text.secondary',
            fontWeight: 500,
          }}
        >
          {count} {count === 1 ? 'position' : 'positions'}
        </Typography>
      </Stack>
    </Box>
  );

  const renderJobGrid = (jobList: Job[]) => (
    <Grid container spacing={2}>
      {jobList.map((job) => (
        <Grid item xs={12} sm={6} key={job.id}>
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

  // Combine all jobs for a single grid view, but filter out rejected jobs
  const allDisplayJobs = [...newJobs, ...last24hJobs, ...otherJobs].filter(job => !job.rejected);

  return (
    <Box sx={{ width: '100%' }}>
      {allDisplayJobs.length > 0 ? (
        <>
          <SectionHeader title="Available Positions" count={allDisplayJobs.length} />
          {renderJobGrid(allDisplayJobs)}
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