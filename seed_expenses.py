#!/usr/bin/env python3
"""
Seed dummy expenses for a specific user.
"""
import sys
import os
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Add the expense-tracker directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'expense-tracker'))

from database.db import get_db

# Realistic Indian descriptions for each category
CATEGORY_DESCRIPTIONS = {
    'Food': [
        'Dinner at Indian restaurant',
        'Morning coffee at local cafe',
        'Grocery shopping at Reliance Fresh',
        'Lunch at office canteen',
        'Snacks from local bakery',
        'Roti and curry at home',
        'Street food evening',
        'Vegetarian thali',
        'Non-veg biryani',
        'Fast food meal'
    ],
    'Transport': [
        'Auto rickshaw ride',
        'Local train ticket',
        'Uber ride to office',
        'Bus pass recharge',
        'Taxi to airport',
        'Bike fuel',
        'Metro card top-up',
        'Rickshaw fare',
        'Ola cab booking',
        'Local transport'
    ],
    'Bills': [
        'Electricity bill payment',
        'Water supply bill',
        'Internet broadband charge',
        'Mobile phone recharge',
        'Gas cylinder refill',
        'House rent payment',
        'Maintenance charge',
        'Property tax',
        'Society fee',
        'Landline bill'
    ],
    'Health': [
        'Doctor consultation fee',
        'Medicine pharmacy purchase',
        'Dental check-up',
        'Vaccination shots',
        'Health insurance premium',
        'Ayurvedic medicines',
        'Hospital emergency visit',
        'Diagnostic tests',
        'Prescription drugs',
        'Health checkup'
    ],
    'Entertainment': [
        'Movie theater tickets',
        'Online gaming subscription',
        'Music streaming service',
        'Cultural event entry fee',
        'Cricket match tickets',
        'Digital content purchase',
        'Amusement park visit',
        'Concert tickets',
        'Theater show',
        'Sports event'
    ],
    'Shopping': [
        'Clothing store purchase',
        'Electronics item',
        'Footwear shopping',
        'Accessories and jewelry',
        'Home decor items',
        'Personal care products',
        'Grooming products',
        'Baby items',
        'Kitchenware',
        'Sports equipment'
    ],
    'Other': [
        'Pet food and supplies',
        'Alcoholic beverages',
        'Tobacco products',
        'Travel booking fee',
        'ATM withdrawal fee',
        'Bank service charges',
        'Digital wallet top-up',
        'Lottery/ticket purchase',
        'Fitness center membership',
        'Parking fee'
    ]
}


def parse_arguments():
    """Parse command line arguments."""
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if len(args) < 3:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        return None, None, None

    try:
        user_id = int(args[0])
        count = int(args[1])
        months = int(args[2])
    except ValueError:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        return None, None, None

    return user_id, count, months


def verify_user_exists(cursor, user_id):
    """Check if user exists in the users table."""
    cursor.execute('SELECT COUNT(*) FROM users WHERE id = ?', (user_id,))
    return cursor.fetchone()[0] > 0


def get_category_id_by_name(cursor, user_id, category_name):
    """Get or create a category ID for the given user and category name."""
    cursor.execute('SELECT id FROM categories WHERE user_id = ? AND name = ?', (user_id, category_name))
    result = cursor.fetchone()

    if result:
        return result[0]

    # Create category if it doesn't exist
    cursor.execute('''
        INSERT INTO categories (user_id, name)
        VALUES (?, ?)
    ''', (user_id, category_name))

    return cursor.lastrowid


def get_category_distribution(count):
    """
    Distribute expenses across categories proportionally.
    Food most common, Health and Entertainment least.
    """
    # Weighted distribution for 7 categories
    weights = {
        'Food': 35,      # Most common
        'Shopping': 20,  # Second most common
        'Bills': 15,     # Third most common
        'Transport': 12, # Fourth most common
        'Other': 8,      # Fifth most common
        'Health': 5,     # Second least common
        'Entertainment': 5  # Least common
    }

    # Calculate number of expenses per category
    distribution = {}
    remaining = count

    # Assign amounts based on weights
    for category, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        if remaining <= 0:
            distribution[category] = 0
            continue

        # Calculate this category's allocation
        category_count = int(count * weight / 100)
        distribution[category] = min(category_count, remaining)
        remaining -= distribution[category]

    # Distribute remaining expenses to avoid gaps
    if remaining > 0:
        for category in list(distribution.keys()):
            if remaining <= 0:
                break
            distribution[category] += 1
            remaining -= 1

    return distribution


def generate_expense_data(user_id, cursor, category_name, count, start_date, end_date):
    """Generate expense data for a specific category."""
    expenses = []

    # Get or create category ID
    category_id = get_category_id_by_name(cursor, user_id, category_name)

    for _ in range(count):
        # Generate random date within the range
        date_offset = random.randint(0, (end_date - start_date).days)
        expense_date = start_date + timedelta(days=date_offset)
        date_str = expense_date.strftime('%Y-%m-%d')

        # Generate amount based on category ranges (in INR)
        category_ranges = {
            'Food': (50, 800),
            'Transport': (20, 500),
            'Bills': (200, 3000),
            'Health': (100, 2000),
            'Entertainment': (100, 1500),
            'Shopping': (200, 5000),
            'Other': (50, 1000)
        }

        min_amount, max_amount = category_ranges[category_name]
        amount = round(random.uniform(min_amount, max_amount), 2)

        # Get random description
        descriptions = CATEGORY_DESCRIPTIONS[category_name]
        description = random.choice(descriptions)

        expenses.append((user_id, category_id, amount, description, date_str))

    return expenses


def seed_expenses(user_id, count, months):
    """Generate and insert expenses for a user."""
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Step 1: Verify user exists
        if not verify_user_exists(cursor, user_id):
            print(f"No user found with id {user_id}.")
            return

        # Step 2: Generate expenses
        # Calculate date range for the past months
        today = datetime.now()
        start_date = today - relativedelta(months=months)

        # Get category distribution
        distribution = get_category_distribution(count)

        all_expenses = []

        for category_name, category_count in distribution.items():
            if category_count <= 0:
                continue

            # Generate expenses for this category
            category_expenses = generate_expense_data(user_id, cursor, category_name, category_count, start_date, today)
            all_expenses.extend(category_expenses)

        if not all_expenses:
            print("No expenses to insert.")
            return

        # Step 3: Insert all expenses in a single transaction
        # Expenses tuple format: (user_id, category_id, amount, description, date)
        insert_query = '''
            INSERT INTO expenses (user_id, category_id, amount, description, date)
            VALUES (?, ?, ?, ?, ?)
        '''

        cursor.executemany(insert_query, all_expenses)
        conn.commit()

        # Step 4: Confirm and report
        print(f"Inserted {len(all_expenses)} expenses successfully.")

        # Get date range for all expenses
        cursor.execute('SELECT MIN(date), MAX(date) FROM expenses WHERE user_id = ?', (user_id,))
        min_date_result, max_date_result = cursor.fetchone()

        if min_date_result and max_date_result:
            print(f"Date range: {min_date_result} to {max_date_result}")

        # Get sample of 5 inserted records
        cursor.execute('''
            SELECT e.id, e.user_id, e.amount, c.name as category, e.date, e.description
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = ?
            ORDER BY e.id DESC
            LIMIT 5
        ''', (user_id,))

        sample_records = cursor.fetchall()
        print("Sample of 5 inserted records:")
        for record in sample_records:
            print(f"  - ID: {record['id']}, Amount: Rs {record['amount']}, "
                  f"Category: {record['category']}, Date: {record['date']}, "
                  f"Description: {record['description']}")

    except Exception as e:
        conn.rollback()
        print(f"Error seeding expenses: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    user_id, count, months = parse_arguments()

    if user_id is None:
        sys.exit(1)

    seed_expenses(user_id, count, months)
