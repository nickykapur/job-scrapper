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
    <Grid container spacing={3} sx={{ mb: 3 }}>
      {statItems.map((item) => (
        <Grid item xs={6} md={3} key={item.label}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              borderLeft: `4px solid ${item.color}`,
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
              },
              transition: 'all 0.3s ease',
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 48,
                height: 48,
                borderRadius: '50%',
                backgroundColor: `${item.color}20`,
                color: item.color,
                mb: 1,
              }}
            >
              {item.icon}
            </Box>
            <Typography variant=\"h4\" component=\"div\" color={item.color} fontWeight=\"bold\">
              {item.value}
            </Typography>
            <Typography variant=\"body2\" color=\"text.secondary\" textAlign=\"center\">
              {item.label}
            </Typography>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
};