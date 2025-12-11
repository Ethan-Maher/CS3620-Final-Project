#!/usr/bin/env python
"""
Fix data separation - ensures movies come from letterboxd_movies_dataset.csv
and shows come from tv_only.csv only.
"""
import os
import sys
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databases_proj.settings')
django.setup()

from api.models import AllFilms, AllShows, Actors, ActedIn

def clear_data():
    """Clear all films and shows data"""
    print("Clearing existing data...")
    
    # Clear related data first
    Actors.objects.filter(film_id__isnull=False).delete()
    ActedIn.objects.all().delete()
    
    # Clear main tables
    AllFilms.objects.all().delete()
    AllShows.objects.all().delete()
    
    print("Data cleared")

def reimport_correctly():
    """Re-import data based on filename"""
    print("\nRe-importing data based on filename...")
    print("  - letterboxd_movies_dataset.csv → AllFilms (movies)")
    print("  - tv_only.csv → AllShows (shows)")
    print()
    
    # Import using the fixed import script
    from import_all_csv import main as import_main
    import_main()

if __name__ == '__main__':
    print("=" * 60)
    print("Fix Data Separation")
    print("=" * 60)
    print()
    print("  1. Clear all existing films and shows")
    print("  2. Re-import from CSV files based on filename")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    try:
        clear_data()
        reimport_correctly()
        print("\n" + "=" * 60)
        print("Data separation fixed!")
        print("=" * 60)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

