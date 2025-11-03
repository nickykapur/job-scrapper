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

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await login(username, password);
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

          {/* Login Card */}
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
              Welcome back
            </Typography>

            <Typography variant="body2" color="text.secondary" mb={4}>
              Sign in to continue to your dashboard
            </Typography>

            {/* Login Form */}
            <form onSubmit={handleSubmit}>
              <Box mb={2}>
                <Typography variant="body2" fontWeight={600} mb={1} color="text.primary">
                  Username or Email
                </Typography>
                <TextField
                  fullWidth
                  placeholder="Enter your username"
                  variant="outlined"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="username"
                  autoFocus
                  disabled={isSubmitting}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: (theme) => theme.palette.mode === 'dark' ? '#1a1a1a' : '#f9fafb',
                      borderRadius: 2,
                      '& fieldset': {
                        borderColor: 'transparent',
                      },
                      '&:hover fieldset': {
                        borderColor: (theme) => alpha(theme.palette.primary.main, 0.3),
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: 'primary.main',
                        borderWidth: '2px',
                      },
                    },
                  }}
                />
              </Box>

              <Box mb={3}>
                <Typography variant="body2" fontWeight={600} mb={1} color="text.primary">
                  Password
                </Typography>
                <TextField
                  fullWidth
                  placeholder="Enter your password"
                  variant="outlined"
                  required
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
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
                      '& fieldset': {
                        borderColor: 'transparent',
                      },
                      '&:hover fieldset': {
                        borderColor: (theme) => alpha(theme.palette.primary.main, 0.3),
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: 'primary.main',
                        borderWidth: '2px',
                      },
                    },
                  }}
                />
              </Box>

              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={isSubmitting || !username || !password}
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
                {isSubmitting ? <CircularProgress size={24} color="inherit" /> : 'Sign in'}
              </Button>
            </form>

            {/* Register Link */}
            <Box textAlign="center" mt={3}>
              <Typography variant="body2" color="text.secondary">
                Don't have an account?{' '}
                <Link
                  component={RouterLink}
                  to="/register"
                  underline="none"
                  sx={{
                    color: 'primary.main',
                    fontWeight: 600,
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  Create account
                </Link>
              </Typography>
            </Box>
          </Box>

          {/* Footer */}
          <Box mt={6} textAlign="center">
            <Typography variant="caption" color="text.secondary">
              Secure job application tracking
            </Typography>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default LoginPage;
