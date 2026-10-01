-- Migration: add the enforce_city_filter column /api/jobs already reads
--
-- railway_server.py has had this for some time:
--
--     if preferences.get('enforce_city_filter') and preferences.get('preferred_cities'):
--         city_match = any(city.lower() in location for city in preferences['preferred_cities'])
--         if not city_match:
--             continue
--
-- but no migration ever created the column. get_user_preferences does
-- SELECT * and returns dict(row), so the key is simply absent, .get() yields
-- None, and the branch has never once executed. Several users already have
-- preferred_cities populated (Dublin, Chicago, Detroit and so on) and none of
-- it has ever had any effect.
--
-- DEFAULT FALSE deliberately. Defaulting to TRUE would switch city filtering
-- on for every existing user who has preferred_cities set, silently narrowing
-- their feed — the opposite of what they would expect from a migration.
-- Existing behaviour is preserved exactly; the filter only applies to users
-- who are explicitly opted in afterwards.

ALTER TABLE user_preferences
    ADD COLUMN IF NOT EXISTS enforce_city_filter BOOLEAN DEFAULT FALSE;
