import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Users, RefreshCw, AlertCircle, MousePointerClick,
  Eye, Briefcase, ChevronDown, ChevronUp, Clock,
} from 'lucide-react';
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

const formatTimeAgo = (iso: string | null): string => {
  if (!iso) return '—';
  try {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  } catch {
    return iso ?? '—';
  }
};

const PAGE_COLORS: Record<string, string> = {
  jobs:           'bg-blue-100 text-blue-700',
  analytics:      'bg-purple-100 text-purple-700',
  'my-analytics': 'bg-indigo-100 text-indigo-700',
  applied:        'bg-green-100 text-green-700',
  interview:      'bg-amber-100 text-amber-700',
  settings:       'bg-gray-100 text-gray-700',
};

const pageColor = (page: string) =>
  PAGE_COLORS[page] ?? 'bg-slate-100 text-slate-600';

interface UserCardProps {
  username: string;
  display_name: string;
  events: ActivityEvent[];
}

const UserCard: React.FC<UserCardProps> = ({ username, display_name, events }) => {
  const [expanded, setExpanded] = useState(false);

  const applied   = events.filter(e => e.event_type === 'job_action' && e.event_data?.action === 'applied').length;
  const rejected  = events.filter(e => e.event_type === 'job_action' && e.event_data?.action === 'rejected').length;
  const pageViews = events.filter(e => e.event_type === 'page_view').length;
  const total     = events.length;
  const lastSeen  = events[0]?.occurred_at ?? null;

  // Pages visited (unique, in order of first visit)
  const pagesVisited = [...new Set(
    events
      .filter(e => e.event_type === 'page_view' && e.event_data?.page)
      .map(e => e.event_data.page as string)
  )];

  // Activity bar widths
  const applyPct   = total > 0 ? Math.round((applied  / total) * 100) : 0;
  const rejectPct  = total > 0 ? Math.round((rejected / total) * 100) : 0;
  const viewPct    = total > 0 ? Math.round((pageViews / total) * 100) : 0;

  const initials = display_name
    .split(' ')
    .map(p => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <div className="rounded-xl border bg-card overflow-hidden">
      {/* Card header row */}
      <div
        className="flex items-center gap-4 p-4 cursor-pointer hover:bg-muted/40 transition-colors select-none"
        onClick={() => setExpanded(x => !x)}
      >
        {/* Avatar */}
        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center font-bold text-sm shrink-0">
          {initials}
        </div>

        {/* Name + last seen */}
        <div className="flex-1 min-w-0">
          <div className="font-semibold leading-tight truncate">{display_name}</div>
          <div className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
            <Clock className="h-3 w-3" />
            {formatTimeAgo(lastSeen)}
          </div>
        </div>

        {/* Stat pills */}
        <div className="flex items-center gap-2 shrink-0 flex-wrap justify-end">
          {applied > 0 && (
            <span className="inline-flex items-center gap-1 rounded-full bg-green-100 text-green-700 px-2.5 py-0.5 text-xs font-semibold">
              <Briefcase className="h-3 w-3" />
              {applied} applied
            </span>
          )}
          {rejected > 0 && (
            <span className="inline-flex items-center gap-1 rounded-full bg-red-100 text-red-700 px-2.5 py-0.5 text-xs font-semibold">
              {rejected} rejected
            </span>
          )}
          <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 text-blue-700 px-2.5 py-0.5 text-xs font-semibold">
            <Eye className="h-3 w-3" />
            {pageViews} views
          </span>
          <span className="text-xs text-muted-foreground">{total} total</span>
        </div>

        {/* Expand toggle */}
        <div className="text-muted-foreground shrink-0">
          {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </div>
      </div>

      {/* Activity ratio bar */}
      <div className="h-1.5 flex mx-4 mb-3 rounded-full overflow-hidden bg-muted">
        {applyPct  > 0 && <div className="bg-green-500 transition-all" style={{ width: `${applyPct}%` }} />}
        {rejectPct > 0 && <div className="bg-red-400  transition-all" style={{ width: `${rejectPct}%` }} />}
        {viewPct   > 0 && <div className="bg-blue-400 transition-all" style={{ width: `${viewPct}%` }} />}
      </div>

      {/* Expanded detail panel */}
      {expanded && (
        <div className="border-t px-4 pb-4 pt-3 space-y-3">

          {/* Pages visited */}
          {pagesVisited.length > 0 && (
            <div>
              <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
                Pages visited
              </div>
              <div className="flex flex-wrap gap-1.5">
                {pagesVisited.map(page => (
                  <span
                    key={page}
                    className={`text-xs rounded-full px-2.5 py-0.5 font-medium capitalize ${pageColor(page)}`}
                  >
                    {page.replace(/-/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Event timeline */}
          <div>
            <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
              Activity timeline
            </div>
            <div className="space-y-1 max-h-64 overflow-y-auto pr-1">
              {events.map(e => {
                const isApply   = e.event_type === 'job_action' && e.event_data?.action === 'applied';
                const isReject  = e.event_type === 'job_action' && e.event_data?.action === 'rejected';
                const isView    = e.event_type === 'page_view';

                const dotColor  = isApply  ? 'bg-green-500'
                                : isReject ? 'bg-red-400'
                                : isView   ? 'bg-blue-400'
                                :            'bg-muted-foreground';

                const label     = isApply  ? 'Applied to job'
                                : isReject ? 'Rejected job'
                                : isView   ? `Viewed: ${(e.event_data?.page ?? '').replace(/-/g, ' ')}`
                                : e.event_type;

                const detail    = isApply || isReject
                  ? e.event_data?.job_id ? `job #${e.event_data.job_id}` : ''
                  : '';

                return (
                  <div key={e.id} className="flex items-start gap-2.5 py-1">
                    <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${dotColor}`} />
                    <div className="flex-1 min-w-0">
                      <span className="text-sm">{label}</span>
                      {detail && (
                        <span className="text-xs text-muted-foreground ml-1.5 font-mono">{detail}</span>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground shrink-0 whitespace-nowrap">
                      {formatDate(e.occurred_at)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export const UserBehaviourPage: React.FC = () => {
  const [data, setData]       = useState<ActivityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);
  const [filterUser, setFilterUser] = useState<string | null>(null);

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

  // Group events by user (preserve insertion order → most recently active first)
  const byUser: Record<string, { display_name: string; events: ActivityEvent[] }> = {};
  for (const e of data.events) {
    if (!byUser[e.username]) byUser[e.username] = { display_name: e.display_name, events: [] };
    byUser[e.username].events.push(e);
  }

  const jobActions   = data.events.filter(e => e.event_type === 'job_action');
  const appliedCount = jobActions.filter(e => e.event_data?.action === 'applied').length;
  const rejectedCount= jobActions.filter(e => e.event_data?.action === 'rejected').length;

  const userList = Object.keys(byUser);
  const filteredEvents = filterUser
    ? data.events.filter(e => e.username === filterUser)
    : data.events;

  return (
    <div className="container mx-auto p-6 max-w-7xl space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <MousePointerClick className="h-8 w-8" />
            User Behaviour
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Last 7 days · {userList.length} active users</p>
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
            <CardTitle className="flex items-center gap-2 text-base">
              <Eye className="h-5 w-5" />
              Page Views (7d) — all users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {data.page_views_7d.map(({ page, count }) => (
                <div key={page} className={`rounded-lg border px-4 py-2 text-center min-w-[90px] ${pageColor(page)}`}>
                  <div className="text-xs font-medium capitalize mb-1">{page.replace(/-/g, ' ')}</div>
                  <div className="font-bold text-xl">{count}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Per-user expandable cards */}
      {userList.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-5 w-5 text-muted-foreground" />
            <h2 className="text-lg font-semibold">Per-User Activity</h2>
            <span className="text-sm text-muted-foreground">— click a card to expand the timeline</span>
          </div>
          <div className="space-y-3">
            {userList.map(username => (
              <UserCard
                key={username}
                username={username}
                display_name={byUser[username].display_name}
                events={byUser[username].events}
              />
            ))}
          </div>
        </div>
      )}

      {/* Recent events log with per-user filter */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <CardTitle className="text-base">Recent Events</CardTitle>
            {/* User filter tabs */}
            {userList.length > 1 && (
              <div className="flex flex-wrap gap-1.5">
                <button
                  onClick={() => setFilterUser(null)}
                  className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                    filterUser === null
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'bg-background hover:bg-muted border-border'
                  }`}
                >
                  All users
                </button>
                {userList.map(u => (
                  <button
                    key={u}
                    onClick={() => setFilterUser(filterUser === u ? null : u)}
                    className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                      filterUser === u
                        ? 'bg-primary text-primary-foreground border-primary'
                        : 'bg-background hover:bg-muted border-border'
                    }`}
                  >
                    {byUser[u].display_name}
                  </button>
                ))}
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {filteredEvents.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-6">
              No events recorded yet.
            </p>
          ) : (
            <div className="overflow-x-auto max-h-96 overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-background z-10">
                  <tr className="border-b text-muted-foreground text-xs uppercase tracking-wide">
                    <th className="text-left p-2">Time</th>
                    <th className="text-left p-2">User</th>
                    <th className="text-left p-2">Event</th>
                    <th className="text-left p-2">Details</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredEvents.map((e) => {
                    const isApply  = e.event_type === 'job_action' && e.event_data?.action === 'applied';
                    const isReject = e.event_type === 'job_action' && e.event_data?.action === 'rejected';
                    return (
                      <tr key={e.id} className="border-b hover:bg-muted/40">
                        <td className="p-2 text-muted-foreground whitespace-nowrap text-xs">
                          {formatDate(e.occurred_at)}
                        </td>
                        <td className="p-2">
                          <span className="font-medium text-xs">{e.display_name}</span>
                        </td>
                        <td className="p-2">
                          {e.event_type === 'page_view' ? (
                            <span className="inline-flex items-center gap-1 text-xs rounded-full bg-blue-100 text-blue-700 px-2 py-0.5">
                              <Eye className="h-3 w-3" />
                              {(e.event_data?.page ?? 'page').replace(/-/g, ' ')}
                            </span>
                          ) : isApply ? (
                            <span className="inline-flex items-center gap-1 text-xs rounded-full bg-green-100 text-green-700 px-2 py-0.5">
                              <Briefcase className="h-3 w-3" />
                              applied
                            </span>
                          ) : isReject ? (
                            <span className="inline-flex items-center gap-1 text-xs rounded-full bg-red-100 text-red-700 px-2 py-0.5">
                              rejected
                            </span>
                          ) : (
                            <Badge variant="outline" className="text-xs">{e.event_type}</Badge>
                          )}
                        </td>
                        <td className="p-2 text-xs text-muted-foreground font-mono">
                          {Object.keys(e.event_data).length > 0
                            ? Object.entries(e.event_data)
                                .filter(([k]) => k !== 'action' && k !== 'page')
                                .map(([k, v]) => `${k}=${v}`)
                                .join(', ') || '—'
                            : '—'}
                        </td>
                      </tr>
                    );
                  })}
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
