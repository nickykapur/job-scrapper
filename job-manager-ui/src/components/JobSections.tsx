import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  FiberNew as NewIcon,
  Schedule as ClockIcon,
  Storage as AllIcon,
  LocationOn as LocationIcon,
} from '@mui/icons-material';
import type { Job } from '../types';
import { JobCard } from './JobCard';

interface JobSectionsProps {
  jobs: Record<string, Job>;
  onApplyAndOpen: (jobId: string, jobUrl: string) => void;
  updatingJobs: Set<string>;
}

export const JobSections: React.FC<JobSectionsProps> = ({
  jobs,
  onApplyAndOpen,
  updatingJobs,
}) => {
  // Function to check if job was posted within last 24 hours
  const isWithin24Hours = (postedDate: string): boolean => {
    if (!postedDate) return false;
    
    const normalizedDate = postedDate.toLowerCase().trim();
    
    // Handle "X hours ago" - these are definitely within 24 hours
    if (normalizedDate.includes('hour') && normalizedDate.includes('ago')) {
      return true;
    }
    
    // Handle "1 day ago" - this is exactly 24 hours
    if (normalizedDate === '1 day ago') {
      return true;
    }
    
    // Handle "X days ago" - anything more than 1 day is outside 24 hours
    if (normalizedDate.includes('day') && normalizedDate.includes('ago')) {
      const match = normalizedDate.match(/(\d+)\s+days?\s+ago/);
      if (match) {
        const days = parseInt(match[1]);
        return days <= 1;
      }
    }
    
    // Handle "today" or similar
    if (normalizedDate.includes('today') || normalizedDate.includes('now')) {
      return true;
    }
    
    // Default to false for unparseable dates
    return false;
  };

  // Filter out metadata and categorize jobs, then filter by 24 hours
  const jobEntries = Object.entries(jobs).filter(([key]) => !key.startsWith('_'));
  const allJobValues = jobEntries.map(([, job]) => job);
  
  // Filter to show only jobs posted in last 24 hours
  const jobValues = allJobValues.filter(job => isWithin24Hours(job.posted_date));
  
  const newJobs = jobValues.filter(job => job.category === 'new');
  const last24hJobs = jobValues.filter(job => job.category === 'last_24h');
  const otherJobs = jobValues.filter(job => !job.category || job.category === 'existing');
  const dublinJobs = jobValues.filter(job => 
    job.location?.toLowerCase().includes('dublin')
  );

  return (
    <Box>
      {/* Dublin Jobs Summary */}
      {dublinJobs.length > 0 && (
        <Box sx={{ mb: 3, p: 2, backgroundColor: 'background.paper', borderRadius: 2, border: '1px solid', borderColor: 'primary.main' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <LocationIcon color="primary" />
            <Typography variant="h6" color="primary">
              Dublin Jobs Summary
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              label={`${dublinJobs.length} Total Dublin Jobs`}
              color="primary"
              variant="outlined"
            />
            <Chip
              label={`${dublinJobs.filter(j => j.category === 'new').length} New`}
              color="success"
              variant="outlined"
            />
            <Chip
              label={`${dublinJobs.filter(j => j.category === 'last_24h').length} Last 24h`}
              color="info"
              variant="outlined"
            />
            <Chip
              label={`${dublinJobs.filter(j => j.applied).length} Applied`}
              color="secondary"
              variant="outlined"
            />
          </Box>
        </Box>
      )}

      {/* New Jobs Section */}
      {newJobs.length > 0 && (
        <Accordion defaultExpanded sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              <Badge badgeContent={newJobs.length} color="success">
                <NewIcon color="success" />
              </Badge>
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                🆕 New Jobs
              </Typography>
              <Chip
                label={`${newJobs.length} jobs`}
                color="success"
                size="small"
                variant="outlined"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Jobs that weren't in your database before the last search
            </Typography>
            {newJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onApplyAndOpen={onApplyAndOpen}
                isUpdating={updatingJobs.has(job.id)}
              />
            ))}
          </AccordionDetails>
        </Accordion>
      )}

      {/* Last 24 Hours Jobs Section */}
      {last24hJobs.length > 0 && (
        <Accordion defaultExpanded sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              <Badge badgeContent={last24hJobs.length} color="info">
                <ClockIcon color="info" />
              </Badge>
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                🕐 Last 24 Hours Jobs
              </Typography>
              <Chip
                label={`${last24hJobs.length} jobs`}
                color="info"
                size="small"
                variant="outlined"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Jobs that were already in your database but appeared in the last 24 hours search
            </Typography>
            {last24hJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onApplyAndOpen={onApplyAndOpen}
                isUpdating={updatingJobs.has(job.id)}
              />
            ))}
          </AccordionDetails>
        </Accordion>
      )}

      {/* All Other Jobs Section */}
      {otherJobs.length > 0 && (
        <Accordion sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              <Badge badgeContent={otherJobs.length} color="default">
                <AllIcon />
              </Badge>
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                📋 All Other Jobs
              </Typography>
              <Chip
                label={`${otherJobs.length} jobs`}
                color="default"
                size="small"
                variant="outlined"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Previously saved jobs from your database
            </Typography>
            {otherJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onApplyAndOpen={onApplyAndOpen}
                isUpdating={updatingJobs.has(job.id)}
              />
            ))}
          </AccordionDetails>
        </Accordion>
      )}

      {/* Fallback: Show All Jobs if No Categories */}
      {newJobs.length === 0 && last24hJobs.length === 0 && otherJobs.length === 0 && jobValues.length > 0 && (
        <Accordion defaultExpanded sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              <Badge badgeContent={jobValues.length} color="primary">
                <AllIcon color="primary" />
              </Badge>
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                📋 Jobs (Last 24 Hours)
              </Typography>
              <Chip
                label={`${jobValues.length} jobs`}
                color="primary"
                size="small"
                variant="outlined"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Jobs posted in the last 24 hours from your database
              {allJobValues.length > jobValues.length && ` (${allJobValues.length - jobValues.length} older jobs hidden)`}
            </Typography>
            {jobValues.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onApplyAndOpen={onApplyAndOpen}
                isUpdating={updatingJobs.has(job.id)}
              />
            ))}
          </AccordionDetails>
        </Accordion>
      )}

      {/* Empty State */}
      {jobValues.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No jobs found from the last 24 hours
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {allJobValues.length > 0 
              ? `${allJobValues.length} total jobs in database, but none posted within 24 hours`
              : 'Try running the Dublin job search script to populate your database'
            }
          </Typography>
        </Box>
      )}
    </Box>
  );
};