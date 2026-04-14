# Week 8 Action Plan: Completing Your Project

## Target Completion Time
**2-3 hours** (if you do Option A - Enhance Current Project)

---

## TASK 1: Add Setup/Installation Instructions (30 min)

### Current State
README jumps directly to project summary without setup steps.

### What to Add to README

Add this section at the top, after the title:

```markdown
## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project:**
   ```bash
   cd applied-ai-system-project
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows (PowerShell):**
     ```bash
     venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt):**
     ```bash
     venv\Scripts\activate.bat
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Project

**Run the recommender:**
```bash
python src/main.py
```

**Expected output:**
```
Successfully loaded 10 songs from data/songs.csv

================================================================================
🎵 MUSIC RECOMMENDER SIMULATION
================================================================================
User Profile: pop + happy + energy 0.8

1. SUNRISE CITY
   Artist:  Neon Echo
   Score:   125/125
   Reasons: Genre match (+35) · Mood match (+40) · Energy match (0.82 vs 0.80) (+40) · Not acoustic (0.18) (+10)
...
```

**Run the tests:**
```bash
pytest tests/
```

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: csvfile` | Activate venv, then `pip install -r requirements.txt` |
| `FileNotFoundError: data/songs.csv` | Make sure you're in the project root directory |
| `pytest: command not found` | Run `pip install pytest` |
```

---

## TASK 2: Add Logging & Error Handling (45 min)

### Current State
- `load_songs()` has try-catch
- `recommend_songs()` and main logic have minimal error checking

### What to Add

**In `src/recommender.py`, add at the top:**

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

**In `recommend_songs()` function, add validation:**

```python
def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """
    Generate top-k song recommendations based on user preferences.
    
    Args:
        user_prefs: Dictionary with keys 'genre', 'mood', 'energy', optional 'likes_acoustic'
        songs: List of song dictionaries to score and rank
        k: Number of recommendations to return (default 5)
        
    Returns:
        List of (song_dict, score, reasons_list) tuples sorted by score descending.
        
    Raises:
        ValueError: If required keys missing from user_prefs
        ValueError: If songs list is empty
    """
    # Validation
    required_keys = {'genre', 'mood', 'energy'}
    missing_keys = required_keys - set(user_prefs.keys())
    if missing_keys:
        logger.error(f"User profile missing required keys: {missing_keys}")
        raise ValueError(f"User profile must include: {required_keys}")
    
    if not songs:
        logger.warning("No songs provided for recommendation")
        return []
    
    if k <= 0:
        logger.error(f"k must be positive, got {k}")
        raise ValueError("k must be >= 1")
    
    logger.info(f"Recommending {min(k, len(songs))} songs for user: {user_prefs['genre']} + {user_prefs['mood']}")
    
    # Score each song
    scored_songs = []
    for song in songs:
        score, reasons = score_song_functional(user_prefs, song)
        scored_songs.append((song, score, reasons))
        
        if score == 0:
            logger.debug(f"Song '{song['title']}' scored 0 (no matches)")
    
    # Sort by score descending
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    
    # Return top-k
    results = scored_songs[:k]
    logger.info(f"Top recommendation: '{results[0][0]['title']}' (score: {results[0][1]:.0f}/125)")
    
    return results
```

**In `src/main.py`, enhance error handling:**

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    try:
        songs = load_songs("data/songs.csv")
        
        if not songs:
            logger.error("No songs loaded. Check data/songs.csv exists and is valid.")
            return
        
        # Starter example profile
        user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
        
        recommendations = recommend_songs(user_prefs, songs, k=5)
        
        print("\n" + "=" * 80)
        print("🎵 MUSIC RECOMMENDER SIMULATION")
        print("=" * 80)
        print(f"User Profile: {user_prefs['genre']} + {user_prefs['mood']} + energy {user_prefs['energy']}\n")
        
        if not recommendations:
            print("No recommendations found. Try adjusting preferences.")
            return
        
        for i, rec in enumerate(recommendations, 1):
            song, score, reasons = rec
            print(f"{i}. {song['title'].upper()}")
            print(f"   Artist:  {song['artist']}")
            print(f"   Score:   {score:.0f}/125")
            print(f"   Reasons: {' · '.join(reasons) if reasons else 'No matching criteria'}")
            print()
        
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
```

---

## TASK 3: Expand Test Suite (45 min)

### Current Tests
2 basic tests exist. Add these edge cases.

### New Tests to Add

Create a new file or append to `tests/test_recommender.py`:

```python
import pytest
from src.recommender import (
    Recommender, Song, UserProfile, 
    recommend_songs, score_song_functional
)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_recommend_with_empty_song_list(self):
        """Recommending with no songs returns empty list."""
        user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False,
        )
        rec = Recommender([])
        results = rec.recommend(user)
        assert results == []
    
    def test_recommend_with_zero_matches(self):
        """User with zero-match profile gets songs ordered by score."""
        songs = [
            Song(id=1, title="Rock Song", artist="Rock Band", genre="rock",
                 mood="intense", energy=0.9, tempo_bpm=150, valence=0.6,
                 danceability=0.6, acousticness=0.1),
        ]
        user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.2,  # Completely different
            likes_acoustic=True,
        )
        rec = Recommender(songs)
        results = rec.recommend(user, k=1)
        
        # Should still return the song, just with low score
        assert len(results) == 1
        assert results[0].title == "Rock Song"
    
    def test_recommend_k_greater_than_songs(self):
        """Requesting more songs than available returns all songs."""
        song1 = Song(id=1, title="Song 1", artist="Artist", genre="pop",
                     mood="happy", energy=0.8, tempo_bpm=120, valence=0.9,
                     danceability=0.8, acousticness=0.2)
        song2 = Song(id=2, title="Song 2", artist="Artist", genre="rock",
                     mood="intense", energy=0.9, tempo_bpm=150, valence=0.6,
                     danceability=0.6, acousticness=0.1)
        
        user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False,
        )
        rec = Recommender([song1, song2])
        results = rec.recommend(user, k=100)
        
        assert len(results) == 2
    
    def test_recommend_with_k_zero(self):
        """k=0 should raise error."""
        user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False,
        )
        song = Song(id=1, title="Test", artist="Artist", genre="pop",
                    mood="happy", energy=0.8, tempo_bpm=120, valence=0.9,
                    danceability=0.8, acousticness=0.2)
        rec = Recommender([song])
        
        with pytest.raises(ValueError):
            rec.recommend(user, k=0)
    
    def test_score_all_criteria_match(self):
        """Perfect match scores 125 points."""
        user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False,
        )
        song = Song(
            id=1, title="Perfect", artist="Artist", genre="pop",
            mood="happy", energy=0.82, tempo_bpm=120, valence=0.9,
            danceability=0.8, acousticness=0.18,
        )
        rec = Recommender([song])
        score, reasons = rec.score_song(user, song)
        
        assert score == 125
        assert len(reasons) == 4  # All 4 criteria match
    
    def test_score_no_criteria_match(self):
        """No matches scores 0 points."""
        user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False,
        )
        song = Song(
            id=1, title="None", artist="Artist", genre="rock",
            mood="intense", energy=0.2, tempo_bpm=80, valence=0.3,
            danceability=0.3, acousticness=0.85,
        )
        rec = Recommender([song])
        score, reasons = rec.score_song(user, song)
        
        assert score == 0
        assert len(reasons) == 0
    
    def test_scores_are_sorted_descending(self):
        """Recommendations sorted by score descending."""
        songs = [
            Song(id=1, title="Title1", artist="Artist", genre="pop",
                 mood="happy", energy=0.82, tempo_bpm=120, valence=0.9,
                 danceability=0.8, acousticness=0.18),
            Song(id=2, title="Title2", artist="Artist", genre="rock",
                 mood="intense", energy=0.9, tempo_bpm=150, valence=0.6,
                 danceability=0.6, acousticness=0.05),
        ]
        user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False,
        )
        rec = Recommender(songs)
        results = rec.recommend(user, k=2)
        
        # Song 1 should score higher (pop + happy match)
        assert results[0].title == "Title1"
        assert results[1].title == "Title2"
    
    def test_functional_api_validates_input(self):
        """recommend_songs raises error on invalid profile."""
        songs = [
            {"id": 1, "title": "Song", "artist": "Artist", "genre": "pop",
             "mood": "happy", "energy": 0.8, "tempo_bpm": 120, 
             "valence": 0.9, "danceability": 0.8, "acousticness": 0.2}
        ]
        
        # Missing 'energy' key
        bad_profile = {"genre": "pop", "mood": "happy"}
        
        with pytest.raises(ValueError):
            recommend_songs(bad_profile, songs)


class TestAcousticnessBonus:
    """Test the acousticness bonus behavior."""
    
    def test_acoustic_preference_true_high_acousticness(self):
        """User likes acoustic, song is acoustic (>0.7) → +10 bonus."""
        user = UserProfile(
            favorite_genre="lofi",
            favorite_mood="chill",
            target_energy=0.4,
            likes_acoustic=True,  # likes acoustic
        )
        song = Song(
            id=1, title="Acoustic Song", artist="Artist", genre="lofi",
            mood="chill", energy=0.4, tempo_bpm=80, valence=0.6,
            danceability=0.5, acousticness=0.85,  # High acousticness
        )
        rec = Recommender([song])
        score, reasons = rec.score_song(user, song)
        
        # 35 (genre) + 40 (mood) + 40 (energy) + 10 (acoustic) = 125
        assert score == 125
        assert any("Acoustic" in r for r in reasons)
    
    def test_acoustic_preference_false_low_acousticness(self):
        """User dislikes acoustic, song is electronic (<0.3) → +10 bonus."""
        user = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False,  # dislikes acoustic
        )
        song = Song(
            id=1, title="Electronic Song", artist="Artist", genre="pop",
            mood="happy", energy=0.82, tempo_bpm=120, valence=0.9,
            danceability=0.8, acousticness=0.05,  # Low acousticness
        )
        rec = Recommender([song])
        score, reasons = rec.score_song(user, song)
        
        # 35 + 40 + 40 + 10 = 125
        assert score == 125
        assert any("Not acoustic" in r for r in reasons)
```

### How to Run Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test
pytest tests/test_recommender.py::TestEdgeCases::test_recommend_with_empty_song_list -v

# Run with coverage
pytest tests/ --cov=src
```

---

## TASK 4: Explicitly Frame "Advanced Feature" (20 min)

### What to Add to README

Add this new section after "How It Works" and before "Limitations":

```markdown
## Advanced AI Feature: Reliability & Testing System

This project demonstrates **Reliability Testing** as its advanced AI feature, per Week 8 requirements.

### What This Means

Rather than relying on unverified AI predictions, this system includes:

1. **Systematic Evaluation (Phase 4)**
   - Tests across 3 distinct user profiles
   - Edge case experiments (missing genres, different preferences)
   - Reproducible results you can verify

2. **Transparency Through Limitations**
   - 6 major limitations identified upfront
   - Each limitation explained with concrete examples
   - Shows what works vs. what fails

3. **Score Breakdown & Explainability**
   - Every recommendation includes point breakdown
   - Users see exactly why a song was recommended
   - No "black box" decisions

4. **Bias Identification**
   - Binary energy scoring (not gradual)
   - Genre dominance in low-match cases
   - Limited dataset effects on niche genres

### Why This Matters for AI Systems

Production AI systems fail when:
- Hidden biases slip into production
- Edge cases aren't tested
- No human interpretation of results
- Failures aren't understood

This project's reliability focus ensures:
✅ Transparent decision-making  
✅ Known limitations documented  
✅ Testable, reproducible behavior  
✅ Human oversight maintained  

### Testing the System Yourself

See [Phase 4 Evaluation](PHASE4_EVALUATION.md) for detailed test results and methodology.

Run the evaluation:
```bash
python src/evaluate.py
```
```

---

## TASK 5: Write Reflection (30 min)

### Create new file: `REFLECTION.md`

```markdown
# Week 8 Reflection: Building a Reliable AI System

## Overview

This project started as a simple recommendation algorithm but evolved into a **Reliability Testing System**—demonstrating that trustworthy AI requires more than just clever math.

## Key Learning: Why "AI" Isn't About Magic

When I started, I thought "AI" meant:
- Complex machine learning models
- Neural networks that learn from data
- Black-box predictions

But this project taught me that **reliable AI** means:
- Clear, auditable decision logic
- Honest about limitations
- Testable across many scenarios
- Human-explainable results

## The Reliability Testing System

### What We Did

1. **Ran 3+ user profiles** through the recommender
2. **Identified 6 major limitations**
3. **Documented each with concrete examples**
4. **Traced the root cause** of each limitation

### What We Learned

**Success stories:**
- Genre + mood weighting is intuitive and works well
- Energy matching has strong predictive power
- Explainability (point breakdown) is crucial

**Failure modes:**
- Binary energy scoring misses gradual matching
- Small dataset creates filter bubbles (rock fans get only 1 option)
- No user feedback means weights never improve

## If I Were to Improve This System

### Short-term (2-3 hours)
1. Add gradual energy scoring: `(1 - |energy_diff| / 0.3) * 40` instead of all-or-nothing
2. Implement genre similarity: treat "pop" and "indie pop" as 70% similar
3. Add confidence scoring: low scores get a "confidence: LOW" flag

### Medium-term (1-2 days)
1. Collect simulated user feedback (likes/dislikes)
2. Use feedback to learn weights via simple gradient descent
3. Implement A/B testing: compare new weights vs. old weights

### Long-term (1+ week)
1. Use embedding-based similarity (from Spotify API or fine-tuned model)
2. Implement collaborative filtering (user-user similarity)
3. Add cold-start solution using content + popularity hybrid

## What "Production-Ready" Would Look Like

| Aspect | Current | Production-Ready |
|--------|---------|-----------------|
| **Data** | 10 songs, static CSV | Millions of songs, real-time updates |
| **Weights** | Hardcoded | Learned from user feedback |
| **Cold-start** | No solution | Hybrid content + popularity |
| **Monitoring** | Phase 4 evaluation | Continuous A/B tests, user surveys |
| **Bias** | Documented | Continuously monitored |
| **Explainability** | Point breakdown | NLP-generated explanations |

## Final Thought

AI systems in production fail not because they're wrong, but because they're **wrong in unexpected ways**. By building a Reliability Testing System, we ensure:

1. We know what works
2. We know what doesn't
3. We can explain why
4. We can improve incrementally

This is how trustworthy AI is actually built.

---

## Discussion Questions

1. **Would this system work better with a neural network?**
   - Probably yes (learned weights), but we'd lose explainability
   - Trade-off between accuracy and interpretability

2. **How would you handle the "cold-start problem"?**
   - New users have no preference history
   - Solutions: content-based (what we did), hybrid, or popularity-based

3. **What would you measure to know if the system is "biased"?**
   - Recommend same 5 songs to all profiles? That's diversity bias
   - Recommend only high-energy songs? That's energy bias
   - Recommend only acoustic? That's acousticness bias

4. **How does this relate to real-world AI systems?**
   - Spotify, Netflix, YouTube all use similar scoring systems
   - They add collaborative filtering (what groups like you liked)
   - They add deep learning (embeddings instead of manual features)
   - But at core: score, rank, explain—just more sophisticated

## Conclusion

Reliability testing isn't the "sexy" part of AI, but it's **the most important** part for systems people trust.
```

---

## Execution Timeline

| Task | Time | Status |
|------|------|--------|
| 1. Setup instructions | 30 min | NOT STARTED |
| 2. Logging + error handling | 45 min | NOT STARTED |
| 3. Expand test suite | 45 min | NOT STARTED |
| 4. Frame advanced feature | 20 min | NOT STARTED |
| 5. Write reflection | 30 min | NOT STARTED |
| **TOTAL** | **~2.5 hours** | |

---

## Quick Checklist Before Submission

- [ ] README has setup/installation steps
- [ ] Code has logging import and basic logs
- [ ] `recommend_songs()` validates user_prefs input
- [ ] 8+ new tests added to test suite
- [ ] README has "Advanced Feature: Reliability Testing" section
- [ ] REFLECTION.md created with thoughtful analysis
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Can run project: `python src/main.py`
- [ ] Can run evaluation: `python src/evaluate.py`

---

## Need Help?

If you get stuck on any task:
1. Read the code comments
2. Run tests in isolation to understand expected behavior
3. Check error logs from logging output
4. Review existing test examples for new test patterns
