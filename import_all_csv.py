#!/usr/bin/env python
"""
Import all CSV files from the data/csv folder.
Detects file type and imports accordingly.

Usage: python import_all_csv.py
"""
import os
import sys
import csv
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databases_proj.settings')
django.setup()

from api.models import (
    MovieGenre, MovieDirector, MovieLanguage, AllFilms, Actors,
    ShowGenre, ShowCertificate, AllShows, ActedIn, AuditLog
)

# Get the CSV folder path
BASE_DIR = Path(__file__).resolve().parent
CSV_FOLDER = BASE_DIR / 'data' / 'csv'

def detect_delimiter(csv_file):
    """Detect CSV delimiter (comma or semicolon)"""
    with open(csv_file, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if ';' in first_line:
            return ';'
        return ','

def detect_file_type(csv_file):
    """Detect what type of data is in the CSV file based on filename first, then column structure"""
    filename = csv_file.name.lower()
    
    # Explicit filename-based detection (most reliable)
    if 'letterboxd_movies' in filename or 'movies' in filename:
        return 'films'
    if 'tv_shows_only_multi_year' in filename or 'tv_only' in filename or 'tv' in filename or 'show' in filename:
        return 'shows'
    
    # Fallback to column-based detection
    delimiter = detect_delimiter(csv_file)
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        headers = [h.lower() for h in reader.fieldnames or []]
        
        # Check for film/movie indicators
        if any(h in headers for h in ['film_name', 'title', 'name', 'movie_name']):
            if any(h in headers for h in ['director_name', 'director']):
                return 'films'
            elif any(h in headers for h in ['show_name', 'show_id']):
                return 'shows'
            else:
                # Could be either, check for show-specific fields
                if any(h in headers for h in ['cert_rating', 'certificate', 'years']):
                    return 'shows'
                return 'films'
        
        # Check for director indicators
        if any(h in headers for h in ['director_name', 'director']):
            if 'film_name' not in headers and 'title' not in headers:
                return 'directors'
        
        # Check for genre indicators
        if any(h in headers for h in ['genre_name', 'genre']):
            if 'film_name' not in headers and 'show_name' not in headers:
                return 'genres'
        
        # Default to films if we can't determine
        return 'films'

def import_directors(csv_file):
    """Import directors from CSV"""
    print(f"\nImporting directors from: {csv_file.name}")
    count = 0
    errors = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                director_name = (row.get('director_name') or row.get('name') or 
                               row.get('director') or '').strip()
                if director_name:
                    try:
                        director, created = MovieDirector.objects.get_or_create(
                            director_name=director_name
                        )
                        if created:
                            count += 1
                            print(f"  Created: {director_name}")
                    except Exception as e:
                        errors += 1
                        print(f"  Error on row {row_num}: {e}")
        
        print(f"  Imported {count} directors ({errors} errors)")
        return count
    except Exception as e:
        print(f"  Failed to import: {e}")
        return 0

def import_genres(csv_file):
    """Import genres from CSV"""
    print(f"\nImporting genres from: {csv_file.name}")
    count = 0
    errors = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                genre_name = (row.get('genre_name') or row.get('name') or 
                            row.get('genre') or '').strip()
                if genre_name:
                    try:
                        genre, created = MovieGenre.objects.get_or_create(
                            genre_name=genre_name
                        )
                        if created:
                            count += 1
                            print(f"  Created: {genre_name}")
                    except Exception as e:
                        errors += 1
                        print(f"  Error on row {row_num}: {e}")
        
        print(f"  Imported {count} genres ({errors} errors)")
        return count
    except Exception as e:
        print(f"  Failed to import: {e}")
        return 0

def import_films(csv_file):
    """Import films from CSV"""
    print(f"\nImporting films from: {csv_file.name}")
    from api.models import AuditLog
    AuditLog.objects.create(
        changes_to_data=f"Data import started: Importing films from {csv_file.name}"
    )
    count = 0
    errors = 0
    
    delimiter = detect_delimiter(csv_file)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row_num, row in enumerate(reader, start=2):
                try:
                    film_name = (row.get('film_name') or row.get('title') or 
                                row.get('name') or row.get('movie_name') or '').strip()
                    if not film_name:
                        continue
                    
                    # Get or create director
                    director = None
                    director_name = (row.get('director_name') or row.get('director') or '').strip()
                    if director_name:
                        director, _ = MovieDirector.objects.get_or_create(
                            director_name=director_name
                        )
                    
                    # Get or create genre - handle comma-separated genres
                    genre = None
                    genre_name = (row.get('genre_name') or row.get('genre') or 
                                 row.get('primary_genre') or row.get('genres') or '').strip()
                    if genre_name:
                        # Take first genre if comma-separated
                        first_genre = genre_name.split(',')[0].strip()
                        genre, _ = MovieGenre.objects.get_or_create(
                            genre_name=first_genre
                        )
                    
                    # Get or create language
                    language = None
                    language_name = (row.get('language_name') or row.get('language') or '').strip()
                    if language_name:
                        language, _ = MovieLanguage.objects.get_or_create(
                            language_name=language_name
                        )
                    
                    # Parse year - handle float years like "2019.0"
                    year = None
                    if row.get('year'):
                        try:
                            year_str = str(row['year']).strip().replace('(', '').replace(')', '')
                            year = int(float(year_str))
                        except:
                            pass
                    
                    # Parse duration - handle "30 min" format
                    duration = None
                    duration_str = row.get('duration') or row.get('runtime') or ''
                    if duration_str:
                        try:
                            # Extract number from strings like "30 min" or "133.0"
                            import re
                            duration_match = re.search(r'(\d+)', str(duration_str))
                            if duration_match:
                                duration = int(duration_match.group(1))
                        except:
                            pass
                    
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
                        count += 1
                        if count % 100 == 0:
                            print(f"  ... {count} films imported so far")
                        
                        # Add actors if provided - handle list format like "['Name, ', 'Name, ']"
                        actors_str = row.get('actors') or row.get('cast') or row.get('stars') or ''
                        if actors_str:
                            # Clean up list format
                            actors_str = str(actors_str).strip()
                            # Remove brackets and quotes
                            actors_str = actors_str.replace('[', '').replace(']', '').replace("'", '').replace('"', '')
                            # Split by comma
                            actors_list = [a.strip().rstrip(',') for a in actors_str.split(',') if a.strip()]
                            for actor_name in actors_list:
                                if actor_name and len(actor_name) > 1:
                                    Actors.objects.get_or_create(
                                        actor_name=actor_name,
                                        film_id=film
                                    )
                    else:
                        if count < 10:  # Only show first few duplicates
                            print(f"  Already exists: {film_name}")
                        
                except Exception as e:
                    errors += 1
                    print(f"  Error on row {row_num}: {e}")
        
        print(f"  Imported {count} films ({errors} errors)")
        if count > 0:
            AuditLog.objects.create(
                changes_to_data=f"Data import completed: Imported {count} films from {csv_file.name} ({errors} errors)"
            )
        return count
    except Exception as e:
        print(f"  Failed to import: {e}")
        import traceback
        traceback.print_exc()
        AuditLog.objects.create(
            changes_to_data=f"Data import failed: Error importing films from {csv_file.name} - {str(e)}"
        )
        return 0

def import_shows(csv_file):
    """Import shows from CSV"""
    print(f"\nImporting shows from: {csv_file.name}")
    AuditLog.objects.create(
        changes_to_data=f"Data import started: Importing shows from {csv_file.name}"
    )
    count = 0
    errors = 0
    
    delimiter = detect_delimiter(csv_file)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row_num, row in enumerate(reader, start=2):
                try:
                    show_name = (row.get('show_name') or row.get('title') or 
                               row.get('name') or '').strip()
                    if not show_name:
                        continue
                    
                    # Get or create certificate
                    cert = None
                    cert_rating = (row.get('cert_rating') or row.get('certificate') or '').strip()
                    if cert_rating:
                        cert, _ = ShowCertificate.objects.get_or_create(
                            cert_rating=cert_rating
                        )
                    
                    # Get or create genre - handle comma-separated
                    genre = None
                    genre_name = (row.get('genre_name') or row.get('genre') or '').strip()
                    if genre_name:
                        # Take first genre if comma-separated
                        first_genre = genre_name.split(',')[0].strip()
                        genre, _ = ShowGenre.objects.get_or_create(
                            genre_name=first_genre
                        )
                    
                    # Parse duration - handle "30 min" format
                    duration = None
                    duration_str = row.get('duration') or ''
                    if duration_str:
                        try:
                            import re
                            duration_match = re.search(r'(\d+)', str(duration_str))
                            if duration_match:
                                duration = int(duration_match.group(1))
                        except:
                            pass
                    
                    # Parse rating
                    rating = None
                    if row.get('rating'):
                        try:
                            rating = float(row['rating'])
                        except:
                            pass
                    
                    # Parse year for years field
                    year = None
                    if row.get('year'):
                        try:
                            year_str = str(row['year']).strip().replace('(', '').replace(')', '')
                            year = int(float(year_str))
                        except:
                            pass
                    
                    years = row.get('years', '').strip()
                    if not years and year:
                        years = str(year)
                    
                    # Create show
                    show, created = AllShows.objects.get_or_create(
                        show_name=show_name,
                        defaults={
                            'duration': duration,
                            'cert_id': cert,
                            'rating': rating,
                            'genre_id': genre,
                            'years': years
                        }
                    )
                    
                    if created:
                        count += 1
                        if count % 100 == 0:
                            print(f"  ... {count} shows imported so far")
                        
                        # Add actors if provided
                        actors_str = row.get('actors') or row.get('stars') or ''
                        if actors_str:
                            # Clean up list format
                            actors_str = str(actors_str).strip()
                            actors_str = actors_str.replace('[', '').replace(']', '').replace("'", '').replace('"', '')
                            actors_list = [a.strip().rstrip(',') for a in actors_str.split(',') if a.strip()]
                            for actor_name in actors_list:
                                if actor_name and len(actor_name) > 1:
                                    # Get or create actor
                                    actor, _ = Actors.objects.get_or_create(actor_name=actor_name)
                                    # Link to show via ActedIn
                                    ActedIn.objects.get_or_create(
                                        show_id=show,
                                        actor_id=actor,
                                        defaults={'actor_name': actor_name}
                                    )
                    else:
                        if count < 10:
                            print(f"  Already exists: {show_name}")
                        
                except Exception as e:
                    errors += 1
                    print(f"  Error on row {row_num}: {e}")
        
        print(f"  Imported {count} shows ({errors} errors)")
        if count > 0:
            AuditLog.objects.create(
                changes_to_data=f"Data import completed: Imported {count} shows from {csv_file.name} ({errors} errors)"
            )
        return count
    except Exception as e:
        print(f"  Failed to import: {e}")
        AuditLog.objects.create(
            changes_to_data=f"Data import failed: Error importing shows from {csv_file.name} - {str(e)}"
        )
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Main function to import all CSV files"""
    print("=" * 60)
    print("CSV Auto-Import Tool")
    print("=" * 60)
    
    # Check if folder exists
    if not CSV_FOLDER.exists():
        print(f"\nFolder not found: {CSV_FOLDER}")
        print(f"Creating folder...")
        CSV_FOLDER.mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {CSV_FOLDER}")
        print(f"\nPlease place your CSV files in: {CSV_FOLDER}")
        return
    
    # Find all CSV files
    csv_files = list(CSV_FOLDER.glob('*.csv'))
    
    if not csv_files:
        print(f"\nNo CSV files found in: {CSV_FOLDER}")
        print(f"\nPlease place your CSV files in this folder and run again.")
        return
    
    print(f"\nFound {len(csv_files)} CSV file(s):")
    for f in csv_files:
        print(f"  - {f.name}")
    
    print("\n" + "=" * 60)
    print("Starting import...")
    print("=" * 60)
    
    total_imported = {
        'directors': 0,
        'genres': 0,
        'films': 0,
        'shows': 0
    }
    
    # Process each file
    for csv_file in csv_files:
        # Skip README if it's a CSV
        if csv_file.name.lower() == 'readme.csv':
            continue
        
        file_type = detect_file_type(csv_file)
        
        if file_type == 'directors':
            total_imported['directors'] += import_directors(csv_file)
        elif file_type == 'genres':
            total_imported['genres'] += import_genres(csv_file)
        elif file_type == 'shows':
            total_imported['shows'] += import_shows(csv_file)
        else:  # films (default)
            total_imported['films'] += import_films(csv_file)
    
    # Summary
    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)
    print(f"  Directors: {total_imported['directors']}")
    print(f"  Genres: {total_imported['genres']}")
    print(f"  Films: {total_imported['films']}")
    print(f"  Shows: {total_imported['shows']}")
    
    total = sum(total_imported.values())
    if total > 0:
        print(f"\nSuccessfully imported {total} total records!")
        # Log to audit log
        AuditLog.objects.create(
            changes_to_data=f"Data import completed: {total_imported['directors']} directors, {total_imported['genres']} genres, {total_imported['films']} films, {total_imported['shows']} shows"
        )
    else:
        print(f"\nNo new records imported (may already exist)")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nImport cancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

