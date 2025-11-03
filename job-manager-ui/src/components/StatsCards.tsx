import React from 'react';
import { Grid, Card, CardContent, Typography, Box, alpha } from '@mui/material';
import { JobStats } from '../types';

interface StatsCardsProps {
  stats: JobStats;
}

export const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  const statItems = [
    {
      label: 'Total Jobs',
      value: stats.total,
      color: '#3b82f6',
    },
    {
      label: 'New Positions',
      value: stats.new,
      color: '#10b981',
    },
    {
      label: 'Applied',
      value: stats.applied,
      color: '#8b5cf6',
    },
    {
      label: 'Pending',
      value: stats.not_applied,
      color: '#f59e0b',
    },
  ];

  return (
    <Grid container spacing={{ xs: 2, sm: 2, md: 3 }} sx={{ mb: { xs: 3, sm: 4, md: 4 } }}>
      {statItems.map((item) => (
        <Grid item xs={6} sm={6} md={3} key={item.label}>
          <Card
            elevation={0}
            sx={{
              height: '100%',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 2.5,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                borderColor: (theme) => alpha(item.color, 0.4),
                transform: 'translateY(-2px)',
                boxShadow: (theme) => theme.palette.mode === 'dark'
                  ? `0 4px 12px ${alpha(item.color, 0.15)}`
                  : `0 4px 12px ${alpha(item.color, 0.1)}`,
              },
            }}
          >
            <CardContent sx={{ p: { xs: 2, sm: 2.5, md: 3 } }}>
              <Box>
                <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {item.label}
                </Typography>
                <Typography
                  variant="h4"
                  component="div"
                  sx={{
                    fontWeight: 800,
                    color: item.color,
                    mt: 1,
                    fontSize: { xs: '1.75rem', sm: '2rem', md: '2.25rem' },
                    letterSpacing: '-0.02em',
                  }}
                >
                  {item.value}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};
