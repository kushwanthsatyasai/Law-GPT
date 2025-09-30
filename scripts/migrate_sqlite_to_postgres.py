"""
Script to migrate data from SQLite to PostgreSQL
Run this script to transfer all your development data to production PostgreSQL database
"""
import sqlite3
import psycopg
from sqlalchemy import create_engine, text
import sys
import os

def migrate_database(sqlite_path, postgres_url):
    """
    Migrate data from SQLite to PostgreSQL
    
    Args:
        sqlite_path: Path to SQLite database file
        postgres_url: PostgreSQL connection URL
    """
    print(f"🔄 Starting migration from SQLite to PostgreSQL...")
    print(f"   Source: {sqlite_path}")
    print(f"   Target: {postgres_url.split('@')[0]}@***")
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to PostgreSQL
        # Convert SQLAlchemy URL to psycopg connection string
        pg_url = postgres_url.replace('postgresql+psycopg://', 'postgresql://')
        pg_conn = psycopg.connect(pg_url)
        pg_cursor = pg_conn.cursor()
        
        # Get all tables from SQLite
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        print(f"\n📊 Found {len(tables)} tables to migrate: {', '.join(tables)}")
        
        # Migrate each table
        for table in tables:
            print(f"\n🔄 Migrating table: {table}")
            
            # Get all rows from SQLite table
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"   ⚠️  No data in table {table}")
                continue
            
            # Get column names
            column_names = [description[0] for description in sqlite_cursor.description]
            
            # Clear existing data in PostgreSQL table (optional - comment out if you want to append)
            try:
                pg_cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
                print(f"   🗑️  Cleared existing data in {table}")
            except Exception as e:
                print(f"   ⚠️  Could not truncate {table}: {e}")
            
            # Insert data into PostgreSQL
            placeholders = ','.join(['%s'] * len(column_names))
            columns = ','.join(column_names)
            insert_query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            success_count = 0
            for row in rows:
                try:
                    pg_cursor.execute(insert_query, tuple(row))
                    success_count += 1
                except Exception as e:
                    print(f"   ❌ Error inserting row: {e}")
                    print(f"      Row data: {dict(row)}")
            
            pg_conn.commit()
            print(f"   ✅ Migrated {success_count}/{len(rows)} rows")
        
        # Update sequences for auto-increment columns
        print(f"\n🔢 Updating PostgreSQL sequences...")
        for table in tables:
            try:
                pg_cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    AND column_default LIKE 'nextval%'
                """)
                id_columns = pg_cursor.fetchall()
                
                for (col,) in id_columns:
                    pg_cursor.execute(f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table}', '{col}'),
                            COALESCE((SELECT MAX({col}) FROM {table}), 1),
                            true
                        )
                    """)
                    print(f"   ✅ Updated sequence for {table}.{col}")
            except Exception as e:
                print(f"   ⚠️  Could not update sequence for {table}: {e}")
        
        pg_conn.commit()
        
        # Close connections
        sqlite_conn.close()
        pg_conn.close()
        
        print(f"\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Configuration
    SQLITE_PATH = "data/lawgpt.db"
    
    # Get PostgreSQL URL from environment or command line
    if len(sys.argv) > 1:
        POSTGRES_URL = sys.argv[1]
    else:
        POSTGRES_URL = os.environ.get('DATABASE_URL')
        if not POSTGRES_URL:
            print("❌ Please provide PostgreSQL URL as argument or set DATABASE_URL environment variable")
            print("Usage: python migrate_sqlite_to_postgres.py 'postgresql+psycopg://user:pass@host:port/dbname'")
            sys.exit(1)
    
    # Ensure PostgreSQL URL uses psycopg driver
    if POSTGRES_URL.startswith('postgresql://'):
        POSTGRES_URL = POSTGRES_URL.replace('postgresql://', 'postgresql+psycopg://')
    elif POSTGRES_URL.startswith('postgres://'):
        POSTGRES_URL = POSTGRES_URL.replace('postgres://', 'postgresql+psycopg://')
    
    migrate_database(SQLITE_PATH, POSTGRES_URL)
