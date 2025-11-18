import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Trophy, Lock, Zap, Target, Calendar } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

interface BadgeData {
  id: string;
  name: string;
  description: string;
  points: number;
  category: 'volume' | 'streak';
  threshold: number;
  metric: 'applications' | 'days';
  icon: string;
  earned: boolean;
  earned_at?: string;
  progress: number;
  progress_percentage: number;
  remaining: number;
}

interface AllAchievementsProps {
  badges: BadgeData[];
}

export const AllAchievements: React.FC<AllAchievementsProps> = ({ badges }) => {
  const [filter, setFilter] = useState<'all' | 'volume' | 'streak'>('all');

  // Filter badges by category
  const filteredBadges = badges.filter(badge =>
    filter === 'all' || badge.category === filter
  );

  // Sort: unearned first (by remaining), then earned by date
  const sortedBadges = [...filteredBadges].sort((a, b) => {
    if (a.earned === b.earned) {
      if (!a.earned) {
        // Both unearned: sort by closest to unlock (least remaining)
        return a.remaining - b.remaining;
      } else {
        // Both earned: sort by earned date (newest first)
        return (b.earned_at || '').localeCompare(a.earned_at || '');
      }
    }
    // Unearned badges first
    return a.earned ? 1 : -1;
  });

  const earnedCount = badges.filter(b => b.earned).length;
  const totalCount = badges.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Trophy className="h-6 w-6 text-yellow-500" />
            All Achievements
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            {earnedCount} of {totalCount} achievements unlocked
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
              filter === 'all'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('volume')}
            className={`px-3 py-1.5 text-sm rounded-lg transition-colors flex items-center gap-1 ${
              filter === 'volume'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            <Target className="h-3 w-3" />
            Volume
          </button>
          <button
            onClick={() => setFilter('streak')}
            className={`px-3 py-1.5 text-sm rounded-lg transition-colors flex items-center gap-1 ${
              filter === 'streak'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            <Calendar className="h-3 w-3" />
            Streak
          </button>
        </div>
      </div>

      {/* Progress Overview */}
      <Card className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 border-purple-500/20">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="text-sm font-bold">{earnedCount}/{totalCount}</span>
          </div>
          <Progress value={(earnedCount / totalCount) * 100} className="h-2" />
        </CardContent>
      </Card>

      {/* Badges Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sortedBadges.map((badge) => (
          <Card
            key={badge.id}
            className={`relative overflow-hidden transition-all hover:shadow-lg hover:-translate-y-0.5 ${
              badge.earned
                ? 'border-green-500/50 bg-gradient-to-br from-green-500/5 to-emerald-500/5'
                : 'border-gray-500/30 bg-gradient-to-br from-gray-500/5 to-slate-500/5'
            }`}
          >
            <CardContent className="p-5">
              {/* Badge Header */}
              <div className="flex items-start justify-between mb-3">
                <div className={`text-4xl ${badge.earned ? '' : 'grayscale opacity-50'}`}>
                  {badge.icon}
                </div>

                {badge.earned ? (
                  <Badge className="bg-green-500/20 text-green-600 dark:text-green-400 border-green-500/50">
                    <Zap className="h-3 w-3 mr-1" />
                    Unlocked
                  </Badge>
                ) : (
                  <Badge variant="outline" className="border-gray-500/50 text-muted-foreground">
                    <Lock className="h-3 w-3 mr-1" />
                    Locked
                  </Badge>
                )}
              </div>

              {/* Badge Info */}
              <h3 className="font-bold text-lg mb-1">{badge.name}</h3>
              <p className="text-sm text-muted-foreground mb-3">
                {badge.description}
              </p>

              {/* Points */}
              <div className="flex items-center gap-2 mb-3">
                <Trophy className="h-4 w-4 text-yellow-500" />
                <span className="text-sm font-semibold text-yellow-600 dark:text-yellow-400">
                  {badge.points} points
                </span>
              </div>

              {/* Progress */}
              {!badge.earned && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-semibold">
                      {badge.progress}/{badge.threshold} {badge.metric}
                    </span>
                  </div>
                  <Progress value={badge.progress_percentage} className="h-2" />
                  <p className="text-xs text-muted-foreground">
                    {badge.remaining} more {badge.metric} to unlock
                  </p>
                </div>
              )}

              {/* Earned Date */}
              {badge.earned && badge.earned_at && (
                <div className="mt-3 pt-3 border-t border-border">
                  <p className="text-xs text-muted-foreground">
                    Unlocked {new Date(badge.earned_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </p>
                </div>
              )}
            </CardContent>

            {/* Shimmer effect for earned badges */}
            {badge.earned && (
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transform -skew-x-12 animate-shimmer" />
            )}
          </Card>
        ))}
      </div>

      {/* No results */}
      {sortedBadges.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          <Trophy className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p>No achievements in this category</p>
        </div>
      )}
    </div>
  );
};
