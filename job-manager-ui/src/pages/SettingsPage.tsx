/**
 * Settings Page
 * User preferences and account settings
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  FormLabel,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Chip,
  Stack,
  Divider,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Save, AccountCircle } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const SettingsPage: React.FC = () => {
  const { user, preferences, updatePreferences, refreshPreferences } = useAuth();

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    jobTypes: [] as string[],
    keywords: [] as string[],
    excludedKeywords: [] as string[],
    experienceLevels: [] as string[],
    excludeSenior: false,
    preferredCountries: [] as string[],
    preferredCities: [] as string[],
    excludedCompanies: [] as string[],
    easyApplyOnly: false,
    remoteOnly: false,
  });

  // Input fields for arrays
  const [keywordInput, setKeywordInput] = useState('');
  const [excludedKeywordInput, setExcludedKeywordInput] = useState('');
  const [cityInput, setCityInput] = useState('');
  const [companyInput, setCompanyInput] = useState('');

  // Available options
  const JOB_TYPES = ['software', 'hr', 'marketing', 'design', 'data', 'sales'];
  const EXPERIENCE_LEVELS = ['entry', 'junior', 'mid', 'senior', 'executive'];
  const COUNTRIES = ['Ireland', 'Spain', 'Panama', 'Chile', 'Netherlands', 'Germany', 'Sweden', 'Belgium', 'Denmark', 'Remote'];

  useEffect(() => {
    const loadPreferences = async () => {
      setIsLoading(true);
      try {
        await refreshPreferences();
      } catch (error) {
        toast.error('Failed to load preferences');
      } finally {
        setIsLoading(false);
      }
    };

    loadPreferences();
  }, [refreshPreferences]);

  useEffect(() => {
    if (preferences) {
      setFormData({
        jobTypes: preferences.job_types || [],
        keywords: preferences.keywords || [],
        excludedKeywords: preferences.excluded_keywords || [],
        experienceLevels: preferences.experience_levels || [],
        excludeSenior: preferences.exclude_senior || false,
        preferredCountries: preferences.preferred_countries || [],
        preferredCities: preferences.preferred_cities || [],
        excludedCompanies: preferences.excluded_companies || [],
        easyApplyOnly: preferences.easy_apply_only || false,
        remoteOnly: preferences.remote_only || false,
      });
    }
  }, [preferences]);

  const handleJobTypeToggle = (type: string) => {
    setFormData(prev => ({
      ...prev,
      jobTypes: prev.jobTypes.includes(type)
        ? prev.jobTypes.filter(t => t !== type)
        : [...prev.jobTypes, type],
    }));
  };

  const handleExperienceLevelToggle = (level: string) => {
    setFormData(prev => ({
      ...prev,
      experienceLevels: prev.experienceLevels.includes(level)
        ? prev.experienceLevels.filter(l => l !== level)
        : [...prev.experienceLevels, level],
    }));
  };

  const handleCountryToggle = (country: string) => {
    setFormData(prev => ({
      ...prev,
      preferredCountries: prev.preferredCountries.includes(country)
        ? prev.preferredCountries.filter(c => c !== country)
        : [...prev.preferredCountries, country],
    }));
  };

  const addKeyword = () => {
    if (keywordInput.trim()) {
      setFormData(prev => ({
        ...prev,
        keywords: [...prev.keywords, keywordInput.trim()],
      }));
      setKeywordInput('');
    }
  };

  const removeKeyword = (keyword: string) => {
    setFormData(prev => ({
      ...prev,
      keywords: prev.keywords.filter(k => k !== keyword),
    }));
  };

  const addExcludedKeyword = () => {
    if (excludedKeywordInput.trim()) {
      setFormData(prev => ({
        ...prev,
        excludedKeywords: [...prev.excludedKeywords, excludedKeywordInput.trim()],
      }));
      setExcludedKeywordInput('');
    }
  };

  const removeExcludedKeyword = (keyword: string) => {
    setFormData(prev => ({
      ...prev,
      excludedKeywords: prev.excludedKeywords.filter(k => k !== keyword),
    }));
  };

  const addCity = () => {
    if (cityInput.trim()) {
      setFormData(prev => ({
        ...prev,
        preferredCities: [...prev.preferredCities, cityInput.trim()],
      }));
      setCityInput('');
    }
  };

  const removeCity = (city: string) => {
    setFormData(prev => ({
      ...prev,
      preferredCities: prev.preferredCities.filter(c => c !== city),
    }));
  };

  const addCompany = () => {
    if (companyInput.trim()) {
      setFormData(prev => ({
        ...prev,
        excludedCompanies: [...prev.excludedCompanies, companyInput.trim()],
      }));
      setCompanyInput('');
    }
  };

  const removeCompany = (company: string) => {
    setFormData(prev => ({
      ...prev,
      excludedCompanies: prev.excludedCompanies.filter(c => c !== company),
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updatePreferences({
        job_types: formData.jobTypes,
        keywords: formData.keywords,
        excluded_keywords: formData.excludedKeywords,
        experience_levels: formData.experienceLevels,
        exclude_senior: formData.excludeSenior,
        preferred_countries: formData.preferredCountries,
        preferred_cities: formData.preferredCities,
        excluded_companies: formData.excludedCompanies,
        easy_apply_only: formData.easyApplyOnly,
        remote_only: formData.remoteOnly,
      });
    } catch (error) {
      // Error is handled in AuthContext
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="md">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        {/* Header */}
        <Box display="flex" alignItems="center" mb={4}>
          <AccountCircle sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
          <Box>
            <Typography variant="h4" fontWeight="bold">
              Settings
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Customize your job preferences
            </Typography>
          </Box>
        </Box>

        {/* User Info */}
        <Alert severity="info" sx={{ mb: 4 }}>
          Logged in as <strong>{user?.username}</strong> ({user?.email})
        </Alert>

        {/* Job Types */}
        <Box mb={4}>
          <FormControl component="fieldset">
            <FormLabel component="legend">
              <Typography variant="h6" gutterBottom>
                Job Types
              </Typography>
            </FormLabel>
            <FormGroup row>
              {JOB_TYPES.map(type => (
                <FormControlLabel
                  key={type}
                  control={
                    <Checkbox
                      checked={formData.jobTypes.includes(type)}
                      onChange={() => handleJobTypeToggle(type)}
                    />
                  }
                  label={type.charAt(0).toUpperCase() + type.slice(1)}
                />
              ))}
            </FormGroup>
          </FormControl>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Experience Levels */}
        <Box mb={4}>
          <FormControl component="fieldset">
            <FormLabel component="legend">
              <Typography variant="h6" gutterBottom>
                Experience Levels
              </Typography>
            </FormLabel>
            <FormGroup row>
              {EXPERIENCE_LEVELS.map(level => (
                <FormControlLabel
                  key={level}
                  control={
                    <Checkbox
                      checked={formData.experienceLevels.includes(level)}
                      onChange={() => handleExperienceLevelToggle(level)}
                    />
                  }
                  label={level.charAt(0).toUpperCase() + level.slice(1)}
                />
              ))}
            </FormGroup>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.excludeSenior}
                  onChange={(e) => setFormData({ ...formData, excludeSenior: e.target.checked })}
                />
              }
              label="Exclude Senior/Lead/Manager roles"
            />
          </FormControl>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Countries */}
        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Preferred Countries/Regions
          </Typography>
          <FormGroup row>
            {COUNTRIES.map(country => (
              <FormControlLabel
                key={country}
                control={
                  <Checkbox
                    checked={formData.preferredCountries.includes(country)}
                    onChange={() => handleCountryToggle(country)}
                  />
                }
                label={country}
              />
            ))}
          </FormGroup>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Keywords */}
        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Keywords (Include)
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={1}>
            Jobs matching these keywords will be shown
          </Typography>
          <Box display="flex" gap={1} mb={2}>
            <TextField
              fullWidth
              size="small"
              placeholder="e.g., Python, React, Machine Learning"
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addKeyword()}
            />
            <Button variant="outlined" onClick={addKeyword}>
              Add
            </Button>
          </Box>
          <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
            {formData.keywords.map(keyword => (
              <Chip key={keyword} label={keyword} onDelete={() => removeKeyword(keyword)} />
            ))}
          </Stack>
        </Box>

        {/* Excluded Keywords */}
        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Excluded Keywords
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={1}>
            Jobs with these keywords will be filtered out
          </Typography>
          <Box display="flex" gap={1} mb={2}>
            <TextField
              fullWidth
              size="small"
              placeholder="e.g., Senior, Lead, Manager"
              value={excludedKeywordInput}
              onChange={(e) => setExcludedKeywordInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addExcludedKeyword()}
            />
            <Button variant="outlined" onClick={addExcludedKeyword}>
              Add
            </Button>
          </Box>
          <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
            {formData.excludedKeywords.map(keyword => (
              <Chip key={keyword} label={keyword} onDelete={() => removeExcludedKeyword(keyword)} color="error" />
            ))}
          </Stack>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Preferred Cities */}
        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Preferred Cities (Optional)
          </Typography>
          <Box display="flex" gap={1} mb={2}>
            <TextField
              fullWidth
              size="small"
              placeholder="e.g., Dublin, Madrid"
              value={cityInput}
              onChange={(e) => setCityInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addCity()}
            />
            <Button variant="outlined" onClick={addCity}>
              Add
            </Button>
          </Box>
          <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
            {formData.preferredCities.map(city => (
              <Chip key={city} label={city} onDelete={() => removeCity(city)} />
            ))}
          </Stack>
        </Box>

        {/* Excluded Companies */}
        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Excluded Companies
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={1}>
            Never show jobs from these companies
          </Typography>
          <Box display="flex" gap={1} mb={2}>
            <TextField
              fullWidth
              size="small"
              placeholder="e.g., Company Name"
              value={companyInput}
              onChange={(e) => setCompanyInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addCompany()}
            />
            <Button variant="outlined" onClick={addCompany}>
              Add
            </Button>
          </Box>
          <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
            {formData.excludedCompanies.map(company => (
              <Chip key={company} label={company} onDelete={() => removeCompany(company)} color="error" />
            ))}
          </Stack>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Filters */}
        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Filters
          </Typography>
          <FormGroup>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.easyApplyOnly}
                  onChange={(e) => setFormData({ ...formData, easyApplyOnly: e.target.checked })}
                />
              }
              label="Easy Apply only (LinkedIn Easy Apply jobs)"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.remoteOnly}
                  onChange={(e) => setFormData({ ...formData, remoteOnly: e.target.checked })}
                />
              }
              label="Remote jobs only"
            />
          </FormGroup>
        </Box>

        {/* Save Button */}
        <Box display="flex" justifyContent="flex-end" mt={4}>
          <Button
            variant="contained"
            size="large"
            startIcon={isSaving ? <CircularProgress size={20} /> : <Save />}
            onClick={handleSave}
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Preferences'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default SettingsPage;
