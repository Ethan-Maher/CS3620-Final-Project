#!/usr/bin/env python
"""
Script to insert sample data into the database.
Run with: python insert_sample_data.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databases_proj.settings')
django.setup()

from api.models import (
    MovieGenre, MovieDirector, MovieLanguage, AllFilms, Actors,
    ShowGenre, ShowCertificate, AllShows, ActedIn
)

def create_sample_data():
    """Create sample movies and shows"""
    print("Creating sample data...")
    
    # Create genres
    print("Creating genres...")
    action = MovieGenre.objects.get_or_create(genre_name='Action')[0]
    drama = MovieGenre.objects.get_or_create(genre_name='Drama')[0]
    comedy = MovieGenre.objects.get_or_create(genre_name='Comedy')[0]
    sci_fi = MovieGenre.objects.get_or_create(genre_name='Sci-Fi')[0]
    thriller = MovieGenre.objects.get_or_create(genre_name='Thriller')[0]
    horror = MovieGenre.objects.get_or_create(genre_name='Horror')[0]
    crime = MovieGenre.objects.get_or_create(genre_name='Crime')[0]
    
    # Create directors
    print("Creating directors...")
    nolan = MovieDirector.objects.get_or_create(director_name='Christopher Nolan')[0]
    spielberg = MovieDirector.objects.get_or_create(director_name='Steven Spielberg')[0]
    tarantino = MovieDirector.objects.get_or_create(director_name='Quentin Tarantino')[0]
    scorsese = MovieDirector.objects.get_or_create(director_name='Martin Scorsese')[0]
    kubrick = MovieDirector.objects.get_or_create(director_name='Stanley Kubrick')[0]
    
    # Create languages
    print("Creating languages...")
    english = MovieLanguage.objects.get_or_create(language_name='English')[0]
    spanish = MovieLanguage.objects.get_or_create(language_name='Spanish')[0]
    french = MovieLanguage.objects.get_or_create(language_name='French')[0]
    
    # Create films
    print("Creating films...")
    films_data = [
        {
            'name': 'The Matrix',
            'director': nolan,
            'year': 1999,
            'duration': 136,
            'genre': sci_fi,
            'language': english,
            'actors': ['Keanu Reeves', 'Laurence Fishburne', 'Carrie-Anne Moss']
        },
        {
            'name': 'Pulp Fiction',
            'director': tarantino,
            'year': 1994,
            'duration': 154,
            'genre': crime,
            'language': english,
            'actors': ['John Travolta', 'Samuel L. Jackson', 'Uma Thurman']
        },
        {
            'name': 'The Shining',
            'director': kubrick,
            'year': 1980,
            'duration': 144,
            'genre': horror,
            'language': english,
            'actors': ['Jack Nicholson', 'Shelley Duvall']
        },
        {
            'name': 'Goodfellas',
            'director': scorsese,
            'year': 1990,
            'duration': 146,
            'genre': drama,
            'language': english,
            'actors': ['Robert De Niro', 'Ray Liotta', 'Joe Pesci']
        },
        {
            'name': 'E.T. the Extra-Terrestrial',
            'director': spielberg,
            'year': 1982,
            'duration': 115,
            'genre': sci_fi,
            'language': english,
            'actors': ['Henry Thomas', 'Dee Wallace', 'Drew Barrymore']
        },
    ]
    
    for film_data in films_data:
        film, created = AllFilms.objects.get_or_create(
            film_name=film_data['name'],
            defaults={
                'director_id': film_data['director'],
                'year': film_data['year'],
                'duration': film_data['duration'],
                'genre_id': film_data['genre'],
                'language_id': film_data['language']
            }
        )
        
        if created:
            print(f"  Created: {film.film_name}")
            # Add actors
            for actor_name in film_data['actors']:
                Actors.objects.get_or_create(
                    actor_name=actor_name,
                    film_id=film
                )
        else:
            print(f"  Already exists: {film.film_name}")
    
    print(f"\n✓ Created {AllFilms.objects.count()} films")
    print(f"✓ Created {Actors.objects.count()} actor entries")
    print("\nSample data insertion complete!")

if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

