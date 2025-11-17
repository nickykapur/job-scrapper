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
  Lightbulb,
  AlertCircle,
  Info,
  CheckCircle,
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

interface Insight {
  type: string;
  severity: string;
  icon: string;
  title: string;
  message: string;
  action: string;
}

export const Rewards: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rewards, setRewards] = useState<RewardsData | null>(null);
  const [showBadgeAnimation, setShowBadgeAnimation] = useState(false);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [insightsLoading, setInsightsLoading] = useState(true);

  useEffect(() => {
    loadRewards();
    loadInsights();
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

  const loadInsights = async () => {
    try {
      setInsightsLoading(true);
      const data = await jobApi.getInsights();
      setInsights(data.insights || []);
    } catch (err: any) {
      console.error('Failed to load insights:', err);
    } finally {
      setInsightsLoading(false);
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
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-lg opacity-50"></div>
            <Trophy className="relative w-8 h-8 text-yellow-500" />
          </div>
          <h2 className="text-3xl font-extrabold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            Rewards & Achievements
          </h2>
        </div>
        <p className="text-muted-foreground">
          Track your progress and unlock achievements on your job search journey
        </p>
      </div>

      {/* New Badge Celebration */}
      <AnimatePresence>
        {showBadgeAnimation && rewards.new_badges.length > 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -20 }}
            transition={{ type: "spring", damping: 15 }}
            className="relative overflow-hidden"
          >
            {/* Animated background particles */}
            <div className="absolute inset-0">
              {[...Array(20)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-2 h-2 bg-yellow-400 rounded-full"
                  initial={{
                    x: '50%',
                    y: '50%',
                    scale: 0,
                    opacity: 1
                  }}
                  animate={{
                    x: `${50 + (Math.random() - 0.5) * 100}%`,
                    y: `${50 + (Math.random() - 0.5) * 100}%`,
                    scale: [0, 1, 0],
                    opacity: [1, 0.8, 0]
                  }}
                  transition={{
                    duration: 2,
                    delay: i * 0.05,
                    ease: "easeOut"
                  }}
                  style={{
                    left: '50%',
                    top: '50%'
                  }}
                />
              ))}
            </div>

            <div className="relative p-6 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 border-2 border-blue-500/30 rounded-xl backdrop-blur-sm">
              <div className="text-center space-y-4">
                <div className="flex items-center justify-center gap-2">
                  <motion.div
                    animate={{ rotate: [0, 10, -10, 0] }}
                    transition={{ duration: 0.5, repeat: 3 }}
                  >
                    <Award className="w-8 h-8 text-yellow-500" />
                  </motion.div>
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    New Achievement Unlocked!
                  </h3>
                </div>

                <div className="flex flex-wrap justify-center gap-4">
                  {rewards.new_badges.map((badge, index) => (
                    <motion.div
                      key={badge.id}
                      initial={{ scale: 0, rotate: -180 }}
                      animate={{ scale: 1, rotate: 0 }}
                      transition={{
                        delay: index * 0.2,
                        type: "spring",
                        stiffness: 200
                      }}
                      className="relative group"
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg blur opacity-50 group-hover:opacity-75 transition-opacity"></div>
                      <div className="relative p-4 bg-card border border-blue-500/30 rounded-lg space-y-2">
                        <div className="w-16 h-16 mx-auto bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                          <Award className="w-8 h-8 text-white" />
                        </div>
                        <p className="font-bold">{badge.name}</p>
                        <p className="text-xs text-muted-foreground">{badge.description}</p>
                        <Badge variant="secondary" className="bg-gradient-to-r from-blue-500 to-purple-500 text-white border-0">
                          +{badge.points} points
                        </Badge>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Insights Section */}
      {!insightsLoading && insights.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-yellow-500 rounded-full blur-md opacity-30"></div>
              <Lightbulb className="relative w-6 h-6 text-yellow-500" />
            </div>
            <h3 className="text-xl font-bold">Personalized Insights</h3>
          </div>
          <div className="grid grid-cols-1 gap-3">
            {insights.map((insight, index) => {
              const getSeverityStyle = (severity: string) => {
                switch (severity) {
                  case 'high': return {
                    border: 'border-orange-500/30',
                    bg: 'bg-gradient-to-br from-orange-500/5 to-red-500/5',
                    glow: 'from-orange-500 to-red-500',
                    icon: <AlertCircle className="w-5 h-5 text-orange-500" />
                  };
                  case 'medium': return {
                    border: 'border-blue-500/30',
                    bg: 'bg-gradient-to-br from-blue-500/5 to-cyan-500/5',
                    glow: 'from-blue-500 to-cyan-500',
                    icon: <Info className="w-5 h-5 text-blue-500" />
                  };
                  case 'positive': return {
                    border: 'border-green-500/30',
                    bg: 'bg-gradient-to-br from-green-500/5 to-emerald-500/5',
                    glow: 'from-green-500 to-emerald-500',
                    icon: <CheckCircle className="w-5 h-5 text-green-500" />
                  };
                  default: return {
                    border: 'border-purple-500/30',
                    bg: 'bg-gradient-to-br from-purple-500/5 to-pink-500/5',
                    glow: 'from-purple-500 to-pink-500',
                    icon: <Lightbulb className="w-5 h-5 text-purple-500" />
                  };
                }
              };

              const style = getSeverityStyle(insight.severity);

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1, type: "spring" }}
                  whileHover={{ scale: 1.01, x: 4 }}
                  className="group"
                >
                  <Card className={`border-2 ${style.border} ${style.bg} overflow-hidden relative`}>
                    {/* Animated gradient border glow */}
                    <div className={`absolute inset-0 bg-gradient-to-r ${style.glow} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}></div>

                    <CardContent className="p-4 relative">
                      <div className="flex items-start gap-4">
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: index * 0.1 + 0.2, type: "spring", stiffness: 200 }}
                          className="mt-1"
                        >
                          {style.icon}
                        </motion.div>
                        <div className="flex-1 space-y-2">
                          <h4 className="font-bold text-base">{insight.title}</h4>
                          <p className="text-sm text-muted-foreground leading-relaxed">{insight.message}</p>
                          <div className="flex items-start gap-2 pt-1">
                            <Target className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                            <span className="text-sm font-medium text-primary">{insight.action}</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Level & Points Card */}
        <MotionCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="col-span-1 md:col-span-2 lg:col-span-1 overflow-hidden relative"
        >
          {/* Animated background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-yellow-500/5 via-orange-500/5 to-red-500/5"></div>
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-yellow-500/10 to-orange-500/10 rounded-full blur-3xl"></div>

          <CardHeader className="relative">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <div className="relative">
                  <motion.div
                    animate={{
                      rotate: [0, 5, -5, 0],
                      scale: [1, 1.1, 1]
                    }}
                    transition={{ duration: 3, repeat: Infinity, repeatDelay: 2 }}
                  >
                    <Trophy className="w-5 h-5 text-yellow-500" />
                  </motion.div>
                  <motion.div
                    className="absolute inset-0 bg-yellow-500 rounded-full blur-md opacity-50"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.3, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </div>
                Level & Progress
              </CardTitle>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", delay: 0.2 }}
                className="relative"
              >
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center shadow-lg">
                  <span className="text-xl font-bold text-white">{rewards.level}</span>
                </div>
                <motion.div
                  className="absolute inset-0 rounded-full bg-gradient-to-br from-yellow-500 to-orange-500"
                  animate={{ scale: [1, 1.1, 1], opacity: [0.5, 0, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </motion.div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 relative">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl font-bold">Level {rewards.level}</span>
                <Badge variant="secondary" className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border-yellow-500/30">
                  {rewards.level_name}
                </Badge>
              </div>
              <div className="relative">
                <Progress value={progressPercent} className="h-3" />
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-yellow-500 to-orange-500 opacity-20 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progressPercent}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                />
              </div>
              <div className="flex justify-between text-sm text-muted-foreground mt-2">
                <span className="font-medium">{rewards.points} points</span>
                <span>{rewards.points_to_next_level} to level up</span>
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Star className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm font-medium">Total Points</span>
                </div>
                <motion.span
                  className="text-2xl font-bold bg-gradient-to-r from-yellow-500 to-orange-500 bg-clip-text text-transparent"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", delay: 0.3 }}
                >
                  {rewards.points}
                </motion.span>
              </div>
            </div>
          </CardContent>
        </MotionCard>

        {/* Streak Card */}
        <MotionCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="overflow-hidden relative"
        >
          {/* Animated flame background */}
          <div className="absolute top-0 right-0 w-40 h-40">
            <motion.div
              className={`w-full h-full bg-gradient-to-br ${
                rewards.current_streak >= 30 ? 'from-purple-500/10 to-pink-500/10' :
                rewards.current_streak >= 14 ? 'from-orange-500/10 to-red-500/10' :
                rewards.current_streak >= 7 ? 'from-yellow-500/10 to-orange-500/10' :
                rewards.current_streak >= 3 ? 'from-blue-500/10 to-cyan-500/10' :
                'from-gray-500/10 to-gray-400/10'
              } rounded-full blur-3xl`}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.3, 0.5, 0.3]
              }}
              transition={{ duration: 3, repeat: Infinity }}
            />
          </div>

          <CardHeader className="relative">
            <CardTitle className="flex items-center gap-2">
              <motion.div
                animate={{
                  scale: rewards.current_streak > 0 ? [1, 1.1, 1] : 1,
                }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Flame className={`w-5 h-5 ${getStreakColor(rewards.current_streak)}`} />
              </motion.div>
              Daily Streak
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 relative">
            <div className="text-center">
              <motion.div
                className={`text-5xl font-bold ${getStreakColor(rewards.current_streak)}`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", delay: 0.2 }}
              >
                {rewards.current_streak}
              </motion.div>
              <p className="text-muted-foreground mt-1 text-sm">consecutive days</p>
            </div>

            <div className="pt-4 border-t">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Personal Best</span>
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
        className="overflow-hidden relative"
      >
        {/* Subtle background gradient */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-full blur-3xl"></div>

        <CardHeader className="relative">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 5, repeat: Infinity, repeatDelay: 3 }}
              >
                <Award className="w-5 h-5 text-primary" />
              </motion.div>
              Achievements
              <Badge variant="outline" className="ml-2">{rewards.badges.length}</Badge>
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="relative">
          {rewards.badges.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {rewards.badges.map((badge, index) => {
                const getBadgeIcon = (badgeId: string) => {
                  if (badgeId.includes('first')) return Target;
                  if (badgeId.includes('getting')) return Zap;
                  if (badgeId.includes('hunter')) return TrendingUp;
                  if (badgeId.includes('seeker')) return Star;
                  if (badgeId.includes('master')) return Trophy;
                  if (badgeId.includes('daily')) return Calendar;
                  if (badgeId.includes('week')) return Flame;
                  if (badgeId.includes('month')) return Award;
                  return Award;
                };

                const getBadgeColor = (badgeId: string) => {
                  if (badgeId.includes('first')) return 'from-blue-500 to-cyan-500';
                  if (badgeId.includes('getting')) return 'from-green-500 to-emerald-500';
                  if (badgeId.includes('hunter')) return 'from-yellow-500 to-orange-500';
                  if (badgeId.includes('seeker')) return 'from-purple-500 to-pink-500';
                  if (badgeId.includes('master')) return 'from-red-500 to-rose-500';
                  if (badgeId.includes('daily')) return 'from-cyan-500 to-blue-500';
                  if (badgeId.includes('week')) return 'from-orange-500 to-red-500';
                  if (badgeId.includes('month')) return 'from-violet-500 to-purple-500';
                  return 'from-gray-500 to-gray-600';
                };

                const Icon = getBadgeIcon(badge.id);
                const colorClass = getBadgeColor(badge.id);

                return (
                  <motion.div
                    key={badge.id}
                    initial={{ opacity: 0, scale: 0.8, rotateY: -180 }}
                    animate={{ opacity: 1, scale: 1, rotateY: 0 }}
                    transition={{
                      delay: index * 0.05,
                      type: "spring",
                      stiffness: 150
                    }}
                    whileHover={{ scale: 1.05, y: -5 }}
                    className="group relative"
                  >
                    {/* Glow effect on hover */}
                    <div className={`absolute inset-0 bg-gradient-to-br ${colorClass} rounded-xl blur opacity-0 group-hover:opacity-30 transition-opacity duration-300`}></div>

                    <div className="relative p-4 border-2 border-border/50 rounded-xl bg-card/50 backdrop-blur-sm hover:border-primary/30 transition-colors">
                      <div className="text-center space-y-3">
                        {/* Badge icon with gradient background */}
                        <div className="mx-auto">
                          <motion.div
                            className={`w-14 h-14 mx-auto rounded-full bg-gradient-to-br ${colorClass} flex items-center justify-center shadow-lg`}
                            whileHover={{ rotate: 360 }}
                            transition={{ duration: 0.6 }}
                          >
                            <Icon className="w-7 h-7 text-white" />
                          </motion.div>
                        </div>

                        <div className="space-y-1">
                          <h4 className="font-bold text-sm">{badge.name}</h4>
                          <p className="text-xs text-muted-foreground line-clamp-2">{badge.description}</p>
                        </div>

                        <Badge
                          variant="secondary"
                          className={`text-xs bg-gradient-to-r ${colorClass} text-white border-0`}
                        >
                          +{badge.points} pts
                        </Badge>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12 text-muted-foreground"
            >
              <motion.div
                animate={{
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{ duration: 3, repeat: Infinity }}
              >
                <Award className="w-16 h-16 mx-auto mb-4 opacity-30" />
              </motion.div>
              <p className="text-base">No achievements unlocked yet</p>
              <p className="text-sm mt-2">Keep applying to jobs to earn your first badge!</p>
            </motion.div>
          )}
        </CardContent>
      </MotionCard>
    </div>
  );
};

export default Rewards;
