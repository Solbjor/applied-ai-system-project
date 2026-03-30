# Phase 4: Evaluation & Bias Analysis

## Executive Summary

Testing the recommender system across 3+ user profiles revealed:
- ✅ **Works well** when user's genre exists in dataset
- ⚠️ **Limitations** when genre is niche or missing
- ⚠️ **Binary energy scoring** (all-or-nothing, not gradual)
- ⚠️ **Small dataset** limits diversity

---

## Test Results

### Test 1: Pop Lover (High Energy)
**Profile:** pop + happy + high energy (0.8) + NOT acoustic

**Ranking:**
1. **Sunrise City** - Score: 125/125 ⭐
   - Reasons: Genre match (+35) · Mood match (+40) · Energy match (+40) · Not acoustic (+10)
   - Perfect score—matches all criteria

2. **Gym Hero** - Score: 85/125
   - Why it ranks 2nd: Has genre + energy match, but mood is "intense" not "happy" (-40 points)
   - Mood mismatch creates significant score gap

3. **Rooftop Lights** - Score: 80/125
   - Why it ranks 3rd: No genre match (indie pop ≠ pop), but mood + energy both match
   - Shows that energy + mood can compensate for genre mismatch

4-5. **Storm Runner, Night Drive Loop** - Score: 50/125
   - Energy only (no genre/mood match); minimal scores

**Key Insight:** Top recommendation is obvious and correct. The algorithm works as designed when the genre exists in the dataset.

---

### Test 2: Lo-Fi Listener (Chill & Acoustic)
**Profile:** lofi + chill + low energy (0.35) + LIKES acoustic

**Ranking:**
1-2. **Midnight Coding & Library Rain** - Score: 125/125 ⭐⭐
   - Both are perfect matches (genre + mood + energy + acoustic all aligned)
   - This is the "best case scenario"

3. **Spacewalk Thoughts** - Score: 90/125
   - Genre mismatch (ambient ≠ lofi), but mood + energy + acoustic match
   - Score: 0 genre + 40 mood + 40 energy + 10 acoustic = 90

4. **Focus Flow** - Score: 85/125
   - Genre + energy match, but mood is "focused" not "chill"
   - Score: 35 genre + 0 mood + 40 energy + 10 acoustic = 85

5. **Coffee Shop Stories** - Score: 50/125
   - Energy + acoustic only; jazz genre and relaxed mood don't match

**Key Insight:** Perfect matches exist in this case. But notice Song #3 (Spacewalk Thoughts) scores high (90) even without the exact genre—mood + energy + acoustic carry it.

---

### Test 3: Rock Fan (High Energy, Not Acoustic)
**Profile:** rock + intense + high energy (0.9) + NOT acoustic

**Ranking:**
1. **Storm Runner** - Score: 125/125 ⭐
   - Perfect match: rock + intense + high energy (0.91) + not acoustic
   - This is the ONLY rock song in dataset, so it dominates

2. **Gym Hero** - Score: 90/125
   - Mood match (intense) + energy match, but genre is pop not rock
   - Score: 0 genre + 40 mood + 40 energy + 10 acoustic = 90

3. **Sunrise City** - Score: 50/125
   - Only energy match; genre and mood don't align
   - Shows a user who likes a rare genre gets limited options

**Key Insight:** Limited dataset emerges as a real problem. Rock is rare (1 song); users interested in rock get disappointed outside of that one perfect match.

---

## Experiments

### Experiment 1: Genre Veto vs. Other Features
**Question:** Can energy + mood compensate for missing genre?

**Test Profile:** reggae (NOT in dataset) + happy + high energy (0.8)

**Results:**
- **#1: Sunrise City** - Score: 90/125 (pop, not reggae!)
  - 0 genre + 40 mood (happy matches) + 40 energy + 10 acoustic = 90
- **#2: Rooftop Lights** - Score: 80/125 (indie pop, not reggae!)
- **#3: Storm Runner** - Score: 50/125

**Observation:** Songs without reggae still score well! The algorithm doesn't completely veto based on genre. Energy + mood can carry recommendations.

**Implication:** Users interested in niche genres can still get decent recommendations through other criteria—but they'd prefer more songs of their favorite genre.

---

### Experiment 2: Acoustic Preference Bias
**Question:** How much does acousticness factor matter?

**Same Profile, Different Acoustic Preferences:**
- Same user: lofi + chill + low energy (0.35)

**A) User LIKES acoustic:**
| Song | Score |
|------|-------|
| Midnight Coding | 125/125 |
| Library Rain | 125/125 |
| Spacewalk Thoughts | 90/125 |

**B) Same user DISLIKES acoustic:**
| Song | Score |
|------|-------|
| Midnight Coding | 115/125 (-10) |
| Library Rain | 115/125 (-10) |
| Spacewalk Thoughts | 80/125 (-10) |

**Key Observation:** Acousticness adds/removes 10 points (8% of max), BUT:
- When genre/mood/energy **all match**, acousticness is a minor tiebreaker
- When genre/mood don't match, acousticness becomes 20% of the score—suddenly important!

---

## Identified Biases & Limitations

### **BIAS 1: Genre as "Primary Signal"**
- Genre match = +35 points (28% of total)
- When genre doesn't match, users must rely on other features
- **Problem:** Some genres are rare in dataset (e.g., rock = 1 song)
- **Workaround:** Add similar-genre matching (pop ≈ indie pop; rock ≈ synthwave)

### **BIAS 2: Energy Scoring is Binary (All-or-Nothing)**
- Current: Energy within 0.3 = +40; outside 0.3 = +0
- **Problem:** Energy 0.30 gets same +40 as energy 0.80 (huge difference!)
- **Better approach:** Gradual scoring
  ```
  energy_score = (1 - |diff|/0.3) * 40  if |diff| ≤ 0.3 else 0
  ```
  This would give partial credit for "close" energy values

- **Real-world impact:** User prefers energy 0.8, song at 0.31 gets 0 points even though they're only 0.01 away

### **BIAS 3: Acousticness Asymmetry**
- Acousticness bonus (+10) is much smaller than other features
- **Problem:** For low-scoring songs, acousticness becomes disproportionately important
- **Example:** Song with no genre/mood match but high acousticness scores 20/125 vs 10/125
- **Impact:** Might over-reward acoustic songs in tie-breaking scenarios

### **BIAS 4: Limited Dataset (10 Songs, 7 Genres)**
- Only 1 rock song, 3 lofi, 2 pop
- **Problem:** Users interested in rock will only see 1 perfect match
- **Real-world:** Spotify has 100M songs; millions per genre
- **Impact:** Our recommender can't diversify recommendations for niche tastes

### **BIAS 5: No "Similar Genre" Recognition**
- Pop ≠ Indie Pop (even though they're related)
- Rock ≠ Synthwave (even though both are high-energy electronic-ish)
- **Problem:** Strict exact matching misses related genres
- **Fix:** Add genre similarity scoring (e.g., "pop" matches "indie pop" at 50%)

---

## What the Recommender Gets Right ✅

1. **Explains why a song ranked high** — Users understand: "Genre + mood + energy all matched"
2. **Doesn't completely veto non-matching genres** — Energy + mood can carry recommendations
3. **Produces sensible top-N rankings** — #1 is always justified by user profile
4. **Transparent scoring breakdown** — "Genre match (+35) · Mood match (+40)..." is clear

---

## What Needs Improvement ⚠️

1. **Make energy scoring gradual** (not binary)
2. **Add genre similarity** (not exact-match only)
3. **Increase dataset size** (or acknowledge small sample limitation)
4. **Consider energy preference more carefully** (0.3 threshold might be too loose)
5. **Rebalance acousticness weight** (currently 10 points seems arbitrary)

---

## Unexpected Results & Learnings

### Result 1: Genre Mismatch Doesn't Break Everything
**Expected:** User who likes reggae (not in dataset) would get terrible recommendations
**Actual:** They still get songs scoring 50-90 through energy + mood matches
**Learning:** The algorithm is more robust than expected; multi-feature approach helps

### Result 2: Acoustic Preference Changes Rankings Less Than Expected
**Expected:** Acoustic preference would significantly reorder top-5
**Actual:** When genre/mood/energy match perfectly, acoustic only changes score by 10 points
**Learning:** Binary acousticness (>0.7 or <0.3) might be too strict; could use continuous scale

### Result 3: Rock Fans Get Limited Choices
**Expected:** Rock + intense + high energy would get 3-4 good recommendations
**Actual:** Only 1 rock song exists (perfect match), then must fall back to pop/synthwave
**Learning:** Small dataset is a real bottleneck; algorithm can't overcome this

---

## Recommendations for Improvement

### Short Term (Tweaks)
- [ ] Make energy scoring gradual instead of binary
- [ ] Add genre similarity dictionary (pop ↔ indie pop, rock ↔ synthwave)
- [ ] Expand CSV to 30-50 songs across more genres

### Medium Term (Enhancements)  
- [ ] Use continued acousticness scale (0.0-1.0) instead of binary threshold
- [ ] Add user feedback loop (user rates recommendations, system learns)
- [ ] Implement collaborative filtering (what similar users liked)

### Long Term (Architecture)
- [ ] Real dataset integration (Spotify API)
- [ ] Deep learning-based embeddings for song similarity
- [ ] A/B testing with real users

---

## Conclusion

The recommender succeeds at its core goal: **transparent, explainable recommendations based on user taste**. However, it reveals real limitations of simplistic content-based filtering:
- Natural language complexity (genres, moods, emotions) doesn't reduce to 4 features
- Binary thresholds (energy 0.3, acousticness >0.7) are overly rigid
- Small datasets can't serve niche preferences

This mirrors real-world recommender challenges: **no algorithm is perfect without more data, user feedback, and nuance.**

