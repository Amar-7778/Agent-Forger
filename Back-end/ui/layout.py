import streamlit as st
import sys
import os

# Ensure storage can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage.agent_registry import list_agents

THEMES = {
    "cyberpunk": {
        "bg": "#0F1117",
        "sidebar_bg": "#1A1D27",
        "card_bg": "#1A1D27",
        "input_bg": "#222536",
        "border": "#2E3148",
        "highlight": "#F97316",
        "highlight_hover": "#EA6A0A",
        "text": "#F1F1F3",
        "muted_text": "#9395A5",
        "subtle_text": "#5A5C6E"
    },
    "space": {
        "bg": "#0A0E17",
        "sidebar_bg": "#101626",
        "card_bg": "#101626",
        "input_bg": "#172036",
        "border": "#1E293B",
        "highlight": "#10B981",
        "highlight_hover": "#059669",
        "text": "#F8FAFC",
        "muted_text": "#94A3B8",
        "subtle_text": "#64748B"
    },
    "nordic": {
        "bg": "#ECEFF4",
        "sidebar_bg": "#D8DEE9",
        "card_bg": "#E5E9F0",
        "input_bg": "#ECEFF4",
        "border": "#D8DEE9",
        "highlight": "#5E81AC",
        "highlight_hover": "#81A1C1",
        "text": "#2E3440",
        "muted_text": "#4C566A",
        "subtle_text": "#9096A2"
    }
}

def inject_global_css():
    theme_name = st.session_state.get("theme", "cyberpunk")
    t = THEMES.get(theme_name, THEMES["cyberpunk"])
    
    is_light = (theme_name == "nordic")
    text_color_main = t["text"]
    bg_color_main = t["bg"]
    
    css = f"""
<style>
:root {{
  --bg: {t["bg"]};
  --sidebar-bg: {t["sidebar_bg"]};
  --card-bg: {t["card_bg"]};
  --input-bg: {t["input_bg"]};
  --border: {t["border"]};
  --highlight: {t["highlight"]};
  --highlight-hover: {t["highlight_hover"]};
  --text: {t["text"]};
  --muted-text: {t["muted_text"]};
  --subtle-text: {t["subtle_text"]};
}}

/* ── Reset and base ── */
* {{ box-sizing: border-box; }}
html, body, [data-testid="stAppViewContainer"] {{
  background: {bg_color_main} !important;
  color: {text_color_main} !important;
  font-family: Inter, -apple-system, sans-serif;
}}
a {{
  text-decoration: none !important;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {{ display: none !important; }}

/* ── Remove default padding ── */
.block-container {{
  padding: 0 !important;
  max-width: 100% !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
  background: {t["sidebar_bg"]} !important;
  border-right: 1px solid {t["border"]} !important;
  padding: 0 !important;
}}
[data-testid="stSidebar"] > div {{
  padding: 24px 16px !important;
}}
[data-testid="stSidebarNav"] {{
  display: none !important;
}}

/* ── Cards ── */
.af-card {{
  background: {t["card_bg"]};
  border: 1px solid {t["border"]};
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
}}
.af-card:hover {{
  border-color: {t["highlight"]}40;
  box-shadow: 0 4px 24px {t["highlight"]}08;
}}

/* ── Buttons ── */
.stButton > button {{
  background: {t["highlight"]} !important;
  color: {"#FFFFFF" if is_light else "#0F1117"} !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  padding: 10px 20px !important;
  transition: background 0.2s, transform 0.1s !important;
  letter-spacing: 0.01em !important;
  width: auto !important;
}}
.stButton > button:hover {{
  background: {t["highlight_hover"]} !important;
  transform: translateY(-1px) !important;
}}
.stButton > button:active {{
  transform: translateY(0) !important;
}}

/* ── Secondary button ── */
.af-btn-secondary > button {{
  background: {t["input_bg"]} !important;
  color: {t["text"]} !important;
  border: 1px solid {t["border"]} !important;
}}
.af-btn-secondary > button:hover {{
  border-color: {t["highlight"]} !important;
  color: {t["highlight"]} !important;
}}

/* ── Input fields ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {{
  background: {t["input_bg"]} !important;
  border: 1px solid {t["border"]} !important;
  border-radius: 8px !important;
  color: {t["text"]} !important;
  font-size: 14px !important;
  padding: 10px 14px !important;
  transition: border-color 0.2s !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
  border-color: {t["highlight"]} !important;
  box-shadow: 0 0 0 3px {t["highlight"]}12 !important;
  outline: none !important;
}}
input::placeholder, textarea::placeholder {{
  color: {t["subtle_text"]} !important;
}}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {{
  background: transparent !important;
  border: none !important;
  padding: 8px 0 !important;
}}
[data-testid="stChatMessage"][data-testid*="user"] {{
  background: {t["input_bg"]} !important;
  color: {t["text"]} !important;
  border-radius: 12px 12px 2px 12px !important;
  padding: 12px 16px !important;
  margin-left: auto !important;
  max-width: 80% !important;
}}
[data-testid="stChatMessage"][data-testid*="assistant"] {{
  background: transparent !important;
  color: {t["text"]} !important;
  border-left: 3px solid {t["highlight"]} !important;
  padding-left: 16px !important;
  border-radius: 0 !important;
  margin-right: auto !important;
  max-width: 80% !important;
}}

/* ── Chat input ── */
[data-testid="stChatInput"] {{
  background: {t["card_bg"]} !important;
  border: 1px solid {t["border"]} !important;
  border-radius: 12px !important;
  padding: 4px !important;
}}
[data-testid="stChatInput"]:focus-within {{
  border-color: {t["highlight"]} !important;
  box-shadow: 0 0 0 3px {t["highlight"]}10 !important;
}}

/* ── Dividers ── */
hr {{
  border: none !important;
  border-top: 1px solid {t["border"]} !important;
  margin: 24px 0 !important;
}}

/* ── Metric cards ── */
[data-testid="stMetric"] {{
  background: {t["card_bg"]} !important;
  border: 1px solid {t["border"]} !important;
  border-radius: 12px !important;
  padding: 20px !important;
}}
[data-testid="stMetricValue"] {{
  color: {t["highlight"]} !important;
  font-size: 28px !important;
  font-weight: 700 !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  background: transparent !important;
  border-bottom: 1px solid {t["border"]} !important;
  gap: 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important;
  color: {t["muted_text"]} !important;
  border-bottom: 2px solid transparent !important;
  padding: 12px 20px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
}}
.stTabs [aria-selected="true"] {{
  color: {t["highlight"]} !important;
  border-bottom-color: {t["highlight"]} !important;
}}

/* ── Badges and tags ── */
.af-badge {{
  display: inline-block;
  background: {t["highlight"]}20;
  color: {t["highlight"]};
  border: 1px solid {t["highlight"]}40;
  border-radius: 24px;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}}
.af-badge-green {{
  display: inline-block;
  background: #22C55E20;
  color: #22C55E;
  border: 1px solid #22C55E40;
  border-radius: 24px;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}}
.af-badge-gray {{
  display: inline-block;
  background: {t["muted_text"]}20;
  color: {t["muted_text"]};
  border: 1px solid {t["muted_text"]}40;
  border-radius: 24px;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
  background: {t["border"]};
  border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{ background: {t["highlight"]}; }}

/* ── Alerts ── */
.stAlert {{
  border-radius: 8px !important;
  border: none !important;
  font-size: 14px !important;
}}

/* ── Custom sidebar styling ── */
.sidebar-section-label {{
  font-size: 11px;
  font-weight: 600;
  color: {t["subtle_text"]};
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-top: 16px;
  margin-bottom: 12px;
  padding-left: 12px;
}}

.sidebar-item {{
  display: block;
  padding: 10px 12px;
  border-radius: 8px;
  color: {t["muted_text"]};
  text-decoration: none !important;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  transition: background 0.15s, color 0.15s;
  border-left: 3px solid transparent;
}}
.sidebar-item:hover {{
  background: {t["input_bg"]};
  color: {t["text"]};
}}
.sidebar-item.active {{
  background: {t["highlight"]}15;
  color: {t["highlight"]};
  border-left: 3px solid {t["highlight"]};
  font-weight: 600;
}}

.sidebar-item-agent {{
  display: block;
  padding: 10px 12px;
  border-radius: 8px;
  color: {t["muted_text"]};
  text-decoration: none !important;
  margin-bottom: 6px;
  transition: background 0.15s, color 0.15s;
  border-left: 3px solid transparent;
}}
.sidebar-item-agent:hover {{
  background: {t["input_bg"]};
}}
.sidebar-item-agent.active {{
  background: {t["highlight"]}15;
  border-left: 3px solid {t["highlight"]};
}}

.status-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}}
.status-dot.active {{
  background-color: #22C55E;
  box-shadow: 0 0 8px #22C55E;
  animation: pulse-dot 2s infinite;
}}
.status-dot.inactive {{
  background-color: {t["muted_text"]};
}}

@keyframes pulse-dot {{
  0% {{ transform: scale(1); opacity: 1; }}
  50% {{ transform: scale(1.3); opacity: 0.5; }}
  100% {{ transform: scale(1); opacity: 1; }}
}}

.quick-pill {{
  background: {t["input_bg"]};
  border: 1px solid {t["border"]};
  border-radius: 24px;
  padding: 8px 16px;
  font-size: 13px;
  color: {t["muted_text"]};
  text-decoration: none !important;
  display: inline-block;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}}
.quick-pill:hover {{
  border-color: {t["highlight"]};
  color: {t["highlight"]};
}}

/* Typing indicator pulsing dots */
.typing-indicator-container {{
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}}
.typing-dots {{
  display: flex;
  gap: 6px;
  margin-bottom: 6px;
}}
.typing-dot {{
  width: 8px;
  height: 8px;
  background-color: {t["highlight"]};
  border-radius: 50%;
  animation: typing-pulse 1.4s infinite ease-in-out both;
}}
.typing-dot:nth-child(1) {{ animation-delay: -0.32s; }}
.typing-dot:nth-child(2) {{ animation-delay: -0.16s; }}
@keyframes typing-pulse {{
  0%, 80%, 100% {{ transform: scale(0.6); opacity: 0.4; }}
  40% {{ transform: scale(1.2); opacity: 1; }}
}}

/* Page loading bar */
.loader-bar-container {{
  width: 100%;
  background-color: {t["border"]};
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 8px;
}}
.loader-bar {{
  background-color: {t["highlight"]};
  height: 100%;
  width: 40%;
  border-radius: 2px;
  animation: progress-pulse 1.5s infinite linear;
}}
@keyframes progress-pulse {{
  0% {{ transform: translateX(-100%); }}
  100% {{ transform: translateX(250%); }}
}}

/* Main app view container adjustment to handle padding */
.main-content-area {{
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
}}

/* General heading and text styling overrides for Streamlit components */
h1, h2, h3, h4, h5, h6, [data-testid="stHeader"] {{
  color: {t["text"]} !important;
}}
div[data-testid="stMarkdownContainer"] p {{
  color: {t["muted_text"]} !important;
}}
span[data-testid="stHeader"] {{
  color: {t["text"]} !important;
}}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)

def render_top_navbar():
    st.markdown("""
<div style="
  background: #1A1D27;
  border-bottom: 1px solid #2E3148;
  padding: 0 32px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 999;
  margin-bottom: 0px;
">
  <!-- Logo -->
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="
      width: 32px; height: 32px;
      background: #F97316;
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 16px; font-weight: 800; color: #0F1117;
    ">A</div>
    <span style="
      font-size: 18px; font-weight: 700;
      color: #F1F1F3; letter-spacing: -0.02em;
    ">AgentForge</span>
    <span style="
      font-size: 10px; font-weight: 600;
      background: #F9731620; color: #F97316;
      border: 1px solid #F9731640;
      border-radius: 4px; padding: 2px 6px;
      letter-spacing: 0.06em; text-transform: uppercase;
    ">BETA</span>
  </div>
  <!-- Nav links -->
  <div style="display:flex;align-items:center;gap:32px;">
    <a href="?page=dashboard" target="_self" style="color:#9395A5;font-size:14px;font-weight:500;
              text-decoration:none;cursor:pointer;">Dashboard</a>
    <a href="?page=my_agents" target="_self" style="color:#9395A5;font-size:14px;font-weight:500;
              text-decoration:none;cursor:pointer;">My Agents</a>
    <a href="?page=schedules" target="_self" style="color:#9395A5;font-size:14px;font-weight:500;
              text-decoration:none;cursor:pointer;">Schedules</a>
    <a href="?page=settings" target="_self" style="color:#9395A5;font-size:14px;font-weight:500;
              text-decoration:none;cursor:pointer;">Settings</a>
  </div>
  <!-- User pill -->
  <div style="
    display:flex;align-items:center;gap:8px;
    background:#222536; border:1px solid #2E3148;
    border-radius:24px; padding:6px 14px 6px 8px;
  ">
    <div style="
      width:26px;height:26px;border-radius:50%;
      background:#F97316;
      display:flex;align-items:center;justify-content:center;
      font-size:11px;font-weight:700;color:#0F1117;
    ">U</div>
    <span style="font-size:13px;font-weight:500;color:#F1F1F3;">
      User
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

def render_sidebar(active_page: str, active_agent_name: str = None):
    # Sidebar items builder
    workspace_items = [
        {"icon": "🏠", "label": "Dashboard", "id": "dashboard"},
        {"icon": "🤖", "label": "My Agents", "id": "my_agents"},
        {"icon": "⏰", "label": "Scheduled Tasks", "id": "schedules"},
        {"icon": "💬", "label": "Chat History", "id": "master_agent"},
    ]
    
    workspace_html = ""
    for item in workspace_items:
        is_active = active_page == item["id"]
        active_class = "active" if is_active else ""
        workspace_html += f'<a href="?page={item["id"]}" target="_self" class="sidebar-item {active_class}">{item["icon"]} {item["label"]}</a>\n'
    
    # Custom agents list
    agents = list_agents()
    agents_html = ""
    if agents:
        for agent in agents:
            is_active = (active_page == "agent_chat" and active_agent_name == agent["name"])
            active_class = "active" if is_active else ""
            active_color_name = "#F97316" if is_active else "#F1F1F3"
            
            # Use defaults
            icon = agent.get("icon", "🤖")
            name = agent["name"]
            purpose = agent.get("description", "Custom AI agent")
            status_dot_class = "active" # Set custom agents as active (green pulsing)
            
            agents_html += f"""
<a href="?page=agent_chat&agent={name}" target="_self" class="sidebar-item-agent {active_class}">
  <div style="display: flex; align-items: center; justify-content: space-between;">
    <div style="display: flex; align-items: center; gap: 8px;">
      <span style="font-size: 16px;">{icon}</span>
      <div style="min-width: 0;">
        <div style="font-weight: 600; font-size: 13px; color: {active_color_name}; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; max-width: 140px;">{name}</div>
        <div style="font-size: 11px; color: #5A5C6E; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px;">{purpose}</div>
      </div>
    </div>
    <span class="status-dot {status_dot_class}"></span>
  </div>
</a>
"""
    else:
        agents_html = '<p style="font-size: 12px; color: #5A5C6E; padding-left: 12px; margin: 0;">No active agents. Create one in the Builder.</p>'
        
    bottom_items = [
        {"icon": "⚙️", "label": "Settings", "id": "settings"},
        {"icon": "📚", "label": "Knowledge Base", "id": "knowledge_base"},
        {"icon": "❓", "label": "Help", "id": "help"}
    ]
    bottom_html = ""
    for item in bottom_items:
        is_active = active_page == item["id"]
        active_class = "active" if is_active else ""
        bottom_html += f'<a href="?page={item["id"]}" target="_self" class="sidebar-item {active_class}">{item["icon"]} {item["label"]}</a>\n'

    # Render all sections inside st.sidebar
    with st.sidebar:
        # Title of sidebar section 1
        st.markdown('<div class="sidebar-section-label">Workspace</div>', unsafe_allow_html=True)
        st.markdown(workspace_html, unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Section 2
        st.markdown('<div class="sidebar-section-label">Your Agents</div>', unsafe_allow_html=True)
        st.markdown(agents_html, unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Section 3 (bottom items)
        st.markdown(bottom_html, unsafe_allow_html=True)

# Typography helpers
def page_heading(title: str):
    st.markdown(f"""
<h1 style="font-size:28px;font-weight:700;color: var(--text);
           margin:0 0 4px;letter-spacing:-0.02em;">
  {title}
</h1>
""", unsafe_allow_html=True)

def section_heading(title: str):
    st.markdown(f"""
<h2 style="font-size:16px;font-weight:600;color: var(--text);
           margin:0 0 16px;">
  {title}
</h2>
""", unsafe_allow_html=True)

def section_label(label: str):
    st.markdown(f"""
<p style="font-size:11px;font-weight:600;color: var(--subtle-text);
          letter-spacing:0.08em;text-transform:uppercase;
          margin:0 0 12px;">
  {label}
</p>
""", unsafe_allow_html=True)

def muted_body_text(text: str):
    st.markdown(f"""
<p style="font-size:14px;color: var(--muted-text);
          line-height:1.6;margin:0;">
  {text}
</p>
""", unsafe_allow_html=True)

def amber_highlight(text: str) -> str:
    return f'<span style="color: var(--highlight);font-weight:600;">{text}</span>'

# Render tools badge
def render_tool_badge(tool_name: str) -> str:
    return f'<span class="af-badge">{tool_name}</span>'

def render_active_badge(label: str = "Active") -> str:
    return f'<span class="af-badge-green">{label}</span>'

def render_gray_badge(label: str) -> str:
    return f'<span class="af-badge-gray">{label}</span>'

# Loading animations
def render_typing_indicator():
    st.markdown("""
<div class="typing-indicator-container">
  <div class="typing-dots">
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  </div>
  <div style="font-size: 13px; color: #9395A5;">AgentForge is thinking...</div>
</div>
""", unsafe_allow_html=True)

def render_tool_loader(tool_name: str):
    st.markdown(f"""
<div class="loader-bar-container">
  <div class="loader-bar"></div>
</div>
<div style="font-size: 12px; color: #9395A5; margin-bottom: 12px;">Calling: {tool_name}...</div>
""", unsafe_allow_html=True)
