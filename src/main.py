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

    # Taste profile for a late-night study session listener.
    # Numerical features (0.0 - 1.0) represent the user's ideal target value.
    # The recommender rewards songs whose features are closest to these targets.
    # tempo_bpm is in beats per minute and will be normalized before scoring.
    user_prefs = {
        # --- Categorical preferences ---
        "favorite_genre":  "lofi",
        # Fix 2: list of moods instead of a single label so "chill" and "focused"
        # both earn the mood bonus — removes the asymmetric 0.10 penalty on chill
        # lofi songs that are otherwise equally good matches.
        "acceptable_moods": ["focused", "chill"],

        # --- Numerical targets (all on a 0.0 – 1.0 scale except tempo) ---
        "target_energy":       0.40,    # Prefers calm, low-intensity tracks
        "target_valence":      0.58,    # Slightly positive but not euphoric
        "target_tempo_bpm":    80,      # Slow, steady beat (~lofi / jazz range)
        "target_acousticness": 0.78,    # Strong preference for organic / acoustic sound
        "target_danceability": 0.60,    # Moderate groove — present but not distracting

        # Fix 3: tempo normalization range derived from the full 20-song catalog.
        # Adding Iron Cathedral (168 BPM) extended the max from 152 to 168.
        # score_song must use these values so tempo_norm stays within [0, 1].
        "tempo_min": 60,
        "tempo_max": 168,

        # --- Scoring weights (must sum to 1.0) ---
        # Higher weight = that feature matters more in the final score.
        "weights": {
            "energy":       0.30,   # Biggest driver of vibe — weighted highest
            "valence":      0.20,   # Emotional tone is a hard filter for this user
            "tempo":        0.15,   # Tempo shapes focus but overlaps with energy
            "acousticness": 0.15,   # Strong acoustic preference in this profile
            "danceability": 0.10,   # Minor signal — kept low to reduce energy overlap
            # Fix 2: reduced from 0.10 — mood is now one of two acceptable labels,
            # so its bonus is smaller and shared across a broader match zone.
            "mood_bonus":   0.05,
            # Fix 1: genre bonus breaks ties within the low-energy cluster (e.g.
            # lofi vs ambient/jazz songs that have similar numerical features).
            "genre_bonus":  0.05,
        },
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
