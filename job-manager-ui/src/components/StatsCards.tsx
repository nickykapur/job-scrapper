import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import {
  Work as WorkIcon,
  FiberNew as NewIcon,
  Check as CheckIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { JobStats } from '../types';

interface StatsCardsProps {
  stats: JobStats;
}

export const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  const statItems = [
    {
      label: 'Total Jobs',
      value: stats.total,
      icon: <WorkIcon />,
      color: '#2196f3',
    },
    {
      label: 'New Jobs',
      value: stats.new,
      icon: <NewIcon />,
      color: '#4caf50',
    },
    {
      label: 'Applied',
      value: stats.applied,
      icon: <CheckIcon />,
      color: '#ff9800',
    },
    {
      label: 'Not Applied',
      value: stats.not_applied,
      icon: <ScheduleIcon />,
      color: '#f44336',
    },
  ];

  return (
    <Grid container spacing={2} sx={{ mb: 2, width: '100%' }}>
      {statItems.map((item) => (
        <Grid item xs={12} sm={6} md={3} key={item.label}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'row',
              alignItems: 'center',
              gap: 2,
              borderLeft: `4px solid ${item.color}`,
              '&:hover': {
                transform: 'translateY(-1px)',
                boxShadow: '0 3px 12px rgba(0,0,0,0.1)',
              },
              transition: 'all 0.2s ease',
              minHeight: 80,
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 40,
                height: 40,
                borderRadius: '50%',
                backgroundColor: `${item.color}20`,
                color: item.color,
                flexShrink: 0,
              }}
            >
              {item.icon}
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h5" component="div" color={item.color} fontWeight="bold" sx={{ lineHeight: 1 }}>
                {item.value}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {item.label}
              </Typography>
            </Box>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
};