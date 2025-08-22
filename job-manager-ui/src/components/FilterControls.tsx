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
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Block as BlockIcon,
} from '@mui/icons-material';
import { FilterState } from '../types';

interface FilterControlsProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  onRefresh: () => void;
  onExport: () => void;
  onMarkAllRead: () => void;
  onRemoveApplied: () => void;
  onSearch: (keywords: string) => void;
  onAddExcludedCompany: (company: string) => void;
  excludedCompanies: string[];
  onRemoveExcludedCompany: (company: string) => void;
  isRefreshing?: boolean;
  isSearching?: boolean;
}

export const FilterControls: React.FC<FilterControlsProps> = ({
  filters,
  onFiltersChange,
  onRefresh,
  onExport,
  onMarkAllRead,
  onRemoveApplied,
  onSearch,
  onAddExcludedCompany,
  excludedCompanies,
  onRemoveExcludedCompany,
  isRefreshing = false,
  isSearching = false,
}) => {
  const [searchDialog, setSearchDialog] = useState(false);
  const [excludeDialog, setExcludeDialog] = useState(false);
  const [searchKeywords, setSearchKeywords] = useState('');
  const [excludeCompany, setExcludeCompany] = useState('');

  const handleSearch = () => {
    if (searchKeywords.trim()) {
      onSearch(searchKeywords.trim());
      setSearchDialog(false);
      setSearchKeywords('');
    }
  };

  const handleExclude = () => {
    if (excludeCompany.trim()) {
      onAddExcludedCompany(excludeCompany.trim());
      setExcludeDialog(false);
      setExcludeCompany('');
    }
  };

  return (
    <>
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box
          display=\"flex\"
          gap={2}
          flexWrap=\"wrap\"
          alignItems=\"center\"
          sx={{ mb: excludedCompanies.length > 0 ? 2 : 0 }}
        >
          <FormControl size=\"small\" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status}
              label=\"Status\"
              onChange={(e) =>
                onFiltersChange({ ...filters, status: e.target.value as any })
              }
            >
              <MenuItem value=\"all\">All Jobs</MenuItem>
              <MenuItem value=\"applied\">Applied</MenuItem>
              <MenuItem value=\"not-applied\">Not Applied</MenuItem>
              <MenuItem value=\"new\">New Jobs</MenuItem>
            </Select>
          </FormControl>

          <FormControl size=\"small\" sx={{ minWidth: 140 }}>
            <InputLabel>Sort by</InputLabel>
            <Select
              value={filters.sort}
              label=\"Sort by\"
              onChange={(e) =>
                onFiltersChange({ ...filters, sort: e.target.value as any })
              }
            >
              <MenuItem value=\"newest\">Newest First</MenuItem>
              <MenuItem value=\"oldest\">Oldest First</MenuItem>
              <MenuItem value=\"title\">Title A-Z</MenuItem>
              <MenuItem value=\"company\">Company A-Z</MenuItem>
            </Select>
          </FormControl>

          <TextField
            size=\"small\"
            placeholder=\"Search jobs...\"
            value={filters.search}
            onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
            sx={{ minWidth: 200 }}
          />

          <Button
            variant=\"outlined\"
            startIcon={<RefreshIcon />}
            onClick={onRefresh}
            disabled={isRefreshing}
          >
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </Button>

          <Button variant=\"outlined\" startIcon={<DownloadIcon />} onClick={onExport}>
            Export
          </Button>

          <Button variant=\"outlined\" startIcon={<VisibilityIcon />} onClick={onMarkAllRead}>
            Mark All Read
          </Button>

          <Button
            variant=\"outlined\"
            color=\"error\"
            startIcon={<DeleteIcon />}
            onClick={onRemoveApplied}
          >
            Remove Applied
          </Button>

          <Button
            variant=\"contained\"
            startIcon={<SearchIcon />}
            onClick={() => setSearchDialog(true)}
            disabled={isSearching}
          >
            {isSearching ? 'Searching...' : 'Search Jobs'}
          </Button>

          <Button
            variant=\"outlined\"
            startIcon={<BlockIcon />}
            onClick={() => setExcludeDialog(true)}
          >
            Exclude Company
          </Button>
        </Box>

        {excludedCompanies.length > 0 && (
          <Box>
            <Typography variant=\"body2\" color=\"text.secondary\" sx={{ mb: 1 }}>
              🚫 Excluded companies:
            </Typography>
            <Box display=\"flex\" gap={1} flexWrap=\"wrap\">
              {excludedCompanies.map((company) => (
                <Chip
                  key={company}
                  label={company}
                  onDelete={() => onRemoveExcludedCompany(company)}
                  color=\"error\"
                  variant=\"outlined\"
                  size=\"small\"
                />
              ))}
            </Box>
          </Box>
        )}
      </Paper>

      {/* Search Dialog */}
      <Dialog open={searchDialog} onClose={() => setSearchDialog(false)}>
        <DialogTitle>Search for New Jobs</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin=\"dense\"
            label=\"Keywords\"
            placeholder=\"e.g., Python Developer\"
            fullWidth
            variant=\"outlined\"
            value={searchKeywords}
            onChange={(e) => setSearchKeywords(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSearchDialog(false)}>Cancel</Button>
          <Button onClick={handleSearch} variant=\"contained\">
            Search
          </Button>
        </DialogActions>
      </Dialog>

      {/* Exclude Company Dialog */}
      <Dialog open={excludeDialog} onClose={() => setExcludeDialog(false)}>
        <DialogTitle>Exclude Company</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin=\"dense\"
            label=\"Company Name\"
            placeholder=\"e.g., Company XYZ\"
            fullWidth
            variant=\"outlined\"
            value={excludeCompany}
            onChange={(e) => setExcludeCompany(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleExclude()}
          />
          <Typography variant=\"body2\" color=\"text.secondary\" sx={{ mt: 1 }}>
            Jobs from this company will be hidden from the list.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExcludeDialog(false)}>Cancel</Button>
          <Button onClick={handleExclude} variant=\"contained\">
            Exclude
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};