# CSV Data Folder

Drop your CSV files here for automatic import.

## How to Use

1. **Place your CSV files in this folder** (`data/csv/`)

2. **Run the import script:**
   ```bash
   source venv/bin/activate
   python import_all_csv.py
   ```

   This will automatically detect and import all CSV files in this folder.

## CSV File Format

Your CSV files should have one of these formats:

### For Movies/Films:
Required columns:
- `film_name` or `title` or `name`

Optional columns:
- `director_name` or `director`
- `year`
- `duration` or `runtime` (in minutes)
- `genre_name` or `genre`
- `language_name` or `language`
- `actors` or `cast` (comma-separated)

### For Directors:
- `director_name` or `name`

### For Genres:
- `genre_name` or `name`

### For Shows:
- `show_name` or `title` or `name`
- `duration` (in minutes)
- `cert_rating` or `certificate`
- `rating` (decimal)
- `genre_name` or `genre`
- `years` or `year` (e.g., "2020-2024" or "(20082013)")

**Note**: The current TV shows dataset is `tv_shows_only_multi_year.csv`

## Example

See `example_movies.csv` for a sample format.

## Notes

- The script will automatically detect the file type based on column names
- Duplicate entries will be skipped (won't create duplicates)
- Missing optional fields are fine - they'll just be left empty

