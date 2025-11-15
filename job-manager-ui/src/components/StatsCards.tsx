import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { JobStats } from '../types';
import { motion } from 'framer-motion';

interface StatsCardsProps {
  stats: JobStats;
}

const MotionCard = motion(Card);

export const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  const statItems = [
    {
      label: 'Total Jobs',
      value: stats.total,
      color: 'rgb(59, 130, 246)', // blue-500
      colorClass: 'text-blue-500',
      hoverClass: 'hover:border-blue-500/40 hover:shadow-blue-500/10',
    },
    {
      label: 'New Positions',
      value: stats.new,
      color: 'rgb(16, 185, 129)', // emerald-500
      colorClass: 'text-emerald-500',
      hoverClass: 'hover:border-emerald-500/40 hover:shadow-emerald-500/10',
    },
    {
      label: 'Applied',
      value: stats.applied,
      color: 'rgb(139, 92, 246)', // violet-500
      colorClass: 'text-violet-500',
      hoverClass: 'hover:border-violet-500/40 hover:shadow-violet-500/10',
    },
    {
      label: 'Pending',
      value: stats.not_applied,
      color: 'rgb(245, 158, 11)', // amber-500
      colorClass: 'text-amber-500',
      hoverClass: 'hover:border-amber-500/40 hover:shadow-amber-500/10',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-4 md:mb-6">
      {statItems.map((item, index) => (
        <MotionCard
          key={item.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
          className={`transition-all duration-200 ${item.hoverClass} hover:-translate-y-1 hover:shadow-lg`}
        >
          <CardContent className="p-4 md:p-6">
            <div className="space-y-2">
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                {item.label}
              </p>
              <p className={`text-3xl md:text-4xl font-bold ${item.colorClass} tracking-tight`}>
                {item.value}
              </p>
            </div>
          </CardContent>
        </MotionCard>
      ))}
    </div>
  );
};
