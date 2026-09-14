-- Migration: add the index enforce-country-limit needs
--
-- The cleanup endpoint runs a window function over the whole jobs table:
--
--     ROW_NUMBER() OVER (PARTITION BY country, COALESCE(job_type,'other')
--                        ORDER BY scraped_at DESC)
--
-- database_setup.sql declares a matching composite index, but nothing creates
-- it at runtime: init_database() does not, and no Python file references it. A
-- database that predates that line has never had it, so the DELETE sorts the
-- whole table and exceeds the asyncpg pool's 60s command_timeout — surfacing as
-- HTTP 500 with an empty message, because str(asyncio.TimeoutError()) is "".
--
-- The result is a feedback loop. Cleanup fails, rows accumulate, the query gets
-- slower, cleanup fails sooner. The table reached 89,058 rows against per-
-- country caps of 60 to 1,000.
--
-- Plain CREATE INDEX rather than CONCURRENTLY: the maintenance runner wraps each
-- migration in a transaction, and CONCURRENTLY cannot run inside one. At this
-- table size the build takes seconds, and it only blocks writes for that window.

CREATE INDEX IF NOT EXISTS idx_jobs_enforce
    ON jobs(country, job_type, scraped_at DESC);

-- The 72-hour protection clause scans on scraped_at alone.
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at
    ON jobs(scraped_at DESC);

ANALYZE jobs;
