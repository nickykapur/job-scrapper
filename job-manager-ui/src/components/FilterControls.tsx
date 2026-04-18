import React, { useMemo } from 'react';
import {
  Input,
  Select,
  Label,
  Card,
  makeStyles,
  tokens,
  Text,
} from '@fluentui/react-components';
import {
  SearchRegular,
  FilterRegular,
  DismissRegular,
} from '@fluentui/react-icons';
import type { FilterState, Job } from '../types';

interface FilterControlsProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  jobs: Record<string, Job>;
}

const useStyles = makeStyles({
  card: {
    borderRadius: tokens.borderRadiusXLarge,
    boxShadow: tokens.shadow4,
    marginBottom: '20px',
    overflow: 'hidden',
  },
  inner: {
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '4px',
  },
  row: {
    display: 'grid',
    gridTemplateColumns: '1fr',
    gap: '12px',
    '@media (min-width: 640px)': {
      gridTemplateColumns: '1fr 1fr',
    },
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  searchWrap: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
  },
  clearBtn: {
    position: 'absolute',
    right: '10px',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    color: tokens.colorNeutralForeground3,
    padding: '0',
    ':hover': {
      color: tokens.colorNeutralForeground1,
    },
  },
});

export const FilterControls: React.FC<FilterControlsProps> = ({
  filters,
  onFiltersChange,
  jobs,
}) => {
  const styles = useStyles();

  const availableCountries = useMemo(() => {
    const countrySet = new Set<string>();
    Object.entries(jobs).forEach(([key, job]) => {
      if (!key.startsWith('_') && job.country && !job.applied && !job.rejected) {
        countrySet.add(job.country);
      }
    });
    return Array.from(countrySet).sort();
  }, [jobs]);

  return (
    <Card className={styles.card}>
      <div className={styles.inner}>
        <div className={styles.header}>
          <FilterRegular style={{ fontSize: '18px', color: tokens.colorBrandForeground1 }} />
          <Text weight="semibold" size={400}>Filters</Text>
        </div>

        {/* Keyword search */}
        <div className={styles.field}>
          <Label size="small" style={{ color: tokens.colorNeutralForeground2 }}>Search jobs</Label>
          <div className={styles.searchWrap}>
            <Input
              contentBefore={<SearchRegular style={{ fontSize: '16px' }} />}
              placeholder="Job title or company…"
              value={filters.keyword || ''}
              onChange={(_, d) => onFiltersChange({ ...filters, keyword: d.value })}
              style={{ width: '100%', paddingRight: filters.keyword ? '36px' : undefined }}
            />
            {filters.keyword && (
              <button
                className={styles.clearBtn}
                onClick={() => onFiltersChange({ ...filters, keyword: '' })}
              >
                <DismissRegular style={{ fontSize: '16px' }} />
              </button>
            )}
          </div>
        </div>

        <div className={styles.row}>
          {/* Status */}
          <div className={styles.field}>
            <Label size="small" style={{ color: tokens.colorNeutralForeground2 }}>Status</Label>
            <Select
              value={filters.status}
              onChange={(_, d) => onFiltersChange({ ...filters, status: d.value as FilterState['status'] })}
            >
              <option value="all">Active Jobs</option>
              <option value="applied">Applied</option>
              <option value="not_applied">Not Applied</option>
              <option value="rejected">Rejected</option>
              <option value="new">New Only</option>
            </Select>
          </div>

          {/* Sort */}
          <div className={styles.field}>
            <Label size="small" style={{ color: tokens.colorNeutralForeground2 }}>Sort by</Label>
            <Select
              value={filters.sort}
              onChange={(_, d) => onFiltersChange({ ...filters, sort: d.value as FilterState['sort'] })}
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
            </Select>
          </div>

          {/* Country */}
          {availableCountries.length > 1 && (
            <div className={styles.field}>
              <Label size="small" style={{ color: tokens.colorNeutralForeground2 }}>Country</Label>
              <Select
                value={filters.country || 'all'}
                onChange={(_, d) => onFiltersChange({ ...filters, country: d.value })}
              >
                <option value="all">All Countries</option>
                {availableCountries.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </Select>
            </div>
          )}

          {/* Quick Apply */}
          <div className={styles.field}>
            <Label size="small" style={{ color: tokens.colorNeutralForeground2 }}>Quick Apply</Label>
            <Select
              value={filters.quickApply || 'all'}
              onChange={(_, d) => onFiltersChange({ ...filters, quickApply: d.value as FilterState['quickApply'] })}
            >
              <option value="all">All Jobs</option>
              <option value="quick_only">Quick Apply Only</option>
              <option value="confirmed_only">Verified Quick Apply</option>
              <option value="non_quick">Standard Apply Only</option>
            </Select>
          </div>
        </div>
      </div>
    </Card>
  );
};
