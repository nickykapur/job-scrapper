import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  IconButton,
  Link,
} from '@mui/material';
import {
  OpenInNew as OpenInNewIcon,
  Check as CheckIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { Job } from '../types';

interface JobCardProps {
  job: Job;
  onToggleApplied: (jobId: string) => void;
  isUpdating?: boolean;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  onToggleApplied,
  isUpdating = false,
}) => {
  const getCardStyle = () => {
    let borderLeft = '4px solid #ddd';
    if (job.is_new) borderLeft = '4px solid #4caf50';
    if (job.applied) borderLeft = '4px solid #2196f3';
    return { borderLeft };
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  return (
    <Card
      sx={{
        mb: 1.5,
        ...getCardStyle(),
        '&:hover': {
          transform: 'translateY(-1px)',
          boxShadow: '0 4px 16px rgba(0,119,181,0.15)',
        },
        transition: 'all 0.2s ease',
        animation: job.is_new ? 'pulse 2s ease-in-out' : 'none',
      }}
    >
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        {/* Header Row */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1.5}>
          <Box flex={1} mr={2}>
            <Typography variant="h6" component="h2" sx={{ fontSize: '1.1rem', fontWeight: 600, mb: 0.5 }}>
              {job.title}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ fontWeight: 500 }}>
              {job.company}
            </Typography>
          </Box>
          
          {/* Status Chips */}
          <Box display="flex" gap={1} alignItems="center">
            {job.is_new && (
              <Chip
                icon={<CheckIcon />}
                label="New"
                size="small"
                color="success"
                variant="filled"
                sx={{ height: 24 }}
              />
            )}
            <Chip
              icon={job.applied ? <CheckIcon /> : <ScheduleIcon />}
              label={job.applied ? 'Applied' : 'Pending'}
              size="small"
              color={job.applied ? 'success' : 'warning'}
              variant={job.applied ? 'filled' : 'outlined'}
              sx={{ height: 24 }}
            />
          </Box>
        </Box>

        {/* Info Row */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1.5}>
          <Box display="flex" gap={3}>
            <Typography variant="body2" color="text.secondary">
              📍 {job.location}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              📅 {job.posted_date}
            </Typography>
          </Box>
          
          {/* Action Buttons */}
          <Box display="flex" gap={1}>
            <Button
              variant={job.applied ? 'contained' : 'outlined'}
              color={job.applied ? 'success' : 'primary'}
              size="small"
              onClick={() => onToggleApplied(job.id)}
              disabled={isUpdating}
              startIcon={job.applied ? <CheckIcon /> : <ScheduleIcon />}
              sx={{ minWidth: 120 }}
            >
              {isUpdating ? 'Updating...' : job.applied ? 'Applied' : 'Mark Applied'}
            </Button>
            <Button
              variant="outlined"
              size="small"
              startIcon={<OpenInNewIcon />}
              component={Link}
              href={job.job_url}
              target="_blank"
              rel="noopener noreferrer"
              sx={{ minWidth: 100 }}
            >
              View Job
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};