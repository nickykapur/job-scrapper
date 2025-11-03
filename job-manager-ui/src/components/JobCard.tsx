import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Stack,
  Chip,
  alpha,
} from '@mui/material';
import {
  OpenInNew as OpenInNewIcon,
  Check as CheckIcon,
  Close as RejectIcon,
} from '@mui/icons-material';
import type { Job } from '../types';
import { getCountryFromLocation } from '../utils/countryUtils';

interface JobCardProps {
  job: Job;
  onApplyAndOpen: (jobId: string, jobUrl: string) => void;
  onRejectJob: (jobId: string) => void;
  isUpdating?: boolean;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  onApplyAndOpen,
  onRejectJob,
  isUpdating = false,
}) => {
  const extractedCountry = job.country || getCountryFromLocation(job.location);

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2.5,
        background: 'background.paper',
        border: '1px solid',
        borderColor: (theme) => theme.palette.mode === 'dark' ? '#2a2a2a' : '#e5e7eb',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          borderColor: (theme) => theme.palette.mode === 'dark' ? '#404040' : '#d1d5db',
          boxShadow: (theme) => theme.palette.mode === 'dark'
            ? '0 4px 12px rgba(0,0,0,0.3)'
            : '0 4px 12px rgba(0,0,0,0.08)',
          transform: 'translateY(-2px)',
        },
      }}
    >
      <CardContent sx={{ p: 3, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Company Name */}
        <Typography
          variant="caption"
          sx={{
            fontWeight: 600,
            fontSize: '0.75rem',
            color: 'text.secondary',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            mb: 1
          }}
        >
          {job.company}
        </Typography>

        {/* Job Title */}
        <Typography
          variant="h6"
          sx={{
            fontWeight: 700,
            fontSize: '1rem',
            mb: 2,
            color: 'text.primary',
            lineHeight: 1.4,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {job.title}
        </Typography>

        {/* Job Details */}
        <Stack spacing={1} sx={{ mb: 3, flexGrow: 1 }}>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.8125rem' }}>
              {job.location}
            </Typography>
            {extractedCountry && extractedCountry !== 'Unknown' && (
              <Typography variant="caption" sx={{ fontSize: '0.75rem', fontWeight: 600, color: 'primary.main' }}>
                {extractedCountry}
              </Typography>
            )}
          </Box>

          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.8125rem' }}>
              {job.posted_date}
            </Typography>
            {job.easy_apply && (
              <Chip
                label="Quick Apply"
                size="small"
                sx={{
                  height: 20,
                  bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(16, 185, 129, 0.1)',
                  color: '#10b981',
                  fontSize: '0.65rem',
                  fontWeight: 600,
                  borderRadius: 1,
                }}
              />
            )}
          </Box>
        </Stack>

        {/* Action Buttons */}
        <Box>
          {!job.applied && !job.rejected && (
            <Stack spacing={1.5}>
              <Button
                variant="contained"
                size="medium"
                onClick={() => onApplyAndOpen(job.id, job.job_url)}
                disabled={isUpdating}
                endIcon={<OpenInNewIcon sx={{ fontSize: '1rem' }} />}
                sx={{
                  borderRadius: 2,
                  fontWeight: 600,
                  textTransform: 'none',
                  fontSize: '0.875rem',
                  py: 1.25,
                  background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                  boxShadow: 'none',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                    boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)',
                  },
                }}
              >
                {isUpdating ? 'Processing...' : 'Apply Now'}
              </Button>

              <Button
                variant="text"
                size="medium"
                onClick={() => onRejectJob(job.id)}
                disabled={isUpdating}
                startIcon={<RejectIcon sx={{ fontSize: '1rem' }} />}
                sx={{
                  borderRadius: 2,
                  fontWeight: 500,
                  textTransform: 'none',
                  fontSize: '0.875rem',
                  py: 1,
                  color: 'text.secondary',
                  '&:hover': {
                    color: 'error.main',
                    backgroundColor: (theme) => alpha(theme.palette.error.main, 0.08),
                  },
                }}
              >
                Not Interested
              </Button>
            </Stack>
          )}

          {job.applied && (
            <Button
              variant="contained"
              size="medium"
              disabled
              startIcon={<CheckIcon />}
              sx={{
                borderRadius: 2,
                fontWeight: 600,
                textTransform: 'none',
                fontSize: '0.875rem',
                py: 1.25,
                width: '100%',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              }}
            >
              Applied
            </Button>
          )}

          {job.rejected && (
            <Button
              variant="contained"
              size="medium"
              disabled
              startIcon={<RejectIcon />}
              sx={{
                borderRadius: 2,
                fontWeight: 600,
                textTransform: 'none',
                fontSize: '0.875rem',
                py: 1.25,
                width: '100%',
                background: (theme) => alpha(theme.palette.text.secondary, 0.12),
                color: 'text.secondary',
              }}
            >
              Rejected
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
