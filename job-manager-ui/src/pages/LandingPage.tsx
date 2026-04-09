import React, { useRef, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  motion,
  useScroll,
  useTransform,
  useInView,
  useReducedMotion,
} from 'framer-motion';
import {
  Briefcase, BarChart3, Target, Bell, Globe, Zap,
  ArrowRight, Check, Star, TrendingUp, Shield, Menu, X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

// ── Helpers ───────────────────────────────────────────────────────────────────

const RevealSection: React.FC<{ children: React.ReactNode; className?: string; delay?: number }> = ({
  children, className = '', delay = 0,
}) => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-80px' });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.65, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

// ── Data ──────────────────────────────────────────────────────────────────────

const FEATURES = [
  {
    icon: Target,
    title: 'Smart job matching',
    desc: 'Set your keywords, countries and experience level once. We surface only jobs that fit.',
    color: 'from-blue-500 to-blue-600',
  },
  {
    icon: Globe,
    title: 'Multi-country scraping',
    desc: 'Live listings from Ireland, Spain, Germany, Netherlands, UK and more — updated daily.',
    color: 'from-violet-500 to-violet-600',
  },
  {
    icon: BarChart3,
    title: 'Personal analytics',
    desc: 'See your application velocity, response rates, and which roles get the most traction.',
    color: 'from-emerald-500 to-emerald-600',
  },
  {
    icon: Bell,
    title: 'Real-time alerts',
    desc: 'Get notified the moment a matching job is posted — before the queue fills up.',
    color: 'from-orange-500 to-orange-600',
  },
  {
    icon: Zap,
    title: 'One-click apply',
    desc: 'Easy Apply jobs are flagged so you can blitz through applications in minutes.',
    color: 'from-yellow-500 to-yellow-600',
  },
  {
    icon: TrendingUp,
    title: 'Interview tracker',
    desc: 'Log interviews, track outcomes, and spot patterns across companies and roles.',
    color: 'from-pink-500 to-pink-600',
  },
];

const STATS = [
  { value: '500+', label: 'Jobs tracked daily' },
  { value: '8',    label: 'Countries covered' },
  { value: '100%', label: 'Free to use' },
  { value: '< 24h', label: 'Listing freshness' },
];

const HOW_IT_WORKS = [
  { step: '01', title: 'Create your account', desc: 'Sign up in under a minute. No credit card, no tricks.' },
  { step: '02', title: 'Set your preferences', desc: 'Tell us the roles, keywords and countries you care about.' },
  { step: '03', title: 'Get matched jobs', desc: 'Your personal feed updates every day with filtered, relevant listings.' },
  { step: '04', title: 'Track & apply', desc: 'Apply directly on LinkedIn and track every application in one place.' },
];

// ── Component ─────────────────────────────────────────────────────────────────

const LandingPage: React.FC = () => {
  const heroRef = useRef(null);
  const prefersReduced = useReducedMotion();
  const [isMobile, setIsMobile] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  const disableParallax = prefersReduced || isMobile;

  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] });

  // Parallax transforms — disabled on mobile/reduced-motion for performance
  const heroY       = useTransform(scrollYProgress, [0, 1], disableParallax ? ['0%', '0%'] : ['0%', '35%']);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.7], disableParallax ? [1, 1] : [1, 0]);
  const orb1Y       = useTransform(scrollYProgress, [0, 1], disableParallax ? ['0%', '0%'] : ['0%', '-25%']);
  const orb2Y       = useTransform(scrollYProgress, [0, 1], disableParallax ? ['0%', '0%'] : ['0%', '20%']);
  const orb3Y       = useTransform(scrollYProgress, [0, 1], disableParallax ? ['0%', '0%'] : ['0%', '-15%']);

  return (
    <div className="bg-[#060b18] text-white min-h-screen overflow-x-hidden">

      {/* ── Sticky Header ── */}
      <header className="fixed top-0 left-0 right-0 z-50">
        <div className="mx-auto max-w-6xl px-5 py-4 flex items-center justify-between">
          {/* Glass pill */}
          <div className="absolute inset-0 mx-2 mt-2 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 pointer-events-none" />

          <div className="relative flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
              <Briefcase className="h-4 w-4 text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">JobHunt</span>
          </div>

          <nav className="relative hidden md:flex items-center gap-8 text-sm text-white/70">
            <a href="#features"   className="hover:text-white transition-colors">Features</a>
            <a href="#how"        className="hover:text-white transition-colors">How it works</a>
            <a href="#stats"      className="hover:text-white transition-colors">Stats</a>
          </nav>

          <div className="relative flex items-center gap-3">
            <Link to="/login" className="hidden md:block">
              <Button variant="ghost" size="sm"
                className="text-white/80 hover:text-white hover:bg-white/10 border border-white/10">
                Log in
              </Button>
            </Link>
            <Link to="/register" className="hidden md:block">
              <Button size="sm"
                className="bg-gradient-to-r from-blue-500 to-violet-600 hover:from-blue-600 hover:to-violet-700 text-white border-0 shadow-lg shadow-blue-500/25">
                Get started
              </Button>
            </Link>
            {/* Mobile menu toggle */}
            <button
              className="relative md:hidden p-2 text-white/70 hover:text-white"
              onClick={() => setMenuOpen(o => !o)}
              aria-label="Toggle menu"
            >
              {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Mobile dropdown */}
        {menuOpen && (
          <div className="md:hidden mx-2 mb-2 rounded-2xl bg-[#0d1425] border border-white/10 px-5 py-4 flex flex-col gap-4 text-sm">
            <a href="#features" className="text-white/70 hover:text-white transition-colors" onClick={() => setMenuOpen(false)}>Features</a>
            <a href="#how"      className="text-white/70 hover:text-white transition-colors" onClick={() => setMenuOpen(false)}>How it works</a>
            <a href="#stats"    className="text-white/70 hover:text-white transition-colors" onClick={() => setMenuOpen(false)}>Stats</a>
            <div className="flex gap-3 pt-1 border-t border-white/10">
              <Link to="/login" className="flex-1" onClick={() => setMenuOpen(false)}>
                <Button variant="ghost" size="sm" className="w-full text-white/80 hover:text-white hover:bg-white/10 border border-white/10">
                  Log in
                </Button>
              </Link>
              <Link to="/register" className="flex-1" onClick={() => setMenuOpen(false)}>
                <Button size="sm" className="w-full bg-gradient-to-r from-blue-500 to-violet-600 text-white border-0">
                  Get started
                </Button>
              </Link>
            </div>
          </div>
        )}
      </header>

      {/* ── Hero ── */}
      <section ref={heroRef} className="relative min-h-screen flex items-center justify-center overflow-hidden">

        {/* Parallax background orbs — smaller on mobile to reduce GPU load */}
        <motion.div style={{ y: orb1Y }}
          className="absolute top-1/4 left-1/4 w-[250px] h-[250px] sm:w-[600px] sm:h-[600px] rounded-full bg-blue-600/20 blur-[60px] sm:blur-[120px] pointer-events-none" />
        <motion.div style={{ y: orb2Y }}
          className="absolute top-1/3 right-1/4 w-[200px] h-[200px] sm:w-[500px] sm:h-[500px] rounded-full bg-violet-600/20 blur-[60px] sm:blur-[120px] pointer-events-none" />
        <motion.div style={{ y: orb3Y }}
          className="absolute bottom-1/4 left-1/2 w-[180px] h-[180px] sm:w-[400px] sm:h-[400px] rounded-full bg-indigo-500/15 blur-[50px] sm:blur-[100px] pointer-events-none" />

        {/* Grid overlay */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjAzKSIgc3Ryb2tlLXdpZHRoPSIxIj48cGF0aCBkPSJNNjAgMEgwdjYwaDYwVjB6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-100 pointer-events-none" />

        <motion.div style={{ y: heroY, opacity: heroOpacity }}
          className="relative text-center px-5 max-w-4xl mx-auto pt-20">

          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-medium text-blue-300 mb-8"
          >
            <Star className="h-3 w-3 fill-blue-400 text-blue-400" />
            Completely free · No credit card needed
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.75, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight leading-[1.08] mb-6"
          >
            Find your{' '}
            <span className="bg-gradient-to-r from-blue-400 via-violet-400 to-blue-300 bg-clip-text text-transparent">
              dream job
            </span>
            <br />before everyone else
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="text-lg sm:text-xl text-white/60 max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            JobHunt scrapes LinkedIn daily across 8 countries, filters jobs to your exact criteria,
            and tracks every application — so you can focus on getting hired.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link to="/register">
              <Button size="lg"
                className="h-13 px-8 bg-gradient-to-r from-blue-500 to-violet-600 hover:from-blue-600 hover:to-violet-700 text-white font-semibold text-base shadow-2xl shadow-blue-500/30 border-0">
                Start for free
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline"
                className="h-13 px-8 border-white/20 bg-white/5 text-white hover:bg-white/10 hover:border-white/30 font-medium text-base backdrop-blur-sm">
                Already have an account
              </Button>
            </Link>
          </motion.div>

          {/* Trust strip */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.75 }}
            className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 mt-12 text-xs text-white/40"
          >
            {['No spam', 'No subscriptions', 'Open to everyone', 'Updated daily'].map(t => (
              <span key={t} className="flex items-center gap-1.5">
                <Check className="h-3 w-3 text-emerald-400" />{t}
              </span>
            ))}
          </motion.div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1"
        >
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ repeat: Infinity, duration: 1.6, ease: 'easeInOut' }}
            className="w-px h-10 bg-gradient-to-b from-white/40 to-transparent"
          />
        </motion.div>
      </section>

      {/* ── Stats ── */}
      <section id="stats" className="py-20 border-y border-white/5 bg-white/[0.02]">
        <div className="max-w-5xl mx-auto px-5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {STATS.map(({ value, label }, i) => (
              <RevealSection key={label} delay={i * 0.08} className="text-center">
                <div className="text-3xl sm:text-4xl font-extrabold bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent mb-1">
                  {value}
                </div>
                <div className="text-sm text-white/50">{label}</div>
              </RevealSection>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="py-28 px-5">
        <div className="max-w-6xl mx-auto">
          <RevealSection className="text-center mb-16">
            <p className="text-xs font-semibold text-blue-400 uppercase tracking-widest mb-3">Features</p>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight">
              Everything you need to<br />
              <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                land the role
              </span>
            </h2>
          </RevealSection>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map(({ icon: Icon, title, desc, color }, i) => (
              <RevealSection key={title} delay={i * 0.07}>
                <div className="group h-full rounded-2xl border border-white/8 bg-white/[0.03] hover:bg-white/[0.06] hover:border-white/15 p-6 transition-all duration-300">
                  <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-4 shadow-lg`}>
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <h3 className="font-semibold text-base mb-2">{title}</h3>
                  <p className="text-sm text-white/50 leading-relaxed">{desc}</p>
                </div>
              </RevealSection>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section id="how" className="py-28 px-5 bg-white/[0.02] border-y border-white/5">
        <div className="max-w-5xl mx-auto">
          <RevealSection className="text-center mb-16">
            <p className="text-xs font-semibold text-violet-400 uppercase tracking-widest mb-3">How it works</p>
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              Up and running in{' '}
              <span className="bg-gradient-to-r from-violet-400 to-blue-400 bg-clip-text text-transparent">
                minutes
              </span>
            </h2>
          </RevealSection>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {HOW_IT_WORKS.map(({ step, title, desc }, i) => (
              <RevealSection key={step} delay={i * 0.1}>
                <div className="flex gap-5 p-6 rounded-2xl border border-white/8 bg-white/[0.03]">
                  <div className="text-3xl font-black text-white/10 shrink-0 leading-none mt-0.5">{step}</div>
                  <div>
                    <h3 className="font-semibold mb-1">{title}</h3>
                    <p className="text-sm text-white/50 leading-relaxed">{desc}</p>
                  </div>
                </div>
              </RevealSection>
            ))}
          </div>
        </div>
      </section>

      {/* ── Final CTA ── */}
      <section className="relative py-32 px-5 overflow-hidden">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="absolute inset-0 pointer-events-none"
        >
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] rounded-full bg-blue-600/15 blur-[100px]" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] rounded-full bg-violet-600/15 blur-[80px]" />
        </motion.div>

        <div className="relative max-w-2xl mx-auto text-center">
          <RevealSection>
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5 text-xs font-medium text-emerald-300 mb-8">
              <Shield className="h-3 w-3" />
              Free forever · No hidden fees
            </div>
            <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-5">
              Your next job is{' '}
              <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
                waiting
              </span>
            </h2>
            <p className="text-white/50 text-lg mb-10">
              Join and start tracking opportunities that actually match what you're looking for.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/register">
                <Button size="lg"
                  className="h-13 px-10 bg-gradient-to-r from-blue-500 to-violet-600 hover:from-blue-600 hover:to-violet-700 text-white font-semibold text-base shadow-2xl shadow-blue-500/30 border-0">
                  Create free account
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/login"
                className="text-sm text-white/50 hover:text-white transition-colors underline underline-offset-4">
                Sign in to existing account
              </Link>
            </div>
          </RevealSection>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-white/5 py-8 px-5">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/30">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
              <Briefcase className="h-3 w-3 text-white" />
            </div>
            <span className="font-semibold text-white/60">JobHunt</span>
          </div>
          <span>Built to help you get hired faster.</span>
          <div className="flex items-center gap-5">
            <Link to="/login"    className="hover:text-white transition-colors">Log in</Link>
            <Link to="/register" className="hover:text-white transition-colors">Sign up</Link>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default LandingPage;
