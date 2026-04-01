import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { Eye, EyeOff, Loader2, BarChart3, Briefcase, Target, Trophy } from 'lucide-react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '../contexts/AuthContext';

const FEATURES = [
  { icon: Briefcase, title: 'Track every application', desc: 'Never lose track of where you applied' },
  { icon: BarChart3,  title: 'Visual analytics',       desc: 'See your job hunt progress at a glance' },
  { icon: Target,     title: 'Smart job matching',     desc: 'Filter by role, country, and experience' },
  { icon: Trophy,     title: 'Gamified progress',      desc: 'Earn badges and level up as you apply' },
];

const fadeUp = (delay = 0) => ({
  initial:   { opacity: 0, y: 18 },
  animate:   { opacity: 1, y: 0 },
  transition: { duration: 0.45, delay, ease: 'easeOut' },
});

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();

  const [username, setUsername]       = useState('');
  const [password, setPassword]       = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await login(username, password);
      navigate('/');
    } catch {
      // handled in AuthContext via toast
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
    <div className="min-h-screen flex">

      {/* ── Left branding panel ── */}
      <div className="hidden lg:flex lg:w-[55%] relative overflow-hidden flex-col justify-between p-12
                      bg-gradient-to-br from-blue-600 via-blue-700 to-purple-700">

        {/* Decorative orbs */}
        <div className="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-white/5 blur-3xl pointer-events-none" />
        <div className="absolute top-1/2 -right-32 w-80 h-80 rounded-full bg-purple-400/10 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 left-1/3 w-72 h-72 rounded-full bg-blue-300/10 blur-3xl pointer-events-none" />

        {/* Logo */}
        <motion.div {...fadeUp(0)}>
          <div className="text-4xl font-extrabold text-white tracking-tight">JobHunt</div>
          <p className="text-blue-200 text-sm mt-1">Your career, organised</p>
        </motion.div>

        {/* Feature list */}
        <div className="space-y-6">
          {FEATURES.map(({ icon: Icon, title, desc }, i) => (
            <motion.div key={title} {...fadeUp(0.1 + i * 0.08)} className="flex items-start gap-4">
              <div className="w-9 h-9 rounded-lg bg-white/10 flex items-center justify-center shrink-0 mt-0.5">
                <Icon className="h-4.5 w-4.5 text-white" />
              </div>
              <div>
                <div className="text-white font-semibold text-sm">{title}</div>
                <div className="text-blue-200 text-xs mt-0.5">{desc}</div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Stats row */}
        <motion.div {...fadeUp(0.5)} className="flex gap-8">
          {[
            { value: '500+', label: 'Jobs tracked daily' },
            { value: '8',    label: 'Countries covered' },
            { value: '100%', label: 'Free to use' },
          ].map(({ value, label }) => (
            <div key={label}>
              <div className="text-2xl font-bold text-white">{value}</div>
              <div className="text-xs text-blue-200">{label}</div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* ── Right form panel ── */}
      <div className="flex-1 flex flex-col justify-center bg-background relative overflow-hidden">

        {/* Subtle background tint (mobile only fallback) */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-purple-500/5 pointer-events-none lg:hidden" />

        <div className="relative w-full max-w-sm mx-auto px-6 py-10">

          {/* Mobile logo */}
          <motion.div {...fadeUp(0)} className="mb-10 lg:hidden">
            <div className="text-3xl font-extrabold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
              JobHunt
            </div>
            <p className="text-xs text-muted-foreground mt-1">Track and manage your career opportunities</p>
          </motion.div>

          {/* Heading */}
          <motion.div {...fadeUp(0.05)} className="mb-8">
            <h2 className="text-2xl font-bold">Welcome back</h2>
            <p className="text-sm text-muted-foreground mt-1">Sign in to continue to your dashboard</p>
          </motion.div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <motion.div {...fadeUp(0.1)}>
              <label className="text-sm font-semibold mb-1.5 block">Username or Email</label>
              <Input
                type="text"
                placeholder="Enter your username"
                required
                value={username}
                onChange={e => setUsername(e.target.value)}
                autoComplete="username"
                autoFocus
                disabled={isSubmitting}
                className="bg-muted/50 h-11"
              />
            </motion.div>

            <motion.div {...fadeUp(0.15)}>
              <label className="text-sm font-semibold mb-1.5 block">Password</label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  required
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  autoComplete="current-password"
                  disabled={isSubmitting}
                  className="bg-muted/50 h-11 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(x => !x)}
                  disabled={isSubmitting}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </motion.div>

            <motion.div {...fadeUp(0.2)} className="pt-1">
              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold shadow-md shadow-blue-500/20 transition-shadow hover:shadow-lg hover:shadow-blue-500/30"
                size="lg"
                disabled={isSubmitting || !username || !password}
              >
                {isSubmitting ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Signing in...</>
                ) : 'Sign in'}
              </Button>
            </motion.div>
          </form>

          <motion.div {...fadeUp(0.25)} className="text-center mt-6">
            <p className="text-sm text-muted-foreground">
              Don't have an account?{' '}
              <RouterLink to="/register" className="text-primary font-semibold hover:underline">
                Create account
              </RouterLink>
            </p>
          </motion.div>

          <motion.div {...fadeUp(0.3)} className="mt-10 text-center">
            <p className="text-xs text-muted-foreground">Secure job application tracking</p>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
