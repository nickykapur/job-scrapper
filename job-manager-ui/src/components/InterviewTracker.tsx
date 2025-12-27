import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Plus, X, Building2, MapPin, Calendar, GripVertical } from 'lucide-react';
import toast from 'react-hot-toast';

interface TrackedJob {
  id: string;
  company: string;
  position: string;
  location: string;
  stage: 'recruiter' | 'technical' | 'final';
  addedDate: string;
  notes?: string;
}

const STAGES = [
  { id: 'recruiter', label: 'Recruiter Call', color: 'bg-blue-500' },
  { id: 'technical', label: 'Technical Interview', color: 'bg-purple-500' },
  { id: 'final', label: 'Final/Awaiting Response', color: 'bg-emerald-500' },
] as const;

export const InterviewTracker: React.FC = () => {
  const [trackedJobs, setTrackedJobs] = useState<TrackedJob[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newJob, setNewJob] = useState({
    company: '',
    position: '',
    location: '',
    stage: 'recruiter' as const,
  });

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('interview-tracker');
    if (saved) {
      try {
        setTrackedJobs(JSON.parse(saved));
      } catch (error) {
        console.error('Failed to load tracked jobs:', error);
      }
    }
  }, []);

  // Save to localStorage whenever trackedJobs changes
  useEffect(() => {
    localStorage.setItem('interview-tracker', JSON.stringify(trackedJobs));
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
      addedDate: new Date().toISOString(),
    };

    setTrackedJobs([...trackedJobs, job]);
    setNewJob({ company: '', position: '', location: '', stage: 'recruiter' });
    setShowAddForm(false);
    toast.success('Job added to tracker!');
  };

  const handleDeleteJob = (id: string) => {
    setTrackedJobs(trackedJobs.filter(job => job.id !== id));
    toast.success('Job removed from tracker');
  };

  const handleMoveJob = (id: string, newStage: 'recruiter' | 'technical' | 'final') => {
    setTrackedJobs(trackedJobs.map(job =>
      job.id === id ? { ...job, stage: newStage } : job
    ));
    toast.success('Job moved!');
  };

  const getJobsByStage = (stage: 'recruiter' | 'technical' | 'final') => {
    return trackedJobs.filter(job => job.stage === stage);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const days = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    return `${days} days ago`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold">Interview Tracker</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Track your interview progress • {trackedJobs.length} application{trackedJobs.length !== 1 ? 's' : ''}
          </p>
        </div>
        <Button
          onClick={() => setShowAddForm(!showAddForm)}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Application
        </Button>
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

      {/* Kanban Board */}
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
              <div className="space-y-3 min-h-[200px]">
                {jobs.length === 0 ? (
                  <div className="border-2 border-dashed rounded-lg p-8 text-center">
                    <p className="text-sm text-muted-foreground">No applications yet</p>
                  </div>
                ) : (
                  jobs.map(job => (
                    <Card key={job.id} className="group hover:shadow-md transition-all">
                      <CardContent className="p-4 space-y-3">
                        {/* Header with delete button */}
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
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
                            className="opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 p-0 text-destructive hover:text-destructive hover:bg-destructive/10"
                            onClick={() => handleDeleteJob(job.id)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>

                        {/* Location */}
                        {job.location && (
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <MapPin className="h-3 w-3" />
                            {job.location}
                          </div>
                        )}

                        {/* Date Added */}
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Calendar className="h-3 w-3" />
                          Added {formatDate(job.addedDate)}
                        </div>

                        {/* Move Buttons */}
                        <div className="flex gap-1 pt-2 border-t">
                          {STAGES.filter(s => s.id !== stage.id).map(targetStage => (
                            <Button
                              key={targetStage.id}
                              variant="outline"
                              size="sm"
                              className="flex-1 text-xs h-7"
                              onClick={() => handleMoveJob(job.id, targetStage.id)}
                            >
                              Move to {targetStage.label.split('/')[0]}
                            </Button>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {trackedJobs.length === 0 && !showAddForm && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <div className="w-16 h-16 rounded-full bg-blue-500/10 flex items-center justify-center mb-4">
              <GripVertical className="h-8 w-8 text-blue-500" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No applications tracked yet</h3>
            <p className="text-sm text-muted-foreground mb-6 text-center max-w-md">
              Start tracking your interview progress by adding applications manually.
              Move them through stages as you progress!
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
    </div>
  );
};
