import React, { useState } from 'react';
import {
  Card,
  CardHeader,
  CardFooter,
  Button,
  Badge,
  Text,
  makeStyles,
  tokens,
  Tooltip,
} from '@fluentui/react-components';
import {
  BuildingRegular,
  LocationRegular,
  ClockRegular,
  CheckmarkCircleFilled,
  DismissCircleFilled,
  ArrowRightRegular,
  FlashRegular,
  PeopleRegular,
  BriefcaseRegular,
  PaintBrushRegular,
  VideoRegular,
  HeadphonesRegular,
  TagRegular,
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

// Per-type visual config
const JOB_TYPE_CONFIG: Record<string, {
  label: string;
  icon: React.ElementType;
  color: string;
  bg: string;
}> = {
  sales: {
    label: 'Sales',
    icon: BriefcaseRegular,
    color: '#b45309',
    bg: '#fef3c7',
  },
  painter: {
    label: 'Painter',
    icon: PaintBrushRegular,
    color: '#1d4ed8',
    bg: '#dbeafe',
  },
  painting: {
    label: 'Painter',
    icon: PaintBrushRegular,
    color: '#1d4ed8',
    bg: '#dbeafe',
  },
  customer_service: {
    label: 'Customer Service',
    icon: HeadphonesRegular,
    color: '#065f46',
    bg: '#d1fae5',
  },
  customer_support: {
    label: 'Customer Support',
    icon: HeadphonesRegular,
    color: '#065f46',
    bg: '#d1fae5',
  },
  media_production: {
    label: 'Media',
    icon: VideoRegular,
    color: '#6d28d9',
    bg: '#ede9fe',
  },
  media: {
    label: 'Media',
    icon: VideoRegular,
    color: '#6d28d9',
    bg: '#ede9fe',
  },
  software: {
    label: 'Software',
    icon: TagRegular,
    color: '#1e40af',
    bg: '#dbeafe',
  },
  hr: {
    label: 'HR',
    icon: PeopleRegular,
    color: '#6d28d9',
    bg: '#ede9fe',
  },
  finance: {
    label: 'Finance',
    icon: TagRegular,
    color: '#065f46',
    bg: '#d1fae5',
  },
  aml: {
    label: 'AML / Compliance',
    icon: TagRegular,
    color: '#991b1b',
    bg: '#fee2e2',
  },
};

const useStyles = makeStyles({
  card: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    borderRadius: tokens.borderRadiusXLarge,
    boxShadow: tokens.shadow4,
    transition: 'box-shadow 0.2s ease, transform 0.2s ease',
    ':hover': {
      boxShadow: tokens.shadow16,
      transform: 'translateY(-2px)',
    },
    overflow: 'hidden',
  },
  typeStripe: {
    height: '4px',
    width: '100%',
    flexShrink: 0,
  },
  body: {
    flex: 1,
    padding: '16px 20px 12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  companyRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  title: {
    fontSize: '15px',
    fontWeight: '600',
    lineHeight: '1.35',
    display: '-webkit-box',
    WebkitLineClamp: '2',
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  metaRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    color: tokens.colorNeutralForeground3,
    fontSize: '12px',
  },
  tagsRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    flexWrap: 'wrap',
    marginTop: '4px',
  },
  typeBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    borderRadius: tokens.borderRadiusMedium,
    padding: '2px 8px',
    fontSize: '11px',
    fontWeight: '600',
  },
  footer: {
    padding: '12px 20px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  applyBtn: {
    width: '100%',
    fontWeight: '600',
    borderRadius: tokens.borderRadiusMedium,
  },
  actionRow: {
    display: 'flex',
    gap: '8px',
  },
  appliedState: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '10px',
    borderRadius: tokens.borderRadiusMedium,
    background: tokens.colorPaletteGreenBackground2,
    color: tokens.colorPaletteGreenForeground2,
    fontWeight: '600',
    fontSize: '14px',
  },
  rejectedState: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '10px',
    borderRadius: tokens.borderRadiusMedium,
    background: tokens.colorNeutralBackground3,
    color: tokens.colorNeutralForeground4,
    fontWeight: '600',
    fontSize: '14px',
    opacity: '0.7',
  },
  confirmText: {
    textAlign: 'center',
    color: tokens.colorNeutralForeground2,
    fontSize: '13px',
    fontWeight: '500',
    paddingTop: '2px',
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

  const typeKey = (job.job_type || '').toLowerCase();
  const typeConfig = JOB_TYPE_CONFIG[typeKey] || {
    label: job.job_type || '',
    icon: TagRegular,
    color: '#374151',
    bg: '#f3f4f6',
  };
  const TypeIcon = typeConfig.icon;

  const safeDecode = (str: string) => {
    try { return decodeURIComponent(str); } catch { return str; }
  };

  const getScrapedAgo = () => {
    if (!job.scraped_at) return null;
    try {
      const diff = Date.now() - new Date(job.scraped_at).getTime();
      const mins = Math.floor(diff / 60000);
      const hours = Math.floor(mins / 60);
      const days = Math.floor(hours / 24);
      if (days > 7) return `${Math.floor(days / 7)}w ago`;
      if (days > 0) return `${days}d ago`;
      if (hours > 0) return `${hours}h ago`;
      if (mins > 0) return `${mins}m ago`;
      return 'Just now';
    } catch { return null; }
  };

  const handleBulkReject = async () => {
    if (!window.confirm(`Reject ALL jobs from ${job.company}?`)) return;
    setBulkLoading(true);
    try {
      const result = await jobApi.bulkRejectJobs({ company: job.company });
      toast.success(`${result.jobs_rejected} jobs from ${job.company} rejected!`);
      if (onRefreshJobs) setTimeout(onRefreshJobs, 800);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to bulk reject');
    } finally {
      setBulkLoading(false);
    }
  };

  const hasQuickApply =
    job.easy_apply_status === 'confirmed' ||
    job.easy_apply_status === 'probable' ||
    (job.easy_apply && !job.easy_apply_status);

  const scrapedAgo = getScrapedAgo();
  const location = safeDecode(job.location || '');
  const company = safeDecode(job.company || '');
  const title = safeDecode(job.title || '');
  const extractedCountry = job.country || getCountryFromLocation(job.location);

  return (
    <Card className={styles.card}>
      {/* Color stripe at top */}
      <div
        className={styles.typeStripe}
        style={{ background: typeConfig.color }}
      />

      {/* Card body */}
      <div className={styles.body}>
        {/* Company */}
        <div className={styles.companyRow}>
          <BuildingRegular style={{ color: tokens.colorNeutralForeground3, fontSize: '14px', flexShrink: 0 }} />
          <Text size={100} weight="semibold" style={{ color: tokens.colorNeutralForeground3, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {company}
          </Text>
        </div>

        {/* Title */}
        <div className={styles.title}>
          <Text weight="semibold" size={300}>
            {title}
          </Text>
        </div>

        {/* Location */}
        {location && (
          <div className={styles.metaRow}>
            <LocationRegular style={{ fontSize: '13px', flexShrink: 0 }} />
            <Text size={100}>{location}</Text>
            {extractedCountry && extractedCountry !== 'Unknown' && (
              <Text size={100} weight="semibold" style={{ color: tokens.colorBrandForeground1, marginLeft: '4px' }}>
                · {extractedCountry}
              </Text>
            )}
          </div>
        )}

        {/* Date + scraped */}
        {(job.posted_date || scrapedAgo) && (
          <div className={styles.metaRow}>
            <ClockRegular style={{ fontSize: '13px', flexShrink: 0 }} />
            <Text size={100}>{job.posted_date || ''}</Text>
            {scrapedAgo && (
              <Text size={100} style={{ color: tokens.colorNeutralForeground4 }}>
                · scraped {scrapedAgo}
              </Text>
            )}
          </div>
        )}

        {/* Tags */}
        <div className={styles.tagsRow}>
          {typeConfig.label && (
            <span
              className={styles.typeBadge}
              style={{ background: typeConfig.bg, color: typeConfig.color }}
            >
              <TypeIcon style={{ fontSize: '11px' }} />
              {typeConfig.label}
            </span>
          )}
          {hasQuickApply && (
            <Tooltip
              content={
                job.easy_apply_status === 'confirmed'
                  ? 'Verified Quick Apply'
                  : 'Likely Quick Apply'
              }
              relationship="label"
            >
              <span
                className={styles.typeBadge}
                style={{
                  background: job.easy_apply_status === 'confirmed' ? '#d1fae5' : '#fef3c7',
                  color: job.easy_apply_status === 'confirmed' ? '#065f46' : '#92400e',
                }}
              >
                <FlashRegular style={{ fontSize: '11px' }} />
                {job.easy_apply_status === 'confirmed' ? 'Quick Apply ✓' : 'Quick Apply ?'}
              </span>
            </Tooltip>
          )}
        </div>
      </div>

      {/* Footer actions */}
      <div className={styles.footer}>
        {!job.applied && !job.rejected && !pendingApply && (
          <>
            <Button
              appearance="primary"
              className={styles.applyBtn}
              icon={<ArrowRightRegular />}
              iconPosition="after"
              disabled={isUpdating}
              onClick={() => {
                const a = document.createElement('a');
                a.href = job.job_url;
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                setPendingApply(true);
              }}
            >
              Apply Now
            </Button>

            <div className={styles.actionRow}>
              <Button
                appearance="subtle"
                style={{ flex: 1, color: tokens.colorPaletteRedForeground1 }}
                onClick={() => onRejectJob(job.id)}
                disabled={isUpdating}
              >
                Not Interested
              </Button>
              <Tooltip content={`Reject all from ${company}`} relationship="label">
                <Button
                  appearance="subtle"
                  icon={<BuildingRegular />}
                  style={{ color: tokens.colorNeutralForeground3 }}
                  onClick={handleBulkReject}
                  disabled={bulkLoading}
                />
              </Tooltip>
            </div>
          </>
        )}

        {!job.applied && !job.rejected && pendingApply && (
          <>
            <Text className={styles.confirmText}>Did you complete the application?</Text>
            <Button
              appearance="primary"
              className={styles.applyBtn}
              style={{ background: tokens.colorPaletteGreenBackground3, border: 'none' }}
              icon={<CheckmarkCircleFilled />}
              onClick={() => { setPendingApply(false); onMarkApplied(job.id); }}
            >
              Yes, I Applied!
            </Button>
            <Button
              appearance="outline"
              className={styles.applyBtn}
              onClick={() => setPendingApply(false)}
            >
              Not Yet
            </Button>
          </>
        )}

        {job.applied && (
          <div className={styles.appliedState}>
            <CheckmarkCircleFilled style={{ fontSize: '18px' }} />
            Applied
          </div>
        )}

        {job.rejected && (
          <div className={styles.rejectedState}>
            <DismissCircleFilled style={{ fontSize: '18px' }} />
            Not Interested
          </div>
        )}
      </div>
    </Card>
  );
};
