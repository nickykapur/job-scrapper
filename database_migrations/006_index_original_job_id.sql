-- Migration: index the self-referencing foreign key on jobs.original_job_id
--
-- 005 added the composite index the enforce-country-limit SELECT needs, and the
-- endpoint STILL died after exactly 60 seconds with an empty detail. The index
-- was not the binding constraint. This is.
--
-- 002 added:
--
--     ALTER TABLE jobs ADD COLUMN IF NOT EXISTS original_job_id VARCHAR(50)
--         REFERENCES jobs(id);
--
-- A self-referencing foreign key with no index on the referencing column and no
-- ON DELETE action. Postgres does not index the referencing side automatically,
-- so every row deleted from jobs forces a check for children:
--
--     SELECT 1 FROM jobs WHERE original_job_id = <deleted id> FOR KEY SHARE
--
-- With no index that is a sequential scan of the whole jobs table, once per
-- deleted row. Removing the ~69,000 rows that are over cap therefore costs
-- ~69,000 scans of an 89,000-row table — billions of comparisons. It cannot
-- finish inside the pool's 60s command_timeout, and would not finish inside the
-- 120s server-side statement_timeout either.
--
-- user_job_interactions.job_id is already indexed (001), so that cascade is
-- cheap. This was the only unindexed FK pointing at jobs.
--
-- With the index each check becomes a single index probe.

CREATE INDEX IF NOT EXISTS idx_jobs_original_job_id
    ON jobs(original_job_id);

ANALYZE jobs;
