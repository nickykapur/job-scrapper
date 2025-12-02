import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ExternalLink, Check, X, Zap, Building2 } from 'lucide-react';
import type { Job } from '../types';
import { getCountryFromLocation } from '../utils/countryUtils';
import { jobApi } from '../services/api';
import toast from 'react-hot-toast';

interface JobCardProps {
  job: Job;
  onApplyAndOpen: (jobId: string, jobUrl: string) => void;
  onRejectJob: (jobId: string) => void;
  isUpdating?: boolean;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  onApplyAndOpen,
  onRejectJob,
  isUpdating = false,
}) => {
  const [bulkActionLoading, setBulkActionLoading] = useState(false);
  const extractedCountry = job.country || getCountryFromLocation(job.location);

  const handleRejectAllFromCompany = async () => {
    if (!window.confirm(`Reject ALL jobs from ${job.company}? This will mark all current ${job.company} jobs as rejected.`)) {
      return;
    }

    setBulkActionLoading(true);
    try {
      const result = await jobApi.bulkRejectJobs({ company: job.company });
      toast.success(`${result.jobs_rejected} jobs from ${job.company} rejected!`);
      // Reload to refresh the job list
      setTimeout(() => window.location.reload(), 1000);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to bulk reject jobs');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const jobTypeColors: Record<string, { bg: string; text: string }> = {
    software: { bg: 'bg-blue-500/10 dark:bg-blue-500/20', text: 'text-blue-600 dark:text-blue-400' },
    hr: { bg: 'bg-violet-500/10 dark:bg-violet-500/20', text: 'text-violet-600 dark:text-violet-400' },
    cybersecurity: { bg: 'bg-red-500/10 dark:bg-red-500/20', text: 'text-red-600 dark:text-red-400' },
    sales: { bg: 'bg-amber-500/10 dark:bg-amber-500/20', text: 'text-amber-600 dark:text-amber-400' },
    finance: { bg: 'bg-emerald-500/10 dark:bg-emerald-500/20', text: 'text-emerald-600 dark:text-emerald-400' },
  };

  const jobTypeStyle = jobTypeColors[job.job_type || 'software'] || { bg: 'bg-gray-500/10', text: 'text-gray-600' };

  return (
    <Card className="h-full flex flex-col border-border hover:border-gray-400 dark:hover:border-gray-600 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
      <CardContent className="p-6 flex-grow flex flex-col">
        {/* Company Name */}
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
          {job.company}
        </p>

        {/* Job Title */}
        <h3 className="text-base font-bold mb-4 text-foreground line-clamp-2 leading-snug">
          {job.title}
        </h3>

        {/* Job Details */}
        <div className="space-y-2 mb-6 flex-grow">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {job.location}
            </p>
            {extractedCountry && extractedCountry !== 'Unknown' && (
              <p className="text-xs font-semibold text-primary">
                {extractedCountry}
              </p>
            )}
          </div>

          <div className="flex items-center justify-between flex-wrap gap-1">
            <p className="text-sm text-muted-foreground">
              {job.posted_date}
            </p>
            <div className="flex gap-1 items-center">
              {job.job_type && job.job_type !== 'other' && (
                <Badge
                  variant="outline"
                  className={`h-5 text-[10px] font-semibold px-2 ${jobTypeStyle.bg} ${jobTypeStyle.text} border-0`}
                >
                  {job.job_type === 'hr' ? 'HR' : job.job_type.charAt(0).toUpperCase() + job.job_type.slice(1)}
                </Badge>
              )}
              {/* Show Easy Apply badge with verification status */}
              {(job.easy_apply_status === 'confirmed' || job.easy_apply_status === 'probable' || (job.easy_apply && !job.easy_apply_status)) && (
                <Badge
                  variant="outline"
                  className={`h-5 text-[10px] font-semibold px-2 flex items-center gap-0.5 ${
                    job.easy_apply_status === 'confirmed'
                      ? 'bg-gradient-to-r from-emerald-500/20 to-green-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
                      : 'bg-gradient-to-r from-yellow-500/20 to-amber-500/20 text-yellow-700 dark:text-yellow-400 border border-yellow-500/30'
                  }`}
                  title={
                    job.easy_apply_status === 'confirmed'
                      ? 'Verified Quick Apply'
                      : job.easy_apply_status === 'probable'
                      ? 'Likely Quick Apply (unverified)'
                      : 'Quick Apply (legacy data)'
                  }
                >
                  <Zap className={`w-3 h-3 ${job.easy_apply_status === 'confirmed' ? 'fill-emerald-500' : 'fill-yellow-500'}`} />
                  {job.easy_apply_status === 'confirmed' ? 'Quick Apply ✓' : 'Quick Apply ?'}
                </Badge>
              )}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div>
          {!job.applied && !job.rejected && (
            <div className="space-y-3">
              <Button
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold shadow-none hover:shadow-lg hover:shadow-blue-500/30 transition-all"
                size="lg"
                onClick={() => onApplyAndOpen(job.id, job.job_url)}
                disabled={isUpdating}
              >
                {isUpdating ? 'Processing...' : 'Apply Now'}
                <ExternalLink className="ml-2 h-4 w-4" />
              </Button>

              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  className="flex-1 text-muted-foreground hover:text-destructive hover:bg-destructive/10 font-medium"
                  onClick={() => onRejectJob(job.id)}
                  disabled={isUpdating}
                >
                  <X className="mr-2 h-4 w-4" />
                  Not Interested
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-xs text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                  onClick={handleRejectAllFromCompany}
                  disabled={isUpdating || bulkActionLoading}
                  title={`Reject all from ${job.company}`}
                >
                  <Building2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}

          {job.applied && (
            <Button
              className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 text-white font-semibold cursor-not-allowed"
              size="lg"
              disabled
            >
              <Check className="mr-2 h-4 w-4" />
              Applied
            </Button>
          )}

          {job.rejected && (
            <Button
              variant="secondary"
              className="w-full font-semibold cursor-not-allowed opacity-60"
              size="lg"
              disabled
            >
              <X className="mr-2 h-4 w-4" />
              Rejected
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
