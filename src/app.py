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

import base64
from pathlib import Path
import streamlit.components.v1 as components

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

EXAMPLES = [
    "upbeat pop songs for a workout",
    "chill acoustic songs for late night studying",
    "dark intense metal for when I'm angry",
    "happy latin songs for a summer party",
]

st.set_page_config(page_title="✨ Music Recommender", page_icon="🎵", layout="centered")

BASE_DIR = Path(__file__).resolve().parent.parent

dark_bg = image_to_base64(BASE_DIR / "assets" / "darkbg.png")
light_bg = image_to_base64(BASE_DIR / "assets" / "lightbg.png")



_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

.stApp {{
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
    background-repeat: no-repeat !important;
}}

html[data-bg-theme="dark"] .stApp {{
    background-image:
        linear-gradient(rgba(10, 5, 45, 0.35), rgba(20, 0, 60, 0.72)),
        url("data:image/png;base64,{dark_bg}") !important;
}}

html[data-bg-theme="light"] .stApp {{
    background-image:
        linear-gradient(rgba(255, 235, 255, 0.25), rgba(255, 220, 255, 0.45)),
        url("data:image/png;base64,{light_bg}") !important;
}}        

.stApp, .stApp * {
    font-family: 'Press Start 2P', monospace !important;
}

/* Base text size */
.stApp p,
.stApp li,
.stApp label,
.stApp input,
.stApp textarea,
.stApp button {
    font-size: 0.8rem !important;
}

/* Headings */
.stApp h1 {
    font-size: 2.5rem !important;
}

.stApp h2,
.stApp h3 {
    font-size: .8rem !important;
}
.block-container {
    padding-top: 2rem !important;
    max-width: 760px !important;
}

h1 {
    color: #ffe6ff !important;
    text-shadow:
        2px 2px 0px #5b2b9b,
        4px 4px 0px #2d145f,
        0 0 10px #ff8cff,
        0 0 24px #9b7cff !important;
    text-align: center;
}

h2, h3 {
    color: #6600aa !important;
    text-shadow: 1px 1px 0px #cc88ff !important;
}

.section-label {
    color: #7700aa !important;
}

.section-label::before,
.section-label::after {
    content: " ✧ ";
    color: #ffd36e;
    text-shadow: 0 0 8px #ffb3ff;
}        

.stTextInput input {
    background: rgba(20, 12, 75, 0.88) !important;
    color: #ffe6ff !important;
    border: 3px solid #ff8cff !important;
    box-shadow:
        0 0 12px rgba(255, 140, 255, 0.9),
        4px 4px 0px #3b1a75 !important;
}

.stTextInput input::placeholder {
    color: #c9a7ff !important;
}

.pixel-card {
    background: rgba(18, 10, 70, 0.78) !important;
    border: 3px solid #ff8cff !important;
    box-shadow:
        0 0 12px #ff8cff,
        0 0 28px rgba(180, 80, 255, 0.7),
        6px 6px 0px #3b1a75 !important;
    color: #ffe6ff !important;
    padding: 1.25rem;
    position: relative;
}

.stButton > button {
    background: rgba(30, 18, 95, 0.85) !important;
    color: #ffe6ff !important;
    border: 3px solid #ff8cff !important;
    border-radius: 0px !important;
    box-shadow:
        0 0 10px rgba(255, 140, 255, 0.9),
        4px 4px 0px #3b1a75 !important;
    text-shadow: 2px 2px 0px #3b1a75 !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow:
        0 0 16px #ffb3ff,
        0 0 32px rgba(255, 140, 255, 0.8),
        4px 4px 0px #3b1a75 !important;
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
            0 0 1px #fff,
            0 0 4px #dd88ff,
            0 0 8px #cc66ff,
            0 0 13px #bb55dd;
    }
    50% {
        color: #cc44ff;
        text-shadow:
            0 0 2px #fff,
            0 0 6px #ffccff,
            0 0 12px #ee99ff,
            0 0 18px #dd77ff;
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

.sparkle {
    position: fixed;
    pointer-events: none;
    z-index: 3;
    font-size: 1rem;
    opacity: 0;

    text-shadow:
        0 0 6px #ffffff,
        0 0 14px #ff9cff,
        0 0 28px #b66dff;

    animation: sparkle-fade 5s ease-in-out infinite;
}

/* Each sparkle has a unique position + delay */

.sparkle-1 {
    top: 18%;
    left: 15%;
    animation-delay: 0s;
}

.sparkle-2 {
    top: 32%;
    right: 18%;
    animation-delay: 1.5s;
}

.sparkle-3 {
    top: 55%;
    left: 22%;
    animation-delay: 3s;
}

.sparkle-4 {
    bottom: 20%;
    right: 25%;
    animation-delay: 4.5s;
}

.sparkle-5 {
    top: 12%;
    right: 35%;
    animation-delay: 2.2s;
}

/* Soft fade in/out (no bouncing) */
@keyframes sparkle-fade {
    0%, 100% {
        opacity: 0;
    }
    45%, 60% {
        opacity: 0.9;
    }
}
</style>
"""
st.html(_html.replace("{{", "{").replace("}}", "}").replace("{dark_bg}", dark_bg).replace("{light_bg}", light_bg))

st.html("""
<div class="sparkle sparkle-1">✦</div>
<div class="sparkle sparkle-2">✦</div>
<div class="sparkle sparkle-3">✦</div>
<div class="sparkle sparkle-4">✦</div>
<div class="sparkle sparkle-5">✦</div>
""")
components.html(
    """
    <script>
    function syncBackgroundTheme() {
        const parentDoc = window.parent.document;
        const root = parentDoc.documentElement;

        const candidates = [
            root,
            parentDoc.body,
            parentDoc.querySelector(".stApp"),
            parentDoc.querySelector("[data-testid='stAppViewContainer']")
        ].filter(Boolean);

        let bg = "";

        for (const el of candidates) {
            const styles = getComputedStyle(el);

            bg =
                styles.getPropertyValue("--background-color").trim() ||
                styles.backgroundColor.trim();

            if (bg && bg !== "rgba(0, 0, 0, 0)" && bg !== "transparent") {
                break;
            }
        }

        let newTheme = "dark";

        if (
            bg.includes("252, 228, 255") ||
            bg.includes("255, 245, 255") ||
            bg.includes("255, 255, 255") ||
            bg === "#fce4ff" ||
            bg === "#fff5ff" ||
            bg === "#ffffff"
        ) {
            newTheme = "light";
        }

        if (root.getAttribute("data-bg-theme") !== newTheme) {
            root.setAttribute("data-bg-theme", newTheme);
        }
    }

    syncBackgroundTheme();

    const observer = new MutationObserver(syncBackgroundTheme);

    observer.observe(window.parent.document.documentElement, {
        attributes: true
    });

    observer.observe(window.parent.document.head, {
        childList: true,
        subtree: true
    });

    setInterval(syncBackgroundTheme, 1000);

    function injectHeadingStyles() {
        const parentDoc = window.parent.document;
        if (parentDoc.getElementById('st-heading-size-fix')) return;
        const s = parentDoc.createElement('style');
        s.id = 'st-heading-size-fix';
        s.textContent = `
            .stApp h1,
            [data-testid="stHeading"] h1,
            [data-testid="stHeadingWithActionElements"] {
                font-size: 2.8rem !important;
            }
            .stApp h2, .stApp h3,
            [data-testid="stHeading"] h2,
            [data-testid="stHeading"] h3 {
                font-size: 1rem !important;
            }
        `;
        parentDoc.head.appendChild(s);
    }
    injectHeadingStyles();
    </script>
    """,
    height=0,
)

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
        try:
            result = recommender.recommend(query)
        except ValueError as e:
            st.warning(f"**invalid query:** {e}")
            st.stop()
        except RuntimeError as e:
            st.error(f"**api error:** {e}\n\ncheck your `GOOGLE_API_KEY` and try again.")
            st.stop()
        except Exception as e:
            st.error(f"**unexpected error:** {e}")
            st.stop()

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