import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Activity, RefreshCw, ExternalLink, AlertCircle, Database, Trash2, Timer } from 'lucide-react';
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

interface TableStat {
  table_name: string;
  total_bytes: number;
  data_bytes: number;
  row_estimate: number;
}

interface ScraperRunLog {
  country: string;
  github_run_id: string | null;
  github_run_number: number | null;
  started_at: string | null;
  duration_seconds: number | null;
  phases: {
    fetch_existing: number | null;
    fetch_job_types: number | null;
    scraping: number | null;
    upload: number | null;
  };
  total_terms: number | null;
  successful_searches: number | null;
  failed_searches: number | null;
  jobs_scraped: number | null;
  new_jobs: number | null;
  dry_run: boolean;
  error: string | null;
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
    storage: {
      db_bytes: number;
      jobs_total_bytes: number;
      jobs_data_bytes: number;
      jobs_index_bytes: number;
    } | null;
    tables: TableStat[];
    scraper_runs: ScraperRunLog[];
    oldest_job: string | null;
    newest_job: string | null;
    cleanup_candidates: {
      rejected: number;
      applied: number;
      older_than_30d: number;
      older_than_60d: number;
    } | null;
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

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
};

// Railway Hobby plan free tier: 1 GB storage
const RAILWAY_LIMIT_BYTES = 1 * 1024 * 1024 * 1024;

const StorageBar: React.FC<{ bytes: number; limitBytes: number; label: string }> = ({ bytes, limitBytes, label }) => {
  const pct = Math.min((bytes / limitBytes) * 100, 100);
  const color = pct > 85 ? 'bg-red-500' : pct > 60 ? 'bg-yellow-500' : 'bg-green-500';
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span>{label}</span>
        <span className="font-medium">{formatBytes(bytes)} / {formatBytes(limitBytes)}</span>
      </div>
      <div className="h-3 rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <div className="text-xs text-muted-foreground mt-0.5 text-right">{pct.toFixed(1)}% used</div>
    </div>
  );
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

  const db = data.database;

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

      {/* DB Storage — most important, show first */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Database Storage
          </CardTitle>
        </CardHeader>
        <CardContent>
          {db.error ? (
            <p className="text-sm text-red-500">{db.error}</p>
          ) : db.storage ? (
            <div className="space-y-5">
              {/* Progress bars */}
              <StorageBar
                bytes={db.storage.db_bytes}
                limitBytes={RAILWAY_LIMIT_BYTES}
                label="Total DB size (Railway 1 GB limit)"
              />
              <StorageBar
                bytes={db.storage.jobs_total_bytes}
                limitBytes={RAILWAY_LIMIT_BYTES}
                label="Jobs table (data + indexes)"
              />

              {/* Breakdown cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
                <div className="rounded-lg border p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-1">Total DB</div>
                  <div className="font-bold text-lg">{formatBytes(db.storage.db_bytes)}</div>
                </div>
                <div className="rounded-lg border p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-1">Jobs Data</div>
                  <div className="font-bold text-lg">{formatBytes(db.storage.jobs_data_bytes)}</div>
                </div>
                <div className="rounded-lg border p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-1">Jobs Indexes</div>
                  <div className="font-bold text-lg">{formatBytes(db.storage.jobs_index_bytes)}</div>
                </div>
                <div className="rounded-lg border p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-1">Total Jobs</div>
                  <div className="font-bold text-lg">{db.total_jobs.toLocaleString()}</div>
                </div>
              </div>

              {/* Date range */}
              {(db.oldest_job || db.newest_job) && (
                <div className="flex gap-6 text-sm text-muted-foreground border-t pt-3">
                  <span>Oldest job: <span className="text-foreground">{formatDate(db.oldest_job)}</span></span>
                  <span>Newest job: <span className="text-foreground">{formatDate(db.newest_job)}</span></span>
                </div>
              )}

              {/* All tables */}
              {db.tables && db.tables.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2 text-sm">All Tables</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b text-muted-foreground">
                          <th className="text-left p-2">Table</th>
                          <th className="text-left p-2">Size (total)</th>
                          <th className="text-left p-2">Data</th>
                          <th className="text-left p-2">Rows (est.)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {db.tables.map(t => (
                          <tr key={t.table_name} className="border-b hover:bg-muted/50">
                            <td className="p-2 font-mono text-xs">{t.table_name}</td>
                            <td className="p-2">{formatBytes(t.total_bytes)}</td>
                            <td className="p-2">{formatBytes(t.data_bytes)}</td>
                            <td className="p-2">{t.row_estimate.toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Storage data unavailable</p>
          )}
        </CardContent>
      </Card>

      {/* Cleanup Candidates */}
      {db.cleanup_candidates && (
        <Card className="border-orange-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trash2 className="h-5 w-5 text-orange-500" />
              Cleanup Candidates
              <span className="text-sm font-normal text-muted-foreground ml-1">— safe rows to delete to free space</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="rounded-lg border border-red-500/30 bg-red-500/5 p-3 text-center">
                <div className="text-xs text-muted-foreground mb-1">Rejected jobs</div>
                <div className="font-bold text-xl text-red-600">{db.cleanup_candidates.rejected.toLocaleString()}</div>
              </div>
              <div className="rounded-lg border border-green-500/30 bg-green-500/5 p-3 text-center">
                <div className="text-xs text-muted-foreground mb-1">Applied jobs</div>
                <div className="font-bold text-xl text-green-600">{db.cleanup_candidates.applied.toLocaleString()}</div>
              </div>
              <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/5 p-3 text-center">
                <div className="text-xs text-muted-foreground mb-1">Older than 30 days</div>
                <div className="font-bold text-xl text-yellow-600">{db.cleanup_candidates.older_than_30d.toLocaleString()}</div>
              </div>
              <div className="rounded-lg border border-orange-500/30 bg-orange-500/5 p-3 text-center">
                <div className="text-xs text-muted-foreground mb-1">Older than 60 days</div>
                <div className="font-bold text-xl text-orange-600">{db.cleanup_candidates.older_than_60d.toLocaleString()}</div>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-3">
              Tip: deleting rejected + old unapplied jobs is safe and will free the most space.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Scraper Run Logs */}
      {db.scraper_runs && db.scraper_runs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Timer className="h-5 w-5" />
              Scraper Run Timing
              <span className="text-sm font-normal text-muted-foreground ml-1">— last {db.scraper_runs.length} country runs</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="text-left p-2">Country</th>
                    <th className="text-left p-2">Started</th>
                    <th className="text-left p-2">Total</th>
                    <th className="text-left p-2">Fetch Jobs</th>
                    <th className="text-left p-2">Scraping</th>
                    <th className="text-left p-2">Upload</th>
                    <th className="text-left p-2">Terms</th>
                    <th className="text-left p-2">New Jobs</th>
                    <th className="text-left p-2">Run</th>
                  </tr>
                </thead>
                <tbody>
                  {db.scraper_runs.map((run, i) => {
                    const total = run.duration_seconds || 0;
                    const scraping = run.phases.scraping || 0;
                    const scrapingPct = total > 0 ? Math.round((scraping / total) * 100) : 0;
                    const hasError = !!run.error;
                    return (
                      <tr key={i} className={`border-b hover:bg-muted/50 ${hasError ? 'bg-red-500/5' : ''}`}>
                        <td className="p-2 font-medium">{run.country}</td>
                        <td className="p-2 text-muted-foreground">{formatDate(run.started_at)}</td>
                        <td className="p-2 font-mono">
                          <span className={total > 900 ? 'text-red-500' : total > 600 ? 'text-yellow-500' : 'text-green-600'}>
                            {formatDuration(run.duration_seconds)}
                          </span>
                        </td>
                        <td className="p-2 font-mono text-muted-foreground">{formatDuration(run.phases.fetch_existing)}</td>
                        <td className="p-2">
                          <div className="flex items-center gap-1">
                            <span className="font-mono">{formatDuration(run.phases.scraping)}</span>
                            {scrapingPct > 0 && (
                              <span className="text-xs text-muted-foreground">({scrapingPct}%)</span>
                            )}
                          </div>
                        </td>
                        <td className="p-2 font-mono text-muted-foreground">{formatDuration(run.phases.upload)}</td>
                        <td className="p-2">
                          <span className={`${(run.failed_searches || 0) > 0 ? 'text-red-500' : ''}`}>
                            {run.successful_searches}/{run.total_terms}
                            {(run.failed_searches || 0) > 0 && ` (${run.failed_searches} failed)`}
                          </span>
                        </td>
                        <td className="p-2 font-medium text-green-600">+{run.new_jobs ?? '—'}</td>
                        <td className="p-2">
                          {run.github_run_number ? (
                            <a
                              href={`https://github.com/nickykapur/job-scrapper/actions/runs/${run.github_run_id}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-500 hover:underline flex items-center gap-1"
                            >
                              #{run.github_run_number} <ExternalLink className="h-3 w-3" />
                            </a>
                          ) : '—'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-muted-foreground mt-3">
              Total time colored: <span className="text-green-600">green</span> = under 10 min, <span className="text-yellow-500">yellow</span> = 10-15 min, <span className="text-red-500">red</span> = over 15 min
            </p>
          </CardContent>
        </Card>
      )}

      {/* Job Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Job Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          {db.error ? (
            <p className="text-sm text-red-500">{db.error}</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* By Country */}
              <div>
                <h3 className="font-semibold mb-2 text-sm">By Country</h3>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-muted-foreground">
                      <th className="text-left p-2">Country</th>
                      <th className="text-left p-2">Count</th>
                      <th className="text-left p-2">Last Scraped</th>
                    </tr>
                  </thead>
                  <tbody>
                    {db.by_country.map((row) => (
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
                <h3 className="font-semibold mb-2 text-sm">By Job Type</h3>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-muted-foreground">
                      <th className="text-left p-2">Job Type</th>
                      <th className="text-left p-2">Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {db.by_job_type.map((row) => (
                      <tr key={row.job_type} className="border-b hover:bg-muted/50">
                        <td className="p-2 capitalize">{row.job_type}</td>
                        <td className="p-2 font-medium">{row.count.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

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
