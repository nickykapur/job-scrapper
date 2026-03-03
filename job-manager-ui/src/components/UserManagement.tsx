import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Users, CheckCircle, XCircle, Clock, AlertCircle, Plus, X } from 'lucide-react';
import { jobApi } from '../services/api';

interface UserData {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
  job_types: string[] | null;
  countries: string[] | null;
  stats: {
    total_applied: number;
    total_rejected: number;
    total_saved: number;
    last_interaction: string | null;
  };
}

const ALL_JOB_TYPES = ['software', 'hr', 'cybersecurity', 'sales', 'finance', 'marketing', 'data', 'design', 'biotech', 'engineering', 'events'];
const ALL_COUNTRIES = ['Ireland', 'Spain', 'Panama', 'Luxembourg', 'Germany', 'Switzerland', 'United States'];

interface CreateUserForm {
  username: string;
  email: string;
  password: string;
  full_name: string;
  is_admin: boolean;
  job_types: string[];
  keywords: string[];
  preferred_countries: string[];
}

export const UserManagement: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [users, setUsers] = useState<UserData[]>([]);
  const [processingUserId, setProcessingUserId] = useState<number | null>(null);

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [keywordInput, setKeywordInput] = useState('');
  const [createForm, setCreateForm] = useState<CreateUserForm>({
    username: '',
    email: '',
    password: '',
    full_name: '',
    is_admin: false,
    job_types: [],
    keywords: [],
    preferred_countries: [],
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await jobApi.getAllUsers();
      setUsers(data.users);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load users');
      console.error('Failed to load users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleUserStatus = async (userId: number, currentStatus: boolean) => {
    try {
      setProcessingUserId(userId);

      if (currentStatus) {
        // Deactivate user
        await jobApi.deactivateUser(userId);
      } else {
        // Activate user
        await jobApi.activateUser(userId);
      }

      // Reload users to get updated status
      await loadUsers();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to update user status';
      alert(errorMsg);
      console.error('Failed to update user:', err);
    } finally {
      setProcessingUserId(null);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setCreateError(null);
    try {
      await jobApi.createUser({
        username: createForm.username,
        email: createForm.email,
        password: createForm.password,
        full_name: createForm.full_name || undefined,
        is_admin: createForm.is_admin,
        job_types: createForm.job_types.length ? createForm.job_types : undefined,
        keywords: createForm.keywords.length ? createForm.keywords : undefined,
        preferred_countries: createForm.preferred_countries.length ? createForm.preferred_countries : undefined,
      });
      setShowCreateForm(false);
      setCreateForm({ username: '', email: '', password: '', full_name: '', is_admin: false, job_types: [], keywords: [], preferred_countries: [] });
      setKeywordInput('');
      await loadUsers();
    } catch (err: any) {
      setCreateError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setCreating(false);
    }
  };

  const toggleJobType = (type: string) => {
    setCreateForm(prev => ({
      ...prev,
      job_types: prev.job_types.includes(type)
        ? prev.job_types.filter(t => t !== type)
        : [...prev.job_types, type],
    }));
  };

  const toggleCountry = (country: string) => {
    setCreateForm(prev => ({
      ...prev,
      preferred_countries: prev.preferred_countries.includes(country)
        ? prev.preferred_countries.filter(c => c !== country)
        : [...prev.preferred_countries, country],
    }));
  };

  const addKeyword = () => {
    const kw = keywordInput.trim();
    if (kw && !createForm.keywords.includes(kw)) {
      setCreateForm(prev => ({ ...prev, keywords: [...prev.keywords, kw] }));
    }
    setKeywordInput('');
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading users...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="max-w-md">
          <CardContent className="p-6">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Error Loading Users</h3>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button onClick={loadUsers}>Try Again</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const activeUsers = users.filter(u => u.is_active);
  const inactiveUsers = users.filter(u => !u.is_active);

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2 mb-2">
            <Users className="h-8 w-8" />
            User Management
          </h1>
          <p className="text-muted-foreground">
            Manage user accounts and their active status
          </p>
        </div>
        <Button onClick={() => { setShowCreateForm(!showCreateForm); setCreateError(null); }} className="flex items-center gap-2">
          {showCreateForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showCreateForm ? 'Cancel' : 'Create User'}
        </Button>
      </div>

      {/* Create User Form */}
      {showCreateForm && (
        <Card className="mb-6 border-primary/50">
          <CardHeader>
            <CardTitle className="text-lg">Create New User</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateUser} className="space-y-4">
              {createError && (
                <div className="p-3 rounded bg-red-500/10 border border-red-500/30 text-red-600 text-sm">
                  {createError}
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Username *</label>
                  <Input
                    required
                    placeholder="username"
                    value={createForm.username}
                    onChange={e => setCreateForm(p => ({ ...p, username: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Full Name</label>
                  <Input
                    placeholder="Full Name"
                    value={createForm.full_name}
                    onChange={e => setCreateForm(p => ({ ...p, full_name: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Email *</label>
                  <Input
                    required
                    type="email"
                    placeholder="email@example.com"
                    value={createForm.email}
                    onChange={e => setCreateForm(p => ({ ...p, email: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Password *</label>
                  <Input
                    required
                    type="password"
                    placeholder="Min 8 characters"
                    value={createForm.password}
                    onChange={e => setCreateForm(p => ({ ...p, password: e.target.value }))}
                  />
                </div>
              </div>

              {/* Job Types */}
              <div>
                <label className="block text-sm font-medium mb-2">Job Types</label>
                <div className="flex flex-wrap gap-2">
                  {ALL_JOB_TYPES.map(type => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => toggleJobType(type)}
                      className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                        createForm.job_types.includes(type)
                          ? 'bg-primary text-primary-foreground border-primary'
                          : 'border-muted-foreground/30 hover:border-primary/50'
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              {/* Countries */}
              <div>
                <label className="block text-sm font-medium mb-2">Preferred Countries</label>
                <div className="flex flex-wrap gap-2">
                  {ALL_COUNTRIES.map(country => (
                    <button
                      key={country}
                      type="button"
                      onClick={() => toggleCountry(country)}
                      className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                        createForm.preferred_countries.includes(country)
                          ? 'bg-primary text-primary-foreground border-primary'
                          : 'border-muted-foreground/30 hover:border-primary/50'
                      }`}
                    >
                      {country}
                    </button>
                  ))}
                </div>
              </div>

              {/* Keywords */}
              <div>
                <label className="block text-sm font-medium mb-2">Custom Search Keywords</label>
                <div className="flex gap-2 mb-2">
                  <Input
                    placeholder="e.g., Python Developer"
                    value={keywordInput}
                    onChange={e => setKeywordInput(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addKeyword(); } }}
                  />
                  <Button type="button" variant="outline" onClick={addKeyword}>Add</Button>
                </div>
                {createForm.keywords.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {createForm.keywords.map(kw => (
                      <span key={kw} className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-muted border">
                        {kw}
                        <button type="button" onClick={() => setCreateForm(p => ({ ...p, keywords: p.keywords.filter(k => k !== kw) }))}>
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_admin"
                  checked={createForm.is_admin}
                  onChange={e => setCreateForm(p => ({ ...p, is_admin: e.target.checked }))}
                  className="rounded"
                />
                <label htmlFor="is_admin" className="text-sm">Grant admin privileges</label>
              </div>

              <div className="flex gap-3 pt-2">
                <Button type="submit" disabled={creating}>
                  {creating ? 'Creating...' : 'Create User'}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowCreateForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Users</p>
                <p className="text-2xl font-bold">{users.length}</p>
              </div>
              <Users className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-green-500/50 bg-green-500/5">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Users</p>
                <p className="text-2xl font-bold text-green-600">{activeUsers.length}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-red-500/50 bg-red-500/5">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Inactive Users</p>
                <p className="text-2xl font-bold text-red-600">{inactiveUsers.length}</p>
              </div>
              <XCircle className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3 font-semibold">User</th>
                  <th className="text-left p-3 font-semibold">Email</th>
                  <th className="text-left p-3 font-semibold">Status</th>
                  <th className="text-left p-3 font-semibold">Job Types</th>
                  <th className="text-left p-3 font-semibold">Stats</th>
                  <th className="text-left p-3 font-semibold">Last Login</th>
                  <th className="text-right p-3 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-muted/50">
                    <td className="p-3">
                      <div>
                        <div className="font-semibold">{user.full_name || user.username}</div>
                        <div className="text-sm text-muted-foreground">@{user.username}</div>
                      </div>
                    </td>
                    <td className="p-3 text-sm">{user.email}</td>
                    <td className="p-3">
                      <div className="flex items-center gap-2">
                        {user.is_active ? (
                          <Badge className="bg-green-500/20 text-green-600 dark:text-green-400 border-green-500/50">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Active
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="border-red-500/50 text-red-600 dark:text-red-400">
                            <XCircle className="h-3 w-3 mr-1" />
                            Inactive
                          </Badge>
                        )}
                        {user.is_admin && (
                          <Badge variant="secondary" className="text-xs">
                            Admin
                          </Badge>
                        )}
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="flex flex-wrap gap-1">
                        {user.job_types && user.job_types.length > 0 ? (
                          user.job_types.slice(0, 2).map((type) => (
                            <Badge key={type} variant="outline" className="text-xs">
                              {type}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-xs text-muted-foreground">None</span>
                        )}
                        {user.job_types && user.job_types.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{user.job_types.length - 2}
                          </Badge>
                        )}
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="text-sm space-y-1">
                        <div className="text-green-600 dark:text-green-400">
                          {user.stats.total_applied} applied
                        </div>
                        <div className="text-red-600 dark:text-red-400">
                          {user.stats.total_rejected} rejected
                        </div>
                      </div>
                    </td>
                    <td className="p-3 text-sm">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {formatDate(user.last_login)}
                      </div>
                    </td>
                    <td className="p-3 text-right">
                      <Button
                        size="sm"
                        variant={user.is_active ? "destructive" : "default"}
                        onClick={() => handleToggleUserStatus(user.id, user.is_active)}
                        disabled={processingUserId === user.id || user.is_admin}
                      >
                        {processingUserId === user.id ? (
                          <div className="flex items-center gap-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            Processing...
                          </div>
                        ) : user.is_active ? (
                          'Deactivate'
                        ) : (
                          'Activate'
                        )}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {users.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                <Users className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No users found</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default UserManagement;
