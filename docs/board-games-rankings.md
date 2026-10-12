# Board Games Rankings

Functional v1 adds public rankings and a private admin workflow for board game results.

## Public Routes

- `/games` — active games directory, with each row linking directly to the game's ranking.
- `/games/catan/rankings`
- `/games/flipseven/rankings`

The portfolio's Games link opens `/games`. The shared header links to the portfolio, games directory and administration. The ranking is each game's main view; standalone game landing pages have been removed. Player profiles return to their game's ranking.

## Admin Routes

- `/admin/login` — admin login.
- `/admin` — private admin entry point.
- `/admin/players` — create, edit and activate/deactivate players.
- `/admin/matches` — create, edit, filter and soft-delete matches.

Default local credentials after running the seed:

- Username: `admin`
- Password: `change-me`

Use real secrets in staging and production.

## Data Flow

1. Seed creates base games and the initial admin user.
2. Admin logs in through `/admin/login`.
3. Admin creates active players in `/admin/players`.
4. Admin registers matches in `/admin/matches`.
5. Rankings are calculated from stored matches on every public API request.

Rankings are not edited or stored manually.

## API Summary

Public endpoints:

```txt
GET /api/games
GET /api/games/{game_slug}
GET /api/games/{game_slug}/rankings
```

Auth endpoints:

```txt
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
GET  /api/auth/csrf
```

Admin players endpoints:

```txt
GET   /api/admin/players
POST  /api/admin/players
GET   /api/admin/players/{player_id}
PUT   /api/admin/players/{player_id}
PATCH /api/admin/players/{player_id}/status
```

Admin matches endpoints:

```txt
GET    /api/admin/matches
GET    /api/admin/matches?game={game_slug}
POST   /api/admin/matches
GET    /api/admin/matches/{match_id}
PUT    /api/admin/matches/{match_id}
DELETE /api/admin/matches/{match_id}
```

## Auth And CSRF

- Login sets a signed HttpOnly session cookie.
- `APP_ENV=development` uses non-secure cookies for local HTTP.
- Staging and production use secure cookies by default.
- Admin reads require a valid session.
- Admin mutations require both a valid session and `X-CSRF-Token`.
- The frontend obtains the CSRF token from `GET /api/auth/csrf` after session validation.

## Ranking Rules

All active players appear in each game's ranking, including those with no matches for that game (all statistics start at zero). Inactive players appear only when they have non-deleted matches for that game. Statistics are built from non-deleted matches only; matches in other games do not count. Players without matches appear in the table but not in the podium or leader card.

Common metrics:

- `matches_played`
- `wins`
- `total_points`
- `average_points`
- `win_rate`

The ranking page keeps the main table. Clicking a row opens an independent player profile at `/games/{game_slug}/player?id={player_id}`; the player name is also a keyboard-accessible link. The query parameter allows direct links and reloads with the static Astro deployment, without rebuilding when players are created. Profiles link back to their game's ranking and handle missing or unavailable players. All profiles show the current game's general statistics. Catán profiles additionally show `catan` aggregates: totals, means and maximum final counts for cities, settlements, roads and victory-point cards; final longest-road/largest-army counts and percentages. Only non-deleted matches of that game count. Each metric includes `recorded_matches`: missing values are excluded from its denominator, while explicit zero/false values count. No recorded data produces null means, maxima and rates, displayed as “Sin datos registrados”. These statistics do not change the ranking order.

Catán ordering:

- Wins descending.
- Average points descending.
- Total points descending.
- Matches played descending.
- Player name ascending (case-insensitive) as final tie-breaker.

Flip Seven ordering:

- Wins descending.
- Total points descending.
- Average points descending.
- Matches played descending.
- Player name ascending (case-insensitive) as final tie-breaker.

Inactive players can still appear in rankings if they have historical matches. Inactive players cannot be selected for new matches.
When editing an existing match, its original participants may remain even if they are now inactive. Other inactive players cannot be added. Once removed and saved, an inactive participant cannot be added back without reactivation.

Rankings include all recorded dates and refresh when the page is loaded. Match positions are stored but do not affect ranking order. The win rate is informational; accumulated wins determine the primary order.

## Match Validation

Catán results accept an optional `catan` object with `cities`, `settlements`, `roads`, `victory_point_cards` (non-negative integers), `longest_road` and `largest_army` (booleans). These describe each player's state at the end of the match. The admin form shows them only for Catán, starting at zero/false, and includes them when creating or editing results. Other games reject non-null Catán details. Total points remain manual and ranking rules are unchanged. Updating a result replaces its details; omitted or null details remove them.

Apply migration `202610040001` before using this version: `docker compose -f infra/local/compose.yml exec backend alembic upgrade head`.

Backend validation is the source of truth. The admin frontend also validates the same core rules before submitting:

- Game must exist and be active.
- All selected players must exist and be active, except original participants retained when editing a historical match.
- Players cannot be repeated in one match.
- Exactly one result must be marked as winner.
- Scores must be `>= 0`.
- Catán requires at least 3 players and a position for every player.
- Flip Seven requires at least 2 players and allows empty positions.

Deletes are soft deletes: deleted matches are excluded from admin lists and public rankings.

## Local Smoke Test

Start the local stack:

```bash
docker compose -f infra/local/compose.yml up --build
```

Then test:

1. Open `http://localhost:4321/admin/login`.
2. Log in with `admin` / `change-me`.
3. Create at least 3 players in `/admin/players`.
4. Create a Catán match in `/admin/matches` with positions for every player and one winner.
5. Open `http://localhost:4321/games/catan/rankings` and verify the ranking updates.
6. Create a Flip Seven match with two or more players and no positions.
7. Open `http://localhost:4321/games/flipseven/rankings` and verify the ranking updates.
8. Deactivate a Catán participant and verify their historical results remain in the ranking.
9. Edit their existing match, keeping that participant, and reload the ranking to check the corrected scores.
10. Verify the inactive participant is unavailable when creating a new match.
11. Delete the edited match and reload the ranking to verify its results no longer count.

Use `localhost` consistently for both frontend and API in this local stack so the session cookie is sent correctly.
