---
# Spec: Registration

## Overview

This feature implements user registration for Spendly. It allows new users to create an account by submitting their full name, email address, and password through the registration form. Submitted passwords are securely hashed using Werkzeug before being stored in the SQLite database, and newly registered users are automatically logged in or redirected.

## Depends on

Step 1 — Database setup

## Routes

- `GET /register` — Render the registration page — Public
- `POST /register` — Process registration form submission, validate input, create user in database, and handle session/redirect — Public

## Database changes

No new database changes required. The `users` table already exists from Step 1 with columns: `id`, `name`, `email`, `password_hash`, `created_at`.

## Templates

- **Create:** None
- **Modify:** `templates/register.html` (ensure form action points correctly to `/register`, inputs have correct names: `name`, `email`, `password`, and error handling/flashing is supported if needed).

## Files to change

- `app.py` — Add POST handling for `/register`, input validation, password hashing, user insertion, and session management.
- `templates/register.html` — Verify form attributes and field names.

## Files to create

- None

## New dependencies

No new dependencies. Uses `werkzeug.security` (already installed) for password hashing and `sqlite3` for database operations.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done

- [ ] Navigating to `/register` displays the registration form correctly.
- [ ] Submitting valid registration details creates a new user record in the database with a securely hashed password.
- [ ] Attempting to register with an existing email address displays an appropriate error message.
- [ ] Input validation prevents empty submissions or malformed emails.
- [ ] Successful registration redirects the user appropriately (e.g., to login or dashboard).
- [ ] App passes all tests without errors.
