import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-background relative">
      {/* Background gradient */}
      <div className="absolute top-0 left-0 right-0 h-[400px] bg-gradient-to-br from-blue-500/10 via-blue-600/10 to-purple-500/10 -z-10" />

      <div className="container max-w-sm mx-auto relative z-10">
        <div className="flex flex-col justify-center min-h-screen py-4">
          {/* Logo */}
          <div className="mb-12">
            <h1 className="text-4xl font-extrabold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent tracking-tight">
              JobHunt
            </h1>
            <p className="text-sm text-muted-foreground mt-2 font-medium">
              Track and manage your career opportunities
            </p>
          </div>

          {/* Login Card */}
          <div className="bg-card rounded-lg p-8 shadow-lg border">
            <h2 className="text-2xl font-bold mb-1">Welcome back</h2>
            <p className="text-sm text-muted-foreground mb-6">
              Sign in to continue to your dashboard
            </p>

            {/* Login Form */}
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="text-sm font-semibold mb-2 block">
                  Username or Email
                </label>
                <Input
                  type="text"
                  placeholder="Enter your username"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="username"
                  autoFocus
                  disabled={isSubmitting}
                  className="bg-muted/50"
                />
              </div>

              <div className="mb-6">
                <label className="text-sm font-semibold mb-2 block">
                  Password
                </label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="current-password"
                    disabled={isSubmitting}
                    className="bg-muted/50 pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={isSubmitting}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold"
                size="lg"
                disabled={isSubmitting || !username || !password}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign in'
                )}
              </Button>
            </form>

            {/* Register Link */}
            <div className="text-center mt-6">
              <p className="text-sm text-muted-foreground">
                Don't have an account?{' '}
                <RouterLink
                  to="/register"
                  className="text-primary font-semibold hover:underline"
                >
                  Create account
                </RouterLink>
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-12 text-center">
            <p className="text-xs text-muted-foreground">
              Secure job application tracking
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
