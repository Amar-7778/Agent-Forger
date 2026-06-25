import os
import sys
import json
import datetime
import urllib.parse
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add current path to python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from storage.agent_registry import (
    list_agents, get_agent, save_agent, delete_agent,
    list_scheduled_agents, save_scheduled_agent, delete_scheduled_agent, update_scheduled_agent_status
)
from storage.history_store import get_history, add_message, clear_history
from tools.rag_tool import ingest_document, query_knowledge_base
from brain.llm_factory import get_llm
from brain.router import route_request

app = FastAPI(title="AgentForge API")

# Enable CORS for frontend local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class AgentCreate(BaseModel):
    name: str
    description: str
    scope: str = ""
    restrictions: str = ""
    tools: List[str] = []
    theme: str = "cyberpunk"
    icon: str = "🤖"

class ScheduleCreate(BaseModel):
    agentId: str
    task: str
    frequency: str
    destination: str = ""

class ChatRequest(BaseModel):
    prompt: str
    agentName: Optional[str] = None  # None for Master Agent
    sessionId: Optional[str] = None

# --- Helper functions ---

def slugify(name: str) -> str:
    import re
    cleaned = name.strip()
    cleaned = re.sub(r'\s+', '-', cleaned)
    return cleaned.lower()

def get_agent_by_slug(slug: str):
    agents = list_agents()
    for a in agents:
        if slugify(a["name"]) == slug:
            return a
    return None

def agent_db_to_api(agent_db):
    name = agent_db.get("name", "")
    agent_id = slugify(name)
    
    # Generate quick actions
    quick_actions = [
        f"Ask about scope",
        f"Help menu",
    ]
    tools = agent_db.get("tools", [])
    if "RAG Knowledge Base" in tools or "RAG" in tools:
        quick_actions.append("Search docs")
    if "Web Search" in tools or "Tavily" in tools:
        quick_actions.append("Search the web")
    if "Slack Output" in tools or "Slack MCP" in tools:
        quick_actions.append("Slack update")
    if "Email Output" in tools:
        quick_actions.append("Draft email")
        
    while len(quick_actions) < 5:
        for act in ["Restrictions?", "Execution plan", "List tools"]:
            if act not in quick_actions and len(quick_actions) < 5:
                quick_actions.append(act)
                
    return {
        "id": agent_id,
        "name": name,
        "icon": agent_db.get("icon", "🤖"),
        "company": "Acme Corp",
        "status": "active",
        "purpose": agent_db.get("description", ""),
        "tools": tools,
        "lastUsed": "Just now",
        "quickActions": quick_actions,
        "scope": agent_db.get("scope", ""),
        "restrictions": agent_db.get("restrictions", ""),
        "theme": agent_db.get("theme", "cyberpunk"),
    }

# --- API Endpoints ---

@app.get("/api/agents")
def get_all_agents():
    agents = list_agents()
    return [agent_db_to_api(a) for a in agents]

@app.get("/api/agents/{agent_id}")
def get_single_agent(agent_id: str):
    agent_db = get_agent_by_slug(agent_id)
    if not agent_db:
        # Fallback to direct name query
        agent_db = get_agent(agent_id)
    if not agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_db_to_api(agent_db)

@app.post("/api/agents")
def create_agent(agent: AgentCreate):
    stripped_name = agent.name.strip()
    agent_data = {
        "name": stripped_name,
        "description": agent.description,
        "scope": agent.scope,
        "restrictions": agent.restrictions,
        "tools": agent.tools,
        "theme": agent.theme,
        "icon": agent.icon,
        "knowledge_base": None
    }
    try:
        agent_id = save_agent(agent_data)
        return {"id": slugify(stripped_name), "db_id": agent_id, "name": stripped_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/agents/{agent_name}")
def api_delete_agent(agent_name: str):
    # Try looking it up by slug first
    agent_db = get_agent_by_slug(agent_name)
    name_to_del = agent_db["name"] if agent_db else agent_name
    
    try:
        delete_agent(name_to_del)
        # Also delete schedules associated with this agent name/slug
        schedules = list_scheduled_agents()
        for s in schedules:
            if s["name"] == name_to_del or slugify(s["name"]) == slugify(name_to_del):
                delete_scheduled_agent(s["name"])
        # Clear chat history
        session_id = f"agent_chat_{name_to_del.replace(' ', '_').lower()}"
        clear_history(session_id)
        return {"status": "success", "message": f"Agent '{name_to_del}' and related data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/schedules")
def get_schedules():
    tasks = list_scheduled_agents()
    agents_list = list_agents()
    
    formatted_tasks = []
    for t in tasks:
        # Find corresponding agent ID/slug
        agent_name = t["name"]
        agent_id = slugify(agent_name)
        # Check if agent exists, otherwise default
        agent_exists = any(slugify(a["name"]) == agent_id for a in agents_list)
        
        formatted_tasks.append({
            "id": str(t["id"]),
            "agentId": agent_id if agent_exists else "master-agent",
            "agentName": agent_name,
            "task": t["task"],
            "frequency": f"{t['schedule_type'].title()}: {t['schedule_value']}" if t['schedule_type'] else t['schedule_value'],
            "nextRun": "in 3 hours" if t["status"] == "active" else "—",
            "status": t["status"]
        })
    return formatted_tasks

@app.post("/api/schedules")
def create_schedule(task: ScheduleCreate):
    # Get agent name from id/slug
    agent_db = get_agent_by_slug(task.agentId)
    agent_name = agent_db["name"] if agent_db else task.agentId
    
    # Simple scheduler format mapping
    schedule_value = task.frequency
    schedule_type = "interval"
    if "*" in task.frequency:
        schedule_type = "cron"
    
    agent_data = {
        "name": agent_name,
        "task": task.task,
        "schedule_type": schedule_type,
        "schedule_value": schedule_value,
        "destination": task.destination or "System Logs",
        "status": "active"
    }
    
    try:
        task_id = save_scheduled_agent(agent_data)
        return {"id": str(task_id), "status": "active"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/schedules/{name}/status")
def toggle_schedule_status(name: str, status: dict):
    new_status = status.get("status", "active")
    # Try slug lookup
    schedules = list_scheduled_agents()
    target_name = name
    for s in schedules:
        if slugify(s["name"]) == slugify(name):
            target_name = s["name"]
            break
            
    try:
        update_scheduled_agent_status(target_name, new_status)
        return {"status": "success", "name": target_name, "new_status": new_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/schedules/{name}")
def api_delete_schedule(name: str):
    schedules = list_scheduled_agents()
    target_name = name
    for s in schedules:
        if slugify(s["name"]) == slugify(name) or s["name"] == name:
            target_name = s["name"]
            break
            
    try:
        delete_scheduled_agent(target_name)
        return {"status": "success", "message": f"Schedule '{target_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def api_chat(req: ChatRequest):
    session_id = req.sessionId or "default_session"
    prompt = req.prompt
    
    # 1. Master Agent chat
    if not req.agentName or req.agentName == "master-agent" or req.agentName == "assistant":
        session_id = req.sessionId or "master_chat"
        add_message(session_id, "user", prompt)
        try:
            response = route_request(prompt)
        except Exception as e:
            response = f"I encountered an error: {e}"
        add_message(session_id, "assistant", response)
        return {
            "from": "agent",
            "text": response,
            "time": datetime.datetime.now().strftime("%I:%M %p")
        }
    
    # 2. Specific Custom Agent Chat
    agent_db = get_agent_by_slug(req.agentName)
    if not agent_db:
        # Fallback to direct name query
        agent_db = get_agent(req.agentName)
        
    if not agent_db:
        raise HTTPException(status_code=404, detail=f"Agent '{req.agentName}' not found")
        
    agent_name = agent_db["name"]
    session_id = f"agent_chat_{agent_name.replace(' ', '_').lower()}"
    add_message(session_id, "user", prompt)
    
    tools = agent_db.get("tools", [])
    desc = agent_db.get("description", "")
    scope = agent_db.get("scope", "General purpose")
    restrictions = agent_db.get("restrictions", "None")
    
    context = ""
    # RAG search trigger
    if "RAG Knowledge Base" in tools and any(x in prompt.lower() for x in ["search", "knowledge", "document", "policy", "info"]):
        context = query_knowledge_base(prompt)
    # Web search trigger
    elif "Web Search" in tools and any(x in prompt.lower() for x in ["web", "search", "google", "news"]):
        context = f"Simulated Web Search for: '{prompt}' found no new external updates."
        
    system_prompt = f"""
    You are the specialized business agent '{agent_name}'.
    Description: {desc}
    Scope of Operations: {scope}
    Restrictions: {restrictions}
    Available Tools: {tools}
    
    Context of active tools / RAG retrieval: {context}
    
    You MUST follow the constraints:
    - Respond directly to the user.
    - Answer in direct, short, actionable, and clear terms.
    - Do NOT run tools or perform tasks outside your scope or boundaries.
    - If a request violates your restrictions, state it politely but firmly.
    """
    
    try:
        llm = get_llm()
        response_obj = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        response = response_obj.content
    except Exception as e:
        response = f"Sorry, {agent_name} encountered an error: {e}"
        
    add_message(session_id, "assistant", response)
    
    return {
        "from": "agent",
        "text": response,
        "time": datetime.datetime.now().strftime("%I:%M %p")
    }

@app.get("/api/chat/history/{agent_name}")
def get_chat_history(agent_name: str):
    if agent_name == "master-agent" or agent_name == "assistant":
        session_id = "master_chat"
    else:
        agent_db = get_agent_by_slug(agent_name)
        name = agent_db["name"] if agent_db else agent_name
        session_id = f"agent_chat_{name.replace(' ', '_').lower()}"
        
    history = get_history(session_id)
    formatted = []
    for msg in history:
        timestamp = msg.get("timestamp", "")
        try:
            # Format time
            time_part = timestamp.split(" ")[1][:5] if timestamp else datetime.datetime.now().strftime("%H:%M")
        except Exception:
            time_part = timestamp[:5]
        formatted.append({
            "from": "user" if msg["role"] == "user" else "agent",
            "text": msg["content"],
            "time": time_part
        })
    return formatted

@app.post("/api/chat/clear/{agent_name}")
def api_clear_chat(agent_name: str):
    if agent_name == "master-agent" or agent_name == "assistant":
        session_id = "master_chat"
    else:
        agent_db = get_agent_by_slug(agent_name)
        name = agent_db["name"] if agent_db else agent_name
        session_id = f"agent_chat_{name.replace(' ', '_').lower()}"
    try:
        clear_history(session_id)
        return {"status": "success", "message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge")
def get_knowledge_files():
    docs_dir = os.path.join(os.path.dirname(__file__), "data", "company_docs")
    if not os.path.exists(docs_dir):
        return []
    files = []
    for f in os.listdir(docs_dir):
        f_path = os.path.join(docs_dir, f)
        if os.path.isfile(f_path):
            stat = os.stat(f_path)
            files.append({
                "name": f,
                "size": stat.st_size,
                "uploadedAt": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            })
    return files

@app.post("/api/knowledge/upload")
async def upload_knowledge_file(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        success, message = ingest_document(file.filename, file_bytes)
        if not success:
            raise HTTPException(status_code=400, detail=message)
        return {"status": "success", "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/knowledge/{file_name}")
def delete_knowledge_file(file_name: str):
    docs_dir = os.path.join(os.path.dirname(__file__), "data", "company_docs")
    file_path = os.path.join(docs_dir, file_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            # Re-initializing vector database is complex, but file deletion works.
            # In production, we'd also remove documents with metadata source=file_name from Chroma.
            return {"status": "success", "message": f"File '{file_name}' deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/api/metrics")
def get_metrics():
    agents = list_agents()
    schedules = list_scheduled_agents()
    
    active_schedules_count = sum(1 for s in schedules if s["status"] == "active")
    
    return {
        "totalAgents": {"value": len(agents), "delta": "+1 this week" if len(agents) > 0 else "no change"},
        "activeSchedules": {"value": active_schedules_count, "delta": "no change"},
        "tasksThisWeek": {"value": len(schedules) * 12 + 5, "delta": "+8% vs last week"},
        "messagesToday": {"value": 42, "delta": "+12 since yesterday"}
    }

if __name__ == "__main__":
    import uvicorn
    # In Windows PowerShell, run: python Back-end/main.py
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
