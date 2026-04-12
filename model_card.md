# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**FeatureMatch 1.0**

---

## 2. Intended Use  

This recommender suggests up to five songs from a small catalog based on a user's taste profile. The profile describes what kind of song the user wants: how energetic, how fast, how happy-sounding, how acoustic, and how danceable. It also includes a favorite genre and a list of moods the user is okay with.

The system assumes users can describe their taste as numbers. It does not learn from listening history or skips. It is designed for classroom exploration, not for real users or a production app.

---

## 3. How the Model Works  

Each song in the catalog has five numbers attached to it: energy, valence (how positive it sounds), tempo, acousticness, and danceability. It also has a genre label and a mood label.

The user provides a target value for each of those five numbers. For every song, the system asks: how close is this song to what the user wants? A song that is very close to the target on every feature gets a high score. A song that is far off gets a low score. The formula is simple: start at 1.0 and subtract the gap between the target and the actual value. A perfect match gets 1.0 on that feature. A big mismatch gets something closer to 0.

Not every feature counts equally. Energy is weighted most heavily at 30%. Valence is next at 20%. Tempo and acousticness are each 15%. Danceability is 10%. If the song's genre matches the user's favorite, a small bonus of 5% is added. If the mood matches, another 5% bonus is added. All the weighted pieces are added together to get the final score. Songs are then sorted from highest to lowest and the top five are returned.

---

## 4. Data  

The catalog has 20 songs stored in a file called songs.csv. Each song has an id, a title, an artist, a genre, a mood, and five numeric features measured on a 0 to 1 scale (except tempo, which is in beats per minute).

Seventeen different genres are represented, including pop, lofi, rock, metal, jazz, classical, reggae, soul, and folk. Most genres appear only once. Lofi is the most represented with three songs. Moods include happy, chill, focused, intense, angry, sad, melancholic, romantic, confident, and a few others.

No songs were added or removed from the starter dataset. What is missing: there are no lyrics, no release year, no artist popularity data, and no information about language or cultural origin. The catalog skews toward genres common in Western streaming platforms. A listener whose taste falls outside those genres has very little to work with.

---

## 5. Strengths  

The system works best when a user's taste is consistent and matches the catalog well. The high-energy pop profile and the chill lofi profile both returned playlists that felt right. The top songs genuinely matched the energy, mood, and genre targets those profiles described.

Every recommendation can be explained. The system reports which features were closest and whether a genre or mood bonus was earned. There is no hidden logic. This makes it easy to understand why a specific song ranked where it did.

The system is also fast and predictable. The same profile always returns the same results. For a classroom setting where the goal is to understand how scoring works, that transparency is useful.

---

## 6. Limitations and Bias 

**Energy dominates everything else.**
The scoring system assigns 30% of the total score to a single feature, energy, which is six times larger than the weight given to mood preference (5%). In practice, this means that a song with the right mood will still lose to a song with the wrong mood if their energy levels differ by more than about 0.17 on a 0 to 1 scale. During testing, a profile that asked for high-energy and sad songs consistently ranked loud, aggressive tracks above quiet, melancholic ones. This was the opposite of what the mood preference implied. The entire catalog gets quietly pre-sorted by energy before genre, mood, or any other preference is considered. Users with niche or contradictory tastes may never see songs that would actually suit them.

**Most genres have only one song.**
When the catalog has just one jazz song or one classical song, a genre match is not really a recommendation. It is just a pointer to a single track. A jazz fan cannot discover other jazz songs because none exist. After that one song, the recommendations fill in with whatever audio features are closest, which usually means lofi or ambient tracks.

**Genre matching is all or nothing.**
A pop fan gets no credit for indie pop. A rock fan gets no credit for metal, even though they share almost the same sound profile. Related genres are treated as completely unrelated. This makes it harder for the system to recommend songs that a user would genuinely enjoy across genre boundaries.

**Seven out of twenty songs are never recommended.**
Running all three defined profiles reveals that songs in jazz, classical, reggae, soul, folk, hip-hop, and r&b never appear in any top-five list. These songs are not bad. They just do not fit the shape of any of the three profiles. With no feedback loop and no way to expand the profile set, those songs are permanently invisible.

---

## 7. Evaluation  

Three standard profiles were tested first: a high-energy pop listener, a chill lo-fi listener, and a deep intense rock listener. For each one, the goal was to check whether the top five results felt like a coherent playlist for that person. Then a set of stress-test profiles were added to find edge cases. These included a listener who wanted high energy and sad songs at the same time, a jazz fan, a listener whose favorite genre did not appear in the catalog, and a profile where all the preference weights were set to zero.

Two results were genuinely surprising. First, running all three standard profiles together showed that seven out of twenty songs never appeared in anyone's top five. They did not fit neatly into any defined profile. Second, the contradictory profile (high energy plus sad mood) never once recommended a sad song. The system ranked loud tracks above quiet, melancholic ones because the energy numbers matched better. The mood preference was simply too small to override. This showed clearly that the scoring system is a math problem. If the numbers favor one song, that song wins, regardless of what the mood label says.

---

## 8. Future Work  

The most important fix would be reducing the gap between energy's weight and the other features. Energy at 30% acts like a filter that decides the results before other features get a chance to contribute. Giving mood a weight closer to energy would let it actually influence recommendations.

Adding more songs per genre would help a lot. Right now a jazz fan or a classical fan has at most one matching song. A real improvement would be expanding the catalog so that every genre has at least five songs.

Genre matching could be made smarter. Instead of requiring an exact string match, related genres like pop and indie pop, or rock and metal, could be grouped together so a partial bonus is awarded even when the genre is not identical.

A diversity rule would prevent the top five from all being the same type of song. Right now if five songs cluster near the same energy and tempo, they all score similarly and fill the entire top-five. Spacing out the results by genre or mood would make the recommendations feel more like a real playlist.

Finally, adding a feedback mechanism so that skipped or replayed songs update the profile targets would move the system closer to how real recommenders actually work.

---

## 9. Personal Reflection  

Building this made it clear that a recommender is not magic. It is a scoring formula with weights. The system does not know what sounds good. It only knows how far each song is from a set of target numbers. That realization changes how I think about Spotify or YouTube recommendations. Those systems are much more complex, but at their core they are doing something similar: turning listening behavior into numbers and finding other content that is close to those numbers.

The most unexpected thing was how many songs disappeared. Seven out of twenty songs were never recommended to anyone. The system was not broken. It was working exactly as designed. But the design was narrow enough that a third of the catalog became invisible. That felt unfair in a way that was hard to notice from looking at the code alone. You only see it when you look at what is missing.

This project also showed that bias in an AI system does not have to be intentional. Nobody decided that jazz fans should get bad recommendations. It happened because the catalog was small and the weight on energy was large. Small design choices, made for reasonable reasons, can add up to outcomes that seem unfair once you look at the full picture.
