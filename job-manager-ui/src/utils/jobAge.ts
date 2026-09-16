/**
 * Job age, anchored to when the job was scraped.
 *
 * `posted_date` is LinkedIn's own relative text ("3 days ago"), captured at
 * scrape time and stored verbatim. It never ages. Reading it as an offset from
 * *now* — which is what this code used to do — misdates every job by however
 * long ago it was scraped:
 *
 *   scraped 11 Sep, posted_date "3 days ago"  ->  really posted 8 Sep
 *   read as now - 3 days on 16 Sep            ->  looks posted 13 Sep
 *
 * The error grows with the age of the row, so stale jobs are flattered the
 * most and sort above genuinely fresh ones.
 */

const UNIT_MS: Record<string, number> = {
  second: 1000,
  minute: 60_000,
  min: 60_000,
  hour: 3_600_000,
  day: 86_400_000,
  week: 604_800_000,
  month: 2_592_000_000,
  year: 31_536_000_000,
};

interface JobLike {
  posted_date?: string | null;
  scraped_at?: string | null;
}

/** When the job was scraped, or now if that is missing or unparseable. */
function scrapeAnchor(job: JobLike): number {
  const t = new Date(job.scraped_at || 0).getTime();
  return Number.isFinite(t) && t > 0 ? t : Date.now();
}

/**
 * Absolute timestamp the job was posted, as best we can tell.
 * Offsets run from the scrape, not from now.
 */
export function postedAtMs(job: JobLike): number {
  const anchor = scrapeAnchor(job);
  const raw = (job.posted_date || '')
    .toLowerCase()
    .replace(/^posted\s+/, '')
    .trim();

  const m = raw.match(/^(\d+)\s+(second|minute|min|hour|day|week|month|year)/);
  if (m) {
    const n = parseInt(m[1], 10);
    return anchor - n * (UNIT_MS[m[2]] ?? UNIT_MS.day);
  }
  if (raw === 'just now' || raw === 'moments ago' || raw === 'today') {
    return anchor;
  }
  // "Unknown", empty, or anything unparseable: the scrape is all we know.
  return anchor;
}

/** How old the posting actually is now, in whole hours. */
export function postedAgeHours(job: JobLike): number {
  return Math.max(0, (Date.now() - postedAtMs(job)) / 3_600_000);
}

/**
 * True age for display. Recomputed from the anchored timestamp, so it keeps
 * counting up instead of showing whatever LinkedIn said on the scrape day.
 */
export function postedAgeLabel(job: JobLike): string {
  const h = postedAgeHours(job);
  if (h < 1) return 'Just posted';
  if (h < 24) return `${Math.floor(h)}h ago`;
  const d = Math.floor(h / 24);
  if (d === 1) return '1 day ago';
  if (d < 7) return `${d} days ago`;
  const w = Math.floor(d / 7);
  return w === 1 ? '1 week ago' : `${w} weeks ago`;
}
