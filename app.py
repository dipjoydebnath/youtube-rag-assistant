import os
import streamlit as st
from ingest import get_youtube_transcript
from vector_store import create_vector_db
from rag_chain import answer_question, generate_summary, generate_quiz

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="YouTube RAG Assistant",
    page_icon="🎬",
    layout="wide"
)

# ---------------------------------------------------------
# Helper Function to Load External CSS
# ---------------------------------------------------------
def load_css(file_name: str):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load external stylesheet
load_css("style.css")

# ---------------------------------------------------------
# Header & Branding Section
# ---------------------------------------------------------
st.markdown('<p class="main-title">🎬 YouTube RAG Assistant</p>', unsafe_allow_html=True)
st.markdown("""
<div class="badge-container">
    <span class="badge">🇬🇧 English</span>
    <span class="badge">🇮🇳 Hindi</span>
    <span class="badge">🇧🇩 Bengali</span>
    <span class="badge">⚡ Groq Whisper + Qwen</span>
</div>
""", unsafe_allow_html=True)
st.markdown('<p class="sub-title">Extract insights, generate structured notes, and ask questions from YouTube videos in any supported language.</p>', unsafe_allow_html=True)

# Session State Initialization
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processed_url" not in st.session_state:
    st.session_state.processed_url = ""

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Video Control Center")
    st.markdown("---")
    youtube_url = st.text_input("YouTube Video Link:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("🚀 Process Video"):
        if youtube_url.strip():
            with st.spinner("⏳ Extracting audio/captions and processing vectors..."):
                transcript = get_youtube_transcript(youtube_url)
                
                if transcript.startswith("Error"):
                    st.error(transcript)
                else:
                    vector_db = create_vector_db(transcript)
                    st.session_state.vector_store = vector_db
                    st.session_state.processed_url = youtube_url
                    st.session_state.chat_history = []
                    st.success("✅ Video successfully indexed!")
        else:
            st.warning("Please enter a valid URL.")

# ---------------------------------------------------------
# Main Content Tabs
# ---------------------------------------------------------
if st.session_state.vector_store is not None:
    tab1, tab2, tab3 = st.tabs(["💬 Interactive Q&A", "📝 Executive Summary", "🧩 Practice Quiz"])

    # --- TAB 1: CHAT INTERFACE ---
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Ask Questions About the Video")
        
        # Display existing chat history
        for q, a in st.session_state.chat_history:
            st.markdown(f'<div class="user-bubble"><b>You:</b> {q}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="assistant-bubble"><b>Assistant:</b><br>{a}</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)
        
        # User input
        user_query = st.chat_input("Ask a question in English...")
        if user_query:
            answer = answer_question(st.session_state.vector_store, user_query)
            st.session_state.chat_history.append((user_query, answer))
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 2: SUMMARY ---
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Detailed Video Summary")
        if st.button("Generate Summary"):
            with st.spinner("Creating summary..."):
                summary_text = generate_summary(st.session_state.vector_store)
                st.markdown(summary_text)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 3: QUIZ ---
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🧩 Generated Quiz")
        if st.button("Generate Quiz"):
            with st.spinner("Generating MCQs..."):
                quiz_text = generate_quiz(st.session_state.vector_store)
                st.markdown(quiz_text)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # Empty State Display
    st.info("👈 Paste a YouTube URL in the sidebar and click **Process Video** to get started!")