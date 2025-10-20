import React, { useState } from 'react';
import {
  Card,
  CardContent,
  TextField,
  Button,
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import { Search as SearchIcon, Work as WorkIcon } from '@mui/icons-material';
import { jobApi } from '../services/api';

interface JobSearchProps {
  onSearchComplete?: (newJobsCount: number) => void;
}

const countries = [
  { value: 'Dublin, County Dublin, Ireland', label: 'Ireland (Dublin)' },
  { value: 'Barcelona, Catalonia, Spain', label: 'Spain (Barcelona)' },
  { value: 'Madrid, Community of Madrid, Spain', label: 'Spain (Madrid)' },
  { value: 'Panama City, Panama', label: 'Panama (Panama City)' },
  { value: 'Santiago, Chile', label: 'Chile (Santiago)' },
];

const JobSearch: React.FC<JobSearchProps> = ({ onSearchComplete }) => {
  const [keywords, setKeywords] = useState('');
  const [location, setLocation] = useState('Dublin, County Dublin, Ireland');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResult, setSearchResult] = useState<{ success: boolean; message?: string; new_jobs?: number } | null>(null);

  const handleSearch = async () => {
    if (!keywords.trim()) {
      setSearchResult({
        success: false,
        message: 'Please enter keywords to search for jobs'
      });
      return;
    }

    setIsSearching(true);
    setSearchResult(null);

    try {
      const result = await jobApi.searchJobs(keywords.trim(), location);
      setSearchResult({
        success: result.success,
        message: result.success
          ? `Search completed! Found ${result.new_jobs} new jobs.`
          : 'Search failed. Please try again.',
        new_jobs: result.new_jobs
      });

      if (result.success && onSearchComplete) {
        onSearchComplete(result.new_jobs);
      }
    } catch (error: any) {
      console.error('Search error:', error);
      setSearchResult({
        success: false,
        message: error.response?.data?.detail || 'Search failed. Please try again.'
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <WorkIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
            Search New Jobs
          </Typography>
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Box sx={{ display: 'flex', gap: 2, mb: 2, flexDirection: { xs: 'column', sm: 'row' } }}>
          <TextField
            fullWidth
            label="Keywords"
            placeholder="e.g. Software Engineer, Python, React"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isSearching}
            sx={{ flex: 2 }}
          />

          <FormControl sx={{ flex: 1, minWidth: 200 }}>
            <InputLabel>Location</InputLabel>
            <Select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              label="Location"
              disabled={isSearching}
            >
              {countries.map((country) => (
                <MenuItem key={country.value} value={country.value}>
                  {country.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button
            variant="contained"
            startIcon={isSearching ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
            onClick={handleSearch}
            disabled={isSearching || !keywords.trim()}
            sx={{ minWidth: 120 }}
          >
            {isSearching ? 'Searching...' : 'Search Jobs'}
          </Button>
        </Box>

        {searchResult && (
          <Box sx={{ mt: 2 }}>
            <Alert
              severity={searchResult.success ? 'success' : 'error'}
              sx={{ borderRadius: 2 }}
            >
              {searchResult.message}
            </Alert>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default JobSearch;