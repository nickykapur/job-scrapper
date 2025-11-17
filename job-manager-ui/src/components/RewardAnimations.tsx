import React from 'react';
import { motion } from 'framer-motion';

// Circular Progress Ring SVG
export const CircularProgress: React.FC<{
  progress: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
}> = ({ progress, size = 120, strokeWidth = 8, color = '#3b82f6' }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <svg width={size} height={size} className="transform -rotate-90">
      {/* Background circle */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke="currentColor"
        strokeWidth={strokeWidth}
        fill="none"
        className="text-muted opacity-20"
      />
      {/* Progress circle */}
      <motion.circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke={color}
        strokeWidth={strokeWidth}
        fill="none"
        strokeLinecap="round"
        strokeDasharray={circumference}
        initial={{ strokeDashoffset: circumference }}
        animate={{ strokeDashoffset: offset }}
        transition={{ duration: 1, ease: "easeOut" }}
      />
    </svg>
  );
};

// Animated Trophy SVG
export const AnimatedTrophy: React.FC<{
  level: number;
  size?: number;
}> = ({ level, size = 64 }) => {
  const getTrophyColor = (level: number) => {
    if (level >= 8) return { primary: '#e879f9', secondary: '#c026d3', glow: '#f0abfc' }; // Purple (Elite)
    if (level >= 7) return { primary: '#fbbf24', secondary: '#f59e0b', glow: '#fcd34d' }; // Gold (Legend)
    if (level >= 5) return { primary: '#60a5fa', secondary: '#3b82f6', glow: '#93c5fd' }; // Blue (Pro)
    if (level >= 3) return { primary: '#34d399', secondary: '#10b981', glow: '#6ee7b7' }; // Green (Seeker)
    return { primary: '#9ca3af', secondary: '#6b7280', glow: '#d1d5db' }; // Gray (Beginner)
  };

  const colors = getTrophyColor(level);

  return (
    <motion.svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.5, type: "spring" }}
    >
      <defs>
        <linearGradient id={`trophyGradient-${level}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={colors.primary} />
          <stop offset="100%" stopColor={colors.secondary} />
        </linearGradient>
        <filter id={`glow-${level}`}>
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      {/* Glow effect */}
      <motion.circle
        cx="32"
        cy="32"
        r="28"
        fill={colors.glow}
        opacity="0.3"
        animate={{ scale: [1, 1.1, 1], opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 2, repeat: Infinity }}
      />

      {/* Trophy base */}
      <motion.rect
        x="26"
        y="50"
        width="12"
        height="8"
        rx="2"
        fill={`url(#trophyGradient-${level})`}
        filter={`url(#glow-${level})`}
      />

      {/* Trophy stem */}
      <motion.rect
        x="30"
        y="42"
        width="4"
        height="8"
        fill={`url(#trophyGradient-${level})`}
      />

      {/* Trophy cup */}
      <motion.path
        d="M 20 12 L 18 28 Q 18 36 24 38 L 28 42 L 36 42 L 40 38 Q 46 36 46 28 L 44 12 Z"
        fill={`url(#trophyGradient-${level})`}
        filter={`url(#glow-${level})`}
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1, ease: "easeOut" }}
      />

      {/* Trophy handles */}
      <motion.path
        d="M 18 16 Q 12 16 12 22 Q 12 26 16 26 L 18 26"
        stroke={colors.primary}
        strokeWidth="2"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.8, delay: 0.3 }}
      />
      <motion.path
        d="M 46 16 Q 52 16 52 22 Q 52 26 48 26 L 46 26"
        stroke={colors.primary}
        strokeWidth="2"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.8, delay: 0.3 }}
      />

      {/* Stars for high levels */}
      {level >= 5 && (
        <motion.g
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.8, type: "spring" }}
        >
          <path
            d="M 32 8 L 34 14 L 40 14 L 35 18 L 37 24 L 32 20 L 27 24 L 29 18 L 24 14 L 30 14 Z"
            fill={colors.glow}
          />
        </motion.g>
      )}
    </motion.svg>
  );
};

// Animated Flame for Streaks
export const AnimatedFlame: React.FC<{
  streakDays: number;
  size?: number;
}> = ({ streakDays, size = 48 }) => {
  const getFlameColors = (days: number) => {
    if (days >= 30) return { primary: '#a855f7', secondary: '#c026d3', particles: '#e879f9' }; // Purple
    if (days >= 14) return { primary: '#f97316', secondary: '#ea580c', particles: '#fb923c' }; // Orange
    if (days >= 7) return { primary: '#eab308', secondary: '#ca8a04', particles: '#fde047' }; // Yellow
    if (days >= 3) return { primary: '#3b82f6', secondary: '#2563eb', particles: '#60a5fa' }; // Blue
    return { primary: '#9ca3af', secondary: '#6b7280', particles: '#d1d5db' }; // Gray
  };

  const colors = getFlameColors(streakDays);

  return (
    <motion.svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      animate={{ scale: [1, 1.05, 1] }}
      transition={{ duration: 1.5, repeat: Infinity }}
    >
      <defs>
        <linearGradient id={`flameGradient-${streakDays}`} x1="0%" y1="100%" x2="0%" y2="0%">
          <stop offset="0%" stopColor={colors.primary} />
          <stop offset="100%" stopColor={colors.secondary} />
        </linearGradient>
      </defs>

      {/* Flame particles */}
      {streakDays >= 3 && (
        <>
          <motion.circle
            cx="24"
            cy="10"
            r="2"
            fill={colors.particles}
            animate={{
              y: [-5, -15, -5],
              opacity: [0, 1, 0],
              scale: [0, 1, 0]
            }}
            transition={{ duration: 2, repeat: Infinity, delay: 0 }}
          />
          <motion.circle
            cx="18"
            cy="14"
            r="1.5"
            fill={colors.particles}
            animate={{
              y: [-3, -10, -3],
              opacity: [0, 1, 0],
              scale: [0, 1, 0]
            }}
            transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
          />
          <motion.circle
            cx="30"
            cy="14"
            r="1.5"
            fill={colors.particles}
            animate={{
              y: [-3, -10, -3],
              opacity: [0, 1, 0],
              scale: [0, 1, 0]
            }}
            transition={{ duration: 2, repeat: Infinity, delay: 1 }}
          />
        </>
      )}

      {/* Main flame */}
      <motion.path
        d="M 24 4 Q 18 10 18 18 Q 18 26 24 32 Q 30 26 30 18 Q 30 10 24 4 Z"
        fill={`url(#flameGradient-${streakDays})`}
        animate={{
          d: [
            "M 24 4 Q 18 10 18 18 Q 18 26 24 32 Q 30 26 30 18 Q 30 10 24 4 Z",
            "M 24 6 Q 19 11 19 18 Q 19 25 24 30 Q 29 25 29 18 Q 29 11 24 6 Z",
            "M 24 4 Q 18 10 18 18 Q 18 26 24 32 Q 30 26 30 18 Q 30 10 24 4 Z"
          ]
        }}
        transition={{ duration: 1.5, repeat: Infinity }}
      />

      {/* Inner flame */}
      <motion.path
        d="M 24 12 Q 21 15 21 20 Q 21 24 24 27 Q 27 24 27 20 Q 27 15 24 12 Z"
        fill={colors.particles}
        opacity="0.8"
        animate={{
          d: [
            "M 24 12 Q 21 15 21 20 Q 21 24 24 27 Q 27 24 27 20 Q 27 15 24 12 Z",
            "M 24 13 Q 22 16 22 20 Q 22 23 24 26 Q 26 23 26 20 Q 26 16 24 13 Z",
            "M 24 12 Q 21 15 21 20 Q 21 24 24 27 Q 27 24 27 20 Q 27 15 24 12 Z"
          ]
        }}
        transition={{ duration: 1.2, repeat: Infinity }}
      />

      {/* Flame base */}
      <ellipse
        cx="24"
        cy="32"
        rx="8"
        ry="3"
        fill={colors.primary}
        opacity="0.3"
      />
    </motion.svg>
  );
};

// Badge Unlock Animation
export const BadgeUnlockAnimation: React.FC<{
  icon: string;
  onComplete?: () => void;
}> = ({ icon, onComplete }) => {
  return (
    <motion.div
      className="relative"
      initial={{ scale: 0, rotate: -180 }}
      animate={{ scale: 1, rotate: 0 }}
      transition={{
        duration: 0.6,
        type: "spring",
        stiffness: 200
      }}
      onAnimationComplete={onComplete}
    >
      {/* Burst rays */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute top-1/2 left-1/2 w-1 h-8 bg-gradient-to-t from-yellow-400 to-transparent"
          style={{
            transformOrigin: 'top',
            transform: `rotate(${i * 45}deg) translateY(-50%)`,
          }}
          initial={{ scaleY: 0, opacity: 0 }}
          animate={{ scaleY: 1, opacity: [0, 1, 0] }}
          transition={{
            duration: 0.8,
            delay: 0.3 + i * 0.05,
            ease: "easeOut"
          }}
        />
      ))}

      {/* Badge circle background */}
      <motion.div
        className="relative z-10 w-24 h-24 rounded-full bg-gradient-to-br from-yellow-400 via-orange-400 to-red-500 flex items-center justify-center shadow-lg"
        animate={{
          boxShadow: [
            '0 0 20px rgba(251, 191, 36, 0.5)',
            '0 0 40px rgba(251, 191, 36, 0.8)',
            '0 0 20px rgba(251, 191, 36, 0.5)',
          ]
        }}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        <span className="text-4xl">{icon}</span>
      </motion.div>

      {/* Sparkles */}
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={`sparkle-${i}`}
          className="absolute w-2 h-2 bg-yellow-300 rounded-full"
          style={{
            top: '50%',
            left: '50%',
          }}
          initial={{ scale: 0, x: 0, y: 0 }}
          animate={{
            scale: [0, 1, 0],
            x: Math.cos((i * 30) * Math.PI / 180) * (40 + Math.random() * 20),
            y: Math.sin((i * 30) * Math.PI / 180) * (40 + Math.random() * 20),
          }}
          transition={{
            duration: 1,
            delay: 0.2 + i * 0.05,
            ease: "easeOut"
          }}
        />
      ))}
    </motion.div>
  );
};

// Tier Badge SVG (Bronze, Silver, Gold, Platinum)
export const TierBadge: React.FC<{
  tier: 'bronze' | 'silver' | 'gold' | 'platinum';
  size?: number;
}> = ({ tier, size = 40 }) => {
  const tierColors = {
    bronze: { primary: '#cd7f32', secondary: '#8b5a2b', glow: '#e6a75f' },
    silver: { primary: '#c0c0c0', secondary: '#808080', glow: '#e8e8e8' },
    gold: { primary: '#ffd700', secondary: '#daa520', glow: '#ffed4e' },
    platinum: { primary: '#e5e4e2', secondary: '#b0b0b0', glow: '#ffffff' },
  };

  const colors = tierColors[tier];

  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <defs>
        <linearGradient id={`tierGradient-${tier}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={colors.glow} />
          <stop offset="50%" stopColor={colors.primary} />
          <stop offset="100%" stopColor={colors.secondary} />
        </linearGradient>
        <filter id={`tierGlow-${tier}`}>
          <feGaussianBlur stdDeviation="1.5"/>
        </filter>
      </defs>

      {/* Badge shape (hexagon) */}
      <motion.path
        d="M 20 2 L 35 11 L 35 29 L 20 38 L 5 29 L 5 11 Z"
        fill={`url(#tierGradient-${tier})`}
        stroke={colors.glow}
        strokeWidth="1"
        filter={`url(#tierGlow-${tier})`}
        initial={{ scale: 0, rotate: -45 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 200 }}
      />

      {/* Inner decoration */}
      <motion.circle
        cx="20"
        cy="20"
        r="10"
        fill="none"
        stroke={colors.glow}
        strokeWidth="1"
        opacity="0.6"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2 }}
      />

      {/* Tier initial */}
      <text
        x="20"
        y="26"
        textAnchor="middle"
        fontSize="14"
        fontWeight="bold"
        fill="#1f2937"
      >
        {tier[0].toUpperCase()}
      </text>
    </svg>
  );
};
