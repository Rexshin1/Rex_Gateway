
import sqlite3
import os

# Path to database file - assuming standard Flask instance/ folder or app root
# We'll try common locations
db_paths = [
    'flask_server/app/database.db', 
    'instance/database.db',
    'database.db',
    'app.db',
    'flask_server/database.db'
]

# Find the valid path
db_path = None
for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    # If not found, try to search for .db files
    print("Database path not found in candidate list. Searching...")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".db"):
                db_path = os.path.join(root, file)
                break
        if db_path: break

if db_path:
    print(f"Migrating database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(device_records)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'water' not in columns:
            print("Adding 'water' column to device_records...")
            cursor.execute("ALTER TABLE device_records ADD COLUMN water FLOAT")
            conn.commit()

        # New Power functionality columns
        new_cols = ['voltage', 'current', 'frequency', 'energy', 'water_level', 'total_volume']
        for col in new_cols:
            if col not in columns:
                 print(f"Adding '{col}' column to device_records...")
                 cursor.execute(f"ALTER TABLE device_records ADD COLUMN {col} FLOAT")
                 conn.commit()
                 
        print("Migration successful.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()
else:
    print("Could not find database file!")
