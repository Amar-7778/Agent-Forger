import streamlit as st
import os
import sys
import textwrap
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# Streamlit Page Config - must be at the very top
st.set_page_config(
    page_title="AgentForge Enterprise OS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import UI components
from ui.layout import inject_global_css, render_top_navbar, render_sidebar, page_heading, muted_body_text
from ui.views.dashboard import show_dashboard
from ui.views.agent_chat import show_agent_chat
from ui.views.my_agents import show_my_agents
from ui.views.scheduled_agents import show_scheduled_agents
from ui.views.agent_builder import show_agent_builder
from ui.views.knowledge_base import show_knowledge_base
from ui.views.settings import show_settings
from ui.views.master_agent import show_master_agent

def show_help():
    page_heading("❓ Help & Documentation")
    muted_body_text("Get assistance and find answers about using the AgentForge platform.")
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("""<div class="af-card" style="margin-bottom: 0;">
<h3 style="font-size: 16px; font-weight: 600; color: #F1F1F3; margin-top: 0; margin-bottom: 12px;">Frequently Asked Questions</h3>
<div style="margin-bottom: 16px;">
<div style="font-size: 14px; font-weight: 600; color: #F97316;">How do I create a custom agent?</div>
<div style="font-size: 13px; color: #9395A5; margin-top: 4px; line-height: 1.5;">
Go to the <b>Agent Builder</b> page using the link in the sidebar or navbar. Enter the agent name, icon emoji, operational scope, restrictions, and select tools (e.g., RAG, Search). Once saved, the agent will appear in the "Your Agents" list in the sidebar.
</div>
</div>
<div style="margin-bottom: 16px;">
<div style="font-size: 14px; font-weight: 600; color: #F97316;">How does RAG (Knowledge Base) work?</div>
<div style="font-size: 13px; color: #9395A5; margin-top: 4px; line-height: 1.5;">
Upload company files (PDF, DOCX, TXT, CSV) in the <b>Knowledge Base</b> page. Files are read, parsed, chunked, and embedded into a local vector storage. Any custom agent with the "RAG Knowledge Base" tool enabled will automatically check this context database when relevant queries are received.
</div>
</div>
<div style="margin-bottom: 16px;">
<div style="font-size: 14px; font-weight: 600; color: #F97316;">How do scheduled tasks execute?</div>
<div style="font-size: 13px; color: #9395A5; margin-top: 4px; line-height: 1.5;">
Scheduled agents run workflows in the background at specified intervals (in minutes) or via standard Cron triggers. You can monitor, pause, or resume task schedules from the <b>Scheduled Tasks</b> tab.
</div>
</div>
</div>""", unsafe_allow_html=True)

# 1. Inject styling
inject_global_css()

# 2. Render Top Navigation Bar
render_top_navbar()

# 3. Parse query params to determine routing page
page = st.query_params.get("page", "dashboard")
agent_param = st.query_params.get("agent", None)

# 4. Render Sidebar
render_sidebar(active_page=page, active_agent_name=agent_param)

# 5. Render active view in main content area
st.markdown('<div class="main-content-area">', unsafe_allow_html=True)

if page == "dashboard":
    show_dashboard()
elif page == "agent_chat" and agent_param:
    show_agent_chat(agent_param)
elif page == "my_agents":
    show_my_agents()
elif page == "schedules":
    show_scheduled_agents()
elif page == "agent_builder":
    show_agent_builder()
elif page == "knowledge_base":
    show_knowledge_base()
elif page == "settings":
    show_settings()
elif page == "master_agent":
    show_master_agent()
elif page == "help":
    show_help()
else:
    # Fallback
    show_dashboard()

st.markdown('</div>', unsafe_allow_html=True)
