import React from 'react';
import {
  Box,
  Typography,
  Container,
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
    <Paper
      sx={{
        p: 3,
        mb: 4,
        borderRadius: 3,
        background: (theme) => theme.palette.mode === 'dark'
          ? 'linear-gradient(135deg, #1e293b 0%, #334155 100%)'
          : 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
        border: '1px solid',
        borderColor: (theme) => theme.palette.mode === 'dark' ? '#475569' : '#cbd5e1',
      }}
    >
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
        <Box
          sx={{
            px: 2,
            py: 1,
            borderRadius: 2,
            background: (theme) => theme.palette.mode === 'dark'
              ? 'rgba(59,130,246,0.2)'
              : 'rgba(59,130,246,0.1)',
            color: '#3b82f6',
            fontWeight: 600,
            fontSize: '0.875rem',
          }}
        >
          {count} {count === 1 ? 'position' : 'positions'}
        </Box>
      </Stack>
    </Paper>
  );

  const renderJobGrid = (jobList: Job[]) => (
    <Grid container spacing={3}>
      {jobList.map((job) => (
        <Grid item xs={12} key={job.id}>
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

  return (
    <Container maxWidth="lg" sx={{ py: 2 }}>
      {/* New Jobs Section */}
      {newJobs.length > 0 && (
        <Box sx={{ mb: 6 }}>
          <SectionHeader title="New Positions" count={newJobs.length} />
          {renderJobGrid(newJobs)}
        </Box>
      )}

      {/* Last 24 Hours Jobs Section */}
      {last24hJobs.length > 0 && (
        <Box sx={{ mb: 6 }}>
          <SectionHeader title="Recent Listings" count={last24hJobs.length} />
          {renderJobGrid(last24hJobs)}
        </Box>
      )}

      {/* All Other Jobs Section */}
      {otherJobs.length > 0 && (
        <Box sx={{ mb: 6 }}>
          <SectionHeader title="Available Positions" count={otherJobs.length} />
          {renderJobGrid(otherJobs)}
        </Box>
      )}

      {/* Fallback: Show All Jobs if No Categories */}
      {newJobs.length === 0 && last24hJobs.length === 0 && otherJobs.length === 0 && jobValues.length > 0 && (
        <Box sx={{ mb: 6 }}>
          <SectionHeader title="Job Opportunities" count={jobValues.length} />
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{ mb: 4, textAlign: 'center' }}
          >
            Recent positions posted in the last 24 hours
            {allJobValues.length > jobValues.length && ` (${allJobValues.length - jobValues.length} older positions available)`}
          </Typography>
          {renderJobGrid(jobValues)}
        </Box>
      )}

      {/* Empty State */}
      {jobValues.length === 0 && (
        <Paper
          sx={{
            p: 8,
            textAlign: 'center',
            borderRadius: 4,
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
    </Container>
  );
};