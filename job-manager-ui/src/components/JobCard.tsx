import React, { useState } from 'react';
import { Button, makeStyles, tokens, Tooltip } from '@fluentui/react-components';
import {
  CheckmarkCircleFilled,
  DismissCircleFilled,
  ArrowRightRegular,
  BriefcaseRegular,
  PaintBrushRegular,
  VideoRegular,
  HeadphonesRegular,
  CodeRegular,
  MoneyRegular,
  ShieldRegular,
  LocationRegular,
  ClockRegular,
  DismissRegular,
  BuildingRegular,
  FlashRegular,
} from '@fluentui/react-icons';
import type { Job } from '../types';
import { getCountryFromLocation } from '../utils/countryUtils';
import { jobApi } from '../services/api';
import toast from 'react-hot-toast';

interface JobCardProps {
  job: Job;
  onMarkApplied: (jobId: string) => void;
  onRejectJob: (jobId: string) => void;
  onRefreshJobs?: () => void;
  isUpdating?: boolean;
}

type JobTypeKey = string;

const TYPE_CONFIG: Record<string, { label: string; Icon: React.ElementType; accent: string; dim: string }> = {
  sales:            { label: 'Sales',            Icon: BriefcaseRegular,  accent: '#f59e0b', dim: 'rgba(245,158,11,0.12)' },
  painter:          { label: 'Painter',           Icon: PaintBrushRegular, accent: '#60a5fa', dim: 'rgba(96,165,250,0.12)' },
  painting:         { label: 'Painter',           Icon: PaintBrushRegular, accent: '#60a5fa', dim: 'rgba(96,165,250,0.12)' },
  customer_service: { label: 'Customer Service',  Icon: HeadphonesRegular, accent: '#34d399', dim: 'rgba(52,211,153,0.12)' },
  customer_support: { label: 'Customer Support',  Icon: HeadphonesRegular, accent: '#34d399', dim: 'rgba(52,211,153,0.12)' },
  media_production: { label: 'Media Production',  Icon: VideoRegular,      accent: '#a78bfa', dim: 'rgba(167,139,250,0.12)' },
  media:            { label: 'Media',             Icon: VideoRegular,      accent: '#a78bfa', dim: 'rgba(167,139,250,0.12)' },
  software:         { label: 'Software',          Icon: CodeRegular,       accent: '#818cf8', dim: 'rgba(129,140,248,0.12)' },
  hr:               { label: 'HR',                Icon: BriefcaseRegular,  accent: '#f472b6', dim: 'rgba(244,114,182,0.12)' },
  finance:          { label: 'Finance',           Icon: MoneyRegular,      accent: '#2dd4bf', dim: 'rgba(45,212,191,0.12)' },
  aml:              { label: 'AML / Compliance',  Icon: ShieldRegular,     accent: '#f87171', dim: 'rgba(248,113,113,0.12)' },
  compliance:       { label: 'Compliance',        Icon: ShieldRegular,     accent: '#f87171', dim: 'rgba(248,113,113,0.12)' },
  cybersecurity:    { label: 'Cybersecurity',     Icon: ShieldRegular,     accent: '#fb923c', dim: 'rgba(251,146,60,0.12)'  },
};

// Deterministic avatar color from string
const AVATAR_COLORS = ['#6366f1','#3b82f6','#0ea5e9','#10b981','#f59e0b','#f97316','#ec4899','#a855f7'];
function pickColor(s: string) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return AVATAR_COLORS[h % AVATAR_COLORS.length];
}

const useStyles = makeStyles({
  card: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    borderRadius: '14px',
    border: '1px solid rgba(255,255,255,0.07)',
    background: '#111114',
    boxShadow: '0 1px 3px rgba(0,0,0,0.4), 0 8px 24px rgba(0,0,0,0.2)',
    transition: 'transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease',
    ':hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 16px rgba(0,0,0,0.5), 0 16px 40px rgba(0,0,0,0.3)',
      borderColor: 'rgba(255,255,255,0.13)',
    },
    overflow: 'hidden',
  },
  accentBar: {
    height: '3px',
    flexShrink: 0,
  },
  body: {
    flex: 1,
    padding: '18px 20px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  topRow: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
  },
  avatar: {
    width: '38px',
    height: '38px',
    borderRadius: '9px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '14px',
    fontWeight: '700',
    color: '#fff',
    flexShrink: 0,
    letterSpacing: '-0.3px',
  },
  topRight: {
    flex: 1,
    minWidth: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  company: {
    fontSize: '11px',
    fontWeight: '600',
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
    color: '#71717a',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  typeBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    borderRadius: '6px',
    padding: '2px 8px',
    fontSize: '10.5px',
    fontWeight: '600',
    width: 'fit-content',
    letterSpacing: '0.02em',
  },
  title: {
    fontSize: '14.5px',
    fontWeight: '600',
    lineHeight: '1.45',
    color: '#fafafa',
    display: '-webkit-box',
    WebkitLineClamp: '2',
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  metaList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
    marginTop: '2px',
  },
  metaRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '12px',
    color: '#71717a',
  },
  locationAccent: {
    color: '#a1a1aa',
    fontWeight: '500',
  },
  quickBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    borderRadius: '5px',
    padding: '2px 7px',
    fontSize: '10px',
    fontWeight: '600',
    background: 'rgba(52,211,153,0.12)',
    color: '#34d399',
    marginTop: '2px',
    width: 'fit-content',
  },
  divider: {
    height: '1px',
    background: 'rgba(255,255,255,0.06)',
    margin: '0',
  },
  footer: {
    padding: '14px 20px 18px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  applyBtn: {
    width: '100%',
    height: '40px',
    borderRadius: '9px',
    fontSize: '13.5px',
    fontWeight: '600',
    border: 'none',
    color: '#fff',
    cursor: 'pointer',
    transition: 'opacity 0.15s ease, transform 0.15s ease',
    ':hover': {
      opacity: 0.88,
      transform: 'translateY(-1px)',
    },
    ':active': {
      transform: 'translateY(0)',
    },
  },
  secondRow: {
    display: 'flex',
    gap: '8px',
  },
  skipBtn: {
    flex: 1,
    height: '36px',
    borderRadius: '8px',
    fontSize: '12.5px',
    fontWeight: '500',
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.07)',
    color: '#71717a',
    cursor: 'pointer',
    transition: 'background 0.15s ease, color 0.15s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
    ':hover': {
      background: 'rgba(255,255,255,0.08)',
      color: '#a1a1aa',
    },
  },
  blockBtn: {
    width: '36px',
    height: '36px',
    borderRadius: '8px',
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.07)',
    color: '#52525b',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'background 0.15s ease, color 0.15s ease',
    flexShrink: 0,
    ':hover': {
      background: 'rgba(239,68,68,0.1)',
      color: '#f87171',
    },
  },
  confirmNote: {
    textAlign: 'center',
    fontSize: '12px',
    color: '#71717a',
  },
  yesBtn: {
    width: '100%',
    height: '40px',
    borderRadius: '9px',
    background: 'rgba(52,211,153,0.15)',
    border: '1px solid rgba(52,211,153,0.25)',
    color: '#34d399',
    fontSize: '13.5px',
    fontWeight: '600',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    transition: 'background 0.15s ease',
    ':hover': { background: 'rgba(52,211,153,0.22)' },
  },
  notYetBtn: {
    width: '100%',
    height: '36px',
    borderRadius: '8px',
    background: 'transparent',
    border: '1px solid rgba(255,255,255,0.08)',
    color: '#71717a',
    fontSize: '12.5px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background 0.15s ease',
    ':hover': { background: 'rgba(255,255,255,0.05)' },
  },
  appliedBox: {
    height: '44px',
    borderRadius: '9px',
    background: 'rgba(52,211,153,0.1)',
    border: '1px solid rgba(52,211,153,0.2)',
    color: '#34d399',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    fontSize: '13.5px',
    fontWeight: '600',
  },
  skippedBox: {
    height: '40px',
    borderRadius: '9px',
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,255,255,0.06)',
    color: '#52525b',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    fontSize: '12.5px',
    fontWeight: '500',
  },
});

export const JobCard: React.FC<JobCardProps> = ({ job, onMarkApplied, onRejectJob, onRefreshJobs, isUpdating = false }) => {
  const s = useStyles();
  const [pending, setPending] = useState(false);
  const [blocking, setBlocking] = useState(false);

  const safe = (v: string) => { try { return decodeURIComponent(v); } catch { return v; } };
  const company  = safe(job.company  || '');
  const title    = safe(job.title    || '');
  const location = safe(job.location || '');
  const country  = job.country || getCountryFromLocation(job.location);

  const typeKey = (job.job_type || '').toLowerCase();
  const type = TYPE_CONFIG[typeKey] ?? { label: job.job_type ?? '', Icon: BriefcaseRegular, accent: '#6366f1', dim: 'rgba(99,102,241,0.12)' };
  const { Icon } = type;

  const initials = company.split(/\s+/).slice(0, 2).map(w => w[0]?.toUpperCase() ?? '').join('') || '?';
  const avatarColor = pickColor(company);

  const timeAgo = (() => {
    if (!job.scraped_at) return null;
    try {
      const h = Math.floor((Date.now() - new Date(job.scraped_at).getTime()) / 3600000);
      if (h < 1) return 'Just now';
      if (h < 24) return `${h}h ago`;
      const d = Math.floor(h / 24);
      return d < 7 ? `${d}d ago` : `${Math.floor(d / 7)}w ago`;
    } catch { return null; }
  })();

  const hasQuick = job.easy_apply_status === 'confirmed' || job.easy_apply_status === 'probable' || (job.easy_apply && !job.easy_apply_status);

  const handleBlock = async () => {
    if (!window.confirm(`Block all jobs from ${company}?`)) return;
    setBlocking(true);
    try {
      const r = await jobApi.bulkRejectJobs({ company: job.company });
      toast.success(`${r.jobs_rejected} jobs blocked from ${company}`);
      if (onRefreshJobs) setTimeout(onRefreshJobs, 800);
    } catch { toast.error('Failed'); }
    finally { setBlocking(false); }
  };

  return (
    <div className={s.card}>
      {/* Accent bar */}
      <div className={s.accentBar} style={{ background: type.accent }} />

      {/* Body */}
      <div className={s.body}>
        {/* Top: avatar + company + badge */}
        <div className={s.topRow}>
          <div className={s.avatar} style={{ background: avatarColor }}>
            {initials}
          </div>
          <div className={s.topRight}>
            <div className={s.company}>{company}</div>
            {type.label && (
              <span className={s.typeBadge} style={{ background: type.dim, color: type.accent }}>
                <Icon style={{ fontSize: '10px' }} />
                {type.label}
              </span>
            )}
          </div>
        </div>

        {/* Title */}
        <div className={s.title}>{title}</div>

        {/* Meta */}
        <div className={s.metaList}>
          {location && (
            <div className={s.metaRow}>
              <LocationRegular style={{ fontSize: '13px', flexShrink: 0 }} />
              <span className={s.locationAccent}>{location}</span>
              {country && country !== 'Unknown' && (
                <span style={{ color: '#52525b' }}>· {country}</span>
              )}
            </div>
          )}
          {(job.posted_date || timeAgo) && (
            <div className={s.metaRow}>
              <ClockRegular style={{ fontSize: '13px', flexShrink: 0 }} />
              <span>{job.posted_date}</span>
              {timeAgo && <span style={{ color: '#52525b' }}>· scraped {timeAgo}</span>}
            </div>
          )}
          {hasQuick && (
            <span className={s.quickBadge}>
              <FlashRegular style={{ fontSize: '10px' }} />
              Quick Apply
            </span>
          )}
        </div>
      </div>

      <div className={s.divider} />

      {/* Footer */}
      <div className={s.footer}>
        {!job.applied && !job.rejected && !pending && (
          <>
            <button
              className={s.applyBtn}
              style={{ background: type.accent }}
              disabled={isUpdating}
              onClick={() => {
                const a = document.createElement('a');
                a.href = job.job_url; a.target = '_blank'; a.rel = 'noopener noreferrer';
                document.body.appendChild(a); a.click(); document.body.removeChild(a);
                setPending(true);
              }}
            >
              Apply Now <ArrowRightRegular style={{ marginLeft: '6px', fontSize: '14px' }} />
            </button>
            <div className={s.secondRow}>
              <button className={s.skipBtn} onClick={() => onRejectJob(job.id)} disabled={isUpdating}>
                <DismissRegular style={{ fontSize: '14px' }} />
                Not Interested
              </button>
              <Tooltip content={`Block all from ${company}`} relationship="label">
                <button className={s.blockBtn} onClick={handleBlock} disabled={blocking}>
                  <BuildingRegular style={{ fontSize: '14px' }} />
                </button>
              </Tooltip>
            </div>
          </>
        )}

        {!job.applied && !job.rejected && pending && (
          <>
            <div className={s.confirmNote}>Did you submit the application?</div>
            <button className={s.yesBtn} onClick={() => { setPending(false); onMarkApplied(job.id); }}>
              <CheckmarkCircleFilled style={{ fontSize: '16px' }} />
              Yes, Applied!
            </button>
            <button className={s.notYetBtn} onClick={() => setPending(false)}>Not yet</button>
          </>
        )}

        {job.applied && (
          <div className={s.appliedBox}>
            <CheckmarkCircleFilled style={{ fontSize: '18px' }} />
            Applied
          </div>
        )}

        {job.rejected && (
          <div className={s.skippedBox}>
            <DismissCircleFilled style={{ fontSize: '16px' }} />
            Skipped
          </div>
        )}
      </div>
    </div>
  );
};
