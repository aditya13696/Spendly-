import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.db import init_db, get_db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        init_db()
    with app.test_client() as client:
        yield client


def test_profile_redirect_when_not_logged_in(client):
    """Unauthenticated users should be redirected to login."""
    response = client.get("/profile", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_200_when_logged_in(client):
    """Authenticated users should see the profile page."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/profile")
    assert response.status_code == 200


def test_profile_contains_user_card(client):
    """Profile page should display user info card."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/profile")
    html = response.data.decode("utf-8")
    assert "Alex Morgan" in html
    assert "alex.morgan@example.com" in html
    assert "Member since October 2026" in html


def test_profile_contains_summary_stats(client):
    """Profile page should display at least 3 summary stat values."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/profile")
    html = response.data.decode("utf-8")
    assert "Total Spent" in html
    assert "Transactions" in html
    assert "Top Category" in html
    assert "42" in html
    assert "Food" in html


def test_profile_contains_transaction_table(client):
    """Profile page should display transaction history table with rows."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/profile")
    html = response.data.decode("utf-8")
    assert "Recent Transactions" in html
    assert "Grocery store run" in html
    assert "Metro card recharge" in html
    assert "Electricity bill" in html


def test_profile_contains_category_breakdown(client):
    """Profile page should display category breakdown section."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/profile")
    html = response.data.decode("utf-8")
    assert "Category Breakdown" in html
    assert "Bills" in html
    assert "Food" in html
    assert "Transport" in html


def test_profile_uses_badge_classes(client):
    """Category badges should use CSS classes, not inline styles."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/profile")
    html = response.data.decode("utf-8")
    assert "badge-cat badge-cat-food" in html
    assert "badge-cat badge-cat-bills" in html
    assert "badge-cat badge-cat-transport" in html


def test_profile_no_inline_hex_colors(client):
    """Profile page should not contain inline hex color values (#)."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/profile")
    html_content = response.data.decode('utf-8')

    import re
    style_tags = re.findall(r'style="[^"]*#[0-9a-fA-F]{3,6}[^"]*"', html_content)
    for style_tag in style_tags:
        if '#' in style_tag:
            assert False, f"Found inline hex color in style attribute: {style_tag}"
