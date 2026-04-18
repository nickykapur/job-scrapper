import React from 'react';
import {
  Card,
  Text,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import {
  BriefcaseFilled,
  SparkleRegular,
} from '@fluentui/react-icons';
import type { JobStats } from '../types';

interface StatsCardsProps {
  stats: JobStats;
}

const useStyles = makeStyles({
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '12px',
    marginBottom: '20px',
  },
  card: {
    borderRadius: tokens.borderRadiusXLarge,
    boxShadow: tokens.shadow4,
    overflow: 'hidden',
    transition: 'box-shadow 0.2s ease, transform 0.2s ease',
    ':hover': {
      boxShadow: tokens.shadow16,
      transform: 'translateY(-2px)',
    },
  },
  inner: {
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  iconBox: {
    width: '40px',
    height: '40px',
    borderRadius: tokens.borderRadiusLarge,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '22px',
  },
  value: {
    fontSize: '36px',
    fontWeight: '700',
    lineHeight: '1',
    letterSpacing: '-1px',
  },
  label: {
    fontSize: '11px',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
    color: tokens.colorNeutralForeground3,
  },
});

export const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  const styles = useStyles();

  const items = [
    {
      label: 'Available Jobs',
      value: stats.total,
      icon: BriefcaseFilled,
      iconBg: '#dbeafe',
      iconColor: '#1d4ed8',
      valueColor: '#1d4ed8',
      accent: '#3b82f6',
    },
    {
      label: 'New Today',
      value: stats.new,
      icon: SparkleRegular,
      iconBg: '#d1fae5',
      iconColor: '#065f46',
      valueColor: '#059669',
      accent: '#10b981',
    },
  ];

  return (
    <div className={styles.grid}>
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <Card key={item.label} className={styles.card} style={{ borderTop: `3px solid ${item.accent}` }}>
            <div className={styles.inner}>
              <div
                className={styles.iconBox}
                style={{ background: item.iconBg }}
              >
                <Icon style={{ color: item.iconColor, fontSize: '22px' }} />
              </div>
              <div>
                <div className={styles.value} style={{ color: item.valueColor }}>
                  {item.value.toLocaleString()}
                </div>
                <Text className={styles.label}>{item.label}</Text>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
};
