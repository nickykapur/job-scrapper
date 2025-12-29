import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { BarChart3, TrendingUp, Calendar, Clock, Building2, Globe } from 'lucide-react';
import { jobApi } from '@/services/api';
import toast from 'react-hot-toast';

interface CountryAnalyticsData {
  time_range_days: number;
  generated_at: string;
  country_summary: CountrySummary[];
  daily_trends: DailyTrend[];
  day_of_week_patterns: DayOfWeekPattern[];
  top_companies: TopCompany[];
  hourly_patterns: HourlyPattern[];
  weekly_trends: WeeklyTrend[];
}

interface CountrySummary {
  country: string;
  total_jobs: number;
  unique_companies: number;
  new_jobs: number;
  easy_apply_jobs: number;
  active_days: number;
  first_scrape: string | null;
  last_scrape: string | null;
  avg_jobs_per_day: number;
}

interface DailyTrend {
  date: string;
  country: string;
  total_jobs: number;
  new_jobs: number;
  unique_companies: number;
}

interface DayOfWeekPattern {
  day_name: string;
  day_number: number;
  country: string;
  total_jobs: number;
  new_jobs: number;
  new_job_percentage: number;
}

interface TopCompany {
  country: string;
  company: string;
  total_jobs: number;
  new_jobs: number;
  easy_apply_jobs: number;
  last_posted: string | null;
  first_posted: string | null;
}

interface HourlyPattern {
  hour: number;
  country: string;
  total_jobs: number;
}

interface WeeklyTrend {
  week_start: string | null;
  country: string;
  total_jobs: number;
  new_jobs: number;
  unique_companies: number;
}

type ViewMode = 'daily' | 'weekly' | 'companies' | 'timing';

export const CountryAnalytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<CountryAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCountry, setSelectedCountry] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<number>(90);
  const [viewMode, setViewMode] = useState<ViewMode>('daily');

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const data = await jobApi.getCountryAnalytics(timeRange);
      setAnalytics(data);
    } catch (error: any) {
      console.error('Failed to load country analytics:', error);
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-muted-foreground">No analytics data available</p>
          <Button onClick={loadAnalytics} className="mt-4">Retry</Button>
        </CardContent>
      </Card>
    );
  }

  const filteredCountries = selectedCountry === 'all'
    ? analytics.country_summary
    : analytics.country_summary.filter(c => c.country === selectedCountry);

  const countries = analytics.country_summary.map(c => c.country);

  // Get day of week patterns for selected country
  const dayOfWeekData = analytics.day_of_week_patterns.filter(
    d => selectedCountry === 'all' || d.country === selectedCountry
  );

  // Aggregate by day if 'all' is selected
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const aggregatedDayOfWeek = dayNames.map((day, idx) => {
    const dayData = dayOfWeekData.filter(d => d.day_number === idx);
    return {
      day,
      total_jobs: dayData.reduce((sum, d) => sum + d.total_jobs, 0),
      new_jobs: dayData.reduce((sum, d) => sum + d.new_jobs, 0),
    };
  });

  // Get top companies for selected country
  const topCompaniesData = analytics.top_companies
    .filter(c => selectedCountry === 'all' || c.country === selectedCountry)
    .slice(0, 20);

  // Group by country for display
  const companiesByCountry: Record<string, TopCompany[]> = {};
  topCompaniesData.forEach(company => {
    if (!companiesByCountry[company.country]) {
      companiesByCountry[company.country] = [];
    }
    if (companiesByCountry[company.country].length < 10) {
      companiesByCountry[company.country].push(company);
    }
  });

  // Hourly patterns
  const hourlyData = analytics.hourly_patterns.filter(
    h => selectedCountry === 'all' || h.country === selectedCountry
  );

  const aggregatedHourly = Array.from({ length: 24 }, (_, hour) => {
    const hourData = hourlyData.filter(h => h.hour === hour);
    return {
      hour,
      total_jobs: hourData.reduce((sum, h) => sum + h.total_jobs, 0),
    };
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-3xl font-bold">Country Analytics Dashboard</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Job market insights across countries
          </p>
        </div>
        <div className="flex gap-2 flex-wrap items-center">
          <select
            className="h-10 px-3 rounded-md border border-input bg-background text-sm"
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={180}>Last 6 months</option>
            <option value={365}>Last year</option>
          </select>
          <Button variant="outline" onClick={loadAnalytics}>
            <TrendingUp className="mr-2 h-4 w-4" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Country Filter */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Filter by Country
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 flex-wrap">
            <Badge
              variant={selectedCountry === 'all' ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setSelectedCountry('all')}
            >
              All Countries
            </Badge>
            {countries.map(country => (
              <Badge
                key={country}
                variant={selectedCountry === country ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => setSelectedCountry(country)}
              >
                {country}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {filteredCountries.map(country => (
          <Card key={country.country}>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center justify-between">
                {country.country}
                <Globe className="h-4 w-4 text-muted-foreground" />
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div>
                <div className="text-2xl font-bold">{country.total_jobs.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Total Jobs</p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <div className="font-semibold">{country.unique_companies}</div>
                  <p className="text-xs text-muted-foreground">Companies</p>
                </div>
                <div>
                  <div className="font-semibold">{country.avg_jobs_per_day.toFixed(1)}</div>
                  <p className="text-xs text-muted-foreground">Jobs/Day</p>
                </div>
              </div>
              <div className="pt-2 border-t">
                <div className="text-xs text-muted-foreground">
                  Active {country.active_days} days
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* View Selector */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <Button
              variant={viewMode === 'daily' ? 'default' : 'outline'}
              onClick={() => setViewMode('daily')}
              className="w-full"
            >
              <Calendar className="mr-2 h-4 w-4" />
              Daily Trends
            </Button>
            <Button
              variant={viewMode === 'weekly' ? 'default' : 'outline'}
              onClick={() => setViewMode('weekly')}
              className="w-full"
            >
              <BarChart3 className="mr-2 h-4 w-4" />
              Day of Week
            </Button>
            <Button
              variant={viewMode === 'companies' ? 'default' : 'outline'}
              onClick={() => setViewMode('companies')}
              className="w-full"
            >
              <Building2 className="mr-2 h-4 w-4" />
              Top Companies
            </Button>
            <Button
              variant={viewMode === 'timing' ? 'default' : 'outline'}
              onClick={() => setViewMode('timing')}
              className="w-full"
            >
              <Clock className="mr-2 h-4 w-4" />
              Best Time
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* View Content */}
      <div className="space-y-4">
        {/* Daily Trends */}
        {viewMode === 'daily' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Daily Job Posting Trends
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Date</th>
                      <th className="text-left py-2">Country</th>
                      <th className="text-right py-2">Total Jobs</th>
                      <th className="text-right py-2">New Jobs</th>
                      <th className="text-right py-2">Companies</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.daily_trends
                      .filter(d => selectedCountry === 'all' || d.country === selectedCountry)
                      .slice(0, 50)
                      .map((trend, idx) => (
                        <tr key={idx} className="border-b hover:bg-muted/50">
                          <td className="py-2">{new Date(trend.date).toLocaleDateString()}</td>
                          <td className="py-2">{trend.country}</td>
                          <td className="py-2 text-right font-semibold">{trend.total_jobs}</td>
                          <td className="py-2 text-right">{trend.new_jobs}</td>
                          <td className="py-2 text-right">{trend.unique_companies}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Day of Week Patterns */}
        {viewMode === 'weekly' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Best Days to Check for Jobs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {aggregatedDayOfWeek.map((day) => {
                  const maxJobs = Math.max(...aggregatedDayOfWeek.map(d => d.total_jobs));
                  const percentage = (day.total_jobs / maxJobs) * 100;

                  return (
                    <div key={day.day} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium">{day.day}</span>
                        <span className="text-muted-foreground">
                          {day.total_jobs} jobs ({day.new_jobs} new)
                        </span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-3">
                        <div
                          className="bg-primary rounded-full h-3 transition-all"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
                <h4 className="font-semibold mb-2">Insights</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  {(() => {
                    const sorted = [...aggregatedDayOfWeek].sort((a, b) => b.total_jobs - a.total_jobs);
                    const bestDay = sorted[0];
                    const worstDay = sorted[sorted.length - 1];
                    return (
                      <>
                        <li>Most jobs posted on <strong>{bestDay.day}</strong> ({bestDay.total_jobs} jobs)</li>
                        <li>Fewest jobs on <strong>{worstDay.day}</strong> ({worstDay.total_jobs} jobs)</li>
                        <li>Best days for scraping: {sorted.slice(0, 3).map(d => d.day).join(', ')}</li>
                      </>
                    );
                  })()}
                </ul>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Top Companies */}
        {viewMode === 'companies' && (
          <>
            {Object.entries(companiesByCountry).map(([country, companies]) => (
            <Card key={country}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Top Companies in {country}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2">Company</th>
                        <th className="text-right py-2">Total Jobs</th>
                        <th className="text-right py-2">New Jobs</th>
                        <th className="text-right py-2">Easy Apply</th>
                        <th className="text-right py-2">Last Posted</th>
                      </tr>
                    </thead>
                    <tbody>
                      {companies.map((company, idx) => (
                        <tr key={idx} className="border-b hover:bg-muted/50">
                          <td className="py-2 font-medium">{company.company}</td>
                          <td className="py-2 text-right">{company.total_jobs}</td>
                          <td className="py-2 text-right">{company.new_jobs}</td>
                          <td className="py-2 text-right">{company.easy_apply_jobs}</td>
                          <td className="py-2 text-right text-xs text-muted-foreground">
                            {company.last_posted ? new Date(company.last_posted).toLocaleDateString() : 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
            ))}
          </>
        )}

        {/* Hourly Patterns */}
        {viewMode === 'timing' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Hourly Posting Patterns (UTC)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {aggregatedHourly.map((hour) => {
                  const maxJobs = Math.max(...aggregatedHourly.map(h => h.total_jobs));
                  const percentage = maxJobs > 0 ? (hour.total_jobs / maxJobs) * 100 : 0;

                  return (
                    <div key={hour.hour} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium w-16">
                          {hour.hour.toString().padStart(2, '0')}:00
                        </span>
                        <span className="text-muted-foreground">
                          {hour.total_jobs} jobs
                        </span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className="bg-green-500 rounded-full h-2 transition-all"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="mt-6 p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-lg">
                <h4 className="font-semibold mb-2">Scraping Recommendations</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  {(() => {
                    const sorted = [...aggregatedHourly].sort((a, b) => b.total_jobs - a.total_jobs);
                    const peakHours = sorted.slice(0, 3);
                    return (
                      <>
                        <li>Peak posting hours: {peakHours.map(h => `${h.hour}:00`).join(', ')}</li>
                        <li>Run scraper during these hours for maximum job discovery</li>
                        <li>Consider scheduling GitHub Actions cron jobs around peak times</li>
                      </>
                    );
                  })()}
                </ul>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
