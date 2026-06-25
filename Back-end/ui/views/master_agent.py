import streamlit as st
import datetime
import uuid
import sys
import os

# Adjust paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from storage.history_store import get_history, add_message
from brain.router import route_request
from ui.layout import (
    page_heading, muted_body_text, render_typing_indicator, render_tool_loader
)

def show_master_agent():
    page_heading("💬 AgentForge Master Chat")
    muted_body_text("Interact with the core Operations Director AI and inspect full chat logs.")
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    session_id = st.session_state.setdefault("session_id", str(uuid.uuid4()))
    history = get_history(session_id)

    chat_container = st.container(height=480, border=True)
    
    with chat_container:
        if not history:
            st.markdown("""
            <div style="padding: 32px; text-align: center;">
              <span style="font-size: 40px; color: #2E3148;">💬</span>
              <div style="font-weight: 600; color: #9395A5; font-size: 15px; margin-top: 8px;">No chat logs yet</div>
              <div style="font-size: 12px; color: #5A5C6E;">Send a query from the Dashboard or type below to start.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in history:
                role = msg['role']
                timestamp = msg.get('timestamp', '')
                try:
                    time_part = timestamp.split(" ")[1][:5] if timestamp else datetime.datetime.now().strftime("%H:%M")
                except Exception:
                    time_part = timestamp[:5]
                    
                with st.chat_message(role):
                    st.write(msg['content'])
                    st.markdown(f'<div style="font-size: 10px; color: #5A5C6E; text-align: right; margin-top: 4px;">{time_part}</div>', unsafe_allow_html=True)

    prompt_placeholder = "Ask the Operations Director anything..."
    
    # Check if there is an incoming prompt from query parameters
    incoming_prompt = st.query_params.get("prompt", None)
    if incoming_prompt:
        st.query_params.pop("prompt")
        prompt = incoming_prompt
    else:
        prompt = st.chat_input(prompt_placeholder)
        
    if prompt:
        add_message(session_id, "user", prompt)
        
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
                time_now = datetime.datetime.now().strftime("%H:%M")
                st.markdown(f'<div style="font-size: 10px; color: #5A5C6E; text-align: right; margin-top: 4px;">{time_now}</div>', unsafe_allow_html=True)

        with chat_container:
            loader_placeholder = st.empty()
            typing_placeholder = st.empty()
            with loader_placeholder.container():
                render_tool_loader("AgentForge Router")
            with typing_placeholder.container():
                render_typing_indicator()
            
            try:
                response = route_request(prompt)
            except Exception as e:
                response = f"Sorry, I encountered an error: {e}"
                
            loader_placeholder.empty()
            typing_placeholder.empty()
            
        add_message(session_id, "assistant", response)
        st.rerun()
