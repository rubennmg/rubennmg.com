# Board Games Rankings

Functional v1 adds public rankings and a private admin workflow for board game results.

## Public Routes

- `/games/catan`
- `/games/catan/rankings`
- `/games/flipseven`
- `/games/flipseven/rankings`

These routes are intentionally not linked from the portfolio yet. They are available directly by URL.

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

Ranking data is built from non-deleted matches only.

Common metrics:

- `matches_played`
- `wins`
- `total_points`
- `average_points`
- `win_rate`

Catán ordering:

- Wins descending.
- Total points descending.
- Average points descending.
- Player name ascending as final deterministic tie-breaker.

Flip Seven ordering:

- Total points descending.
- Wins descending.
- Average points descending.
- Player name ascending as final deterministic tie-breaker.

Inactive players can still appear in rankings if they have historical matches. Inactive players cannot be selected for new matches.

## Match Validation

Backend validation is the source of truth. The admin frontend also validates the same core rules before submitting:

- Game must exist and be active.
- All selected players must exist and be active.
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
