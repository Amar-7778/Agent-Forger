import time
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from storage.agent_registry import list_scheduled_agents

def execute_scheduled_task(agent):
    print(f"[Scheduler] Executing task for {agent['name']}: {agent['task']} -> Sending to {agent['destination']}")
    # In a production system, this would call tools.langgraph_planner or tools.mcp_executor
    
def check_and_run():
    print("[Scheduler] Checking for active scheduled agents...")
    agents = list_scheduled_agents()
    for agent in agents:
        if agent['status'] == 'active':
            execute_scheduled_task(agent)

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Simplified: Polls database every 60 seconds and runs active tasks.
    # In a robust production environment, jobs would be added to APScheduler dynamically.
    scheduler.add_job(check_and_run, 'interval', seconds=60)
    scheduler.start()
    print("Scheduler started. Polling every 60 seconds...")
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    start_scheduler()
