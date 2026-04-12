"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

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
            "energy":       0.35,   # raw power is the top priority
            "valence":      0.20,   # darker emotional tone matters
            "tempo":        0.20,   # fast BPM is part of the genre feel
            "acousticness": 0.10,   # electric/produced sound expected
            "danceability": 0.05,   # least important for this listener
            "mood_bonus":   0.05,
            "genre_bonus":  0.05,
        },
    },
}


def print_recommendations(label: str, recommendations: list) -> None:
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


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for label, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(label, recommendations)


if __name__ == "__main__":
    main()
