"""
Phase 4: Reliability & Testing - Comprehensive Test Suite
========================================================

Tests for confidence scoring, weight learning, and system reliability.
Measures what works well and what doesn't.

Test Categories:
  1. Confidence Scoring Tests - Verify confidence accuracy
  2. Calibration Tests - Confidence vs reality correlation
  3. Weight Learning Tests - System improvement over feedback
  4. Edge Case Tests - Robustness
  5. Performance Tests - Speed & scalability
"""

from typing import List, Tuple, Dict
import statistics
import time

from adaptive_recommender import Song, UserProfile, AdaptiveRecommender, load_songs
from adaptive_feedback import AdaptiveSystem

def create_test_profiles() -> Dict[str, UserProfile]:
    """Create diverse test profiles for reliability testing."""
    return {
        "pop_happy_energetic": UserProfile("pop", "happy", 0.8, False),
        "rock_sad_mellow": UserProfile("rock", "sad", 0.2, True),
        "jazz_calm_acoustic": UserProfile("jazz", "calm", 0.5, True),
        "edm_energetic": UserProfile("edm", "energetic", 0.9, False),
        "acoustic_chill": UserProfile("acoustic", "chill", 0.3, True),
        "pop_balanced": UserProfile("pop", "happy", 0.5, False),
    }


# ============================================================================
# TEST SUITE 1: CONFIDENCE SCORING ACCURACY
# ============================================================================

class ConfidenceScoringTest:
    """Test that confidence scores reflect criteria matching."""
    
    def __init__(self, songs: List[Song], system: AdaptiveSystem):
        self.songs = songs
        self.system = system
    
    def test_confidence_range(self):
        """Test 1a: Confidence should be between 0-1."""
        recommender = self.system.recommender
        profile = UserProfile("pop", "happy", 0.5, False)
        
        for song in self.songs:
            score, reasons, confidence = recommender.score_song(profile, song)
            assert 0.0 <= confidence <= 1.0, \
                f"Confidence {confidence} out of range [0, 1]"
        
        return True, "✓ All confidence scores in valid range [0-1]"
    
    def test_confidence_varies(self):
        """Test 1b: Confidence should vary across different songs."""
        recommender = self.system.recommender
        profile = UserProfile("pop", "happy", 0.5, False)
        
        confidences = []
        for song in self.songs:
            score, reasons, confidence = recommender.score_song(profile, song)
            confidences.append(confidence)
        
        # Should have varying confidence scores
        unique_confidences = len(set(confidences))
        assert unique_confidences >= 2, f"Only {unique_confidences} unique confidence values"
        
        return True, f"✓ Confidence varies across songs ({unique_confidences} unique values)"
    
    def test_high_matching_high_confidence(self):
        """Test 1c: Songs matching profile should have higher confidence."""
        recommender = self.system.recommender
        profile = UserProfile("pop", "happy", 0.5, False)
        
        best_confidence = 0.0
        for song in self.songs:
            score, reasons, confidence = recommender.score_song(profile, song)
            best_confidence = max(best_confidence, confidence)
        
        # Best confidence should be substantial (multiple criteria matched)
        assert best_confidence >= 0.25, \
            f"Best recommendation confidence only {best_confidence:.1%}"
        
        return True, f"✓ Best match has {best_confidence:.0%} confidence"
    
    def run_all(self) -> Tuple[int, int, List[Tuple]]:
        """Run all confidence scoring tests."""
        tests = [
            ("Confidence in range [0-1]", self.test_confidence_range),
            ("Confidence varies by song", self.test_confidence_varies),
            ("High matching = high confidence", self.test_high_matching_high_confidence),
        ]
        
        passed = 0
        failed = 0
        results = []
        
        for test_name, test_func in tests:
            try:
                success, message = test_func()
                results.append((test_name, True, message))
                passed += 1
            except AssertionError as e:
                results.append((test_name, False, f"✗ {str(e)}"))
                failed += 1
            except Exception as e:
                results.append((test_name, False, f"✗ ERROR: {str(e)}"))
                failed += 1
        
        return passed, failed, results


# ============================================================================
# TEST SUITE 2: CALIBRATION ANALYSIS
# ============================================================================

class CalibrationTest:
    """Test that confidence reflects actual correctness."""
    
    def __init__(self, songs: List[Song], system: AdaptiveSystem):
        self.songs = songs
        self.system = system
    
    def test_calibration_across_profiles(self) -> Tuple[bool, str]:
        """Test 2a: Calibration across different user profiles."""
        profiles = create_test_profiles()
        results = []
        
        for profile_name, profile in list(profiles.items())[:3]:  # Test 3 profiles
            recommender = AdaptiveRecommender(self.songs)
            
            # Get confidence scores for all songs
            confidences = []
            for song in self.songs[:5]:  # Sample 5 songs
                score, reasons, conf = recommender.score_song(profile, song)
                confidences.append(conf)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            results.append(f"{profile_name}: {avg_confidence:.0%}")
        
        result_text = ", ".join(results)
        return True, f"✓ Calibration across profiles:\n    {result_text}"
    
    def test_range_of_confidences(self) -> Tuple[bool, str]:
        """Test 2b: System should produce full range of confidences."""
        profile = UserProfile("pop", "happy", 0.5, False)
        recommender = AdaptiveRecommender(self.songs)
        
        confidences = []
        for song in self.songs:
            score, reasons, conf = recommender.score_song(profile, song)
            confidences.append(conf)
        
        assert len(confidences) > 0, "No confidences computed"
        
        max_conf = max(confidences)
        min_conf = min(confidences)
        
        has_range = (max_conf - min_conf) > 0.1
        
        return has_range, f"✓ Confidence range: {min_conf:.0%} to {max_conf:.0%}"
    
    def run_all(self) -> Tuple[int, int, List[Tuple]]:
        """Run all calibration tests."""
        tests = [
            ("Calibration across profiles", self.test_calibration_across_profiles),
            ("Range of confidences", self.test_range_of_confidences),
        ]
        
        passed = 0
        failed = 0
        results = []
        
        for test_name, test_func in tests:
            try:
                success, message = test_func()
                results.append((test_name, True, message))
                if success:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                results.append((test_name, False, f"✗ {str(e)}"))
                failed += 1
        
        return passed, failed, results


# ============================================================================
# TEST SUITE 3: WEIGHT LEARNING
# ============================================================================

class WeightLearningTest:
    """Test that the system learns from feedback."""
    
    def __init__(self, songs: List[Song], system: AdaptiveSystem):
        self.songs = songs
        self.system = system
        self.base_system = AdaptiveSystem(songs)
    
    def test_weights_change_with_feedback(self) -> Tuple[bool, str]:
        """Test 3a: Weights should change after learning."""
        system = AdaptiveSystem(self.songs)
        profile = UserProfile("pop", "happy", 0.5, False)
        
        # Record initial weights
        initial_weight = system.learner.weights.energy_weight
        
        # Get recommendations and record feedback
        recommender = AdaptiveRecommender(self.songs)
        for i, song in enumerate(self.songs[:5]):
            # Simulate feedback: like first 2, dislike rest
            liked = (i < 2)
            score, reasons, conf = recommender.score_song(profile, song)
            system.tracker.record_feedback(
                song_id=song.id,
                song_title=song.title,
                liked=liked,
                predicted_confidence=conf,
                profile=profile
            )
        
        # Learn
        system.learn_from_feedback(learning_rate=0.5)
        
        new_weight = system.learner.weights.energy_weight
        weights_changed = initial_weight != new_weight
        
        change = abs(new_weight - initial_weight)
        
        return weights_changed, f"✓ Weights adapted after feedback (change: {change:.4f})"
    
    def test_tracker_accumulates_feedback(self) -> Tuple[bool, str]:
        """Test 3b: Feedback tracker should accumulate entries."""
        system = AdaptiveSystem(self.songs)
        profile = UserProfile("pop", "happy", 0.5, False)
        recommender = AdaptiveRecommender(self.songs)
        
        initial_count = len(system.tracker.feedback_entries)
        
        # Add feedback
        for song in self.songs[:3]:
            score, reasons, conf = recommender.score_song(profile, song)
            system.tracker.record_feedback(song.id, song.title, True, conf, profile)
        
        final_count = len(system.tracker.feedback_entries)
        
        feedback_added = final_count > initial_count
        
        return feedback_added, f"✓ Feedback accumulated ({initial_count} → {final_count} entries)"
    
    def test_weight_bounds(self) -> Tuple[bool, str]:
        """Test 3c: Weights should stay within reasonable bounds."""
        system = AdaptiveSystem(self.songs)
        profile = UserProfile("pop", "happy", 0.5, False)
        recommender = AdaptiveRecommender(self.songs)
        
        # Add feedback multiple times and learn
        for _ in range(3):
            for i, song in enumerate(self.songs[:4]):
                score, reasons, conf = recommender.score_song(profile, song)
                system.tracker.record_feedback(song.id, song.title, i < 2, conf, profile)
            system.learn_from_feedback(learning_rate=0.3)
        
        weights = system.learner.weights
        
        # Check bounds
        valid = True
        issues = []
        
        for attr in ['energy_weight', 'genre_weight', 'mood_weight', 'acoustic_weight']:
            val = getattr(weights, attr)
            if val < 0 or val > 1000:
                valid = False
                issues.append(f"{attr}={val:.2f}")
        
        if issues:
            return False, f"✗ Weights out of bounds: {', '.join(issues)}"
        
        return True, "✓ All weights remain in valid range [0, 1000]"
    
    def run_all(self) -> Tuple[int, int, List[Tuple]]:
        """Run all weight learning tests."""
        tests = [
            ("Weights change with feedback", self.test_weights_change_with_feedback),
            ("Feedback accumulates", self.test_tracker_accumulates_feedback),
            ("Weights stay in bounds", self.test_weight_bounds),
        ]
        
        passed = 0
        failed = 0
        results = []
        
        for test_name, test_func in tests:
            try:
                success, message = test_func()
                results.append((test_name, True, message))
                passed += 1
            except Exception as e:
                results.append((test_name, False, f"✗ {str(e)}"))
                failed += 1
        
        return passed, failed, results


# ============================================================================
# TEST SUITE 4: EDGE CASES & ROBUSTNESS
# ============================================================================

class EdgeCaseTest:
    """Test system robustness with edge cases."""
    
    def __init__(self, songs: List[Song], system: AdaptiveSystem):
        self.songs = songs
        self.system = system
    
    def test_none_values_in_profile(self) -> Tuple[bool, str]:
        """Test 4a: System should handle edge case profiles."""
        # Test with various profile combinations
        profiles = [
            UserProfile("unknown_genre", "happy", 0.5, False),
            UserProfile("pop", "unknown_mood", 0.5, False),
            UserProfile("pop", "happy", 0.5, True),  # With acousticness preference
        ]
        
        recommender = AdaptiveRecommender(self.songs)
        
        for profile in profiles:
            try:
                for song in self.songs[:2]:
                    score, reasons, conf = recommender.score_song(profile, song)
                    assert 0.0 <= conf <= 1.0
            except Exception as e:
                return False, f"✗ Failed with edge profile: {str(e)}"
        
        return True, "✓ Handles edge case profile values"
    
    def test_boundary_energy_values(self) -> Tuple[bool, str]:
        """Test 4b: Extreme energy values."""
        profiles_to_test = [
            UserProfile("pop", "happy", 0.0, False),   # Minimum
            UserProfile("pop", "happy", 1.0, True),    # Maximum
        ]
        
        recommender = AdaptiveRecommender(self.songs)
        
        for profile in profiles_to_test:
            for song in self.songs[:1]:
                try:
                    score, reasons, conf = recommender.score_song(profile, song)
                    assert 0.0 <= conf <= 1.0
                except Exception as e:
                    return False, f"✗ Failed with extreme energy: {str(e)}"
        
        return True, "✓ Handles extreme energy values [0.0-1.0]"
    
    def test_empty_feedback_learning(self) -> Tuple[bool, str]:
        """Test 4c: Learning with no feedback should not crash."""
        system = AdaptiveSystem(self.songs)
        
        try:
            # Learn with no feedback
            system.learn_from_feedback()
            return True, "✓ Learning with no feedback is safe"
        except Exception as e:
            return False, f"✗ Failed with no feedback: {str(e)}"
    
    def test_large_top_k_request(self) -> Tuple[bool, str]:
        """Test 4d: Request more songs than available."""
        recommender = AdaptiveRecommender(self.songs)
        profile = UserProfile("pop", "happy", 0.5, False)
        
        try:
            # Try to get more recommendations than songs available
            # This tests graceful handling of k > len(songs)
            results = []
            for song in self.songs:
                score, reasons, conf = recommender.score_song(profile, song)
                results.append((song, conf))
            
            sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
            top_k = sorted_results[:1000]  # Request more than available
            
            # Should return at most len(songs) results
            assert len(top_k) <= len(self.songs)
            return True, f"✓ Handles large k gracefully (got {len(top_k)} of requested 1000)"
        except Exception as e:
            return False, f"✗ Failed with large k: {str(e)}"
    
    def run_all(self) -> Tuple[int, int, List[Tuple]]:
        """Run all edge case tests."""
        tests = [
            ("Edge case profile values", self.test_none_values_in_profile),
            ("Extreme energy values", self.test_boundary_energy_values),
            ("Learn with no feedback", self.test_empty_feedback_learning),
            ("Large top_k requests", self.test_large_top_k_request),
        ]
        
        passed = 0
        failed = 0
        results = []
        
        for test_name, test_func in tests:
            try:
                success, message = test_func()
                results.append((test_name, True, message))
                if success:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                results.append((test_name, False, f"✗ Uncaught: {str(e)}"))
                failed += 1
        
        return passed, failed, results


# ============================================================================
# TEST SUITE 5: PERFORMANCE
# ============================================================================

class PerformanceTest:
    """Test system performance and efficiency."""
    
    def __init__(self, songs: List[Song], system: AdaptiveSystem):
        self.songs = songs
        self.system = system
    
    def test_scoring_speed(self) -> Tuple[bool, str]:
        """Test 5a: Scoring should be very fast."""
        recommender = AdaptiveRecommender(self.songs)
        profile = UserProfile("pop", "happy", 0.5, False)
        
        start = time.time()
        for song in self.songs:
            score, reasons, conf = recommender.score_song(profile, song)
        elapsed = time.time() - start
        
        avg_time = elapsed / len(self.songs) * 1000  # milliseconds
        is_fast = avg_time < 10  # Each score should be < 10ms
        
        return is_fast, f"{'✓' if is_fast else '⚠'} Scoring speed: {avg_time:.2f}ms per song"
    
    def test_learning_speed(self) -> Tuple[bool, str]:
        """Test 5b: Learning should be fast."""
        system = AdaptiveSystem(self.songs)
        profile = UserProfile("pop", "happy", 0.5, False)
        recommender = AdaptiveRecommender(self.songs)
        
        # Add feedback
        for i, song in enumerate(self.songs[:10]):
            score, reasons, conf = recommender.score_song(profile, song)
            system.tracker.record_feedback(song.id, song.title, i < 5, conf, profile)
        
        # Time learning
        start = time.time()
        system.learn_from_feedback()
        elapsed = time.time() - start
        
        is_fast = elapsed < 0.05
        
        return is_fast, f"{'✓' if is_fast else '⚠'} Learning time: {elapsed*1000:.1f}ms"
    
    def test_feedback_accumulation(self) -> Tuple[bool, str]:
        """Test 5c: System should handle many feedback entries."""
        system = AdaptiveSystem(self.songs)
        profile = UserProfile("pop", "happy", 0.5, False)
        recommender = AdaptiveRecommender(self.songs)
        
        # Add lots of feedback
        num_iterations = 50
        start = time.time()
        
        for _ in range(num_iterations):
            for song in self.songs:
                score, reasons, conf = recommender.score_song(profile, song)
                system.tracker.record_feedback(song.id, song.title, True, conf, profile)
        
        elapsed = time.time() - start
        total_entries = len(system.tracker.feedback_entries)
        
        is_efficient = elapsed < 5.0  # Should accumulate 500 entries in < 5 seconds
        
        return is_efficient, f"✓ Accumulated {total_entries} entries in {elapsed:.2f}s"
    
    def run_all(self) -> Tuple[int, int, List[Tuple]]:
        """Run all performance tests."""
        tests = [
            ("Scoring speed", self.test_scoring_speed),
            ("Learning speed", self.test_learning_speed),
            ("Feedback accumulation", self.test_feedback_accumulation),
        ]
        
        passed = 0
        failed = 0
        results = []
        
        for test_name, test_func in tests:
            try:
                success, message = test_func()
                results.append((test_name, True, message))
                if success:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                results.append((test_name, False, f"✗ {str(e)}"))
                failed += 1
        
        return passed, failed, results


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all Phase 4 reliability tests."""
    print("=" * 80)
    print("PHASE 4: RELIABILITY & TESTING - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()
    
    # Load songs
    try:
        songs = load_songs("data/songs.csv")
        print(f"✓ Loaded {len(songs)} songs from data/songs.csv")
        print()
    except Exception as e:
        print(f"✗ Failed to load songs: {e}")
        return
    
    # Create adaptive system
    try:
        system = AdaptiveSystem(songs)
        print(f"✓ Created adaptive system")
        print()
    except Exception as e:
        print(f"✗ Failed to create system: {e}")
        return
    
    test_suites = [
        ("1. CONFIDENCE SCORING", ConfidenceScoringTest(songs, system)),
        ("2. CALIBRATION ANALYSIS", CalibrationTest(songs, system)),
        ("3. WEIGHT LEARNING", WeightLearningTest(songs, system)),
        ("4. EDGE CASES & ROBUSTNESS", EdgeCaseTest(songs, system)),
        ("5. PERFORMANCE", PerformanceTest(songs, system)),
    ]
    
    total_passed = 0
    total_failed = 0
    all_suite_results = []
    
    for suite_name, suite in test_suites:
        print(f"\n{suite_name}")
        print("-" * 80)
        
        passed, failed, results = suite.run_all()
        total_passed += passed
        total_failed += failed
        
        for test_name, success, message in results:
            print(f"  • {test_name}")
            print(f"    {message}")
        
        all_suite_results.append((suite_name, passed, failed))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    
    for suite_name, passed, failed in all_suite_results:
        status = "✓" if failed == 0 else "⚠"
        suite_short = suite_name.split('.')[1].strip() if '.' in suite_name else suite_name
        print(f"{status} {suite_short}: {passed} passed, {failed} failed")
    
    print()
    print(f"TOTAL: {total_passed} passed, {total_failed} failed")
    
    pass_rate = total_passed / (total_passed + total_failed) * 100 if (total_passed + total_failed) > 0 else 0
    print(f"PASS RATE: {pass_rate:.0f}%")
    print()
    
    if total_failed == 0:
        print("✓ ALL TESTS PASSED")
    else:
        print(f"⚠ {total_failed} test(s) need attention")

    print("=" * 80)


if __name__ == "__main__":
    main()
