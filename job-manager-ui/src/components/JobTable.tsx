import React, { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  IconButton,
  Chip,
  Box,
  Typography,
  TableSortLabel,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  Tooltip,
  TablePagination,
  CircularProgress,
} from '@mui/material';
import {
  OpenInNew as OpenIcon,
  Check as ApplyIcon,
  Close as RejectIcon,
  LocationOn as LocationIcon,
  Business as CompanyIcon,
  Schedule as TimeIcon,
  FilterList as FilterIcon,
  Bolt as EasyApplyIcon,
  CheckCircle as SuccessIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import type { Job } from '../types';

interface JobTableProps {
  jobs: Record<string, Job>;
  onApplyAndOpen: (jobId: string, jobUrl: string) => void;
  onRejectJob: (jobId: string) => void;
  updatingJobs: Set<string>;
}

type SortField = 'title' | 'company' | 'location' | 'posted_date' | 'country';
type SortDirection = 'asc' | 'desc';

// Animation variants for smooth transitions
const rowVariants = {
  hidden: {
    opacity: 0,
    y: 20,
    scale: 0.95
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.3,
      ease: [0.4, 0, 0.2, 1]
    }
  },
  exit: {
    opacity: 0,
    x: -100,
    scale: 0.95,
    transition: {
      duration: 0.2,
      ease: [0.4, 0, 1, 1]
    }
  }
};

const buttonVariants = {
  idle: { scale: 1 },
  hover: { scale: 1.05, transition: { duration: 0.2 } },
  tap: { scale: 0.95, transition: { duration: 0.1 } },
  loading: {
    scale: 1,
    rotate: 360,
    transition: {
      rotate: { repeat: Infinity, duration: 1, ease: "linear" }
    }
  },
  success: {
    scale: [1, 1.2, 1],
    transition: { duration: 0.3 }
  }
};

const JobTable: React.FC<JobTableProps> = ({
  jobs,
  onApplyAndOpen,
  onRejectJob,
  updatingJobs,
}) => {
  const [sortField, setSortField] = useState<SortField>('posted_date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(50);
  const [actionStates, setActionStates] = useState<Record<string, 'idle' | 'applying' | 'rejecting' | 'success'>>({});

  // Convert jobs to array and filter
  const jobsArray = useMemo(() => {
    return Object.values(jobs).filter((job: any) =>
      typeof job === 'object' && job !== null && !job.id?.startsWith('_') && !job.rejected
    );
  }, [jobs]);

  // Filter and sort jobs
  const filteredAndSortedJobs = useMemo(() => {
    let filtered = jobsArray.filter((job: any) => {
      const matchesSearch = !searchTerm ||
        job.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company?.toLowerCase().includes(searchTerm.toLowerCase());

      return matchesSearch;
    });

    // Sort jobs
    filtered.sort((a: any, b: any) => {
      let aValue = a[sortField] || '';
      let bValue = b[sortField] || '';

      if (sortField === 'posted_date') {
        // Handle date sorting
        aValue = new Date(aValue || 0).getTime();
        bValue = new Date(bValue || 0).getTime();
      } else {
        aValue = String(aValue).toLowerCase();
        bValue = String(bValue).toLowerCase();
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [jobsArray, sortField, sortDirection, searchTerm]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Get paginated jobs
  const paginatedJobs = useMemo(() => {
    const startIndex = page * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return filteredAndSortedJobs.slice(startIndex, endIndex);
  }, [filteredAndSortedJobs, page, rowsPerPage]);

  // Enhanced handlers with animation states
  const handleApplyAndOpen = async (jobId: string, jobUrl: string) => {
    setActionStates(prev => ({ ...prev, [jobId]: 'applying' }));
    await onApplyAndOpen(jobId, jobUrl);
    setActionStates(prev => ({ ...prev, [jobId]: 'success' }));
    setTimeout(() => {
      setActionStates(prev => ({ ...prev, [jobId]: 'idle' }));
    }, 1000);
  };

  const handleReject = async (jobId: string) => {
    setActionStates(prev => ({ ...prev, [jobId]: 'rejecting' }));
    await onRejectJob(jobId);
    // Keep rejecting state until component unmounts
  };


  if (jobsArray.length === 0) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No jobs available
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
          <FilterIcon sx={{ color: 'primary.main' }} />
          <TextField
            label="Search jobs or companies"
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ flex: 1, minWidth: 200 }}
          />

          <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
            {filteredAndSortedJobs.length} jobs
          </Typography>
        </Stack>
      </Paper>

      {/* Jobs Table */}
      <TableContainer component={Paper} sx={{ boxShadow: 2 }}>
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: 'primary.main' }}>
              <TableCell sx={{ color: 'white', fontWeight: 600 }}>
                <TableSortLabel
                  active={sortField === 'title'}
                  direction={sortField === 'title' ? sortDirection : 'asc'}
                  onClick={() => handleSort('title')}
                  sx={{ color: 'white', '&.Mui-active': { color: 'white' } }}
                >
                  Job Title
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 600 }}>
                <TableSortLabel
                  active={sortField === 'company'}
                  direction={sortField === 'company' ? sortDirection : 'asc'}
                  onClick={() => handleSort('company')}
                  sx={{ color: 'white', '&.Mui-active': { color: 'white' } }}
                >
                  Company
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 600 }}>
                <TableSortLabel
                  active={sortField === 'posted_date'}
                  direction={sortField === 'posted_date' ? sortDirection : 'asc'}
                  onClick={() => handleSort('posted_date')}
                  sx={{ color: 'white', '&.Mui-active': { color: 'white' } }}
                >
                  Posted
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 600, textAlign: 'center' }}>
                Actions
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <AnimatePresence mode="popLayout">
              {paginatedJobs.map((job: any, index: number) => (
                <TableRow
                  key={job.id}
                  component={motion.tr}
                  variants={rowVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  custom={index}
                  layout
                  sx={{
                    '&:hover': {
                      bgcolor: 'action.hover',
                      transform: 'scale(1.01)',
                      transition: 'all 0.2s ease',
                    },
                    '&:nth-of-type(even)': { bgcolor: 'action.selected' },
                    transition: 'background-color 0.2s ease',
                  }}
                >
                <TableCell>
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="body1" sx={{ fontWeight: 600 }}>
                        {job.title}
                      </Typography>
                      {job.easy_apply && (
                        <Chip
                          icon={<EasyApplyIcon sx={{ fontSize: '0.75rem' }} />}
                          label="Easy Apply"
                          size="small"
                          sx={{
                            height: 20,
                            bgcolor: '#10b98120',
                            color: '#10b981',
                            fontSize: '0.65rem',
                            fontWeight: 600,
                            '& .MuiChip-icon': { color: '#10b981' }
                          }}
                        />
                      )}
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                      <LocationIcon sx={{ fontSize: '0.75rem', mr: 0.5 }} />
                      {job.location}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <CompanyIcon sx={{ fontSize: '1rem', mr: 1, color: 'text.secondary' }} />
                    <Typography variant="body2">{job.company}</Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <TimeIcon sx={{ fontSize: '0.9rem', mr: 0.5, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">
                      {job.posted_date || 'Unknown'}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1} justifyContent="center">
                    <Tooltip title="Apply & Open">
                      <Box
                        component={motion.div}
                        variants={buttonVariants}
                        initial="idle"
                        whileHover="hover"
                        whileTap="tap"
                        animate={
                          actionStates[job.id] === 'applying' ? 'loading' :
                          actionStates[job.id] === 'success' ? 'success' : 'idle'
                        }
                      >
                        <IconButton
                          size="small"
                          onClick={() => handleApplyAndOpen(job.id, job.job_url)}
                          disabled={updatingJobs.has(job.id) || actionStates[job.id] === 'applying'}
                          sx={{
                            bgcolor: actionStates[job.id] === 'success' ? 'success.light' : 'success.main',
                            color: 'white',
                            '&:hover': { bgcolor: 'success.dark' },
                            '&:disabled': {
                              bgcolor: 'success.light',
                              opacity: 0.7,
                            },
                            transition: 'all 0.3s ease',
                          }}
                        >
                          {actionStates[job.id] === 'applying' ? (
                            <CircularProgress size={20} sx={{ color: 'white' }} />
                          ) : actionStates[job.id] === 'success' ? (
                            <SuccessIcon />
                          ) : (
                            <ApplyIcon />
                          )}
                        </IconButton>
                      </Box>
                    </Tooltip>

                    <Tooltip title="Reject Job">
                      <Box
                        component={motion.div}
                        variants={buttonVariants}
                        initial="idle"
                        whileHover="hover"
                        whileTap="tap"
                        animate={actionStates[job.id] === 'rejecting' ? 'exit' : 'idle'}
                      >
                        <IconButton
                          size="small"
                          onClick={() => handleReject(job.id)}
                          disabled={updatingJobs.has(job.id) || actionStates[job.id] === 'rejecting'}
                          sx={{
                            bgcolor: 'error.main',
                            color: 'white',
                            '&:hover': { bgcolor: 'error.dark' },
                            '&:disabled': {
                              bgcolor: 'error.light',
                              opacity: 0.7,
                            },
                            transition: 'all 0.3s ease',
                          }}
                        >
                          {actionStates[job.id] === 'rejecting' ? (
                            <CircularProgress size={20} sx={{ color: 'white' }} />
                          ) : (
                            <RejectIcon />
                          )}
                        </IconButton>
                      </Box>
                    </Tooltip>

                    <Tooltip title="Open Job">
                      <Box
                        component={motion.div}
                        variants={buttonVariants}
                        initial="idle"
                        whileHover="hover"
                        whileTap="tap"
                      >
                        <IconButton
                          size="small"
                          onClick={() => window.open(job.job_url, '_blank')}
                          sx={{
                            bgcolor: 'primary.main',
                            color: 'white',
                            '&:hover': { bgcolor: 'primary.dark' },
                            transition: 'all 0.3s ease',
                          }}
                        >
                          <OpenIcon />
                        </IconButton>
                      </Box>
                    </Tooltip>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
            </AnimatePresence>
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={filteredAndSortedJobs.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          sx={{
            borderTop: 1,
            borderColor: 'divider',
            '& .MuiTablePagination-toolbar': {
              minHeight: 56,
            },
          }}
        />
      </TableContainer>
    </Box>
  );
};

export default JobTable;