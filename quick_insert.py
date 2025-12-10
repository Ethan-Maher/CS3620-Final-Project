#!/usr/bin/env python
"""
Quick script to insert data interactively or from a simple format.
Run with: python quick_insert.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databases_proj.settings')
django.setup()

from api.models import (
    MovieGenre, MovieDirector, MovieLanguage, AllFilms, Actors
)

def insert_movie_interactive():
    """Interactively insert a movie"""
    print("\n=== Insert New Movie ===")
    
    # Get film name
    film_name = input("Film name: ").strip()
    if not film_name:
        print("Film name is required!")
        return
    
    # Get or create director
    director_name = input("Director name (or press Enter to skip): ").strip()
    director = None
    if director_name:
        director, _ = MovieDirector.objects.get_or_create(director_name=director_name)
    
    # Get or create genre
    genre_name = input("Genre name (or press Enter to skip): ").strip()
    genre = None
    if genre_name:
        genre, _ = MovieGenre.objects.get_or_create(genre_name=genre_name)
    
    # Get year
    year = None
    year_str = input("Year (or press Enter to skip): ").strip()
    if year_str:
        try:
            year = int(year_str)
        except:
            print("Invalid year, skipping...")
    
    # Get duration
    duration = None
    duration_str = input("Duration in minutes (or press Enter to skip): ").strip()
    if duration_str:
        try:
            duration = int(duration_str)
        except:
            print("Invalid duration, skipping...")
    
    # Get language
    language_name = input("Language (or press Enter to skip): ").strip()
    language = None
    if language_name:
        language, _ = MovieLanguage.objects.get_or_create(language_name=language_name)
    
    # Create film
    film, created = AllFilms.objects.get_or_create(
        film_name=film_name,
        defaults={
            'director_id': director,
            'year': year,
            'duration': duration,
            'genre_id': genre,
            'language_id': language
        }
    )
    
    if created:
        print(f"\n✓ Created film: {film_name}")
    else:
        print(f"\n⚠ Film already exists: {film_name}")
    
    # Add actors
    actors_str = input("Actors (comma-separated, or press Enter to skip): ").strip()
    if actors_str:
        actors_list = [a.strip() for a in actors_str.split(',') if a.strip()]
        for actor_name in actors_list:
            Actors.objects.get_or_create(actor_name=actor_name, film_id=film)
        print(f"✓ Added {len(actors_list)} actors")

def main():
    print("=" * 60)
    print("Quick Data Insertion Tool")
    print("=" * 60)
    print("\nOptions:")
    print("1. Insert a movie interactively")
    print("2. Show current data counts")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            insert_movie_interactive()
        elif choice == '2':
            print(f"\nCurrent data:")
            print(f"  Films: {AllFilms.objects.count()}")
            print(f"  Directors: {MovieDirector.objects.count()}")
            print(f"  Genres: {MovieGenre.objects.count()}")
            print(f"  Actors: {Actors.objects.count()}")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

