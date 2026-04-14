# API Documentation

Complete API reference for the Adaptive Music Recommender System.

---

## Table of Contents

1. [adaptive_recommender.py](#adaptive_recommenderpy)
2. [adaptive_feedback.py](#adaptive_feedbackpy)
3. [Data Classes](#data-classes)
4. [Examples](#examples)

---

## adaptive_recommender.py

Module for scoring songs and computing confidence.

### Class: `ScoringWeights`

Configurable weights for the scoring algorithm.

```python
class ScoringWeights:
    def __init__(self, 
                 genre_weight: float = 35.0,
                 mood_weight: float = 40.0,
                 energy_weight: float = 40.0,
                 acoustic_weight: float = 10.0,
                 energy_decay_rate: float = 0.0):
        """
        Initialize scoring weights.
        
        Args:
            genre_weight: Points for exact genre match (default: 35)
            mood_weight: Points for exact mood match (default: 40)
            energy_weight: Max points for energy similarity (default: 40)
            acoustic_weight: Points for acousticness match (default: 10)
            energy_decay_rate: Gradient for energy scoring
                - 0.0: Binary (40 or 0 points)
                - 1.0: Gradual falloff (smooth gradient)
        
        Example:
            weights = ScoringWeights(genre_weight=40, mood_weight=45)
        """
```

**Methods:**

```python
def to_dict(self) -> Dict[str, float]:
    """
    Export weights as dictionary.
    
    Returns:
        {
            'genre_weight': 35.0,
            'mood_weight': 40.0,
            'energy_weight': 40.0,
            'acoustic_weight': 10.0,
            'energy_decay_rate': 0.0,
        }
    """

@staticmethod
def from_dict(data: Dict[str, float]) -> 'ScoringWeights':
    """
    Create ScoringWeights from dictionary.
    
    Args:
        data: Dictionary with weight keys
        
    Returns:
        ScoringWeights instance
        
    Example:
        weights_dict = {'genre_weight': 35, 'mood_weight': 40, ...}
        weights = ScoringWeights.from_dict(weights_dict)
    """
```

---

### Class: `AdaptiveRecommender`

Enhanced recommender with confidence scoring and learnable weights.

```python
class AdaptiveRecommender:
    def __init__(self, songs: List[Song], 
                 weights: Optional[ScoringWeights] = None):
        """
        Initialize recommender.
        
        Args:
            songs: List of Song objects to recommend from
            weights: ScoringWeights (defaults to standard weights)
            
        Example:
            songs = load_songs("data/songs.csv")
            rec = AdaptiveRecommender(songs)
        """
```

**Methods:**

```python
def score_song(self, user: UserProfile, song: Song) \
    -> Tuple[float, List[str], float]:
    """
    Score a song and compute confidence.
    
    Args:
        user: UserProfile with preferences
        song: Song to score
        
    Returns:
        Tuple of:
        - score: Float (0 to max_score, typically 0-125)
        - reasons: List[str] explaining each score component
        - confidence: Float (0.0 to 100.0) showing certainty
        
    Example:
        user = UserProfile('pop', 'happy', 0.8, False)
        song = Song(1, 'Sunrise City', 'Neon Echo', 'pop', 'happy', 0.82, ...)
        
        score, reasons, confidence = rec.score_song(user, song)
        # score: 125.0
        # reasons: ['Genre match (+35)', 'Mood match (+40)', ...]
        # confidence: 100.0
    """

def recommend(self, user: UserProfile, k: int = 5) \
    -> List[Tuple[Song, float, List[str], float]]:
    """
    Generate top-k recommendations with confidence scores.
    
    Args:
        user: UserProfile with preferences
        k: Number of recommendations (default: 5)
        
    Returns:
        List of (song, score, reasons, confidence) tuples
        sorted by score descending
        
    Example:
        recommendations = rec.recommend(user, k=5)
        
        for song, score, reasons, confidence in recommendations:
            print(f"{song.title}: {score:.0f}/125 ({confidence:.0f}%)")
    """

def explain_recommendation(self, user: UserProfile, song: Song) -> str:
    """
    Generate human-readable explanation for a recommendation.
    
    Args:
        user: UserProfile
        song: Song to explain
        
    Returns:
        String explaining the recommendation
        
    Example:
        explanation = rec.explain_recommendation(user, song)
        # "Score: 125/125 (100% confidence) — Genre match (+35) | Mood match..."
    """

def update_weights(self, new_weights: ScoringWeights) -> None:
    """
    Update the scoring weights (called by learner).
    
    Args:
        new_weights: New ScoringWeights to use
        
    Note:
        This affects all future recommendations.
        
    Example:
        improved_weights = ScoringWeights(genre_weight=36, ...)
        rec.update_weights(improved_weights)
    """
```

---

### Function: `load_songs(csv_path: str) -> List[Song]`

Load songs from CSV file.

```python
def load_songs(csv_path: str) -> List[Song]:
    """
    Load songs from CSV and return as Song dataclass instances.
    
    Args:
        csv_path: Path to CSV file (relative or absolute)
        
    Returns:
        List of Song objects
        
    Raises:
        FileNotFoundError: If CSV file not found
        
    Example:
        songs = load_songs("data/songs.csv")
        print(f"Loaded {len(songs)} songs")
    """
```

---

## adaptive_feedback.py

Module for tracking feedback and learning from it.

### Class: `FeedbackEntry`

Records a single piece of user feedback.

```python
@dataclass
class FeedbackEntry:
    """Records user feedback on a recommendation."""
    
    timestamp: datetime          # When feedback was given
    song_id: int                # ID of recommended song
    song_title: str             # Title of song
    user_profile: Dict          # Serialized user preferences
    liked: bool                 # True = user liked, False = disliked
    confidence: float           # Predicted confidence (0-100)
    actual_score: float         # Score assigned by recommender
```

---

### Class: `FeedbackTracker`

Accumulates and analyzes user feedback.

```python
class FeedbackTracker:
    """Tracks user feedback for learning and analysis."""
    
    def __init__(self):
        """Initialize empty feedback history."""
```

**Methods:**

```python
def record_feedback(self, song: Song, user_profile: UserProfile,
                   liked: bool, confidence: float, 
                   actual_score: float) -> None:
    """
    Record feedback on a recommendation.
    
    Args:
        song: The recommended song
        user_profile: User profile used for recommendation
        liked: Whether user liked the recommendation
        confidence: Confidence score from recommender (0-100)
        actual_score: Score assigned by recommender (0-125)
        
    Example:
        tracker.record_feedback(
            song=song,
            user_profile=user,
            liked=True,
            confidence=85.0,
            actual_score=100.0
        )
    """

def get_accuracy(self) -> float:
    """
    Calculate recommendation accuracy.
    
    Returns:
        Float between 0.0 and 1.0
        (percentage of recommendations user liked)
        
    Example:
        accuracy = tracker.get_accuracy()
        # 0.8 = 80% of recommendations were liked
    """

def get_confidence_calibration(self) -> float:
    """
    Measure how well confidence scores match actual outcomes.
    
    Returns:
        Float between 0.0 and 100.0 (percentage)
        
    How it works:
        Groups recommendations by confidence level (0-20%, 20-40%, etc)
        For each group, compares average confidence to accuracy
        
    Example:
        calibration = tracker.get_confidence_calibration()
        # 87.5 = When system says '80% confident', it's right 87.5%
    """

def get_summary(self) -> Dict:
    """
    Get summary statistics about feedback.
    
    Returns:
        Dict with:
        {
            'total_feedback': int,
            'accuracy': float (0-1),
            'calibration': float (0-100),
            'recommendations_liked': int,
            'recommendations_disliked': int,
            'avg_confidence_when_liked': float,
            'avg_confidence_when_disliked': float,
        }
        
    Example:
        stats = tracker.get_summary()
        print(f"Accuracy: {stats['accuracy']*100:.1f}%")
    """

def export_feedback(self, filepath: str) -> None:
    """
    Export feedback history to JSON file.
    
    Args:
        filepath: Where to save JSON
        
    Example:
        tracker.export_feedback("feedback_log.json")
    """
```

---

### Class: `WeightLearner`

Learns to adjust weights based on feedback.

```python
class WeightLearner:
    """Learns to adapt weights from user feedback."""
    
    def __init__(self, initial_weights: ScoringWeights):
        """
        Initialize learner.
        
        Args:
            initial_weights: Starting ScoringWeights
        """
```

**Methods:**

```python
def learn_from_feedback(self, feedback_history: List[FeedbackEntry]) -> None:
    """
    Update weights based on accumulated feedback.
    
    Algorithm:
        1. Measure accuracy (% of recommendations user liked)
        2. If accuracy > 50%: increase weights (more confident)
        3. If accuracy < 50%: decrease weights (less confident)
        4. Apply adjustment to all weights equally
    
    Args:
        feedback_history: List of FeedbackEntry objects
        
    Example:
        learner.learn_from_feedback(tracker.feedback_history)
        # Weights have been updated internally
    """

def enable_gradual_energy(self) -> None:
    """
    Enable smooth energy scoring instead of binary.
    
    Changes energy_decay_rate from 0 to 1.
    
    Example:
        learner.enable_gradual_energy()
        # Now energy scoring is gradual, not binary
    """

def get_weight_changes(self) -> Dict:
    """
    Compare current weights to initial weights.
    
    Returns:
        Dict showing before/after for each weight:
        {
            'genre_weight': {
                'initial': 35.0,
                'current': 36.5,
                'change_percent': 4.3,
            },
            'mood_weight': {...},
            'energy_weight': {...},
        }
    """
```

---

### Class: `AdaptiveSystem`

Orchestrates recommender + feedback + learning.

```python
class AdaptiveSystem:
    """
    Full adaptive system combining recommender, feedback, and learning.
    
    This is the main class most users interact with.
    """
    
    def __init__(self, songs: List[Song], 
                 initial_weights: Optional[ScoringWeights] = None):
        """
        Initialize adaptive system.
        
        Args:
            songs: List of Song objects
            initial_weights: Starting ScoringWeights (optional)
            
        Example:
            songs = load_songs("data/songs.csv")
            system = AdaptiveSystem(songs)
        """
```

**Methods:**

```python
def get_recommendations(self, user: UserProfile, k: int = 5) \
    -> List[Tuple[Song, float, List[str], float]]:
    """
    Get recommendations with confidence scores.
    
    Args:
        user: UserProfile with preferences
        k: Number of recommendations (default: 5)
        
    Returns:
        List of (song, score, reasons, confidence) tuples
        
    Example:
        recs = system.get_recommendations(user, k=5)
        for song, score, reasons, confidence in recs:
            print(f"{song.title} ({confidence:.0f}% confident)")
    """

def feedback_on_recommendation(self, song: Song, 
                              user: UserProfile, liked: bool) -> None:
    """
    Record user feedback on a recommendation.
    
    Args:
        song: The recommended song
        user: User profile
        liked: Whether user liked it (True/False)
        
    Example:
        system.feedback_on_recommendation(song, user, liked=True)
        system.feedback_on_recommendation(song, user, liked=False)
    """

def learn_and_adapt(self) -> Dict:
    """
    Learn from accumulated feedback and update weights.
    
    This is the "AI" part - weights adapt based on data.
    
    Returns:
        Dict with learning results:
        {
            'accuracy_before': float (0-100),
            'weights_changed': Dict,
            'total_feedback_samples': int,
        }
        
    Example:
        # After collecting >10 feedback entries
        results = system.learn_and_adapt()
        print(f"Accuracy: {results['accuracy_before']:.1f}%")
        print(f"Weights updated: {results['weights_changed']}")
    """

def get_system_stats(self) -> Dict:
    """
    Get overall system performance statistics.
    
    Returns:
        Dict with:
        {
            'feedback_summary': Dict (from FeedbackTracker),
            'weight_history': int (number of weight updates),
            'current_weights': Dict,
        }
        
    Example:
        stats = system.get_system_stats()
        print(f"Accuracy: {stats['feedback_summary']['accuracy']:.1f}%")
    """
```

---

## Data Classes

### Class: `Song`

Represents a song with audio features.

```python
@dataclass
class Song:
    """Represents a song and its attributes."""
    
    id: int                      # Unique identifier (1-10)
    title: str                   # Song name
    artist: str                  # Artist name
    genre: str                   # Music genre
    mood: str                    # Emotional mood
    energy: float                # Energy level (0-1)
    tempo_bpm: float             # Beats per minute
    valence: float               # Musical positivity (0-1)
    danceability: float          # How danceable (0-1)
    acousticness: float          # Acoustic vs electronic (0-1)
```

---

### Class: `UserProfile`

Represents user taste preferences.

```python
@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    
    favorite_genre: str          # Preferred music genre
    favorite_mood: str           # Preferred mood
    target_energy: float         # Preferred energy level (0-1)
    likes_acoustic: bool         # Acoustic or electronic preference
    
    # Optional (for learning):
    # user_id: Optional[int] = None  # To track repeated users
```

---

## Examples

### Example 1: Basic Recommendation

```python
from src.adaptive_recommender import load_songs, UserProfile
from src.adaptive_feedback import AdaptiveSystem

# Load songs
songs = load_songs("data/songs.csv")

# Create system
system = AdaptiveSystem(songs)

# Create user
user = UserProfile(
    favorite_genre="pop",
    favorite_mood="happy",
    target_energy=0.8,
    likes_acoustic=False
)

# Get recommendations
recs = system.get_recommendations(user, k=3)

for song, score, reasons, confidence in recs:
    print(f"\n{song.title}")
    print(f"Score: {score:.0f}/125 ({confidence:.0f}% confident)")
    print(f"Reasons: {' · '.join(reasons)}")
```

---

### Example 2: Learning From Feedback

```python
# Get recommendations
recs = system.get_recommendations(user, k=3)

# User provides feedback
system.feedback_on_recommendation(recs[0][0], user, liked=True)   # Liked first
system.feedback_on_recommendation(recs[1][0], user, liked=False)  # Disliked second
system.feedback_on_recommendation(recs[2][0], user, liked=True)   # Liked third

# Repeat this multiple times (say, 20 recommendations)
# Then learn from feedback
results = system.learn_and_adapt()
print(f"Accuracy improved: {results['accuracy_before']:.1f}%")
```

---

### Example 3: A/B Testing

```python
from src.phase2_ab_test import ABTestComparison

# Create A/B test
test = ABTestComparison(songs)

# Compare algorithms
result = test.run_test(user, num_recommendations=10)

print(f"System A (Binary): {result['top_5_a']}")
print(f"System B (Gradual): {result['top_5_b']}")
print(f"Differences: {result['ranking_differences']}")
```

---

### Example 4: Check Metrics

```python
# After collecting feedback
stats = system.get_system_stats()

feedback_stats = stats['feedback_summary']
print(f"Total recommendations: {feedback_stats['total_feedback']}")
print(f"User liked: {feedback_stats['recommendations_liked']}")
print(f"User disliked: {feedback_stats['recommendations_disliked']}")
print(f"Accuracy: {feedback_stats['accuracy']:.1f}%")
print(f"Confidence calibration: {feedback_stats['calibration']:.1f}%")

weights = stats['current_weights']
print(f"Current weights: {weights}")
```

---

## Error Handling

The system includes robust error handling:

```python
# Safe loading with error messages
songs = load_songs("nonexistent.csv")
if not songs:
    print("Failed to load songs")
    return

# Validation in learning
if len(tracker.feedback_history) < 5:
    logger.warning("Need at least 5 feedback entries to learn")
    
# Graceful handling of edge cases
if not recommendations:
    print("No recommendations available")
```

---

## Performance Considerations

| Operation | Time | Space |
|-----------|------|-------|
| Load 10 songs | < 1ms | < 1KB |
| Score 10 songs | < 1ms | < 1KB |
| Get top-5 | < 1ms | < 1KB |
| Record 100 feedback entries | < 10ms | < 10KB |
| Learn from feedback | < 50ms | < 1KB |

---

## Logging

System uses Python `logging` module:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Then run code
songs = load_songs("data/songs.csv")
# Output: INFO:adaptive_recommender:Successfully loaded 10 songs from data/songs.csv

system = AdaptiveSystem(songs)
# Output: INFO:adaptive_recommender:Initialized adaptive recommender with 10 songs

system.feedback_on_recommendation(song, user, True)
# Output: INFO:adaptive_feedback:Recorded feedback: 'Song Title' - liked=True, confidence=85%
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | Apr 2026 | Added AI features (confidence, feedback, learning) |
| 1.0 | Mar 2026 | Initial rule-based recommender |

---

**Last Updated:** April 13, 2026
