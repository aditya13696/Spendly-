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

def test_get_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create your account" in response.data
    assert b"name=\"name\"" in response.data
    assert b"name=\"email\"" in response.data
    assert b"name=\"password\"" in response.data

def test_register_empty_fields(client):
    response = client.post("/register", data={"name": "", "email": "", "password": ""})
    assert response.status_code == 200
    assert b"All fields are required." in response.data

def test_register_invalid_email(client):
    response = client.post("/register", data={
        "name": "Test User",
        "email": "notanemail",
        "password": "password123"
    })
    assert response.status_code == 200
    assert b"Please enter a valid email address." in response.data

def test_register_short_password(client):
    response = client.post("/register", data={
        "name": "Test User",
        "email": "test@example.com",
        "password": "short"
    })
    assert response.status_code == 200
    assert b"Password must be at least 8 characters long." in response.data

def test_register_success(client):
    email = "unique_new_user@spendly.com"
    # Ensure not already in db
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM users WHERE email = ?", (email,))
        db.commit()
        db.close()

    response = client.post("/register", data={
        "name": "Unique User",
        "email": email,
        "password": "securepassword123"
    }, follow_redirects=False)

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    # Verify user in database and password hashed
    with app.app_context():
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

    assert user is not None
    assert user["name"] == "Unique User"
    assert user["password_hash"] != "securepassword123"
    assert user["password_hash"].startswith("pbkdf2:") or user["password_hash"].startswith("scrypt:")

def test_register_duplicate_email(client):
    email = "duplicate@spendly.com"
    # First registration
    client.post("/register", data={
        "name": "First User",
        "email": email,
        "password": "password123"
    })

    # Second registration with same email
    response = client.post("/register", data={
        "name": "Second User",
        "email": email,
        "password": "password456"
    })
    assert response.status_code == 200
    assert b"An account with this email already exists." in response.data
