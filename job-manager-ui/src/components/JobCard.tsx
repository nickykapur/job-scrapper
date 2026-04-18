import React, { useState } from 'react';
import {
  Button,
  Text,
  makeStyles,
  tokens,
  Tooltip,
  shorthands,
} from '@fluentui/react-components';
import {
  CheckmarkCircleFilled,
  DismissCircleFilled,
  ArrowRightFilled,
  FlashFilled,
  PeopleRegular,
  BriefcaseFilled,
  PaintBrushFilled,
  VideoFilled,
  HeadphonesFilled,
  CodeFilled,
  MoneyFilled,
  ShieldFilled,
  LocationRegular,
  ClockRegular,
  BuildingRegular,
  DismissRegular,
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

type JobTypeKey = 'sales'|'painter'|'painting'|'customer_service'|'customer_support'|'media_production'|'media'|'software'|'hr'|'finance'|'aml'|'compliance'|'cybersecurity';

const JOB_TYPES: Record<JobTypeKey, { label: string; Icon: React.ElementType; color: string; light: string; dark: string; gradient: string }> = {
  sales:            { label: 'Sales',           Icon: BriefcaseFilled,   color: '#b45309', light: '#fef3c7', dark: '#78350f', gradient: 'linear-gradient(135deg,#f59e0b,#d97706)' },
  painter:          { label: 'Painter',          Icon: PaintBrushFilled,  color: '#1d4ed8', light: '#dbeafe', dark: '#1e3a8a', gradient: 'linear-gradient(135deg,#3b82f6,#2563eb)' },
  painting:         { label: 'Painter',          Icon: PaintBrushFilled,  color: '#1d4ed8', light: '#dbeafe', dark: '#1e3a8a', gradient: 'linear-gradient(135deg,#3b82f6,#2563eb)' },
  customer_service: { label: 'Customer Service', Icon: HeadphonesFilled,  color: '#065f46', light: '#d1fae5', dark: '#064e3b', gradient: 'linear-gradient(135deg,#10b981,#059669)' },
  customer_support: { label: 'Customer Support', Icon: HeadphonesFilled,  color: '#065f46', light: '#d1fae5', dark: '#064e3b', gradient: 'linear-gradient(135deg,#10b981,#059669)' },
  media_production: { label: 'Media',            Icon: VideoFilled,       color: '#5b21b6', light: '#ede9fe', dark: '#3b0764', gradient: 'linear-gradient(135deg,#8b5cf6,#7c3aed)' },
  media:            { label: 'Media',            Icon: VideoFilled,       color: '#5b21b6', light: '#ede9fe', dark: '#3b0764', gradient: 'linear-gradient(135deg,#8b5cf6,#7c3aed)' },
  software:         { label: 'Software',         Icon: CodeFilled,        color: '#1e40af', light: '#dbeafe', dark: '#1e3a8a', gradient: 'linear-gradient(135deg,#6366f1,#4f46e5)' },
  hr:               { label: 'HR',               Icon: PeopleRegular,     color: '#9d174d', light: '#fce7f3', dark: '#831843', gradient: 'linear-gradient(135deg,#ec4899,#db2777)' },
  finance:          { label: 'Finance',           Icon: MoneyFilled,       color: '#0f766e', light: '#ccfbf1', dark: '#134e4a', gradient: 'linear-gradient(135deg,#14b8a6,#0d9488)' },
  aml:              { label: 'AML/Compliance',   Icon: ShieldFilled,      color: '#991b1b', light: '#fee2e2', dark: '#7f1d1d', gradient: 'linear-gradient(135deg,#ef4444,#dc2626)' },
  compliance:       { label: 'Compliance',        Icon: ShieldFilled,      color: '#991b1b', light: '#fee2e2', dark: '#7f1d1d', gradient: 'linear-gradient(135deg,#ef4444,#dc2626)' },
  cybersecurity:    { label: 'Cybersecurity',    Icon: ShieldFilled,      color: '#92400e', light: '#fef3c7', dark: '#78350f', gradient: 'linear-gradient(135deg,#f97316,#ea580c)' },
};

// Consistent avatar color from company name
const AVATAR_GRADIENTS = [
  'linear-gradient(135deg,#6366f1,#8b5cf6)',
  'linear-gradient(135deg,#3b82f6,#06b6d4)',
  'linear-gradient(135deg,#10b981,#14b8a6)',
  'linear-gradient(135deg,#f59e0b,#f97316)',
  'linear-gradient(135deg,#ec4899,#8b5cf6)',
  'linear-gradient(135deg,#ef4444,#f97316)',
  'linear-gradient(135deg,#0ea5e9,#6366f1)',
  'linear-gradient(135deg,#84cc16,#10b981)',
];
function avatarGradient(name: string) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) & 0xffffffff;
  return AVATAR_GRADIENTS[Math.abs(hash) % AVATAR_GRADIENTS.length];
}

const useStyles = makeStyles({
  card: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    borderRadius: '16px',
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    overflow: 'hidden',
    background: tokens.colorNeutralBackground1,
    boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
    transition: 'transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease',
    ':hover': {
      transform: 'translateY(-3px)',
      boxShadow: '0 12px 32px rgba(0,0,0,0.12)',
      borderColor: tokens.colorNeutralStroke1,
    },
    cursor: 'default',
  },
  topAccent: {
    height: '5px',
    flexShrink: 0,
  },
  body: {
    flex: 1,
    ...shorthands.padding('18px', '20px', '14px'),
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  companyRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  avatar: {
    width: '42px',
    height: '42px',
    borderRadius: '10px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '16px',
    fontWeight: '700',
    color: '#fff',
    flexShrink: 0,
    letterSpacing: '-0.5px',
  },
  companyInfo: {
    flex: 1,
    minWidth: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  companyName: {
    fontSize: '11px',
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    color: tokens.colorNeutralForeground3,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  typePill: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    borderRadius: '20px',
    padding: '2px 9px 2px 7px',
    fontSize: '10.5px',
    fontWeight: '700',
    width: 'fit-content',
  },
  title: {
    fontSize: '15px',
    fontWeight: '650',
    lineHeight: '1.4',
    color: tokens.colorNeutralForeground1,
    display: '-webkit-box',
    WebkitLineClamp: '2',
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  metaList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  metaRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    color: tokens.colorNeutralForeground3,
    fontSize: '12px',
  },
  metaIcon: {
    fontSize: '13px',
    flexShrink: 0,
    opacity: 0.7,
  },
  quickBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '3px',
    borderRadius: '20px',
    padding: '2px 8px',
    fontSize: '10px',
    fontWeight: '700',
    marginTop: '2px',
    width: 'fit-content',
  },
  divider: {
    height: '1px',
    background: tokens.colorNeutralStroke2,
    margin: '0 20px',
  },
  footer: {
    ...shorthands.padding('14px', '20px', '18px'),
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  applyBtn: {
    width: '100%',
    height: '42px',
    borderRadius: '10px',
    fontSize: '14px',
    fontWeight: '700',
  },
  actionRow: {
    display: 'flex',
    gap: '8px',
  },
  skipBtn: {
    flex: 1,
    height: '36px',
    borderRadius: '8px',
    fontSize: '13px',
    color: tokens.colorNeutralForeground3,
  },
  blockBtn: {
    height: '36px',
    width: '36px',
    borderRadius: '8px',
    minWidth: 'unset',
    padding: '0',
    color: tokens.colorNeutralForeground4,
  },
  appliedBox: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    height: '44px',
    borderRadius: '10px',
    background: 'linear-gradient(135deg,#d1fae5,#a7f3d0)',
    color: '#065f46',
    fontSize: '14px',
    fontWeight: '700',
  },
  rejectedBox: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    height: '44px',
    borderRadius: '10px',
    background: tokens.colorNeutralBackground3,
    color: tokens.colorNeutralForeground4,
    fontSize: '13px',
    fontWeight: '600',
    opacity: '0.65',
  },
  confirmLabel: {
    textAlign: 'center',
    fontSize: '12.5px',
    fontWeight: '500',
    color: tokens.colorNeutralForeground3,
  },
});

export const JobCard: React.FC<JobCardProps> = ({
  job,
  onMarkApplied,
  onRejectJob,
  onRefreshJobs,
  isUpdating = false,
}) => {
  const styles = useStyles();
  const [pendingApply, setPendingApply] = useState(false);
  const [bulkLoading, setBulkLoading] = useState(false);

  const safeDecode = (s: string) => { try { return decodeURIComponent(s); } catch { return s; } };

  const company = safeDecode(job.company || '');
  const title   = safeDecode(job.title || '');
  const location = safeDecode(job.location || '');

  const typeKey = (job.job_type || '').toLowerCase() as JobTypeKey;
  const type = JOB_TYPES[typeKey] ?? { label: job.job_type ?? '', Icon: BriefcaseFilled, color: '#6b7280', light: '#f3f4f6', dark: '#374151', gradient: 'linear-gradient(135deg,#6b7280,#4b5563)' };
  const { Icon: TypeIcon } = type;

  const initials = company.split(/\s+/).slice(0, 2).map(w => w[0]?.toUpperCase() ?? '').join('') || '?';

  const extractedCountry = job.country || getCountryFromLocation(job.location);

  const getTimeAgo = () => {
    if (!job.scraped_at) return null;
    try {
      const diff = Date.now() - new Date(job.scraped_at).getTime();
      const h = Math.floor(diff / 3600000);
      const d = Math.floor(h / 24);
      if (d > 6) return `${Math.floor(d/7)}w ago`;
      if (d > 0) return `${d}d ago`;
      if (h > 0) return `${h}h ago`;
      return 'Just now';
    } catch { return null; }
  };

  const hasQuickApply = job.easy_apply_status === 'confirmed' || job.easy_apply_status === 'probable' || (job.easy_apply && !job.easy_apply_status);
  const isConfirmedQuick = job.easy_apply_status === 'confirmed';

  const handleBulkReject = async () => {
    if (!window.confirm(`Reject ALL jobs from ${company}?`)) return;
    setBulkLoading(true);
    try {
      const r = await jobApi.bulkRejectJobs({ company: job.company });
      toast.success(`${r.jobs_rejected} jobs from ${company} rejected!`);
      if (onRefreshJobs) setTimeout(onRefreshJobs, 800);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Failed to bulk reject');
    } finally {
      setBulkLoading(false);
    }
  };

  const timeAgo = getTimeAgo();

  return (
    <div className={styles.card}>
      {/* Color accent stripe */}
      <div className={styles.topAccent} style={{ background: type.gradient }} />

      {/* Body */}
      <div className={styles.body}>
        {/* Company row: avatar + name + type badge */}
        <div className={styles.companyRow}>
          <div className={styles.avatar} style={{ background: avatarGradient(company) }}>
            {initials}
          </div>
          <div className={styles.companyInfo}>
            <div className={styles.companyName}>{company}</div>
            {type.label && (
              <span
                className={styles.typePill}
                style={{ background: type.light, color: type.color }}
              >
                <TypeIcon style={{ fontSize: '11px' }} />
                {type.label}
              </span>
            )}
          </div>
        </div>

        {/* Title */}
        <div className={styles.title}>{title}</div>

        {/* Meta */}
        <div className={styles.metaList}>
          {location && (
            <div className={styles.metaRow}>
              <LocationRegular className={styles.metaIcon} />
              <span>{location}</span>
              {extractedCountry && extractedCountry !== 'Unknown' && (
                <span style={{ color: tokens.colorBrandForeground1, fontWeight: 600 }}>· {extractedCountry}</span>
              )}
            </div>
          )}
          {(job.posted_date || timeAgo) && (
            <div className={styles.metaRow}>
              <ClockRegular className={styles.metaIcon} />
              <span>{job.posted_date || ''}</span>
              {timeAgo && <span style={{ opacity: 0.6 }}>· {timeAgo}</span>}
            </div>
          )}
          {hasQuickApply && (
            <span
              className={styles.quickBadge}
              style={{
                background: isConfirmedQuick ? '#d1fae5' : '#fef3c7',
                color: isConfirmedQuick ? '#065f46' : '#92400e',
              }}
            >
              <FlashFilled style={{ fontSize: '10px' }} />
              {isConfirmedQuick ? 'Quick Apply ✓' : 'Quick Apply'}
            </span>
          )}
        </div>
      </div>

      {/* Divider */}
      <div className={styles.divider} />

      {/* Footer */}
      <div className={styles.footer}>
        {!job.applied && !job.rejected && !pendingApply && (
          <>
            <Button
              className={styles.applyBtn}
              style={{ background: type.gradient, border: 'none', color: '#fff' }}
              icon={<ArrowRightFilled />}
              iconPosition="after"
              disabled={isUpdating}
              onClick={() => {
                const a = document.createElement('a');
                a.href = job.job_url; a.target = '_blank'; a.rel = 'noopener noreferrer';
                document.body.appendChild(a); a.click(); document.body.removeChild(a);
                setPendingApply(true);
              }}
            >
              Apply Now
            </Button>
            <div className={styles.actionRow}>
              <Button
                appearance="subtle"
                className={styles.skipBtn}
                onClick={() => onRejectJob(job.id)}
                disabled={isUpdating}
              >
                <DismissRegular style={{ marginRight: '6px', fontSize: '14px' }} />
                Skip
              </Button>
              <Tooltip content={`Block all from ${company}`} relationship="label">
                <Button
                  appearance="subtle"
                  className={styles.blockBtn}
                  icon={<BuildingRegular />}
                  onClick={handleBulkReject}
                  disabled={bulkLoading}
                />
              </Tooltip>
            </div>
          </>
        )}

        {!job.applied && !job.rejected && pendingApply && (
          <>
            <div className={styles.confirmLabel}>Did you complete the application?</div>
            <Button
              className={styles.applyBtn}
              style={{ background: 'linear-gradient(135deg,#10b981,#059669)', border: 'none', color: '#fff' }}
              icon={<CheckmarkCircleFilled />}
              onClick={() => { setPendingApply(false); onMarkApplied(job.id); }}
            >
              Yes, I Applied!
            </Button>
            <Button appearance="outline" className={styles.applyBtn} onClick={() => setPendingApply(false)}>
              Not Yet
            </Button>
          </>
        )}

        {job.applied && (
          <div className={styles.appliedBox}>
            <CheckmarkCircleFilled style={{ fontSize: '20px', color: '#059669' }} />
            Applied Successfully
          </div>
        )}

        {job.rejected && (
          <div className={styles.rejectedBox}>
            <DismissCircleFilled style={{ fontSize: '18px' }} />
            Skipped
          </div>
        )}
      </div>
    </div>
  );
};
