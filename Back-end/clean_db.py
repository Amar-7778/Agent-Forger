import sqlite3
import os
import json

DB_PATH = os.getenv("DB_PATH", "agents.db")

def run_migration():
    print(f"Connecting to database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database file does not exist. No action taken.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Clean agents table
    print("Scanning 'agents' table...")
    cursor.execute("SELECT id, name FROM agents")
    agents = cursor.fetchall()
    
    for row in agents:
        agent_id = row['id']
        name = row['name']
        stripped_name = name.strip()
        
        if name != stripped_name:
            print(f"Found agent with trailing/leading space: '{name}' (ID: {agent_id})")
            try:
                cursor.execute("UPDATE agents SET name = ? WHERE id = ?", (stripped_name, agent_id))
                print(f"  -> Updated to '{stripped_name}'")
            except sqlite3.IntegrityError as e:
                print(f"  -> Conflict: '{stripped_name}' already exists. Merging duplicate.")
                # If the stripped name already exists, delete this duplicate to preserve unique constraint
                cursor.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
                print(f"  -> Deleted duplicate agent ID {agent_id}")
                
    # 2. Clean scheduled_agents table
    print("Scanning 'scheduled_agents' table...")
    cursor.execute("SELECT id, name FROM scheduled_agents")
    schedules = cursor.fetchall()
    
    for row in schedules:
        schedule_id = row['id']
        name = row['name']
        stripped_name = name.strip()
        
        if name != stripped_name:
            print(f"Found schedule with trailing/leading space: '{name}' (ID: {schedule_id})")
            try:
                cursor.execute("UPDATE scheduled_agents SET name = ? WHERE id = ?", (stripped_name, schedule_id))
                print(f"  -> Updated to '{stripped_name}'")
            except sqlite3.IntegrityError as e:
                print(f"  -> Conflict: '{stripped_name}' schedule already exists. Deleting duplicate.")
                cursor.execute("DELETE FROM scheduled_agents WHERE id = ?", (schedule_id,))
                print(f"  -> Deleted duplicate schedule ID {schedule_id}")

    conn.commit()
    conn.close()
    print("Migration finished successfully.")

if __name__ == "__main__":
    run_migration()
