import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { motion } from 'framer-motion';
import {
  Building2,
  CheckCircle,
  ExternalLink,
  FileText,
  Video,
  Code,
  BookOpen,
} from 'lucide-react';

interface SystemDesignItem {
  id: string;
  title: string;
  description: string;
  difficulty: 'Foundation' | 'Intermediate' | 'Advanced';
  completed: boolean;
  category: 'concept' | 'practice' | 'deep-dive';
  resources: {
    articles?: string[];
    videos?: string[];
    github?: string[];
    tutorials?: string[];
  };
}

interface SystemDesignLevel {
  id: string;
  name: string;
  description: string;
  items: SystemDesignItem[];
  icon: string;
  color: string;
}

// System Design Roadmap
const SYSTEM_DESIGN_ROADMAP: SystemDesignLevel[] = [
  {
    id: 'foundation',
    name: 'Level 1: Foundation',
    description: 'Essential concepts and mindset for system design interviews',
    icon: 'F',
    color: 'hsl(var(--chart-1))',
    items: [
      {
        id: 'about-tree',
        title: 'About This Roadmap',
        description: 'Understanding how system design interviews work and why preparation matters',
        difficulty: 'Foundation',
        completed: false,
        category: 'concept',
        resources: {
          articles: [
            'https://github.com/donnemartin/system-design-primer',
            'https://www.educative.io/guide/complete-guide-to-system-design'
          ],
          tutorials: [
            'https://www.geeksforgeeks.org/system-design/system-design-tutorial/'
          ]
        }
      },
      {
        id: 'cap-theorem',
        title: 'CAP Theorem',
        description: 'Understanding consistency, availability, and partition tolerance trade-offs',
        difficulty: 'Foundation',
        completed: false,
        category: 'concept',
        resources: {
          articles: [
            'https://dev.to/karanpratapsingh/system-design-cap-theorem-2n9j'
          ],
          github: [
            'https://github.com/Devinterview-io/cap-theorem-interview-questions'
          ]
        }
      },
      {
        id: 'client-server-basics',
        title: 'Client-Server Architecture',
        description: 'Fundamental request-response patterns and communication protocols',
        difficulty: 'Foundation',
        completed: false,
        category: 'concept',
        resources: {
          tutorials: [
            'https://www.geeksforgeeks.org/system-design/getting-started-with-system-design/'
          ]
        }
      },
    ],
  },
  {
    id: 'core-skills',
    name: 'Level 2: Core Skills',
    description: 'Building blocks of scalable distributed systems',
    icon: 'C',
    color: 'hsl(var(--chart-2))',
    items: [
      {
        id: 'distributed-communication',
        title: 'Distributed System Communication',
        description: 'Async pub-sub patterns, message queues, and service communication',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
        resources: {},
      },
      {
        id: 'database-overview',
        title: 'Database Overview',
        description: 'SQL vs NoSQL, indexing, sharding, and trade-offs',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
        resources: {},
      },
      {
        id: 'load-balancing',
        title: 'Load Balancing',
        description: 'Distribution strategies and algorithms (round-robin, least connections)',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
        resources: {},
      },
      {
        id: 'caching-strategies',
        title: 'Caching Strategies',
        description: 'CDN, Redis, Memcached, and cache invalidation patterns',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
        resources: {
          articles: [
            'https://www.geeksforgeeks.org/caching-system-design-concept-for-beginners/'
          ],
          github: [
            'https://github.com/ashishps1/awesome-system-design-resources'
          ]
        },
      },
      {
        id: 'scaling-patterns',
        title: 'Horizontal vs Vertical Scaling',
        description: 'When to scale up vs scale out and associated trade-offs',
        difficulty: 'Intermediate',
        completed: false,
        category: 'concept',
        resources: {},
      },
    ],
  },
  {
    id: 'mastery',
    name: 'Level 3: Mastery',
    description: 'Advanced patterns and real-world system complexity',
    icon: 'M',
    color: 'hsl(var(--chart-3))',
    items: [
      {
        id: 'microservice-vs-monolith',
        title: 'Microservice vs Monolith',
        description: 'Splitting vs staying whole with real-world cost/benefit analysis',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
        resources: {},
      },
      {
        id: 'consistency-patterns',
        title: 'Consistency Patterns',
        description: 'Eventual consistency, strong consistency, and ACID properties',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
        resources: {},
      },
      {
        id: 'fault-tolerance',
        title: 'Fault Tolerance & Reliability',
        description: 'Circuit breakers, bulkhead patterns, and cascading failure prevention',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
        resources: {},
      },
      {
        id: 'event-driven-architecture',
        title: 'Event-Driven Architecture',
        description: 'Event sourcing, CQRS, and asynchronous processing patterns',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
        resources: {},
      },
      {
        id: 'security-design',
        title: 'Security & Authentication',
        description: 'OAuth, JWT, encryption, and security in distributed systems',
        difficulty: 'Advanced',
        completed: false,
        category: 'deep-dive',
        resources: {},
      },
    ],
  },
  {
    id: 'practice',
    name: 'Practice Problems',
    description: 'Real-world system design interview questions',
    icon: 'P',
    color: 'hsl(var(--chart-4))',
    items: [
      {
        id: 'design-twitter',
        title: 'Design Twitter/X',
        description: 'Social media platform with feeds, tweets, and real-time updates',
        difficulty: 'Advanced',
        completed: false,
        category: 'practice',
        resources: {
          github: [
            'https://github.com/donnemartin/system-design-primer#design-the-twitter-timeline-and-search'
          ]
        },
      },
      {
        id: 'design-uber',
        title: 'Design Uber/Lyft',
        description: 'Ride-sharing platform with real-time location and matching',
        difficulty: 'Advanced',
        completed: false,
        category: 'practice',
        resources: {},
      },
      {
        id: 'design-rate-limiter',
        title: 'Design Rate Limiter',
        description: 'API rate limiting service with various algorithms',
        difficulty: 'Intermediate',
        completed: false,
        category: 'practice',
        resources: {},
      },
      {
        id: 'design-url-shortener',
        title: 'Design URL Shortener',
        description: 'Service like bit.ly with custom URLs and analytics',
        difficulty: 'Intermediate',
        completed: false,
        category: 'practice',
        resources: {},
      },
    ],
  },
];

const LOCAL_STORAGE_KEY = 'system-design-progress';

const MotionCard = motion(Card);

const getResourceIcon = (type: string) => {
  switch (type) {
    case 'articles': return FileText;
    case 'videos': return Video;
    case 'github': return Code;
    case 'tutorials': return BookOpen;
    default: return ExternalLink;
  }
};

export const SystemDesign: React.FC = () => {
  const initializedRoadmap = SYSTEM_DESIGN_ROADMAP.map(level => ({
    ...level,
    items: level.items.map(item => ({
      ...item,
      resources: item.resources || {}
    }))
  }));

  const [levels, setLevels] = useState<SystemDesignLevel[]>(initializedRoadmap);

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
              resources: item.resources || {},
            })),
          }))
        );
      } catch (error) {
        console.error('Failed to load system design progress:', error);
      }
    }
  }, []);

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

  const getDifficultyVariant = (difficulty: string): "default" | "secondary" | "destructive" => {
    switch (difficulty) {
      case 'Foundation': return 'secondary';
      case 'Intermediate': return 'default';
      case 'Advanced': return 'destructive';
      default: return 'default';
    }
  };

  const overallProgress = getOverallProgress();

  return (
    <div className="space-y-6">
      {/* Header */}
      <MotionCard
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Building2 className="w-8 h-8 text-primary" />
            </div>
            <div>
              <CardTitle className="text-3xl font-bold">System Design Roadmap</CardTitle>
              <p className="text-muted-foreground">
                Master system design interviews with this comprehensive roadmap
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="font-semibold">Overall Progress</span>
              <span className="text-muted-foreground">
                {overallProgress.completed} / {overallProgress.total} topics completed
              </span>
            </div>
            <Progress value={overallProgress.percentage} className="h-3" />
            <p className="text-xs text-muted-foreground">
              {overallProgress.percentage.toFixed(1)}% Complete
            </p>
          </div>
        </CardContent>
      </MotionCard>

      {/* Learning Levels */}
      <Accordion type="multiple" defaultValue={['foundation']} className="space-y-3">
        {levels.map((level) => {
          const progress = getLevelProgress(level);
          return (
            <AccordionItem
              key={level.id}
              value={level.id}
              className="border rounded-lg bg-card"
            >
              <AccordionTrigger className="px-6 hover:no-underline">
                <div className="flex items-center gap-3 w-full pr-4">
                  <div
                    className="w-10 h-10 rounded-md text-white flex items-center justify-center font-semibold"
                    style={{ backgroundColor: level.color }}
                  >
                    {level.icon}
                  </div>
                  <div className="flex-1 text-left">
                    <h3 className="font-semibold">{level.name}</h3>
                    <p className="text-sm text-muted-foreground">{level.description}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={progress.completed === progress.total ? "default" : "outline"}>
                      {progress.completed === progress.total && <CheckCircle className="w-3 h-3 mr-1" />}
                      {progress.completed}/{progress.total}
                    </Badge>
                    <span className="text-sm text-muted-foreground min-w-[40px]">
                      {progress.percentage.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </AccordionTrigger>
              <AccordionContent className="px-6 pb-4">
                <div className="mb-4">
                  <Progress value={progress.percentage} className="h-2" />
                </div>
                <div className="space-y-3">
                  {level.items.map((item) => (
                    <div
                      key={item.id}
                      className="p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex items-start gap-3">
                        <Checkbox
                          checked={item.completed}
                          onCheckedChange={() => toggleItemCompletion(level.id, item.id)}
                          className="mt-1"
                        />
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span
                              className={`font-medium ${
                                item.completed ? 'line-through text-muted-foreground' : ''
                              }`}
                            >
                              {item.title}
                            </span>
                            <Badge variant={getDifficultyVariant(item.difficulty)} className="text-xs">
                              {item.difficulty}
                            </Badge>
                            {item.completed && (
                              <CheckCircle className="w-4 h-4 text-green-500 ml-auto" />
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">{item.description}</p>

                          {/* Resources */}
                          {item.resources && Object.keys(item.resources).length > 0 && (
                            <div className="space-y-2 pt-2">
                              {Object.entries(item.resources).map(([type, links]) => {
                                if (!links || !Array.isArray(links) || links.length === 0) return null;
                                const Icon = getResourceIcon(type);

                                return (
                                  <div key={type} className="flex items-start gap-2">
                                    <Icon className="w-4 h-4 text-muted-foreground mt-0.5" />
                                    <div className="flex-1 flex flex-wrap gap-2">
                                      {links.map((link, index) => (
                                        <Button
                                          key={index}
                                          variant="outline"
                                          size="sm"
                                          className="h-7 text-xs"
                                          onClick={() => window.open(link, '_blank')}
                                        >
                                          {type} {index + 1}
                                          <ExternalLink className="w-3 h-3 ml-1" />
                                        </Button>
                                      ))}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>
          );
        })}
      </Accordion>
    </div>
  );
};

export default SystemDesign;
