#!/usr/bin/env python3
"""
Seed a random Indian user into the expense tracker database.
"""
import sys
import os
import random
from datetime import datetime

# Add the expense-tracker directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'expense-tracker'))

from database.db import get_db
from werkzeug.security import generate_password_hash

# Realistic Indian names across different regions
FIRST_NAMES = [
    # North Indian (Hindi/Punjabi)
    'Rahul', 'Priya', 'Amit', 'Neha', 'Rohan', 'Anjali', 'Vikram', 'Pooja',
    'Arjun', 'Kavya', 'Aditya', 'Riya', 'Karan', 'Shreya', 'Varun', 'Meera',
    # South Indian (Tamil/Telugu/Malayalam/Kannada)
    'Karthik', 'Lakshmi', 'Suresh', 'Deepika', 'Rajesh', 'Divya', 'Sanjay', 'Preethi',
    'Arun', 'Shalini', 'Manoj', 'Sowmya', 'Ramesh', 'Nandini', 'Venkat', 'Sangeetha',
    # West Indian (Gujarati/Marathi)
    'Nikhil', 'Sneha', 'Jayesh', 'Isha', 'Harsh', 'Diya', 'Rohan', 'Ananya',
    # East Indian (Bengali/Odia)
    'Ayan', 'Ishita', 'Sourav', 'Tanvi', 'Abhishek', 'Ritika', 'Siddharth', 'Aditi',
    # Gender-neutral/Common
    'Aryan', 'Avani', 'Dev', 'Kiara', 'Aarav', 'Saanvi', 'Reyansh', 'Aadhya'
]

LAST_NAMES = [
    # North Indian
    'Sharma', 'Verma', 'Singh', 'Kumar', 'Gupta', 'Agarwal', 'Jain', 'Malhotra',
    'Kapoor', 'Mehta', 'Patel', 'Shah', 'Chopra', 'Sethi', 'Bhatia', 'Khanna',
    # South Indian
    'Reddy', 'Iyer', 'Nair', 'Menon', 'Rao', 'Krishnan', 'Naidu', 'Pillai',
    'Raman', 'Subramanian', 'Ayyar', 'Kumar', 'Bhat', 'Shetty', 'Hegde',
    # West Indian
    'Desai', 'Joshi', 'Kulkarni', 'Doshi', 'Pandya', 'Parekh', 'Trivedi',
    # East Indian
    'Chatterjee', 'Mukherjee', 'Banerjee', 'Ghosh', 'Das', 'Bose', 'Sen',
    # Pan-Indian
    'Khan', 'Ali', 'Ahmed', 'Hussain', 'D\'Souza', 'Fernandes', 'Rodrigues'
]


def generate_random_indian_user():
    """Generate a realistic random Indian user with name, email, and hashed password."""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"

    # Generate email: firstname.lastname{random_digits}@gmail.com
    email_prefix = f"{first_name.lower()}.{last_name.lower()}"
    random_suffix = random.randint(10, 999)  # 2-3 digit number
    email = f"{email_prefix}{random_suffix}@gmail.com"

    # Hash the default password
    password_hash = generate_password_hash('password123')

    # Current datetime
    created_at = datetime.now().isoformat()

    return name, email, password_hash, created_at


def check_email_exists(cursor, email):
    """Check if an email already exists in the database."""
    cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', (email,))
    return cursor.fetchone()[0] > 0


def seed_random_user():
    """Seed a random Indian user into the database."""
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Generate user and ensure email is unique
        max_attempts = 50
        for attempt in range(max_attempts):
            name, email, password_hash, created_at = generate_random_indian_user()

            if not check_email_exists(cursor, email):
                break

            if attempt == max_attempts - 1:
                print(f"Failed to generate unique email after {max_attempts} attempts.")
                return

        # Insert the user
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', (name, email, password_hash, created_at))

        # Get the inserted user's ID
        user_id = cursor.lastrowid

        conn.commit()

        # Print confirmation
        print("User seeded successfully:")
        print(f"  ID: {user_id}")
        print(f"  Name: {name}")
        print(f"  Email: {email}")

    except Exception as e:
        conn.rollback()
        print(f"Error seeding user: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    seed_random_user()
