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
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  School as SchoolIcon,
} from '@mui/icons-material';

interface TrainingItem {
  id: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  completed: boolean;
}

interface TrainingCategory {
  id: string;
  name: string;
  description: string;
  items: TrainingItem[];
  icon: string;
}

// Neetcode.io roadmap data structure
const NEETCODE_ROADMAP: TrainingCategory[] = [
  {
    id: 'arrays',
    name: 'Arrays & Hashing',
    description: 'Foundation problems for arrays and hash tables',
    icon: '📊',
    items: [
      { id: 'contains-duplicate', title: 'Contains Duplicate', difficulty: 'Easy', completed: false },
      { id: 'valid-anagram', title: 'Valid Anagram', difficulty: 'Easy', completed: false },
      { id: 'two-sum', title: 'Two Sum', difficulty: 'Easy', completed: false },
      { id: 'group-anagrams', title: 'Group Anagrams', difficulty: 'Medium', completed: false },
      { id: 'top-k-frequent', title: 'Top K Frequent Elements', difficulty: 'Medium', completed: false },
      { id: 'product-except-self', title: 'Product of Array Except Self', difficulty: 'Medium', completed: false },
      { id: 'valid-sudoku', title: 'Valid Sudoku', difficulty: 'Medium', completed: false },
      { id: 'encode-decode', title: 'Encode and Decode Strings', difficulty: 'Medium', completed: false },
      { id: 'longest-consecutive', title: 'Longest Consecutive Sequence', difficulty: 'Medium', completed: false },
    ],
  },
  {
    id: 'two-pointers',
    name: 'Two Pointers',
    description: 'Efficient array traversal techniques',
    icon: '👉',
    items: [
      { id: 'valid-palindrome', title: 'Valid Palindrome', difficulty: 'Easy', completed: false },
      { id: 'two-sum-ii', title: 'Two Sum II - Input Array Is Sorted', difficulty: 'Medium', completed: false },
      { id: '3sum', title: '3Sum', difficulty: 'Medium', completed: false },
      { id: 'container-water', title: 'Container With Most Water', difficulty: 'Medium', completed: false },
      { id: 'trapping-rain-water', title: 'Trapping Rain Water', difficulty: 'Hard', completed: false },
    ],
  },
  {
    id: 'sliding-window',
    name: 'Sliding Window',
    description: 'Dynamic window problems for subarray optimization',
    icon: '🪟',
    items: [
      { id: 'best-time-stock', title: 'Best Time to Buy and Sell Stock', difficulty: 'Easy', completed: false },
      { id: 'longest-substring', title: 'Longest Substring Without Repeating Characters', difficulty: 'Medium', completed: false },
      { id: 'longest-repeating-replacement', title: 'Longest Repeating Character Replacement', difficulty: 'Medium', completed: false },
      { id: 'permutation-string', title: 'Permutation in String', difficulty: 'Medium', completed: false },
      { id: 'minimum-window-substring', title: 'Minimum Window Substring', difficulty: 'Hard', completed: false },
      { id: 'sliding-window-maximum', title: 'Sliding Window Maximum', difficulty: 'Hard', completed: false },
    ],
  },
  {
    id: 'stack',
    name: 'Stack',
    description: 'LIFO data structure problems',
    icon: '📚',
    items: [
      { id: 'valid-parentheses', title: 'Valid Parentheses', difficulty: 'Easy', completed: false },
      { id: 'min-stack', title: 'Min Stack', difficulty: 'Medium', completed: false },
      { id: 'evaluate-rpn', title: 'Evaluate Reverse Polish Notation', difficulty: 'Medium', completed: false },
      { id: 'generate-parentheses', title: 'Generate Parentheses', difficulty: 'Medium', completed: false },
      { id: 'daily-temperatures', title: 'Daily Temperatures', difficulty: 'Medium', completed: false },
      { id: 'car-fleet', title: 'Car Fleet', difficulty: 'Medium', completed: false },
      { id: 'largest-rectangle', title: 'Largest Rectangle in Histogram', difficulty: 'Hard', completed: false },
    ],
  },
  {
    id: 'binary-search',
    name: 'Binary Search',
    description: 'Efficient searching in sorted arrays',
    icon: '🔍',
    items: [
      { id: 'binary-search', title: 'Binary Search', difficulty: 'Easy', completed: false },
      { id: 'search-2d-matrix', title: 'Search a 2D Matrix', difficulty: 'Medium', completed: false },
      { id: 'koko-eating-bananas', title: 'Koko Eating Bananas', difficulty: 'Medium', completed: false },
      { id: 'find-minimum-rotated', title: 'Find Minimum in Rotated Sorted Array', difficulty: 'Medium', completed: false },
      { id: 'search-rotated', title: 'Search in Rotated Sorted Array', difficulty: 'Medium', completed: false },
      { id: 'time-based-store', title: 'Time Based Key-Value Store', difficulty: 'Medium', completed: false },
      { id: 'median-two-arrays', title: 'Median of Two Sorted Arrays', difficulty: 'Hard', completed: false },
    ],
  },
  {
    id: 'linked-list',
    name: 'Linked List',
    description: 'Dynamic data structure manipulation',
    icon: '⛓️',
    items: [
      { id: 'reverse-linked-list', title: 'Reverse Linked List', difficulty: 'Easy', completed: false },
      { id: 'merge-two-lists', title: 'Merge Two Sorted Lists', difficulty: 'Easy', completed: false },
      { id: 'reorder-list', title: 'Reorder List', difficulty: 'Medium', completed: false },
      { id: 'remove-nth-node', title: 'Remove Nth Node From End of List', difficulty: 'Medium', completed: false },
      { id: 'copy-random-list', title: 'Copy List with Random Pointer', difficulty: 'Medium', completed: false },
      { id: 'add-two-numbers', title: 'Add Two Numbers', difficulty: 'Medium', completed: false },
      { id: 'linked-list-cycle', title: 'Linked List Cycle', difficulty: 'Easy', completed: false },
      { id: 'find-duplicate', title: 'Find the Duplicate Number', difficulty: 'Medium', completed: false },
      { id: 'lru-cache', title: 'LRU Cache', difficulty: 'Medium', completed: false },
      { id: 'merge-k-lists', title: 'Merge k Sorted Lists', difficulty: 'Hard', completed: false },
      { id: 'reverse-nodes-k-group', title: 'Reverse Nodes in k-Group', difficulty: 'Hard', completed: false },
    ],
  },
];

const LOCAL_STORAGE_KEY = 'neetcode-training-progress';

export const Training: React.FC = () => {
  const [categories, setCategories] = useState<TrainingCategory[]>(NEETCODE_ROADMAP);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['arrays']));

  // Load progress from localStorage on component mount
  useEffect(() => {
    const savedProgress = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (savedProgress) {
      try {
        const progress = JSON.parse(savedProgress);
        setCategories(prevCategories =>
          prevCategories.map(category => ({
            ...category,
            items: category.items.map(item => ({
              ...item,
              completed: progress[item.id] || false,
            })),
          }))
        );
      } catch (error) {
        console.error('Failed to load training progress:', error);
      }
    }
  }, []);

  // Save progress to localStorage whenever it changes
  const saveProgress = (updatedCategories: TrainingCategory[]) => {
    const progress: Record<string, boolean> = {};
    updatedCategories.forEach(category => {
      category.items.forEach(item => {
        progress[item.id] = item.completed;
      });
    });
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(progress));
  };

  const toggleItemCompletion = (categoryId: string, itemId: string) => {
    const updatedCategories = categories.map(category => {
      if (category.id === categoryId) {
        return {
          ...category,
          items: category.items.map(item =>
            item.id === itemId ? { ...item, completed: !item.completed } : item
          ),
        };
      }
      return category;
    });
    setCategories(updatedCategories);
    saveProgress(updatedCategories);
  };

  const toggleCategoryExpansion = (categoryId: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(categoryId)) {
        newSet.delete(categoryId);
      } else {
        newSet.add(categoryId);
      }
      return newSet;
    });
  };

  const getCategoryProgress = (category: TrainingCategory) => {
    const completed = category.items.filter(item => item.completed).length;
    const total = category.items.length;
    return { completed, total, percentage: total > 0 ? (completed / total) * 100 : 0 };
  };

  const getOverallProgress = () => {
    const allItems = categories.flatMap(cat => cat.items);
    const completedItems = allItems.filter(item => item.completed).length;
    return {
      completed: completedItems,
      total: allItems.length,
      percentage: allItems.length > 0 ? (completedItems / allItems.length) * 100 : 0,
    };
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'success';
      case 'Medium': return 'warning';
      case 'Hard': return 'error';
      default: return 'default';
    }
  };

  const overallProgress = getOverallProgress();

  return (
    <Box sx={{ width: '100%', px: 1 }}>
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
          <SchoolIcon color="primary" sx={{ fontSize: 32 }} />
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 700, color: 'text.primary' }}>
              Training Roadmap
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Track your progress through the Neetcode.io algorithm roadmap
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
              {overallProgress.completed} / {overallProgress.total} problems completed
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
                background: 'linear-gradient(90deg, #4caf50 0%, #8bc34a 100%)',
              },
            }}
          />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {overallProgress.percentage.toFixed(1)}% Complete
          </Typography>
        </Box>
      </Paper>

      {/* Training Categories */}
      <Grid container spacing={2}>
        {categories.map((category) => {
          const progress = getCategoryProgress(category);
          return (
            <Grid item xs={12} key={category.id}>
              <Accordion
                expanded={expandedCategories.has(category.id)}
                onChange={() => toggleCategoryExpansion(category.id)}
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
                    <Typography sx={{ fontSize: '1.5rem' }}>{category.icon}</Typography>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" fontWeight={600}>
                        {category.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {category.description}
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
                        },
                      }}
                    />
                  </Box>
                  <List disablePadding>
                    {category.items.map((item) => (
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
                        />
                        <ListItemSecondaryAction>
                          <Checkbox
                            edge="end"
                            checked={item.completed}
                            onChange={() => toggleItemCompletion(category.id, item.id)}
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