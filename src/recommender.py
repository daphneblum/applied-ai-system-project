from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Parse a CSV file of songs into a list of dicts with numeric fields cast to int or float."""
    import csv

    int_fields   = {"id", "tempo_bpm"}
    float_fields = {"energy", "valence", "danceability", "acousticness"}

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return a weighted similarity score and a list of reasons for a single song against user preferences."""
    weights = user_prefs["weights"]

    # --- Numerical feature scores: 1 - |target - actual| ---
    energy_score       = 1 - abs(user_prefs["target_energy"]       - song["energy"])
    valence_score      = 1 - abs(user_prefs["target_valence"]      - song["valence"])
    acousticness_score = 1 - abs(user_prefs["target_acousticness"] - song["acousticness"])
    danceability_score = 1 - abs(user_prefs["target_danceability"] - song["danceability"])

    # Tempo is in BPM, so normalize to [0, 1] before scoring
    tempo_range        = user_prefs["tempo_max"] - user_prefs["tempo_min"]
    song_tempo_norm    = (song["tempo_bpm"]                - user_prefs["tempo_min"]) / tempo_range
    target_tempo_norm  = (user_prefs["target_tempo_bpm"]   - user_prefs["tempo_min"]) / tempo_range
    tempo_score        = 1 - abs(target_tempo_norm - song_tempo_norm)

    # --- Categorical bonuses ---
    genre_bonus = weights["genre_bonus"] if song["genre"] == user_prefs["favorite_genre"] else 0.0
    mood_bonus  = weights["mood_bonus"]  if song["mood"]  in user_prefs["acceptable_moods"] else 0.0

    # --- Weighted total ---
    score = (
        energy_score       * weights["energy"]       +
        valence_score      * weights["valence"]      +
        tempo_score        * weights["tempo"]        +
        acousticness_score * weights["acousticness"] +
        danceability_score * weights["danceability"] +
        genre_bonus +
        mood_bonus
    )

    # --- Build reasons list ---
    reasons = []
    if genre_bonus:
        reasons.append(f"genre match ({song['genre']})")
    if mood_bonus:
        reasons.append(f"mood match ({song['mood']})")

    # Report the two numerical features that contributed the most
    numeric_contribs = {
        "energy":       energy_score       * weights["energy"],
        "valence":      valence_score      * weights["valence"],
        "tempo":        tempo_score        * weights["tempo"],
        "acousticness": acousticness_score * weights["acousticness"],
        "danceability": danceability_score * weights["danceability"],
    }
    top_two = sorted(numeric_contribs.items(), key=lambda x: x[1], reverse=True)[:2]
    for feature, _ in top_two:
        reasons.append(f"close {feature}")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song against user preferences and return the top k sorted by score descending."""
    scored = [
        (song, score, ", ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
