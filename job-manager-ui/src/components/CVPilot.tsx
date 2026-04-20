import React, { useState, useEffect, useRef, useCallback } from 'react';
import toast from 'react-hot-toast';
import {
  Upload,
  FileText,
  Check,
  ChevronRight,
  Mail,
  Phone,
  MapPin,
  Linkedin,
  Github,
  Link,
  Code2,
  ArrowLeft,
  RefreshCw,
  Trash2,
  AlertCircle,
  User,
  Briefcase,
  GraduationCap,
  Globe,
  Award,
  TrendingUp,
  Target,
  Building2,
} from 'lucide-react';
import { jobApi } from '../services/api';

// ── Types ─────────────────────────────────────────────────────────────────────

interface CVExperience {
  company?: string | null;
  title?: string | null;
  start?: string | null;
  end?: string | null;
  is_current?: boolean;
  location?: string | null;
  employment_type?: string | null;
  bullets?: string[];
}

interface CVEducation {
  school?: string | null;
  degree?: string | null;
  field?: string | null;
  start?: string | null;
  end?: string | null;
  gpa?: string | null;
}

interface CVLanguage {
  name?: string;
  level?: string | null;
}

interface CVInsights {
  years_of_experience?: number | null;
  current_title?: string | null;
  current_company?: string | null;
  seniority?: string | null;
  target_roles?: string[];
  industries?: string[];
  top_skills?: string[];
  highest_education?: string | null;
  management_experience?: boolean;
  direct_reports_max?: number | null;
  remote_experience?: boolean;
  primary_tech_stack?: string[];
  notable_achievements?: string[];
  availability?: string | null;
  work_authorization?: string | null;
}

interface CVData {
  exists: boolean;
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  headline?: string;
  skills?: string[];
  summary?: string;
  experience?: CVExperience[];
  education?: CVEducation[];
  languages?: CVLanguage[];
  certifications?: string[];
  insights?: CVInsights;
  parse_model?: string | null;
  parse_input_tokens?: number | null;
  parse_output_tokens?: number | null;
  cv_filename?: string;
  uploaded_at?: string;
}

type Step = 1 | 2;

// ── Helpers ───────────────────────────────────────────────────────────────────

const ACCEPTED = '.pdf,.docx,.txt';
const MAX_BYTES = 5 * 1024 * 1024;

function fmtDate(iso?: string) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' });
}

// ── Sub-components ────────────────────────────────────────────────────────────

const StepBadge = ({ n, active, done }: { n: number; active: boolean; done: boolean }) => (
  <div
    style={{
      width: 32,
      height: 32,
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontWeight: 700,
      fontSize: 13,
      flexShrink: 0,
      background: done
        ? 'linear-gradient(135deg,#22c55e,#16a34a)'
        : active
        ? 'linear-gradient(135deg,#3b82f6,#6366f1)'
        : 'rgba(255,255,255,0.08)',
      color: done || active ? '#fff' : 'rgba(255,255,255,0.35)',
      border: active ? '2px solid rgba(99,102,241,0.5)' : '2px solid transparent',
      transition: 'all 0.2s',
    }}
  >
    {done ? <Check size={15} strokeWidth={2.5} /> : n}
  </div>
);

const InfoRow = ({
  icon: Icon,
  label,
  value,
  href,
}: {
  icon: React.ElementType;
  label: string;
  value?: string;
  href?: string;
}) => {
  if (!value) return null;
  const content = (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
      <div
        style={{
          width: 34,
          height: 34,
          borderRadius: 10,
          background: 'rgba(99,102,241,0.12)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <Icon size={15} color="#818cf8" />
      </div>
      <div>
        <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', margin: 0, marginBottom: 2 }}>{label}</p>
        <p
          style={{
            fontSize: 13,
            color: href ? '#93c5fd' : 'rgba(255,255,255,0.85)',
            margin: 0,
            wordBreak: 'break-all',
            textDecoration: href ? 'underline' : 'none',
          }}
        >
          {value}
        </p>
      </div>
    </div>
  );

  if (href) {
    return (
      <a href={href} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
        {content}
      </a>
    );
  }
  return <div>{content}</div>;
};

const SkillTag = ({ label }: { label: string }) => (
  <span
    style={{
      display: 'inline-block',
      padding: '4px 11px',
      borderRadius: 20,
      fontSize: 12,
      fontWeight: 600,
      background: 'rgba(59,130,246,0.12)',
      color: '#93c5fd',
      border: '1px solid rgba(59,130,246,0.22)',
      letterSpacing: 0.2,
    }}
  >
    {label}
  </span>
);

const Card = ({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) => (
  <div
    style={{
      borderRadius: 18,
      border: '1px solid rgba(255,255,255,0.08)',
      background: 'rgba(255,255,255,0.03)',
      padding: '24px',
      ...style,
    }}
  >
    {children}
  </div>
);

const SectionHeading = ({ icon: Icon, title }: { icon: React.ElementType; title: string }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
    <Icon size={15} color="#6366f1" />
    <p
      style={{
        fontSize: 11,
        fontWeight: 700,
        letterSpacing: 1,
        textTransform: 'uppercase',
        color: 'rgba(255,255,255,0.45)',
        margin: 0,
      }}
    >
      {title}
    </p>
  </div>
);

// ── Main Component ────────────────────────────────────────────────────────────

export const CVPilot: React.FC = () => {
  const [step, setStep] = useState<Step>(1);
  const [cvData, setCvData] = useState<CVData>({ exists: false });
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const loadProfile = useCallback(async () => {
    try {
      const data = await jobApi.getCVProfile();
      setCvData(data);
      if (data.exists) setStep(2);
    } catch {
      toast.error('Failed to load CV profile');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const handleFile = async (file: File) => {
    if (!file.name.match(/\.(pdf|docx|txt)$/i)) {
      toast.error('Please upload a PDF, DOCX, or TXT file');
      return;
    }
    if (file.size > MAX_BYTES) {
      toast.error('File too large — max 5 MB');
      return;
    }
    setUploading(true);
    try {
      await jobApi.uploadCV(file);
      toast.success('CV parsed successfully!');
      await loadProfile();
      setStep(2);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleDelete = async () => {
    if (!confirm('Delete your CV data? This cannot be undone.')) return;
    try {
      await jobApi.deleteCV();
      setCvData({ exists: false });
      setStep(1);
      toast.success('CV data removed');
    } catch {
      toast.error('Delete failed');
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 240 }}>
        <div className="animate-spin" style={{ width: 28, height: 28, borderRadius: '50%', border: '3px solid rgba(99,102,241,0.3)', borderTopColor: '#6366f1' }} />
      </div>
    );
  }

  // ── Stepper header ─────────────────────────────────────────────────────────
  const steps: { label: string; sub: string }[] = [
    { label: 'Upload CV', sub: 'PDF, DOCX or TXT' },
    { label: 'Review Extraction', sub: 'Verify parsed data' },
  ];

  const StepperHeader = () => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 0, marginBottom: 32 }}>
      {steps.map((s, i) => {
        const n = (i + 1) as Step;
        const active = step === n;
        const done = step > n;
        return (
          <React.Fragment key={n}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: i < steps.length - 1 ? undefined : 1 }}>
              <StepBadge n={n} active={active} done={done} />
              <div>
                <p style={{ margin: 0, fontSize: 13, fontWeight: active ? 700 : 500, color: active ? '#fff' : done ? 'rgba(255,255,255,0.6)' : 'rgba(255,255,255,0.3)' }}>
                  {s.label}
                </p>
                <p style={{ margin: 0, fontSize: 11, color: 'rgba(255,255,255,0.3)' }}>{s.sub}</p>
              </div>
            </div>
            {i < steps.length - 1 && (
              <div style={{ flex: 1, height: 1, background: step > n + 1 ? '#22c55e' : 'rgba(255,255,255,0.1)', margin: '0 16px', transition: 'background 0.3s' }} />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );

  // ── Step 1 — Upload ────────────────────────────────────────────────────────
  const Step1 = () => (
    <div style={{ maxWidth: 560, margin: '0 auto' }}>
      <Card style={{ textAlign: 'center', marginBottom: 20 }}>
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: 18,
            background: 'linear-gradient(135deg,rgba(59,130,246,0.2),rgba(99,102,241,0.2))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
          }}
        >
          <FileText size={28} color="#818cf8" />
        </div>
        <h2 style={{ margin: '0 0 8px', fontSize: 20, fontWeight: 700 }}>Upload your CV</h2>
        <p style={{ margin: 0, fontSize: 14, color: 'rgba(255,255,255,0.5)', lineHeight: 1.6 }}>
          We'll extract your contact info, skills and experience automatically.<br />
          Supported: <strong style={{ color: 'rgba(255,255,255,0.7)' }}>PDF · DOCX · TXT</strong> (max 5 MB)
        </p>
      </Card>

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => !uploading && fileRef.current?.click()}
        style={{
          borderRadius: 18,
          border: `2px dashed ${dragOver ? '#6366f1' : 'rgba(255,255,255,0.15)'}`,
          background: dragOver ? 'rgba(99,102,241,0.07)' : uploading ? 'rgba(99,102,241,0.04)' : 'rgba(255,255,255,0.02)',
          padding: '48px 24px',
          textAlign: 'center',
          cursor: uploading ? 'not-allowed' : 'pointer',
          transition: 'all 0.2s',
        }}
      >
        <input
          ref={fileRef}
          type="file"
          accept={ACCEPTED}
          style={{ display: 'none' }}
          onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
          disabled={uploading}
        />
        {uploading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
            <div
              className="animate-spin"
              style={{ width: 44, height: 44, borderRadius: '50%', border: '3px solid rgba(99,102,241,0.2)', borderTopColor: '#6366f1' }}
            />
            <p style={{ margin: 0, fontSize: 14, color: '#818cf8', fontWeight: 600 }}>Parsing your CV…</p>
            <p style={{ margin: 0, fontSize: 12, color: 'rgba(255,255,255,0.35)' }}>Extracting skills, contact info and more</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
            <div
              style={{
                width: 52,
                height: 52,
                borderRadius: 14,
                background: 'rgba(99,102,241,0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Upload size={24} color="#818cf8" />
            </div>
            <div>
              <p style={{ margin: '0 0 4px', fontSize: 15, fontWeight: 600 }}>Drop file here</p>
              <p style={{ margin: 0, fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>or click to browse</p>
            </div>
          </div>
        )}
      </div>

      {/* If CV already exists, offer to skip */}
      {cvData.exists && (
        <button
          onClick={() => setStep(2)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            margin: '16px auto 0',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'rgba(255,255,255,0.4)',
            fontSize: 13,
          }}
        >
          <ChevronRight size={14} />
          Skip — view previously extracted data
        </button>
      )}
    </div>
  );

  // ── Step 2 — Results ───────────────────────────────────────────────────────
  const Step2 = () => {
    const d = cvData;
    const skills = d.skills || [];
    const hasContact = d.email || d.phone || d.location;
    const hasLinks = d.linkedin_url || d.github_url || d.portfolio_url;

    return (
      <div style={{ maxWidth: 720, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Status banner */}
        <div
          style={{
            borderRadius: 14,
            background: 'linear-gradient(135deg,rgba(34,197,94,0.1),rgba(16,185,129,0.08))',
            border: '1px solid rgba(34,197,94,0.2)',
            padding: '14px 18px',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
          }}
        >
          <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'rgba(34,197,94,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <Check size={16} color="#22c55e" />
          </div>
          <div style={{ flex: 1 }}>
            <p style={{ margin: 0, fontSize: 13, fontWeight: 700, color: '#4ade80' }}>Extraction complete</p>
            {d.cv_filename && (
              <p style={{ margin: '2px 0 0', fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>
                {d.cv_filename}
                {d.uploaded_at && ` · uploaded ${fmtDate(d.uploaded_at)}`}
              </p>
            )}
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={() => setStep(1)}
              title="Re-upload CV"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 5,
                padding: '6px 12px',
                borderRadius: 8,
                border: '1px solid rgba(255,255,255,0.12)',
                background: 'rgba(255,255,255,0.06)',
                color: 'rgba(255,255,255,0.7)',
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <RefreshCw size={12} />
              Replace
            </button>
            <button
              onClick={handleDelete}
              title="Delete CV data"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 5,
                padding: '6px 12px',
                borderRadius: 8,
                border: '1px solid rgba(239,68,68,0.2)',
                background: 'rgba(239,68,68,0.06)',
                color: '#f87171',
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <Trash2 size={12} />
              Delete
            </button>
          </div>
        </div>

        {/* Personal info */}
        <Card>
          <SectionHeading icon={User} title="Personal Info" />
          {d.full_name && (
            <p style={{ fontSize: 20, fontWeight: 700, margin: '0 0 16px' }}>{d.full_name}</p>
          )}
          {hasContact || hasLinks ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(240px,1fr))', gap: 14 }}>
              <InfoRow icon={Mail} label="Email" value={d.email} href={d.email ? `mailto:${d.email}` : undefined} />
              <InfoRow icon={Phone} label="Phone" value={d.phone} />
              <InfoRow icon={MapPin} label="Location" value={d.location} />
              <InfoRow icon={Linkedin} label="LinkedIn" value={d.linkedin_url} href={d.linkedin_url} />
              <InfoRow icon={Github} label="GitHub" value={d.github_url} href={d.github_url} />
              <InfoRow icon={Link} label="Portfolio" value={d.portfolio_url} href={d.portfolio_url} />
            </div>
          ) : (
            <EmptyNote text="No contact details extracted. The CV may be image-based or have unusual formatting." />
          )}
        </Card>

        {/* Skills */}
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
            <SectionHeading icon={Code2} title="Skills" />
            {skills.length > 0 && (
              <span
                style={{
                  marginLeft: 'auto',
                  fontSize: 11,
                  fontWeight: 700,
                  padding: '3px 10px',
                  borderRadius: 20,
                  background: 'rgba(99,102,241,0.15)',
                  color: '#818cf8',
                  border: '1px solid rgba(99,102,241,0.25)',
                }}
              >
                {skills.length} found
              </span>
            )}
          </div>
          {skills.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {skills.map(s => <SkillTag key={s} label={s} />)}
            </div>
          ) : (
            <EmptyNote text="No recognisable skills found. Skills are matched against a built-in keyword list." />
          )}
        </Card>

        {/* Summary */}
        {d.summary && (
          <Card>
            <SectionHeading icon={FileText} title="Summary" />
            <p style={{ margin: 0, fontSize: 13, color: 'rgba(255,255,255,0.75)', lineHeight: 1.7 }}>{d.summary}</p>
          </Card>
        )}

        {/* AI Insights */}
        {d.insights && Object.keys(d.insights).length > 0 && <InsightsCard insights={d.insights} />}

        {/* Experience */}
        {d.experience && d.experience.length > 0 && <ExperienceCard items={d.experience} />}

        {/* Education */}
        {d.education && d.education.length > 0 && <EducationCard items={d.education} />}

        {/* Languages + Certifications */}
        {((d.languages && d.languages.length > 0) || (d.certifications && d.certifications.length > 0)) && (
          <LangCertCard languages={d.languages || []} certifications={d.certifications || []} />
        )}

        {/* Auto-apply hint */}
        <div
          style={{
            borderRadius: 14,
            border: '1px solid rgba(99,102,241,0.2)',
            background: 'rgba(99,102,241,0.06)',
            padding: '14px 18px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: 12,
          }}
        >
          <AlertCircle size={15} color="#818cf8" style={{ flexShrink: 0, marginTop: 2 }} />
          <div style={{ flex: 1 }}>
            <p style={{ margin: '0 0 3px', fontSize: 13, fontWeight: 600, color: '#a5b4fc' }}>
              Auto-Apply Ready
            </p>
            <p style={{ margin: 0, fontSize: 12, color: 'rgba(255,255,255,0.4)', lineHeight: 1.6 }}>
              Your parsed profile is stored and will be used to pre-fill applications on supported job boards.
              {d.parse_model && (
                <span> Parsed by <code style={{ color: '#a5b4fc' }}>{d.parse_model}</code>
                  {d.parse_input_tokens && d.parse_output_tokens ? (
                    <> · {d.parse_input_tokens.toLocaleString()} in / {d.parse_output_tokens.toLocaleString()} out tokens</>
                  ) : null}
                </span>
              )}
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ padding: '4px 0' }}>
      <StepperHeader />
      {step === 1 ? <Step1 /> : <Step2 />}
    </div>
  );
};

// ── Tiny helper ───────────────────────────────────────────────────────────────
const EmptyNote = ({ text }: { text: string }) => (
  <p style={{ margin: 0, fontSize: 13, color: 'rgba(255,255,255,0.3)', fontStyle: 'italic' }}>{text}</p>
);

// ── Rich display cards ────────────────────────────────────────────────────────

const Stat = ({ label, value, accent }: { label: string; value: React.ReactNode; accent?: string }) => (
  <div
    style={{
      borderRadius: 12,
      border: '1px solid rgba(255,255,255,0.08)',
      background: 'rgba(255,255,255,0.03)',
      padding: '12px 14px',
      minWidth: 140,
    }}
  >
    <p style={{ margin: 0, fontSize: 10, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', color: 'rgba(255,255,255,0.35)' }}>
      {label}
    </p>
    <p style={{ margin: '4px 0 0', fontSize: 15, fontWeight: 700, color: accent || '#fff' }}>{value}</p>
  </div>
);

const Chip = ({ label, tone = 'indigo' }: { label: string; tone?: 'indigo' | 'emerald' | 'amber' | 'rose' }) => {
  const tones = {
    indigo: { bg: 'rgba(99,102,241,0.12)', fg: '#a5b4fc', bd: 'rgba(99,102,241,0.25)' },
    emerald: { bg: 'rgba(16,185,129,0.12)', fg: '#6ee7b7', bd: 'rgba(16,185,129,0.25)' },
    amber: { bg: 'rgba(245,158,11,0.12)', fg: '#fcd34d', bd: 'rgba(245,158,11,0.25)' },
    rose: { bg: 'rgba(244,63,94,0.12)', fg: '#fda4af', bd: 'rgba(244,63,94,0.25)' },
  }[tone];
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '4px 11px',
        borderRadius: 20,
        fontSize: 12,
        fontWeight: 600,
        background: tones.bg,
        color: tones.fg,
        border: `1px solid ${tones.bd}`,
      }}
    >
      {label}
    </span>
  );
};

const InsightsCard: React.FC<{ insights: CVInsights }> = ({ insights }) => {
  const i = insights;
  const yoe = i.years_of_experience != null ? `${i.years_of_experience} yrs` : null;
  return (
    <div
      style={{
        borderRadius: 18,
        border: '1px solid rgba(99,102,241,0.25)',
        background: 'linear-gradient(135deg,rgba(99,102,241,0.08),rgba(59,130,246,0.04))',
        padding: '24px',
      }}
    >
      <SectionHeading icon={TrendingUp} title="AI Insights" />
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginBottom: i.target_roles?.length || i.industries?.length ? 18 : 0 }}>
        {yoe && <Stat label="Experience" value={yoe} accent="#a5b4fc" />}
        {i.seniority && <Stat label="Seniority" value={i.seniority} accent="#a5b4fc" />}
        {i.current_title && <Stat label="Current Role" value={i.current_title} />}
        {i.current_company && <Stat label="Current Company" value={i.current_company} />}
        {i.highest_education && <Stat label="Education" value={i.highest_education} />}
        {i.management_experience && (
          <Stat
            label="Management"
            value={i.direct_reports_max ? `Yes · up to ${i.direct_reports_max}` : 'Yes'}
            accent="#6ee7b7"
          />
        )}
        {i.remote_experience && <Stat label="Remote" value="Yes" accent="#6ee7b7" />}
        {i.availability && <Stat label="Availability" value={i.availability} />}
        {i.work_authorization && <Stat label="Work Auth" value={i.work_authorization} />}
      </div>

      {i.target_roles && i.target_roles.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <Target size={13} color="#818cf8" />
            <p style={{ margin: 0, fontSize: 11, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', color: 'rgba(255,255,255,0.45)' }}>
              Best-fit Roles
            </p>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {i.target_roles.map(r => <Chip key={r} label={r} tone="indigo" />)}
          </div>
        </div>
      )}

      {i.industries && i.industries.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <Building2 size={13} color="#818cf8" />
            <p style={{ margin: 0, fontSize: 11, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', color: 'rgba(255,255,255,0.45)' }}>
              Industries
            </p>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {i.industries.map(x => <Chip key={x} label={x} tone="emerald" />)}
          </div>
        </div>
      )}

      {i.primary_tech_stack && i.primary_tech_stack.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <p style={{ margin: '0 0 8px', fontSize: 11, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', color: 'rgba(255,255,255,0.45)' }}>
            Primary Tech Stack
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {i.primary_tech_stack.map(x => <Chip key={x} label={x} tone="amber" />)}
          </div>
        </div>
      )}

      {i.notable_achievements && i.notable_achievements.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <p style={{ margin: '0 0 8px', fontSize: 11, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', color: 'rgba(255,255,255,0.45)' }}>
            Notable Achievements
          </p>
          <ul style={{ margin: 0, paddingLeft: 18, color: 'rgba(255,255,255,0.75)', fontSize: 13, lineHeight: 1.7 }}>
            {i.notable_achievements.map((a, idx) => <li key={idx}>{a}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
};

const formatDateRange = (start?: string | null, end?: string | null, isCurrent?: boolean) => {
  const s = start || '';
  const e = isCurrent ? 'Present' : (end || '');
  if (!s && !e) return '';
  return `${s}${s && e ? ' — ' : ''}${e}`;
};

const ExperienceCard: React.FC<{ items: CVExperience[] }> = ({ items }) => (
  <Card>
    <SectionHeading icon={Briefcase} title="Experience" />
    <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
      {items.map((e, idx) => {
        const range = formatDateRange(e.start, e.end, e.is_current);
        return (
          <div
            key={idx}
            style={{
              paddingLeft: 16,
              borderLeft: '2px solid rgba(99,102,241,0.3)',
              position: 'relative',
            }}
          >
            <div
              style={{
                position: 'absolute',
                left: -6,
                top: 4,
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: e.is_current ? '#22c55e' : '#6366f1',
                boxShadow: e.is_current ? '0 0 0 3px rgba(34,197,94,0.2)' : 'none',
              }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 6, alignItems: 'baseline' }}>
              <p style={{ margin: 0, fontSize: 15, fontWeight: 700 }}>
                {e.title || 'Role'}
                {e.company && <span style={{ color: 'rgba(255,255,255,0.5)', fontWeight: 500 }}> · {e.company}</span>}
              </p>
              {range && (
                <span style={{ fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.45)' }}>{range}</span>
              )}
            </div>
            {(e.location || e.employment_type) && (
              <p style={{ margin: '4px 0 0', fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>
                {e.location}
                {e.location && e.employment_type && ' · '}
                {e.employment_type}
              </p>
            )}
            {e.bullets && e.bullets.length > 0 && (
              <ul style={{ margin: '8px 0 0', paddingLeft: 18, color: 'rgba(255,255,255,0.72)', fontSize: 13, lineHeight: 1.7 }}>
                {e.bullets.map((b, i) => <li key={i}>{b}</li>)}
              </ul>
            )}
          </div>
        );
      })}
    </div>
  </Card>
);

const EducationCard: React.FC<{ items: CVEducation[] }> = ({ items }) => (
  <Card>
    <SectionHeading icon={GraduationCap} title="Education" />
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {items.map((ed, idx) => {
        const range = formatDateRange(ed.start, ed.end);
        const headline = [ed.degree, ed.field].filter(Boolean).join(' · ');
        return (
          <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 6, alignItems: 'baseline' }}>
            <div>
              <p style={{ margin: 0, fontSize: 14, fontWeight: 700 }}>{ed.school || 'School'}</p>
              {headline && (
                <p style={{ margin: '2px 0 0', fontSize: 13, color: 'rgba(255,255,255,0.6)' }}>{headline}</p>
              )}
              {ed.gpa && (
                <p style={{ margin: '2px 0 0', fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>GPA: {ed.gpa}</p>
              )}
            </div>
            {range && (
              <span style={{ fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.45)' }}>{range}</span>
            )}
          </div>
        );
      })}
    </div>
  </Card>
);

const LangCertCard: React.FC<{ languages: CVLanguage[]; certifications: string[] }> = ({ languages, certifications }) => (
  <div style={{ display: 'grid', gridTemplateColumns: languages.length && certifications.length ? '1fr 1fr' : '1fr', gap: 16 }}>
    {languages.length > 0 && (
      <Card>
        <SectionHeading icon={Globe} title="Languages" />
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {languages.map((l, idx) => (
            <Chip
              key={idx}
              label={l.level ? `${l.name} · ${l.level}` : (l.name || '')}
              tone="emerald"
            />
          ))}
        </div>
      </Card>
    )}
    {certifications.length > 0 && (
      <Card>
        <SectionHeading icon={Award} title="Certifications" />
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {certifications.map((c, idx) => <Chip key={idx} label={c} tone="amber" />)}
        </div>
      </Card>
    )}
  </div>
);

export default CVPilot;
