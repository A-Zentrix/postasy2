#!/usr/bin/env python3
"""
Lightweight migration to add missing columns to the SQLite database.
Currently adds user.razorpay_customer_id if it does not exist.
"""

from app import app, db
from sqlalchemy import inspect, text


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in the given table."""
    inspector = inspect(db.engine)
    for col in inspector.get_columns(table_name):
        if col.get("name") == column_name:
            return True
    return False


def migrate():
    print("🔧 Running migration checks...")
    with app.app_context():
        # Ensure tables exist first
        db.create_all()

        # Add user.razorpay_customer_id if missing
        if not column_exists("user", "razorpay_customer_id"):
            print("➡️  Adding column user.razorpay_customer_id")
            db.session.execute(
                text("ALTER TABLE user ADD COLUMN razorpay_customer_id VARCHAR(100)")
            )
            db.session.commit()
            print("✅ Added user.razorpay_customer_id")
        else:
            print("✅ Column user.razorpay_customer_id already exists")

        # Ensure subscription table has all expected columns
        def add_col(table: str, name: str, ddl: str):
            if not column_exists(table, name):
                print(f"➡️  Adding column {table}.{name}")
                db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
                db.session.commit()
                print(f"✅ Added {table}.{name}")
            else:
                print(f"✅ Column {table}.{name} already exists")

        # Columns for subscription based on models.Subscription
        add_col("subscription", "razorpay_customer_id", "VARCHAR(100)")
        add_col("subscription", "razorpay_subscription_id", "VARCHAR(100)")
        add_col("subscription", "razorpay_payment_id", "VARCHAR(100)")
        add_col("subscription", "plan_id", "VARCHAR(20)")
        add_col("subscription", "status", "VARCHAR(20)")
        add_col("subscription", "current_period_start", "DATETIME")
        add_col("subscription", "current_period_end", "DATETIME")
        add_col("subscription", "created_at", "DATETIME")
        add_col("subscription", "updated_at", "DATETIME")

        print("🎉 Migrations complete!")


if __name__ == "__main__":
    migrate()


