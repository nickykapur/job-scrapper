import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Trophy,
  Flame,
  Star,
  TrendingUp,
  Award,
  Zap,
  Target,
  Calendar,
} from 'lucide-react';
import { jobApi } from '../services/api';
import {
  CircularProgress,
  AnimatedTrophy,
  AnimatedFlame,
  BadgeUnlockAnimation,
  TierBadge,
} from './RewardAnimations';

const MotionCard = motion(Card);

interface RewardsData {
  points: number;
  level: number;
  level_name: string;
  level_icon: string;
  next_level_points: number;
  points_to_next_level: number;
  current_streak: number;
  longest_streak: number;
  badges: Array<{
    id: string;
    name: string;
    description: string;
    points: number;
    earned_at: string;
  }>;
  new_badges: Array<{
    id: string;
    name: string;
    description: string;
    icon: string;
    points: number;
  }>;
  stats: {
    total_applied: number;
    total_saved: number;
    total_rejected: number;
    applied_today: number;
    applied_last_7_days: number;
    active_days: number;
    countries_explored: number;
  };
}

const getStreakColor = (streak: number) => {
  if (streak >= 30) return 'text-purple-500';
  if (streak >= 14) return 'text-orange-500';
  if (streak >= 7) return 'text-yellow-500';
  if (streak >= 3) return 'text-blue-500';
  return 'text-gray-400';
};

export const Rewards: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rewards, setRewards] = useState<RewardsData | null>(null);
  const [showBadgeAnimation, setShowBadgeAnimation] = useState(false);

  useEffect(() => {
    loadRewards();
  }, []);

  const loadRewards = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await jobApi.getRewards();
      setRewards(data);

      // Show animation if new badges were earned
      if (data.new_badges && data.new_badges.length > 0) {
        setShowBadgeAnimation(true);
        setTimeout(() => setShowBadgeAnimation(false), 5000);
      }
    } catch (err: any) {
      console.error('Failed to load rewards:', err);
      setError(err.response?.data?.detail || 'Failed to load rewards');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Rewards & Achievements</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="h-[200px] animate-pulse bg-muted/50" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !rewards) {
    return (
      <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
        {error || 'Failed to load rewards'}
      </div>
    );
  }

  const progressPercent = ((rewards.points / rewards.next_level_points) * 100);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-3xl font-extrabold bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500 bg-clip-text text-transparent">
          🏆 Rewards & Achievements
        </h2>
        <p className="text-muted-foreground">
          Track your progress and earn badges for your job search journey
        </p>
      </div>

      {/* New Badge Celebration */}
      <AnimatePresence>
        {showBadgeAnimation && rewards.new_badges.length > 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: -20 }}
            className="p-6 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border-2 border-yellow-500 rounded-lg"
          >
            <div className="text-center space-y-3">
              <h3 className="text-2xl font-bold">🎉 New Badge Unlocked!</h3>
              <div className="flex flex-wrap justify-center gap-4">
                {rewards.new_badges.map((badge) => (
                  <div key={badge.id} className="text-center">
                    <div className="text-4xl">{badge.icon}</div>
                    <p className="font-bold mt-2">{badge.name}</p>
                    <p className="text-sm text-muted-foreground">{badge.description}</p>
                    <Badge variant="secondary" className="mt-1">+{badge.points} points</Badge>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Level & Points Card */}
        <MotionCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="col-span-1 md:col-span-2 lg:col-span-1"
        >
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Trophy className="w-5 h-5 text-yellow-500" />
                Level & Progress
              </CardTitle>
              <span className="text-3xl">{rewards.level_icon}</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl font-bold">Level {rewards.level}</span>
                <Badge variant="secondary">{rewards.level_name}</Badge>
              </div>
              <Progress value={progressPercent} className="h-3" />
              <div className="flex justify-between text-sm text-muted-foreground mt-2">
                <span>{rewards.points} points</span>
                <span>{rewards.points_to_next_level} to next level</span>
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Star className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm font-medium">Total Points</span>
                </div>
                <span className="text-2xl font-bold text-yellow-500">{rewards.points}</span>
              </div>
            </div>
          </CardContent>
        </MotionCard>

        {/* Streak Card */}
        <MotionCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Flame className={`w-5 h-5 ${getStreakColor(rewards.current_streak)}`} />
              Daily Streak
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <div className={`text-5xl font-bold ${getStreakColor(rewards.current_streak)}`}>
                {rewards.current_streak}
              </div>
              <p className="text-muted-foreground mt-1">Days in a row</p>
            </div>

            <div className="pt-4 border-t">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Longest Streak</span>
                <span className="font-bold flex items-center gap-1">
                  <Trophy className="w-4 h-4 text-purple-500" />
                  {rewards.longest_streak} days
                </span>
              </div>
            </div>
          </CardContent>
        </MotionCard>

        {/* Quick Stats Card */}
        <MotionCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              Quick Stats
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Applied Today</span>
              <Badge variant="default">{rewards.stats.applied_today}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Last 7 Days</span>
              <Badge variant="secondary">{rewards.stats.applied_last_7_days}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Active Days</span>
              <Badge variant="outline">{rewards.stats.active_days}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Countries</span>
              <Badge variant="outline">{rewards.stats.countries_explored}</Badge>
            </div>
          </CardContent>
        </MotionCard>
      </div>

      {/* Badges Section */}
      <MotionCard
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5 text-primary" />
              Earned Badges ({rewards.badges.length})
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {rewards.badges.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {rewards.badges.map((badge, index) => (
                <motion.div
                  key={badge.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-4 border rounded-lg hover:shadow-lg transition-all hover:-translate-y-1"
                >
                  <div className="text-center space-y-2">
                    <div className="text-4xl">
                      {badge.id.includes('first') && '🎯'}
                      {badge.id.includes('getting') && '🚀'}
                      {badge.id.includes('hunter') && '💼'}
                      {badge.id.includes('seeker') && '⭐'}
                      {badge.id.includes('master') && '👑'}
                      {badge.id.includes('daily') && '📅'}
                      {badge.id.includes('week') && '🎯'}
                      {badge.id.includes('month') && '💪'}
                    </div>
                    <h4 className="font-bold text-sm">{badge.name}</h4>
                    <p className="text-xs text-muted-foreground">{badge.description}</p>
                    <Badge variant="secondary" className="text-xs">+{badge.points} pts</Badge>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Award className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No badges earned yet. Keep applying to jobs to unlock achievements!</p>
            </div>
          )}
        </CardContent>
      </MotionCard>
    </div>
  );
};

export default Rewards;
