#!/usr/bin/env python
"""
Verification script to test SQLite integration with the website.
Run this to verify all connections are working correctly.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databases_proj.settings')
django.setup()

from django.test import RequestFactory
from django.db import connection
from api.views import testdb, genres, actors, movies
from api.models import AllFilms, MovieGenre, Actors, MovieDirector
import json

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def test_database():
    """Test database connection and integrity"""
    print_section("1. Database Connection Test")
    
    try:
        with connection.cursor() as cursor:
            # Integrity check
            cursor.execute('PRAGMA integrity_check')
            integrity = cursor.fetchone()
            print(f"✓ Integrity check: {integrity[0]}")
            
            # Foreign key check
            cursor.execute('PRAGMA foreign_key_check')
            fk_errors = cursor.fetchall()
            if fk_errors:
                print(f"⚠ Foreign key errors: {len(fk_errors)}")
                return False
            else:
                print("✓ No foreign key violations")
            
            # Table count
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'django_%'
            """)
            tables = cursor.fetchall()
            print(f"✓ Found {len(tables)} custom tables")
            
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_models():
    """Test Django models"""
    print_section("2. Django Models Test")
    
    try:
        film_count = AllFilms.objects.count()
        genre_count = MovieGenre.objects.count()
        actor_count = Actors.objects.count()
        director_count = MovieDirector.objects.count()
        
        print(f"✓ AllFilms: {film_count} records")
        print(f"✓ MovieGenre: {genre_count} records")
        print(f"✓ Actors: {actor_count} records")
        print(f"✓ MovieDirector: {director_count} records")
        
        # Test relationships
        if film_count > 0:
            film = AllFilms.objects.first()
            print(f"\n✓ Testing relationships with: {film.film_name}")
            if film.director_id:
                print(f"  - Director: {film.director_id.director_name}")
            if film.genre_id:
                print(f"  - Genre: {film.genre_id.genre_name}")
            actors_count = film.actors_set.count()
            print(f"  - Actors: {actors_count}")
        
        return True
    except Exception as e:
        print(f"❌ Models error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print_section("3. API Endpoints Test")
    
    factory = RequestFactory()
    results = {}
    
    # Test testdb
    try:
        request = factory.get('/api/testdb')
        response = testdb(request)
        data = json.loads(response.content)
        results['testdb'] = response.status_code == 200 and data.get('connected')
        print(f"{'✓' if results['testdb'] else '❌'} /api/testdb - Status: {response.status_code}")
    except Exception as e:
        results['testdb'] = False
        print(f"❌ /api/testdb - Error: {e}")
    
    # Test genres
    try:
        request = factory.get('/api/genres')
        response = genres(request)
        data = json.loads(response.content)
        results['genres'] = response.status_code == 200 and data.get('success')
        genre_count = len(data.get('genres', []))
        print(f"{'✓' if results['genres'] else '❌'} /api/genres - Status: {response.status_code}, Genres: {genre_count}")
    except Exception as e:
        results['genres'] = False
        print(f"❌ /api/genres - Error: {e}")
    
    # Test actors
    try:
        request = factory.get('/api/actors')
        response = actors(request)
        data = json.loads(response.content)
        results['actors'] = response.status_code == 200 and data.get('success')
        actor_count = len(data.get('actors', []))
        print(f"{'✓' if results['actors'] else '❌'} /api/actors - Status: {response.status_code}, Actors: {actor_count}")
    except Exception as e:
        results['actors'] = False
        print(f"❌ /api/actors - Error: {e}")
    
    # Test movies
    try:
        request = factory.get('/api/movies?limit=5')
        response = movies(request)
        data = json.loads(response.content)
        results['movies'] = response.status_code == 200 and data.get('success')
        movie_count = len(data.get('movies', []))
        print(f"{'✓' if results['movies'] else '❌'} /api/movies - Status: {response.status_code}, Movies: {movie_count}")
    except Exception as e:
        results['movies'] = False
        print(f"❌ /api/movies - Error: {e}")
        import traceback
        traceback.print_exc()
    
    return all(results.values())

def test_filtering():
    """Test movie filtering"""
    print_section("4. Filtering Test")
    
    factory = RequestFactory()
    results = {}
    
    filters = [
        ('genre=Action', 'Genre filter'),
        ('yearFrom=2008&yearTo=2010', 'Year filter'),
        ('titleSearch=Dark', 'Title search'),
        ('actors=Leonardo', 'Actor filter'),
    ]
    
    for params, name in filters:
        try:
            request = factory.get(f'/api/movies?{params}')
            response = movies(request)
            data = json.loads(response.content)
            success = response.status_code == 200 and data.get('success')
            count = len(data.get('movies', []))
            results[name] = success
            print(f"{'✓' if success else '❌'} {name}: {count} movies found")
        except Exception as e:
            results[name] = False
            print(f"❌ {name}: Error - {e}")
    
    return all(results.values())

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SQLite Integration Verification")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database),
        ("Django Models", test_models),
        ("API Endpoints", test_api_endpoints),
        ("Filtering", test_filtering),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} failed with exception: {e}")
            results[name] = False
    
    # Summary
    print_section("Summary")
    
    all_passed = all(results.values())
    for name, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Integration successful!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please check the errors above")
        return 1

if __name__ == '__main__':
    sys.exit(main())

