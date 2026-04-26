"""
Music Recommender

Run modes:
    python src/main.py            # RAG mode — natural-language queries (default)
    python src/main.py --legacy   # original deterministic recommender (songs.csv)

RAG mode requires:
    1. GOOGLE_API_KEY set in your .env file
    2. The index built:  python scripts/build_index.py
"""

import sys
import os


# ── RAG mode ─────────────────────────────────────────────────────────────────

def run_rag() -> None:
    from rag_recommender import RAGRecommender

    print("\n  Music Recommender")
    print("  Describe the kind of music you want and we'll find it.\n")
    print("  Examples:")
    print("    'upbeat pop songs for a workout'")
    print("    'chill acoustic songs for late night studying'")
    print("    'dark intense metal for when I'm angry'")
    print("    'happy latin songs for a summer party'")
    print("\n  Type 'quit' to exit.\n")

    try:
        recommender = RAGRecommender()
    except FileNotFoundError as e:
        print(f"\nSetup needed: {e}\n")
        sys.exit(1)

    while True:
        try:
            query = input("What are you in the mood for? ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue

        print("\nSearching...\n")
        result = recommender.recommend(query)
        print(result)
        print()


# ── Legacy mode ───────────────────────────────────────────────────────────────

def run_legacy() -> None:
    from recommender import load_songs, recommend_songs

    PROFILES = {
        "High-Energy Pop": {
            "favorite_genre":      "pop",
            "acceptable_moods":    ["happy", "euphoric"],
            "target_energy":       0.85,
            "target_valence":      0.85,
            "target_tempo_bpm":    125,
            "target_acousticness": 0.10,
            "target_danceability": 0.85,
            "tempo_min": 60,
            "tempo_max": 168,
            "weights": {
                "energy":       0.30,
                "valence":      0.20,
                "tempo":        0.15,
                "acousticness": 0.15,
                "danceability": 0.10,
                "mood_bonus":   0.05,
                "genre_bonus":  0.05,
            },
        },
        "Chill Lofi": {
            "favorite_genre":      "lofi",
            "acceptable_moods":    ["chill", "focused"],
            "target_energy":       0.40,
            "target_valence":      0.58,
            "target_tempo_bpm":    80,
            "target_acousticness": 0.78,
            "target_danceability": 0.60,
            "tempo_min": 60,
            "tempo_max": 168,
            "weights": {
                "energy":       0.30,
                "valence":      0.20,
                "tempo":        0.15,
                "acousticness": 0.15,
                "danceability": 0.10,
                "mood_bonus":   0.05,
                "genre_bonus":  0.05,
            },
        },
        "Deep Intense Rock": {
            "favorite_genre":      "rock",
            "acceptable_moods":    ["intense", "angry"],
            "target_energy":       0.95,
            "target_valence":      0.35,
            "target_tempo_bpm":    155,
            "target_acousticness": 0.07,
            "target_danceability": 0.60,
            "tempo_min": 60,
            "tempo_max": 168,
            "weights": {
                "energy":       0.35,
                "valence":      0.20,
                "tempo":        0.20,
                "acousticness": 0.10,
                "danceability": 0.05,
                "mood_bonus":   0.05,
                "genre_bonus":  0.05,
            },
        },
    }

    def print_recommendations(label, recommendations):
        width = 50
        print(f"\n{'=' * width}")
        print(f"  Profile: {label}")
        print(f"  Top {len(recommendations)} Recommendations")
        print(f"{'=' * width}")
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            bar = "#" * round(score * 20)
            print(f"\n  #{rank}  {song['title']} by {song['artist']}")
            print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}")
            print(f"       Score: {score:.2f}  [{bar:<20}]")
            print(f"       Why:   {explanation}")
        print(f"\n{'=' * width}\n")

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    for label, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(label, recommendations)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--legacy" in sys.argv:
        run_legacy()
    else:
        run_rag()
