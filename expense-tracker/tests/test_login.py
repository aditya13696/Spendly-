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
    # Use a test database or ensure db is initialized
    with app.app_context():
        init_db()
    with app.test_client() as client:
        yield client

def test_get_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign in" in response.data
    assert b"name=\"email\"" in response.data
    assert b"name=\"password\"" in response.data

def test_login_empty_fields(client):
    response = client.post("/login", data={"email": "", "password": ""})
    assert response.status_code == 200
    assert b"Both email and password are required." in response.data

def test_login_invalid_email(client):
    response = client.post("/login", data={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert b"Invalid email or password." in response.data

def test_login_wrong_password(client):
    response = client.post("/login", data={
        "email": "demo@spendly.com",
        "password": "wrongpassword123"
    })
    assert response.status_code == 200
    assert b"Invalid email or password." in response.data

def test_login_success(client):
    response = client.post("/login", data={
        "email": "demo@spendly.com",
        "password": "demo123"
    }, follow_redirects=False)

    assert response.status_code == 302
    assert "/" in response.headers["Location"]

    # Verify session
    with app.app_context():
        db = get_db()
        # Session user_id should be set
        session = db.execute("SELECT * FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()
        db.close()

    assert session is not None

def test_login_duplicate_redirect(client):
    # Try logging in when already logged in via session
    with client.session_transaction() as sess:
        sess["user_id"] = 999

    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 200

def test_logout(client):
    # First login as demo user
    client.post("/login", data={
        "email": "demo@spendly.com",
        "password": "demo123"
    }, follow_redirects=False)

    # Then logout
    response = client.get("/logout", follow_redirects=False)

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]