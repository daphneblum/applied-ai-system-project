"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Taste profile for an upbeat pop listener.
    user_prefs = {
        "favorite_genre":  "pop",
        "acceptable_moods": ["happy", "euphoric"],

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
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    width = 50
    print(f"\n{'=' * width}")
    print(f"  Top {len(recommendations)} Recommendations")
    print(f"{'=' * width}")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        bar = "#" * round(score * 20)
        print(f"\n  #{rank}  {song['title']} by {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}")
        print(f"       Score: {score:.2f}  [{bar:<20}]")
        print(f"       Why:   {explanation}")
    print(f"\n{'=' * width}\n")


if __name__ == "__main__":
    main()
