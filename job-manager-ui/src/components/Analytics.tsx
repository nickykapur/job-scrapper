import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { motion } from 'framer-motion';
import {
  Users,
  Briefcase,
  CheckCircle,
  XCircle,
  TrendingUp,
  Globe,
  Building2,
} from 'lucide-react';
import { jobApi } from '../services/api';

interface UserAnalytics {
  id: number;
  username: string;
  email: string;
  full_name: string;
  created_at: string | null;
  last_login: string | null;
  is_admin: boolean;
  job_types: string[];
  preferred_countries: string[];
  experience_levels: string[];
  stats: {
    jobs_applied: number;
    jobs_rejected: number;
    jobs_saved: number;
    last_application_date: string | null;
    applications_last_7_days: number;
    applications_last_30_days: number;
  };
}

interface AnalyticsData {
  users: UserAnalytics[];
  job_types: Array<{
    job_type: string;
    total_jobs: number;
    applied_jobs: number;
    rejected_jobs: number;
    available_jobs: number;
  }>;
  countries: Array<{
    country: string;
    total_jobs: number;
    applied_jobs: number;
    rejected_jobs: number;
  }>;
  application_timeline: Array<{
    date: string;
    applications: number;
  }>;
  summary: {
    total_users: number;
    total_applications: number;
    total_rejections: number;
    applications_last_7_days: number;
    applications_last_30_days: number;
  };
}

const MotionCard = motion(Card);

const StatCard: React.FC<{
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  subtitle?: string;
}> = ({ title, value, icon, color, subtitle }) => {
  const theme = useTheme();

  return (
    <MotionCard
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      sx={{
        background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
        border: `1px solid ${color}30`,
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: theme.shadows[8],
        },
        transition: 'all 0.3s ease',
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="body2" color="text.secondary" fontWeight={500}>
              {title}
            </Typography>
            <Typography variant="h3" fontWeight={700} color={color} sx={{ mt: 1 }}>
              {value.toLocaleString()}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          <Avatar
            sx={{
              bgcolor: `${color}20`,
              color: color,
              width: 56,
              height: 56,
            }}
          >
            {icon}
          </Avatar>
        </Box>
      </CardContent>
    </MotionCard>
  );
};

export const Analytics: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const theme = useTheme();

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await jobApi.getAnalytics();
      setAnalytics(data);
    } catch (err: any) {
      console.error('Failed to load analytics:', err);
      setError(err.response?.data?.detail || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Analytics Dashboard
        </Typography>
        <Grid container spacing={3} sx={{ mt: 2 }}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Skeleton variant="rectangular" height={140} sx={{ borderRadius: 2 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  if (error || !analytics) {
    return (
      <Box>
        <Alert severity="error" sx={{ borderRadius: 2 }}>
          {error || 'Failed to load analytics'}
        </Alert>
      </Box>
    );
  }

  const { users, job_types, countries, summary } = analytics;

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          fontWeight={800}
          sx={{
            background: theme.palette.mode === 'dark'
              ? 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%)'
              : 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Analytics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
          Real-time insights across all user accounts
        </Typography>
      </Box>

      {/* Summary Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Users"
            value={summary.total_users}
            icon={<PeopleIcon />}
            color="#3b82f6"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Applications"
            value={summary.total_applications}
            icon={<CheckCircleIcon />}
            color="#10b981"
            subtitle={`${summary.applications_last_7_days} this week`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Rejections"
            value={summary.total_rejections}
            icon={<CancelIcon />}
            color="#ef4444"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Last 30 Days"
            value={summary.applications_last_30_days}
            icon={<TrendingUpIcon />}
            color="#8b5cf6"
          />
        </Grid>
      </Grid>

      {/* User Statistics Table */}
      <MotionCard
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        sx={{ mb: 4 }}
      >
        <CardContent>
          <Typography variant="h6" fontWeight={700} gutterBottom>
            User Activity
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>User</strong></TableCell>
                  <TableCell><strong>Job Types</strong></TableCell>
                  <TableCell align="center"><strong>Applied</strong></TableCell>
                  <TableCell align="center"><strong>Rejected</strong></TableCell>
                  <TableCell align="center"><strong>7 Days</strong></TableCell>
                  <TableCell align="center"><strong>30 Days</strong></TableCell>
                  <TableCell><strong>Last Application</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1.5}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: '0.875rem' }}>
                          {user.username.charAt(0).toUpperCase()}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight={600}>
                            {user.username}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {user.email}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={0.5} flexWrap="wrap">
                        {user.job_types.map((type) => (
                          <Chip
                            key={type}
                            label={type}
                            size="small"
                            sx={{
                              bgcolor: 'primary.main',
                              color: 'white',
                              fontWeight: 500,
                              fontSize: '0.75rem',
                            }}
                          />
                        ))}
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Typography variant="body2" fontWeight={600} color="success.main">
                        {user.stats.jobs_applied}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Typography variant="body2" fontWeight={600} color="error.main">
                        {user.stats.jobs_rejected}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={user.stats.applications_last_7_days}
                        size="small"
                        color={user.stats.applications_last_7_days > 0 ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={user.stats.applications_last_30_days}
                        size="small"
                        color={user.stats.applications_last_30_days > 0 ? 'info' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" color="text.secondary">
                        {user.stats.last_application_date
                          ? new Date(user.stats.last_application_date).toLocaleDateString()
                          : 'Never'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </MotionCard>

      <Grid container spacing={3}>
        {/* Job Types Distribution */}
        <Grid item xs={12} md={6}>
          <MotionCard
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <BusinessIcon color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  Job Types
                </Typography>
              </Box>
              {job_types.map((jt, index) => (
                <Box key={jt.job_type} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                    <Typography variant="body2" fontWeight={600} textTransform="capitalize">
                      {jt.job_type}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {jt.applied_jobs}/{jt.total_jobs} applied
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(jt.applied_jobs / jt.total_jobs) * 100}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'action.hover',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 4,
                        bgcolor: `hsl(${(index * 60) % 360}, 70%, 50%)`,
                      },
                    }}
                  />
                  <Box display="flex" gap={2} mt={0.5}>
                    <Typography variant="caption" color="success.main">
                      Applied: {jt.applied_jobs}
                    </Typography>
                    <Typography variant="caption" color="error.main">
                      Rejected: {jt.rejected_jobs}
                    </Typography>
                    <Typography variant="caption" color="info.main">
                      Available: {jt.available_jobs}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </MotionCard>
        </Grid>

        {/* Countries Distribution */}
        <Grid item xs={12} md={6}>
          <MotionCard
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <LanguageIcon color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  Countries
                </Typography>
              </Box>
              {countries.slice(0, 10).map((country, index) => (
                <Box key={country.country} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                    <Typography variant="body2" fontWeight={600}>
                      {country.country}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {country.total_jobs} jobs
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(country.applied_jobs / country.total_jobs) * 100}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'action.hover',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 4,
                        bgcolor: `hsl(${200 + (index * 20)}, 70%, 50%)`,
                      },
                    }}
                  />
                  <Box display="flex" gap={2} mt={0.5}>
                    <Typography variant="caption" color="success.main">
                      Applied: {country.applied_jobs}
                    </Typography>
                    <Typography variant="caption" color="error.main">
                      Rejected: {country.rejected_jobs}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </MotionCard>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
