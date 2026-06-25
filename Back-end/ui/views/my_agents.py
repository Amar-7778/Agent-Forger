import streamlit as st
import sys
import os

# Adjust paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from storage.agent_registry import list_agents, delete_agent
from ui.layout import page_heading, muted_body_text, render_tool_badge

def show_my_agents():
    # Handle deletion query param
    to_delete = st.query_params.get("delete", None)
    if to_delete:
        delete_agent(to_delete)
        st.query_params.pop("delete")
        st.success(f"Agent '{to_delete}' deleted successfully!")
        st.rerun()

    page_heading("🤖 Custom Agents")
    muted_body_text("Manage and configure your custom AI workers.")
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    
    # Custom delete button style injection
    st.markdown("""
<style>
.open-link-btn {
  background: #F97316;
  color: #0F1117 !important;
  border: none;
  border-radius: 6px;
  padding: 7px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: background 0.2s, transform 0.1s;
}
.open-link-btn:hover {
  background: #EA6A0A;
  transform: translateY(-1px);
}
.delete-link-btn {
  background: #EF444420;
  color: #EF4444 !important;
  border: 1px solid #EF444440;
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: background 0.2s, border-color 0.2s;
}
.delete-link-btn:hover {
  background: #EF444440;
  border-color: #EF4444;
}
</style>
""", unsafe_allow_html=True)

    agents = list_agents()
    
    if not agents:
        # Render empty state
        st.markdown("""
        <div style="text-align: center; padding: 48px 24px; background: #1A1D27; border: 1px solid #2E3148; border-radius: 12px; margin-top: 16px;">
          <div style="font-size: 48px; color: #2E3148; margin-bottom: 16px;">🤖</div>
          <h2 style="font-size: 18px; font-weight: 600; color: #9395A5; margin-bottom: 8px;">No custom agents found</h2>
          <p style="font-size: 14px; color: #5A5C6E; max-width: 400px; margin: 0 auto 24px;">Deploy a specialized AI agent to automate specific business logic and workflows.</p>
          <a href="?page=agent_builder" target="_self" style="
            background: #F97316; color: #0F1117; border: none;
            border-radius: 8px; padding: 10px 20px; text-decoration: none;
            font-weight: 600; font-size: 14px; display: inline-block;
          ">Build an agent →</a>
        </div>
        """, unsafe_allow_html=True)
        return

    # Render agents as cards
    cols = st.columns(3)
    for idx, agent in enumerate(agents):
        name = agent["name"]
        icon = agent.get("icon", "🤖")
        purpose = agent.get("description", "")
        scope = agent.get("scope", "General purpose")
        tools = agent.get("tools", [])
        
        # Tools badges
        tool_tags_html = ""
        for tool in tools:
            tool_tags_html += f'<span class="af-badge">{tool}</span>\n'
        if not tool_tags_html:
            tool_tags_html = '<span class="af-badge-gray">No Tools</span>'
            
        last_used = agent.get("created_at", "Just now")
        if " " in last_used:
            last_used = last_used.split(" ")[0]

        with cols[idx % 3]:
            st.markdown(f"""
<div class="af-card">
  <div style="display:flex;justify-content:space-between;
              align-items:flex-start;margin-bottom:12px;">
    <div style="display:flex;align-items:center;gap:12px;">
      <!-- Icon circle -->
      <div style="
        width:44px;height:44px;border-radius:10px;
        background:#F9731615;border:1px solid #F9731630;
        display:flex;align-items:center;justify-content:center;
        font-size:20px;
      ">{icon}</div>
      <div>
        <div style="font-size:15px;font-weight:600;
                    color:#F1F1F3;">{name}</div>
        <div style="font-size:12px;color:#9395A5;
                    margin-top:2px;">AgentForge</div>
      </div>
    </div>
    <!-- Status badge -->
    <span class="af-badge-green">Active</span>
  </div>
  <!-- Purpose -->
  <p style="font-size:13px;color:#9395A5;margin:0 0 16px;height: 48px;overflow:hidden;text-overflow:ellipsis;">
    {purpose}
  </p>
  <!-- Tool tags -->
  <div style="display:flex;gap:6px;flex-wrap:wrap;
              margin-bottom:16px;height: 28px;overflow:hidden;">
    {tool_tags_html}
  </div>
  <!-- Footer -->
  <div style="display:flex;justify-content:space-between;
              align-items:center;padding-top:12px;
              border-top:1px solid #2E3148;">
    <span style="font-size:12px;color:#5A5C6E;">
      Created: {last_used}
    </span>
    <div style="display: flex; gap: 8px;">
      <a href="?page=my_agents&delete={name}" target="_self" class="delete-link-btn">Delete</a>
      <a href="?page=agent_chat&agent={name}" target="_self" class="open-link-btn">Open →</a>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
