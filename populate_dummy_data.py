#!/usr/bin/env python
"""
Simple script to populate the database with dummy data.
Run this script from the project root directory.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

# Now import Django models and run the population
from django.core.management import call_command

if __name__ == "__main__":
    print("🚀 Starting database population...")
    print("This will create dummy data for users, products, and orders.")
    print()

    # Ask user if they want to clear existing data
    clear_data = (
        input("Do you want to clear existing data first? (y/N): ").lower().strip()
    )

    if clear_data in ["y", "yes"]:
        print("⚠️  Clearing existing data and populating with fresh dummy data...")
        call_command(
            "populate_db", "--clear", "--users=15", "--products=60", "--orders=30"
        )
    else:
        print("📝 Adding dummy data to existing database...")
        call_command("populate_db", "--users=10", "--products=50", "--orders=25")

    print()
    print("✅ Database population completed!")
    print()
    print("📊 Summary of created data:")
    print("   - Users: Test users with username/password combinations")
    print("   - Products: Various categories (Electronics, Clothing, Books, etc.)")
    print("   - Orders: Orders with multiple items and realistic data")
    print()
    print("🔐 All test users have password: 'testpass123'")
    print("🌐 You can now test the API endpoints with this data!")
