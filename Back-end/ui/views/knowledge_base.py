import streamlit as st
import sys
import os

# Adjust paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.rag_tool import ingest_document
from ui.layout import page_heading, muted_body_text

def show_knowledge_base():
    page_heading("📚 Knowledge Base")
    muted_body_text("Upload company documents (PDF, DOCX, TXT, CSV) to the RAG system to enable knowledge-aware agents.")
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="af-card" style="margin-bottom: 0;">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-size:16px;font-weight:600;color:#F1F1F3;margin-top:0;margin-bottom:12px;">Ingest Documents</h3>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True, type=['pdf', 'docx', 'txt', 'csv'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Ingest Documents", use_container_width=True):
            if uploaded_files:
                # Use custom progress loader
                progress_placeholder = st.empty()
                with progress_placeholder.container():
                    st.markdown("""
                    <div class="loader-bar-container">
                      <div class="loader-bar"></div>
                    </div>
                    <div style="font-size: 13px; color: #9395A5; margin-bottom: 12px;">Processing and chunking files...</div>
                    """, unsafe_allow_html=True)
                    
                for file in uploaded_files:
                    bytes_data = file.read()
                    success, msg = ingest_document(file.name, bytes_data)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                        
                progress_placeholder.empty()
            else:
                st.warning("Please upload at least one file.")
                
        st.markdown('</div>', unsafe_allow_html=True)
