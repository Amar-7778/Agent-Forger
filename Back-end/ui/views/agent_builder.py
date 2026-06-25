import streamlit as st
import sys
import os

# Adjust paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.agent_builder import create_custom_agent
from ui.layout import page_heading, muted_body_text

def show_agent_builder():
    page_heading("🏗️ Agent Builder")
    muted_body_text("Design and instantiate a specialized AI agent for your business operations.")
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        with st.form("agent_builder_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Agent Name", placeholder="e.g. Sales Assistant")
                scope = st.text_input("Scope", placeholder="e.g. Internal sales data only")
                theme = st.selectbox("Theme", ["dark", "light", "blue"])
            with col2:
                icon = st.text_input("Icon Emoji", value="🤖")
                restrictions = st.text_input("Restrictions", placeholder="e.g. Cannot send emails")
                tools = st.multiselect("Tools Needed", ["RAG Knowledge Base", "Web Search", "Slack Output", "Email Output"])
            
            description = st.text_area("Description", placeholder="What exactly does this agent do?", height=120)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("✨ Create Agent", use_container_width=True)
            
            if submitted:
                if name and description:
                    create_custom_agent(name, description, scope, restrictions, tools, theme, icon)
                    st.success(f"Agent '{name}' created successfully! Access it under 'Your Agents' in the sidebar.")
                    st.rerun()
                else:
                    st.error("Name and Description are required.")
