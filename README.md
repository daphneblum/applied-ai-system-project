# 🎵 Music Recommender Simulation

## Project Summary

This project builds a small content-based music recommender. It reads a catalog of 20 songs, each described by five numeric features and two labels. A user is represented as a taste profile with target values for each feature and a list of acceptable moods. The system scores every song by measuring how close it is to the user's targets, weights the features by importance, and adds small bonuses for genre and mood matches. The top five songs by score are returned along with a plain-language explanation of why each one ranked where it did.

---

## How The System Works

Real-world recommenders like Spotify and YouTube learn your taste by watching what you play, skip, and save, then find patterns across millions of users to predict what you will enjoy next. They combine two main ideas: collaborative filtering, which says "people who liked the same things you did also loved this," and content-based filtering, which says "this song sounds and feels like the ones you already enjoy." In practice, those systems run on massive amounts of data and continuously update as your behavior changes.

This version focuses on content-based filtering using a catalog of 20 songs. Each song is described by five numerical features (energy, valence, tempo, acousticness, and danceability) plus two categorical labels: genre and mood. A user profile stores target values for each numerical feature and a list of acceptable moods. The recommender scores every song by measuring how close each of its features is to the user's targets, applies weights so that more important features count more, and adds small bonuses when the song's genre or mood matches. Songs are then ranked by total score and the top K are returned. Every recommendation can be explained by pointing directly at which features matched and by how much.

### Algorithm Recipe

**Step 1: Load the catalog**
Parse `data/songs.csv` into a list of song dictionaries, one per row.

**Step 2: Score each song**
For every song, compute a closeness score for each numerical feature:

```
feature_score = 1 - | user_target - song_value |
```

Tempo is first normalized to [0, 1] using the catalog's min/max range (60-168 BPM) before applying the same formula.

**Step 3: Apply categorical bonuses**
- Add `genre_bonus` (0.05) if `song["genre"] == user["favorite_genre"]`
- Add `mood_bonus` (0.05) if `song["mood"]` is in `user["acceptable_moods"]`

**Step 4: Compute the weighted total**

```
score = (energy       x 0.30)
      + (valence      x 0.20)
      + (tempo        x 0.15)
      + (acousticness x 0.15)
      + (danceability x 0.10)
      + genre_bonus
      + mood_bonus
```

Weights sum to 1.0. Energy is weighted highest because it most strongly determines the overall vibe.

**Step 5: Rank and return**
Sort all (song, score, reasons) tuples by score descending and slice the top K results.

### Potential Biases

| Bias | Description |
|---|---|
| **Energy dominance** | With a 0.30 weight, energy is the single biggest driver. A song that perfectly matches every other feature but misses on energy will still score poorly. |
| **Genre sparsity** | Most genres appear only once in the 20-song catalog. A genre match is effectively a pointer to a single song, which means the genre bonus disproportionately benefits whichever one song fits the label. |
| **Mood label subjectivity** | Mood labels ("chill", "focused", "relaxed") are manually assigned and culturally subjective. Two songs that feel identical to a listener may carry different labels and score differently. |
| **No feedback loop** | The system has no way to learn from skips, replays, or saves. A user who hates the top recommendation gets the same result every time. |
| **Single-profile design** | Scores are computed for one user at a time with no collaborative signal. Niche or unusual taste profiles are served just as well (or as poorly) as common ones. |

The screenshots below show the output for three profiles: High-energy pop, chill lofi, and deep intense rock.

![screenshot of output](assets/screenshot.png)
![alt text](assets/screenshot2.png)

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

**Contradictory profile: high energy plus sad mood**
A profile was built with a high energy target (0.9) but with "sad" as the only acceptable mood. Every sad song in the catalog has low energy. The system always ranked loud, aggressive tracks above the sad songs because the energy gap was too large for the 5% mood bonus to overcome. The mood preference was completely overridden by the energy weight.

**Missing genre: favorite genre not in catalog**
A profile was set with `favorite_genre` set to "bossa-nova", a genre that does not appear in any song. The system ran without errors and returned five results. The genre bonus was never awarded and the 5% weight was silently wasted. There was no warning.

**Zero weights: all weights set to 0.0**
Setting every weight to 0.0 caused every song to score 0.0. The top five results were returned in catalog order (song id 1, 2, 3...) because Python's sort is stable and preserves insertion order when scores are equal. The system did not raise an error or signal that the output was meaningless.

**Invisible songs: comparing all three profiles at once**
After running all three standard profiles and collecting their top-five lists, seven out of twenty songs never appeared in any list. These included jazz, classical, reggae, soul, and folk tracks. The songs were not bad. They just did not fit the shape of any of the three defined profiles. A real system would need a way to surface these songs to users who might enjoy them.

**Oversized weights: weights that sum to more than 1.0**
Setting every weight to 0.5 caused a perfect-match song to score above 1.0. The bar chart in the output (built from `"#" * round(score * 20)`) grew to over 50 characters. No error was raised. The system accepted the input and produced visually broken output.

---

## Limitations and Risks

The catalog has only 20 songs across 17 genres. Most genres have a single representative song. A genre fan cannot discover new music within their genre because there is nothing else to find.

Energy carries 30% of the total score. It acts as a pre-filter that sorts the entire catalog before any other preference is considered. Users with unusual or contradictory taste profiles will get recommendations that satisfy the energy target but may ignore everything else they care about.

The mood and genre bonuses together are only 10% of the total score. They are too small to rescue a song that is off on energy, even if that song matches perfectly on every other dimension.

The system has no feedback loop. Skips, replays, and saves are not tracked. A user who dislikes every recommendation will see the same results every time they run the system.

Genre matching uses exact string comparison. "Pop" and "indie pop" are treated as completely unrelated. Songs that a user would genuinely enjoy across genre boundaries are systematically penalized.

See [model_card.md](model_card.md) for a deeper discussion of limitations and bias.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

### Profile Pair Comparisons

**High-Energy Pop vs. Chill Lofi**

These two profiles have identical weight structures. The only thing that differs is what numbers they are aiming for. Despite that, their top-5 lists share zero songs. High-Energy Pop surfaces Sunrise City, Gym Hero, Altitude Drop, Rooftop Lights, and Mango Boulevard, all with energy above 0.75. Chill Lofi surfaces Focus Flow, Library Rain, Midnight Coding, and similarly quiet tracks with energy below 0.45. This makes sense because energy carries the heaviest weight (30%) and acts like a first filter that splits the catalog in two before any other feature matters. The logic is a perfect mirror. A song that scores near the top for one profile scores near the bottom for the other. The system does not treat these as different styles, just different target numbers. That is a reminder that the algorithm has no concept of vibe. It only knows distance.

**High-Energy Pop vs. Deep Intense Rock**

Both profiles want high energy, so their top-5 lists overlap more than any other pair. Songs like Altitude Drop and Gym Hero appear for both. But they diverge sharply on valence (0.85 for pop vs. 0.35 for rock) and on genre and mood. High-Energy Pop rewards happy, euphoric songs. Deep Intense Rock rewards intense and angry ones. A song like Mango Boulevard (festive, latin, high valence) ranks 5th for the pop profile but drops out of the rock top-5 entirely because its cheerful valence clashes with the rock target. Iron Cathedral (metal, angry, energy=0.97) is the flip side. It is nearly invisible to the pop listener because its low valence and low danceability hurt its score, but it is much more competitive for the rock profile. The rock profile also puts more weight on tempo (20% vs. 15%), which is why faster songs like Iron Cathedral and Storm Runner climb higher in that list specifically.

**Chill Lofi vs. Deep Intense Rock**

These profiles sit at opposite ends of every feature axis. Low vs. high energy, acoustic vs. electric, slow vs. fast tempo. Their top-5 lists have no overlap at all. Chill Lofi's recommendations are dominated by lofi and ambient tracks with high acousticness scores. Deep Intense Rock's list is dominated by metal and rock tracks with near-zero acousticness. The catalog itself shapes this outcome significantly. Lofi has three songs, so the Chill Lofi profile gets multiple lofi matches near the top. Rock has only one song (Storm Runner), so even though it earns the full genre bonus, the rest of the list fills in with non-rock songs like Iron Cathedral and Altitude Drop. A rock fan would notice that their playlist is mostly metal and EDM. Accurate on audio features, but not the same as actually being rock.

### Personal Reflection

**What was your biggest learning moment?**

The biggest moment was discovering that 7 out of 20 songs never appeared in any top-5 list across all three profiles. Those songs were not flawed. They were just caught between profiles, close enough to none of them to ever rank. That showed me something important: a recommender does not have to be wrong to be unfair. It can be working exactly as designed and still leave a large part of the catalog invisible to every user. The bias was not in the code. It was in the weight choices and the narrow set of profiles.

**How did using AI tools help, and when did you need to double-check them?**

AI tools were useful for generating adversarial test cases quickly and for walking through the math of the scoring formula to find edge cases I would not have thought to test on my own. The zero-weight edge case and the tempo-out-of-range bug came directly from that kind of systematic analysis. But I always needed to run the actual code to confirm what the analysis predicted. A few times the reasoning about which song would rank where turned out to be off because of interactions between multiple features that were not obvious until the numbers were computed. The tool helped me ask better questions. The code gave me the real answers.

**What surprised you about how a simple algorithm can still feel like a recommendation?**

The scoring formula is just subtraction and multiplication. There is no concept of music in it at all. But the High-Energy Pop profile really does return a list that sounds like a high-energy pop playlist, and the Chill Lofi profile really does return something you could study to. That surprised me. The math captures something real about musical similarity, not because it understands music, but because the features chosen (energy, tempo, acousticness) happen to line up with how humans describe the feel of a song. The algorithm feels smart because the features are well chosen, not because the algorithm itself is doing anything clever.

**What would you try next if you extended this project?**

The first thing I would change is the catalog size. Most genres have one song, which means genre-based exploration is impossible. Adding at least five songs per genre would make the recommendations feel much more useful for niche listeners. I would also add a diversity rule so the top five cannot all cluster at the same energy level. Right now the results often feel repetitive because the highest-scoring songs tend to share similar audio profiles. Finally, I would try partial genre matching so that "pop" and "indie pop" are treated as related rather than completely separate. That single change would open up a lot of cross-genre discovery that the current system blocks entirely.
