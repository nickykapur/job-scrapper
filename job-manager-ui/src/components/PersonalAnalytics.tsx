import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  Calendar,
  Clock,
  Globe,
  Target,
  Award,
  BarChart3,
  CheckCircle,
  XCircle,
  Zap,
} from 'lucide-react';
import { jobApi } from '../services/api';

const MotionCard = motion(Card);

interface PersonalAnalyticsData {
  hourly_pattern: Array<{ hour: number; applications: number }>;
  daily_pattern: Array<{ day: string; day_number: number; applications: number }>;
  countries: Array<{ country: string; applied: number; rejected: number; saved: number }>;
  velocity: Array<{ date: string; applications: number }>;
  job_types: Array<{ job_type: string; applied: number; rejected: number }>;
  experience_levels: Array<{ level: string; applied: number; rejected: number }>;
  summary: {
    total_applied: number;
    total_rejected: number;
    total_saved: number;
    applied_last_7_days: number;
    applied_last_30_days: number;
    first_application: string | null;
    last_application: string | null;
    success_rate: number;
    avg_per_active_day: number;
    days_active: number;
  };
}

const StatCard: React.FC<{
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  colorClass: string;
}> = ({ title, value, subtitle, icon, colorClass }) => {
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
              {value}
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

export const PersonalAnalytics: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<PersonalAnalyticsData | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await jobApi.getPersonalAnalytics();
      setAnalytics(data);
    } catch (err: any) {
      console.error('Failed to load personal analytics:', err);
      setError(err.response?.data?.detail || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">My Analytics</h2>
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

  const { summary, hourly_pattern, daily_pattern, countries, velocity, job_types, experience_levels } = analytics;

  // Find peak hour
  const peakHour = hourly_pattern.reduce((max, curr) =>
    curr.applications > (max?.applications || 0) ? curr : max, hourly_pattern[0]
  );

  // Find peak day
  const peakDay = daily_pattern.reduce((max, curr) =>
    curr.applications > (max?.applications || 0) ? curr : max, daily_pattern[0]
  );

  // Get max values for progress bars
  const maxHourlyApps = Math.max(...hourly_pattern.map(h => h.applications), 1);
  const maxDailyApps = Math.max(...daily_pattern.map(d => d.applications), 1);
  const maxCountryApps = Math.max(...countries.map(c => c.applied), 1);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-3xl font-extrabold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
          My Job Application Analytics
        </h2>
        <p className="text-muted-foreground">
          Insights into your job search patterns and performance
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Applied"
          value={summary.total_applied}
          icon={<CheckCircle className="h-6 w-6" />}
          colorClass="text-green-500"
          subtitle={`${summary.applied_last_7_days} this week`}
        />
        <StatCard
          title="Success Rate"
          value={`${summary.success_rate}%`}
          icon={<Target className="h-6 w-6" />}
          colorClass="text-blue-500"
          subtitle={`${summary.total_applied}/${summary.total_applied + summary.total_rejected} applications`}
        />
        <StatCard
          title="Avg Per Day"
          value={summary.avg_per_active_day.toFixed(1)}
          icon={<Zap className="h-6 w-6" />}
          colorClass="text-orange-500"
          subtitle={`${summary.days_active} active days`}
        />
        <StatCard
          title="Last 30 Days"
          value={summary.applied_last_30_days}
          icon={<Calendar className="h-6 w-6" />}
          colorClass="text-purple-500"
        />
      </div>

      {/* Time Patterns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hour of Day Pattern */}
        <MotionCard
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <CardHeader>
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-primary" />
              <CardTitle>Application Time Pattern</CardTitle>
            </div>
            <p className="text-sm text-muted-foreground">
              Most active at {peakHour?.hour}:00 ({peakHour?.applications} applications)
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {hourly_pattern.map((item) => (
                <div key={item.hour} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{item.hour}:00</span>
                    <Badge variant="outline">{item.applications}</Badge>
                  </div>
                  <Progress
                    value={(item.applications / maxHourlyApps) * 100}
                    className="h-2"
                  />
                </div>
              ))}
              {hourly_pattern.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No data yet. Start applying to jobs!
                </p>
              )}
            </div>
          </CardContent>
        </MotionCard>

        {/* Day of Week Pattern */}
        <MotionCard
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <CardHeader>
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary" />
              <CardTitle>Weekly Pattern</CardTitle>
            </div>
            <p className="text-sm text-muted-foreground">
              Most active on {peakDay?.day} ({peakDay?.applications} applications)
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {daily_pattern.map((item) => (
                <div key={item.day_number} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{item.day}</span>
                    <Badge variant="outline">{item.applications}</Badge>
                  </div>
                  <Progress
                    value={(item.applications / maxDailyApps) * 100}
                    className="h-2"
                  />
                </div>
              ))}
              {daily_pattern.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No data yet. Start applying to jobs!
                </p>
              )}
            </div>
          </CardContent>
        </MotionCard>
      </div>

      {/* Country Distribution */}
      <MotionCard
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <CardHeader>
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-primary" />
            <CardTitle>Applications by Country</CardTitle>
          </div>
          <p className="text-sm text-muted-foreground">
            Where you're applying most
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {countries.slice(0, 10).map((item) => (
              <div key={item.country} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{item.country}</span>
                  <div className="flex items-center gap-2">
                    <Badge variant="default" className="bg-green-500">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      {item.applied}
                    </Badge>
                    <Badge variant="destructive">
                      <XCircle className="w-3 h-3 mr-1" />
                      {item.rejected}
                    </Badge>
                  </div>
                </div>
                <Progress
                  value={(item.applied / maxCountryApps) * 100}
                  className="h-2"
                />
              </div>
            ))}
            {countries.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-4">
                No data yet. Start applying to jobs!
              </p>
            )}
          </div>
        </CardContent>
      </MotionCard>

      {/* Job Types & Experience Levels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Job Types */}
        <MotionCard
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <CardHeader>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              <CardTitle>Job Type Preferences</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {job_types.map((item) => (
                <div key={item.job_type} className="flex items-center justify-between">
                  <span className="font-medium capitalize">{item.job_type}</span>
                  <div className="flex items-center gap-2">
                    <Badge variant="default">{item.applied} applied</Badge>
                    <Badge variant="outline">{item.rejected} rejected</Badge>
                  </div>
                </div>
              ))}
              {job_types.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No data yet
                </p>
              )}
            </div>
          </CardContent>
        </MotionCard>

        {/* Experience Levels */}
        <MotionCard
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <CardHeader>
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-primary" />
              <CardTitle>Experience Level Breakdown</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {experience_levels.map((item) => (
                <div key={item.level} className="flex items-center justify-between">
                  <span className="font-medium capitalize">{item.level}</span>
                  <div className="flex items-center gap-2">
                    <Badge variant="default">{item.applied} applied</Badge>
                    <Badge variant="outline">{item.rejected} rejected</Badge>
                  </div>
                </div>
              ))}
              {experience_levels.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No data yet
                </p>
              )}
            </div>
          </CardContent>
        </MotionCard>
      </div>

      {/* Application Velocity */}
      {velocity.length > 0 && (
        <MotionCard
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <CardHeader>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              <CardTitle>Application Velocity (Last 30 Days)</CardTitle>
            </div>
            <p className="text-sm text-muted-foreground">
              Your application activity over time
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {velocity.map((item) => (
                <div key={item.date} className="flex items-center gap-3">
                  <span className="text-sm font-medium min-w-[100px]">
                    {new Date(item.date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric'
                    })}
                  </span>
                  <div className="flex-1">
                    <Progress
                      value={(item.applications / Math.max(...velocity.map(v => v.applications))) * 100}
                      className="h-2"
                    />
                  </div>
                  <Badge variant="outline" className="min-w-[40px] justify-center">
                    {item.applications}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </MotionCard>
      )}

      {/* Summary Info */}
      {summary.first_application && (
        <Card className="bg-muted/50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <p className="text-sm text-muted-foreground">First Application</p>
                <p className="font-semibold">
                  {new Date(summary.first_application).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Last Application</p>
                <p className="font-semibold">
                  {summary.last_application ? new Date(summary.last_application).toLocaleDateString() : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Active Days</p>
                <p className="font-semibold">{summary.days_active}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Saved</p>
                <p className="font-semibold">{summary.total_saved}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PersonalAnalytics;
