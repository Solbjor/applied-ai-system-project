# 🎵 Adaptive Music Recommender System

**A production-quality music recommendation engine with built-in learning capabilities.**

This project demonstrates an AI-enhanced recommender system that:
- ✅ Scores songs based on user preferences
- ✅ Provides confidence scores on recommendations
- ✅ Learns from user feedback
- ✅ Adapts weights to improve over time
- ✅ Explains every recommendation

---

## 🚀 Quick Start

### Installation

```bash
# Clone or navigate to the project
cd applied-ai-system-project

# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate
# OR activate (Windows PowerShell)
# venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Run Basic Recommender
```bash
python src/main.py
```

Expected output:
```
Successfully loaded 10 songs from data/songs.csv

================================================================================
🎵 MUSIC RECOMMENDER SIMULATION
================================================================================
User Profile: pop + happy + energy 0.8

1. SUNRISE CITY
   Artist:  Neon Echo
   Score:   125/125
   ...
```

### Run Adaptive Demos
```bash
# See AI features in action
python src/phase1_demo.py

# Compare different algorithms
python src/phase2_ab_test.py
```

---

## 📚 Project Overview

### What It Does

This system recommends music by:

1. **Understanding User Taste** - Captures genre, mood, energy, acoustic preferences
2. **Scoring Songs** - Evaluates each song against user preferences
3. **Ranking Results** - Returns top recommendations with explanations
4. **Learning from Feedback** - Tracks what users like and adapts (NEW!)
5. **Improving Over Time** - Adjusts weights based on feedback accuracy (NEW!)

### Example: How It Works

**User:** Wants pop music, happy mood, high energy (0.8), electronic (not acoustic)

**System Response:**
```
1. SUNRISE CITY - Score: 125/125 (100% confident)
   ✓ Genre match (pop) +35
   ✓ Mood match (happy) +40
   ✓ Energy match (0.82 vs 0.80) +40
   ✓ Electronic match (0.18 acousticness) +10

2. GYM HERO - Score: 85/125 (75% confident)
   ✓ Genre match (pop) +35
   ✓ Energy match (0.93 vs 0.80) +40
   ✓ Electronic match (0.05 acousticness) +10
   ✗ No mood match (intense, not happy) -40

3. ROOFTOP LIGHTS - Score: 80/125 (50% confident)
   ✓ Mood match (happy) +40
   ✓ Energy match (0.76 vs 0.80) +40
   ✗ No genre match (indie pop, not pop) -35
   ✗ No acoustic match required
```

---

## 🧠 AI Features (New!)

### Feature 1: Confidence Scoring

Every recommendation includes a **confidence percentage** (0-100%).

**What it means:**
- Based on how many criteria matched (genre, mood, energy, acoustic)
- Higher confidence = recommender is more certain you'll like it
- Lower confidence = risky recommendation

**Example:**
```
Recommendation with 100% confidence:
  → All 4 criteria match (genre + mood + energy + acoustic)
  → You'll probably like this

Recommendation with 25% confidence:
  → Only 1 criterion matches
  → You might not like this—but it's worth a try
```

**Why it matters:** You know which recommendations are safe vs. experimental.

---

### Feature 2: User Feedback Learning

The system **learns what works** by tracking your actual reactions.

**How it works:**
1. System makes a recommendation
2. You tell it: "I liked that" or "I didn't like that"
3. System records the feedback
4. Over time, learns what kinds of recommendations work

**Feedback Example:**
```python
# User likes a recommendation
system.feedback_on_recommendation(song, user_profile, liked=True)

# User dislikes a recommendation  
system.feedback_on_recommendation(song, user_profile, liked=False)

# Get feedback summary
stats = system.get_system_stats()
# {
#   'accuracy': '85%',  ← Of last 20 recs, 17 were liked
#   'recommendations_liked': 17,
#   'recommendations_disliked': 3,
#   'avg_confidence_when_liked': 82.5,
# }
```

---

### Feature 3: Weight Adaptation

The **scoring weights automatically improve** based on feedback accuracy.

**Before Learning:**
```
Weights: genre=35, mood=40, energy=40, acoustic=10
Accuracy: 50% (only 50% of recommendations are liked)
```

**After Learning (from feedback):**
```
Accuracy improved? 
  YES → Increase weights (become more confident)
  NO  → Decrease weights (become more cautious)

If accuracy was 80%:
  New weights: genre=37.5, mood=42.5, energy=42.5, acoustic=10.5
               (1.07× adjustment = +7% confidence)

If accuracy was 40%:
  New weights: genre=33, mood=38, energy=38, acoustic=9.5
               (0.93× adjustment = -7% confidence)
```

**Real-world example:**
```
Round 1: System recommends 20 songs
         User likes 16 out of 20 (80% accuracy)
         System: "I'm doing well! Increase confidence."
         
Round 2: System recommends 20 more songs with adjusted weights
         User likes 18 out of 20 (90% accuracy)
         System: "Even better! Keep increasing."
```

---

### Feature 4: Gradual Energy Matching (Bonus)

Energy scoring is now **smooth, not binary**.

**Before (Binary - cliff at 0.3):**
```
Target energy: 0.8
Song energy: 0.81 → 40 points ✓
Song energy: 0.79 → 40 points ✓
Song energy: 0.50 → 0 points ✗ (sharp cliff)
Song energy: 0.49 → 0 points ✗
```

**After (Gradual - smooth falloff):**
```
Target energy: 0.8
Song energy: 0.81 → 40 points ✓
Song energy: 0.79 → 40 points ✓
Song energy: 0.50 → 12 points ✓ (partial credit)
Song energy: 0.49 → 10 points ✓ (more lenient)
Song energy: 0.20 → 0 points ✗ (too far)
```

Enable with:
```python
system.weight_learner.enable_gradual_energy()
```

---

## 📖 Usage Guide

### Basic Usage (Original System)

```python
from src.recommender import load_songs, recommend_songs, UserProfile

# Load songs
songs = load_songs("data/songs.csv")

# Create user profile
user = UserProfile(
    favorite_genre="pop",
    favorite_mood="happy",
    target_energy=0.8,
    likes_acoustic=False
)

# Get recommendations
recommendations = recommend_songs(user, songs, k=5)

# Display results
for song, score, reasons in recommendations:
    print(f"{song['title']}: {score:.0f}/125")
    print(f"  {' · '.join(reasons)}")
```

---

### Advanced Usage (Adaptive System with Learning)

```python
from src.adaptive_recommender import load_songs, UserProfile
from src.adaptive_feedback import AdaptiveSystem

# Load songs
songs = load_songs("data/songs.csv")

# Create adaptive system
system = AdaptiveSystem(songs)

# Create user profile
user = UserProfile(
    favorite_genre="lofi",
    favorite_mood="chill",
    target_energy=0.35,
    likes_acoustic=True
)

# Get recommendations with confidence
recommendations = system.get_recommendations(user, k=5)

for song, score, reasons, confidence in recommendations:
    print(f"{song.title}: {score:.0f}/125 ({confidence:.0f}% confident)")
    print(f"  {' · '.join(reasons)}")

# User provides feedback
system.feedback_on_recommendation(recommendations[0][0], user, liked=True)
system.feedback_on_recommendation(recommendations[1][0], user, liked=False)

# Check accuracy
stats = system.feedback_tracker.get_summary()
print(f"Accuracy: {stats['accuracy']:.1f}%")
print(f"Liked: {stats['recommendations_liked']}")
print(f"Disliked: {stats['recommendations_disliked']}")

# System learns and adapts
learning_results = system.learn_and_adapt()
print(f"Weights adjusted: {learning_results['weights_changed']}")
```

---

### A/B Testing Different Algorithms

```python
from src.phase2_ab_test import ABTestComparison

# Create A/B test
test = ABTestComparison(songs)

# Run test with different user profiles
result = test.run_test(user_profile, num_recommendations=10)

print(f"Top 5 (System A): {result['top_5_a']}")
print(f"Top 5 (System B): {result['top_5_b']}")
print(f"Ranking differences: {result['ranking_differences']}")
```

---

## 🏗️ Architecture

### Component Overview

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| `adaptive_recommender.py` | Score songs with AI weights | `ScoringWeights`, `AdaptiveRecommender` |
| `adaptive_feedback.py` | Track feedback & learn | `FeedbackTracker`, `WeightLearner`, `AdaptiveSystem` |
| `phase1_demo.py` | Demonstrate all features | Various demos |
| `phase2_ab_test.py` | Compare algorithms | `ABTestComparison` |

### Data Flow

```
User Input (genre, mood, energy, likes_acoustic)
    ↓
AdaptiveRecommender.recommend()
    ├─ Score each song
    ├─ Calculate confidence (0-100%)
    └─ Return: (song, score, reasons, confidence) ×k
    ↓
User Reviews & Reacts
    ↓
system.feedback_on_recommendation(song, user, liked=True/False)
    ├─ FeedbackTracker records reaction
    └─ Stores: timestamp, profile, actual outcome
    ↓
After N feedback entries:
system.learn_and_adapt()
    ├─ WeightLearner analyzes accuracy
    ├─ Calculates new weights
    └─ Updates AdaptiveRecommender
    ↓
Next Round: Better recommendations!
```

---

## 📊 Scoring Formula

### Original (Base Algorithm)

Each song scored on 4 criteria (max 125 points):

| Criterion | Points | Condition |
|-----------|--------|-----------|
| Genre Match | +35 | `song.genre == user.favorite_genre` |
| Mood Match | +40 | `song.mood == user.favorite_mood` |
| Energy | +40 | `\|song.energy - user.target_energy\| ≤ 0.3` |
| Acousticness | +10 | User preference matches |

### With AI Features

- **Weights are learnable** - Can scale based on feedback
- **Confidence = (criteria matched / 4) × 100%**
- **Energy scoring can be gradual** - Not just binary
- **System improves as it learns** - Accuracy feedback → weight adjustment

---

## 🔍 Understanding Confidence

### How Confidence is Calculated

```
Criteria matched = 0
if genre matches:     criteria_matched += 1
if mood matches:      criteria_matched += 1
if energy is close:   criteria_matched += 1
if acoustic matches:  criteria_matched += 1

confidence = (criteria_matched / 4.0) * 100.0
```

### Confidence Interpretation

| Score | Matches | Meaning |
|-------|---------|---------|
| 100% | 4/4 | All criteria aligned—you'll probably love this |
| 75% | 3/4 | Main criteria match—likely to enjoy |
| 50% | 2/4 | Mixed match—could go either way |
| 25% | 1/4 | Long shot—risky but worth exploring |
| 0% | 0/4 | No matches—skip this one |

### Confidence Calibration

Over time, system measures: **"When I said 80% confident, was I right?"**

```python
stats = system.feedback_tracker.get_summary()
print(f"Calibration: {stats['calibration']:.1f}%")

# If 80% calibrated:
# When system says "80% confident", user likes it 80% of the time
# Perfect match! System correctly estimates its own uncertainty.
```

---

## ⚠️ Known Limitations

### 1. Limited Dataset
- Only 10 songs (real systems have millions)
- Users with niche taste preferences will see repeated recommendations
- Solution: Integrate Spotify API for real song database

### 2. No Collaborative Filtering
- System only looks at individual user preferences
- Can't learn from "users like you also enjoyed..."
- Solution: Collect feedback from multiple users, find patterns

### 3. No Cold-Start Handling
- New users get generic recommendations
- Solution: Ask user detailed profile questions on signup

### 4. Manual Feedback Entry
- Requires user to explicitly rate recommendations
- Real systems track plays, skips, saves automatically
- Solution: Integrate Spotify API for implicit feedback

### 5. Learning Rate Fixed
- All weights adjust equally based on accuracy
- Can't learn which criteria matter most to THIS user
- Solution: Implement per-weight learning algorithm

### 6. No Real-Time Updates
- Weights update after manual training call
- Real systems update continuously
- Solution: Trigger learning after every N feedback entries

---

## 🧪 Testing & Evaluation

### Unit Tests

```bash
# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score -v
```

### Demo Scripts

```bash
# Phase 1: See all AI features
python src/phase1_demo.py
# - Confidence scoring
# - Feedback collection
# - Weight learning
# - Gradual vs binary energy

# Phase 2: A/B test comparison
python src/phase2_ab_test.py
# - Compare binary vs gradual energy scoring
# - See how weights affect rankings
```

### Evaluation Metrics

The system tracks:

| Metric | Meaning | Formula |
|--------|---------|---------|
| **Accuracy** | % of recommendations user liked | `liked / total` |
| **Calibration** | How well confidence predicts outcomes | `avg(confidence \| liked) / avg(confidence \| disliked)` |
| **Average Confidence When Liked** | What confidence was on hits | `mean(confidence for liked=True)` |
| **Average Confidence When Disliked** | What confidence was on misses | `mean(confidence for liked=False)` |

---

## 📁 Project Structure

```
applied-ai-system-project/
├── README.md                          ← You are here
├── PHASE2_ARCHITECTURE.md             ← Architecture documentation
├── ALGORITHM_DESIGN.md                ← Original algorithm design
├── PHASE4_EVALUATION.md               ← Original evaluation results
├── requirements.txt                   ← Dependencies
│
├── data/
│   └── songs.csv                      ← 10 sample songs with features
│
├── src/
│   ├── main.py                        ← Basic recommender entry point
│   ├── recommender.py                 ← Original algorithm (rule-based)
│   ├── evaluate.py                    ← Original evaluation script
│   ├── adaptive_recommender.py        ← NEW: AI-enhanced recommender
│   ├── adaptive_feedback.py           ← NEW: Feedback & learning system
│   ├── phase1_demo.py                 ← NEW: Feature demonstrations
│   ├── phase2_ab_test.py              ← NEW: A/B testing framework
│   └── PHASE2_SUMMARY.txt             ← Architecture explanation
│
└── tests/
    ├── test_recommender.py            ← Original tests
    └── test_adaptive.py               ← NEW: Tests for AI features
```

---

## 🚀 Getting Started for Developers

### Extending the System

**Add a new scoring criterion:**
```python
# In adaptive_recommender.py, AdaptiveRecommender.score_song()

# Add: Tempo matching
if abs(song.tempo_bpm - user.target_tempo) < 10:
    score += self.weights.tempo_weight  # New weight!
    reasons.append(f"Tempo match (+{self.weights.tempo_weight:.0f})")
    criteria_matched += 1
```

**Add a new learning strategy:**
```python
# In adaptive_feedback.py, WeightLearner

def learn_per_weight(self, feedback_history):
    """Learn which weights matter most for this user"""
    # Analyze feedback patterns
    # Find which criteria most correlate with "liked"
    # Increase those weights selectively
```

**Implement real feedback integration:**
```python
# Replace manual feedback with Spotify integration
import spotipy

def get_real_feedback(user_spotify_id):
    client = spotipy.Spotify()
    recent_plays = client.current_user_recently_played()
    # Track plays, skips, saves
    # Auto-generate feedback entries
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | This file—overview and quick start |
| `PHASE2_ARCHITECTURE.md` | Detailed architecture explanation |
| `ALGORITHM_DESIGN.md` | Original algorithm design (v1) |
| `PHASE4_EVALUATION.md` | Original evaluation & bias analysis |
| `src/PHASE2_SUMMARY.txt` | Summary for architecture review |

---

## 🎓 Learning Outcomes

After exploring this project, you'll understand:

✅ How content-based recommenders work  
✅ How to design scoring algorithms  
✅ How to add confidence/uncertainty estimation  
✅ How machine learning improves rule-based systems  
✅ How to measure system quality (accuracy, calibration)  
✅ How to test and verify AI systems  
✅ How to document complex systems clearly  

---

## 📝 License

Educational use. Created for Applied AI Systems course (Spring 2026).

---

## ❓ FAQ

**Q: Is this real AI or just rules?**  
A: Both! It starts as rules (weighted scoring) then becomes AI by learning from feedback (weight adaptation). The key difference: without feedback, weights are static. With feedback, they adapt. That's machine learning.

**Q: How is this different from Netflix/Spotify?**  
A: Those systems are much more sophisticated:
- Millions of songs vs. 10
- Collaborative filtering (learn from millions of users)
- Deep learning embeddings (learned features, not hand-picked)
- Streaming integration (implicit feedback from plays/skips)
- A/B testing infrastructure (experiment at scale)

This is a simplified version that demonstrates the same principles.

**Q: Can I improve it?**  
A: Absolutely! See "Extending the System" section. Some ideas:
- Add more criteria (tempo, artist similarity, genre similarity)
- Implement per-weight learning
- Add cold-start strategies
- Integrate Spotify API for real data
- Build web UI with Flask/Django

**Q: How do I know it's working?**  
A: Run the demos:
```bash
python src/phase1_demo.py       # See features working
python src/phase2_ab_test.py    # Compare algorithms
```

Then check accuracy metrics:
```python
stats = system.get_system_stats()
print(stats)  # Shows accuracy, confidence calibration, learned weights
```

---

## 🤝 Contributing

To extend this project:

1. **Add tests** first (test-driven development)
2. **Make changes** to `adaptive_recommender.py` or `adaptive_feedback.py`
3. **Run tests** to verify: `pytest tests/ -v`
4. **Update documentation** to explain new features
5. **Create demo** showing how to use new feature

---

## 📞 Questions or Issues?

Review these files for answers:
- **How does it work?** → `PHASE2_ARCHITECTURE.md`
- **How do I use it?** → Look above in "Usage Guide"
- **Why does it rank songs this way?** → `ALGORITHM_DESIGN.md`
- **What are the biases?** → `PHASE4_EVALUATION.md`

---

**Last Updated:** April 13, 2026  
**Version:** 2.0 (Adaptive with Learning)  
**Status:** ✅ Production-Ready for Educational Use
