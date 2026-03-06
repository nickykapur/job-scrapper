import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Users, RefreshCw, AlertCircle, MousePointerClick, Eye, Briefcase } from 'lucide-react';
import { jobApi } from '../services/api';

interface ActivityEvent {
  id: number;
  user_id: number;
  username: string;
  display_name: string;
  event_type: string;
  event_data: Record<string, any>;
  occurred_at: string | null;
}

interface ActivityData {
  active_today: number;
  total_events_7d: number;
  page_views_7d: { page: string; count: number }[];
  events: ActivityEvent[];
}

const formatDate = (iso: string | null): string => {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('en-US', {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  } catch {
    return iso;
  }
};

const EVENT_LABELS: Record<string, { label: string; icon: React.ReactNode }> = {
  page_view:  { label: 'Page View',   icon: <Eye className="h-3 w-3" /> },
  job_action: { label: 'Job Action',  icon: <Briefcase className="h-3 w-3" /> },
};

export const UserBehaviourPage: React.FC = () => {
  const [data, setData] = useState<ActivityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await jobApi.getActivity(200);
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load activity data');
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
          <p className="text-muted-foreground">Loading user behaviour data...</p>
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

  // Group events by user for per-user breakdown
  const byUser: Record<string, { display_name: string; events: ActivityEvent[] }> = {};
  for (const e of data.events) {
    if (!byUser[e.username]) byUser[e.username] = { display_name: e.display_name, events: [] };
    byUser[e.username].events.push(e);
  }

  const jobActions = data.events.filter(e => e.event_type === 'job_action');
  const appliedCount = jobActions.filter(e => e.event_data?.action === 'applied').length;
  const rejectedCount = jobActions.filter(e => e.event_data?.action === 'rejected').length;

  return (
    <div className="container mx-auto p-6 max-w-7xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <MousePointerClick className="h-8 w-8" />
            User Behaviour
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Last 7 days of user activity</p>
        </div>
        <Button variant="outline" onClick={load} className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-xs text-muted-foreground mb-1">Active today</div>
            <div className="font-bold text-3xl text-blue-600">{data.active_today}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-xs text-muted-foreground mb-1">Total events (7d)</div>
            <div className="font-bold text-3xl">{data.total_events_7d.toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-xs text-muted-foreground mb-1">Applied (7d)</div>
            <div className="font-bold text-3xl text-green-600">{appliedCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-xs text-muted-foreground mb-1">Rejected (7d)</div>
            <div className="font-bold text-3xl text-red-600">{rejectedCount}</div>
          </CardContent>
        </Card>
      </div>

      {/* Page view breakdown */}
      {data.page_views_7d.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Page Views (7d)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {data.page_views_7d.map(({ page, count }) => (
                <div key={page} className="rounded-lg border px-4 py-2 text-center min-w-[100px]">
                  <div className="text-xs text-muted-foreground capitalize mb-1">{page.replace(/-/g, ' ')}</div>
                  <div className="font-bold text-xl">{count}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Per-user breakdown */}
      {Object.keys(byUser).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Per-User Activity (last 200 events)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(byUser).map(([username, { display_name, events }]) => {
                const userApplied = events.filter(e => e.event_type === 'job_action' && e.event_data?.action === 'applied').length;
                const userRejected = events.filter(e => e.event_type === 'job_action' && e.event_data?.action === 'rejected').length;
                const userPageViews = events.filter(e => e.event_type === 'page_view').length;
                const lastSeen = events[0]?.occurred_at;
                return (
                  <div key={username} className="flex items-center gap-4 rounded-lg border p-3">
                    <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center font-bold text-sm shrink-0">
                      {display_name[0]?.toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium">{display_name}</div>
                      <div className="text-xs text-muted-foreground">Last seen: {formatDate(lastSeen)}</div>
                    </div>
                    <div className="flex gap-3 text-sm shrink-0">
                      <span className="text-green-600 font-medium">{userApplied} applied</span>
                      <span className="text-red-500 font-medium">{userRejected} rejected</span>
                      <span className="text-muted-foreground">{userPageViews} views</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Full event log */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Events</CardTitle>
        </CardHeader>
        <CardContent>
          {data.events.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-6">
              No events recorded yet. Events will appear here as users navigate the app.
            </p>
          ) : (
            <div className="overflow-x-auto max-h-96 overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-background">
                  <tr className="border-b text-muted-foreground">
                    <th className="text-left p-2">Time</th>
                    <th className="text-left p-2">User</th>
                    <th className="text-left p-2">Event</th>
                    <th className="text-left p-2">Details</th>
                  </tr>
                </thead>
                <tbody>
                  {data.events.map((e) => (
                    <tr key={e.id} className="border-b hover:bg-muted/50">
                      <td className="p-2 text-muted-foreground whitespace-nowrap">{formatDate(e.occurred_at)}</td>
                      <td className="p-2 font-medium">{e.display_name}</td>
                      <td className="p-2">
                        <Badge variant="outline" className="text-xs flex items-center gap-1 w-fit">
                          {EVENT_LABELS[e.event_type]?.icon}
                          {EVENT_LABELS[e.event_type]?.label ?? e.event_type}
                        </Badge>
                      </td>
                      <td className="p-2 text-xs text-muted-foreground font-mono">
                        {Object.keys(e.event_data).length > 0
                          ? Object.entries(e.event_data).map(([k, v]) => `${k}=${v}`).join(', ')
                          : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default UserBehaviourPage;
