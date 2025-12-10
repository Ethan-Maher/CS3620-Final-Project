#!/usr/bin/env python
"""
Script to import data from CSV files.
Usage: python import_from_csv.py <csv_file> <data_type>

Example:
  python import_from_csv.py movies.csv films
  python import_from_csv.py directors.csv directors
"""
import os
import sys
import csv
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databases_proj.settings')
django.setup()

from api.models import (
    MovieGenre, MovieDirector, MovieLanguage, AllFilms, Actors
)

def import_directors(csv_file):
    """Import directors from CSV"""
    print(f"Importing directors from {csv_file}...")
    count = 0
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            director_name = row.get('director_name') or row.get('name')
            if director_name:
                director, created = MovieDirector.objects.get_or_create(
                    director_name=director_name.strip()
                )
                if created:
                    count += 1
                    print(f"  Created: {director_name}")
    print(f"✓ Imported {count} directors")
    return count

def import_genres(csv_file):
    """Import genres from CSV"""
    print(f"Importing genres from {csv_file}...")
    count = 0
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            genre_name = row.get('genre_name') or row.get('name')
            if genre_name:
                genre, created = MovieGenre.objects.get_or_create(
                    genre_name=genre_name.strip()
                )
                if created:
                    count += 1
                    print(f"  Created: {genre_name}")
    print(f"✓ Imported {count} genres")
    return count

def import_films(csv_file):
    """Import films from CSV
    
    Expected CSV columns:
    - film_name (required)
    - director_name (optional, will create if doesn't exist)
    - year (optional)
    - duration (optional)
    - genre_name (optional, will create if doesn't exist)
    - language_name (optional, will create if doesn't exist)
    - actors (optional, comma-separated)
    """
    print(f"Importing films from {csv_file}...")
    count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            film_name = row.get('film_name') or row.get('title') or row.get('name')
            if not film_name:
                continue
            
            # Get or create director
            director = None
            director_name = row.get('director_name') or row.get('director')
            if director_name:
                director, _ = MovieDirector.objects.get_or_create(
                    director_name=director_name.strip()
                )
            
            # Get or create genre
            genre = None
            genre_name = row.get('genre_name') or row.get('genre')
            if genre_name:
                genre, _ = MovieGenre.objects.get_or_create(
                    genre_name=genre_name.strip()
                )
            
            # Get or create language
            language = None
            language_name = row.get('language_name') or row.get('language')
            if language_name:
                language, _ = MovieLanguage.objects.get_or_create(
                    language_name=language_name.strip()
                )
            
            # Parse year and duration
            year = None
            if row.get('year'):
                try:
                    year = int(row['year'])
                except:
                    pass
            
            duration = None
            if row.get('duration') or row.get('runtime'):
                try:
                    duration = int(row.get('duration') or row.get('runtime'))
                except:
                    pass
            
            # Create film
            film, created = AllFilms.objects.get_or_create(
                film_name=film_name.strip(),
                defaults={
                    'director_id': director,
                    'year': year,
                    'duration': duration,
                    'genre_id': genre,
                    'language_id': language
                }
            )
            
            if created:
                count += 1
                print(f"  Created: {film_name}")
                
                # Add actors if provided
                actors_str = row.get('actors') or row.get('cast')
                if actors_str:
                    actors_list = [a.strip() for a in actors_str.split(',') if a.strip()]
                    for actor_name in actors_list:
                        Actors.objects.get_or_create(
                            actor_name=actor_name,
                            film_id=film
                        )
            else:
                print(f"  Already exists: {film_name}")
    
    print(f"✓ Imported {count} films")
    return count

def main():
    if len(sys.argv) < 3:
        print("Usage: python import_from_csv.py <csv_file> <data_type>")
        print("\nData types:")
        print("  - directors: Import directors")
        print("  - genres: Import genres")
        print("  - films: Import films (with directors, genres, actors)")
        print("\nExample:")
        print("  python import_from_csv.py movies.csv films")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    data_type = sys.argv[2].lower()
    
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found")
        sys.exit(1)
    
    if data_type == 'directors':
        import_directors(csv_file)
    elif data_type == 'genres':
        import_genres(csv_file)
    elif data_type == 'films':
        import_films(csv_file)
    else:
        print(f"Error: Unknown data type '{data_type}'")
        print("Valid types: directors, genres, films")
        sys.exit(1)

if __name__ == '__main__':
    main()

