#!/usr/bin/env python3
"""
Sync data from Neon cloud database to local PostgreSQL
"""

import psycopg2
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def sync_cloud_to_local():
    """Sync all data from cloud to local database"""

    # Database URLs from environment variables
    cloud_db_url = os.getenv('DATABASE_URL')
    local_db_url = "postgresql://cv_user:cv_password@localhost:5432/cv_builder"

    if not cloud_db_url:
        print("❌ DATABASE_URL environment variable not found")
        sys.exit(1)

    try:
        # Connect to both databases
        print("Connecting to cloud database...")
        cloud_conn = psycopg2.connect(cloud_db_url)
        cloud_cur = cloud_conn.cursor()

        print("Connecting to local database...")
        local_conn = psycopg2.connect(local_db_url)
        local_cur = local_conn.cursor()

        # Get all table names
        cloud_cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        tables = [row[0] for row in cloud_cur.fetchall()]
        print(f"Found tables: {tables}")

        # Sync each table
        for table in tables:
            print(f"\nSyncing table: {table}")

            # Clear local table
            local_cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")

            # Get all data from cloud
            cloud_cur.execute(f"SELECT * FROM {table}")
            rows = cloud_cur.fetchall()

            if rows:
                # Get column names
                cloud_cur.execute(f"""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = '{table}' ORDER BY ordinal_position
                """)
                columns = [row[0] for row in cloud_cur.fetchall()]

                # Insert into local
                placeholders = ','.join(['%s'] * len(columns))
                columns_str = ','.join(columns)

                insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                local_cur.executemany(insert_query, rows)

                print(f"  Synced {len(rows)} rows")
            else:
                print(f"  No data in {table}")

        # Commit changes
        local_conn.commit()
        print("\n✅ Sync completed successfully!")

        # Close connections
        cloud_cur.close()
        cloud_conn.close()
        local_cur.close()
        local_conn.close()

    except Exception as e:
        print(f"❌ Sync failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting cloud to local database sync...")
    sync_cloud_to_local()