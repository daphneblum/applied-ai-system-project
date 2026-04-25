"""
Streamlit UI for the RAG-based music recommender.

Run from the project root:
    streamlit run src/app.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import re
import streamlit as st
from rag_recommender import RAGRecommender

EXAMPLES = [
    "upbeat pop songs for a workout",
    "chill acoustic songs for late night studying",
    "dark intense metal for when I'm angry",
    "happy latin songs for a summer party",
]

st.set_page_config(page_title="✨ Music Recommender", page_icon="🎵", layout="centered")

st.html("""
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">

<style>
h1, h2, h3, h4, h5, h6,
p, li, label, input, textarea,
button, .stButton > button,
.stTextInput input,
.stMarkdown, .stMarkdown *,
.block-container, .block-container div,
.section-label, .pixel-card {
    font-family: 'Press Start 2P', monospace !important;
}

.block-container {
    padding-top: 2rem !important;
    max-width: 760px !important;
}

h1 {
    color: #8800bb !important;
    text-shadow: 2px 2px 0px #dd88ff, 4px 4px 0px #cc66ff !important;
}

h2, h3 {
    color: #6600aa !important;
    text-shadow: 1px 1px 0px #cc88ff !important;
}

.section-label {
    color: #7700aa !important;
}

.stTextInput input {
    background-color: #fff5ff !important;
    color: #330044 !important;
    border: 3px solid #aa44cc !important;
    box-shadow: 4px 4px 0px #cc88ff !important;
}

.stTextInput input::placeholder {
    color: #9966aa !important;
}

.pixel-card {
    background: rgba(255, 240, 255, 0.9) !important;
    border: 3px solid #aa44cc !important;
    box-shadow: 6px 6px 0px #cc88dd !important;
    color: #330044 !important;
    padding: 1rem;
}

.stButton > button {
    background: linear-gradient(180deg, #ffffff 0%, #f3c7ff 100%) !important;
    color: #440055 !important;
    border: 3px solid #aa44cc !important;
    border-radius: 0px !important;
    box-shadow: 4px 4px 0px #cc88ff !important;
}
        
.pixel-card strong {
    position: relative;
    display: inline-block;
    animation: magical-glow 2.8s ease-in-out infinite;
}

@keyframes magical-glow {
    0%, 100% {
        color: #aa22cc;
        text-shadow:
            0 0 2px #fff,
            0 0 6px #dd88ff,
            0 0 12px #cc66ff,
            0 0 20px #bb55dd;
    }
    50% {
        color: #cc44ff;
        text-shadow:
            0 0 4px #fff,
            0 0 10px #ffccff,
            0 0 18px #ee99ff,
            0 0 28px #dd77ff;
    }
}
.pixel-card strong::after {
    content: " ✦";
    position: absolute;
    right: -1.2em;
    top: 0;
    font-size: 0.7em;
    animation: sparkle-twinkle 1.8s ease-in-out infinite;
    color: #ff66dd;
}
</style>
""")

# ── Header ───────────────────────────────────────────────────────────────────

st.html('<div style="text-align:center; font-size:2.5rem; margin-bottom:0.25rem;">🎵</div>')
st.title("✨ Music Recommender ✨")
st.html('<p style="text-align:center; color:#cc88ff; font-family:\'Press Start 2P\',monospace; font-size:0.65rem;">describe the vibe. get the playlist.</p>')
st.markdown("---")

# ── Example queries ───────────────────────────────────────────────────────────

st.html('<span class="section-label">★ need inspiration? try these ★</span>')
cols = st.columns(2)
for i, example in enumerate(EXAMPLES):
    if cols[i % 2].button(example, key=f"ex_{i}"):
        st.session_state["query_input"] = example

st.markdown("---")

# ── Query input ───────────────────────────────────────────────────────────────

query = st.text_input(
    "what are you in the mood for?",
    key="query_input",
    placeholder="e.g. chill acoustic songs for late night studying",
)

if st.button("🎮  find my songs", type="primary", disabled=not query):
    try:
        recommender = RAGRecommender()
    except FileNotFoundError as e:
        st.error(
            f"**setup needed:** {e}\n\n"
            "run `python scripts/build_index.py` from the project root first."
        )
        st.stop()
    except KeyError:
        st.error("**missing api key:** set `GOOGLE_API_KEY` in your `.env` file.")
        st.stop()

    with st.spinner("✨ searching the cosmos..."):
        result = recommender.recommend(query)

    st.markdown("---")
    st.subheader("♪ your recommendations ♪")
    html_result = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', result)
    html_result = html_result.replace("\n", "<br>")
    st.markdown(f'<div class="pixel-card">{html_result}</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────

st.html("""
<div style="margin-top:3rem; text-align:center;
     color:#660099; font-family:'Press Start 2P',monospace; font-size:0.4rem;">
    powered by gemini ✦ chromadb ✦ sentence-transformers
</div>
""")