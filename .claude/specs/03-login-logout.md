---
# Spec: Login and Logout

## Overview

This feature implements user authentication functionality for Spendly, allowing users to log in to their accounts and log out securely. It builds upon the existing registration system (Step 2) by adding login functionality and a logout mechanism to complete the user authentication flow.

## Depends on

Step 2 — User Registration (already implemented)

## Routes

- `POST /login` — Process login form submission, authenticate user, and establish session — Logged-in
- `GET /logout` — Clear user session and redirect to login page — Logged-in

## Database changes

No database changes required. The `users` table already exists with necessary columns: `id`, `name`, `email`, `password_hash`, `created_at`.

## Templates

- **Create:** None
- **Modify:** None (login.html already exists with proper form structure)

## Files to change

- `app.py` — Add POST handling for `/login`, implement session management, and create `/logout` route

## Files to create

None

## New dependencies

No new dependencies. Uses existing Flask session management and Werkzeug security functions.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only for database operations
- Passwords hashed with werkzeug (`generate_password_hash`)
- Use Flask session management for user authentication state
- All templates must extend `base.html`
- Use CSS variables — never hardcode hex values
- Implement proper error handling and flash messages

## Definition of done

- [ ] Navigating to `/login` displays the login form correctly
- [ ] Submitting valid login credentials authenticates the user and establishes session
- [ ] Submitting invalid credentials displays appropriate error message
- [ ] Successful login redirects to the landing page or dashboard
- [ ] Clicking logout clears the session and redirects to login page
- [ ] App passes all tests without errors