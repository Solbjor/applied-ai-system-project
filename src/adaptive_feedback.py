"""
User Feedback & Learning System

This module implements an adaptive learning system that:
1. Tracks user feedback on recommendations
2. Learns to adjust weights based on what works
3. Measures recommendation quality over time
4. Generates A/B test comparisons
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import statistics

from adaptive_recommender import Song, UserProfile, ScoringWeights, AdaptiveRecommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FeedbackEntry:
    """Records user feedback on a recommendation."""
    
    timestamp: datetime
    song_id: int
    song_title: str
    user_profile: Dict  # Serialized UserProfile
    liked: bool  # True = user liked, False = user disliked
    confidence: float  # The confidence scores predicted
    actual_score: float  # The score assigned
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'song_id': self.song_id,
            'song_title': self.song_title,
            'user_profile': self.user_profile,
            'liked': self.liked,
            'confidence': self.confidence,
            'actual_score': self.actual_score,
        }


class FeedbackTracker:
    """Tracks user feedback on recommendations for learning."""
    
    def __init__(self):
        self.feedback_history: List[FeedbackEntry] = []
        self.accuracy_history: List[Tuple[datetime, float]] = []  # (timestamp, accuracy)
    
    def record_feedback(self, 
                       song: Song, 
                       user_profile: UserProfile,
                       liked: bool,
                       confidence: float,
                       actual_score: float) -> None:
        """
        Record feedback on a recommendation.
        
        Args:
            song: The recommended song
            user_profile: User profile used for recommendation
            liked: Whether the user liked the recommendation
            confidence: Confidence score from recommender
            actual_score: Score assigned by recommender
        """
        entry = FeedbackEntry(
            timestamp=datetime.now(),
            song_id=song.id,
            song_title=song.title,
            user_profile={
                'genre': user_profile.favorite_genre,
                'mood': user_profile.favorite_mood,
                'energy': user_profile.target_energy,
                'likes_acoustic': user_profile.likes_acoustic,
            },
            liked=liked,
            confidence=confidence,
            actual_score=actual_score,
        )
        self.feedback_history.append(entry)
        logger.info(f"Recorded feedback: '{song.title}' - liked={liked}, confidence={confidence:.0f}%")
    
    def get_accuracy(self) -> float:
        """
        Calculate accuracy: % of recommendations user actually liked.
        
        Returns:
            Float between 0.0 and 1.0 (0% to 100%)
        """
        if not self.feedback_history:
            return 0.0
        
        liked_count = sum(1 for entry in self.feedback_history if entry.liked)
        accuracy = liked_count / len(self.feedback_history)
        
        self.accuracy_history.append((datetime.now(), accuracy))
        return accuracy
    
    def get_confidence_calibration(self) -> float:
        """
        Measure how well confidence scores match actual outcomes.
        
        High calibration = confidence scores are accurate.
        Example: If we say 80% confidence, 80% of those should be correct.
        
        Returns:
            Float between 0.0 and 1.0 (0% to 100%)
        """
        if not self.feedback_history:
            return 0.0
        
        # Group feedback by confidence bins (0-20%, 20-40%, etc.)
        bins = {i: [] for i in range(5)}  # 5 bins of 20% each
        
        for entry in self.feedback_history:
            bin_index = int(entry.confidence / 20)
            bin_index = min(bin_index, 4)  # Cap at bin 4
            bins[bin_index].append(entry.liked)
        
        # For each bin, compare avg confidence to actual accuracy
        calibration_errors = []
        for bin_index, feedback_list in bins.items():
            if not feedback_list:
                continue
            
            bin_confidence = (bin_index + 0.5) * 20  # Center of bin
            bin_accuracy = sum(feedback_list) / len(feedback_list) * 100
            error = abs(bin_confidence - bin_accuracy)
            calibration_errors.append(error)
        
        if not calibration_errors:
            return 100.0
        
        # Return inverse of average error
        avg_error = statistics.mean(calibration_errors)
        calibration = max(0, 100 - avg_error)
        return calibration
    
    def export_feedback(self, filepath: str) -> None:
        """Export feedback history to JSON file."""
        data = [entry.to_dict() for entry in self.feedback_history]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported {len(data)} feedback entries to {filepath}")
    
    def get_summary(self) -> Dict:
        """Get summary statistics about feedback."""
        if not self.feedback_history:
            return {
                'total_feedback': 0,
                'accuracy': 0.0,
                'calibration': 0.0,
                'recommendations_liked': 0,
                'recommendations_disliked': 0,
            }
        
        liked_count = sum(1 for e in self.feedback_history if e.liked)
        disliked_count = len(self.feedback_history) - liked_count
        
        return {
            'total_feedback': len(self.feedback_history),
            'accuracy': self.get_accuracy() * 100,
            'calibration': self.get_confidence_calibration(),
            'recommendations_liked': liked_count,
            'recommendations_disliked': disliked_count,
            'avg_confidence_when_liked': statistics.mean(
                [e.confidence for e in self.feedback_history if e.liked]
            ) if liked_count > 0 else 0,
            'avg_confidence_when_disliked': statistics.mean(
                [e.confidence for e in self.feedback_history if not e.liked]
            ) if disliked_count > 0 else 0,
        }


class WeightLearner:
    """
    Learns to adjust weights based on user feedback.
    
    Uses simple gradient-based approach:
    - If user likes a recommendation, increase weights of criteria that matched
    - If user dislikes, decrease those weights
    """
    
    def __init__(self, initial_weights: ScoringWeights):
        self.weights = initial_weights
        self.learning_rate = 0.01  # How fast to adapt (0-1)
        self.learning_history: List[Tuple[datetime, ScoringWeights]] = [(datetime.now(), initial_weights)]
    
    def learn_from_feedback(self, feedback_history: List[FeedbackEntry]) -> None:
        """
        Update weights based on accumulated feedback.
        
        Strategy:
        - Collect feedback into liked/disliked groups
        - Analyze which weights worked for liked items
        - Adjust weights toward what works
        """
        if not feedback_history:
            logger.warning("No feedback to learn from")
            return
        
        liked = [e for e in feedback_history if e.liked]
        disliked = [e for e in feedback_history if not e.liked]
        
        logger.info(f"Learning from {len(liked)} liked and {len(disliked)} disliked recommendations")
        
        # Simple adjustment: 
        # If accuracy > 50%, slightly increase all weights (more confidence)
        # If accuracy < 50%, slightly decrease all weights (less confidence)
        accuracy = len(liked) / len(feedback_history) if feedback_history else 0
        
        adjustment_factor = 1 + (accuracy - 0.5) * self.learning_rate
        
        # Apply adjustment
        new_weights = ScoringWeights(
            genre_weight=self.weights.genre_weight * adjustment_factor,
            mood_weight=self.weights.mood_weight * adjustment_factor,
            energy_weight=self.weights.energy_weight * adjustment_factor,
            acoustic_weight=self.weights.acoustic_weight * adjustment_factor,
            energy_decay_rate=self.weights.energy_decay_rate,
        )
        
        logger.info(f"Adjusted weights by factor {adjustment_factor:.3f} (accuracy={accuracy:.1%})")
        self.weights = new_weights
        self.learning_history.append((datetime.now(), new_weights))
    
    def enable_gradual_energy(self) -> None:
        """Enable smooth energy scoring instead of binary."""
        self.weights.energy_decay_rate = 1.0
        logger.info("Enabled gradual energy scoring")
    
    def get_weight_changes(self) -> Dict:
        """Compare current weights to initial weights."""
        initial = self.learning_history[0][1]
        current = self.weights
        
        return {
            'genre_weight': {
                'initial': initial.genre_weight,
                'current': current.genre_weight,
                'change_percent': ((current.genre_weight - initial.genre_weight) / initial.genre_weight * 100) if initial.genre_weight > 0 else 0,
            },
            'mood_weight': {
                'initial': initial.mood_weight,
                'current': current.mood_weight,
                'change_percent': ((current.mood_weight - initial.mood_weight) / initial.mood_weight * 100) if initial.mood_weight > 0 else 0,
            },
            'energy_weight': {
                'initial': initial.energy_weight,
                'current': current.energy_weight,
                'change_percent': ((current.energy_weight - initial.energy_weight) / initial.energy_weight * 100) if initial.energy_weight > 0 else 0,
            },
        }


class AdaptiveSystem:
    """
    Full adaptive system combining recommender + learning.
    
    This is the integrated AI component that:
    1. Makes recommendations
    2. Collects feedback
    3. Learns and adapts
    """
    
    def __init__(self, songs: List[Song], initial_weights: Optional[ScoringWeights] = None):
        weights = initial_weights or ScoringWeights()
        self.recommender = AdaptiveRecommender(songs, weights)
        self.feedback_tracker = FeedbackTracker()
        self.weight_learner = WeightLearner(weights)
        self.songs = songs
    
    def get_recommendations(self, 
                           user: UserProfile, 
                           k: int = 5) -> List[Tuple[Song, float, List[str], float]]:
        """Get recommendations with confidence scores."""
        return self.recommender.recommend(user, k)
    
    def feedback_on_recommendation(self, 
                                   song: Song, 
                                   user: UserProfile, 
                                   liked: bool) -> None:
        """Record user feedback on a recommendation."""
        score, _, confidence = self.recommender.score_song(user, song)
        self.feedback_tracker.record_feedback(song, user, liked, confidence, score)
    
    def learn_and_adapt(self) -> Dict:
        """
        Learn from accumulated feedback and update weights.
        
        Returns:
            Dictionary with learning results
        """
        old_accuracy = self.feedback_tracker.get_accuracy()
        
        # Learn from all feedback
        self.weight_learner.learn_from_feedback(self.feedback_tracker.feedback_history)
        
        # Update recommender with new weights
        self.recommender.update_weights(self.weight_learner.weights)
        
        return {
            'accuracy_before': old_accuracy * 100,
            'weights_changed': self.weight_learner.get_weight_changes(),
            'total_feedback_samples': len(self.feedback_tracker.feedback_history),
        }
    
    def get_system_stats(self) -> Dict:
        """Get overall system performance statistics."""
        return {
            'feedback_summary': self.feedback_tracker.get_summary(),
            'weight_history': len(self.weight_learner.learning_history),
            'current_weights': self.recommender.weights.to_dict(),
        }
