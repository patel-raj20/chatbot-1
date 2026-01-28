"""
Migration script to add position_x and position_y columns to PostgreSQL nodes table
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Raj%402006@localhost:5432/chatbot_db")

# Parse connection string
# Format: postgresql://user:password@host:port/database
url_parts = DATABASE_URL.replace("postgresql://", "").replace("postgres://", "")
user_pass, host_db = url_parts.split("@")
user, password = user_pass.split(":")
host_port, database = host_db.split("/")
host, port = host_port.split(":") if ":" in host_port else (host_port, "5432")

# Decode URL-encoded password
from urllib.parse import unquote
password = unquote(password)

def migrate():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Check if position_x column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='nodes' AND column_name='position_x'
        """)
        
        if not cursor.fetchone():
            print("Adding position_x column...")
            cursor.execute("ALTER TABLE nodes ADD COLUMN position_x DOUBLE PRECISION DEFAULT 0.0")
            print("✓ Added position_x column")
        else:
            print("✓ position_x column already exists")
        
        # Check if position_y column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='nodes' AND column_name='position_y'
        """)
        
        if not cursor.fetchone():
            print("Adding position_y column...")
            cursor.execute("ALTER TABLE nodes ADD COLUMN position_y DOUBLE PRECISION DEFAULT 0.0")
            print("✓ Added position_y column")
        else:
            print("✓ position_y column already exists")
        
        # Update existing nodes with default positions (grid layout)
        cursor.execute("SELECT id FROM nodes WHERE position_x = 0.0 AND position_y = 0.0 ORDER BY created_at")
        nodes = cursor.fetchall()
        
        for i, (node_id,) in enumerate(nodes):
            x = float((i % 3) * 350)
            y = float((i // 3) * 200)
            cursor.execute("UPDATE nodes SET position_x = %s, position_y = %s WHERE id = %s", (x, y, node_id))
        
        if nodes:
            print(f"✓ Updated positions for {len(nodes)} existing nodes")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate()
