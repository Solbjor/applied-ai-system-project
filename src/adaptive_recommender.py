"""
Adaptive Music Recommender with Confidence Scoring and Learning Capability

This module implements an AI-enhanced recommender that:
1. Computes confidence scores for each recommendation
2. Uses gradual energy matching (not binary)
3. Supports learnable weights that can adapt based on feedback
4. Tracks which factors influence recommendations
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Song:
    """Represents a song and its audio features."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class ScoringWeights:
    """
    Configurable weights for the scoring algorithm.
    
    These can be learned from user feedback to adapt the recommender.
    Default weights match the original algorithm.
    """
    
    def __init__(self, 
                 genre_weight: float = 35.0,
                 mood_weight: float = 40.0,
                 energy_weight: float = 40.0,
                 acoustic_weight: float = 10.0,
                 energy_decay_rate: float = 0.0):
        """
        Initialize scoring weights.
        
        Args:
            genre_weight: Points for exact genre match
            mood_weight: Points for exact mood match
            energy_weight: Max points for energy similarity (uses gradient)
            acoustic_weight: Points for acousticness preference match
            energy_decay_rate: How quickly energy score falls off (0=binary, 1=linear)
        """
        self.genre_weight = genre_weight
        self.mood_weight = mood_weight
        self.energy_weight = energy_weight
        self.acoustic_weight = acoustic_weight
        self.energy_decay_rate = energy_decay_rate
        self.max_score = genre_weight + mood_weight + energy_weight + acoustic_weight
    
    def to_dict(self) -> Dict[str, float]:
        """Export weights as dictionary."""
        return {
            'genre_weight': self.genre_weight,
            'mood_weight': self.mood_weight,
            'energy_weight': self.energy_weight,
            'acoustic_weight': self.acoustic_weight,
            'energy_decay_rate': self.energy_decay_rate,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, float]) -> 'ScoringWeights':
        """Create weights from dictionary."""
        return ScoringWeights(**data)


class AdaptiveRecommender:
    """
    AI-enhanced music recommender with:
    - Confidence scoring (shows uncertainty)
    - Gradual energy matching (not binary)
    - Support for learning from user feedback
    """
    
    def __init__(self, songs: List[Song], weights: Optional[ScoringWeights] = None):
        """
        Initialize recommender.
        
        Args:
            songs: List of Song objects
            weights: ScoringWeights object (defaults to standard weights)
        """
        self.songs = songs
        self.weights = weights or ScoringWeights()
        logger.info(f"Initialized adaptive recommender with {len(songs)} songs")
    
    def score_song(self, user: UserProfile, song: Song) -> Tuple[float, List[str], float]:
        """
        Score a song and compute confidence.
        
        Returns:
            (score, reasons, confidence) where:
            - score: Raw score (0 to max_score)
            - reasons: List of scoring reasons
            - confidence: Confidence in recommendation (0.0 to 1.0)
        """
        score = 0.0
        reasons = []
        criteria_matched = 0  # Track for confidence
        
        # 1. GENRE MATCH: +35 if exact match
        if song.genre == user.favorite_genre:
            score += self.weights.genre_weight
            reasons.append(f"Genre match (+{self.weights.genre_weight:.0f})")
            criteria_matched += 1
        
        # 2. MOOD MATCH: +40 if exact match
        if song.mood == user.favorite_mood:
            score += self.weights.mood_weight
            reasons.append(f"Mood match (+{self.weights.mood_weight:.0f})")
            criteria_matched += 1
        
        # 3. ENERGY SIMILARITY: Gradual scoring (not binary!)
        energy_score = self._score_energy(song.energy, user.target_energy)
        if energy_score > 0:
            reasons.append(f"Energy match ({song.energy:.2f} vs {user.target_energy:.2f}) (+{energy_score:.1f})")
            score += energy_score
            criteria_matched += 1
        
        # 4. ACOUSTICNESS PREFERENCE: +10 if matches
        if user.likes_acoustic and song.acousticness > 0.7:
            score += self.weights.acoustic_weight
            reasons.append(f"Acoustic match (+{self.weights.acoustic_weight:.0f})")
            criteria_matched += 1
        elif not user.likes_acoustic and song.acousticness < 0.3:
            score += self.weights.acoustic_weight
            reasons.append(f"Electronic match (+{self.weights.acoustic_weight:.0f})")
            criteria_matched += 1
        
        # CONFIDENCE: Based on how many criteria matched
        # 0 criteria = 0% confidence
        # 1 criteria = 40% confidence
        # 2 criteria = 60% confidence
        # 3 criteria = 80% confidence
        # 4 criteria = 100% confidence
        confidence = (criteria_matched / 4.0) * 100.0
        
        return score, reasons, confidence
    
    def _score_energy(self, song_energy: float, target_energy: float) -> float:
        """
        Score energy similarity using gradient (not binary).
        
        Formula:
        - If decay_rate = 0 (default): Binary (40 if within 0.3, else 0)
        - If decay_rate = 1: Linear gradient (more matches = more points)
        - If decay_rate > 0.5: Smoother falloff
        """
        energy_diff = abs(song_energy - target_energy)
        
        if self.weights.energy_decay_rate == 0:
            # Original binary behavior
            if energy_diff <= 0.3:
                return self.weights.energy_weight
            return 0
        
        else:
            # Gradual scoring: full points within tolerance, then decay
            tolerance = 0.3
            if energy_diff <= tolerance:
                return self.weights.energy_weight
            
            # Beyond tolerance: linearly decay to 0
            # At distance 0.3: full points
            # At distance 0.6: half points
            # At distance 0.9: zero points
            remaining_distance = energy_diff - tolerance
            max_distance = 0.6  # Full range is 0 to 1.0 energy
            
            if remaining_distance >= max_distance:
                return 0
            
            # Linear falloff
            decay_factor = 1 - (remaining_distance / max_distance)
            return self.weights.energy_weight * decay_factor
    
    def recommend(self, user: UserProfile, k: int = 5) -> List[Tuple[Song, float, List[str], float]]:
        """
        Generate top-k recommendations with confidence scores.
        
        Returns:
            List of (song, score, reasons, confidence) tuples sorted by score
        """
        scored_songs = []
        for song in self.songs:
            score, reasons, confidence = self.score_song(user, song)
            scored_songs.append((song, score, reasons, confidence))
        
        # Sort by score (descending), then by confidence (descending)
        scored_songs.sort(key=lambda x: (x[1], x[3]), reverse=True)
        
        return scored_songs[:k]
    
    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Generate human-readable explanation for a recommendation."""
        score, reasons, confidence = self.score_song(user, song)
        reasons_str = " | ".join(reasons) if reasons else "No matching criteria"
        explanation = f"Score: {score:.0f}/{self.weights.max_score:.0f} ({confidence:.0f}% confidence) — {reasons_str}"
        return explanation
    
    def update_weights(self, new_weights: ScoringWeights) -> None:
        """
        Update the scoring weights (used for learning).
        
        Args:
            new_weights: New ScoringWeights object
        """
        logger.info(f"Updating weights: {new_weights.to_dict()}")
        self.weights = new_weights


def load_songs(csv_path: str) -> List[Song]:
    """
    Load songs from CSV and return as Song dataclass instances.
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        List of Song objects
    """
    songs = []
    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                song = Song(
                    id=int(row['id']),
                    title=row['title'],
                    artist=row['artist'],
                    genre=row['genre'],
                    mood=row['mood'],
                    energy=float(row['energy']),
                    tempo_bpm=float(row['tempo_bpm']),
                    valence=float(row['valence']),
                    danceability=float(row['danceability']),
                    acousticness=float(row['acousticness']),
                )
                songs.append(song)
        logger.info(f"Successfully loaded {len(songs)} songs from {csv_path}")
        return songs
    except FileNotFoundError:
        logger.error(f"Could not find file {csv_path}")
        return []
    except Exception as e:
        logger.error(f"Error loading songs: {e}")
        return []
