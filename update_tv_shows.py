#!/usr/bin/env python
"""
Script to update TV shows data from the new tv_shows_only_multi_year.csv file.
This will clear existing shows and re-import from the new file.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databases_proj.settings')
django.setup()

from api.models import AllShows, ActedIn

def clear_shows():
    """Clear all shows data"""
    print("Clearing existing shows data...")
    
    # Clear related data first
    ActedIn.objects.all().delete()
    
    # Clear shows
    count = AllShows.objects.count()
    AllShows.objects.all().delete()
    
    print(f"✓ Cleared {count} shows")

def reimport_shows():
    """Re-import shows from the new CSV file"""
    print("\nRe-importing shows from tv_shows_only_multi_year.csv...")
    print()
    
    # Import using the fixed import script
    from import_all_csv import import_shows
    from pathlib import Path
    
    csv_file = Path('data/csv/tv_shows_only_multi_year.csv')
    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        return False
    
    count = import_shows(csv_file)
    return count > 0

if __name__ == '__main__':
    print("=" * 60)
    print("Update TV Shows Data")
    print("=" * 60)
    print()
    print("This will:")
    print("  1. Clear all existing shows")
    print("  2. Re-import from tv_shows_only_multi_year.csv")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    try:
        clear_shows()
        success = reimport_shows()
        
        if success:
            from api.models import AllShows
            print("\n" + "=" * 60)
            print("✅ TV Shows updated successfully!")
            print(f"   Total shows: {AllShows.objects.count()}")
            print("=" * 60)
        else:
            print("\n❌ Import failed or no data imported")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

