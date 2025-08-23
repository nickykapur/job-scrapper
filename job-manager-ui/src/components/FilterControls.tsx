import React, { useState } from 'react';
import {
  Paper,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Stack,
  Divider,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Delete as DeleteIcon,
  Block as BlockIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { FilterState } from '../types';

interface FilterControlsProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  onRefresh: () => void;
  onExport: () => void;
  onMarkAllRead: () => void;
  onRemoveApplied: () => void;
  onAddExcludedCompany: (company: string) => void;
  excludedCompanies: string[];
  onRemoveExcludedCompany: (company: string) => void;
  isRefreshing?: boolean;
}

export const FilterControls: React.FC<FilterControlsProps> = ({
  filters,
  onFiltersChange,
  onRefresh,
  onExport,
  onMarkAllRead,
  onRemoveApplied,
  onAddExcludedCompany,
  excludedCompanies,
  onRemoveExcludedCompany,
  isRefreshing = false,
}) => {
  const [excludeCompanyDialog, setExcludeCompanyDialog] = useState(false);
  const [newExcludedCompany, setNewExcludedCompany] = useState('');

  const handleAddExcludedCompany = () => {
    if (newExcludedCompany.trim()) {
      onAddExcludedCompany(newExcludedCompany.trim());
      setNewExcludedCompany('');
      setExcludeCompanyDialog(false);
    }
  };

  return (
    <>
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
                <MenuItem value="all">📋 All Jobs</MenuItem>
                <MenuItem value="new">✨ New Only</MenuItem>
                <MenuItem value="applied">✅ Applied</MenuItem>
                <MenuItem value="not-applied">📝 Not Applied</MenuItem>
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
                <MenuItem value="newest">🕐 Newest First</MenuItem>
                <MenuItem value="oldest">📅 Oldest First</MenuItem>
                <MenuItem value="company">🏢 Company A-Z</MenuItem>
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
              startIcon={<DownloadIcon />}
              onClick={onExport}
              sx={{ minWidth: 120 }}
            >
              Export Data
            </Button>

            <Button
              variant="outlined"
              startIcon={<VisibilityIcon />}
              onClick={onMarkAllRead}
              sx={{ minWidth: 140 }}
            >
              Mark All Read
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

            <Button
              variant="outlined"
              startIcon={<BlockIcon />}
              onClick={() => setExcludeCompanyDialog(true)}
              sx={{ minWidth: 160 }}
            >
              Block Company
            </Button>
          </Stack>

          {/* Blocked Companies */}
          {excludedCompanies.length > 0 && (
            <Box>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1.5, fontWeight: 600 }}>
                🚫 Blocked Companies ({excludedCompanies.length}):
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {excludedCompanies.map((company) => (
                  <Chip
                    key={company}
                    label={company}
                    onDelete={() => onRemoveExcludedCompany(company)}
                    color="error"
                    variant="outlined"
                    size="small"
                    sx={{
                      fontWeight: 500,
                      '& .MuiChip-deleteIcon': {
                        '&:hover': {
                          color: 'error.dark',
                        }
                      }
                    }}
                  />
                ))}
              </Stack>
            </Box>
          )}
        </Stack>
      </Paper>

      {/* Block Company Dialog */}
      <Dialog open={excludeCompanyDialog} onClose={() => setExcludeCompanyDialog(false)}>
        <DialogTitle sx={{ fontWeight: 600 }}>
          🚫 Block Company
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Block a company so their jobs won't appear in your list anymore.
          </Typography>
          <TextField
            autoFocus
            fullWidth
            label="Company Name"
            placeholder="e.g. Bending Spoons"
            value={newExcludedCompany}
            onChange={(e) => setNewExcludedCompany(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddExcludedCompany()}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExcludeCompanyDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleAddExcludedCompany} 
            variant="contained"
            color="error"
            disabled={!newExcludedCompany.trim()}
          >
            Block Company
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};