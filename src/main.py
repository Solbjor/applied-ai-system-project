"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 80)
    print("🎵 MUSIC RECOMMENDER SIMULATION")
    print("=" * 80)
    print(f"User Profile: {user_prefs['genre']} + {user_prefs['mood']} + energy {user_prefs['energy']}\n")
    
    for i, rec in enumerate(recommendations, 1):
        song, score, reasons = rec
        print(f"{i}. {song['title'].upper()}")
        print(f"   Artist:  {song['artist']}")
        print(f"   Score:   {score:.0f}/125")
        print(f"   Reasons: {' · '.join(reasons) if reasons else 'No matching criteria'}")
        print()
    
    print("=" * 80)


if __name__ == "__main__":
    main()
