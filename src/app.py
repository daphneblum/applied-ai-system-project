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
/* ─── 1. SHARED STYLES (Always active) ─── */
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

header[data-testid="stHeader"] {
    height: 2rem !important;
    min-height: 2rem !important;
}

/* Scrollbar sizing */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: #cc44ff; }

/* ─── 2. DARK MODE (Only active if system is Dark) ─── */
@media (prefers-color-scheme: dark) {
    .stApp, .stMain, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: linear-gradient(160deg, #1a0033 0%, #2d0050 40%, #1a003a 100%) !important;
    }
    h1 {
        color: #ff88ff !important;
        text-shadow: 3px 3px 0px #880088, 6px 6px 0px #440044 !important;
    }
    h2, h3 { color: #dd88ff !important; text-shadow: 2px 2px 0px #660066 !important; }
    p, li, label { color: #f0bbff !important; }
    
    .stTextInput > div > div > input {
        background-color: #1a0033 !important;
        color: #ffbbff !important;
        border: 3px solid #cc44ff !important;
        box-shadow: 4px 4px 0px #660099 !important;
    }
    
    .pixel-card {
        background: rgba(30, 0, 50, 0.85) !important;
        border: 3px solid #cc44ff !important;
        box-shadow: 6px 6px 0px #440066 !important;
        color: #f0bbff !important;
    }
    
    hr { border-color: #660099 !important; }
    ::-webkit-scrollbar-track { background: #2d0050; }
    .section-label { color: #aa55dd; }
}

/* ─── 3. LIGHT MODE (Only active if system is Light) ─── */
@media (prefers-color-scheme: light) {
    .stApp, .stMain, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: linear-gradient(160deg, #fce4ff 0%, #f5d0ff 40%, #ffe4f8 100%) !important;
    }
    h1 {
        color: #8800bb !important;
        text-shadow: 2px 2px 0px #dd88ff, 4px 4px 0px #cc66ff !important;
    }
    h2, h3 { color: #6600aa !important; text-shadow: 1px 1px 0px #cc88ff !important; }
    p, li, label { color: #440055 !important; }
    
    .stTextInput > div > div > input {
        background-color: #fff5ff !important;
        color: #330044 !important;
        border-color: #aa44cc !important;
        box-shadow: 4px 4px 0px #cc88ff !important;
    }
    
    .pixel-card {
        background: rgba(255, 240, 255, 0.9) !important;
        border-color: #aa44cc !important;
        box-shadow: 6px 6px 0px #cc88dd !important;
        color: #330044 !important;
    }
    
    hr { border-color: #cc88dd !important; }
    ::-webkit-scrollbar-track { background: #f5d0ff; }
    .section-label { color: #7700aa; }
}

/* ─── 4. ANIMATIONS (Always available) ─── */
@keyframes magical-glow {
    0%, 100% { color: #ffddff; text-shadow: 0 0 4px #fff, 0 0 10px #ffaaff, 0 0 20px #ff44ff; }
    50% { color: #ffffff; text-shadow: 0 0 6px #fff, 0 0 14px #ffccff, 0 0 28px #ff88ff; }
}

.pixel-card strong {
    animation: magical-glow 2.5s ease-in-out infinite;
    display: inline-block;
}

/* Button styles (Static gradients) */
.stButton > button {
    background: linear-gradient(180deg, #cc44ff 0%, #9900cc 100%) !important;
    color: #ffffff !important;
    border: 3px solid #ff88ff !important;
    border-radius: 0px !important;
}
</style>
<script>
(function() {
    function syncTheme() {
        var bg = getComputedStyle(document.documentElement)
                     .getPropertyValue('--background-color').trim();
        var isLight = bg === '#ffffff' || bg === '#fff' || bg === 'white';
        document.documentElement.setAttribute(
            'data-user-theme', isLight ? 'light' : 'dark'
        );
    }
    syncTheme();
    // Re-check whenever Streamlit updates :root styles (theme toggle writes here)
    new MutationObserver(syncTheme).observe(document.head, {
        childList: true, subtree: true
    });
    setInterval(syncTheme, 600);
})();
</script>
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
