import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "agents.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Custom Agents Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            scope TEXT,
            restrictions TEXT,
            tools TEXT, -- JSON list
            knowledge_base TEXT, -- Optional ID/Name of KB
            theme TEXT,
            icon TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Scheduled Agents Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            task TEXT NOT NULL,
            schedule_type TEXT, -- 'cron' or 'interval'
            schedule_value TEXT,
            destination TEXT,
            status TEXT DEFAULT 'active', -- 'active' or 'paused'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize on import
init_db()

# --- Custom Agent Registry ---

def save_agent(agent_data: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    name = agent_data.get('name', '').strip()
    # Check if exists to do update vs insert
    cursor.execute('SELECT id FROM agents WHERE name = ?', (name,))
    existing = cursor.fetchone()
    
    tools = agent_data.get('tools', [])
    if isinstance(tools, list):
        tools = json.dumps(tools)
        
    if existing:
        cursor.execute('''
            UPDATE agents SET 
            description=?, scope=?, restrictions=?, tools=?, knowledge_base=?, theme=?, icon=?
            WHERE name=?
        ''', (
            agent_data.get('description'),
            agent_data.get('scope'),
            agent_data.get('restrictions'),
            tools,
            agent_data.get('knowledge_base'),
            agent_data.get('theme', 'dark'),
            agent_data.get('icon', '🤖'),
            name
        ))
        agent_id = existing['id']
    else:
        cursor.execute('''
            INSERT INTO agents 
            (name, description, scope, restrictions, tools, knowledge_base, theme, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            agent_data.get('description'),
            agent_data.get('scope'),
            agent_data.get('restrictions'),
            tools,
            agent_data.get('knowledge_base'),
            agent_data.get('theme', 'dark'),
            agent_data.get('icon', '🤖')
        ))
        agent_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return agent_id

def get_agent(name: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM agents WHERE name = ?', (name.strip(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        agent = dict(row)
        if agent['tools']:
            agent['tools'] = json.loads(agent['tools'])
        else:
            agent['tools'] = []
        return agent
    return None

def list_agents() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM agents')
    rows = cursor.fetchall()
    conn.close()
    agents = []
    for row in rows:
        agent = dict(row)
        if agent['tools']:
            agent['tools'] = json.loads(agent['tools'])
        else:
            agent['tools'] = []
        agents.append(agent)
    return agents

def delete_agent(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM agents WHERE name = ?', (name.strip(),))
    conn.commit()
    conn.close()

# --- Scheduled Agent Registry ---

def save_scheduled_agent(agent_data: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    name = agent_data.get('name', '').strip()
    cursor.execute('SELECT id FROM scheduled_agents WHERE name = ?', (name,))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute('''
            UPDATE scheduled_agents SET 
            task=?, schedule_type=?, schedule_value=?, destination=?, status=?
            WHERE name=?
        ''', (
            agent_data.get('task'),
            agent_data.get('schedule_type'),
            agent_data.get('schedule_value'),
            agent_data.get('destination'),
            agent_data.get('status', 'active'),
            name
        ))
        agent_id = existing['id']
    else:
        cursor.execute('''
            INSERT INTO scheduled_agents 
            (name, task, schedule_type, schedule_value, destination, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            name,
            agent_data.get('task'),
            agent_data.get('schedule_type'),
            agent_data.get('schedule_value'),
            agent_data.get('destination'),
            agent_data.get('status', 'active')
        ))
        agent_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return agent_id

def list_scheduled_agents() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scheduled_agents')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_scheduled_agent_status(name: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE scheduled_agents SET status = ? WHERE name = ?', (status, name.strip()))
    conn.commit()
    conn.close()

def delete_scheduled_agent(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM scheduled_agents WHERE name = ?', (name.strip(),))
    conn.commit()
    conn.close()
