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
  initial:    { opacity: 0, y: 18 },
  animate:    { opacity: 1, y: 0 },
  transition: { duration: 0.45, delay, ease: 'easeOut' },
});

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading } = useAuth();

  const [formData, setFormData] = useState({
    username: '', email: '', password: '', confirmPassword: '', fullName: '',
  });
  const [showPassword, setShowPassword]   = useState(false);
  const [isSubmitting, setIsSubmitting]   = useState(false);
  const [errors, setErrors]               = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (errors[e.target.name]) setErrors({ ...errors, [e.target.name]: '' });
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (formData.username.length < 3)
      newErrors.username = 'Username must be at least 3 characters';
    if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(formData.email))
      newErrors.email = 'Invalid email format';
    if (formData.password.length < 8)
      newErrors.password = 'Password must be at least 8 characters';
    if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.password))
      newErrors.password = 'Password must contain letters and numbers';
    if (formData.password !== formData.confirmPassword)
      newErrors.confirmPassword = 'Passwords do not match';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setIsSubmitting(true);
    try {
      await register(formData.username, formData.email, formData.password, formData.fullName || undefined);
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
      <div className="hidden lg:flex lg:w-[45%] relative overflow-hidden flex-col justify-between p-12
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
        <div className="space-y-5">
          {FEATURES.map(({ icon: Icon, title, desc }, i) => (
            <motion.div key={title} {...fadeUp(0.1 + i * 0.08)} className="flex items-start gap-4">
              <div className="w-9 h-9 rounded-lg bg-white/10 flex items-center justify-center shrink-0 mt-0.5">
                <Icon className="h-4 w-4 text-white" />
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

        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-purple-500/5 pointer-events-none lg:hidden" />

        <div className="relative w-full max-w-sm mx-auto px-6 py-10">

          {/* Mobile logo */}
          <motion.div {...fadeUp(0)} className="mb-8 lg:hidden">
            <div className="text-3xl font-extrabold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
              JobHunt
            </div>
            <p className="text-xs text-muted-foreground mt-1">Track and manage your career opportunities</p>
          </motion.div>

          {/* Heading */}
          <motion.div {...fadeUp(0.05)} className="mb-6">
            <h2 className="text-2xl font-bold">Create your account</h2>
            <p className="text-sm text-muted-foreground mt-1">Start tracking your job applications today</p>
          </motion.div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <motion.div {...fadeUp(0.1)}>
              <label className="text-sm font-semibold mb-1.5 block">Username</label>
              <Input
                name="username" type="text" placeholder="Choose a username" required
                value={formData.username} onChange={handleChange}
                autoComplete="username" autoFocus disabled={isSubmitting}
                className="bg-muted/50 h-11"
              />
              {errors.username && <p className="text-xs text-destructive mt-1">{errors.username}</p>}
            </motion.div>

            <motion.div {...fadeUp(0.13)}>
              <label className="text-sm font-semibold mb-1.5 block">Email</label>
              <Input
                name="email" type="email" placeholder="your@email.com" required
                value={formData.email} onChange={handleChange}
                autoComplete="email" disabled={isSubmitting}
                className="bg-muted/50 h-11"
              />
              {errors.email && <p className="text-xs text-destructive mt-1">{errors.email}</p>}
            </motion.div>

            <motion.div {...fadeUp(0.16)}>
              <label className="text-sm font-semibold mb-1.5 block">
                Full Name <span className="font-normal opacity-50">(optional)</span>
              </label>
              <Input
                name="fullName" type="text" placeholder="Your full name"
                value={formData.fullName} onChange={handleChange}
                autoComplete="name" disabled={isSubmitting}
                className="bg-muted/50 h-11"
              />
            </motion.div>

            <motion.div {...fadeUp(0.19)}>
              <label className="text-sm font-semibold mb-1.5 block">Password</label>
              <div className="relative">
                <Input
                  name="password" type={showPassword ? 'text' : 'password'}
                  placeholder="Create a strong password" required
                  value={formData.password} onChange={handleChange}
                  autoComplete="new-password" disabled={isSubmitting}
                  className="bg-muted/50 h-11 pr-10"
                />
                <button
                  type="button" onClick={() => setShowPassword(x => !x)} disabled={isSubmitting}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {errors.password && <p className="text-xs text-destructive mt-1">{errors.password}</p>}
            </motion.div>

            <motion.div {...fadeUp(0.22)}>
              <label className="text-sm font-semibold mb-1.5 block">Confirm Password</label>
              <Input
                name="confirmPassword" type={showPassword ? 'text' : 'password'}
                placeholder="Re-enter your password" required
                value={formData.confirmPassword} onChange={handleChange}
                autoComplete="new-password" disabled={isSubmitting}
                className="bg-muted/50 h-11"
              />
              {errors.confirmPassword && <p className="text-xs text-destructive mt-1">{errors.confirmPassword}</p>}
            </motion.div>

            <motion.div {...fadeUp(0.26)} className="pt-1">
              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold shadow-md shadow-blue-500/20 transition-shadow hover:shadow-lg hover:shadow-blue-500/30"
                size="lg"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Creating account...</>
                ) : 'Create account'}
              </Button>
            </motion.div>
          </form>

          <motion.div {...fadeUp(0.3)} className="text-center mt-6">
            <p className="text-sm text-muted-foreground">
              Already have an account?{' '}
              <RouterLink to="/login" className="text-primary font-semibold hover:underline">
                Sign in
              </RouterLink>
            </p>
          </motion.div>

          <motion.div {...fadeUp(0.35)} className="mt-8 text-center">
            <p className="text-xs text-muted-foreground">By creating an account, you agree to our terms</p>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
