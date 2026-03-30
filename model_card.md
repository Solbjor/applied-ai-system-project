# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**ContentMatch v1.0** — A weighted, content-based music recommender system

---

## 2. Intended Use  

Classroom exploration tool for content-based recommendation algorithms. Generates song recommendations (from 10 songs) based on 4 user taste dimensions: genre, mood, energy, and acoustic preference. **Not suitable for real-world deployment.**

---

## 3. How the Model Works  

Scores each song (max 125 points) by matching user taste:
- **Genre match:** +35 (exact match) or 0
- **Mood match:** +40 (exact match) or 0  
- **Energy match:** +40 (within ±0.3 of target) or 0
- **Acousticness match:** +10 (>0.7 if acoustic preference, <0.3 if not) or 0

Returns top-5 songs ranked by score with reason breakdown.

---

## 4. Data  

**Dataset:** 10 songs from `data/songs.csv` across 7 genres (Pop 2, Lofi 3, Rock 1, Ambient 1, Jazz 1, Synthwave 1, Indie Pop 1)

**Limitations:** Very limited genre representation; missing reggae, hip-hop, electronic, metal, country, R&B, etc. Rock fans get 1 recommendation; electronic fans get 0.

---

## 5. Strengths  

- **Transparent:** Every recommendation shows point breakdown and reasons
- **Reasonable for mainstream tastes:** Pop, lofi, ambient users get expected results
- **Non-genre-veto:** Songs can score 50-90 without genre match through mood+energy alignment
- **Captures vibe:** Energy and acousticness matter equally to genre

---

## 6. Limitations and Bias 

**6 Key Biases Identified:**

1. **Binary Energy:** Full credit (±0.3) or zero; no partial credit for close misses
2. **Genre Dominance:** Rock fans get 1 song, electronic fans get 0—limited diversity for niche tastes
3. **No Genre Similarity:** Pop ≠ Indie Pop despite being musically adjacent
4. **Acousticness Hard Thresholds:** Song at 0.69 gets 0 points; 0.71 gets 10 (cliff effect)
5. **Dataset Size:** Only 10 songs can't serve diverse preferences
6. **Weight Disparity:** Acousticness becomes 8-20% of score depending on match quality

---

## 7. Evaluation  

**Testing Summary:**
- **Pop Lover (pop+happy+0.8 energy+not acoustic):** Sunrise City ranked #1 at 125/125 ✓
- **Lofi Listener (lofi+chill+0.35 energy+acoustic):** Midnight Coding ranked #1 at 125/125 ✓  
- **Rock Fan (rock+intense+0.85 energy+not acoustic):** Storm Runner ranked #1 but limited fallback options
- **Genre Veto Test:** Reggae user got 50-90 point songs despite genre mismatch (shows no hard veto)
- **Acousticness Impact:** Same user with flipped preference showed 8-10 point swing

For detailed test results, see [PHASE4_EVALUATION.md](PHASE4_EVALUATION.md).

---

## 8. Future Work  

**High Priority:** Expand dataset to 100+ songs, gradient energy scoring, genre similarity map  
**Medium Priority:** Continuous acousticness scale, fix weight disparity, multi-seed preferences  
**Long Term:** Collaborative filtering, exploration (discovery), temporal mood patterns
