import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import init_db, seed_db, get_user_by_email, create_user, get_user_by_id, get_expenses_by_user, get_user_stats, get_category_breakdown

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-spendly")


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    # Redirect logged in users to profile page
    if session.get("user_id"):
        return redirect(url_for("profile"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Redirect to landing if already logged in
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # 1. Required fields check
        if not name or not email or not password:
            return render_template(
                "register.html",
                error="All fields are required.",
                name=name,
                email=email,
            )

        # 2. Email format check
        if "@" not in email or "." not in email.split("@")[-1] or len(email.split("@")[0]) == 0:
            return render_template(
                "register.html",
                error="Please enter a valid email address.",
                name=name,
                email=email,
            )

        # 3. Password length check
        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must be at least 8 characters long.",
                name=name,
                email=email,
            )

        # 4. Check if user already exists
        if get_user_by_email(email):
            return render_template(
                "register.html",
                error="An account with this email already exists.",
                name=name,
                email=email,
            )

        # 5. Hash password and insert user
        password_hash = generate_password_hash(password)
        user_id = create_user(name, email, password_hash)

        if user_id:
            flash("Account created successfully! Please sign in.", "success")
            return redirect(url_for("login"))
        else:
            return render_template(
                "register.html",
                error="Registration failed. Please try again.",
                name=name,
                email=email,
            )

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect to landing if already logged in
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # 1. Required fields check
        if not email or not password:
            return render_template(
                "login.html",
                error="Both email and password are required."
            )

        # 2. Look up user by email
        user = get_user_by_email(email)
        if not user:
            return render_template(
                "login.html",
                error="Invalid email or password.",
                email=email
            )

        # 3. Verify password
        if not check_password_hash(user["password_hash"], password):
            return render_template(
                "login.html",
                error="Invalid email or password.",
                email=email
            )

        # 4. Set session and redirect
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        flash("Signed in successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    # Authentication guard: redirect to login if not authenticated
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Fetch user data from database
    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for("login"))

    user_data = {
        "name": user["name"],
        "email": user["email"],
        "initials": "".join([n[0].upper() for n in user["name"].split()[:2]]),
        "member_since": user["created_at"][:10] if user["created_at"] else "Unknown",
    }

    # Date filtering logic
    preset = request.args.get('preset', 'all')
    custom_start = request.args.get('start_date', '').strip()
    custom_end = request.args.get('end_date', '').strip()

    start_date = None
    end_date = None
    period_label = "All time"

    try:
        today = datetime.now().date()

        if preset == 'this_month':
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
            period_label = "This month"

        elif preset == 'last_month':
            first_day_this_month = today.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            first_day_last_month = last_day_last_month.replace(day=1)
            start_date = first_day_last_month.strftime('%Y-%m-%d')
            end_date = last_day_last_month.strftime('%Y-%m-%d')
            period_label = "Last month"

        elif preset == 'last_30_days':
            start_date = (today - timedelta(days=29)).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
            period_label = "Last 30 days"

        elif preset == 'this_year':
            start_date = today.replace(month=1, day=1).strftime('%Y-%m-%d')
            end_date = today.replace(month=12, day=31).strftime('%Y-%m-%d')
            period_label = "This year"

        elif preset == 'custom' and custom_start and custom_end:
            # Validate custom dates
            start_dt = datetime.strptime(custom_start, '%Y-%m-%d').date()
            end_dt = datetime.strptime(custom_end, '%Y-%m-%d').date()

            # Swap if start > end
            if start_dt > end_dt:
                start_dt, end_dt = end_dt, start_dt

            start_date = start_dt.strftime('%Y-%m-%d')
            end_date = end_dt.strftime('%Y-%m-%d')
            period_label = f"{start_dt.strftime('%b %d, %Y')} – {end_dt.strftime('%b %d, %Y')}"

        elif preset != 'all':
            # Invalid preset, fallback to all
            preset = 'all'

    except (ValueError, AttributeError):
        # Date parsing failed, fallback to all
        preset = 'all'
        start_date = None
        end_date = None
        period_label = "All time"

    # Fetch summary stats from database with date filter
    stats_raw = get_user_stats(user_id, start_date, end_date)
    stats = {
        "total_spent": f"₹{stats_raw['total_spent']:,.2f}",
        "transaction_count": stats_raw['transaction_count'],
        "top_category": stats_raw['top_category'] or "N/A",
        "period_label": period_label,
    }

    # Fetch expenses from database with date filter
    # When filtering by date, show all matching expenses (no limit)
    limit = None if (start_date or end_date) else 5
    expenses_raw = get_expenses_by_user(user_id, limit=limit, start_date=start_date, end_date=end_date)
    recent_expenses = []
    for exp in expenses_raw:
        recent_expenses.append({
            "date": exp["date"],
            "description": exp["description"],
            "category": exp["category"],
            "amount": f"₹{exp['amount']:,.2f}",
        })

    # Fetch category breakdown from database with date filter
    categories_raw = get_category_breakdown(user_id, start_date, end_date)
    category_breakdown = []
    for cat in categories_raw:
        category_breakdown.append({
            "category": cat["category"],
            "amount": f"₹{cat['amount']:,.2f}",
            "percentage": cat["percentage"],
        })

    # Pass filter info to template
    filter_info = {
        "preset": preset,
        "start_date": custom_start if preset == 'custom' else '',
        "end_date": custom_end if preset == 'custom' else '',
        "label": period_label,
    }

    return render_template(
        "profile.html",
        user=user_data,
        stats=stats,
        expenses=recent_expenses,
        categories=category_breakdown,
        filter_info=filter_info
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
