# Data Insertion Guide

This guide shows you multiple ways to insert data into your SQLite database.

## Quick Start

**Fastest method for beginners:**
```bash
source venv/bin/activate
python quick_insert.py
```

**Import from CSV:**
```bash
python import_from_csv.py example_movies.csv films
```

---

## Method 1: Quick Insert Script (Recommended for Beginners)

Interactive script that guides you through inserting data:

```bash
source venv/bin/activate
python quick_insert.py
```

This will:
- Prompt you for movie details
- Automatically create directors, genres, languages if they don't exist
- Let you add actors
- Show current data counts

---

## Method 2: Import from CSV (Best for Bulk Data)

### Step 1: Prepare your CSV file

Create a CSV file with these columns:
- `film_name` (required)
- `director_name` (optional)
- `year` (optional)
- `duration` (optional, in minutes)
- `genre_name` (optional)
- `language_name` (optional)
- `actors` (optional, comma-separated)

See `example_movies.csv` for a template.

### Step 2: Import the data

```bash
source venv/bin/activate

# Import films (creates directors, genres, languages automatically)
python import_from_csv.py your_movies.csv films

# Or import just directors
python import_from_csv.py directors.csv directors

# Or import just genres
python import_from_csv.py genres.csv genres
```

---

## Method 3: Django Admin (Easiest for Manual Entry)

### Step 1: Create a Superuser
```bash
source venv/bin/activate
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

### Step 2: Access Admin Panel
1. Start the server: `python manage.py runserver`
2. Visit: http://localhost:8000/admin
3. Login with your superuser credentials
4. Click on any model (e.g., "All Films", "Movie Directors") to add data

**Tip:** Django admin automatically handles relationships - when creating a film, you can select existing directors/genres or create new ones.

---

## Method 4: Django Shell (For Programmatic Insertion)

### Basic Usage
```bash
source venv/bin/activate
python manage.py shell
```

### Example: Insert Movies
```python
from api.models import MovieGenre, MovieDirector, MovieLanguage, AllFilms, Actors

# Create a genre (or get existing)
action = MovieGenre.objects.get_or_create(genre_name='Action')[0]

# Create a director (or get existing)
director = MovieDirector.objects.get_or_create(director_name='Quentin Tarantino')[0]

# Create a language (or get existing)
english = MovieLanguage.objects.get_or_create(language_name='English')[0]

# Create a film
film = AllFilms.objects.create(
    film_name='Pulp Fiction',
    director_id=director,
    year=1994,
    duration=154,
    genre_id=action,
    language_id=english
)

# Add actors
Actors.objects.create(actor_name='John Travolta', film_id=film)
Actors.objects.create(actor_name='Samuel L. Jackson', film_id=film)
Actors.objects.create(actor_name='Uma Thurman', film_id=film)

# Exit shell
exit()
```

**Note:** Using `get_or_create()` prevents duplicates - it returns the existing object if found, or creates a new one.

---

## Method 5: Python Script

### Run the sample data script:
```bash
source venv/bin/activate
python insert_sample_data.py
```

This creates sample movies, directors, genres, and actors.

### Create your own script:

Create a file `my_data.py`:
```python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databases_proj.settings')
django.setup()

from api.models import MovieGenre, MovieDirector, AllFilms, Actors

# Your code here
genre = MovieGenre.objects.get_or_create(genre_name='Comedy')[0]
director = MovieDirector.objects.get_or_create(director_name='Edgar Wright')[0]
# ... etc
```

Run it:
```bash
python my_data.py
```

---

## Method 6: Direct SQL (Advanced)

For advanced users who want to use raw SQL:

```bash
sqlite3 db.sqlite3
```

Then use SQL:
```sql
-- Insert a director
INSERT INTO Movie_Directors (Director_name) VALUES ('Christopher Nolan');

-- Insert a film (note: use the director_id from above)
INSERT INTO All_Films (Film_name, Director_id, Year, Duration) 
VALUES ('Inception', 1, 2010, 148);

-- Exit
.quit
```

**Warning:** Using raw SQL bypasses Django's validation and may cause issues with relationships.

---

## Data Structure Reminder

When inserting films, remember the relationships:
- **AllFilms** requires (or can have):
  - `film_name` (required)
  - `director_id` → MovieDirector (optional)
  - `genre_id` → MovieGenre (optional)
  - `language_id` → MovieLanguage (optional)
  - `year` (optional)
  - `duration` (optional)

- **Actors** links to films via `film_id`

---

## Checking Your Data

View current counts:
```bash
python quick_insert.py
# Choose option 2
```

Or in Django shell:
```python
from api.models import AllFilms, MovieGenre, MovieDirector, Actors
print(f"Films: {AllFilms.objects.count()}")
print(f"Genres: {MovieGenre.objects.count()}")
print(f"Directors: {MovieDirector.objects.count()}")
print(f"Actors: {Actors.objects.count()}")
```

---

## Tips

1. **Use `get_or_create()`** to avoid duplicates:
   ```python
   genre, created = MovieGenre.objects.get_or_create(genre_name='Action')
   ```

2. **Bulk imports**: Use CSV import for large datasets

3. **Relationships**: Create directors/genres/languages first, then films

4. **Actors**: Can be added after creating the film

5. **Django Admin**: Best for manual entry and browsing data

