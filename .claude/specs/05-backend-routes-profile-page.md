# Spec: Backend Routes for Profile Page

## Overview
This feature replaces the hardcoded profile page data with real database queries. The `/profile` route will now fetch actual user data, expense statistics, transaction history, and category breakdowns from the SQLite database, making the profile page functional for logged-in users.

## Depends on
- Step 1: Database setup (schema with users and expenses tables)
- Step 2: Registration (create_user function exists)
- Step 3: Login + Logout (session authentication works)
- Step 4: Profile Page (UI template exists, needs backend data)

## Routes
No new routes. This step modifies the existing:
- GET /profile — now fetches real data from database — logged-in only

## Database changes
No new tables or columns. Add these new functions to `database/db.py`:
- `get_user_by_id(user_id)` — fetch user details by ID
- `get_expenses_by_user(user_id, limit=None)` — fetch all expenses for a user
- `get_user_stats(user_id)` — calculate total spent, transaction count, top category
- `get_category_breakdown(user_id)` — aggregate expenses by category

## Templates
No new templates. Modify:
- `templates/profile.html` — already exists with correct structure; no template changes needed since the variable names remain the same

## Files to change
- `database/db.py` — add new database functions for fetching profile data
- `app.py` — replace hardcoded data in `/profile` route with calls to new DB functions

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw sqlite3 via `get_db()` with parameterized queries
- Parameterised queries only — never string-format SQL
- Passwords hashed with werkzeug (no changes to auth)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `session.get("user_id")` to get current user ID for database queries
- Handle empty states gracefully (new users with no expenses)
- Close database connections properly (use try/finally)
- Format currency amounts consistently (use ₹ symbol with commas)
- Format dates consistently (e.g., "28 Oct 2026")

## Definition of done
- [ ] Visiting `/profile` while logged in shows real user name and email from database
- [ ] Profile shows correct total spent calculated from actual expenses
- [ ] Profile shows correct transaction count from database
- [ ] Profile shows correct top category based on highest spending
- [ ] Transaction history shows real expenses from database
- [ ] Category breakdown shows accurate percentages from database
- [ ] New users with no expenses see appropriate empty/zero states
- [ ] All database queries use parameterized queries (no SQL injection)