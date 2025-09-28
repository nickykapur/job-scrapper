import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  Stack,
  Avatar,
  Fade,
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
  const getCompanyInitials = (company: string) => {
    return company
      .split(' ')
      .slice(0, 2)
      .map(word => word[0])
      .join('')
      .toUpperCase();
  };

  const getStatusConfig = () => {
    if (job.applied) {
      return {
        color: '#10b981',
        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        label: 'Applied',
        variant: 'filled' as const,
      };
    }
    if (job.rejected) {
      return {
        color: '#ef4444',
        background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
        label: 'Rejected',
        variant: 'filled' as const,
      };
    }
    if (job.is_new) {
      return {
        color: '#3b82f6',
        background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
        label: 'New',
        variant: 'filled' as const,
      };
    }
    return {
      color: '#64748b',
      background: 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
      label: 'Open',
      variant: 'outlined' as const,
    };
  };

  const statusConfig = getStatusConfig();

  return (
    <Fade in timeout={300}>
      <Card
        sx={{
          mb: 3,
          borderRadius: 4,
          background: (theme) => theme.palette.mode === 'dark'
            ? 'linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 100%)'
            : 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
          border: '1px solid',
          borderColor: (theme) => theme.palette.mode === 'dark' ? '#333' : '#e2e8f0',
          boxShadow: (theme) => theme.palette.mode === 'dark'
            ? '0 4px 24px rgba(0,0,0,0.4)'
            : '0 4px 24px rgba(71,85,105,0.08)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          '&:hover': {
            transform: 'translateY(-8px)',
            boxShadow: (theme) => theme.palette.mode === 'dark'
              ? '0 20px 40px rgba(0,0,0,0.6)'
              : '0 20px 40px rgba(71,85,105,0.15)',
            borderColor: statusConfig.color,
          },
        }}
      >
        {/* Status Accent Bar */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 4,
            background: statusConfig.background,
            zIndex: 1,
          }}
        />

        <CardContent sx={{ p: 4, pt: 5 }}>
          {/* Header */}
          <Box display="flex" alignItems="flex-start" justifyContent="space-between" mb={3}>
            <Box display="flex" alignItems="center" flex={1} minWidth={0}>
              <Avatar
                sx={{
                  width: 56,
                  height: 56,
                  mr: 3,
                  background: statusConfig.background,
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                }}
              >
                {getCompanyInitials(job.company)}
              </Avatar>

              <Box flex={1} minWidth={0}>
                <Typography
                  variant="h5"
                  sx={{
                    fontWeight: 700,
                    fontSize: '1.5rem',
                    mb: 1,
                    color: 'text.primary',
                    lineHeight: 1.2,
                  }}
                >
                  {job.title}
                </Typography>

                <Box display="flex" alignItems="center" mb={1}>
                  <CompanyIcon sx={{ fontSize: 18, mr: 1, color: 'text.secondary' }} />
                  <Typography
                    variant="subtitle1"
                    color="text.secondary"
                    sx={{ fontWeight: 600, fontSize: '1.1rem' }}
                  >
                    {job.company}
                  </Typography>
                </Box>
              </Box>
            </Box>

            <Chip
              label={statusConfig.label}
              variant={statusConfig.variant}
              sx={{
                height: 32,
                fontWeight: 600,
                fontSize: '0.875rem',
                borderRadius: 2,
                background: statusConfig.variant === 'filled' ? statusConfig.background : 'transparent',
                borderColor: statusConfig.color,
                color: statusConfig.variant === 'filled' ? 'white' : statusConfig.color,
                '& .MuiChip-label': {
                  px: 2,
                }
              }}
            />
          </Box>

          {/* Job Details */}
          <Stack direction="row" spacing={4} sx={{ mb: 4 }}>
            <Box display="flex" alignItems="center">
              <LocationIcon sx={{ fontSize: 18, mr: 1, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                {job.location}
              </Typography>
            </Box>
            <Box display="flex" alignItems="center">
              <TimeIcon sx={{ fontSize: 18, mr: 1, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                {job.posted_date}
              </Typography>
            </Box>
          </Stack>

          {/* Action Buttons */}
          <Box display="flex" gap={2}>
            {!job.applied && !job.rejected && (
              <>
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => onApplyAndOpen(job.id, job.job_url)}
                  disabled={isUpdating}
                  startIcon={<OpenInNewIcon />}
                  sx={{
                    flex: 1,
                    borderRadius: 3,
                    fontWeight: 600,
                    textTransform: 'none',
                    py: 1.5,
                    background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                    boxShadow: '0 4px 16px rgba(59,130,246,0.3)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 24px rgba(59,130,246,0.4)',
                    },
                  }}
                >
                  {isUpdating ? 'Processing...' : 'Apply Now'}
                </Button>

                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => onRejectJob(job.id)}
                  disabled={isUpdating}
                  startIcon={<RejectIcon />}
                  sx={{
                    flex: 1,
                    borderRadius: 3,
                    fontWeight: 600,
                    textTransform: 'none',
                    py: 1.5,
                    borderColor: '#ef4444',
                    color: '#ef4444',
                    '&:hover': {
                      borderColor: '#dc2626',
                      color: '#dc2626',
                      backgroundColor: 'rgba(239,68,68,0.04)',
                      transform: 'translateY(-2px)',
                    },
                  }}
                >
                  Not Suitable
                </Button>
              </>
            )}

            {job.applied && (
              <Button
                variant="contained"
                size="large"
                disabled
                startIcon={<CheckIcon />}
                sx={{
                  flex: 1,
                  borderRadius: 3,
                  fontWeight: 600,
                  textTransform: 'none',
                  py: 1.5,
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                }}
              >
                Applied
              </Button>
            )}

            {job.rejected && (
              <Button
                variant="contained"
                size="large"
                disabled
                startIcon={<RejectIcon />}
                sx={{
                  flex: 1,
                  borderRadius: 3,
                  fontWeight: 600,
                  textTransform: 'none',
                  py: 1.5,
                  background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                }}
              >
                Rejected
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>
    </Fade>
  );
};