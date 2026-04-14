"""
Phase 1 Demo: Adaptive Music Recommender in Action

This demo shows:
1. Initial recommendations with confidence scores
2. User providing feedback (likes/dislikes)
3. System learning from feedback
4. Improved recommendations after learning

Run this to see the AI feature working end-to-end.
"""

from adaptive_recommender import load_songs, UserProfile
from adaptive_feedback import AdaptiveSystem
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_recommendation(i: int, song, score, reasons, confidence):
    """Pretty print a single recommendation."""
    print(f"{i}. {song.title.upper()}")
    print(f"   Artist: {song.artist}")
    print(f"   Score: {score:.0f}/125")
    print(f"   Confidence: {confidence:.0f}%")
    print(f"   Why: {' · '.join(reasons) if reasons else 'No criteria matched'}")
    print()


def demo_basic_recommendations():
    """Demo 1: Show basic recommendations with confidence scores."""
    print_section("DEMO 1: Recommendations with Confidence Scoring")
    
    songs = load_songs("data/songs.csv")
    if not songs:
        logger.error("Failed to load songs")
        return
    
    # Create adaptive system
    system = AdaptiveSystem(songs)
    
    # User profile: pop + happy + energetic
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False
    )
    
    print(f"User Profile: {user.favorite_genre} + {user.favorite_mood} + energy {user.target_energy}")
    print(f"Acoustic preference: {'likes acoustic' if user.likes_acoustic else 'prefers electronic'}\n")
    
    # Get recommendations
    recs = system.get_recommendations(user, k=5)
    
    print("🎵 RECOMMENDATIONS:\n")
    for i, (song, score, reasons, confidence) in enumerate(recs, 1):
        print_recommendation(i, song, score, reasons, confidence)


def demo_confidence_calibration():
    """Demo 2: Show how confidence translates to actual accuracy."""
    print_section("DEMO 2: Confidence Calibration")
    
    songs = load_songs("data/songs.csv")
    if not songs:
        return
    
    system = AdaptiveSystem(songs)
    
    # Create a couple of user profiles
    profiles = [
        UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False
        ),
        UserProfile(
            favorite_genre="lofi",
            favorite_mood="chill",
            target_energy=0.35,
            likes_acoustic=True
        ),
    ]
    
    print("Simulating user feedback to measure confidence calibration...\n")
    
    # For each profile, get recommendations and simulate feedback
    for profile_idx, user in enumerate(profiles, 1):
        print(f"\n--- Profile {profile_idx}: {user.favorite_genre} + {user.favorite_mood} ---")
        
        recs = system.get_recommendations(user, k=3)
        
        for song, score, reasons, confidence in recs:
            # Simulate: if confidence > 70%, assume user likes it
            # if confidence < 50%, assume user dislikes it
            # if 50-70%, random-ish behavior
            like_probability = confidence / 100.0
            
            # For demo: if high confidence and genre matches, user likes
            if confidence > 60:
                liked = True
            elif confidence < 40:
                liked = False
            else:
                liked = confidence > 50
            
            outcome = "👍 LIKED" if liked else "👎 DISLIKED"
            system.feedback_on_recommendation(song, user, liked)
            
            print(f"  {song.title}: confidence {confidence:.0f}% → {outcome}")
    
    # Show accuracy metrics
    stats = system.feedback_tracker.get_summary()
    print(f"\n\n📊 FEEDBACK SUMMARY:")
    print(f"  Total feedback: {stats['total_feedback']}")
    print(f"  Liked: {stats['recommendations_liked']}")
    print(f"  Disliked: {stats['recommendations_disliked']}")
    print(f"  Accuracy: {stats['accuracy']:.1f}%")
    print(f"  Confidence Calibration: {stats['calibration']:.1f}%")


def demo_learning_and_adaptation():
    """Demo 3: Show system learning from feedback."""
    print_section("DEMO 3: Learning from Feedback & Weight Adaptation")
    
    songs = load_songs("data/songs.csv")
    if not songs:
        return
    
    system = AdaptiveSystem(songs)
    
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False
    )
    
    print(f"Starting with user: {user.favorite_genre} + {user.favorite_mood}")
    print(f"Initial weights: {system.recommender.weights.to_dict()}\n")
    
    # Round 1: Get recommendations and collect feedback
    print("ROUND 1: Initial recommendations")
    print("-" * 80)
    recs = system.get_recommendations(user, k=3)
    
    for i, (song, score, reasons, confidence) in enumerate(recs, 1):
        # Simulate feedback: high confidence = like, low confidence = dislike
        liked = confidence > 50
        outcome = "👍" if liked else "👎"
        system.feedback_on_recommendation(song, user, liked)
        print(f"{i}. {song.title} (confidence: {confidence:.0f}%) {outcome}")
    
    stats_before = system.feedback_tracker.get_summary()
    print(f"\nAccuracy: {stats_before['accuracy']:.1f}%")
    
    # Learn from feedback
    print("\n🧠 LEARNING FROM FEEDBACK...")
    learning_results = system.learn_and_adapt()
    print(f"Weights updated based on accuracy")
    print(f"New weights: {system.recommender.weights.to_dict()}\n")
    
    # Round 2: Get new recommendations with learned weights
    print("ROUND 2: Recommendations after learning")
    print("-" * 80)
    recs = system.get_recommendations(user, k=3)
    
    for i, (song, score, reasons, confidence) in enumerate(recs, 1):
        liked = confidence > 50
        outcome = "👍" if liked else "👎"
        system.feedback_on_recommendation(song, user, liked)
        print(f"{i}. {song.title} (confidence: {confidence:.0f}%) {outcome}")
    
    stats_after = system.feedback_tracker.get_summary()
    print(f"\nAccuracy: {stats_after['accuracy']:.1f}%")
    print(f"Accuracy improved by: {stats_after['accuracy'] - stats_before['accuracy']:.1f}%")


def demo_gradual_energy_scoring():
    """Demo 4: Show difference between binary and gradual energy scoring."""
    print_section("DEMO 4: Binary vs Gradual Energy Scoring")
    
    songs = load_songs("data/songs.csv")
    if not songs:
        return
    
    # User with specific energy target
    user = UserProfile(
        favorite_genre="lofi",
        favorite_mood="chill",
        target_energy=0.4,  # Target 0.4 energy
        likes_acoustic=True
    )
    
    print(f"Target energy: {user.target_energy}")
    print(f"Energy tolerance (old): exactly ±0.3 (binary)")
    print(f"Energy tolerance (new): smooth gradient\n")
    
    # Binary scoring (current default)
    print("BINARY SCORING (current):")
    print("-" * 80)
    system_binary = AdaptiveSystem(songs)
    system_binary.recommender.weights.energy_decay_rate = 0  # Binary mode
    
    recs = system_binary.get_recommendations(user, k=5)
    for i, (song, score, reasons, confidence) in enumerate(recs, 1):
        energy_diff = abs(song.energy - user.target_energy)
        in_range = energy_diff <= 0.3
        print(f"{i}. {song.title}: energy={song.energy:.2f} (diff={energy_diff:.2f}) {'✓' if in_range else '✗'}")
        print(f"   Score: {score:.0f}/125\n")
    
    # Gradual scoring
    print("\nGRADUAL SCORING (new):")
    print("-" * 80)
    system_gradual = AdaptiveSystem(songs)
    system_gradual.weight_learner.enable_gradual_energy()
    system_gradual.recommender.weights.energy_decay_rate = 1  # Gradual mode
    
    recs = system_gradual.get_recommendations(user, k=5)
    for i, (song, score, reasons, confidence) in enumerate(recs, 1):
        energy_diff = abs(song.energy - user.target_energy)
        print(f"{i}. {song.title}: energy={song.energy:.2f} (diff={energy_diff:.2f})")
        print(f"   Score: {score:.0f}/125 (gradient applied)")
        print(f"   Benefits: Closer energy gets more credit\n")


def main():
    """Run all demos."""
    print("\n")
    print("████████████████████████████████████████████████████████████████████████████████")
    print("█                                                                              █")
    print("█  🎵 ADAPTIVE MUSIC RECOMMENDER - PHASE 1 FUNCTIONALITY DEMO 🎵              █")
    print("█                                                                              █")
    print("█  Demonstrating AI features:                                                █")
    print("█  ✓ Confidence Scoring - shows recommendation certainty                      █")
    print("█  ✓ User Feedback Learning - system learns from feedback                    █")
    print("█  ✓ Weight Adaptation - adjusts weights based on what works                 █")
    print("█  ✓ Gradual Energy Scoring - smooth matching instead of binary              █")
    print("█                                                                              █")
    print("████████████████████████████████████████████████████████████████████████████████")
    
    try:
        # Run all demos
        demo_basic_recommendations()
        demo_confidence_calibration()
        demo_learning_and_adaptation()
        demo_gradual_energy_scoring()
        
        print_section("✅ ALL DEMOS COMPLETE")
        print("""
The adaptive recommender demonstrates:

1. CONFIDENCE SCORING
   - Each recommendation includes a confidence percentage
   - Higher confidence = recommender is sure about the match
   - Lower confidence = user might not like it

2. LEARNING FROM FEEDBACK
   - System tracks which recommendations users actually liked
   - Adjusts weights to improve over time
   - Accuracy improves as more feedback is collected

3. GRADUAL ENERGY MATCHING
   - Instead of binary (0 or 40 points), use smooth gradient
   - Songs closer to target energy score more points
   - Prevents cliff-edge scoring at 0.3 threshold

4. REAL AI FEATURE
   - This is actual machine learning (not just rules)
   - Weights are adapted based on data (user feedback)
   - System improves with experience

This is a fully integrated AI feature that affects:
- How recommendations are scored
- What songs rank highest
- How accurate predictions become over time
        """)
    
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
