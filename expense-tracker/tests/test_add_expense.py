import os
import sys
from datetime import datetime
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.db import init_db, get_db, create_user
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        init_db()
    with app.test_client() as client:
        yield client


def test_add_expense_redirects_when_not_logged_in(client):
    """Unauthenticated users should be redirected to login on GET and POST."""
    res_get = client.get("/expenses/add", follow_redirects=False)
    assert res_get.status_code == 302
    assert "/login" in res_get.headers["Location"]

    res_post = client.post("/expenses/add", data={"amount": "50", "category": "Food", "date": "2026-10-10"}, follow_redirects=False)
    assert res_post.status_code == 302
    assert "/login" in res_post.headers["Location"]


def test_add_expense_renders_when_logged_in(client):
    """Authenticated users should see the Add Expense form."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/expenses/add")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Add Expense" in html
    assert 'name="amount"' in html
    assert 'name="category"' in html
    assert 'name="date"' in html
    assert 'name="description"' in html
    assert "Food" in html
    assert "Transport" in html


def test_add_expense_defaults_date_to_today(client):
    """Date input should prefill with today's date in YYYY-MM-DD."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/expenses/add")
    html = response.data.decode("utf-8")
    today_str = datetime.now().date().strftime("%Y-%m-%d")
    assert f'value="{today_str}"' in html


def test_add_expense_validation_missing_fields(client):
    """Submitting empty fields should re-render with an error message."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.post("/expenses/add", data={"amount": "", "category": "Food", "date": "2026-10-10"})
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Amount, category, and date are required." in html


def test_add_expense_validation_invalid_amount(client):
    """Submitting invalid amount (negative, zero, or text) should fail."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    # Negative amount
    response = client.post("/expenses/add", data={"amount": "-15.50", "category": "Food", "date": "2026-10-10"})
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Please enter a valid amount greater than 0." in html

    # Zero amount
    response = client.post("/expenses/add", data={"amount": "0", "category": "Food", "date": "2026-10-10"})
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Please enter a valid amount greater than 0." in html

    # Non-numeric amount
    response = client.post("/expenses/add", data={"amount": "abc", "category": "Food", "date": "2026-10-10"})
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Please enter a valid amount greater than 0." in html


def test_add_expense_validation_invalid_category(client):
    """Submitting an unrecognized category should fail."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.post("/expenses/add", data={"amount": "50.00", "category": "Crypto", "date": "2026-10-10"})
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Please select a valid category." in html


def test_add_expense_validation_invalid_date(client):
    """Submitting a date in incorrect format should fail."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.post("/expenses/add", data={"amount": "50.00", "category": "Food", "date": "10-10-2026"})
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Please enter a valid date in YYYY-MM-DD format." in html


def test_add_expense_success(client):
    """Submitting valid expense data creates the expense and redirects to profile."""
    import time
    unique_email = f"user_{int(time.time() * 1000)}@example.com"
    user_id = create_user("Test User", unique_email, generate_password_hash("password123"))

    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = "Test User"

    response = client.post("/expenses/add", data={
        "amount": "149.99",
        "category": "Shopping",
        "date": "2026-10-28",
        "description": "Wireless headphones"
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Expense added successfully!" in html
    assert "Wireless headphones" in html
    assert "₹149.99" in html
    assert "Shopping" in html


def test_profile_contains_add_expense_button(client):
    """Profile page should display an Add Expense button linking to /expenses/add."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/profile")
    html = response.data.decode("utf-8")
    assert "/expenses/add" in html
    assert "Add Expense" in html
