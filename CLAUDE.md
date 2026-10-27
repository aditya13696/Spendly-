# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Spendly** is a Flask-based expense tracking web application in early-stage development. The project is structured as a learning/progressive build where core features are implemented incrementally across multiple steps (Steps 1–9+).

- **Framework**: Flask 3.1.3 with Werkzeug
- **Database**: SQLite (connection and initialization are student implementations)
- **Entry Point**: `expense-tracker/app.py`
- **Port**: 5001 (debug mode enabled)

## Directory Structure

```
expense-tracker/
├── app.py                 # Flask application with all routes
├── requirements.txt       # Python dependencies
├── database/
│   ├── __init__.py
│   └── db.py             # Database connection and initialization (student implementation)
├── templates/            # Jinja2 HTML templates extending base.html
│   ├── base.html         # Base layout with navbar and footer
│   ├── landing.html      # Landing/home page
│   ├── login.html        # Login form
│   ├── register.html     # Registration form
│   ├── terms.html        # Terms and Conditions
│   └── privacy.html      # Privacy Policy
└── static/
    ├── css/style.css     # Stylesheet (DM Sans and DM Serif Display fonts)
    ├── js/main.js        # Client-side JavaScript
    └── images/           # Static images (hero-desktop@2x.png)
```

## Architecture

### Flask Routes

All routes are defined in `app.py`. The app uses Jinja2 templating with a base template inheritance pattern:

**Implemented Routes**:
- `GET /` — Landing page
- `GET /login` — Login page
- `GET /register` — Registration page
- `GET /terms` — Terms and Conditions
- `GET /privacy` — Privacy Policy

**Placeholder Routes** (student implementation phases):
- `GET /logout` (Step 3)
- `GET /profile` (Step 4)
- `POST /expenses/add` (Step 7)
- `POST /expenses/<id>/edit` (Step 8)
- `POST /expenses/<id>/delete` (Step 9)

### Template Inheritance

All pages extend `base.html`, which provides:
- Navigation bar with brand (Spendly) and sign-in/get-started links
- Footer with brand and legal links
- Shared CSS and JS includes
- `{% block content %}` for page-specific content
- `{% block head %}` for page-specific styles
- `{% block scripts %}` for page-specific scripts

### Database Layer (Not Yet Implemented)

The `database/db.py` module will be implemented in Step 1 and should provide:
- `get_db()` — Returns a SQLite connection with row_factory and foreign keys enabled
- `init_db()` — Creates all tables using CREATE TABLE IF NOT EXISTS
- `seed_db()` — Inserts sample data for development

## Common Commands

### Development

Start the Flask development server (runs on `http://127.0.0.1:5001`):
```bash
cd expense-tracker
python app.py
```

Or from the repo root:
```bash
python expense-tracker/app.py
```

### Dependency Management

Install dependencies:
```bash
pip install -r expense-tracker/requirements.txt
```

Update requirements after installing new packages:
```bash
pip freeze > expense-tracker/requirements.txt
```

### Testing

Run tests (pytest configured via `pytest-flask`):
```bash
cd expense-tracker
pytest
```

Run a single test file:
```bash
pytest tests/test_routes.py
```

Run a single test function:
```bash
pytest tests/test_routes.py::test_landing_page
```

Show test output and print statements:
```bash
pytest -s
```

## Development Guidelines

### Adding Routes

1. Define the route in `app.py` with appropriate HTTP method
2. Create or update a template in `templates/` that extends `base.html`
3. Use `{{ url_for('route_name') }}` for internal links (handles routing centrally)

### Database Operations

- Use the database connection provided by `db.get_db()`
- Enable foreign key constraints in `get_db()`
- Use row_factory for dict-like access: `row['column_name']`
- Keep SQL queries in the database layer, not in routes

### Styling

- CSS is in `static/css/style.css`
- Uses Google Fonts: DM Sans (weights 300, 400, 500, 600) and DM Serif Display
- Avoid inline styles; use CSS classes
- The project supports light/dark modes (manage via CSS)

### Static Assets

- Images go in `static/images/`
- Reference static files in templates using `{{ url_for('static', filename='path/to/file') }}`

## Git Workflow

- Main branch: `main`
- Commits require Co-authored attribution: `Co-Authored-By: Claude Code <noreply@anthropic.com>`
- Pull requests should end with: `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
- Always create a new branch before making changes; never push directly to main

## Important Notes

- The `.env` file is gitignored; use it for local environment variables (not committed)
- `expense_tracker.db` is gitignored; generate it via `seed_db()` or tests
- `__pycache__/` and `.claude/plans/` are gitignored
- Debug mode is enabled in `app.py` — disable in production
- The app is a learning project with incremental feature implementation; placeholder routes return simple text responses
