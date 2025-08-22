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
        mb: 2,
        ...getCardStyle(),
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 20px rgba(0,119,181,0.2)',
        },
        transition: 'all 0.3s ease',
        animation: job.is_new ? 'pulse 2s ease-in-out' : 'none',
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
          <Box flex={1}>
            <Typography variant="h6" component="h2" gutterBottom>
              {job.title}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" gutterBottom>
              {job.company}
            </Typography>
          </Box>
          <Box display="flex" gap={1} flexWrap="wrap">
            {job.is_new && (
              <Chip
                icon={<CheckIcon />}
                label="New"
                size="small"
                color="success"
                variant="outlined"
              />
            )}
            <Chip
              icon={job.applied ? <CheckIcon /> : <ScheduleIcon />}
              label={job.applied ? 'Applied' : 'Not Applied'}
              size="small"
              color={job.applied ? 'primary' : 'warning'}
              variant="outlined"
            />
          </Box>
        </Box>

        <Box
          display="grid"
          gridTemplateColumns={{ xs: '1fr', sm: 'repeat(2, 1fr)' }}
          gap={1}
          mb={2}
        >
          <Typography variant="body2" color="text.secondary">
            <strong>Location:</strong> {job.location}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Posted:</strong> {job.posted_date}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Job ID:</strong> {job.id}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Scraped:</strong> {formatDate(job.scraped_at)}
          </Typography>
        </Box>

        <Box display="flex" gap={1} flexWrap="wrap">
          <Button
            variant={job.applied ? 'contained' : 'outlined'}
            color={job.applied ? 'success' : 'warning'}
            size="small"
            onClick={() => onToggleApplied(job.id)}
            disabled={isUpdating}
            startIcon={job.applied ? <CheckIcon /> : <ScheduleIcon />}
          >
            {isUpdating ? 'Updating...' : job.applied ? 'Applied' : 'Mark as Applied'}
          </Button>
          <Button
            variant="outlined"
            size="small"
            startIcon={<OpenInNewIcon />}
            component={Link}
            href={job.job_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            View Job
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};