import streamlit as st
import sys
import os

# Adjust paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from storage.agent_registry import (
    list_scheduled_agents, save_scheduled_agent, delete_scheduled_agent, update_scheduled_agent_status
)
from ui.layout import page_heading, muted_body_text, render_active_badge, render_gray_badge

def show_scheduled_agents():
    # --- QUERY PARAMETER CONTROLLER ---
    to_delete = st.query_params.get("delete_sched", None)
    if to_delete:
        delete_scheduled_agent(to_delete)
        st.query_params.pop("delete_sched")
        st.success(f"Automation '{to_delete}' deleted successfully!")
        st.rerun()
        
    to_toggle = st.query_params.get("toggle_sched", None)
    if to_toggle:
        # Check current status
        agents = list_scheduled_agents()
        agent = next((a for a in agents if a["name"] == to_toggle), None)
        if agent:
            new_status = "paused" if agent["status"] == "active" else "active"
            update_scheduled_agent_status(to_toggle, new_status)
            st.success(f"Automation '{to_toggle}' is now {new_status}!")
        st.query_params.pop("toggle_sched")
        st.rerun()

    page_heading("⏰ Scheduled Tasks")
    muted_body_text("Manage and audit your recurring automated agent workflows.")
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # --- TABLE AND LAYOUT STYLING ---
    st.markdown("""
<style>
.af-table-container {
  border: 1px solid #2E3148;
  border-radius: 12px;
  background: #1A1D27;
  overflow: hidden;
  margin-top: 16px;
  margin-bottom: 24px;
}
.af-table {
  width: 100%;
  border-collapse: collapse;
}
.af-table th {
  background: #222536;
  color: #F1F1F3;
  text-align: left;
  padding: 14px 16px;
  font-size: 13px;
  font-weight: 600;
  border-bottom: 1px solid #2E3148;
}
.af-table td {
  padding: 14px 16px;
  font-size: 13px;
  color: #9395A5;
  border-bottom: 1px solid #2E3148;
  vertical-align: middle;
}
.af-table tr:last-child td {
  border-bottom: none;
}
.af-table tr:hover {
  background: #22253640;
}
.action-btn {
  color: #F97316 !important;
  font-weight: 600;
  text-decoration: none;
  margin-right: 12px;
  cursor: pointer;
  font-size: 13px;
}
.action-btn:hover {
  color: #EA6A0A !important;
  text-decoration: underline;
}
.action-btn.delete {
  color: #EF4444 !important;
}
.action-btn.delete:hover {
  color: #EF4444BB !important;
  text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

    # --- CREATE AUTOMATION FORM ---
    with st.expander("Create New Automation", expanded=False):
        with st.form("scheduled_agent_form"):
            name = st.text_input("Automation Name", placeholder="e.g. Daily Sales Report")
            task = st.text_area("Task Description", placeholder="What should the agent do?")
            
            col1, col2 = st.columns(2)
            with col1:
                schedule_type = st.selectbox("Schedule Type", ["cron", "interval"])
            with col2:
                schedule_value = st.text_input("Schedule Value", placeholder="e.g. 0 8 * * * (Cron) or 60 (Minutes interval)")
                
            destination = st.text_input("Destination", placeholder="e.g. email@example.com")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Create Automation")
            if submitted:
                if name and task and schedule_value:
                    agent_data = {
                        "name": name,
                        "task": task,
                        "schedule_type": schedule_type,
                        "schedule_value": schedule_value,
                        "destination": destination,
                        "status": "active"
                    }
                    save_scheduled_agent(agent_data)
                    st.success(f"Automation '{name}' created successfully!")
                    st.rerun()
                else:
                    st.error("Name, Task, and Schedule Value are required.")

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    agents = list_scheduled_agents()
    
    if not agents:
        # Render empty state
        st.markdown("""
        <div style="text-align: center; padding: 48px 24px; background: #1A1D27; border: 1px solid #2E3148; border-radius: 12px;">
          <div style="font-size: 48px; color: #2E3148; margin-bottom: 16px;">⏰</div>
          <h2 style="font-size: 18px; font-weight: 600; color: #9395A5; margin-bottom: 8px;">No scheduled tasks yet</h2>
          <p style="font-size: 14px; color: #5A5C6E; max-width: 400px; margin: 0 auto 24px;">Tell AgentForge to run automated workflows automatically on a repeating timeline.</p>
          <a href="?page=schedules" target="_self" onclick="alert('Open Create New Automation above to schedule a task.'); return false;" style="
            background: #F97316; color: #0F1117; border: none;
            border-radius: 8px; padding: 10px 20px; text-decoration: none;
            font-weight: 600; font-size: 14px; display: inline-block;
          ">Schedule a task →</a>
        </div>
        """, unsafe_allow_html=True)
        return

    # --- RENDER TABLE ---
    table_rows_html = ""
    for idx, agent in enumerate(agents):
        name = agent["name"]
        task = agent["task"]
        # Truncate task to 40 chars
        truncated_task = task[:40] + "..." if len(task) > 40 else task
        
        freq = f"{agent['schedule_type'].title()}: {agent['schedule_value']}"
        freq_badge = f'<span class="af-badge">{freq}</span>'
        
        status = agent["status"]
        if status == "active":
            status_badge = '<span class="af-badge-green">Active</span>'
            toggle_action = "Pause"
        else:
            status_badge = '<span class="af-badge-gray">Paused</span>'
            toggle_action = "Resume"
            
        next_run = "in 3 hours" if status == "active" else "—" # realistic mock value for scheduler
        
        table_rows_html += f"""
<tr>
  <td style="font-weight: 600; color: #F1F1F3;">⏰ {name}</td>
  <td title="{task}">{truncated_task}</td>
  <td>{freq_badge}</td>
  <td>{next_run}</td>
  <td>{status_badge}</td>
  <td>
    <a href="?page=schedules&toggle_sched={name}" target="_self" class="action-btn">{toggle_action}</a>
    <a href="?page=schedules&delete_sched={name}" target="_self" class="action-btn delete">Delete</a>
  </td>
</tr>
"""

    st.markdown(f"""
<div class="af-table-container">
  <table class="af-table">
    <thead>
      <tr>
        <th>Agent</th>
        <th>Task</th>
        <th>Frequency</th>
        <th>Next Run</th>
        <th>Status</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {table_rows_html}
    </tbody>
  </table>
</div>
""", unsafe_allow_html=True)
