import React from 'react';
import { makeStyles, tokens } from '@fluentui/react-components';
import {
  BriefcaseRegular,
  SparkleRegular,
} from '@fluentui/react-icons';
import type { JobStats } from '../types';

const useStyles = makeStyles({
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '12px',
    marginBottom: '24px',
  },
  card: {
    borderRadius: '14px',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    border: '1px solid rgba(255,255,255,0.06)',
    background: '#111114',
    transition: 'border-color 0.15s',
    ':hover': {
      borderColor: 'rgba(255,255,255,0.12)',
    },
  },
  iconWrap: {
    width: '36px',
    height: '36px',
    borderRadius: '10px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '18px',
  },
  value: {
    fontSize: '38px',
    fontWeight: '800',
    lineHeight: '1',
    letterSpacing: '-2px',
  },
  label: {
    fontSize: '11px',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.07em',
    marginTop: '2px',
    color: tokens.colorNeutralForeground3,
  },
});

const CARDS = [
  {
    label: 'Available',
    key: 'total' as const,
    Icon: BriefcaseRegular,
    accent: '#3b82f6',
    iconBg: 'rgba(59,130,246,0.12)',
  },
  {
    label: 'New Today',
    key: 'new' as const,
    Icon: SparkleRegular,
    accent: '#10b981',
    iconBg: 'rgba(16,185,129,0.12)',
  },
];

export const StatsCards: React.FC<{ stats: JobStats }> = ({ stats }) => {
  const styles = useStyles();

  return (
    <div className={styles.grid}>
      {CARDS.map(({ label, key, Icon, accent, iconBg }) => (
        <div key={label} className={styles.card}>
          <div className={styles.iconWrap} style={{ background: iconBg }}>
            <Icon style={{ color: accent, fontSize: '18px' }} />
          </div>
          <div>
            <div className={styles.value} style={{ color: accent }}>
              {stats[key].toLocaleString()}
            </div>
            <div className={styles.label}>{label}</div>
          </div>
        </div>
      ))}
    </div>
  );
};
