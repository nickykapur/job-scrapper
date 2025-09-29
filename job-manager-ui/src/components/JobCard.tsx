import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Stack,
} from '@mui/material';
import {
  OpenInNew as OpenInNewIcon,
  Check as CheckIcon,
  Close as RejectIcon,
  LocationOn as LocationIcon,
  AccessTime as TimeIcon,
  Business as CompanyIcon,
} from '@mui/icons-material';
import type { Job } from '../types';

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
  // Country flag mapping
  const getCountryFlag = (country: string): string => {
    const flags: Record<string, string> = {
      'Ireland': '🇮🇪',
      'Spain': '🇪🇸',
      'Germany': '🇩🇪',
      'Switzerland': '🇨🇭',
      'United Kingdom': '🇬🇧',
      'Netherlands': '🇳🇱',
      'France': '🇫🇷',
      'Italy': '🇮🇹',
    };
    return flags[country] || '🏳️';
  };
  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2,
        background: (theme) => theme.palette.mode === 'dark'
          ? '#1a1a1a'
          : '#ffffff',
        border: '1px solid',
        borderColor: (theme) => theme.palette.mode === 'dark' ? '#333' : '#e5e7eb',
        boxShadow: (theme) => theme.palette.mode === 'dark'
          ? '0 1px 3px rgba(0,0,0,0.3)'
          : '0 1px 3px rgba(0,0,0,0.1)',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          boxShadow: (theme) => theme.palette.mode === 'dark'
            ? '0 4px 12px rgba(0,0,0,0.4)'
            : '0 4px 12px rgba(0,0,0,0.15)',
          transform: 'translateY(-2px)',
        },
      }}
    >
      <CardContent sx={{ p: 3, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Company Name */}
        <Box display="flex" alignItems="center" mb={1}>
          <CompanyIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ fontWeight: 500, fontSize: '0.875rem' }}
          >
            {job.company}
          </Typography>
        </Box>

        {/* Job Title */}
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            fontSize: '1.125rem',
            mb: 2,
            color: 'text.primary',
            lineHeight: 1.3,
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
          <Box display="flex" alignItems="center">
            <LocationIcon sx={{ fontSize: 14, mr: 0.5, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
              {job.location}
            </Typography>
          </Box>
          {job.country && (
            <Box display="flex" alignItems="center">
              <Typography variant="body2" sx={{ fontSize: '0.8rem', fontWeight: 600, color: 'primary.main' }}>
                {getCountryFlag(job.country)} {job.country}
              </Typography>
            </Box>
          )}
          <Box display="flex" alignItems="center">
            <TimeIcon sx={{ fontSize: 14, mr: 0.5, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
              {job.posted_date}
            </Typography>
          </Box>
        </Stack>

        {/* Action Buttons */}
        <Box>
          {!job.applied && !job.rejected && (
            <Stack spacing={1}>
              <Button
                variant="contained"
                size="small"
                onClick={() => onApplyAndOpen(job.id, job.job_url)}
                disabled={isUpdating}
                startIcon={<OpenInNewIcon />}
                sx={{
                  borderRadius: 1.5,
                  fontWeight: 600,
                  textTransform: 'none',
                  fontSize: '0.875rem',
                  py: 1,
                  background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                  },
                }}
              >
                {isUpdating ? 'Processing...' : 'Apply Now'}
              </Button>

              <Button
                variant="outlined"
                size="small"
                onClick={() => onRejectJob(job.id)}
                disabled={isUpdating}
                startIcon={<RejectIcon />}
                sx={{
                  borderRadius: 1.5,
                  fontWeight: 600,
                  textTransform: 'none',
                  fontSize: '0.875rem',
                  py: 1,
                  borderColor: '#ef4444',
                  color: '#ef4444',
                  '&:hover': {
                    borderColor: '#dc2626',
                    color: '#dc2626',
                    backgroundColor: 'rgba(239,68,68,0.04)',
                  },
                }}
              >
                Not Suitable
              </Button>
            </Stack>
          )}

          {job.applied && (
            <Button
              variant="contained"
              size="small"
              disabled
              startIcon={<CheckIcon />}
              sx={{
                borderRadius: 1.5,
                fontWeight: 600,
                textTransform: 'none',
                fontSize: '0.875rem',
                py: 1,
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
              size="small"
              disabled
              startIcon={<RejectIcon />}
              sx={{
                borderRadius: 1.5,
                fontWeight: 600,
                textTransform: 'none',
                fontSize: '0.875rem',
                py: 1,
                width: '100%',
                background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
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