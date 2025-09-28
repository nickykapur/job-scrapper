import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Checkbox,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stack,
  Card,
  CardContent,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Architecture as ArchitectureIcon,
  Storage as DatabaseIcon,
  CloudQueue as CloudIcon,
  Security as SecurityIcon,
  Speed as PerformanceIcon,
  AccountTree as MicroservicesIcon,
} from '@mui/icons-material';

interface SystemDesignItem {
  id: string;
  title: string;
  description: string;
  difficulty: 'Foundation' | 'Intermediate' | 'Advanced';
  completed: boolean;
  category: 'concept' | 'practice' | 'deep-dive';
}

interface SystemDesignLevel {
  id: string;
  name: string;
  description: string;
  items: SystemDesignItem[];
  icon: string;
  color: string;
}

// Comprehensive System Design Roadmap based on research and the provided structure
const SYSTEM_DESIGN_ROADMAP: SystemDesignLevel[] = [
  {
    id: 'foundation',
    name: 'Level 1: Foundation',
    description: 'Essential concepts and mindset for system design interviews',
    icon: 'F',
    color: '#2196f3',
    items: [
      {
        id: 'about-tree',
        title: 'About This Roadmap',
        description: 'Understanding how system design interviews work and why preparation matters',
        difficulty: 'Foundation',
        completed: false,
        category: 'concept',
      },
      {
        id: 'expectations-by-level',
        title: 'Expectations by Level',
        description: 'What interviewers look for from junior through staff engineer levels',
        difficulty: 'Foundation',
        completed: false,
        category: 'concept',
      },
      {
        id: 'requirement-collection',
        title: 'Requirement Collection',
        description: 'Extracting functional and non-functional requirements before designing',
        difficulty: 'Foundation',
        completed: false,
        category: 'concept',
      },
      {
        id: 'cap-theorem',
        title: 'CAP Theorem',
        description: 'Understanding consistency, availability, and partition tolerance trade-offs',
        difficulty: 'Foundation',
        completed: false,
        category: 'concept',
      },
      {
        id: 'client-server-basics',
        title: 'Client-Server Architecture',
        description: 'Fundamental request-response patterns and communication protocols',
        difficulty: 'Foundation',
        completed: false,
        category: 'concept',
      },
    ],
  },
  {
    id: 'core-skills',
    name: 'Level 2: Core Skills',
    description: 'Building blocks of scalable distributed systems',
    icon: 'C',
    color: '#ff9800',
    items: [
      {
        id: 'communication-skills',
        title: 'How to Be a Good Communicator',
        description: 'Narrating your thinking process without rambling during interviews',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
      },
      {
        id: 'distributed-communication',
        title: 'Distributed System Communication',
        description: 'Async pub-sub patterns, message queues, and service communication',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
      },
      {
        id: 'api-design',
        title: 'API Design - Should You Do It or Skip It?',
        description: 'When REST APIs help and when they burn interview time',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
      },
      {
        id: 'entity-design',
        title: 'Entity Design',
        description: 'Lean, scalable data models that scale effectively',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
      },
      {
        id: 'database-overview',
        title: 'Database Overview',
        description: 'SQL vs NoSQL, indexing, sharding, and trade-offs',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
      },
      {
        id: 'high-level-design',
        title: 'High-Level Design',
        description: 'The 10,000-foot blueprint that guides every deep dive',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
      },
      {
        id: 'load-balancing',
        title: 'Load Balancing',
        description: 'Distribution strategies and algorithms (round-robin, least connections)',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
      },
      {
        id: 'caching-strategies',
        title: 'Caching Strategies',
        description: 'CDN, Redis, Memcached, and cache invalidation patterns',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
      },
      {
        id: 'scaling-patterns',
        title: 'Horizontal vs Vertical Scaling',
        description: 'When to scale up vs scale out and associated trade-offs',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
      },
    ],
  },
  {
    id: 'mastery',
    name: 'Level 3: Mastery',
    description: 'Advanced patterns and real-world system complexity',
    icon: 'M',
    color: '#4caf50',
    items: [
      {
        id: 'microservice-vs-monolith',
        title: 'Microservice vs Monolith',
        description: 'Splitting vs staying whole with real-world cost/benefit analysis',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
      },
      {
        id: 'deep-dive',
        title: 'Deep Dive Techniques',
        description: 'Moving from big picture to component contracts, layer by layer',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
      },
      {
        id: 'workflow-engines',
        title: 'Workflow Engines',
        description: 'Orchestrating long-running business flows without chaos',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
      },
      {
        id: 'consistency-patterns',
        title: 'Consistency Patterns',
        description: 'Eventual consistency, strong consistency, and ACID properties',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
      },
      {
        id: 'fault-tolerance',
        title: 'Fault Tolerance & Reliability',
        description: 'Circuit breakers, bulkhead patterns, and cascading failure prevention',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
      },
      {
        id: 'data-partitioning',
        title: 'Data Partitioning & Sharding',
        description: 'Horizontal partitioning strategies and shard key selection',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
      },
      {
        id: 'event-driven-architecture',
        title: 'Event-Driven Architecture',
        description: 'Event sourcing, CQRS, and asynchronous processing patterns',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
      },
      {
        id: 'security-design',
        title: 'Security & Authentication',
        description: 'OAuth, JWT, encryption, and security in distributed systems',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
      },
      {
        id: 'monitoring-observability',
        title: 'Monitoring & Observability',
        description: 'Metrics, logging, tracing, and system health monitoring',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
      },
    ],
  },
  {
    id: 'practice',
    name: 'Practice Problems',
    description: 'Real-world system design interview questions',
    icon: 'P',
    color: '#9c27b0',
    items: [
      {
        id: 'design-twitter',
        title: 'Design Twitter/X',
        description: 'Social media platform with feeds, tweets, and real-time updates',
        difficulty: 'Advanced',
        completed: false,
        category: 'practice',
      },
      {
        id: 'design-netflix',
        title: 'Design Netflix',
        description: 'Video streaming service with content delivery and recommendations',
        difficulty: 'Advanced',
        completed: false,
        category: 'practice',
      },
      {
        id: 'design-amazon',
        title: 'Design Amazon E-commerce',
        description: 'Online marketplace with inventory, orders, and payments',
        difficulty: 'Advanced',
        completed: false,
        category: 'practice',
      },
      {
        id: 'design-google-search',
        title: 'Design Google Search',
        description: 'Web search engine with crawling, indexing, and ranking',
        difficulty: 'Advanced',
        completed: false,
        category: 'practice',
      },
      {
        id: 'design-youtube',
        title: 'Design YouTube',
        description: 'Video upload, storage, streaming, and content management',
        difficulty: 'Advanced',
        completed: false,
        category: 'practice',
      },
      {
        id: 'design-uber',
        title: 'Design Uber/Lyft',
        description: 'Ride-sharing platform with real-time location and matching',
        difficulty: 'Advanced',
        completed: false,
        category: 'practice',
      },
      {
        id: 'design-whatsapp',
        title: 'Design WhatsApp',
        description: 'Real-time messaging service with end-to-end encryption',
        difficulty: 'Advanced',
        completed: false,
        category: 'practice',
      },
      {
        id: 'design-rate-limiter',
        title: 'Design Rate Limiter',
        description: 'API rate limiting service with various algorithms',
        difficulty: 'Intermediate',
        completed: false,
        category: 'practice',
      },
      {
        id: 'design-autocomplete',
        title: 'Design Autocomplete/Typeahead',
        description: 'Search suggestion system with fast response times',
        difficulty: 'Intermediate',
        completed: false,
        category: 'practice',
      },
      {
        id: 'design-url-shortener',
        title: 'Design URL Shortener',
        description: 'Service like bit.ly with custom URLs and analytics',
        difficulty: 'Intermediate',
        completed: false,
        category: 'practice',
      },
    ],
  },
];

const LOCAL_STORAGE_KEY = 'system-design-progress';

export const SystemDesign: React.FC = () => {
  const [levels, setLevels] = useState<SystemDesignLevel[]>(SYSTEM_DESIGN_ROADMAP);
  const [expandedLevels, setExpandedLevels] = useState<Set<string>>(new Set(['foundation']));

  // Load progress from localStorage on component mount
  useEffect(() => {
    const savedProgress = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (savedProgress) {
      try {
        const progress = JSON.parse(savedProgress);
        setLevels(prevLevels =>
          prevLevels.map(level => ({
            ...level,
            items: level.items.map(item => ({
              ...item,
              completed: progress[item.id] || false,
            })),
          }))
        );
      } catch (error) {
        console.error('Failed to load system design progress:', error);
      }
    }
  }, []);

  // Save progress to localStorage whenever it changes
  const saveProgress = (updatedLevels: SystemDesignLevel[]) => {
    const progress: Record<string, boolean> = {};
    updatedLevels.forEach(level => {
      level.items.forEach(item => {
        progress[item.id] = item.completed;
      });
    });
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(progress));
  };

  const toggleItemCompletion = (levelId: string, itemId: string) => {
    const updatedLevels = levels.map(level => {
      if (level.id === levelId) {
        return {
          ...level,
          items: level.items.map(item =>
            item.id === itemId ? { ...item, completed: !item.completed } : item
          ),
        };
      }
      return level;
    });
    setLevels(updatedLevels);
    saveProgress(updatedLevels);
  };

  const toggleLevelExpansion = (levelId: string) => {
    setExpandedLevels(prev => {
      const newSet = new Set(prev);
      if (newSet.has(levelId)) {
        newSet.delete(levelId);
      } else {
        newSet.add(levelId);
      }
      return newSet;
    });
  };

  const getLevelProgress = (level: SystemDesignLevel) => {
    const completed = level.items.filter(item => item.completed).length;
    const total = level.items.length;
    return { completed, total, percentage: total > 0 ? (completed / total) * 100 : 0 };
  };

  const getOverallProgress = () => {
    const allItems = levels.flatMap(level => level.items);
    const completedItems = allItems.filter(item => item.completed).length;
    return {
      completed: completedItems,
      total: allItems.length,
      percentage: allItems.length > 0 ? (completedItems / allItems.length) * 100 : 0,
    };
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Foundation': return 'info';
      case 'Intermediate': return 'warning';
      case 'Advanced': return 'error';
      default: return 'default';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'concept': return <ArchitectureIcon fontSize="small" />;
      case 'practice': return <CloudIcon fontSize="small" />;
      case 'deep-dive': return <SecurityIcon fontSize="small" />;
      default: return <ArchitectureIcon fontSize="small" />;
    }
  };

  const overallProgress = getOverallProgress();

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header */}
      <Paper
        sx={{
          p: 3,
          mb: 3,
          borderRadius: 3,
          background: (theme) => theme.palette.mode === 'dark'
            ? 'linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%)'
            : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Stack direction="row" alignItems="center" spacing={2} mb={2}>
          <ArchitectureIcon color="primary" sx={{ fontSize: 32 }} />
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 700, color: 'text.primary' }}>
              System Design Roadmap
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Master system design interviews with this comprehensive roadmap
            </Typography>
          </Box>
        </Stack>

        {/* Overall Progress */}
        <Box sx={{ mt: 2 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="subtitle1" fontWeight={600}>
              Overall Progress
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {overallProgress.completed} / {overallProgress.total} topics completed
            </Typography>
          </Stack>
          <LinearProgress
            variant="determinate"
            value={overallProgress.percentage}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'rgba(0,0,0,0.1)',
              '& .MuiLinearProgress-bar': {
                borderRadius: 4,
                background: 'linear-gradient(90deg, #2196f3 0%, #21cbf3 100%)',
              },
            }}
          />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {overallProgress.percentage.toFixed(1)}% Complete
          </Typography>
        </Box>
      </Paper>

      {/* Learning Levels */}
      <Grid container spacing={2}>
        {levels.map((level) => {
          const progress = getLevelProgress(level);
          return (
            <Grid item xs={12} key={level.id}>
              <Accordion
                expanded={expandedLevels.has(level.id)}
                onChange={() => toggleLevelExpansion(level.id)}
                sx={{
                  borderRadius: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  '&:before': { display: 'none' },
                  '&.Mui-expanded': {
                    margin: 0,
                  },
                }}
              >
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  sx={{
                    backgroundColor: 'background.paper',
                    borderRadius: '8px 8px 0 0',
                    '&.Mui-expanded': {
                      minHeight: 56,
                    },
                    '& .MuiAccordionSummary-content': {
                      margin: '12px 0',
                      '&.Mui-expanded': {
                        margin: '12px 0',
                      },
                    },
                  }}
                >
                  <Stack direction="row" alignItems="center" spacing={2} sx={{ width: '100%', mr: 1 }}>
                    <Box
                      sx={{
                        width: 32,
                        height: 32,
                        borderRadius: 1,
                        backgroundColor: level.color,
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 600,
                        fontSize: '0.875rem',
                      }}
                    >
                      {level.icon}
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" fontWeight={600}>
                        {level.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {level.description}
                      </Typography>
                    </Box>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Chip
                        label={`${progress.completed}/${progress.total}`}
                        size="small"
                        color={progress.completed === progress.total ? 'success' : 'default'}
                        icon={progress.completed === progress.total ? <CheckCircleIcon /> : undefined}
                      />
                      <Typography variant="body2" color="text.secondary" sx={{ minWidth: 40 }}>
                        {progress.percentage.toFixed(0)}%
                      </Typography>
                    </Stack>
                  </Stack>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0 }}>
                  <Box sx={{ mb: 2 }}>
                    <LinearProgress
                      variant="determinate"
                      value={progress.percentage}
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        backgroundColor: 'rgba(0,0,0,0.1)',
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 3,
                          backgroundColor: level.color,
                        },
                      }}
                    />
                  </Box>
                  <List disablePadding>
                    {level.items.map((item) => (
                      <ListItem
                        key={item.id}
                        sx={{
                          borderRadius: 1,
                          mb: 0.5,
                          '&:hover': {
                            backgroundColor: 'action.hover',
                          },
                        }}
                      >
                        <ListItemText
                          primary={
                            <Stack direction="row" alignItems="center" spacing={1}>
                              {getCategoryIcon(item.category)}
                              <Typography
                                variant="body1"
                                sx={{
                                  textDecoration: item.completed ? 'line-through' : 'none',
                                  opacity: item.completed ? 0.7 : 1,
                                }}
                              >
                                {item.title}
                              </Typography>
                              <Chip
                                label={item.difficulty}
                                size="small"
                                color={getDifficultyColor(item.difficulty) as any}
                                variant="outlined"
                              />
                            </Stack>
                          }
                          secondary={
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                              {item.description}
                            </Typography>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Checkbox
                            edge="end"
                            checked={item.completed}
                            onChange={() => toggleItemCompletion(level.id, item.id)}
                            color="success"
                          />
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
};