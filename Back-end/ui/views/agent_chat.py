import streamlit as st
import datetime
import sys
import os

# Adjust paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from storage.agent_registry import get_agent
from storage.history_store import get_history, add_message
from tools.rag_tool import query_knowledge_base
from brain.llm_factory import get_llm
from ui.layout import (
    render_typing_indicator, render_tool_loader, render_active_badge,
    render_gray_badge, render_tool_badge
)

def show_agent_chat(agent_name: str):
    agent = get_agent(agent_name)
    if not agent:
        st.error("Agent not found.")
        st.markdown('<a href="?page=dashboard" target="_self" class="stButton">Go back to Dashboard</a>', unsafe_allow_html=True)
        return

    icon = agent.get("icon", "🤖")
    desc = agent.get("description", "")
    scope = agent.get("scope", "General purpose")
    restrictions = agent.get("restrictions", "None")
    tools = agent.get("tools", [])
    created_at = agent.get("created_at", datetime.datetime.now().strftime("%Y-%m-%d"))
    if " " in created_at:
        created_at = created_at.split(" ")[0]

    # --- TOP BAR ---
    st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2E3148; padding-bottom: 16px; margin-bottom: 16px;">
  <div style="display: flex; align-items: center; gap: 12px;">
    <a href="?page=dashboard" target="_self" style="color: #9395A5; font-size: 14px; text-decoration: none; display: flex; align-items: center; gap: 4px;">
      ← Back to Dashboard
    </a>
    <span style="color: #2E3148;">|</span>
    <span style="font-size: 18px; font-weight: 700; color: #F1F1F3;">{icon} {agent_name}</span>
  </div>
  <span class="af-badge-green">Active</span>
</div>
""", unsafe_allow_html=True)

    # --- AGENT INFO STRIP ---
    tools_badges = " ".join([render_tool_badge(t) for t in tools]) if tools else render_gray_badge("No Tools")
    st.markdown(f"""
<div class="af-card" style="padding: 16px; margin-bottom: 16px;">
  <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
    <div>
      <div style="font-size: 12px; color: #5A5C6E; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Purpose</div>
      <div style="font-size: 14px; color: #9395A5; margin-top: 2px;">{desc}</div>
    </div>
    <div>
      <div style="font-size: 12px; color: #5A5C6E; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Scope & restrictions</div>
      <div style="font-size: 13px; color: #9395A5; margin-top: 2px;"><b>Scope:</b> {scope} | <b>Limit:</b> {restrictions}</div>
    </div>
    <div>
      <div style="font-size: 12px; color: #5A5C6E; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Enabled Tools</div>
      <div style="margin-top: 4px; display: flex; gap: 6px; flex-wrap: wrap;">{tools_badges}</div>
    </div>
    <div>
      <div style="font-size: 12px; color: #5A5C6E; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Created Date</div>
      <div style="font-size: 13px; color: #9395A5; margin-top: 2px;">{created_at}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # --- DYNAMIC QUICK ACTIONS ---
    # Create 5 context-relevant actions
    quick_actions = [
        f"Ask {agent_name} about its scope",
        f"How can {agent_name} help me?",
    ]
    if "RAG Knowledge Base" in tools:
        quick_actions.append("Search knowledge base")
    if "Web Search" in tools:
        quick_actions.append("Search the web for news")
    if "Slack Output" in tools:
        quick_actions.append("Draft message to Slack")
    if "Email Output" in tools:
        quick_actions.append("Draft email report")
        
    # Pad to 5 items
    default_actions = [
        "What are your restrictions?",
        "Create an execution plan",
        "Summarize active tools",
        "Perform a dry run"
    ]
    for action in default_actions:
        if len(quick_actions) >= 5:
            break
        if action not in quick_actions:
            quick_actions.append(action)

    # --- CHAT AREA ---
    session_id = f"agent_chat_{agent_name.replace(' ', '_').lower()}"
    history = get_history(session_id)
    
    chat_container = st.container(height=380, border=True)
    with chat_container:
        if not history:
            st.markdown(f"""
            <div style="padding: 24px; text-align: center;">
              <span style="font-size: 40px; color: #2E3148;">🤖</span>
              <div style="font-weight: 600; color: #9395A5; font-size: 15px; margin-top: 8px;">Conversation Started</div>
              <div style="font-size: 12px; color: #5A5C6E;">You are now speaking with {agent_name}.</div>
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

    # Handle quick action select or chat input
    incoming_prompt = st.query_params.get("prompt", None)
    if incoming_prompt:
        st.query_params.pop("prompt")
        prompt = incoming_prompt
    else:
        prompt = st.chat_input(f"Ask {agent_name}...")

    if prompt:
        add_message(session_id, "user", prompt)
        
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
                time_now = datetime.datetime.now().strftime("%H:%M")
                st.markdown(f'<div style="font-size: 10px; color: #5A5C6E; text-align: right; margin-top: 4px;">{time_now}</div>', unsafe_allow_html=True)

        # Agent processing
        with chat_container:
            # Simulate tools or trigger logic
            loader_placeholder = st.empty()
            typing_placeholder = st.empty()
            
            # 1. Decide if we call tools
            context = ""
            if "RAG Knowledge Base" in tools and ("search" in prompt.lower() or "knowledge" in prompt.lower() or "document" in prompt.lower() or "policy" in prompt.lower()):
                with loader_placeholder.container():
                    render_tool_loader("Checking your documents (RAG)")
                context = query_knowledge_base(prompt)
                loader_placeholder.empty()
            elif "Web Search" in tools and ("search" in prompt.lower() or "web" in prompt.lower() or "news" in prompt.lower() or "google" in prompt.lower()):
                with loader_placeholder.container():
                    render_tool_loader("Searching the web")
                import time
                time.sleep(1.2) # Elegant placeholder latency
                context = f"Simulated Web Search for: '{prompt}' found no relevant external changes."
                loader_placeholder.empty()
            elif len(tools) > 0 and ("send" in prompt.lower() or "output" in prompt.lower() or "slack" in prompt.lower() or "email" in prompt.lower()):
                active_tool = tools[0]
                with loader_placeholder.container():
                    render_tool_loader(f"Contacting {active_tool}")
                import time
                time.sleep(1.0)
                context = f"Simulated execution of tool: {active_tool} completed successfully."
                loader_placeholder.empty()

            # 2. Show thinking state
            with typing_placeholder.container():
                render_typing_indicator()
                
            # Build prompt
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
                
            typing_placeholder.empty()
            
        add_message(session_id, "assistant", response)
        st.rerun()

    # --- QUICK ACTIONS ROW ---
    st.markdown('<div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px;">', unsafe_allow_html=True)
    cols_html = ""
    for action in quick_actions:
        # Urlencode prompt query parameter
        import urllib.parse
        encoded_action = urllib.parse.quote_plus(action)
        cols_html += f'<a href="?page=agent_chat&agent={agent_name}&prompt={encoded_action}" target="_self" class="quick-pill">{action}</a>\n'
    st.markdown(cols_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
