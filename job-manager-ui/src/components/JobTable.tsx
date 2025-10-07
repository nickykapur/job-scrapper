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
} from '@mui/icons-material';
import type { Job } from '../types';

interface JobTableProps {
  jobs: Record<string, Job>;
  onApplyAndOpen: (jobId: string, jobUrl: string) => void;
  onRejectJob: (jobId: string) => void;
  updatingJobs: Set<string>;
}

type SortField = 'title' | 'company' | 'location' | 'posted_date' | 'country';
type SortDirection = 'asc' | 'desc';

const JobTable: React.FC<JobTableProps> = ({
  jobs,
  onApplyAndOpen,
  onRejectJob,
  updatingJobs,
}) => {
  const [sortField, setSortField] = useState<SortField>('posted_date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [searchTerm, setSearchTerm] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // Convert jobs to array and filter
  const jobsArray = useMemo(() => {
    return Object.values(jobs).filter((job: any) =>
      typeof job === 'object' && job !== null && !job.id?.startsWith('_') && !job.rejected
    );
  }, [jobs]);

  // Get unique countries
  const countries = useMemo(() => {
    const countrySet = new Set<string>();
    jobsArray.forEach((job: any) => {
      if (job.country) countrySet.add(job.country);
    });
    return Array.from(countrySet).sort();
  }, [jobsArray]);

  // Get unique categories
  const categories = useMemo(() => {
    const categorySet = new Set<string>();
    jobsArray.forEach((job: any) => {
      if (job.category) categorySet.add(job.category);
    });
    return Array.from(categorySet).sort();
  }, [jobsArray]);

  // Filter and sort jobs
  const filteredAndSortedJobs = useMemo(() => {
    let filtered = jobsArray.filter((job: any) => {
      const matchesSearch = !searchTerm ||
        job.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesCountry = !countryFilter || job.country === countryFilter;
      const matchesCategory = !categoryFilter || job.category === categoryFilter;

      return matchesSearch && matchesCountry && matchesCategory;
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
  }, [jobsArray, sortField, sortDirection, searchTerm, countryFilter, categoryFilter]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getCountryFlag = (country: string): string => {
    const flags: Record<string, string> = {
      'Ireland': '🇮🇪',
      'Spain': '🇪🇸',
      'Germany': '🇩🇪',
      'United Kingdom': '🇬🇧',
    };
    return flags[country] || '🌍';
  };

  const getCategoryColor = (category: string): string => {
    switch (category) {
      case 'new': return '#4CAF50';
      case 'last_24h': return '#FF9800';
      default: return '#9C27B0';
    }
  };

  const getCategoryLabel = (category: string): string => {
    switch (category) {
      case 'new': return 'New';
      case 'last_24h': return '24h';
      default: return 'Other';
    }
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

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Country</InputLabel>
            <Select
              value={countryFilter}
              onChange={(e) => setCountryFilter(e.target.value)}
              label="Country"
            >
              <MenuItem value="">All Countries</MenuItem>
              {countries.map((country) => (
                <MenuItem key={country} value={country}>
                  {getCountryFlag(country)} {country}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              label="Category"
            >
              <MenuItem value="">All Categories</MenuItem>
              {categories.map((category) => (
                <MenuItem key={category} value={category}>
                  {getCategoryLabel(category)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

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
                  active={sortField === 'country'}
                  direction={sortField === 'country' ? sortDirection : 'asc'}
                  onClick={() => handleSort('country')}
                  sx={{ color: 'white', '&.Mui-active': { color: 'white' } }}
                >
                  Country
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 600 }}>Category</TableCell>
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
            {filteredAndSortedJobs.map((job: any) => (
              <TableRow
                key={job.id}
                sx={{
                  '&:hover': { bgcolor: 'action.hover' },
                  '&:nth-of-type(even)': { bgcolor: 'action.selected' },
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
                  <Chip
                    label={`${getCountryFlag(job.country || 'Unknown')} ${job.country || 'Unknown'}`}
                    size="small"
                    variant="outlined"
                    sx={{ fontWeight: 500 }}
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={getCategoryLabel(job.category || 'other')}
                    size="small"
                    sx={{
                      bgcolor: `${getCategoryColor(job.category || 'other')}20`,
                      color: getCategoryColor(job.category || 'other'),
                      fontWeight: 600,
                    }}
                  />
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
                      <IconButton
                        size="small"
                        onClick={() => onApplyAndOpen(job.id, job.job_url)}
                        disabled={updatingJobs.has(job.id)}
                        sx={{
                          bgcolor: 'success.main',
                          color: 'white',
                          '&:hover': { bgcolor: 'success.dark' },
                        }}
                      >
                        {updatingJobs.has(job.id) ? <TimeIcon /> : <ApplyIcon />}
                      </IconButton>
                    </Tooltip>

                    <Tooltip title="Reject Job">
                      <IconButton
                        size="small"
                        onClick={() => onRejectJob(job.id)}
                        disabled={updatingJobs.has(job.id)}
                        sx={{
                          bgcolor: 'error.main',
                          color: 'white',
                          '&:hover': { bgcolor: 'error.dark' },
                        }}
                      >
                        <RejectIcon />
                      </IconButton>
                    </Tooltip>

                    <Tooltip title="Open Job">
                      <IconButton
                        size="small"
                        onClick={() => window.open(job.job_url, '_blank')}
                        sx={{
                          bgcolor: 'primary.main',
                          color: 'white',
                          '&:hover': { bgcolor: 'primary.dark' },
                        }}
                      >
                        <OpenIcon />
                      </IconButton>
                    </Tooltip>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default JobTable;