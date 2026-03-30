"""
Phase 4: Evaluation & Bias Analysis

This script tests the recommender with multiple user profiles to identify:
- What recommendations work well
- Where the algorithm has biases
- Edge cases and limitations
"""

from recommender import load_songs, recommend_songs, Recommender, Song, UserProfile


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def evaluate_profile(songs_data: list, profile_name: str, user_prefs: dict) -> None:
    """
    Evaluate recommender for a single user profile.
    
    Args:
        songs_data: List of song dictionaries
        profile_name: Human-readable profile name
        user_prefs: User preference dictionary
    """
    print_section(f"Profile: {profile_name}")
    print(f"Preferences: {user_prefs['genre']} + {user_prefs['mood']} + energy {user_prefs['energy']}")
    if 'likes_acoustic' in user_prefs:
        print(f"Acoustic preference: {'likes acoustic' if user_prefs['likes_acoustic'] else 'prefers NOT acoustic'}")
    print()
    
    recommendations = recommend_songs(user_prefs, songs_data, k=5)
    
    for i, (song, score, reasons) in enumerate(recommendations, 1):
        print(f"{i}. {song['title'].upper()}")
        print(f"   Artist:  {song['artist']}")
        print(f"   Genre/Mood: {song['genre']} / {song['mood']}")
        print(f"   Energy: {song['energy']:.2f}")
        print(f"   Score:   {score:.0f}/125")
        print(f"   Why: {' · '.join(reasons) if reasons else 'No matching criteria'}")
        print()


def analyze_edge_cases(songs_data: list) -> None:
    """Run edge case experiments."""
    print_section("Experiment 1: Genre Veto vs. Other Features")
    print("Question: Can energy + mood compensate for wrong genre?\n")
    
    # Profile that doesn't match any genre exactly but has good energy/mood
    profile = {
        "genre": "reggae",  # NOT in dataset
        "mood": "happy",    # EXISTS in dataset
        "energy": 0.80,     # HIGH energy target
        "likes_acoustic": False
    }
    
    print(f"Profile: reggae (NOT in dataset) + happy + high energy\n")
    recommendations = recommend_songs(profile, songs_data, k=3)
    
    for i, (song, score, reasons) in enumerate(recommendations, 1):
        print(f"{i}. {song['title']} - Score: {score:.0f}/125")
        print(f"   Genre: {song['genre']} (NOT reggae - no genre match!)")
        print(f"   Mood: {song['mood']} (mood match: {'happy' in str(reasons)})")
        print(f"   Energy: {song['energy']:.2f} (energy match: {'Energy match' in str(reasons)})")
        print()
    
    print("\nObservation: Songs without reggae genre can still score well through other features!")
    print("This suggests genre alone doesn't completely block recommendations.\n")


def analyze_acoustic_bias(songs_data: list) -> None:
    """Analyze acoustic preference bias."""
    print_section("Experiment 2: Acoustic Preference Bias")
    print("Question: How does acousticness affect rankings?\n")
    
    profile_acoustic = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": True  # LIKES acoustic
    }
    
    profile_electronic = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": False  # DISLIKES acoustic
    }
    
    print("A. User who LIKES acoustic:\n")
    recs_acoustic = recommend_songs(profile_acoustic, songs_data, k=3)
    for i, (song, score, reasons) in enumerate(recs_acoustic, 1):
        print(f"{i}. {song['title']} - Acoustic: {song['acousticness']:.2f} - Score: {score:.0f}/125")
    
    print("\n\nB. Same user but DISLIKES acoustic:\n")
    recs_electronic = recommend_songs(profile_electronic, songs_data, k=3)
    for i, (song, score, reasons) in enumerate(recs_electronic, 1):
        print(f"{i}. {song['title']} - Acoustic: {song['acousticness']:.2f} - Score: {score:.0f}/125")
    
    print("\n\nObservation: Acousticness preference only adds 10 points (8% of max score).")
    print("In this case with exact genre/mood/energy matches, acousticness has minimal impact.")
    print("But when other factors are tied, it becomes a tiebreaker.\n")


def identify_biases(songs_data: list) -> None:
    """Identify algorithmic biases."""
    print_section("Identified Biases & Limitations")
    
    print("BIAS 1: Genre Dominance in High-Mismatch Cases")
    print("-" * 80)
    print("When user's genre doesn't match any song, they need BOTH mood AND energy matches.")
    print("Example: A user who likes 'reggae' (not in dataset) must compromise on mood/energy.")
    print()
    
    print("BIAS 2: Energy Similarity is Binary (0-40, not 0-40 gradual)")
    print("-" * 80)
    print("Songs within 0.3 of target energy get full +40 points (no gradient).")
    print("Energy 0.51 vs 0.49 gets same same +40 as energy 0.80 vs 0.50.")
    print("This could be improved with scoring: (1 - |diff|/0.3) * 40")
    print()
    
    print("BIAS 3: Acousticness Heavily Weighted for Low-Score Songs")
    print("-" * 80)
    print("For songs that don't match genre/mood, acousticness (+10) becomes 20% of their score.")
    print("This might over-reward acoustic songs when genre/mood don't match.")
    print()
    
    print("BIAS 4: Limited Dataset (10 songs, 7 genres)")
    print("-" * 80)
    print("With only 10 songs, users interested in niche genres will have few/no matches.")
    print("Real recommenders have millions of songs to mitigate this.")
    print()


def main() -> None:
    """Run Phase 4 evaluation."""
    songs = load_songs("data/songs.csv")
    
    print("\n" + "="*80)
    print("🎵 PHASE 4: EVALUATION & BIAS ANALYSIS")
    print("="*80)
    
    # Profile 1: Current default
    evaluate_profile(
        songs, 
        "Pop Lover (High Energy)",
        {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.80,
            "likes_acoustic": False
        }
    )
    
    # Profile 2: Lofi/Chill/Acoustic
    evaluate_profile(
        songs,
        "Lo-Fi Listener (Chill & Acoustic)",
        {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "likes_acoustic": True
        }
    )
    
    # Profile 3: Rock/Intense/Electronic
    evaluate_profile(
        songs,
        "Rock Fan (High Energy, Not Acoustic)",
        {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.90,
            "likes_acoustic": False
        }
    )
    
    # Run experiments
    analyze_edge_cases(songs)
    analyze_acoustic_bias(songs)
    
    # Identify biases
    identify_biases(songs)
    
    print_section("Summary")
    print("✅ The recommender works well for users whose genre exists in the dataset.")
    print("⚠️  Limitations emerge when genre is niche or doesn't match any song.")
    print("⚠️  Energy scoring is binary (all-or-nothing), not gradual.")
    print("⚠️  Small dataset limits recommendation diversity.\n")


if __name__ == "__main__":
    main()
