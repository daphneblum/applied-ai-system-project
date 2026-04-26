"""
Pure unit tests for the RAG module — no ChromaDB index or API key required.

These tests cover:
  - song_to_text() output format and labels
  - RAGRecommender error handling for missing index
  - recommend() input validation guardrails
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rag_recommender import song_to_text, RAGRecommender, MAX_QUERY_LENGTH


# ---------------------------------------------------------------------------
# song_to_text — pure function, no dependencies
# ---------------------------------------------------------------------------

def test_song_to_text_contains_track_and_artist():
    text = song_to_text("Midnight Rain", "Taylor Swift", "pop",
                        energy=0.6, valence=0.7, danceability=0.7,
                        acousticness=0.2, tempo=120)
    assert "Midnight Rain" in text
    assert "Taylor Swift" in text


def test_song_to_text_high_energy_label():
    text = song_to_text("X", "Y", "rock",
                        energy=0.9, valence=0.5, danceability=0.5,
                        acousticness=0.1, tempo=140)
    assert "Very energetic" in text


def test_song_to_text_low_energy_label():
    text = song_to_text("X", "Y", "lofi",
                        energy=0.2, valence=0.5, danceability=0.5,
                        acousticness=0.8, tempo=80)
    assert "calm and low energy" in text.lower()


def test_song_to_text_slow_tempo_label():
    text = song_to_text("X", "Y", "pop",
                        energy=0.5, valence=0.5, danceability=0.5,
                        acousticness=0.5, tempo=70)
    assert "slow tempo" in text


def test_song_to_text_very_acoustic_label():
    text = song_to_text("X", "Y", "folk",
                        energy=0.3, valence=0.5, danceability=0.4,
                        acousticness=0.9, tempo=90)
    assert "Very acoustic" in text


# ---------------------------------------------------------------------------
# RAGRecommender.__init__ — error paths that don't require a real index
# ---------------------------------------------------------------------------

def test_rag_recommender_raises_file_not_found_on_missing_index():
    with pytest.raises(FileNotFoundError, match="build_index"):
        RAGRecommender(chroma_path="data/does_not_exist_xyz")


# ---------------------------------------------------------------------------
# recommend() input validation — checked before any DB or API call,
# so these work even without an initialised index (object.__new__ bypasses __init__)
# ---------------------------------------------------------------------------

def _bare_recommender():
    """Return a RAGRecommender with no __init__ run — only for testing validation."""
    return object.__new__(RAGRecommender)


def test_recommend_raises_on_empty_query():
    rec = _bare_recommender()
    with pytest.raises(ValueError, match="empty"):
        rec.recommend("")


def test_recommend_raises_on_whitespace_only_query():
    rec = _bare_recommender()
    with pytest.raises(ValueError, match="empty"):
        rec.recommend("   ")


def test_recommend_raises_on_overlong_query():
    rec = _bare_recommender()
    with pytest.raises(ValueError, match="too long"):
        rec.recommend("x" * (MAX_QUERY_LENGTH + 1))


def test_recommend_accepts_query_at_exact_max_length():
    """A query exactly at the limit should pass validation (not raise)."""
    rec = _bare_recommender()
    boundary_query = "a" * MAX_QUERY_LENGTH
    # Validation passes; the next line (embed) would fail without a real model,
    # so we catch AttributeError to confirm we got past the guard.
    with pytest.raises(AttributeError):
        rec.recommend(boundary_query)
