import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import {
  Plus, X, Building2, MapPin, Calendar, GripVertical,
  Clock, Edit, Archive, CheckCircle2, XCircle, AlertCircle,
  DollarSign, Mail, StickyNote, TrendingUp
} from 'lucide-react';
import toast from 'react-hot-toast';

interface TrackedJob {
  id: string;
  company: string;
  position: string;
  location: string;
  stage: 'recruiter' | 'technical' | 'final';
  applicationDate: string;
  recruiterDate?: string;
  technicalDate?: string;
  finalDate?: string;
  expectedResponseDate?: string;
  salaryRange?: string;
  recruiterContact?: string;
  recruiterEmail?: string;
  notes?: string;
  stageNotes?: {
    recruiter?: string;
    technical?: string;
    final?: string;
  };
  lastUpdated: string;
  archived?: boolean;
  archiveOutcome?: 'rejected' | 'no-response' | 'accepted' | 'declined';
  archiveDate?: string;
  archiveNotes?: string;
  rejectionStage?: 'recruiter' | 'technical' | 'final' | 'application';
  rejectionReasons?: string[]; // e.g., ['visa', 'experience', 'salary']
  rejectionDetails?: string;
}

const STAGES = [
  { id: 'recruiter', label: 'Recruiter Call', color: 'bg-blue-500', textColor: 'text-blue-600' },
  { id: 'technical', label: 'Technical Interview', color: 'bg-purple-500', textColor: 'text-purple-600' },
  { id: 'final', label: 'Final/Awaiting Response', color: 'bg-emerald-500', textColor: 'text-emerald-600' },
] as const;

const ARCHIVE_OUTCOMES = [
  { id: 'rejected', label: 'Rejected by Company', icon: XCircle, color: 'text-red-600' },
  { id: 'no-response', label: 'No Response / Ghosted', icon: AlertCircle, color: 'text-gray-600' },
  { id: 'accepted', label: 'Offer Accepted', icon: CheckCircle2, color: 'text-green-600' },
  { id: 'declined', label: 'Declined by Me', icon: XCircle, color: 'text-orange-600' },
] as const;

const REJECTION_REASONS = [
  { id: 'visa', label: '🛂 Visa / Work Authorization', description: 'No sponsorship or visa issues' },
  { id: 'experience', label: '💼 Experience Level', description: 'Too junior or too senior' },
  { id: 'skills', label: '⚙️ Technical Skills Gap', description: 'Missing required skills' },
  { id: 'salary', label: '💰 Salary Expectations', description: 'Compensation mismatch' },
  { id: 'location', label: '📍 Location / Remote', description: 'Location or remote work issues' },
  { id: 'timeline', label: '⏰ Timeline / Availability', description: 'Start date or availability issues' },
  { id: 'budget', label: '💳 Company Budget', description: 'Position on hold or budget cuts' },
  { id: 'culture', label: '🤝 Cultural Fit', description: 'Not a good culture match' },
  { id: 'overqualified', label: '📚 Overqualified', description: 'Too much experience' },
  { id: 'other', label: '❓ Other', description: 'Other reasons' },
] as const;

export const InterviewTracker: React.FC = () => {
  const [trackedJobs, setTrackedJobs] = useState<TrackedJob[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingJob, setEditingJob] = useState<TrackedJob | null>(null);
  const [showArchive, setShowArchive] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [draggedJob, setDraggedJob] = useState<TrackedJob | null>(null);
  const [archivingJob, setArchivingJob] = useState<TrackedJob | null>(null);
  const [newJob, setNewJob] = useState({
    company: '',
    position: '',
    location: '',
    stage: 'recruiter' as const,
    applicationDate: new Date().toISOString().split('T')[0],
    salaryRange: '',
    recruiterContact: '',
    recruiterEmail: '',
  });

  // Load from API on mount
  useEffect(() => {
    const loadTrackedJobs = async () => {
      try {
        // Try to load from API first
        const apiData = await jobApi.getInterviewTracker();
        if (apiData && apiData.length > 0) {
          setTrackedJobs(apiData);
          // Also save to localStorage as cache
          localStorage.setItem('interview-tracker-v2', JSON.stringify(apiData));
          return;
        }
      } catch (error) {
        console.error('Failed to load from API, trying localStorage:', error);
      }

      // Fallback to localStorage if API fails
      const saved = localStorage.getItem('interview-tracker-v2');
      if (saved) {
        try {
          setTrackedJobs(JSON.parse(saved));
        } catch (error) {
          console.error('Failed to load tracked jobs from localStorage:', error);
        }
      }
    };

    loadTrackedJobs();
  }, []);

  // Save to both localStorage and API whenever trackedJobs changes
  useEffect(() => {
    const saveTrackedJobs = async () => {
      // Save to localStorage immediately (fast)
      localStorage.setItem('interview-tracker-v2', JSON.stringify(trackedJobs));

      // Save to API (slower, but persistent)
      if (trackedJobs.length === 0) return; // Don't save empty array on initial load

      try {
        await jobApi.saveInterviewTracker(trackedJobs);
        console.log('✅ Interview tracker synced to backend');
      } catch (error: any) {
        // Only show error if it's not a 404 (endpoint not deployed yet)
        if (error?.response?.status === 404) {
          console.warn('⚠️ Interview tracker API not deployed yet. Data saved locally.');
        } else {
          console.error('Failed to save to API:', error?.response?.data || error);
          toast.error('Failed to sync interview tracker. Data saved locally.');
        }
      }
    };

    saveTrackedJobs();
  }, [trackedJobs]);

  const handleAddJob = () => {
    if (!newJob.company || !newJob.position) {
      toast.error('Company and position are required');
      return;
    }

    const job: TrackedJob = {
      id: Date.now().toString(),
      company: newJob.company,
      position: newJob.position,
      location: newJob.location || 'Remote',
      stage: newJob.stage,
      applicationDate: newJob.applicationDate,
      salaryRange: newJob.salaryRange,
      recruiterContact: newJob.recruiterContact,
      recruiterEmail: newJob.recruiterEmail,
      lastUpdated: new Date().toISOString(),
      stageNotes: {},
    };

    setTrackedJobs([...trackedJobs, job]);
    setNewJob({
      company: '',
      position: '',
      location: '',
      stage: 'recruiter',
      applicationDate: new Date().toISOString().split('T')[0],
      salaryRange: '',
      recruiterContact: '',
      recruiterEmail: '',
    });
    setShowAddForm(false);
    toast.success('Job added to tracker!');
  };

  const handleDeleteJob = (id: string) => {
    if (!window.confirm('Are you sure you want to delete this application?')) return;
    setTrackedJobs(trackedJobs.filter(job => job.id !== id));
    toast.success('Application deleted');
  };

  const handleArchiveJob = (
    id: string,
    outcome: 'rejected' | 'no-response' | 'accepted' | 'declined',
    rejectionStage?: 'recruiter' | 'technical' | 'final' | 'application',
    rejectionReasons?: string[],
    rejectionDetails?: string,
    notes?: string
  ) => {
    setTrackedJobs(trackedJobs.map(job =>
      job.id === id ? {
        ...job,
        archived: true,
        archiveOutcome: outcome,
        archiveDate: new Date().toISOString(),
        archiveNotes: notes,
        rejectionStage: outcome === 'rejected' ? rejectionStage : undefined,
        rejectionReasons: outcome === 'rejected' ? rejectionReasons : undefined,
        rejectionDetails: outcome === 'rejected' ? rejectionDetails : undefined,
        lastUpdated: new Date().toISOString(),
      } : job
    ));
    setArchivingJob(null);
    toast.success('Application archived');
  };

  const handleUnarchiveJob = (id: string) => {
    setTrackedJobs(trackedJobs.map(job =>
      job.id === id ? {
        ...job,
        archived: false,
        archiveOutcome: undefined,
        archiveDate: undefined,
        lastUpdated: new Date().toISOString(),
      } : job
    ));
    toast.success('Application restored');
  };

  const handleMoveJob = (id: string, newStage: 'recruiter' | 'technical' | 'final') => {
    const today = new Date().toISOString().split('T')[0];
    setTrackedJobs(trackedJobs.map(job => {
      if (job.id !== id) return job;

      const updates: Partial<TrackedJob> = {
        stage: newStage,
        lastUpdated: new Date().toISOString(),
      };

      if (newStage === 'recruiter' && !job.recruiterDate) {
        updates.recruiterDate = today;
      } else if (newStage === 'technical' && !job.technicalDate) {
        updates.technicalDate = today;
      } else if (newStage === 'final' && !job.finalDate) {
        updates.finalDate = today;
      }

      return { ...job, ...updates };
    }));
    toast.success('Stage updated!');
  };

  const handleUpdateJob = (updatedJob: TrackedJob) => {
    setTrackedJobs(trackedJobs.map(job =>
      job.id === updatedJob.id ? { ...updatedJob, lastUpdated: new Date().toISOString() } : job
    ));
    setEditingJob(null);
    toast.success('Application updated!');
  };

  const getJobsByStage = (stage: 'recruiter' | 'technical' | 'final') => {
    return trackedJobs.filter(job => job.stage === stage && !job.archived);
  };

  const getArchivedJobs = () => {
    return trackedJobs.filter(job => job.archived);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const days = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    return `${days} days ago`;
  };

  const getDaysInStage = (job: TrackedJob) => {
    let stageDate: string | undefined;
    if (job.stage === 'recruiter') stageDate = job.recruiterDate || job.applicationDate;
    else if (job.stage === 'technical') stageDate = job.technicalDate;
    else if (job.stage === 'final') stageDate = job.finalDate;

    if (!stageDate) return null;
    const days = Math.floor((Date.now() - new Date(stageDate).getTime()) / (1000 * 60 * 60 * 24));
    return days;
  };

  const getTotalDays = (job: TrackedJob) => {
    const days = Math.floor((Date.now() - new Date(job.applicationDate).getTime()) / (1000 * 60 * 60 * 24));
    return days;
  };

  const handleDragStart = (job: TrackedJob) => {
    setDraggedJob(job);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (targetStage: 'recruiter' | 'technical' | 'final') => {
    if (draggedJob && draggedJob.stage !== targetStage) {
      handleMoveJob(draggedJob.id, targetStage);
    }
    setDraggedJob(null);
  };

  const activeJobs = trackedJobs.filter(j => !j.archived);
  const archivedJobs = getArchivedJobs();

  // Analytics calculations
  const rejectedJobs = archivedJobs.filter(j => j.archiveOutcome === 'rejected');
  const rejectionStats = {
    total: rejectedJobs.length,
    byStage: {
      application: rejectedJobs.filter(j => j.rejectionStage === 'application').length,
      recruiter: rejectedJobs.filter(j => j.rejectionStage === 'recruiter').length,
      technical: rejectedJobs.filter(j => j.rejectionStage === 'technical').length,
      final: rejectedJobs.filter(j => j.rejectionStage === 'final').length,
    },
    byReason: REJECTION_REASONS.map(reason => ({
      ...reason,
      count: rejectedJobs.filter(j => j.rejectionReasons?.includes(reason.id)).length,
    })).filter(r => r.count > 0).sort((a, b) => b.count - a.count),
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h3 className="text-2xl font-bold">Interview Tracker</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Track your interview progress • {activeJobs.length} active • {archivedJobs.length} archived
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          {rejectedJobs.length > 0 && (
            <Button
              variant={showAnalytics ? 'default' : 'outline'}
              onClick={() => {
                setShowAnalytics(!showAnalytics);
                setShowArchive(false);
              }}
            >
              <TrendingUp className="mr-2 h-4 w-4" />
              Analytics
            </Button>
          )}
          <Button
            variant={showArchive ? 'default' : 'outline'}
            onClick={() => {
              setShowArchive(!showArchive);
              setShowAnalytics(false);
            }}
          >
            <Archive className="mr-2 h-4 w-4" />
            {showArchive ? 'Hide' : 'Show'} Archive ({archivedJobs.length})
          </Button>
          <Button
            onClick={() => setShowAddForm(!showAddForm)}
            className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Application
          </Button>
        </div>
      </div>

      {/* Add Form */}
      {showAddForm && (
        <Card className="border-2 border-blue-500/20">
          <CardHeader>
            <CardTitle className="text-lg">Add New Application</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Company *</label>
                <Input
                  placeholder="e.g., Google"
                  value={newJob.company}
                  onChange={(e) => setNewJob({ ...newJob, company: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Position *</label>
                <Input
                  placeholder="e.g., Software Engineer"
                  value={newJob.position}
                  onChange={(e) => setNewJob({ ...newJob, position: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Location</label>
                <Input
                  placeholder="e.g., Dublin, Ireland"
                  value={newJob.location}
                  onChange={(e) => setNewJob({ ...newJob, location: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Application Date</label>
                <Input
                  type="date"
                  value={newJob.applicationDate}
                  onChange={(e) => setNewJob({ ...newJob, applicationDate: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Salary Range</label>
                <Input
                  placeholder="e.g., €50k - €70k"
                  value={newJob.salaryRange}
                  onChange={(e) => setNewJob({ ...newJob, salaryRange: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Initial Stage</label>
                <select
                  className="w-full h-10 px-3 rounded-md border border-input bg-background"
                  value={newJob.stage}
                  onChange={(e) => setNewJob({ ...newJob, stage: e.target.value as any })}
                >
                  {STAGES.map(stage => (
                    <option key={stage.id} value={stage.id}>{stage.label}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Recruiter Name</label>
                <Input
                  placeholder="e.g., John Doe"
                  value={newJob.recruiterContact}
                  onChange={(e) => setNewJob({ ...newJob, recruiterContact: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Recruiter Email</label>
                <Input
                  type="email"
                  placeholder="e.g., recruiter@company.com"
                  value={newJob.recruiterEmail}
                  onChange={(e) => setNewJob({ ...newJob, recruiterEmail: e.target.value })}
                />
              </div>
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowAddForm(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddJob}>
                Add to Tracker
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analytics View */}
      {showAnalytics && rejectedJobs.length > 0 && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Rejection Analytics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Rejection by Stage */}
              <div>
                <h4 className="font-semibold mb-3">Rejections by Stage</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <Card className="p-4 text-center">
                    <p className="text-2xl font-bold text-red-600">{rejectionStats.byStage.application}</p>
                    <p className="text-xs text-muted-foreground mt-1">After Application</p>
                  </Card>
                  <Card className="p-4 text-center">
                    <p className="text-2xl font-bold text-blue-600">{rejectionStats.byStage.recruiter}</p>
                    <p className="text-xs text-muted-foreground mt-1">Recruiter Stage</p>
                  </Card>
                  <Card className="p-4 text-center">
                    <p className="text-2xl font-bold text-purple-600">{rejectionStats.byStage.technical}</p>
                    <p className="text-xs text-muted-foreground mt-1">Technical Stage</p>
                  </Card>
                  <Card className="p-4 text-center">
                    <p className="text-2xl font-bold text-emerald-600">{rejectionStats.byStage.final}</p>
                    <p className="text-xs text-muted-foreground mt-1">Final Stage</p>
                  </Card>
                </div>
              </div>

              {/* Top Rejection Reasons */}
              {rejectionStats.byReason.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3">Top Rejection Reasons</h4>
                  <div className="space-y-2">
                    {rejectionStats.byReason.map(reason => {
                      const percentage = Math.round((reason.count / rejectionStats.total) * 100);
                      return (
                        <div key={reason.id} className="space-y-1">
                          <div className="flex items-center justify-between text-sm">
                            <span>{reason.label}</span>
                            <span className="font-semibold">{reason.count} ({percentage}%)</span>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <div
                              className="bg-primary rounded-full h-2 transition-all"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Insights */}
              <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h4 className="font-semibold mb-2 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Insights
                </h4>
                <div className="text-sm space-y-1 text-muted-foreground">
                  {rejectionStats.byReason.length > 0 && (
                    <p>• Your top rejection reason is <strong>{rejectionStats.byReason[0].label}</strong> ({rejectionStats.byReason[0].count} times)</p>
                  )}
                  {rejectionStats.total > 0 && (
                    <p>• {Math.round((rejectionStats.total / archivedJobs.length) * 100)}% of your archived applications were rejections</p>
                  )}
                  {rejectionStats.byStage.recruiter > rejectionStats.total / 2 && (
                    <p>• Most rejections happen at recruiter stage - consider improving your resume or initial pitch</p>
                  )}
                  {rejectionStats.byStage.technical > rejectionStats.total / 2 && (
                    <p>• Most rejections happen at technical stage - focus on technical interview prep</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Archive View */}
      {showArchive && archivedJobs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Archive className="h-5 w-5" />
              Archived Applications
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {archivedJobs.map(job => {
                const outcome = ARCHIVE_OUTCOMES.find(o => o.id === job.archiveOutcome);
                const Icon = outcome?.icon || AlertCircle;
                return (
                  <Card key={job.id} className="border-l-4" style={{ borderLeftColor: outcome?.color === 'text-green-600' ? '#16a34a' : outcome?.color === 'text-red-600' ? '#dc2626' : '#9ca3af' }}>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center gap-3">
                            <Icon className={`h-5 w-5 ${outcome?.color}`} />
                            <div>
                              <h5 className="font-bold">{job.company}</h5>
                              <p className="text-sm text-muted-foreground">{job.position}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
                            <span>Applied: {new Date(job.applicationDate).toLocaleDateString()}</span>
                            <span>•</span>
                            <span>Archived: {job.archiveDate ? formatDate(job.archiveDate) : 'Unknown'}</span>
                            <span>•</span>
                            <span>Total: {getTotalDays(job)} days</span>
                          </div>
                          {job.archiveOutcome === 'rejected' && job.rejectionStage && (
                            <div className="flex items-center gap-2 text-xs">
                              <Badge variant="outline" className="bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300">
                                Rejected at {job.rejectionStage.charAt(0).toUpperCase() + job.rejectionStage.slice(1)} stage
                              </Badge>
                            </div>
                          )}
                          {job.rejectionReasons && job.rejectionReasons.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {job.rejectionReasons.map(reasonId => {
                                const reason = REJECTION_REASONS.find(r => r.id === reasonId);
                                return reason ? (
                                  <Badge key={reasonId} variant="secondary" className="text-xs">
                                    {reason.label}
                                  </Badge>
                                ) : null;
                              })}
                            </div>
                          )}
                          {job.rejectionDetails && (
                            <p className="text-sm bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 p-2 rounded">
                              <strong>Details:</strong> {job.rejectionDetails}
                            </p>
                          )}
                          {job.archiveNotes && (
                            <p className="text-sm bg-muted p-2 rounded">{job.archiveNotes}</p>
                          )}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setEditingJob(job)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleUnarchiveJob(job.id)}
                          >
                            Restore
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-destructive hover:text-destructive hover:bg-destructive/10"
                            onClick={() => handleDeleteJob(job.id)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Kanban Board */}
      {!showArchive && !showAnalytics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {STAGES.map(stage => {
            const jobs = getJobsByStage(stage.id);
            return (
              <div key={stage.id} className="space-y-3">
                {/* Column Header */}
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${stage.color}`} />
                  <h4 className="font-semibold text-sm uppercase tracking-wide">
                    {stage.label}
                  </h4>
                  <Badge variant="secondary" className="ml-auto">
                    {jobs.length}
                  </Badge>
                </div>

                {/* Column Content */}
                <div
                  className={`space-y-3 min-h-[200px] p-4 rounded-lg transition-colors ${
                    draggedJob && draggedJob.stage !== stage.id ? 'bg-muted/50 border-2 border-dashed border-primary' : 'bg-muted/20'
                  }`}
                  style={{
                    backgroundImage: 'radial-gradient(circle, rgba(100, 100, 100, 0.15) 1px, transparent 1px)',
                    backgroundSize: '16px 16px',
                  }}
                  onDragOver={handleDragOver}
                  onDrop={() => handleDrop(stage.id)}
                >
                  {jobs.length === 0 ? (
                    <div className="border-2 border-dashed rounded-lg p-8 text-center">
                      <p className="text-sm text-muted-foreground">
                        {draggedJob && draggedJob.stage !== stage.id ? 'Drop here' : 'No applications yet'}
                      </p>
                    </div>
                  ) : (
                    jobs.map(job => {
                      const daysInStage = getDaysInStage(job);
                      const totalDays = getTotalDays(job);
                      const isStale = daysInStage !== null && daysInStage > 14;

                      return (
                        <Card
                          key={job.id}
                          className={`group hover:shadow-md transition-all cursor-grab active:cursor-grabbing ${
                            isStale ? 'border-orange-500/50' : ''
                          } ${draggedJob?.id === job.id ? 'opacity-50 scale-95' : ''}`}
                          draggable
                          onDragStart={() => handleDragStart(job)}
                          onDragEnd={() => setDraggedJob(null)}
                        >
                          <CardContent className="p-4 space-y-3">
                            {/* Header */}
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                  <GripVertical className="h-4 w-4 text-muted-foreground/50 flex-shrink-0" />
                                  <Building2 className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                                  <h5 className="font-bold text-sm truncate">{job.company}</h5>
                                </div>
                                <p className="text-sm text-muted-foreground line-clamp-2">
                                  {job.position}
                                </p>
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 p-0"
                                onClick={() => setEditingJob(job)}
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                            </div>

                            {/* Info */}
                            <div className="space-y-1.5 text-xs text-muted-foreground">
                              {job.location && (
                                <div className="flex items-center gap-2">
                                  <MapPin className="h-3 w-3" />
                                  {job.location}
                                </div>
                              )}
                              <div className="flex items-center gap-2">
                                <Calendar className="h-3 w-3" />
                                Applied {formatDate(job.applicationDate)}
                              </div>
                              {daysInStage !== null && (
                                <div className="flex items-center gap-2">
                                  <Clock className={`h-3 w-3 ${isStale ? 'text-orange-500' : ''}`} />
                                  <span className={isStale ? 'text-orange-500 font-medium' : ''}>
                                    {daysInStage} day{daysInStage !== 1 ? 's' : ''} in stage
                                    {isStale && ' ⚠️'}
                                  </span>
                                </div>
                              )}
                              {job.salaryRange && (
                                <div className="flex items-center gap-2">
                                  <DollarSign className="h-3 w-3" />
                                  {job.salaryRange}
                                </div>
                              )}
                            </div>

                            {/* Stage Notes Preview */}
                            {job.stageNotes?.[stage.id] && (
                              <div className="bg-muted p-2 rounded text-xs">
                                <StickyNote className="h-3 w-3 inline mr-1" />
                                {job.stageNotes[stage.id]!.length > 50
                                  ? job.stageNotes[stage.id]!.substring(0, 50) + '...'
                                  : job.stageNotes[stage.id]
                                }
                              </div>
                            )}

                            {/* Move & Archive Buttons */}
                            <div className="space-y-1 pt-2 border-t">
                              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                {STAGES.filter(s => s.id !== stage.id).map(targetStage => (
                                  <Button
                                    key={targetStage.id}
                                    variant="outline"
                                    size="sm"
                                    className="flex-1 text-xs h-7"
                                    onClick={() => handleMoveJob(job.id, targetStage.id)}
                                  >
                                    → {targetStage.label.split(' ')[0]}
                                  </Button>
                                ))}
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="w-full text-xs h-6 text-muted-foreground hover:text-foreground"
                                onClick={() => setArchivingJob(job)}
                              >
                                <Archive className="h-3 w-3 mr-1" />
                                Archive
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {activeJobs.length === 0 && !showAddForm && !showArchive && !showAnalytics && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <div className="w-16 h-16 rounded-full bg-blue-500/10 flex items-center justify-center mb-4">
              <GripVertical className="h-8 w-8 text-blue-500" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No applications tracked yet</h3>
            <p className="text-sm text-muted-foreground mb-6 text-center max-w-md">
              Start tracking your interview progress by adding applications manually.
              Track dates, notes, and see how long companies take to respond!
            </p>
            <Button
              onClick={() => setShowAddForm(true)}
              className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Your First Application
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Archive Dialog */}
      {archivingJob && (
        <Dialog open={!!archivingJob} onOpenChange={() => setArchivingJob(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Archive Application - {archivingJob.company}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Outcome *</label>
                <div className="grid grid-cols-2 gap-2">
                  {ARCHIVE_OUTCOMES.map(outcome => {
                    const Icon = outcome.icon;
                    return (
                      <Button
                        key={outcome.id}
                        variant="outline"
                        className={`h-auto p-4 justify-start ${outcome.color}`}
                        onClick={() => {
                          if (outcome.id !== 'rejected') {
                            const notes = prompt('Add notes (optional):');
                            handleArchiveJob(archivingJob.id, outcome.id, undefined, undefined, undefined, notes || undefined);
                          }
                        }}
                      >
                        <Icon className={`mr-2 h-5 w-5 ${outcome.color}`} />
                        <span>{outcome.label}</span>
                      </Button>
                    );
                  })}
                </div>
              </div>

              {/* Rejection-specific fields */}
              <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-4 space-y-4">
                <h4 className="font-semibold text-sm">If Rejected, please provide details:</h4>

                <div className="space-y-2">
                  <label className="text-sm font-medium">At which stage were you rejected?</label>
                  <div className="grid grid-cols-2 gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const selectedReasons: string[] = [];
                        const checkboxHTML = REJECTION_REASONS.map((r, i) =>
                          `<div><input type="checkbox" id="reason${i}" value="${r.id}"><label for="reason${i}">${r.label}</label></div>`
                        ).join('');

                        // Simple approach: show dialog with text areas
                        const stage = prompt('Rejection Stage:\n1 - Application (no response after applying)\n2 - Recruiter Stage\n3 - Technical Stage\n4 - Final Stage', '2');
                        if (!stage) return;

                        const stageMap: any = { '1': 'application', '2': 'recruiter', '3': 'technical', '4': 'final' };
                        const rejectionStage = stageMap[stage] || 'recruiter';

                        const reasonInput = prompt(
                          'Select rejection reasons (comma-separated numbers):\n' +
                          '1 - Visa/Work Authorization\n' +
                          '2 - Experience Level\n' +
                          '3 - Technical Skills Gap\n' +
                          '4 - Salary Expectations\n' +
                          '5 - Location/Remote\n' +
                          '6 - Timeline/Availability\n' +
                          '7 - Company Budget\n' +
                          '8 - Cultural Fit\n' +
                          '9 - Overqualified\n' +
                          '10 - Other',
                          '1'
                        );

                        if (!reasonInput) return;

                        const reasonMap: any = {
                          '1': 'visa', '2': 'experience', '3': 'skills', '4': 'salary',
                          '5': 'location', '6': 'timeline', '7': 'budget', '8': 'culture',
                          '9': 'overqualified', '10': 'other'
                        };

                        const reasons = reasonInput.split(',').map(n => reasonMap[n.trim()]).filter(Boolean);

                        const details = prompt('Add specific details about the rejection (optional):');
                        const notes = prompt('Any additional notes (optional):');

                        handleArchiveJob(
                          archivingJob.id,
                          'rejected',
                          rejectionStage,
                          reasons.length > 0 ? reasons : undefined,
                          details || undefined,
                          notes || undefined
                        );
                      }}
                    >
                      After Application
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const reasonInput = prompt(
                          'Select rejection reasons (comma-separated numbers):\n' +
                          '1 - Visa/Work Authorization\n' +
                          '2 - Experience Level\n' +
                          '3 - Technical Skills Gap\n' +
                          '4 - Salary Expectations\n' +
                          '5 - Location/Remote\n' +
                          '6 - Timeline/Availability\n' +
                          '7 - Company Budget\n' +
                          '8 - Cultural Fit\n' +
                          '9 - Overqualified\n' +
                          '10 - Other',
                          '1'
                        );

                        if (reasonInput === null) return;

                        const reasonMap: any = {
                          '1': 'visa', '2': 'experience', '3': 'skills', '4': 'salary',
                          '5': 'location', '6': 'timeline', '7': 'budget', '8': 'culture',
                          '9': 'overqualified', '10': 'other'
                        };

                        const reasons = reasonInput.split(',').map(n => reasonMap[n.trim()]).filter(Boolean);
                        const details = prompt('Add specific details about the rejection:\n(e.g., "Recruiter said they need someone with visa already" or "Failed technical round - struggled with system design")');
                        const notes = prompt('Any additional notes (optional):');

                        handleArchiveJob(
                          archivingJob.id,
                          'rejected',
                          archivingJob.stage,
                          reasons.length > 0 ? reasons : undefined,
                          details || undefined,
                          notes || undefined
                        );
                      }}
                    >
                      At {archivingJob.stage.charAt(0).toUpperCase() + archivingJob.stage.slice(1)} Stage
                    </Button>
                  </div>
                </div>

                <p className="text-xs text-muted-foreground">
                  Track rejection reasons to identify patterns and improve your job search strategy.
                </p>
              </div>

              <div className="flex gap-2 justify-end pt-4 border-t">
                <Button variant="outline" onClick={() => setArchivingJob(null)}>
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Edit Dialog */}
      {editingJob && (
        <Dialog open={!!editingJob} onOpenChange={() => setEditingJob(null)}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Edit Application - {editingJob.company}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Company</label>
                  <Input
                    value={editingJob.company}
                    onChange={(e) => setEditingJob({ ...editingJob, company: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Position</label>
                  <Input
                    value={editingJob.position}
                    onChange={(e) => setEditingJob({ ...editingJob, position: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Location</label>
                  <Input
                    value={editingJob.location}
                    onChange={(e) => setEditingJob({ ...editingJob, location: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Salary Range</label>
                  <Input
                    value={editingJob.salaryRange || ''}
                    onChange={(e) => setEditingJob({ ...editingJob, salaryRange: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Application Date</label>
                  <Input
                    type="date"
                    value={editingJob.applicationDate}
                    onChange={(e) => setEditingJob({ ...editingJob, applicationDate: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Expected Response</label>
                  <Input
                    type="date"
                    value={editingJob.expectedResponseDate || ''}
                    onChange={(e) => setEditingJob({ ...editingJob, expectedResponseDate: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Recruiter Name</label>
                  <Input
                    value={editingJob.recruiterContact || ''}
                    onChange={(e) => setEditingJob({ ...editingJob, recruiterContact: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Recruiter Email</label>
                  <Input
                    value={editingJob.recruiterEmail || ''}
                    onChange={(e) => setEditingJob({ ...editingJob, recruiterEmail: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Recruiter Call Date</label>
                <Input
                  type="date"
                  value={editingJob.recruiterDate || ''}
                  onChange={(e) => setEditingJob({ ...editingJob, recruiterDate: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Recruiter Call Notes</label>
                <textarea
                  className="w-full min-h-[80px] px-3 py-2 rounded-md border border-input bg-background"
                  placeholder="What was discussed? Salary mentioned? Next steps?"
                  value={editingJob.stageNotes?.recruiter || ''}
                  onChange={(e) => setEditingJob({
                    ...editingJob,
                    stageNotes: { ...editingJob.stageNotes, recruiter: e.target.value }
                  })}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Technical Interview Date</label>
                <Input
                  type="date"
                  value={editingJob.technicalDate || ''}
                  onChange={(e) => setEditingJob({ ...editingJob, technicalDate: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Technical Interview Notes</label>
                <textarea
                  className="w-full min-h-[80px] px-3 py-2 rounded-md border border-input bg-background"
                  placeholder="Questions asked? Topics covered? Interviewer names?"
                  value={editingJob.stageNotes?.technical || ''}
                  onChange={(e) => setEditingJob({
                    ...editingJob,
                    stageNotes: { ...editingJob.stageNotes, technical: e.target.value }
                  })}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Final Round Date</label>
                <Input
                  type="date"
                  value={editingJob.finalDate || ''}
                  onChange={(e) => setEditingJob({ ...editingJob, finalDate: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Final Round Notes</label>
                <textarea
                  className="w-full min-h-[80px] px-3 py-2 rounded-md border border-input bg-background"
                  placeholder="Final interview details? Offer details? Decision timeline?"
                  value={editingJob.stageNotes?.final || ''}
                  onChange={(e) => setEditingJob({
                    ...editingJob,
                    stageNotes: { ...editingJob.stageNotes, final: e.target.value }
                  })}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">General Notes</label>
                <textarea
                  className="w-full min-h-[80px] px-3 py-2 rounded-md border border-input bg-background"
                  placeholder="Any other important notes about this application?"
                  value={editingJob.notes || ''}
                  onChange={(e) => setEditingJob({ ...editingJob, notes: e.target.value })}
                />
              </div>

              {/* Archive/Rejection Fields */}
              {editingJob.archived && (
                <div className="border-t pt-4 space-y-4">
                  <h4 className="font-semibold">Archive Information</h4>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Archive Outcome</label>
                    <select
                      className="w-full h-10 px-3 rounded-md border border-input bg-background"
                      value={editingJob.archiveOutcome || 'rejected'}
                      onChange={(e) => setEditingJob({ ...editingJob, archiveOutcome: e.target.value as any })}
                    >
                      {ARCHIVE_OUTCOMES.map(outcome => (
                        <option key={outcome.id} value={outcome.id}>{outcome.label}</option>
                      ))}
                    </select>
                  </div>

                  {editingJob.archiveOutcome === 'rejected' && (
                    <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-4 space-y-4">
                      <h5 className="font-semibold text-sm">Rejection Details</h5>

                      <div className="space-y-2">
                        <label className="text-sm font-medium">Rejection Stage</label>
                        <select
                          className="w-full h-10 px-3 rounded-md border border-input bg-background"
                          value={editingJob.rejectionStage || 'recruiter'}
                          onChange={(e) => setEditingJob({ ...editingJob, rejectionStage: e.target.value as any })}
                        >
                          <option value="application">After Application</option>
                          <option value="recruiter">Recruiter Stage</option>
                          <option value="technical">Technical Stage</option>
                          <option value="final">Final Stage</option>
                        </select>
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-medium">Rejection Reasons</label>
                        <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto p-2 border rounded bg-background">
                          {REJECTION_REASONS.map(reason => {
                            const isSelected = editingJob.rejectionReasons?.includes(reason.id) || false;
                            return (
                              <label key={reason.id} className="flex items-start gap-2 cursor-pointer hover:bg-muted p-2 rounded">
                                <input
                                  type="checkbox"
                                  className="mt-1"
                                  checked={isSelected}
                                  onChange={(e) => {
                                    const currentReasons = editingJob.rejectionReasons || [];
                                    const newReasons = e.target.checked
                                      ? [...currentReasons, reason.id]
                                      : currentReasons.filter(r => r !== reason.id);
                                    setEditingJob({ ...editingJob, rejectionReasons: newReasons });
                                  }}
                                />
                                <div className="flex-1">
                                  <div className="text-sm font-medium">{reason.label}</div>
                                  <div className="text-xs text-muted-foreground">{reason.description}</div>
                                </div>
                              </label>
                            );
                          })}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-medium">Rejection Details</label>
                        <textarea
                          className="w-full min-h-[80px] px-3 py-2 rounded-md border border-input bg-background"
                          placeholder="What specifically did they say? e.g., 'Need visa sponsorship' or 'Failed system design question'"
                          value={editingJob.rejectionDetails || ''}
                          onChange={(e) => setEditingJob({ ...editingJob, rejectionDetails: e.target.value })}
                        />
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Archive Notes</label>
                    <textarea
                      className="w-full min-h-[60px] px-3 py-2 rounded-md border border-input bg-background"
                      placeholder="Additional notes about archiving this application"
                      value={editingJob.archiveNotes || ''}
                      onChange={(e) => setEditingJob({ ...editingJob, archiveNotes: e.target.value })}
                    />
                  </div>
                </div>
              )}

              <div className="flex gap-2 justify-end pt-4 border-t">
                <Button variant="outline" onClick={() => setEditingJob(null)}>
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => {
                    handleDeleteJob(editingJob.id);
                    setEditingJob(null);
                  }}
                >
                  <X className="mr-2 h-4 w-4" />
                  Delete
                </Button>
                <Button onClick={() => handleUpdateJob(editingJob)}>
                  Save Changes
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};
