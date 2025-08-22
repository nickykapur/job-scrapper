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
import { Job } from '../types';
import { JobCard } from './JobCard';

interface JobSectionsProps {
  jobs: Record<string, Job>;
  onToggleApplied: (jobId: string) => void;
  updatingJobs: Set<string>;
}

export const JobSections: React.FC<JobSectionsProps> = ({
  jobs,
  onToggleApplied,
  updatingJobs,
}) => {
  // Categorize jobs
  const newJobs = Object.values(jobs).filter(job => job.category === 'new');
  const last24hJobs = Object.values(jobs).filter(job => job.category === 'last_24h');
  const otherJobs = Object.values(jobs).filter(job => !job.category || job.category === 'existing');
  const dublinJobs = Object.values(jobs).filter(job => 
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
                onToggleApplied={onToggleApplied}
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
                onToggleApplied={onToggleApplied}
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
                onToggleApplied={onToggleApplied}
                isUpdating={updatingJobs.has(job.id)}
              />
            ))}
          </AccordionDetails>
        </Accordion>
      )}

      {/* Empty State */}
      {newJobs.length === 0 && last24hJobs.length === 0 && otherJobs.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No jobs found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try running the Dublin job search script to populate your database
          </Typography>
        </Box>
      )}
    </Box>
  );
};