import React, { useMemo } from 'react';
import { Input, Select, Label, makeStyles, tokens, shorthands } from '@fluentui/react-components';
import { SearchRegular, DismissRegular } from '@fluentui/react-icons';
import type { FilterState, Job } from '../types';

interface FilterControlsProps {
  filters: FilterState;
  onFiltersChange: (f: FilterState) => void;
  jobs: Record<string, Job>;
}

const useStyles = makeStyles({
  wrap: {
    marginBottom: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  searchWrap: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
  },
  clearBtn: {
    position: 'absolute',
    right: '12px',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    color: tokens.colorNeutralForeground3,
    padding: '4px',
    borderRadius: '4px',
    ':hover': { color: tokens.colorNeutralForeground1 },
  },
  row: {
    display: 'flex',
    gap: '10px',
    flexWrap: 'wrap',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    minWidth: '130px',
    flex: '1 1 130px',
  },
  // Status chips row
  chips: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
  },
  chip: {
    ...shorthands.padding('6px', '14px'),
    borderRadius: '20px',
    fontSize: '12.5px',
    fontWeight: '600',
    border: `1.5px solid ${tokens.colorNeutralStroke1}`,
    background: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground2,
    cursor: 'pointer',
    transition: 'all 0.15s ease',
    ':hover': {
      borderColor: tokens.colorBrandStroke1,
      color: tokens.colorBrandForeground1,
    },
  },
  chipActive: {
    ...shorthands.padding('6px', '14px'),
    borderRadius: '20px',
    fontSize: '12.5px',
    fontWeight: '700',
    border: '1.5px solid transparent',
    background: 'linear-gradient(135deg,#3b82f6,#6366f1)',
    color: '#fff',
    cursor: 'pointer',
  },
});

const STATUS_CHIPS: { value: string; label: string }[] = [
  { value: 'all',         label: '🔍 Active' },
  { value: 'new',         label: '✨ New' },
  { value: 'applied',     label: '✅ Applied' },
  { value: 'rejected',    label: '❌ Skipped' },
];

export const FilterControls: React.FC<FilterControlsProps> = ({ filters, onFiltersChange, jobs }) => {
  const styles = useStyles();

  const availableCountries = useMemo(() => {
    const s = new Set<string>();
    Object.entries(jobs).forEach(([k, j]) => {
      if (!k.startsWith('_') && j.country && !j.applied && !j.rejected) s.add(j.country);
    });
    return Array.from(s).sort();
  }, [jobs]);

  return (
    <div className={styles.wrap}>
      {/* Status chip row */}
      <div className={styles.chips}>
        {STATUS_CHIPS.map(({ value, label }) => (
          <button
            key={value}
            className={filters.status === value ? styles.chipActive : styles.chip}
            onClick={() => onFiltersChange({ ...filters, status: value as FilterState['status'] })}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Search bar */}
      <div className={styles.searchWrap}>
        <Input
          contentBefore={<SearchRegular style={{ fontSize: '16px', color: tokens.colorNeutralForeground3 }} />}
          placeholder="Search job title or company…"
          value={filters.keyword || ''}
          onChange={(_, d) => onFiltersChange({ ...filters, keyword: d.value })}
          style={{
            width: '100%',
            height: '44px',
            borderRadius: '12px',
            fontSize: '14px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
            paddingRight: filters.keyword ? '40px' : undefined,
          }}
        />
        {filters.keyword && (
          <button className={styles.clearBtn} onClick={() => onFiltersChange({ ...filters, keyword: '' })}>
            <DismissRegular style={{ fontSize: '16px' }} />
          </button>
        )}
      </div>

      {/* Secondary filters */}
      <div className={styles.row}>
        <div className={styles.field}>
          <Label size="small" style={{ color: tokens.colorNeutralForeground3, fontWeight: 600 }}>Sort</Label>
          <Select
            value={filters.sort}
            onChange={(_, d) => onFiltersChange({ ...filters, sort: d.value as FilterState['sort'] })}
            style={{ borderRadius: '10px' }}
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
          </Select>
        </div>

        <div className={styles.field}>
          <Label size="small" style={{ color: tokens.colorNeutralForeground3, fontWeight: 600 }}>Quick Apply</Label>
          <Select
            value={filters.quickApply || 'all'}
            onChange={(_, d) => onFiltersChange({ ...filters, quickApply: d.value as FilterState['quickApply'] })}
            style={{ borderRadius: '10px' }}
          >
            <option value="all">All jobs</option>
            <option value="confirmed_only">Verified quick</option>
            <option value="quick_only">Quick apply</option>
            <option value="non_quick">Standard only</option>
          </Select>
        </div>

        {availableCountries.length > 1 && (
          <div className={styles.field}>
            <Label size="small" style={{ color: tokens.colorNeutralForeground3, fontWeight: 600 }}>Country</Label>
            <Select
              value={filters.country || 'all'}
              onChange={(_, d) => onFiltersChange({ ...filters, country: d.value })}
              style={{ borderRadius: '10px' }}
            >
              <option value="all">All countries</option>
              {availableCountries.map(c => <option key={c} value={c}>{c}</option>)}
            </Select>
          </div>
        )}
      </div>
    </div>
  );
};
