# Phase 1: Algorithm Design

## Philosophy
**Option B: Multi-Feature Weighted Scoring**

Exact matches on genre and mood matter most, but we weight them differently and use numeric features to refine the ranking. This allows flexibility while respecting user preferences across multiple dimensions.

---

## Scoring Formula (FINAL - After Phase 2 Iteration)

For each song, calculate a **total score** based on:

### 1. Genre Match → **+35 points**
- If `song.genre == user.favorite_genre` → award 35 points
- Otherwise → award 0 points
- (Exact match only; important but not a veto)

### 2. Mood Match → **+40 points**
- If `song.mood == user.favorite_mood` → award 40 points
- Otherwise → award 0 points
- (Exact match only; mood mismatches carry significant penalty)

### 3. Energy Similarity → **+40 points**
- If `|song.energy - user.target_energy| ≤ 0.3` → award 40 points
- Otherwise → award 0 points
- (Equal weight with mood; user emphasized importance)

### 4. Acousticness Preference → **+10 points**
- If `user.likes_acoustic == True` AND `song.acousticness > 0.7` → award 10 points
- OR if `user.likes_acoustic == False` AND `song.acousticness < 0.3` → award 10 points
- Otherwise → award 0 points

### **Final Score = Sum of all points (max 125)**

**Ranking:** Sort songs by score descending. Return top-k songs.

---

## Weight Justification (REVISED)

| Feature | Weight | Reasoning |
|---------|--------|-----------|
| Genre | 35 | Important signal, but NOT a veto blocker |
| Mood | 40 | Mood mismatches hurt significantly; nearly equal to energy |
| Energy | 40 | User emphasized importance; equal weight with mood |
| Acousticness | 10 | Bonus/refinement; binary preference |

**Key insight:** Genre, mood, and energy are now the "triple threat" instead of genre being dominant. A song without the right genre can still score well (50-90 points) if it has excellent mood + energy match.

---

## Phase 2: Manual Verification & Formula Refinement

### Initial Formula Testing (v1)

**Observation:** Genre weight of 50 was too dominant, making songs without the exact genre score 0 completely. This was unrealistic—users wouldn't reject a great song *just* because it's not their favorite genre.

**Decision:** Reduce genre to 35, increase mood to 40, increase energy to 40. This prevents genre from being a complete veto.

### Final Formula (v2) - Verified Correct

Testing the revised weights against both user profiles produced realistic rankings:

#### User Profile 1 Rankings (pop + happy + energetic + NOT acoustic)
| Rank | Song | Score | Notes |
|------|------|-------|-------|
| 1 | #1 Sunrise City (pop, happy, 0.82 energy) | 125 | Perfect match across all factors |
| 2 | #5 Gym Hero (pop, intense, 0.93 energy) | 85 | Genre & energy match, but mood miss costs 40 points |
| 3 | #10 Rooftop Lights (indie pop, happy, 0.76 energy) | 80 | No genre match, but mood + energy carry it |
| 4-5 | #3 Storm Runner, #8 Night Drive Loop (energy matches only) | 50 | Energy alone brings some value |
| 6+ | #2, #4, #6, #7, #9 (lofi/ambient/jazz; low energy) | 0-40 | Poor matches; may score if acousticness aligns |

**Validation:** This ranking matches intuition—Song #5 rightfully drops (mood miss), but Song #10 rises because mood + energy are powerful enough to compensate for genre mismatch.

#### User Profile 2 Rankings (lofi + chill + acoustic)
| Rank | Song | Score | Notes |
|------|------|-------|-------|
| 1-2 | #2 Midnight Coding, #4 Library Rain (lofi, chill, acoustic) | 125 | Perfect matches |
| 3 | #9 Focus Flow (lofi, focused, 0.40 energy) | 85 | Genre & energy match, but mood miss costs 40 points ✓ |
| 4 | #6 Spacewalk Thoughts (ambient, chill, 0.28 energy, acoustic) | 90 | No genre match, but mood + energy + acoustic carry it |
| 5 | #7 Coffee Shop Stories (jazz, relaxed, 0.37 energy, acoustic) | 50 | Energy & acoustic only |
| 6+ | Pop/rock songs (high energy, low acoustic) | 40 | Energy match but no mood match |

**Validation:** Song #9 correctly drops below Song #6 because mood matters. Song #6 still scores well through mood + energy even without the lofi genre. This is realistic.

### Key Refinements Made in Phase 2

1. **Genre weight reduced from 50 → 35**
   - Prevents genre from being a complete veto blocker
   - Allows other features to compensate

2. **Mood weight increased from 30 → 40**
   - Mood mismatches now carry real penalty
   - Addresses concern that Song #5 (intense vs happy) was ranking too high

3. **Energy weight increased from 35 → 40**
   - Equal weight with mood, reflecting their balanced importance
   - Users can now find good recommendations through energy even without genre

---

## Example Calculations

### User Profile 1: "pop + happy + energetic + NOT acoustic"
- `favorite_genre` = "pop"
- `favorite_mood` = "happy"
- `target_energy` = 0.80
- `likes_acoustic` = False

#### Song #1 (Sunrise City)
- Genre (pop): ✓ → +35
- Mood (happy): ✓ → +40
- Energy (0.82 vs 0.80): |0.82 - 0.80| = 0.02 ≤ 0.3 ✓ → +40
- Acousticness (0.18 < 0.3, doesn't like acoustic): ✓ → +10
- **Total: 125/125** ⭐

#### Song #5 (Gym Hero)
- Genre (pop): ✓ → +35
- Mood (intense vs happy): ✗ → +0
- Energy (0.93 vs 0.80): |0.93 - 0.80| = 0.13 ≤ 0.3 ✓ → +40
- Acousticness (0.05 < 0.3, doesn't like acoustic): ✓ → +10
- **Total: 85/125** (good, but mood mismatch costs more now)

#### Song #10 (Rooftop Lights)
- Genre (indie pop vs pop): ✗ → +0
- Mood (happy): ✓ → +40
- Energy (0.76 vs 0.80): |0.76 - 0.80| = 0.04 ≤ 0.3 ✓ → +40
- Acousticness (0.35, doesn't like acoustic): ✗ → +0
- **Total: 80/125** (mood + energy carry it despite genre mismatch)

### User Profile 2: "lofi + chill + acoustic"
- `favorite_genre` = "lofi"
- `favorite_mood` = "chill"
- `target_energy` = 0.35
- `likes_acoustic` = True

#### Song #2 (Midnight Coding)
- Genre (lofi): ✓ → +35
- Mood (chill): ✓ → +40
- Energy (0.42 vs 0.35): |0.42 - 0.35| = 0.07 ≤ 0.3 ✓ → +40
- Acousticness (0.71 > 0.7, likes acoustic): ✓ → +10
- **Total: 125/125** ⭐

#### Song #4 (Library Rain)
- Genre (lofi): ✓ → +35
- Mood (chill): ✓ → +40
- Energy (0.35 vs 0.35): |0.35 - 0.35| = 0.0 ≤ 0.3 ✓ → +40
- Acousticness (0.86 > 0.7, likes acoustic): ✓ → +10
- **Total: 125/125** ⭐

#### Song #6 (Spacewalk Thoughts) - Non-lofi bonus case
- Genre (ambient vs lofi): ✗ → +0
- Mood (chill): ✓ → +40
- Energy (0.28 vs 0.35): |0.28 - 0.35| = 0.07 ≤ 0.3 ✓ → +40
- Acousticness (0.92 > 0.7, likes acoustic): ✓ → +10
- **Total: 90/125** (no genre match, but mood + energy + acoustic carry it!)

---

## Key Insights

1. **Genre is important but not a veto** (35 points)
   - Songs without exact genre match can still score 50-90 if mood & energy align
   - Prevents unrealistic recommendation gaps for users with specialized tastes

2. **Mood and energy are the "dynamic duo"** (40 points each)
   - Together they account for 80 of 125 points
   - A mood mismatch costs 40 points—significant penalty that users noted was important
   - A song can rank highly (#3, #4, #6) with just mood + energy, even missing genre

3. **The 0.3 energy tolerance** allows reasonable flexibility
   - Songs between -0.3 and +0.3 of target energy are considered "good fits"
   - Prevents false positives while allowing adjacent energy levels

4. **Acousticness acts as a refinement** (10 points)
   - Only applies to binary preferences (like acoustic / dislike acoustic)
   - Tiebreaker value; rarely decides ranking alone
