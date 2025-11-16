import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { motion } from 'framer-motion';
import {
  GraduationCap,
  CheckCircle,
  Circle,
} from 'lucide-react';

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
    icon: 'A',
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
    icon: 'TP',
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
    icon: 'SW',
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
    icon: 'S',
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
    icon: 'BS',
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
    icon: 'LL',
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

const MotionCard = motion(Card);

export const Training: React.FC = () => {
  const [categories, setCategories] = useState<TrainingCategory[]>(NEETCODE_ROADMAP);

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

  const getDifficultyVariant = (difficulty: string): "default" | "secondary" | "destructive" => {
    switch (difficulty) {
      case 'Easy': return 'secondary';
      case 'Medium': return 'default';
      case 'Hard': return 'destructive';
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
              <GraduationCap className="w-8 h-8 text-primary" />
            </div>
            <div>
              <CardTitle className="text-3xl font-bold">DSA Training Roadmap</CardTitle>
              <p className="text-muted-foreground">
                Track your progress through the Neetcode.io algorithm roadmap
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="font-semibold">Overall Progress</span>
              <span className="text-muted-foreground">
                {overallProgress.completed} / {overallProgress.total} problems completed
              </span>
            </div>
            <Progress value={overallProgress.percentage} className="h-3" />
            <p className="text-xs text-muted-foreground">
              {overallProgress.percentage.toFixed(1)}% Complete
            </p>
          </div>
        </CardContent>
      </MotionCard>

      {/* Training Categories */}
      <Accordion type="multiple" defaultValue={['arrays']} className="space-y-3">
        {categories.map((category) => {
          const progress = getCategoryProgress(category);
          return (
            <AccordionItem
              key={category.id}
              value={category.id}
              className="border rounded-lg bg-card"
            >
              <AccordionTrigger className="px-6 hover:no-underline">
                <div className="flex items-center gap-3 w-full pr-4">
                  <div className="w-10 h-10 rounded-md bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                    {category.icon}
                  </div>
                  <div className="flex-1 text-left">
                    <h3 className="font-semibold">{category.name}</h3>
                    <p className="text-sm text-muted-foreground">{category.description}</p>
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
                <div className="space-y-1">
                  {category.items.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between p-3 rounded-md hover:bg-accent transition-colors"
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <Checkbox
                          checked={item.completed}
                          onCheckedChange={() => toggleItemCompletion(category.id, item.id)}
                          className="mt-0.5"
                        />
                        <div className="flex items-center gap-2 flex-1">
                          <span
                            className={`text-sm ${
                              item.completed ? 'line-through text-muted-foreground' : ''
                            }`}
                          >
                            {item.title}
                          </span>
                          <Badge variant={getDifficultyVariant(item.difficulty)} className="text-xs">
                            {item.difficulty}
                          </Badge>
                        </div>
                      </div>
                      {item.completed && (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      )}
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

export default Training;
