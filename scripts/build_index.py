"""
One-time script to build the ChromaDB vector index from the Kaggle Spotify dataset.

Dataset: https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset
Save it to:  data/spotify_tracks.csv

Usage:
    python scripts/build_index.py           # index 10,000 songs (fast, good for demos)
    python scripts/build_index.py 50000     # index 50,000 songs
    python scripts/build_index.py 0         # index the entire dataset (~114k songs, slow)

Re-running this script replaces any existing index.
"""

import os
import sys

# Run from the project root so relative paths (data/, src/) resolve correctly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from rag_recommender import song_to_text, CHROMA_PATH, COLLECTION_NAME, EMBEDDING_MODEL

DATA_PATH = "data/spotify_tracks.csv"
DEFAULT_LIMIT = 10_000
BATCH_SIZE = 500


def build_index(limit: int = DEFAULT_LIMIT) -> None:
    # ── 1. Load the dataset ──────────────────────────────────────────────────
    if not os.path.exists(DATA_PATH):
        print(f"\nError: '{DATA_PATH}' not found.\n")
        print("Download the Spotify Tracks dataset from Kaggle:")
        print("  https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset")
        print(f"\nSave the CSV file as:  {DATA_PATH}\n")
        sys.exit(1)

    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)

    required_cols = ["track_name", "artists", "track_genre",
                     "energy", "valence", "danceability", "acousticness", "tempo"]
    df = df.dropna(subset=required_cols)
    df = df.drop_duplicates(subset=["track_name", "artists"])

    if limit and limit < len(df):
        df = df.sample(n=limit, random_state=42)

    print(f"Songs to index: {len(df):,}")

    # ── 2. Set up ChromaDB ───────────────────────────────────────────────────
    os.makedirs(CHROMA_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection(COLLECTION_NAME)
        print("Replaced existing collection.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # ── 3. Load the embedding model ──────────────────────────────────────────
    print(f"Loading embedding model ({EMBEDDING_MODEL})...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # ── 4. Build text descriptions and metadata ──────────────────────────────
    texts, ids, metadatas = [], [], []
    for i, (_, row) in enumerate(df.iterrows()):
        text = song_to_text(
            track_name=str(row["track_name"]),
            artists=str(row["artists"]),
            genre=str(row["track_genre"]),
            energy=float(row["energy"]),
            valence=float(row["valence"]),
            danceability=float(row["danceability"]),
            acousticness=float(row["acousticness"]),
            tempo=float(row["tempo"]),
        )
        texts.append(text)
        ids.append(str(i))
        metadatas.append({
            "title": str(row["track_name"]),
            "artist": str(row["artists"]),
            "genre": str(row["track_genre"]),
        })

    # ── 5. Embed and insert in batches ───────────────────────────────────────
    print("Embedding and indexing songs...")
    for start in range(0, len(texts), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(texts))
        embeddings = model.encode(texts[start:end], show_progress_bar=False).tolist()
        collection.add(
            documents=texts[start:end],
            embeddings=embeddings,
            metadatas=metadatas[start:end],
            ids=ids[start:end],
        )
        print(f"  {end:,}/{len(texts):,}", end="\r")

    print(f"\nDone! {len(texts):,} songs indexed to '{CHROMA_PATH}'")
    print("\nYou can now run the recommender:")
    print("  python src/main.py")


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LIMIT
    build_index(limit)
