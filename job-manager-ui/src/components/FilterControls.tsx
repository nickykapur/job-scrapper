import React from 'react';
import {
  Paper,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Typography,
  Stack,
  Divider,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import type { FilterState } from '../types';

interface FilterControlsProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  onRefresh: () => void;
  onRemoveApplied: () => void;
  isRefreshing?: boolean;
}

export const FilterControls: React.FC<FilterControlsProps> = ({
  filters,
  onFiltersChange,
  onRefresh,
  onRemoveApplied,
  isRefreshing = false,
}) => {
  return (
    <Paper
      sx={{
        p: 3,
        mb: 3,
        borderRadius: 3,
        background: (theme) => theme.palette.mode === 'dark'
          ? 'linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%)'
          : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
        <FilterIcon color="primary" />
        Job Management
      </Typography>

      <Stack spacing={3}>
        {/* Filter Controls */}
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Filter by Status</InputLabel>
            <Select
              value={filters.status}
              label="Filter by Status"
              onChange={(e) => onFiltersChange({ ...filters, status: e.target.value as any })}
            >
              <MenuItem value="all">All Jobs</MenuItem>
              <MenuItem value="new">New Only</MenuItem>
              <MenuItem value="applied">Applied</MenuItem>
              <MenuItem value="not-applied">Not Applied</MenuItem>
              <MenuItem value="rejected">Rejected</MenuItem>
            </Select>
          </FormControl>

          <TextField
            size="small"
            label="Filter by keyword..."
            placeholder="e.g. React, Python, Senior"
            value={filters.search}
            onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
            sx={{ minWidth: 250, flexGrow: 1, maxWidth: 400 }}
          />

          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Sort by</InputLabel>
            <Select
              value={filters.sort}
              label="Sort by"
              onChange={(e) => onFiltersChange({ ...filters, sort: e.target.value as any })}
            >
              <MenuItem value="newest">Newest First</MenuItem>
              <MenuItem value="oldest">Oldest First</MenuItem>
              <MenuItem value="company">Company A-Z</MenuItem>
            </Select>
          </FormControl>
        </Stack>

        <Divider />

        {/* Action Buttons */}
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems="center" flexWrap="wrap">
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={onRefresh}
            disabled={isRefreshing}
            sx={{ minWidth: 140 }}
          >
            {isRefreshing ? 'Refreshing...' : 'Refresh Jobs'}
          </Button>

          <Button
            variant="outlined"
            startIcon={<DeleteIcon />}
            onClick={onRemoveApplied}
            color="error"
            sx={{ minWidth: 160 }}
          >
            Remove Applied
          </Button>
        </Stack>
      </Stack>
    </Paper>
  );
};