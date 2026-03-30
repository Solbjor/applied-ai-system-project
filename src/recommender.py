from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def score_song(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """
        Calculate a score for a song based on user preferences.
        Returns (score, reasons_list) where reasons_list explains each contribution.
        
        Scoring formula (max 125 points):
        - Genre match: +35 points
        - Mood match: +40 points
        - Energy similarity (within 0.3): +40 points
        - Acousticness preference: +10 points
        """
        score = 0.0
        reasons = []
        
        # Genre match: +35 if exact match
        if song.genre == user.favorite_genre:
            score += 35
            reasons.append(f"Genre match (+35)")
        
        # Mood match: +40 if exact match
        if song.mood == user.favorite_mood:
            score += 40
            reasons.append(f"Mood match (+40)")
        
        # Energy similarity: +40 if within 0.3 tolerance
        if abs(song.energy - user.target_energy) <= 0.3:
            score += 40
            reasons.append(f"Energy match ({song.energy:.2f} vs {user.target_energy:.2f}) (+40)")
        
        # Acousticness preference: +10 if matches user preference
        if user.likes_acoustic and song.acousticness > 0.7:
            score += 10
            reasons.append(f"Acoustic (+10)")
        elif not user.likes_acoustic and song.acousticness < 0.3:
            score += 10
            reasons.append(f"Not acoustic ({song.acousticness:.2f}) (+10)")
        
        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Score all songs and return top-k sorted by score (descending).
        """
        # Score each song
        scored_songs = []
        for song in self.songs:
            score, reasons = self.score_song(user, song)
            scored_songs.append((song, score, reasons))
        
        # Sort by score descending
        scored_songs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k songs
        return [song for song, score, reasons in scored_songs[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """
        Explain why a song received its score, listing all reasons.
        """
        score, reasons = self.score_song(user, song)
        reasons_str = " | ".join(reasons) if reasons else "No matching criteria"
        explanation = f"Score: {score:.0f}/125 — {reasons_str}"
        return explanation

def load_songs(csv_path: str) -> List[Dict]:
    """
    Load songs from a CSV file and convert to dictionaries with proper types.
    
    Args:
        csv_path: Path to the CSV file containing song data
        
    Returns:
        List of song dictionaries with numeric fields converted to floats
    """
    songs = []
    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert numeric fields from strings to floats
                song = {
                    'id': int(row['id']),
                    'title': row['title'],
                    'artist': row['artist'],
                    'genre': row['genre'],
                    'mood': row['mood'],
                    'energy': float(row['energy']),
                    'tempo_bpm': float(row['tempo_bpm']),
                    'valence': float(row['valence']),
                    'danceability': float(row['danceability']),
                    'acousticness': float(row['acousticness']),
                }
                songs.append(song)
        print(f"Successfully loaded {len(songs)} songs from {csv_path}")
    except FileNotFoundError:
        print(f"Error: Could not find file {csv_path}")
    except Exception as e:
        print(f"Error loading songs: {e}")
    
    return songs

def score_song_functional(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song with detailed breakdown of contributing factors.
    
    Scoring formula (max 125 points):
    - Genre match: +35 points
    - Mood match: +40 points  
    - Energy similarity (within 0.3): +40 points
    - Acousticness preference: +10 points
    
    Args:
        user_prefs: User preference dictionary with 'genre', 'mood', 'energy', 'likes_acoustic'
        song: Song dictionary to score
        
    Returns:
        Tuple of (score: float, reasons: List[str])
        Reasons contain strings like "Genre match (+35)" showing score breakdown
    """
    score = 0.0
    reasons = []
    
    # Genre match: +35 if exact match
    if song['genre'] == user_prefs.get('genre'):
        score += 35
        reasons.append(f"Genre match (+35)")
    
    # Mood match: +40 if exact match
    if song['mood'] == user_prefs.get('mood'):
        score += 40
        reasons.append(f"Mood match (+40)")
    
    # Energy similarity: +40 if within 0.3 tolerance
    target_energy = user_prefs.get('energy', 0.5)
    if abs(song['energy'] - target_energy) <= 0.3:
        score += 40
        reasons.append(f"Energy match ({song['energy']:.2f} vs {target_energy:.2f}) (+40)")
    
    # Acousticness preference: +10 if matches user preference
    likes_acoustic = user_prefs.get('likes_acoustic', False)
    if likes_acoustic and song['acousticness'] > 0.7:
        score += 10
        reasons.append(f"Acoustic (+10)")
    elif not likes_acoustic and song['acousticness'] < 0.3:
        score += 10
        reasons.append(f"Not acoustic ({song['acousticness']:.2f}) (+10)")
    
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """
    Generate top-k song recommendations based on user preferences.
    
    Args:
        user_prefs: Dictionary with keys 'genre', 'mood', 'energy', optional 'likes_acoustic'
        songs: List of song dictionaries to score and rank
        k: Number of recommendations to return (default 5)
        
    Returns:
        List of (song_dict, score, reasons_list) tuples sorted by score descending.
        Reasons list contains strings like "Genre match (+35)" explaining score composition.
    """
    # Score each song
    scored_songs = []
    for song in songs:
        score, reasons = score_song_functional(user_prefs, song)
        scored_songs.append((song, score, reasons))
    
    # Sort by score descending
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    
    # Return top-k
    return scored_songs[:k]
