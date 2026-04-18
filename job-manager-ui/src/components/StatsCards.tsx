import React from 'react';
import { Text, makeStyles, tokens } from '@fluentui/react-components';
import {
  BriefcaseFilled,
  SparkleRegular,
  CheckmarkCircleFilled,
  DismissCircleFilled,
} from '@fluentui/react-icons';
import type { JobStats } from '../types';

const useStyles = makeStyles({
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '14px',
    marginBottom: '24px',
  },
  card: {
    borderRadius: '16px',
    overflow: 'hidden',
    position: 'relative',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    border: '1px solid transparent',
    transition: 'transform 0.18s, box-shadow 0.18s',
    ':hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 8px 24px rgba(0,0,0,0.1)',
    },
  },
  iconCircle: {
    width: '44px',
    height: '44px',
    borderRadius: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '22px',
  },
  value: {
    fontSize: '40px',
    fontWeight: '800',
    lineHeight: '1',
    letterSpacing: '-2px',
  },
  label: {
    fontSize: '11px',
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    marginTop: '2px',
  },
});

export const StatsCards: React.FC<{ stats: JobStats }> = ({ stats }) => {
  const styles = useStyles();

  const cards = [
    {
      label: 'Available',
      value: stats.total,
      icon: BriefcaseFilled,
      bg: 'linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%)',
      iconBg: 'linear-gradient(135deg,#3b82f6,#6366f1)',
      valueColor: '#1e40af',
      labelColor: '#3730a3',
      border: '#c7d2fe',
    },
    {
      label: 'New Today',
      value: stats.new,
      icon: SparkleRegular,
      bg: 'linear-gradient(135deg, #d1fae5 0%, #ccfbf1 100%)',
      iconBg: 'linear-gradient(135deg,#10b981,#14b8a6)',
      valueColor: '#065f46',
      labelColor: '#0f766e',
      border: '#a7f3d0',
    },
  ];

  // Dark mode: use darker backgrounds
  const isDark = document.documentElement.classList.contains('dark');

  const darkCards = [
    {
      label: 'Available',
      value: stats.total,
      icon: BriefcaseFilled,
      bg: 'linear-gradient(135deg, #1e3a5f 0%, #1e1b4b 100%)',
      iconBg: 'linear-gradient(135deg,#3b82f6,#6366f1)',
      valueColor: '#93c5fd',
      labelColor: '#a5b4fc',
      border: '#1e40af',
    },
    {
      label: 'New Today',
      value: stats.new,
      icon: SparkleRegular,
      bg: 'linear-gradient(135deg, #064e3b 0%, #134e4a 100%)',
      iconBg: 'linear-gradient(135deg,#10b981,#14b8a6)',
      valueColor: '#6ee7b7',
      labelColor: '#5eead4',
      border: '#065f46',
    },
  ];

  const items = isDark ? darkCards : cards;

  return (
    <div className={styles.grid}>
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <div
            key={item.label}
            className={styles.card}
            style={{ background: item.bg, borderColor: item.border }}
          >
            <div
              className={styles.iconCircle}
              style={{ background: item.iconBg }}
            >
              <Icon style={{ color: '#fff', fontSize: '22px' }} />
            </div>
            <div>
              <div className={styles.value} style={{ color: item.valueColor }}>
                {item.value.toLocaleString()}
              </div>
              <div className={styles.label} style={{ color: item.labelColor }}>
                {item.label}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
