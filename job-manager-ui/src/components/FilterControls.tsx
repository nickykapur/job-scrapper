import React, { useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Filter } from 'lucide-react';
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
  // Calculate available countries (only countries with jobs)
  const availableCountries = useMemo(() => {
    const countrySet = new Set<string>();
    Object.entries(jobs).forEach(([key, job]) => {
      if (!key.startsWith('_') && job.country) {
        countrySet.add(job.country);
      }
    });
    // Sort countries alphabetically, but keep Ireland first
    const sorted = Array.from(countrySet).sort();
    return sorted.filter(c => c !== 'Ireland').sort();
  }, [jobs]);

  // Ensure Ireland is in the list if it has jobs
  const hasIreland = availableCountries.includes('Ireland') ||
    Object.values(jobs).some(job => job.country === 'Ireland');

  return (
    <Card className="mb-6">
      <CardContent className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold">Filter by Country</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Country Filter - Only filter shown */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Country</label>
            <Select
              value={filters.country || 'Ireland'}
              onValueChange={(value) => onFiltersChange({ ...filters, country: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select country" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Countries</SelectItem>
                {/* Ireland first if it has jobs */}
                {hasIreland && <SelectItem value="Ireland">Ireland</SelectItem>}
                {/* Other countries with jobs, sorted alphabetically */}
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
        </div>
      </CardContent>
    </Card>
  );
};
