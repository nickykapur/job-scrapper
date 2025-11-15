import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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

          {/* Register Card */}
          <div className="bg-card rounded-lg p-8 shadow-lg border">
            <h2 className="text-2xl font-bold mb-1">Create your account</h2>
            <p className="text-sm text-muted-foreground mb-6">
              Start tracking your job applications today
            </p>

            {/* Registration Form */}
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="text-sm font-semibold mb-2 block">
                  Username
                </label>
                <Input
                  name="username"
                  type="text"
                  placeholder="Choose a username"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  autoComplete="username"
                  autoFocus
                  disabled={isSubmitting}
                  className="bg-muted/50"
                />
                {errors.username && (
                  <p className="text-xs text-destructive mt-1">{errors.username}</p>
                )}
              </div>

              <div className="mb-4">
                <label className="text-sm font-semibold mb-2 block">
                  Email
                </label>
                <Input
                  name="email"
                  type="email"
                  placeholder="your@email.com"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  autoComplete="email"
                  disabled={isSubmitting}
                  className="bg-muted/50"
                />
                {errors.email && (
                  <p className="text-xs text-destructive mt-1">{errors.email}</p>
                )}
              </div>

              <div className="mb-4">
                <label className="text-sm font-semibold mb-2 block">
                  Full Name <span className="opacity-60">(optional)</span>
                </label>
                <Input
                  name="fullName"
                  type="text"
                  placeholder="Your full name"
                  value={formData.fullName}
                  onChange={handleChange}
                  autoComplete="name"
                  disabled={isSubmitting}
                  className="bg-muted/50"
                />
              </div>

              <div className="mb-4">
                <label className="text-sm font-semibold mb-2 block">
                  Password
                </label>
                <div className="relative">
                  <Input
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Create a strong password"
                    required
                    value={formData.password}
                    onChange={handleChange}
                    autoComplete="new-password"
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
                {errors.password && (
                  <p className="text-xs text-destructive mt-1">{errors.password}</p>
                )}
              </div>

              <div className="mb-6">
                <label className="text-sm font-semibold mb-2 block">
                  Confirm Password
                </label>
                <Input
                  name="confirmPassword"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Re-enter your password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  autoComplete="new-password"
                  disabled={isSubmitting}
                  className="bg-muted/50"
                />
                {errors.confirmPassword && (
                  <p className="text-xs text-destructive mt-1">{errors.confirmPassword}</p>
                )}
              </div>

              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold"
                size="lg"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating account...
                  </>
                ) : (
                  'Create account'
                )}
              </Button>
            </form>

            {/* Login Link */}
            <div className="text-center mt-6">
              <p className="text-sm text-muted-foreground">
                Already have an account?{' '}
                <RouterLink
                  to="/login"
                  className="text-primary font-semibold hover:underline"
                >
                  Sign in
                </RouterLink>
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-12 text-center">
            <p className="text-xs text-muted-foreground">
              By creating an account, you agree to our terms
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
