"""
Migration script to add position_x and position_y columns to existing nodes table
"""
import sqlite3
from pathlib import Path

# Database path
db_path = Path(__file__).resolve().parent / 'chatbot.db'

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if position_x column exists
        cursor.execute("PRAGMA table_info(nodes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'position_x' not in columns:
            print("Adding position_x column...")
            cursor.execute("ALTER TABLE nodes ADD COLUMN position_x REAL DEFAULT 0.0")
            print("✓ Added position_x column")
        else:
            print("✓ position_x column already exists")
            
        if 'position_y' not in columns:
            print("Adding position_y column...")
            cursor.execute("ALTER TABLE nodes ADD COLUMN position_y REAL DEFAULT 0.0")
            print("✓ Added position_y column")
        else:
            print("✓ position_y column already exists")
        
        # Update existing nodes with default positions (grid layout)
        cursor.execute("SELECT id FROM nodes WHERE position_x = 0.0 AND position_y = 0.0")
        nodes = cursor.fetchall()
        
        for i, (node_id,) in enumerate(nodes):
            x = (i % 3) * 350
            y = (i // 3) * 200
            cursor.execute("UPDATE nodes SET position_x = ?, position_y = ? WHERE id = ?", (x, y, node_id))
        
        if nodes:
            print(f"✓ Updated positions for {len(nodes)} existing nodes")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("The database will be created automatically when you start the server.")
    else:
        migrate()
