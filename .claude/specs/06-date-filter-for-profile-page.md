# Spec: Date Filter for Profile Page

## Overview

This feature adds date filtering capabilities to the Spendly profile page dashboard. Currently, the profile page displays all-time data or a fixed set of recent transactions. By introducing a date range filter (with preset ranges like "Last 30 Days", "This Month", "Last Month", "This Year", and custom date ranges), users can dynamically analyze their spending habits across specific time periods. This step enhances the analytical value of the profile dashboard before expense creation/editing features are introduced.

## Depends on

- Step 1: Database setup (schema with users and expenses tables)
- Step 2: Registration (user authentication)
- Step 3: Login + Logout (session management)
- Step 4: Profile Page Design (HTML/CSS layout)
- Step 5: Backend Routes for Profile Page (live database queries wired up)

## Routes

No new routes. Modifies existing route:

- `GET /profile` — Profile dashboard with optional query parameters for date filtering (`start_date`, `end_date`, `filter_preset`) — logged-in only

## Database changes

No new tables or columns. Verify existing queries in `database/db.py` to support optional date range filtering parameters (`start_date` and `end_date` in `YYYY-MM-DD` format).

Update the following functions in `database/db.py`:
- `get_expenses_by_user(user_id, limit=None, start_date=None, end_date=None)` — add date filtering to WHERE clause
- `get_user_stats(user_id, start_date=None, end_date=None)` — add date filtering to aggregation queries
- `get_category_breakdown(user_id, start_date=None, end_date=None)` — add date filtering to aggregation queries

## Templates

- **Create:** None
- **Modify:** `expense-tracker/templates/profile.html`
  - Add date filter control bar above summary stats or transactions table
  - Include quick preset buttons/dropdown: "All Time", "This Month", "Last Month", "Last 30 Days", "This Year"
  - Include custom start date and end date inputs with a submit button
  - Ensure filter state persists in form controls upon page refresh
  - Display active filter summary/indicator

## Files to change

- `expense-tracker/database/db.py` — update data retrieval functions to accept optional date filters
- `expense-tracker/app.py` — parse query parameters (`start_date`, `end_date`, `preset`), validate formats, compute date bounds, and pass them to DB functions and template
- `expense-tracker/templates/profile.html` — add filter form and active filter UI
- `expense-tracker/static/css/style.css` — style date filter controls, buttons, and responsive inputs

## Files to create

- `expense-tracker/tests/test_date_filter.py` — automated unit and integration tests for date filtering

## New dependencies

No new dependencies. Standard library `datetime` module is sufficient for date parsing and calculations.

## Rules for implementation

- No SQLAlchemy or ORMs — use raw sqlite3 via `get_db()` with parameterized queries
- Parameterised queries only — never concatenate or format SQL strings
- Validate all user-supplied dates against `YYYY-MM-DD` format to prevent SQL injection or logic errors
- Safe fallback: if invalid dates or presets are supplied, default gracefully to "All Time" or current month without crashing
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Date handling should account for edge cases (e.g., end dates should encompass the entire day)

## Definition of done

- [ ] Navigating to `/profile` loads default view without errors
- [ ] Selecting preset filter "This Month" reloads dashboard with only current month's expenses, stats, and breakdown
- [ ] Selecting preset filter "Last 30 Days" updates metrics according to the last 30-day window
- [ ] Submitting a custom date range (e.g. `2026-10-01` to `2026-10-15`) filters transactions, total spent, and category breakdown correctly
- [ ] Submitting empty/invalid dates resets safely to default view with appropriate feedback or fallback
- [ ] Active filter is clearly indicated in the UI and inputs retain their selected values
- [ ] Category breakdown percentages accurately sum to 100% (or 0% if no expenses match) for the filtered subset
- [ ] Empty state renders cleanly if no expenses match the given date range
- [ ] All automated tests pass (`pytest`)
