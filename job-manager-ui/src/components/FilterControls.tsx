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
  // Calculate available countries (only countries with available jobs - not applied/rejected)
  const availableCountries = useMemo(() => {
    const countrySet = new Set<string>();
    Object.entries(jobs).forEach(([key, job]) => {
      // Only include countries that have at least one job that's not applied or rejected
      if (!key.startsWith('_') && job.country && !job.applied && !job.rejected) {
        countrySet.add(job.country);
      }
    });
    // Sort countries alphabetically
    const sorted = Array.from(countrySet).sort();
    return sorted;
  }, [jobs]);

  // Check if Ireland has available jobs
  const hasIreland = Object.entries(jobs).some(
    ([key, job]) => !key.startsWith('_') && job.country === 'Ireland' && !job.applied && !job.rejected
  );

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
