import React, { useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Filter, Search, X } from 'lucide-react';
import type { FilterState, Job } from '../types';

interface FilterControlsProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  jobs: Record<string, Job>;
}

export const FilterControls: React.FC<FilterControlsProps> = ({
  filters,
  onFiltersChange,
  jobs,
}) => {
  // Auto-detect available countries from actual jobs (not applied/rejected)
  const availableCountries = useMemo(() => {
    const countrySet = new Set<string>();
    Object.entries(jobs).forEach(([key, job]) => {
      if (!key.startsWith('_') && job.country && !job.applied && !job.rejected) {
        countrySet.add(job.country);
      }
    });
    return Array.from(countrySet).sort();
  }, [jobs]);

const hasIreland = Object.entries(jobs).some(
    ([key, job]) => !key.startsWith('_') && job.country === 'Ireland' && !job.applied && !job.rejected
  );

  return (
    <Card className="mb-6">
      <CardContent className="p-6 space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <Filter className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold">Filters</h3>
        </div>

        {/* Keyword search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by job title or company…"
            value={filters.keyword || ''}
            onChange={(e) => onFiltersChange({ ...filters, keyword: e.target.value })}
            className="w-full pl-9 pr-9 py-2 text-sm rounded-md border border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
          {filters.keyword && (
            <button
              onClick={() => onFiltersChange({ ...filters, keyword: '' })}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Country filter */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-muted-foreground">Country</label>
          <Select
            value={filters.country || 'Ireland'}
            onValueChange={(value) => onFiltersChange({ ...filters, country: value })}
          >
            <SelectTrigger className="w-full md:w-48">
              <SelectValue placeholder="Select country" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Countries</SelectItem>
              {hasIreland && <SelectItem value="Ireland">Ireland</SelectItem>}
              {availableCountries
                .filter(c => c !== 'Ireland')
                .map(country => (
                  <SelectItem key={country} value={country}>
                    {country}
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
        </div>
      </CardContent>
    </Card>
  );
};
