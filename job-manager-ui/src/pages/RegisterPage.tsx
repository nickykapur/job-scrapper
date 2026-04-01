import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Eye, EyeOff, Loader2, BarChart3, Briefcase, Target, Trophy,
  Code2, TrendingUp, Database, Shield, Megaphone, Paintbrush,
  Users, Check, X, Plus,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '../contexts/AuthContext';
import authService from '../services/authService';

// ── Experience levels (mirrors SettingsPage + DB values) ─────────────────────

const EXPERIENCE_LEVELS = [
  { id: 'entry',     label: 'Entry',     desc: 'Internships, graduate roles' },
  { id: 'junior',    label: 'Junior',    desc: '0–2 years' },
  { id: 'mid',       label: 'Mid',       desc: '2–5 years' },
  { id: 'senior',    label: 'Senior',    desc: '5+ years' },
  { id: 'executive', label: 'Executive', desc: 'Director / VP / C-suite' },
] as const;

// ── Job type definitions ─────────────────────────────────────────────────────

const JOB_TYPES = [
  { id: 'software',      label: 'Software',      icon: Code2 },
  { id: 'finance',       label: 'Finance',       icon: BarChart3 },
  { id: 'hr',            label: 'HR',            icon: Users },
  { id: 'sales',         label: 'Sales',         icon: TrendingUp },
  { id: 'data',          label: 'Data',          icon: Database },
  { id: 'cybersecurity', label: 'Cyber',         icon: Shield },
  { id: 'marketing',     label: 'Marketing',     icon: Megaphone },
  { id: 'design',        label: 'Design',        icon: Paintbrush },
] as const;

// Suggestions sourced from real user keywords already in the system
const KEYWORD_SUGGESTIONS: Record<string, string[]> = {
  software: [
    'Software Engineer', 'Frontend Developer', 'Backend Developer',
    'Full Stack Developer', 'React Developer', 'Node.js Developer',
    'Python Developer', 'TypeScript Developer', 'Junior Developer',
    'DevOps Engineer', 'Cloud Engineer', 'Web Developer',
  ],
  finance: [
    'Financial Analyst', 'FP&A Analyst', 'Fund Accountant',
    'Credit Analyst', 'Junior Accountant', 'Accountant',
    'Treasury Analyst', 'Finance Associate', 'Investment Analyst',
    'Financial Controller', 'Fund Operations Analyst', 'Finance Analyst',
  ],
  hr: [
    'HR Coordinator', 'Talent Acquisition', 'Recruiter',
    'HR Generalist', 'People Operations', 'HR Business Partner',
    'HR Analyst', 'Recruitment Consultant', 'HR Administrator',
    'Talent Acquisition Specialist',
  ],
  sales: [
    'Sales Development Representative', 'Account Executive',
    'Business Development Manager', 'Inside Sales', 'SDR', 'BDR',
    'Account Manager', 'Sales Manager', 'Business Development Associate',
  ],
  data: [
    'Data Analyst', 'Data Scientist', 'Data Engineer',
    'Business Intelligence Analyst', 'Analytics Engineer',
    'ML Engineer', 'Junior Data Analyst', 'BI Developer',
  ],
  cybersecurity: [
    'Security Analyst', 'SOC Analyst', 'Penetration Tester',
    'Information Security Analyst', 'Cyber Security Analyst',
    'Security Engineer', 'Junior Security Analyst', 'GRC Analyst',
  ],
  marketing: [
    'Digital Marketing Manager', 'Marketing Coordinator',
    'Content Marketing Specialist', 'SEO Specialist',
    'Social Media Manager', 'Performance Marketing Analyst',
    'Growth Marketing', 'Email Marketing Specialist',
  ],
  design: [
    'UX Designer', 'UI Designer', 'Product Designer',
    'Graphic Designer', 'UX Researcher', 'Visual Designer',
    'Web Designer', 'Motion Designer',
  ],
};

// ── Branding features for left panel ────────────────────────────────────────

const FEATURES = [
  { icon: Briefcase, title: 'Track every application', desc: 'Never lose track of where you applied' },
  { icon: BarChart3,  title: 'Visual analytics',       desc: 'See your job hunt progress at a glance' },
  { icon: Target,     title: 'Smart job matching',     desc: 'Filter by role, country, and experience' },
  { icon: Trophy,     title: 'Gamified progress',      desc: 'Earn badges and level up as you apply' },
];

// ── Animation helpers ────────────────────────────────────────────────────────

const fadeUp = (delay = 0) => ({
  initial:    { opacity: 0, y: 18 },
  animate:    { opacity: 1, y: 0 },
  transition: { duration: 0.45, delay, ease: 'easeOut' },
});

// ── Component ────────────────────────────────────────────────────────────────

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, finalizeAuth, isLoading, refreshPreferences, user } = useAuth();

  // Step 1 state
  const [step, setStep] = useState<1 | 2>(1);
  const [formData, setFormData] = useState({
    username: '', email: '', password: '', confirmPassword: '', fullName: '',
  });
  const [showPassword, setShowPassword]   = useState(false);
  const [isSubmitting, setIsSubmitting]   = useState(false);
  const [errors, setErrors]               = useState<Record<string, string>>({});

  // Step 2 state
  const [selectedTypes, setSelectedTypes]       = useState<string[]>([]);
  const [selectedLevels, setSelectedLevels]     = useState<string[]>([]);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const [customInput, setCustomInput]           = useState('');
  const [isSavingPrefs, setIsSavingPrefs]       = useState(false);

  // ── Step 1 handlers ─────────────────────────────────────────────────────

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
      setStep(2); // show job picker instead of navigating immediately
    } catch {
      // error toast handled in AuthContext
    } finally {
      setIsSubmitting(false);
    }
  };

  // ── Step 2 handlers ─────────────────────────────────────────────────────

  const toggleType = (id: string) => {
    setSelectedTypes(prev =>
      prev.includes(id) ? prev.filter(t => t !== id) : [...prev, id]
    );
  };

  const toggleLevel = (id: string) => {
    setSelectedLevels(prev =>
      prev.includes(id) ? prev.filter(l => l !== id) : [...prev, id]
    );
  };

  const toggleKeyword = (kw: string) => {
    setSelectedKeywords(prev =>
      prev.includes(kw) ? prev.filter(k => k !== kw) : [...prev, kw]
    );
  };

  const addCustomKeyword = () => {
    const kw = customInput.trim();
    if (kw && !selectedKeywords.includes(kw)) {
      setSelectedKeywords(prev => [...prev, kw]);
    }
    setCustomInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') { e.preventDefault(); addCustomKeyword(); }
  };

  // Suggestions = union of selected-type keywords, minus already-selected
  const suggestions = [
    ...new Set(selectedTypes.flatMap(t => KEYWORD_SUGGESTIONS[t] ?? [])),
  ].filter(kw => !selectedKeywords.includes(kw));

  const handleFinish = async () => {
    setIsSavingPrefs(true);
    try {
      if (selectedTypes.length > 0 || selectedKeywords.length > 0 || selectedLevels.length > 0) {
        await authService.updatePreferences({
          ...(selectedTypes.length    > 0 && { job_types:         selectedTypes }),
          ...(selectedKeywords.length > 0 && { keywords:          selectedKeywords }),
          ...(selectedLevels.length   > 0 && { experience_levels: selectedLevels }),
        });
      }
    } catch {
      // silently ignore — user can set prefs later in settings
    } finally {
      setIsSavingPrefs(false);
    }
    // Set user state now — AppRouter will redirect to dashboard
    await finalizeAuth();
  };

  // ── Loading screen ───────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen flex">

      {/* ── Left branding panel ── */}
      <div className="hidden lg:flex lg:w-[45%] relative overflow-hidden flex-col justify-between p-12
                      bg-gradient-to-br from-blue-600 via-blue-700 to-purple-700">

        {/* Decorative orbs */}
        <div className="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-white/5 blur-3xl pointer-events-none" />
        <div className="absolute top-1/2 -right-32 w-80 h-80 rounded-full bg-purple-400/10 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 left-1/3 w-72 h-72 rounded-full bg-blue-300/10 blur-3xl pointer-events-none" />

        <AnimatePresence mode="wait">
          {step === 1 ? (
            <motion.div key="brand-step1" {...fadeUp(0)}>
              <div className="text-4xl font-extrabold text-white tracking-tight">JobHunt</div>
              <p className="text-blue-200 text-sm mt-1">Your career, organised</p>
            </motion.div>
          ) : (
            <motion.div key="brand-step2" {...fadeUp(0)}>
              <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center mb-4">
                <Check className="h-6 w-6 text-white" />
              </div>
              <div className="text-3xl font-extrabold text-white tracking-tight">
                Account created!
              </div>
              <p className="text-blue-200 text-sm mt-2">
                Welcome, <span className="text-white font-semibold">{user?.username ?? formData.username}</span>.
                <br />One more step to personalise your feed.
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Feature list — only in step 1 */}
        <AnimatePresence>
          {step === 1 && (
            <motion.div key="features" className="space-y-5" initial={{ opacity: 1 }} exit={{ opacity: 0 }}>
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
            </motion.div>
          )}
        </AnimatePresence>

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

      {/* ── Right panel ── */}
      <div className="flex-1 flex flex-col justify-center bg-background relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-purple-500/5 pointer-events-none lg:hidden" />

        <AnimatePresence mode="wait">

          {/* ── STEP 1: Credentials ── */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 0 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }}
              transition={{ duration: 0.3 }}
              className="relative w-full max-w-sm mx-auto px-6 py-10"
            >
              {/* Mobile logo */}
              <motion.div {...fadeUp(0)} className="mb-8 lg:hidden">
                <div className="text-3xl font-extrabold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
                  JobHunt
                </div>
                <p className="text-xs text-muted-foreground mt-1">Track and manage your career opportunities</p>
              </motion.div>

              <motion.div {...fadeUp(0.05)} className="mb-6">
                <h2 className="text-2xl font-bold">Create your account</h2>
                <p className="text-sm text-muted-foreground mt-1">Start tracking your job applications today</p>
              </motion.div>

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
                    className="w-full h-11 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold shadow-md shadow-blue-500/20 hover:shadow-lg hover:shadow-blue-500/30"
                    size="lg"
                    disabled={isSubmitting}
                  >
                    {isSubmitting
                      ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Creating account...</>
                      : 'Create account →'}
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
            </motion.div>
          )}

          {/* ── STEP 2: Job preferences ── */}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.35 }}
              className="relative w-full max-w-lg mx-auto px-6 py-10"
            >
              <div className="mb-6">
                <div className="text-xs font-semibold text-primary uppercase tracking-wide mb-1">Step 2 of 2</div>
                <h2 className="text-2xl font-bold">What roles are you looking for?</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Pick your job categories — we'll suggest keywords you can add to your profile.
                </p>
              </div>

              {/* Job type cards */}
              <div className="grid grid-cols-4 gap-2 mb-6">
                {JOB_TYPES.map(({ id, label, icon: Icon }) => {
                  const selected = selectedTypes.includes(id);
                  return (
                    <button
                      key={id}
                      type="button"
                      onClick={() => toggleType(id)}
                      className={`flex flex-col items-center gap-1.5 rounded-xl border p-3 text-xs font-medium transition-all
                        ${selected
                          ? 'bg-primary/10 border-primary text-primary shadow-sm'
                          : 'bg-muted/30 border-border text-muted-foreground hover:border-primary/50 hover:text-foreground'
                        }`}
                    >
                      <Icon className="h-5 w-5" />
                      {label}
                      {selected && <Check className="h-3 w-3 text-primary" />}
                    </button>
                  );
                })}
              </div>

              {/* Experience level chips */}
              <div className="mb-6">
                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Experience level
                </div>
                <div className="flex flex-wrap gap-2">
                  {EXPERIENCE_LEVELS.map(({ id, label, desc }) => {
                    const selected = selectedLevels.includes(id);
                    return (
                      <button
                        key={id}
                        type="button"
                        onClick={() => toggleLevel(id)}
                        className={`flex flex-col rounded-xl border px-3 py-2 text-left transition-all
                          ${selected
                            ? 'bg-primary/10 border-primary text-primary shadow-sm'
                            : 'bg-muted/30 border-border text-muted-foreground hover:border-primary/50 hover:text-foreground'
                          }`}
                      >
                        <span className="text-xs font-semibold flex items-center gap-1">
                          {label}
                          {selected && <Check className="h-3 w-3" />}
                        </span>
                        <span className="text-[10px] opacity-60 mt-0.5">{desc}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Keyword suggestions (appear when types selected) */}
              <AnimatePresence>
                {suggestions.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.25 }}
                    className="mb-4 overflow-hidden"
                  >
                    <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                      Suggested keywords — click to add
                    </div>
                    <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto pr-1">
                      {suggestions.map(kw => (
                        <button
                          key={kw}
                          type="button"
                          onClick={() => toggleKeyword(kw)}
                          className="text-xs rounded-full border border-dashed border-border bg-background hover:border-primary hover:text-primary px-2.5 py-1 transition-colors"
                        >
                          + {kw}
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Selected keywords */}
              <AnimatePresence>
                {selectedKeywords.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="mb-4 overflow-hidden"
                  >
                    <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                      Your keywords ({selectedKeywords.length})
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedKeywords.map(kw => (
                        <span
                          key={kw}
                          className="inline-flex items-center gap-1 text-xs rounded-full bg-primary/10 text-primary border border-primary/20 pl-2.5 pr-1.5 py-1 font-medium"
                        >
                          {kw}
                          <button
                            type="button"
                            onClick={() => toggleKeyword(kw)}
                            className="hover:text-destructive transition-colors"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Custom keyword input */}
              <div className="mb-6">
                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Add a custom keyword
                </div>
                <div className="flex gap-2">
                  <Input
                    type="text"
                    placeholder="e.g. Junior Analyst, React Native..."
                    value={customInput}
                    onChange={e => setCustomInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    className="bg-muted/50 h-10 flex-1"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={addCustomKeyword}
                    disabled={!customInput.trim()}
                    className="h-10 px-3 shrink-0"
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex flex-col gap-2">
                <Button
                  onClick={handleFinish}
                  disabled={isSavingPrefs}
                  className="w-full h-11 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold shadow-md shadow-blue-500/20"
                  size="lg"
                >
                  {isSavingPrefs
                    ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</>
                    : selectedTypes.length > 0 || selectedKeywords.length > 0 || selectedLevels.length > 0
                      ? 'Get started →'
                      : 'Go to dashboard →'}
                </Button>
                <button
                  type="button"
                  onClick={finalizeAuth}
                  className="text-sm text-muted-foreground hover:text-foreground text-center py-1 transition-colors"
                >
                  Skip for now — I'll set this up later
                </button>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
};

export default RegisterPage;
