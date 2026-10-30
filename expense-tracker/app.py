import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import init_db, seed_db, get_user_by_email, create_user

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

    # Hardcoded user data (Step 4: UI only, no DB queries)
    user_data = {
        "name": "Alex Morgan",
        "email": "alex.morgan@example.com",
        "initials": "AM",
        "member_since": "October 2026",
    }

    # Hardcoded summary stats
    stats = {
        "total_spent": "₹24,850",
        "transaction_count": 42,
        "top_category": "Food",
    }

    # Hardcoded recent transactions (5 rows, 3+ categories)
    recent_expenses = [
        {"date": "28 Oct 2026", "description": "Grocery store run", "category": "Food", "amount": "₹3,450"},
        {"date": "26 Oct 2026", "description": "Metro card recharge", "category": "Transport", "amount": "₹1,000"},
        {"date": "24 Oct 2026", "description": "Electricity bill", "category": "Bills", "amount": "₹2,800"},
        {"date": "22 Oct 2026", "description": "Cinema tickets & snacks", "category": "Entertainment", "amount": "₹1,250"},
        {"date": "20 Oct 2026", "description": "Doctor consultation", "category": "Health", "amount": "₹1,600"},
    ]

    # Hardcoded category breakdown (3+ categories with amounts and percentages)
    category_breakdown = [
        {"category": "Food", "amount": "₹9,850", "percentage": 40},
        {"category": "Bills", "amount": "₹6,200", "percentage": 25},
        {"category": "Transport", "amount": "₹3,700", "percentage": 15},
        {"category": "Entertainment", "amount": "₹2,600", "percentage": 10},
        {"category": "Health", "amount": "₹2,500", "percentage": 10},
    ]

    return render_template(
        "profile.html",
        user=user_data,
        stats=stats,
        expenses=recent_expenses,
        categories=category_breakdown
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
