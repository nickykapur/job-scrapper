import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import {
  Trophy,
  Flame,
  Star,
  Target,
  Award,
  TrendingUp,
  Sparkles,
  ChevronRight,
} from 'lucide-react';
import { jobApi } from '../services/api';
import toast from 'react-hot-toast';

interface BadgeData {
  id: string;
  name: string;
  description: string;
  points: number;
  threshold: number;
  icon: string;
  earned: boolean;
  earned_at?: string;
  progress: number;
  progress_percentage: number;
  remaining: number;
}

interface RewardsData {
  points: number;
  level: number;
  level_name: string;
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
  all_badges?: BadgeData[];
  stats: {
    total_applied: number;
    applied_today: number;
    applied_last_7_days: number;
  };
}

export const RewardsRevamped: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [rewards, setRewards] = useState<RewardsData | null>(null);
  const [previousRewards, setPreviousRewards] = useState<RewardsData | null>(null);

  useEffect(() => {
    loadRewards();

    // Poll for updates every 30 seconds to detect new achievements
    const interval = setInterval(checkForNewAchievements, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadRewards = async () => {
    try {
      setLoading(true);
      const data = await jobApi.getRewards();

      // Check for new badges (only if we have previous data)
      if (previousRewards && data.badges.length > previousRewards.badges.length) {
        const newBadges = data.badges.filter(
          newBadge => !previousRewards.badges.some(old => old.id === newBadge.id)
        );

        newBadges.forEach(badge => {
          showAchievementToast(badge);
        });
      }

      // Check for level up
      if (previousRewards && data.level > previousRewards.level) {
        showLevelUpToast(data.level, data.level_name);
      }

      setPreviousRewards(rewards);
      setRewards(data);
    } catch (err: any) {
      console.error('Failed to load rewards:', err);
    } finally {
      setLoading(false);
    }
  };

  const checkForNewAchievements = async () => {
    try {
      const data = await jobApi.getRewards();

      if (!rewards) return;

      // New badge check
      if (data.badges.length > rewards.badges.length) {
        const newBadges = data.badges.filter(
          newBadge => !rewards.badges.some(old => old.id === newBadge.id)
        );
        newBadges.forEach(badge => showAchievementToast(badge));
      }

      // Level up check
      if (data.level > rewards.level) {
        showLevelUpToast(data.level, data.level_name);
      }

      setRewards(data);
    } catch (err) {
      console.error('Failed to check achievements:', err);
    }
  };

  const showAchievementToast = (badge: any) => {
    toast.custom((t) => (
      <div
        className={`${
          t.visible ? 'animate-enter' : 'animate-leave'
        } max-w-md w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg pointer-events-auto flex ring-2 ring-blue-500`}
      >
        <div className="flex-1 w-0 p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0 pt-0.5">
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                <Award className="h-6 w-6 text-white" />
              </div>
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-bold text-gray-900 dark:text-white">
                🎉 Achievement Unlocked!
              </p>
              <p className="mt-1 text-sm font-semibold text-blue-600 dark:text-blue-400">
                {badge.name}
              </p>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                +{badge.points} points
              </p>
            </div>
          </div>
        </div>
        <div className="flex border-l border-gray-200 dark:border-gray-700">
          <button
            onClick={() => toast.dismiss(t.id)}
            className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            Close
          </button>
        </div>
      </div>
    ), {
      duration: 6000,
      position: 'top-right',
    });

    // Play sound (optional) - removed for now, can add later with proper sound file
  };

  const showLevelUpToast = (level: number, levelName: string) => {
    toast.custom((t) => (
      <div
        className={`${
          t.visible ? 'animate-enter' : 'animate-leave'
        } max-w-md w-full bg-gradient-to-r from-yellow-400 to-orange-500 shadow-lg rounded-lg pointer-events-auto flex ring-2 ring-yellow-500`}
      >
        <div className="flex-1 w-0 p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0 pt-0.5">
              <div className="h-10 w-10 rounded-full bg-white flex items-center justify-center">
                <Trophy className="h-6 w-6 text-yellow-500" />
              </div>
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-bold text-white">
                🔥 LEVEL UP!
              </p>
              <p className="mt-1 text-sm font-semibold text-white">
                Level {level} - {levelName}
              </p>
              <p className="mt-1 text-xs text-yellow-100">
                Keep crushing it!
              </p>
            </div>
          </div>
        </div>
        <div className="flex border-l border-yellow-600">
          <button
            onClick={() => toast.dismiss(t.id)}
            className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-white hover:text-yellow-100"
          >
            Close
          </button>
        </div>
      </div>
    ), {
      duration: 8000,
      position: 'top-right',
    });
  };

  if (loading || !rewards) {
    return (
      <div className="space-y-4">
        <Card className="h-32 animate-pulse bg-muted/50" />
        <Card className="h-48 animate-pulse bg-muted/50" />
      </div>
    );
  }

  const progressPercent = (rewards.points / rewards.next_level_points) * 100;

  // Get next achievement
  const nextBadge = rewards.all_badges
    ?.filter(b => !b.earned && b.remaining > 0)
    .sort((a, b) => a.remaining - b.remaining)[0];

  // Get recent achievements (last 4)
  const recentBadges = [...rewards.badges]
    .sort((a, b) => new Date(b.earned_at).getTime() - new Date(a.earned_at).getTime())
    .slice(0, 4);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold">Rewards</h2>
        <p className="text-muted-foreground mt-1">Track your progress and achievements</p>
      </div>

      {/* Progress Hero */}
      <Card className="border-2">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Level Progress */}
            <div className="md:col-span-2 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center">
                    <span className="text-xl font-bold text-white">{rewards.level}</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">Level {rewards.level}</h3>
                    <p className="text-sm text-muted-foreground">{rewards.level_name}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-yellow-600">{rewards.points}</div>
                  <p className="text-xs text-muted-foreground">points</p>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Progress to next level</span>
                  <span className="font-medium">{rewards.points_to_next_level} points left</span>
                </div>
                <Progress value={progressPercent} className="h-2" />
              </div>
            </div>

            {/* Current Streak */}
            <div className="flex flex-col items-center justify-center border-l pl-6">
              <Flame className={`w-8 h-8 mb-2 ${
                rewards.current_streak >= 7 ? 'text-orange-500' :
                rewards.current_streak >= 3 ? 'text-yellow-500' :
                'text-gray-400'
              }`} />
              <div className="text-4xl font-bold">{rewards.current_streak}</div>
              <p className="text-sm text-muted-foreground">day streak</p>
              <p className="text-xs text-muted-foreground mt-1">Best: {rewards.longest_streak}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Active Goal */}
      {nextBadge && (
        <Card className="border-2 border-blue-500/50 bg-blue-50/50 dark:bg-blue-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-500" />
              Active Goal
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="text-4xl">{nextBadge.icon}</div>
                <div className="flex-1">
                  <h3 className="font-bold text-lg">{nextBadge.name}</h3>
                  <p className="text-sm text-muted-foreground">{nextBadge.description}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Progress value={nextBadge.progress_percentage} className="h-2 w-48" />
                    <span className="text-sm font-medium">
                      {nextBadge.progress}/{nextBadge.threshold}
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">{nextBadge.remaining}</div>
                <p className="text-xs text-muted-foreground">to go</p>
                <Badge className="mt-2">+{nextBadge.points} pts</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Achievements */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5" />
              Recent Achievements
            </CardTitle>
            {rewards.badges.length > 0 && (
              <Button variant="ghost" size="sm">
                View All
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {recentBadges.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {recentBadges.map((badge, index) => (
                <motion.div
                  key={badge.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="text-center p-4 border rounded-lg hover:shadow-md transition-shadow"
                >
                  <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                    <Award className="w-6 h-6 text-white" />
                  </div>
                  <h4 className="font-semibold text-sm">{badge.name}</h4>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                    {badge.description}
                  </p>
                  <Badge variant="secondary" className="mt-2 text-xs">
                    +{badge.points}
                  </Badge>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Award className="w-12 h-12 mx-auto mb-2 opacity-30" />
              <p>No achievements yet</p>
              <p className="text-sm mt-1">Apply to jobs to start earning!</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{rewards.stats.applied_today}</div>
            <p className="text-xs text-muted-foreground mt-1">Applied Today</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">{rewards.stats.applied_last_7_days}</div>
            <p className="text-xs text-muted-foreground mt-1">Last 7 Days</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{rewards.badges.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Achievements</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
