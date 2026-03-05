import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Activity, RefreshCw, ExternalLink, AlertCircle } from 'lucide-react';
import { jobApi } from '../services/api';

interface WorkflowRun {
  id: number;
  status: string;
  conclusion: string | null;
  event: string;
  run_started_at: string | null;
  updated_at: string | null;
  duration_seconds: number | null;
  html_url: string;
  run_number: number;
}

interface WorkflowData {
  name: string;
  runs: WorkflowRun[];
  error: string | null;
}

interface CountryStat {
  country: string;
  count: number;
  last_scraped: string | null;
}

interface JobTypeStat {
  job_type: string;
  count: number;
}

interface MonitoringData {
  generated_at: string;
  github: {
    token_configured: boolean;
    workflows: WorkflowData[];
  };
  database: {
    total_jobs: number;
    by_country: CountryStat[];
    by_job_type: JobTypeStat[];
    error: string | null;
  };
  sentry: {
    configured: boolean;
    url: string | null;
  };
}

const formatDuration = (seconds: number | null): string => {
  if (seconds === null) return '—';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
};

const formatDate = (iso: string | null): string => {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
};

const getStatusBadge = (run: WorkflowRun) => {
  if (run.status === 'in_progress' || run.status === 'queued') {
    return <Badge className="bg-yellow-500/20 text-yellow-600 border-yellow-500/50">Running</Badge>;
  }
  if (run.conclusion === 'success') {
    return <Badge className="bg-green-500/20 text-green-600 border-green-500/50">Success</Badge>;
  }
  if (run.conclusion === 'failure') {
    return <Badge className="bg-red-500/20 text-red-600 border-red-500/50">Failed</Badge>;
  }
  if (run.conclusion === 'cancelled') {
    return <Badge variant="outline" className="text-muted-foreground">Cancelled</Badge>;
  }
  return <Badge variant="outline">{run.conclusion || run.status}</Badge>;
};

export const MonitoringPage: React.FC = () => {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await jobApi.getMonitoring();
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load monitoring data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading monitoring data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="max-w-md">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={load}>Try Again</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="container mx-auto p-6 max-w-7xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Activity className="h-8 w-8" />
            System Monitoring
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Generated at {formatDate(data.generated_at)}
          </p>
        </div>
        <Button variant="outline" onClick={load} className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* GitHub Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            GitHub Actions
            {data.github.token_configured ? (
              <Badge className="bg-green-500/20 text-green-600 border-green-500/50">Token OK</Badge>
            ) : (
              <Badge className="bg-red-500/20 text-red-600 border-red-500/50">No Token</Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {data.github.workflows.map((wf) => (
            <div key={wf.name}>
              <h3 className="font-semibold mb-2 text-sm text-muted-foreground">{wf.name}</h3>
              {wf.error ? (
                <p className="text-sm text-red-500">{wf.error}</p>
              ) : wf.runs.length === 0 ? (
                <p className="text-sm text-muted-foreground">No runs found</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-muted-foreground">
                        <th className="text-left p-2">Status</th>
                        <th className="text-left p-2">Trigger</th>
                        <th className="text-left p-2">Started</th>
                        <th className="text-left p-2">Duration</th>
                        <th className="text-left p-2">Link</th>
                      </tr>
                    </thead>
                    <tbody>
                      {wf.runs.map((run) => (
                        <tr key={run.id} className="border-b hover:bg-muted/50">
                          <td className="p-2">{getStatusBadge(run)}</td>
                          <td className="p-2 capitalize">{run.event}</td>
                          <td className="p-2">{formatDate(run.run_started_at)}</td>
                          <td className="p-2">{formatDuration(run.duration_seconds)}</td>
                          <td className="p-2">
                            <a
                              href={run.html_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-500 hover:underline flex items-center gap-1"
                            >
                              #{run.run_number} <ExternalLink className="h-3 w-3" />
                            </a>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Database Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Database Stats</CardTitle>
        </CardHeader>
        <CardContent>
          {data.database.error ? (
            <p className="text-sm text-red-500">{data.database.error}</p>
          ) : (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="text-4xl font-bold">{data.database.total_jobs.toLocaleString()}</div>
                <div className="text-muted-foreground">total jobs in database</div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* By Country */}
                <div>
                  <h3 className="font-semibold mb-2">Jobs by Country</h3>
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-muted-foreground">
                        <th className="text-left p-2">Country</th>
                        <th className="text-left p-2">Count</th>
                        <th className="text-left p-2">Last Scraped</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.database.by_country.map((row) => (
                        <tr key={row.country} className="border-b hover:bg-muted/50">
                          <td className="p-2">{row.country}</td>
                          <td className="p-2 font-medium">{row.count.toLocaleString()}</td>
                          <td className="p-2 text-muted-foreground">{formatDate(row.last_scraped)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* By Job Type */}
                <div>
                  <h3 className="font-semibold mb-2">Jobs by Job Type</h3>
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-muted-foreground">
                        <th className="text-left p-2">Job Type</th>
                        <th className="text-left p-2">Count</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.database.by_job_type.map((row) => (
                        <tr key={row.job_type} className="border-b hover:bg-muted/50">
                          <td className="p-2 capitalize">{row.job_type}</td>
                          <td className="p-2 font-medium">{row.count.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Sentry */}
      <Card>
        <CardHeader>
          <CardTitle>Sentry Error Tracking</CardTitle>
        </CardHeader>
        <CardContent>
          {data.sentry.configured ? (
            <div className="flex items-center gap-4">
              <Badge className="bg-green-500/20 text-green-600 border-green-500/50">Configured</Badge>
              {data.sentry.url && (
                <a
                  href={data.sentry.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-blue-500 hover:underline"
                >
                  Open Sentry Dashboard <ExternalLink className="h-4 w-4" />
                </a>
              )}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">Sentry is not configured (SENTRY_DSN env var not set)</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MonitoringPage;
