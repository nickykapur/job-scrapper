import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Link,
  CircularProgress,
  InputAdornment,
  IconButton,
  alpha,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: '' });
    }
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain letters and numbers';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);

    try {
      await register(formData.username, formData.email, formData.password, formData.fullName || undefined);
      navigate('/');
    } catch (error) {
      // Error handling is done in AuthContext with toast
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="sm">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        bgcolor: (theme) => theme.palette.mode === 'dark' ? '#0a0a0a' : '#fafafa',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '400px',
          background: (theme) => theme.palette.mode === 'dark'
            ? 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #7c3aed 100%)'
            : 'linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #8b5cf6 100%)',
          opacity: 0.1,
          zIndex: 0,
        },
      }}
    >
      <Container maxWidth="sm" sx={{ position: 'relative', zIndex: 1 }}>
        <Box
          display="flex"
          flexDirection="column"
          justifyContent="center"
          minHeight="100vh"
          py={4}
        >
          {/* Logo */}
          <Box mb={6}>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 800,
                fontSize: '2rem',
                background: (theme) => theme.palette.mode === 'dark'
                  ? 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%)'
                  : 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                letterSpacing: '-0.02em',
              }}
            >
              JobHunt
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, fontWeight: 500 }}>
              Track and manage your career opportunities
            </Typography>
          </Box>

          {/* Register Card */}
          <Box
            sx={{
              bgcolor: 'background.paper',
              borderRadius: 3,
              p: 4,
              boxShadow: (theme) => theme.palette.mode === 'dark'
                ? '0 8px 32px rgba(0,0,0,0.4)'
                : '0 8px 32px rgba(0,0,0,0.08)',
              border: '1px solid',
              borderColor: (theme) => alpha(theme.palette.divider, 0.1),
            }}
          >
            <Typography variant="h5" fontWeight={700} mb={1}>
              Create your account
            </Typography>

            <Typography variant="body2" color="text.secondary" mb={4}>
              Start tracking your job applications today
            </Typography>

            {/* Registration Form */}
            <form onSubmit={handleSubmit}>
              <Box mb={2}>
                <Typography variant="body2" fontWeight={600} mb={1} color="text.primary">
                  Username
                </Typography>
                <TextField
                  fullWidth
                  name="username"
                  placeholder="Choose a username"
                  variant="outlined"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  error={!!errors.username}
                  helperText={errors.username}
                  autoComplete="username"
                  autoFocus
                  disabled={isSubmitting}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: (theme) => theme.palette.mode === 'dark' ? '#1a1a1a' : '#f9fafb',
                      borderRadius: 2,
                      '& fieldset': { borderColor: 'transparent' },
                      '&:hover fieldset': { borderColor: (theme) => alpha(theme.palette.primary.main, 0.3) },
                      '&.Mui-focused fieldset': { borderColor: 'primary.main', borderWidth: '2px' },
                    },
                  }}
                />
              </Box>

              <Box mb={2}>
                <Typography variant="body2" fontWeight={600} mb={1} color="text.primary">
                  Email
                </Typography>
                <TextField
                  fullWidth
                  name="email"
                  type="email"
                  placeholder="your@email.com"
                  variant="outlined"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  error={!!errors.email}
                  helperText={errors.email}
                  autoComplete="email"
                  disabled={isSubmitting}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: (theme) => theme.palette.mode === 'dark' ? '#1a1a1a' : '#f9fafb',
                      borderRadius: 2,
                      '& fieldset': { borderColor: 'transparent' },
                      '&:hover fieldset': { borderColor: (theme) => alpha(theme.palette.primary.main, 0.3) },
                      '&.Mui-focused fieldset': { borderColor: 'primary.main', borderWidth: '2px' },
                    },
                  }}
                />
              </Box>

              <Box mb={2}>
                <Typography variant="body2" fontWeight={600} mb={1} color="text.primary">
                  Full Name <span style={{ opacity: 0.6 }}>(optional)</span>
                </Typography>
                <TextField
                  fullWidth
                  name="fullName"
                  placeholder="Your full name"
                  variant="outlined"
                  value={formData.fullName}
                  onChange={handleChange}
                  autoComplete="name"
                  disabled={isSubmitting}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: (theme) => theme.palette.mode === 'dark' ? '#1a1a1a' : '#f9fafb',
                      borderRadius: 2,
                      '& fieldset': { borderColor: 'transparent' },
                      '&:hover fieldset': { borderColor: (theme) => alpha(theme.palette.primary.main, 0.3) },
                      '&.Mui-focused fieldset': { borderColor: 'primary.main', borderWidth: '2px' },
                    },
                  }}
                />
              </Box>

              <Box mb={2}>
                <Typography variant="body2" fontWeight={600} mb={1} color="text.primary">
                  Password
                </Typography>
                <TextField
                  fullWidth
                  name="password"
                  placeholder="Create a strong password"
                  variant="outlined"
                  required
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleChange}
                  error={!!errors.password}
                  helperText={errors.password}
                  autoComplete="new-password"
                  disabled={isSubmitting}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          disabled={isSubmitting}
                          size="small"
                        >
                          {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: (theme) => theme.palette.mode === 'dark' ? '#1a1a1a' : '#f9fafb',
                      borderRadius: 2,
                      '& fieldset': { borderColor: 'transparent' },
                      '&:hover fieldset': { borderColor: (theme) => alpha(theme.palette.primary.main, 0.3) },
                      '&.Mui-focused fieldset': { borderColor: 'primary.main', borderWidth: '2px' },
                    },
                  }}
                />
              </Box>

              <Box mb={3}>
                <Typography variant="body2" fontWeight={600} mb={1} color="text.primary">
                  Confirm Password
                </Typography>
                <TextField
                  fullWidth
                  name="confirmPassword"
                  placeholder="Re-enter your password"
                  variant="outlined"
                  required
                  type={showPassword ? 'text' : 'password'}
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  error={!!errors.confirmPassword}
                  helperText={errors.confirmPassword}
                  autoComplete="new-password"
                  disabled={isSubmitting}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: (theme) => theme.palette.mode === 'dark' ? '#1a1a1a' : '#f9fafb',
                      borderRadius: 2,
                      '& fieldset': { borderColor: 'transparent' },
                      '&:hover fieldset': { borderColor: (theme) => alpha(theme.palette.primary.main, 0.3) },
                      '&.Mui-focused fieldset': { borderColor: 'primary.main', borderWidth: '2px' },
                    },
                  }}
                />
              </Box>

              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={isSubmitting}
                sx={{
                  py: 1.5,
                  borderRadius: 2,
                  fontWeight: 600,
                  fontSize: '0.9375rem',
                  textTransform: 'none',
                  background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                  boxShadow: 'none',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                    boxShadow: '0 4px 12px rgba(37,99,235,0.4)',
                  },
                  '&:disabled': {
                    background: (theme) => alpha(theme.palette.action.disabled, 0.12),
                  },
                }}
              >
                {isSubmitting ? <CircularProgress size={24} color="inherit" /> : 'Create account'}
              </Button>
            </form>

            {/* Login Link */}
            <Box textAlign="center" mt={3}>
              <Typography variant="body2" color="text.secondary">
                Already have an account?{' '}
                <Link
                  component={RouterLink}
                  to="/login"
                  underline="none"
                  sx={{
                    color: 'primary.main',
                    fontWeight: 600,
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  Sign in
                </Link>
              </Typography>
            </Box>
          </Box>

          {/* Footer */}
          <Box mt={6} textAlign="center">
            <Typography variant="caption" color="text.secondary">
              By creating an account, you agree to our terms
            </Typography>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default RegisterPage;
