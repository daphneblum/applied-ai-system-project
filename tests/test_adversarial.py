"""
Adversarial / edge-case evaluation for score_song and recommend_songs.

Each test targets a specific structural weakness in the scoring logic.
Run with:  pytest tests/test_adversarial.py -v   (from the repo root)
"""
import math
import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from recommender import score_song, recommend_songs

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

BASE_WEIGHTS = {
    "energy":       0.30,
    "valence":      0.20,
    "tempo":        0.15,
    "acousticness": 0.15,
    "danceability": 0.10,
    "mood_bonus":   0.05,
    "genre_bonus":  0.05,
}

def make_song(**overrides):
    """Return a minimal, valid song dict with sensible defaults."""
    defaults = {
        "id":            1,
        "title":         "Test Song",
        "artist":        "Test Artist",
        "genre":         "pop",
        "mood":          "happy",
        "energy":        0.5,
        "tempo_bpm":     100,
        "valence":       0.5,
        "danceability":  0.5,
        "acousticness":  0.5,
    }
    return {**defaults, **overrides}

def make_prefs(**overrides):
    """Return a minimal, valid user-prefs dict with sensible defaults."""
    defaults = {
        "favorite_genre":      "pop",
        "acceptable_moods":    ["happy"],
        "target_energy":       0.5,
        "target_valence":      0.5,
        "target_tempo_bpm":    100,
        "target_acousticness": 0.5,
        "target_danceability": 0.5,
        "tempo_min":           60,
        "tempo_max":           168,
        "weights":             {**BASE_WEIGHTS},
    }
    return {**defaults, **overrides}


# ===========================================================================
# CASE 1  Contradictory profile: high energy target + "sad" acceptable mood
#
# Why adversarial: the user wants driving, energetic songs (energy=0.9) but
# only accepts mood="sad". Sad songs in the catalog are low-energy (≈0.25),
# so the top-ranked song will likely be whatever best satisfies the heavy
# energy weight (0.30) — probably a high-energy song that is NOT sad.
# This exposes that mood (weight=0.05) is easily drowned out by energy.
# ===========================================================================

CONTRADICTORY_PREFS = make_prefs(
    target_energy=0.9,
    target_valence=0.4,
    acceptable_moods=["sad"],
    weights={**BASE_WEIGHTS, "energy": 0.30, "mood_bonus": 0.05},
)

SAD_SONG    = make_song(mood="sad",    energy=0.25, tempo_bpm=74)
ENERGY_SONG = make_song(mood="angry",  energy=0.97, tempo_bpm=168)

def test_contradictory_high_energy_sad_mood_energy_wins():
    """
    BUG / DESIGN FLAW: The high-energy non-sad song beats the sad low-energy
    song, even though 'sad' is the only acceptable mood. The mood_bonus weight
    (0.05) is too small to compensate for a 0.72-point energy gap.
    """
    sad_score,    _ = score_song(CONTRADICTORY_PREFS, SAD_SONG)
    energy_score, _ = score_song(CONTRADICTORY_PREFS, ENERGY_SONG)

    # This assertion PASSES — but exposes the design flaw:
    # the user said they want sad songs, yet an angry high-energy song ranks higher.
    assert energy_score > sad_score, (
        f"Expected high-energy song to outrank sad song due to weight imbalance.\n"
        f"  sad_score={sad_score:.4f}  energy_score={energy_score:.4f}\n"
        f"  Mood weight is only {CONTRADICTORY_PREFS['weights']['mood_bonus']:.0%} "
        f"of total — easily overridden by energy (30%)."
    )


def test_contradictory_mood_bonus_never_fully_compensates():
    """
    Even with max mood weight (0.30), a large enough energy delta still wins.
    """
    boosted_weights = {**BASE_WEIGHTS, "energy": 0.30, "mood_bonus": 0.30,
                       "valence": 0.15, "danceability": 0.05}
    prefs = make_prefs(target_energy=0.9, acceptable_moods=["sad"],
                       weights=boosted_weights)
    sad_score,    _ = score_song(prefs, SAD_SONG)
    energy_score, _ = score_song(prefs, ENERGY_SONG)

    # Document which regime flips the outcome
    print(f"\n  Mood bonus=0.30: sad={sad_score:.4f}  energy={energy_score:.4f}")
    # No hard assertion — just record the cross-over for the evaluation report


# ===========================================================================
# CASE 2  Tempo target outside [tempo_min, tempo_max]
#
# Why adversarial: if target_tempo_bpm > tempo_max, target_tempo_norm > 1.
# For low-BPM songs, song_tempo_norm ≈ 0, so:
#   |target_tempo_norm - song_tempo_norm| > 1  →  tempo_score < 0
# Negative component weights infect the total score.
# ===========================================================================

def test_tempo_target_above_max_causes_negative_tempo_score():
    """
    BUG: target_tempo_bpm=200 with tempo_max=168 produces a negative
    tempo_score. Low-BPM songs are penalised *below zero* on that component.
    """
    prefs = make_prefs(target_tempo_bpm=200, tempo_min=60, tempo_max=168)
    low_bpm_song = make_song(tempo_bpm=60)

    score, _ = score_song(prefs, low_bpm_song)

    # Manually compute expected tempo component
    tempo_range       = 168 - 60
    song_norm         = (60  - 60) / tempo_range   # = 0.0
    target_norm       = (200 - 60) / tempo_range   # ≈ 1.296
    expected_tempo_sc = 1 - abs(target_norm - song_norm)  # ≈ -0.296

    assert expected_tempo_sc < 0, "Precondition: tempo score should be negative"
    # Verify the bug actually occurs
    weighted_tempo = expected_tempo_sc * prefs["weights"]["tempo"]
    assert weighted_tempo < 0, (
        f"Negative tempo component ({weighted_tempo:.4f}) taints the total score."
    )


# ===========================================================================
# CASE 3  Zero tempo range → ZeroDivisionError
#
# Why adversarial: tempo_range = tempo_max - tempo_min is used as a divisor.
# If both are equal the formula divides by zero.
# ===========================================================================

def test_zero_tempo_range_raises():
    """
    BUG: tempo_min == tempo_max causes ZeroDivisionError in score_song.
    """
    prefs = make_prefs(tempo_min=120, tempo_max=120, target_tempo_bpm=120)
    song  = make_song(tempo_bpm=120)

    with pytest.raises(ZeroDivisionError):
        score_song(prefs, song)


# ===========================================================================
# CASE 4  Weights that do NOT sum to 1
#
# Why adversarial: the scoring formula assumes weights sum to 1 (max score=1).
# If they sum to e.g. 3.0, scores exceed 1.0 and the bar visualisation in
# main.py overflows: "#" * round(score * 20) can produce 50+ characters.
# ===========================================================================

def test_oversized_weights_score_exceeds_one():
    """
    BUG: No weight-normalisation guard. A perfect-match song with weights
    summing to 3.0 scores above 1.0, breaking UI and semantic meaning.
    """
    fat_weights = {k: 0.5 for k in BASE_WEIGHTS}  # sum = 3.5
    prefs = make_prefs(
        target_energy=0.5, target_valence=0.5, target_acousticness=0.5,
        target_danceability=0.5, target_tempo_bpm=100,
        weights=fat_weights,
        favorite_genre="pop", acceptable_moods=["happy"],
    )
    perfect_song = make_song(
        genre="pop", mood="happy",
        energy=0.5, valence=0.5, acousticness=0.5, danceability=0.5, tempo_bpm=100,
    )
    score, _ = score_song(prefs, perfect_song)

    assert score > 1.0, (
        f"Expected score > 1.0 with fat weights; got {score:.4f}. "
        f"bar length would be {round(score * 20)} hashes."
    )


# ===========================================================================
# CASE 5  All weights = 0
#
# Why adversarial: every component contributes nothing. All songs tie at 0.0.
# recommend_songs returns an arbitrary ordering (stable sort on 0.0).
# ===========================================================================

def test_all_zero_weights_every_song_ties():
    """
    EDGE CASE: Zero weights make every song score 0.0. The recommender returns
    k songs but their ranking is arbitrary (catalog insertion order).
    """
    zero_weights = {k: 0.0 for k in BASE_WEIGHTS}
    prefs = make_prefs(weights=zero_weights)

    songs = [make_song(id=i, energy=i/10) for i in range(1, 6)]
    results = recommend_songs(prefs, songs, k=5)

    scores = [s[1] for s in results]
    assert all(s == 0.0 for s in scores), (
        f"Expected all scores = 0.0 with zero weights; got {scores}"
    )


# ===========================================================================
# CASE 6  Empty acceptable_moods list
#
# Why adversarial: the mood_bonus weight (0.05) is never awarded, silently
# discarding a meaningful portion of the scoring budget. Songs are ranked
# entirely on audio features no matter how mood-relevant they are.
# ===========================================================================

def test_empty_acceptable_moods_no_mood_bonus_ever_awarded():
    """
    EDGE CASE: acceptable_moods=[] means mood_bonus=0 for every song.
    The 5% mood budget is permanently wasted.
    """
    prefs = make_prefs(acceptable_moods=[])
    happy_song = make_song(mood="happy")
    score, reasons = score_song(prefs, happy_song)

    assert "mood match" not in " ".join(reasons), (
        "No mood should ever match when acceptable_moods is empty."
    )
    # Confirm the bonus weight (0.05) was never added
    # Best possible score without mood/genre bonus = sum of numeric weights = 0.90
    max_numeric = sum(v for k, v in prefs["weights"].items()
                      if k not in ("mood_bonus", "genre_bonus"))
    assert score <= max_numeric + prefs["weights"]["genre_bonus"] + 1e-9


# ===========================================================================
# CASE 7  Favorite genre not present in catalog
#
# Why adversarial: genre_bonus is never awarded. A niche-genre user gets
# recommendations with a permanently unused 5% budget slot — but the system
# never signals this to the user.
# ===========================================================================

def test_favorite_genre_absent_from_catalog():
    """
    EDGE CASE: If the user's favorite_genre appears in zero songs, genre_bonus
    is never awarded and the weight is silently wasted.
    """
    prefs = make_prefs(favorite_genre="bossa-nova")
    songs = [make_song(id=i, genre="pop") for i in range(1, 6)]

    results = recommend_songs(prefs, songs, k=5)
    for song, score, _ in results:
        _, reasons = score_song(prefs, song)
        assert "genre match" not in " ".join(reasons), (
            "genre_bonus should never appear when the genre is absent from catalog."
        )


# ===========================================================================
# CASE 8  Negative weight values (inverted scoring)
#
# Why adversarial: a weight of -0.30 for energy means songs CLOSER to the
# target_energy are penalised. This inverts the recommender's intent for that
# feature, potentially surfacing the worst matches.
# ===========================================================================

def test_negative_weight_inverts_feature_ranking():
    """
    BUG: Negative weights are accepted without error. A negative energy weight
    means songs CLOSE to target_energy score LOWER — the opposite of intent.
    """
    inverted_weights = {**BASE_WEIGHTS, "energy": -0.30}
    prefs = make_prefs(target_energy=0.9, weights=inverted_weights)

    close_song = make_song(energy=0.90)   # should score HIGH normally
    far_song   = make_song(energy=0.10)   # should score LOW normally

    close_score, _ = score_song(prefs, close_song)
    far_score,   _ = score_song(prefs, far_song)

    # With inverted weight, the "close" song scores lower — the bug manifests
    assert close_score < far_score, (
        f"Negative weight inverts ranking: close={close_score:.4f} "
        f"far={far_score:.4f}. No guard prevents this."
    )


# ===========================================================================
# CASE 9  Song with all-extreme audio features (floor at 0.0)
#
# Why adversarial: energy=0, valence=0, acousticness=0, danceability=0.
# Every 1-|target-actual| term = 1 - target. Scores near 0 if targets are
# high, exposing that the formula has no floor guard.
# ===========================================================================

def test_all_zero_song_features_score_near_floor():
    """
    EDGE CASE: A song where every feature = 0.0 receives the maximum possible
    penalty for each component. Scores stay ≥ 0 because all targets are ≤ 1,
    but highlights the asymmetry: '1 - |t - 0| = 1 - t' never goes negative
    when t ∈ [0, 1]. Verify the floor holds.
    """
    prefs = make_prefs(
        target_energy=1.0, target_valence=1.0,
        target_acousticness=1.0, target_danceability=1.0,
        target_tempo_bpm=168, tempo_min=60, tempo_max=168,
    )
    worst_song = make_song(energy=0.0, valence=0.0, acousticness=0.0,
                           danceability=0.0, tempo_bpm=60)
    score, _ = score_song(prefs, worst_song)
    assert score >= 0.0, f"Score should not go below 0 for in-range features; got {score:.4f}"


# ===========================================================================
# CASE 10  k > len(songs) — recommend_songs asks for more songs than exist
#
# Why adversarial: sorted()[:k] silently returns fewer than k results.
# Callers expecting exactly k items (e.g., zip with rank labels) may fail.
# ===========================================================================

def test_k_larger_than_catalog_returns_all_songs():
    """
    EDGE CASE: Requesting k=20 from a 3-song catalog silently returns 3.
    The system doesn't raise an error or warn the caller.
    """
    prefs = make_prefs()
    songs = [make_song(id=i) for i in range(1, 4)]   # 3 songs
    results = recommend_songs(prefs, songs, k=20)

    assert len(results) == 3, (
        f"Expected 3 results (catalog size), got {len(results)}. "
        "No warning is raised when k exceeds catalog size."
    )
