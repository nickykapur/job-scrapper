import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { Loader2, BarChart3, Briefcase, Target, Trophy } from 'lucide-react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

const FEATURES = [
  { icon: Briefcase,  title: 'Track every application', desc: 'Never lose track of where you applied' },
  { icon: BarChart3,  title: 'Visual analytics',        desc: 'See your job hunt progress at a glance' },
  { icon: Target,     title: 'Smart job matching',      desc: 'Filter by role, country, and experience' },
  { icon: Trophy,     title: 'Gamified progress',       desc: 'Earn badges and level up as you apply' },
];

const fadeUp = (delay = 0) => ({
  initial:    { opacity: 0, y: 18 },
  animate:    { opacity: 1, y: 0 },
  transition: { duration: 0.45, delay, ease: 'easeOut' },
});

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { registerQuick, isLoading } = useAuth();

  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const e: Record<string, string> = {};
    if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
      e.email = 'Invalid email format';
    }
    if (!fullName.trim()) e.fullName = 'Full name is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setIsSubmitting(true);
    try {
      const res = await registerQuick(email.trim(), fullName.trim());
      toast.success(
        `Account created! Temporary password: ${res.default_password}. You can change it later in Settings.`,
        { duration: 8000 }
      );
      navigate('/onboarding', { replace: true });
    } catch {
      // toast already shown in context
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
      <div className="hidden lg:flex lg:w-[45%] relative overflow-hidden flex-col justify-between p-12
                      bg-gradient-to-br from-blue-600 via-blue-700 to-purple-700">
        <div className="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-white/5 blur-3xl pointer-events-none" />
        <div className="absolute top-1/2 -right-32 w-80 h-80 rounded-full bg-purple-400/10 blur-3xl pointer-events-none" />

        <motion.div {...fadeUp(0)}>
          <div className="text-4xl font-extrabold text-white tracking-tight">JobHunt</div>
          <p className="text-blue-200 text-sm mt-1">Your career, organised</p>
        </motion.div>

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

      <div className="flex-1 flex flex-col justify-center bg-background relative overflow-hidden">
        <motion.div {...fadeUp(0)} className="relative w-full max-w-sm mx-auto px-6 py-10">
          <div className="mb-8 lg:hidden">
            <div className="text-3xl font-extrabold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
              JobHunt
            </div>
            <p className="text-xs text-muted-foreground mt-1">Track and manage your career opportunities</p>
          </div>

          <div className="mb-6">
            <h2 className="text-2xl font-bold">Create your account</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Upload your CV next — we'll personalise your job feed automatically.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-semibold mb-1.5 block">Full Name</label>
              <Input
                name="fullName" type="text" placeholder="Your full name" required
                value={fullName} onChange={e => setFullName(e.target.value)}
                autoComplete="name" autoFocus disabled={isSubmitting}
                className="bg-muted/50 h-11"
              />
              {errors.fullName && <p className="text-xs text-destructive mt-1">{errors.fullName}</p>}
            </div>

            <div>
              <label className="text-sm font-semibold mb-1.5 block">Email</label>
              <Input
                name="email" type="email" placeholder="your@email.com" required
                value={email} onChange={e => setEmail(e.target.value)}
                autoComplete="email" disabled={isSubmitting}
                className="bg-muted/50 h-11"
              />
              {errors.email && <p className="text-xs text-destructive mt-1">{errors.email}</p>}
            </div>

            <div className="rounded-lg border border-dashed border-blue-400/30 bg-blue-500/5 p-3 text-xs text-muted-foreground">
              Your temporary password is <code className="text-foreground font-mono">pass1234</code> — change it from Settings once you're in.
            </div>

            <div className="pt-1">
              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold shadow-md shadow-blue-500/20"
                size="lg"
                disabled={isSubmitting}
              >
                {isSubmitting
                  ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Creating account...</>
                  : 'Continue to onboarding →'}
              </Button>
            </div>
          </form>

          <div className="text-center mt-6">
            <p className="text-sm text-muted-foreground">
              Already have an account?{' '}
              <RouterLink to="/login" className="text-primary font-semibold hover:underline">
                Sign in
              </RouterLink>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default RegisterPage;
