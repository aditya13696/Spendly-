# Spec: Add Expense

## Overview

This feature introduces expense creation to Spendly, allowing authenticated users to log individual transactions with an amount, category, date, and description. Prior to this step, the application only displayed pre-seeded demo transactions on the profile dashboard. Adding expenses is the foundational data-entry capability of Spendly, enabling users to record real-world spending, update their personal analytics, and track financial habits across time periods.

## Depends on

- Step 1: Database setup (schema with `users` and `expenses` tables, `get_db()`)
- Step 2: Registration (user authentication)
- Step 3: Login + Logout (session management, user identification)
- Step 4: Profile Page Design (HTML/CSS dashboard layout)
- Step 5: Backend Routes for Profile Page (live display of expenses, user stats, category breakdowns)
- Step 6: Date Filter for Profile Page (date filtering across expenses)

## Routes

- `GET /expenses/add` — Display the Add Expense form with prefilled current date and category selector — logged-in only
- `POST /expenses/add` — Validate input, insert new expense record associated with the authenticated user, set flash message, and redirect to profile dashboard — logged-in only

## Database changes

No new tables, columns, or schema changes needed. The `expenses` table already contains `id`, `user_id`, `amount`, `category`, `date`, `description`, and `created_at`.

Add the following helper function in `database/db.py`:
- `create_expense(user_id, amount, category, date, description)` — Inserts a new row into the `expenses` table using a parameterized query and returns the generated expense ID (`cursor.lastrowid`).

Permitted expense categories:
- `Food`
- `Transport`
- `Bills`
- `Health`
- `Entertainment`
- `Shopping`
- `Other`

## Templates

- **Create:** `expense-tracker/templates/add_expense.html`
  - Extends `base.html`
  - Form containing:
    - Amount (`<input type="number" step="0.01" min="0.01">`, required)
    - Category (`<select>` dropdown with the 7 predefined categories, required)
    - Date (`<input type="date">`, defaults to today's date in `YYYY-MM-DD`, required)
    - Description (`<input type="text">` or `<textarea>`, optional, max 200 characters)
    - Submit button ("Add Expense") and Cancel button/link back to `/profile`
  - Error message alert box if validation fails
  - Preserves entered values on validation failure
- **Modify:** `expense-tracker/templates/profile.html`
  - Add an "Add Expense" call-to-action button linking to `{{ url_for('add_expense') }}` in the header / user card or above the Recent Transactions table.

## Files to change

- `expense-tracker/app.py` — Replace placeholder `add_expense` route with `GET` and `POST` handlers, authentication check, form validation, calling `create_expense`, and redirecting with flash messages.
- `expense-tracker/database/db.py` — Implement `create_expense(user_id, amount, category, date, description)`.
- `expense-tracker/templates/profile.html` — Add the "Add Expense" action button linking to `/expenses/add`.
- `expense-tracker/static/css/style.css` — Add styles for the Add Expense form card, input fields, labels, submit/cancel buttons, and the Add Expense button on the profile page.

## Files to create

- `.claude/specs/07-add-expense.md` — Feature specification document.
- `expense-tracker/templates/add_expense.html` — Jinja2 template for the Add Expense page.
- `expense-tracker/tests/test_add_expense.py` — Automated tests for route access, authentication, validation errors, and expense creation.

## New dependencies

No new dependencies. Built-in Python standard libraries (`datetime`) and existing packages (`Flask`, `pytest`) are sufficient.

## Rules for implementation

- No SQLAlchemy or ORMs — use raw sqlite3 via `get_db()` with parameterized queries
- Parameterised queries only — never construct SQL queries via string formatting or concatenation
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Strict authentication: Unauthenticated users attempting to access `GET` or `POST /expenses/add` must be redirected to `url_for('login')`
- Server-side validation:
  - Amount must be present, numeric, and greater than 0
  - Category must be one of the permitted categories (`Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`)
  - Date must be a valid date in `YYYY-MM-DD` format
  - Description is optional and stripped of leading/trailing whitespace
- Security: Associate the new expense strictly with `session["user_id"]` to prevent unauthorized cross-user writes
- User feedback: Flash a success message on creation (`"Expense added successfully!"`) and display validation errors clearly on form submission failure

## Definition of done

- [ ] Navigating to `/expenses/add` while unauthenticated redirects to `/login`
- [ ] Navigating to `/expenses/add` while authenticated renders the Add Expense form extending `base.html`
- [ ] Add Expense form displays fields for Amount, Category, Date, and Description
- [ ] Date input defaults to today's date (`YYYY-MM-DD`)
- [ ] Submitting valid data inserts a record into the `expenses` table associated with `session['user_id']`
- [ ] Submitting invalid data (empty/negative amount, missing category, invalid date) re-renders the form with an informative error message and preserves user inputs
- [ ] After successful expense creation, user is redirected to `/profile` with a success flash message
- [ ] The newly added expense immediately appears in the Recent Transactions table on `/profile`
- [ ] Total spent, transaction count, and category breakdown metrics on `/profile` update to reflect the new expense
- [ ] An "Add Expense" button is visible and accessible on the `/profile` page
- [ ] Form and controls are styled using Spendly design tokens (CSS variables) and responsive on desktop and mobile
- [ ] All automated tests pass (`pytest tests/test_add_expense.py` and full test suite)
