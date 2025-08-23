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
  Avatar,
  Stack,
  Divider,
} from '@mui/material';
import {
  OpenInNew as OpenInNewIcon,
  Check as CheckIcon,
  Schedule as ScheduleIcon,
  LocationOn as LocationIcon,
  AccessTime as TimeIcon,
  Business as CompanyIcon,
  BookmarkBorder as BookmarkBorderIcon,
  Bookmark as BookmarkIcon,
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
  const getCompanyInitials = (company: string) => {
    return company
      .split(' ')
      .slice(0, 2)
      .map(word => word[0])
      .join('')
      .toUpperCase();
  };

  const getStatusColor = () => {
    if (job.applied) return '#4caf50';
    if (job.is_new) return '#2196f3';
    return '#ff9800';
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
        position: 'relative',
        overflow: 'visible',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: (theme) => theme.palette.mode === 'dark' 
            ? '0 12px 40px rgba(0,0,0,0.4)' 
            : '0 8px 32px rgba(0,0,0,0.12)',
        },
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        borderRadius: 3,
        background: (theme) => theme.palette.mode === 'dark'
          ? 'linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%)'
          : 'linear-gradient(135deg, #ffffff 0%, #fafafa 100%)',
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      {/* Status Indicator Bar */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 4,
          bgcolor: getStatusColor(),
          borderRadius: '12px 12px 0 0',
        }}
      />

      <CardContent sx={{ p: 3 }}>
        {/* Header Section */}
        <Box display="flex" alignItems="flex-start" mb={2}>
          {/* Company Avatar */}
          <Avatar
            sx={{
              bgcolor: 'primary.main',
              width: 48,
              height: 48,
              mr: 2,
              fontSize: '1rem',
              fontWeight: 'bold',
            }}
          >
            {getCompanyInitials(job.company)}
          </Avatar>

          {/* Job Info */}
          <Box flex={1} minWidth={0}>
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 700,
                fontSize: '1.25rem',
                mb: 0.5,
                color: 'text.primary',
                lineHeight: 1.3,
              }}
            >
              {job.title}
            </Typography>
            
            <Box display="flex" alignItems="center" mb={1}>
              <CompanyIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
              <Typography 
                variant="subtitle1" 
                color="text.secondary"
                sx={{ fontWeight: 500 }}
              >
                {job.company}
              </Typography>
            </Box>

            {/* Location and Time */}
            <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
              <Box display="flex" alignItems="center">
                <LocationIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                <Typography variant="body2" color="text.secondary">
                  {job.location}
                </Typography>
              </Box>
              <Box display="flex" alignItems="center">
                <TimeIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                <Typography variant="body2" color="text.secondary">
                  {job.posted_date}
                </Typography>
              </Box>
            </Stack>
          </Box>

          {/* Bookmark Icon */}
          <IconButton
            size="small"
            sx={{
              color: job.applied ? 'success.main' : 'text.secondary',
              '&:hover': {
                bgcolor: job.applied ? 'success.light' + '20' : 'action.hover',
              }
            }}
          >
            {job.applied ? <BookmarkIcon /> : <BookmarkBorderIcon />}
          </IconButton>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Footer Section */}
        <Box display="flex" justifyContent="space-between" alignItems="center">
          {/* Status Chips */}
          <Stack direction="row" spacing={1}>
            {job.is_new && (
              <Chip
                label="New"
                size="small"
                color="primary"
                variant="filled"
                sx={{
                  height: 28,
                  fontWeight: 600,
                  '& .MuiChip-label': {
                    px: 1.5,
                  }
                }}
              />
            )}
            <Chip
              label={job.applied ? 'Applied' : 'Open'}
              size="small"
              color={job.applied ? 'success' : 'warning'}
              variant={job.applied ? 'filled' : 'outlined'}
              sx={{
                height: 28,
                fontWeight: 600,
                '& .MuiChip-label': {
                  px: 1.5,
                }
              }}
            />
          </Stack>

          {/* Action Buttons */}
          <Stack direction="row" spacing={1}>
            <Button
              variant={job.applied ? 'contained' : 'contained'}
              color={job.applied ? 'success' : 'primary'}
              size="medium"
              onClick={() => onToggleApplied(job.id)}
              disabled={isUpdating}
              startIcon={job.applied ? <CheckIcon /> : <ScheduleIcon />}
              sx={{
                minWidth: 140,
                borderRadius: 2,
                fontWeight: 600,
                textTransform: 'none',
                px: 2,
              }}
            >
              {isUpdating ? 'Updating...' : job.applied ? 'Applied ✓' : 'Apply Now'}
            </Button>
            
            <Button
              variant="outlined"
              size="medium"
              startIcon={<OpenInNewIcon />}
              component={Link}
              href={job.job_url}
              target="_blank"
              rel="noopener noreferrer"
              sx={{
                borderRadius: 2,
                fontWeight: 600,
                textTransform: 'none',
                minWidth: 120,
                px: 2,
              }}
            >
              View Details
            </Button>
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
};