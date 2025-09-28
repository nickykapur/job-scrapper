import React from 'react';
import { Grid, Card, CardContent, Typography, Box, useTheme } from '@mui/material';
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
  const theme = useTheme();

  const statItems = [
    {
      label: 'Total Jobs',
      value: stats.total,
      icon: <WorkIcon />,
      color: theme.palette.primary.main,
      bgColor: theme.palette.primary.light + '20',
    },
    {
      label: 'New Positions',
      value: stats.new,
      icon: <NewIcon />,
      color: theme.palette.success.main,
      bgColor: theme.palette.success.light + '20',
    },
    {
      label: 'Applied',
      value: stats.applied,
      icon: <CheckIcon />,
      color: theme.palette.info.main,
      bgColor: theme.palette.info.light + '20',
    },
    {
      label: 'Pending',
      value: stats.not_applied,
      icon: <ScheduleIcon />,
      color: theme.palette.warning.main,
      bgColor: theme.palette.warning.light + '20',
    },
  ];

  return (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      {statItems.map((item) => (
        <Grid item xs={12} sm={6} md={3} key={item.label}>
          <Card
            elevation={0}
            sx={{
              height: '100%',
              border: 1,
              borderColor: 'divider',
              borderRadius: 2,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                borderColor: item.color,
                transform: 'translateY(-2px)',
                boxShadow: theme.shadows[4],
              },
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 700, color: item.color, mb: 0.5 }}>
                    {item.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                    {item.label}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 48,
                    height: 48,
                    borderRadius: 2,
                    backgroundColor: item.bgColor,
                    color: item.color,
                  }}
                >
                  {React.cloneElement(item.icon, { fontSize: 'medium' })}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};