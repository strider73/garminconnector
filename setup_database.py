#!/usr/bin/env python3
"""
Database Setup Script
Creates the optimized garmin_daily_metrics table in family_member_schedule database
"""

import psycopg2
import os

# Database configuration
DB_CONFIG = {
    'host': 'adventuretube.net',
    'port': 5432,
    'database': 'family_member_schedule',
    'user': 'postgres',
    'password': '5785Ch00'
}

def run_sql_file(cursor, filename):
    """Execute SQL commands from a file"""
    print(f"\n{'='*80}")
    print(f"Executing: {filename}")
    print('='*80)

    with open(filename, 'r') as f:
        sql = f.read()

    try:
        cursor.execute(sql)
        print(f"✅ {filename} executed successfully")
        return True
    except Exception as e:
        print(f"❌ Error executing {filename}: {e}")
        return False


def main():
    print("\n" + "="*80)
    print("GARMIN DAILY METRICS - DATABASE SETUP")
    print("="*80)
    print(f"\nDatabase: {DB_CONFIG['database']}")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Table: garmin_daily_metrics")
    print(f"\nThis will create a NEW optimized table with 53 fields:")
    print("  - 2 Identification (user_name, report_date)")
    print("  - 11 Training Load & Status")
    print("  - 9 Training Intensity Zones")
    print("  - 3 HRV")
    print("  - 13 Sleep (ENHANCED with quality metrics)")
    print("  - 3 Heart Rate")
    print("  - 3 Body Battery & Stress")
    print("  - 7 Daily Activity (NEW: steps, distance, calories)")
    print("  - 1 Metadata")

    # Ask for confirmation
    print("\n" + "="*80)
    response = input("\n⚠️  Proceed with table creation? (yes/no): ").strip().lower()

    if response != 'yes':
        print("\n❌ Cancelled by user")
        return

    # Connect to database
    print("\n📡 Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False  # Use transactions
        cursor = conn.cursor()
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    try:
        # Step 1: Create table
        if run_sql_file(cursor, 'create_garmin_table.sql'):
            conn.commit()
            print("\n✅ Table creation committed")
        else:
            conn.rollback()
            print("\n❌ Table creation rolled back")
            return

        # Step 2: Verify table
        print("\n" + "="*80)
        print("VERIFICATION")
        print("="*80)

        # Get column count
        cursor.execute("""
            SELECT COUNT(*) as total_columns
            FROM information_schema.columns
            WHERE table_name = 'garmin_daily_metrics'
        """)
        result = cursor.fetchone()
        total_columns = result[0] if result else 0

        print(f"\n📊 Total columns created: {total_columns}")

        if total_columns == 53:
            print("✅ Column count matches expected (53)")
        else:
            print(f"⚠️  Expected 53 columns, got {total_columns}")

        # Check primary key
        cursor.execute("""
            SELECT pg_get_constraintdef(c.oid) as constraint_def
            FROM pg_constraint c
            WHERE contype = 'p'
            AND conrelid = 'garmin_daily_metrics'::regclass
        """)
        result = cursor.fetchone()
        if result:
            print(f"✅ Primary key: {result[0]}")
        else:
            print("⚠️  No primary key found")

        # Check indexes
        cursor.execute("""
            SELECT COUNT(*) as index_count
            FROM pg_indexes
            WHERE tablename = 'garmin_daily_metrics'
        """)
        result = cursor.fetchone()
        index_count = result[0] if result else 0
        print(f"✅ Indexes created: {index_count}")

        # List new fields
        print("\n" + "="*80)
        print("NEW FIELDS ADDED (vs old schema)")
        print("="*80)

        new_fields = [
            'user_name (User identification)',
            'total_steps (Daily step count)',
            'total_distance_km (Distance in km)',
            'total_calories (Total calories burned)',
            'active_calories (Active calories)',
            'moderate_intensity_mins (Moderate intensity)',
            'vigorous_intensity_mins (Vigorous intensity)',
            'floors_climbed (Floors climbed)',
            'sleep_quality (Sleep quality: POOR/FAIR/GOOD/EXCELLENT)',
            'sleep_rem_percentage (REM sleep %)',
            'sleep_light_percentage (Light sleep %)',
            'sleep_deep_percentage (Deep sleep %)',
            'sleep_feedback (Sleep feedback text)',
            'sleep_insight (Sleep insight text)'
        ]

        for i, field in enumerate(new_fields, 1):
            print(f"  {i:2d}. {field}")

        print("\n" + "="*80)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Run verify_table.sql to see full table structure")
        print("  2. Update store_daily_metrics.py to populate new fields")
        print("  3. Run backfill to populate historical data")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()
        print("\n📡 Database connection closed")


if __name__ == "__main__":
    main()
