"""
RAG-based music recommender.

Flow:
  1. A user types a natural-language request ("chill songs for studying").
  2. The request is embedded with sentence-transformers.
  3. ChromaDB returns the most semantically similar songs from the indexed catalog.
  4. Gemini receives those songs as context and generates recommendations.

Build the index first:
  python scripts/build_index.py
"""

import logging
import os
from dotenv import load_dotenv
load_dotenv()
import chromadb
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "songs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

MAX_QUERY_LENGTH = 500


def song_to_text(
    track_name: str,
    artists: str,
    genre: str,
    energy: float,
    valence: float,
    danceability: float,
    acousticness: float,
    tempo: float,
) -> str:
    """Convert song features into a descriptive sentence for embedding.

    Using natural language (instead of raw numbers) means the embedding model
    can match queries like "chill acoustic" to songs described that way.
    """
    if energy > 0.8:
        energy_desc = "very energetic"
    elif energy > 0.6:
        energy_desc = "energetic"
    elif energy > 0.4:
        energy_desc = "moderate energy"
    else:
        energy_desc = "calm and low energy"

    if valence > 0.75:
        mood_desc = "very upbeat and positive"
    elif valence > 0.5:
        mood_desc = "upbeat"
    elif valence > 0.25:
        mood_desc = "somewhat somber"
    else:
        mood_desc = "dark and melancholic"

    if danceability > 0.75:
        dance_desc = "very danceable"
    elif danceability > 0.5:
        dance_desc = "danceable"
    else:
        dance_desc = "not very danceable"

    if acousticness > 0.75:
        acoustic_desc = "very acoustic"
    elif acousticness > 0.4:
        acoustic_desc = "somewhat acoustic"
    else:
        acoustic_desc = "electric and produced"

    if tempo > 140:
        tempo_desc = "very fast tempo"
    elif tempo > 120:
        tempo_desc = "fast tempo"
    elif tempo > 90:
        tempo_desc = "moderate tempo"
    else:
        tempo_desc = "slow tempo"

    return (
        f"{track_name} by {artists} - {genre} song. "
        f"{energy_desc.capitalize()}, {mood_desc}, {dance_desc}. "
        f"{acoustic_desc.capitalize()}, {tempo_desc} at {tempo:.0f} BPM."
    )


class RAGRecommender:
    def __init__(self, chroma_path: str = CHROMA_PATH):
        if not os.path.exists(chroma_path):
            raise FileNotFoundError(
                f"No index found at '{chroma_path}'. "
                "Run 'python scripts/build_index.py' first."
            )
        logger.info("Loading ChromaDB index from '%s'", chroma_path)
        self.chroma = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma.get_collection(COLLECTION_NAME)
        logger.info("Loading embedding model '%s'", EMBEDDING_MODEL)
        self.embed_model = SentenceTransformer(EMBEDDING_MODEL)
        self.gemini = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        logger.info("RAGRecommender ready (%d songs indexed)", self.collection.count())

    def recommend(self, query: str, k: int = 5, retrieve_n: int = 15) -> str:
        """Return a Gemini-generated recommendation for the given natural-language query.

        Args:
            query:      What the user is looking for, in plain English.
            k:          Number of songs to recommend in the final response.
            retrieve_n: How many candidate songs to pull from the vector store
                        before passing them to Gemini. Should be >= k.

        Raises:
            ValueError: If the query is empty or exceeds MAX_QUERY_LENGTH.
        """
        query = query.strip()
        if not query:
            raise ValueError("Query must not be empty.")
        if len(query) > MAX_QUERY_LENGTH:
            raise ValueError(
                f"Query is too long ({len(query)} chars). "
                f"Please keep it under {MAX_QUERY_LENGTH} characters."
            )

        logger.info("Query received: %r (k=%d, retrieve_n=%d)", query, k, retrieve_n)

        # 1. Embed the user query with the same model used at index time
        query_embedding = self.embed_model.encode(query).tolist()

        # 2. Retrieve the closest matches from ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=retrieve_n,
            include=["documents", "metadatas", "distances"],
        )
        candidates = results["documents"][0]
        logger.info("Retrieved %d candidate songs from vector store", len(candidates))

        # ChromaDB cosine space returns (1 - cosine_similarity); invert for readability
        distances = results["distances"][0]
        similarities = [round(1 - d, 3) for d in distances]
        avg_sim = sum(similarities) / len(similarities) if similarities else 0.0
        min_sim = min(similarities) if similarities else 0.0
        logger.info(
            "Retrieval confidence — avg similarity: %.3f, min: %.3f",
            avg_sim, min_sim,
        )
        if avg_sim < 0.25:
            logger.warning(
                "Low retrieval confidence (avg=%.3f). "
                "The query may be too niche or ambiguous for the indexed catalog.",
                avg_sim,
            )

        # 3. Format retrieved songs as numbered context for Gemini
        songs_context = "\n".join(
            f"{i + 1}. {doc}"
            for i, doc in enumerate(results["documents"][0])
        )

        # 4. Ask Gemini to pick the best k and explain each choice
        prompt = (
            f'Request: "{query}"\n\n'
            f"Candidate songs:\n{songs_context}\n\n"
            f"Please recommend the top {k} songs from the list above "
            f"that best match this request, with a brief explanation for each."
        )

        logger.info("Calling Gemini (model=gemini-2.5-flash)")
        try:
            response = self.gemini.models.generate_content(
                model="models/gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are a music recommendation assistant. "
                        "Given a user's request and a list of candidate songs retrieved "
                        "from a catalog, recommend the best matches. For each song you "
                        "recommend, write a short, specific explanation of why it fits "
                        "the user's request — mention mood, energy, tempo, or genre as relevant."
                    ),
                ),
                contents=prompt,
            )
        except Exception as exc:
            logger.error("Gemini API call failed: %s", exc)
            raise RuntimeError(f"Could not reach the Gemini API: {exc}") from exc

        logger.info("Gemini response received successfully")
        return response.text
