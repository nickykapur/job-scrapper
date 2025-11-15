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
  colorClass: string;
  subtitle?: string;
}> = ({ title, value, icon, colorClass, subtitle }) => {
  return (
    <MotionCard
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="hover:-translate-y-1 transition-all duration-300"
    >
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">
              {title}
            </p>
            <h3 className={`text-3xl font-bold ${colorClass}`}>
              {value.toLocaleString()}
            </h3>
            {subtitle && (
              <p className="text-xs text-muted-foreground mt-1">
                {subtitle}
              </p>
            )}
          </div>
          <div className={`p-3 rounded-full ${colorClass.replace('text-', 'bg-')}/10`}>
            {icon}
          </div>
        </div>
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
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="h-[140px] animate-pulse bg-muted/50" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
        {error || 'Failed to load analytics'}
      </div>
    );
  }

  const { users, job_types, countries, summary } = analytics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-3xl font-extrabold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
          Analytics Dashboard
        </h2>
        <p className="text-muted-foreground">
          Real-time insights across all user accounts
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Users"
          value={summary.total_users}
          icon={<Users className="h-6 w-6" />}
          colorClass="text-blue-500"
        />
        <StatCard
          title="Total Applications"
          value={summary.total_applications}
          icon={<CheckCircle className="h-6 w-6" />}
          colorClass="text-green-500"
          subtitle={`${summary.applications_last_7_days} this week`}
        />
        <StatCard
          title="Total Rejections"
          value={summary.total_rejections}
          icon={<XCircle className="h-6 w-6" />}
          colorClass="text-red-500"
        />
        <StatCard
          title="Last 30 Days"
          value={summary.applications_last_30_days}
          icon={<TrendingUp className="h-6 w-6" />}
          colorClass="text-purple-500"
        />
      </div>

      {/* User Statistics Table */}
      <MotionCard
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <CardHeader>
          <CardTitle>User Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Job Types</TableHead>
                  <TableHead className="text-center">Applied</TableHead>
                  <TableHead className="text-center">Rejected</TableHead>
                  <TableHead className="text-center">7 Days</TableHead>
                  <TableHead className="text-center">30 Days</TableHead>
                  <TableHead>Last Application</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-sm font-semibold">
                          {user.username.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="text-sm font-semibold">{user.username}</p>
                          <p className="text-xs text-muted-foreground">{user.email}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1 flex-wrap">
                        {user.job_types.map((type) => (
                          <Badge key={type} variant="default" className="text-xs">
                            {type}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      <span className="text-sm font-semibold text-green-600">
                        {user.stats.jobs_applied}
                      </span>
                    </TableCell>
                    <TableCell className="text-center">
                      <span className="text-sm font-semibold text-red-600">
                        {user.stats.jobs_rejected}
                      </span>
                    </TableCell>
                    <TableCell className="text-center">
                      <Badge variant={user.stats.applications_last_7_days > 0 ? 'default' : 'secondary'}>
                        {user.stats.applications_last_7_days}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-center">
                      <Badge variant={user.stats.applications_last_30_days > 0 ? 'default' : 'secondary'}>
                        {user.stats.applications_last_30_days}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="text-xs text-muted-foreground">
                        {user.stats.last_application_date
                          ? new Date(user.stats.last_application_date).toLocaleDateString()
                          : 'Never'}
                      </span>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </MotionCard>

      {/* TODO: Migrate Job Types and Countries sections from MUI */}
    </div>
  );
};

export default Analytics;
