import streamlit as st
import os
import sys

# Adjust paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from ui.layout import page_heading, muted_body_text, section_heading
from storage.agent_registry import (
    list_agents, delete_agent, 
    list_scheduled_agents, delete_scheduled_agent
)

def show_settings():
    page_heading("⚙️ Platform Settings")
    muted_body_text("Configure your interface theme preferences and manage registered workspace agents.")
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # --- THEME SELECTION ---
    with st.container(border=True):
        st.markdown('<div class="af-card" style="margin-bottom: 0;">', unsafe_allow_html=True)
        section_heading("🎨 User Interface Theme")
        
        current_theme = st.session_state.get("theme", "cyberpunk")
        
        theme_options = {
            "cyberpunk": "Cyberpunk Dark (Default)",
            "space": "Deep Space Blue",
            "nordic": "Nordic Light"
        }
        
        selected_theme_name = st.selectbox(
            "Select active interface theme:",
            options=list(theme_options.keys()),
            format_func=lambda x: theme_options[x],
            index=list(theme_options.keys()).index(current_theme)
        )
        
        if selected_theme_name != current_theme:
            st.session_state["theme"] = selected_theme_name
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # --- AGENT MANAGEMENT ---
    with st.container(border=True):
        st.markdown('<div class="af-card" style="margin-bottom: 0;">', unsafe_allow_html=True)
        section_heading("🤖 Registered Agents")
        
        agents = list_agents()
        if not agents:
            st.markdown('<div style="font-size:13px; color: var(--muted-text);">No custom agents registered yet. Create agents in the builder.</div>', unsafe_allow_html=True)
        else:
            for agent in agents:
                name = agent["name"]
                icon = agent.get("icon", "🤖")
                desc = agent.get("description", "Custom AI agent")
                
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{icon} {name}** — *{desc}*")
                with col2:
                    if st.button("Delete", key=f"del_agent_{name}", use_container_width=True):
                        delete_agent(name)
                        st.success(f"Agent '{name}' deleted successfully!")
                        st.rerun()
                st.markdown("<hr style='margin: 8px 0 !important;'>", unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # --- SCHEDULED TASKS MANAGEMENT ---
    with st.container(border=True):
        st.markdown('<div class="af-card" style="margin-bottom: 0;">', unsafe_allow_html=True)
        section_heading("⏰ Scheduled Automation Tasks")
        
        scheduled_agents = list_scheduled_agents()
        if not scheduled_agents:
            st.markdown('<div style="font-size:13px; color: var(--muted-text);">No scheduled automation tasks registered yet.</div>', unsafe_allow_html=True)
        else:
            for sa in scheduled_agents:
                name = sa["name"]
                task = sa["task"]
                dest = sa["destination"]
                
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{name}** — Run *{task}* -> Output to *{dest}*")
                with col2:
                    if st.button("Delete", key=f"del_sa_{name}", use_container_width=True):
                        delete_scheduled_agent(name)
                        st.success(f"Scheduled task '{name}' deleted successfully!")
                        st.rerun()
                st.markdown("<hr style='margin: 8px 0 !important;'>", unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)
