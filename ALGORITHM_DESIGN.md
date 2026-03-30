# Phase 1: Algorithm Design

## Philosophy
**Option B: Multi-Feature Weighted Scoring**

Exact matches on genre and mood matter most, but we weight them differently and use numeric features to refine the ranking. This allows flexibility while respecting user preferences across multiple dimensions.

---

## Scoring Formula

For each song, calculate a **total score** based on:

### 1. Genre Match → **+50 points**
- If `song.genre == user.favorite_genre` → award 50 points
- Otherwise → award 0 points
- (Exact match only; no partial credit)

### 2. Mood Match → **+30 points**
- If `song.mood == user.favorite_mood` → award 30 points
- Otherwise → award 0 points
- (Exact match only; no partial credit)

### 3. Energy Similarity → **+35 points**
- If `|song.energy - user.target_energy| ≤ 0.3` → award 35 points
- Otherwise → award 0 points
- (Energy weighted heavily since user prefers this)

### 4. Acousticness Preference → **+10 points**
- If `user.likes_acoustic == True` AND `song.acousticness > 0.7` → award 10 points
- OR if `user.likes_acoustic == False` AND `song.acousticness < 0.3` → award 10 points
- Otherwise → award 0 points

### **Final Score = Sum of all points (max 125)**

**Ranking:** Sort songs by score descending. Return top-k songs.

---

## Weight Justification

| Feature | Weight | Reasoning |
|---------|--------|-----------|
| Genre | 50 | Primary signal; user explicitly stated preference |
| Energy | 35 | User emphasized "energy is more important"; weighted nearly equal to genre |
| Mood | 30 | Important but less critical than genre/energy |
| Acousticness | 10 | Bonus/refinement; binary preference |

---

## Example Calculations

### User Profile 1: "pop + happy + energetic + NOT acoustic"
- `favorite_genre` = "pop"
- `favorite_mood` = "happy"
- `target_energy` = 0.80
- `likes_acoustic` = False

#### Song #1 (Sunrise City)
- Genre (pop): ✓ → +50
- Mood (happy): ✓ → +30
- Energy (0.82 vs 0.80): |0.82 - 0.80| = 0.02 ≤ 0.3 ✓ → +35
- Acousticness (0.18 < 0.3, doesn't like acoustic): ✓ → +10
- **Total: 125/125** ⭐

#### Song #5 (Gym Hero)
- Genre (pop): ✓ → +50
- Mood (intense vs happy): ✗ → +0
- Energy (0.93 vs 0.80): |0.93 - 0.80| = 0.13 ≤ 0.3 ✓ → +35
- Acousticness (0.05 < 0.3, doesn't like acoustic): ✓ → +10
- **Total: 95/125** (good, but mood mismatch hurts)

#### Song #2 (Midnight Coding)
- Genre (lofi vs pop): ✗ → +0
- Mood (chill vs happy): ✗ → +0
- Energy (0.42 vs 0.80): |0.42 - 0.80| = 0.38 > 0.3 ✗ → +0
- Acousticness (0.71 > 0.3, but doesn't like acoustic): ✗ → +0
- **Total: 0/125** (no match)

### User Profile 2: "lofi + chill + acoustic"
- `favorite_genre` = "lofi"
- `favorite_mood` = "chill"
- `target_energy` = 0.35
- `likes_acoustic` = True

#### Song #2 (Midnight Coding)
- Genre (lofi): ✓ → +50
- Mood (chill): ✓ → +30
- Energy (0.42 vs 0.35): |0.42 - 0.35| = 0.07 ≤ 0.3 ✓ → +35
- Acousticness (0.71 > 0.7, likes acoustic): ✓ → +10
- **Total: 125/125** ⭐

#### Song #4 (Library Rain)
- Genre (lofi): ✓ → +50
- Mood (chill): ✓ → +30
- Energy (0.35 vs 0.35): |0.35 - 0.35| = 0.0 ≤ 0.3 ✓ → +35
- Acousticness (0.86 > 0.7, likes acoustic): ✓ → +10
- **Total: 125/125** ⭐

---

## Key Insights

1. **Energy threshold of 0.3** allows reasonable flexibility without being too loose
2. **Genre + Energy combination** is powerful—they together account for 85 of 125 points
3. **Mood mismatches** can significantly hurt a song (see Song #5 example)
4. **Acousticness** acts as a refinement; it's the only bonus that doesn't apply to every preference type
