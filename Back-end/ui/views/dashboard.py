import streamlit as st
import datetime
import uuid
import sys
import os

# Adjust paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from storage.agent_registry import list_agents, list_scheduled_agents
from storage.history_store import get_history, add_message
from brain.router import route_request
from ui.layout import (
    page_heading, muted_body_text, render_typing_indicator, render_tool_loader
)

def show_dashboard():
    # --- ROW 1: Page Header ---
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good morning 👋"
    elif hour < 17:
        greeting = "Good afternoon 👋"
    else:
        greeting = "Good evening 👋"
        
    page_heading(greeting)
    muted_body_text("What would you like to automate today?")
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    
    # --- ROW 2: Metric Cards ---
    custom_agents = list_agents()
    scheduled_agents = list_scheduled_agents()
    
    total_agents = len(custom_agents)
    active_schedules = len([a for a in scheduled_agents if a.get('status') == 'active'])
    
    # Let's count messages today
    session_id = st.session_state.setdefault("session_id", str(uuid.uuid4()))
    history = get_history(session_id)
    messages_today = len(history) # Default to history length
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Agents Created", total_agents)
    with col2:
        st.metric("Active Schedules", active_schedules)
    with col3:
        st.metric("Tasks Completed", 42) # Premium enterprise mock figure
    with col4:
        st.metric("Messages Today", messages_today)
        
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    
    # --- ROW 3: Main Chat Interface ---
    st.markdown("""
<div class="af-card" style="margin-bottom: 8px; padding-bottom: 12px;">
    <div style="font-size:16px;font-weight:600;color:#F1F1F3;">AgentForge Assistant</div>
    <div style="font-size:13px;color:#9395A5;margin-bottom:12px;">Ask me anything or say 'build me an agent'</div>
</div>
""", unsafe_allow_html=True)

    # Chat history container
    # Initialize message list
    chat_container = st.container(height=400, border=True)
    
    # Render existing messages
    with chat_container:
        for msg in history:
            role = msg['role']
            timestamp = msg.get('timestamp', '')
            if timestamp:
                # Truncate timestamp if it has date/time details
                try:
                    time_part = timestamp.split(" ")[1][:5]
                except Exception:
                    time_part = timestamp[:5]
            else:
                time_part = datetime.datetime.now().strftime("%H:%M")
                
            with st.chat_message(role):
                st.write(msg['content'])
                st.markdown(f'<div style="font-size: 10px; color: #5A5C6E; text-align: right; margin-top: 4px;">{time_part}</div>', unsafe_allow_html=True)

    # Handle quick action or input
    prompt_placeholder = "Ask a question, automate a task, or build an agent..."
    
    # Check if there is an incoming prompt from query parameters (pills or sidebar redirect)
    incoming_prompt = st.query_params.get("prompt", None)
    if incoming_prompt:
        st.query_params.pop("prompt") # Clear parameter
        prompt = incoming_prompt
    else:
        prompt = st.chat_input(prompt_placeholder)
        
    if prompt:
        # User message
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
                time_now = datetime.datetime.now().strftime("%H:%M")
                st.markdown(f'<div style="font-size: 10px; color: #5A5C6E; text-align: right; margin-top: 4px;">{time_now}</div>', unsafe_allow_html=True)
                
        add_message(session_id, "user", prompt)
        
        # Assistant response
        with chat_container:
            # Show loader
            loader_placeholder = st.empty()
            typing_placeholder = st.empty()
            with loader_placeholder.container():
                render_tool_loader("AgentForge Router")
            with typing_placeholder.container():
                render_typing_indicator()
            
            # Run router
            try:
                response = route_request(prompt)
            except Exception as e:
                response = f"Sorry, I encountered an error: {e}"
                
            # Clear indicators
            loader_placeholder.empty()
            typing_placeholder.empty()
            
        add_message(session_id, "assistant", response)
        st.rerun()

    # --- ROW 4: Quick Action Buttons ---
    st.markdown("""
<div style="display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px;">
  <a href="?page=agent_builder" target="_self" class="quick-pill">🤖 Build an agent</a>
  <a href="?page=knowledge_base" target="_self" class="quick-pill">🔍 Search company docs</a>
  <a href="?page=schedules" target="_self" class="quick-pill">⏰ Schedule a task</a>
  <a href="?page=my_agents" target="_self" class="quick-pill">📊 Analyze data</a>
  <a href="?page=master_agent&prompt=Search+the+web" target="_self" class="quick-pill">🌐 Search the web</a>
</div>
""", unsafe_allow_html=True)
