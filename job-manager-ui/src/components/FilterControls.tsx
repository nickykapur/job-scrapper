import React, { useMemo } from 'react';
import { Input, Select, Label, makeStyles, tokens } from '@fluentui/react-components';
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
    gap: '12px',
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
  chips: {
    display: 'flex',
    gap: '6px',
    flexWrap: 'wrap',
  },
});

const STATUS_CHIPS: { value: string; label: string }[] = [
  { value: 'all',      label: 'Active' },
  { value: 'new',      label: 'New' },
  { value: 'applied',  label: 'Applied' },
  { value: 'rejected', label: 'Skipped' },
];

const chipBase: React.CSSProperties = {
  padding: '6px 16px',
  borderRadius: '20px',
  fontSize: '12.5px',
  fontWeight: 600,
  border: '1.5px solid rgba(255,255,255,0.1)',
  background: 'transparent',
  color: 'rgba(255,255,255,0.5)',
  cursor: 'pointer',
  transition: 'all 0.15s ease',
  letterSpacing: '0.01em',
};

const chipActive: React.CSSProperties = {
  ...chipBase,
  border: '1.5px solid #3b82f6',
  background: 'rgba(59,130,246,0.15)',
  color: '#60a5fa',
  fontWeight: 700,
};

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
      {/* Status chips */}
      <div className={styles.chips}>
        {STATUS_CHIPS.map(({ value, label }) => (
          <button
            key={value}
            style={filters.status === value ? chipActive : chipBase}
            onClick={() => onFiltersChange({ ...filters, status: value as FilterState['status'] })}
            onMouseEnter={e => {
              if (filters.status !== value) {
                (e.currentTarget as HTMLElement).style.borderColor = 'rgba(255,255,255,0.2)';
                (e.currentTarget as HTMLElement).style.color = 'rgba(255,255,255,0.75)';
              }
            }}
            onMouseLeave={e => {
              if (filters.status !== value) {
                (e.currentTarget as HTMLElement).style.borderColor = 'rgba(255,255,255,0.1)';
                (e.currentTarget as HTMLElement).style.color = 'rgba(255,255,255,0.5)';
              }
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Search bar */}
      <div className={styles.searchWrap}>
        <Input
          contentBefore={<SearchRegular style={{ fontSize: '16px', color: tokens.colorNeutralForeground3 }} />}
          placeholder="Search title or company..."
          value={filters.keyword || ''}
          onChange={(_, d) => onFiltersChange({ ...filters, keyword: d.value })}
          style={{
            width: '100%',
            height: '42px',
            borderRadius: '10px',
            fontSize: '13.5px',
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
          <Label size="small" style={{ color: tokens.colorNeutralForeground3, fontWeight: 600, fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Sort</Label>
          <Select
            value={filters.sort}
            onChange={(_, d) => onFiltersChange({ ...filters, sort: d.value as FilterState['sort'] })}
            style={{ borderRadius: '8px' }}
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
          </Select>
        </div>

        {availableCountries.length > 1 && (
          <div className={styles.field}>
            <Label size="small" style={{ color: tokens.colorNeutralForeground3, fontWeight: 600, fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Country</Label>
            <Select
              value={filters.country || 'all'}
              onChange={(_, d) => onFiltersChange({ ...filters, country: d.value })}
              style={{ borderRadius: '8px' }}
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
