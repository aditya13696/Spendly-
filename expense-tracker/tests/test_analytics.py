import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.db import init_db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        init_db()
    with app.test_client() as client:
        yield client


def test_analytics_redirect_when_logged_out(client):
    """Unauthenticated users visiting /analytics directly should be redirected to login."""
    response = client.get("/analytics", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_analytics_200_when_logged_in(client):
    """Authenticated users should successfully access the analytics page."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/analytics")
    assert response.status_code == 200


def test_analytics_navbar_visibility(client):
    """Analytics link should only be visible in navbar to logged in users."""
    # When logged out
    response_logged_out = client.get("/")
    html_logged_out = response_logged_out.data.decode("utf-8")
    assert "Analytics" not in html_logged_out

    # When logged in
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response_logged_in = client.get("/profile")
    html_logged_in = response_logged_in.data.decode("utf-8")
    assert "Analytics" in html_logged_in
    assert 'href="/analytics"' in html_logged_in


def test_analytics_navbar_active_state(client):
    """Navbar should highlight Analytics with active class when on the analytics page."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/analytics")
    html = response.data.decode("utf-8")
    assert 'class="nav-link active">Analytics</a>' in html


def test_analytics_figma_content_rendered(client):
    """Analytics page must contain all key text and elements from the Figma design."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Demo User"

    response = client.get("/analytics")
    html = response.data.decode("utf-8")

    # Page heading
    assert "Advanced Analytics" in html
    assert "Understand your spending. Make every expense count." in html

    # Announcement card
    assert "COMING SOON" in html
    assert "Your spending." in html
    assert "A clearer picture." in html
    assert "See where your money goes, spot spending patterns, and stay on top of your budget." in html

    # Capability tags
    assert "Spending trends" in html
    assert "Category reports" in html
    assert "Budget insights" in html

    # Release status
    assert "Better money decisions are coming. Stay tuned." in html

    # Preview card
    assert "Spending overview" in html
    assert "PREVIEW" in html
    assert "Your expenses, over time" in html
    assert "A glimpse of what’s ahead" in html
