# 🎵 Music Recommender Simulation

## Project Summary

This is a **content-based music recommender system** that scores songs based on user taste profiles and returns the most compatible recommendations.

### How It Works

The system uses a **weighted scoring algorithm** to match songs with user preferences:

**User Profile includes:**
- `favorite_genre`: Genre preference (e.g., "pop")
- `favorite_mood`: Mood preference (e.g., "happy")
- `target_energy`: Preferred energy level (0.0–1.0)
- `likes_acoustic`: Boolean preference for acoustic vs. electronic

**Scoring Formula (max 125 points):**
- Genre match: **+35 points** (exact match)
- Mood match: **+40 points** (exact match)
- Energy similarity: **+40 points** (within 0.3 of target)
- Acousticness preference: **+10 points** (>0.7 if acoustic preference, <0.3 if not)

**Song Features:**
- id, title, artist, genre, mood
- energy (0-1), tempo_bpm, valence, danceability, acousticness

**Recommendation Output:**
- Top-k songs ranked by score
- Each recommendation includes the score breakdown showing which criteria matched

### Example Run

For a user preferring **pop + happy + high energy (0.8) + not acoustic**:

```
User Profile: pop + happy + energy 0.8

1. SUNRISE CITY
   Artist:  Neon Echo
   Score:   125/125
   Reasons: Genre match (+35) · Mood match (+40) · Energy match (0.82 vs 0.80) (+40) · Not acoustic (0.18) (+10)

2. GYM HERO
   Artist:  Max Pulse
   Score:   85/125
   Reasons: Genre match (+35) · Energy match (0.93 vs 0.80) (+40) · Not acoustic (0.05) (+10)

3. ROOFTOP LIGHTS
   Artist:  Indigo Parade
   Score:   80/125
   Reasons: Mood match (+40) · Energy match (0.76 vs 0.80) (+40)
```

---

## How The System Works

This is a **weighted content-based recommender** that:

1. **Loads songs** from CSV with all audio features
2. **Scores each song** against the user profile by:
   - Checking exact matches on genre/mood
   - Computing similarity on numeric features (energy, acousticness)
   - Weighted combination to produce final score
3. **Ranks all songs** by score and returns top-k
4. **Explains each recommendation** with detailed breakdown of why it scored

### Algorithm Design Philosophy

- **Genre & Mood** are primary signals (35 + 40 = 75 points)
- **Energy** is equally important (40 points), allowing good matches even without genre
- **Acousticness** is a refinement bonus (10 points)
- **Why this matters:** Prevents genre from being a complete "veto" blocker—a user can still get great recommendations through energy + mood alignment

---

## Running the Recommender

**CLI-First Simulation:**

```bash
python src/main.py
```

This runs the default user profile (pop + happy + high energy) against all 10 songs in the dataset and displays:
- Ranked recommendations with scores
- Detailed breakdown of reasons for each recommendation
- Clear visualization of why song #1 ranks higher than song #2

**Example Output:**

![Music Recommender CLI Output](Screenshot%202026-03-29%20223659.png)

**Programmatic Usage:**

```python
from src.recommender import load_songs, recommend_songs

songs = load_songs("data/songs.csv")
user_prefs = {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}
recommendations = recommend_songs(user_prefs, songs, k=5)

for song, score, reasons in recommendations:
    print(f"{song['title']}: {score}/125 - {' · '.join(reasons)}")
```

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

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

