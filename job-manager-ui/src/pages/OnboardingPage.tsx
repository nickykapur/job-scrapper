import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, Upload, Check, ArrowRight, ArrowLeft, FileText, X, Plus } from 'lucide-react';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '../contexts/AuthContext';
import { jobApi } from '../services/api';

const SUPPORTED_COUNTRIES = [
  'Ireland', 'United Kingdom', 'Germany', 'Netherlands', 'Spain',
  'France', 'Portugal', 'Poland', 'Sweden', 'Denmark', 'Norway',
  'Canada', 'United States', 'Australia', 'New Zealand', 'Remote',
];

const MAX_BYTES = 5 * 1024 * 1024;

type Step = 1 | 2 | 3;

interface ParsedProfile {
  exists: boolean;
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  headline?: string;
  summary?: string;
  skills?: string[];
  experience?: any[];
  education?: any[];
  languages?: string[];
  insights?: Record<string, any>;
}

const OnboardingPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();

  const [step, setStep] = useState<Step>(1);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);

  const [profile, setProfile] = useState<ParsedProfile | null>(null);
  const [edited, setEdited] = useState<Partial<ParsedProfile>>({});
  const [derivedKeywords, setDerivedKeywords] = useState<string[]>([]);
  const [country, setCountry] = useState<string>('Ireland');

  const fileRef = useRef<HTMLInputElement>(null);

  // ── Bootstrap: figure out which step the user should resume on ──────────

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [status, profileRes] = await Promise.all([
        jobApi.getOnboardingStatus().catch(() => null),
        jobApi.getCVProfile().catch(() => ({ exists: false })),
      ]);

      if (status?.onboarding_completed) {
        navigate('/', { replace: true });
        return;
      }

      if (profileRes?.exists) {
        setProfile(profileRes);
        setEdited({
          full_name:      profileRes.full_name,
          email:          profileRes.email,
          phone:          profileRes.phone,
          location:       profileRes.location,
          linkedin_url:   profileRes.linkedin_url,
          github_url:     profileRes.github_url,
          portfolio_url:  profileRes.portfolio_url,
          skills:         profileRes.skills || [],
          summary:        profileRes.summary,
        });
        try {
          const kws = await jobApi.getDerivedKeywords();
          setDerivedKeywords(kws.keywords || []);
        } catch {}
        setStep(status?.next_step === 'pick_country' ? 3 : 2);
      } else {
        setStep(1);
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => { loadAll(); }, [loadAll]);

  // ── Step 1: upload CV ───────────────────────────────────────────────────

  const handleFile = async (file: File) => {
    if (!file.name.match(/\.(pdf|docx|txt)$/i)) {
      toast.error('Please upload a PDF, DOCX, or TXT file'); return;
    }
    if (file.size > MAX_BYTES) {
      toast.error('File must be under 5 MB'); return;
    }
    setUploading(true);
    try {
      await jobApi.uploadCV(file);
      toast.success('CV parsed — review the details below.');
      const prof = await jobApi.getCVProfile();
      setProfile(prof);
      setEdited({
        full_name:      prof.full_name,
        email:          prof.email,
        phone:          prof.phone,
        location:       prof.location,
        linkedin_url:   prof.linkedin_url,
        github_url:     prof.github_url,
        portfolio_url:  prof.portfolio_url,
        skills:         prof.skills || [],
        summary:        prof.summary,
      });
      try {
        const kws = await jobApi.getDerivedKeywords();
        setDerivedKeywords(kws.keywords || []);
      } catch {}
      setStep(2);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  // ── Step 2: save edits ──────────────────────────────────────────────────

  const saveProfileEdits = async () => {
    setSaving(true);
    try {
      await jobApi.updateCVProfile(edited);
      const prof = await jobApi.getCVProfile();
      setProfile(prof);
      const kws = await jobApi.getDerivedKeywords();
      setDerivedKeywords(kws.keywords || []);
      toast.success('Profile updated');
      setStep(3);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  // ── Step 3: save scraper config + complete onboarding ───────────────────

  const finishOnboarding = async () => {
    setSaving(true);
    try {
      await jobApi.saveScraperConfig(country);
      toast.success(`We'll scrape ${country} jobs for you daily.`);
      await refreshUser();
      navigate('/', { replace: true });
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to save scraper config');
    } finally {
      setSaving(false);
    }
  };

  // ── Render helpers ──────────────────────────────────────────────────────

  const StepDot = ({ n, label }: { n: Step; label: string }) => {
    const isActive = step === n;
    const isDone = step > n;
    return (
      <div className="flex items-center gap-2">
        <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold
          ${isDone ? 'bg-emerald-500 text-white' : isActive ? 'bg-blue-500 text-white' : 'bg-muted text-muted-foreground'}`}>
          {isDone ? <Check className="h-4 w-4" /> : n}
        </div>
        <span className={`text-sm ${isActive ? 'font-semibold text-foreground' : 'text-muted-foreground'}`}>
          {label}
        </span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30 py-10 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8 text-center">
          <div className="text-2xl font-extrabold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
            JobHunt
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Hi {user?.full_name || user?.username} — let's set up your personalised job feed.
          </p>
        </div>

        {/* Stepper */}
        <div className="flex items-center justify-center gap-6 mb-8">
          <StepDot n={1} label="Upload CV" />
          <div className="h-px w-12 bg-border" />
          <StepDot n={2} label="Review" />
          <div className="h-px w-12 bg-border" />
          <StepDot n={3} label="Country" />
        </div>

        {/* Card */}
        <div className="rounded-2xl border bg-card shadow-sm p-8">
          {step === 1 && (
            <UploadStep
              onFile={handleFile}
              fileRef={fileRef}
              uploading={uploading}
            />
          )}

          {step === 2 && profile && (
            <ReviewStep
              profile={profile}
              edited={edited}
              setEdited={setEdited}
              onBack={() => setStep(1)}
              onContinue={saveProfileEdits}
              saving={saving}
            />
          )}

          {step === 3 && (
            <CountryStep
              country={country}
              setCountry={setCountry}
              keywords={derivedKeywords}
              onBack={() => setStep(2)}
              onFinish={finishOnboarding}
              saving={saving}
            />
          )}
        </div>
      </div>
    </div>
  );
};

// ── Step 1 ────────────────────────────────────────────────────────────────

const UploadStep: React.FC<{
  onFile: (f: File) => void;
  fileRef: React.RefObject<HTMLInputElement>;
  uploading: boolean;
}> = ({ onFile, fileRef, uploading }) => {
  const [drag, setDrag] = useState(false);
  return (
    <div>
      <h2 className="text-xl font-bold mb-1">Upload your CV</h2>
      <p className="text-sm text-muted-foreground mb-6">
        PDF, DOCX, or TXT (max 5 MB). We'll auto-extract your profile.
      </p>

      <div
        onClick={() => !uploading && fileRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={e => {
          e.preventDefault();
          setDrag(false);
          const file = e.dataTransfer.files[0];
          if (file) onFile(file);
        }}
        className={`rounded-xl border-2 border-dashed p-10 text-center cursor-pointer transition-all
          ${drag ? 'border-blue-500 bg-blue-500/5' : 'border-border hover:border-blue-400 hover:bg-muted/30'}`}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.docx,.txt"
          style={{ display: 'none' }}
          onChange={e => e.target.files?.[0] && onFile(e.target.files[0])}
        />
        {uploading ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            <p className="text-sm text-muted-foreground">Parsing your CV with AI… this takes 10–20 seconds.</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center">
              <Upload className="h-6 w-6 text-blue-500" />
            </div>
            <p className="font-semibold">Drop your CV or click to browse</p>
            <p className="text-xs text-muted-foreground">PDF, DOCX, TXT · up to 5 MB</p>
          </div>
        )}
      </div>
    </div>
  );
};

// ── Step 2 ────────────────────────────────────────────────────────────────

const ReviewStep: React.FC<{
  profile: ParsedProfile;
  edited: Partial<ParsedProfile>;
  setEdited: (x: Partial<ParsedProfile>) => void;
  onBack: () => void;
  onContinue: () => void;
  saving: boolean;
}> = ({ profile, edited, setEdited, onBack, onContinue, saving }) => {
  const field = (k: keyof ParsedProfile, label: string, type: string = 'text') => (
    <div>
      <label className="text-xs font-semibold text-muted-foreground mb-1 block">{label}</label>
      <Input
        type={type}
        value={(edited[k] as any) ?? ''}
        onChange={e => setEdited({ ...edited, [k]: e.target.value })}
        className="bg-muted/30 h-10"
      />
    </div>
  );

  const skills = (edited.skills as string[]) || [];
  const [skillInput, setSkillInput] = useState('');

  return (
    <div>
      <h2 className="text-xl font-bold mb-1">Review your profile</h2>
      <p className="text-sm text-muted-foreground mb-6">
        Confirm what we extracted. These fields drive your job matching.
      </p>

      <div className="grid grid-cols-2 gap-4 mb-6">
        {field('full_name', 'Full name')}
        {field('email', 'Email', 'email')}
        {field('phone', 'Phone')}
        {field('location', 'Location')}
        {field('linkedin_url', 'LinkedIn URL')}
        {field('github_url', 'GitHub URL')}
      </div>

      <div className="mb-6">
        <label className="text-xs font-semibold text-muted-foreground mb-1 block">Skills</label>
        <div className="flex flex-wrap gap-1.5 mb-2">
          {skills.map((s, i) => (
            <span key={`${s}-${i}`} className="inline-flex items-center gap-1 text-xs rounded-full bg-blue-500/10 text-blue-600 border border-blue-500/30 pl-2.5 pr-1.5 py-1 font-medium">
              {s}
              <button
                type="button"
                onClick={() => setEdited({ ...edited, skills: skills.filter((_, idx) => idx !== i) })}
                className="hover:text-destructive"
              ><X className="h-3 w-3" /></button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <Input
            placeholder="Add a skill"
            value={skillInput}
            onChange={e => setSkillInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter') {
                e.preventDefault();
                const v = skillInput.trim();
                if (v && !skills.includes(v)) setEdited({ ...edited, skills: [...skills, v] });
                setSkillInput('');
              }
            }}
            className="bg-muted/30 h-10 flex-1"
          />
          <Button
            variant="outline"
            size="sm"
            className="h-10"
            onClick={() => {
              const v = skillInput.trim();
              if (v && !skills.includes(v)) setEdited({ ...edited, skills: [...skills, v] });
              setSkillInput('');
            }}
          ><Plus className="h-4 w-4" /></Button>
        </div>
      </div>

      {profile.insights && (
        <div className="rounded-lg border border-border/60 bg-muted/20 p-4 mb-6">
          <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
            Auto-extracted insights
          </div>
          <div className="grid grid-cols-2 gap-y-1.5 gap-x-4 text-sm">
            <InsightRow label="Years of experience" value={profile.insights.years_of_experience} />
            <InsightRow label="Seniority" value={profile.insights.seniority} />
            <InsightRow label="Current title" value={profile.insights.current_title} />
            <InsightRow label="Current company" value={profile.insights.current_company} />
            <InsightRow
              label="Target roles"
              value={Array.isArray(profile.insights.target_roles) ? profile.insights.target_roles.join(', ') : profile.insights.target_roles}
            />
            <InsightRow
              label="Primary tech stack"
              value={Array.isArray(profile.insights.primary_tech_stack) ? profile.insights.primary_tech_stack.join(', ') : profile.insights.primary_tech_stack}
            />
          </div>
          <p className="text-xs text-muted-foreground mt-3">
            These drive your scraper keywords. Re-upload your CV later if anything is wrong.
          </p>
        </div>
      )}

      <div className="flex justify-between">
        <Button variant="outline" onClick={onBack} disabled={saving}>
          <ArrowLeft className="h-4 w-4 mr-1" /> Re-upload CV
        </Button>
        <Button onClick={onContinue} disabled={saving} className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
          Looks good, continue <ArrowRight className="h-4 w-4 ml-1" />
        </Button>
      </div>
    </div>
  );
};

const InsightRow: React.FC<{ label: string; value?: any }> = ({ label, value }) => (
  <>
    <div className="text-xs text-muted-foreground">{label}</div>
    <div className="text-sm">{value ?? <span className="text-muted-foreground italic">not detected</span>}</div>
  </>
);

// ── Step 3 ────────────────────────────────────────────────────────────────

const CountryStep: React.FC<{
  country: string;
  setCountry: (c: string) => void;
  keywords: string[];
  onBack: () => void;
  onFinish: () => void;
  saving: boolean;
}> = ({ country, setCountry, keywords, onBack, onFinish, saving }) => {
  return (
    <div>
      <h2 className="text-xl font-bold mb-1">Pick your country</h2>
      <p className="text-sm text-muted-foreground mb-6">
        We'll scrape jobs every day in this country and match them against your profile.
      </p>

      <div className="mb-6">
        <label className="text-xs font-semibold text-muted-foreground mb-1 block">Country</label>
        <select
          value={country}
          onChange={e => setCountry(e.target.value)}
          className="w-full h-11 rounded-md border border-border bg-background px-3 text-sm"
        >
          {SUPPORTED_COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      <div className="rounded-lg border border-border/60 bg-muted/20 p-4 mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
            Keywords we'll search for
          </div>
          <span className="text-xs text-muted-foreground italic">auto-derived from your CV</span>
        </div>
        {keywords.length === 0 ? (
          <div className="text-sm text-amber-600">
            No keywords could be derived. Go back and add target roles or tech stack.
          </div>
        ) : (
          <div className="flex flex-wrap gap-1.5">
            {keywords.map(k => (
              <span
                key={k}
                className="text-xs rounded-full bg-emerald-500/10 text-emerald-600 border border-emerald-500/30 px-2.5 py-1 font-medium"
              >
                {k}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="flex justify-between">
        <Button variant="outline" onClick={onBack} disabled={saving}>
          <ArrowLeft className="h-4 w-4 mr-1" /> Back
        </Button>
        <Button
          onClick={onFinish}
          disabled={saving || keywords.length === 0}
          className="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white"
        >
          {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Check className="h-4 w-4 mr-1" />}
          Finish setup
        </Button>
      </div>
    </div>
  );
};

export default OnboardingPage;
