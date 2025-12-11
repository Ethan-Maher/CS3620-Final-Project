# How to Start This Project

## For Your Friend (New User)

### What They Need to Do:

1. **Get the project files** (zip or git clone)

2. **Make sure CSV files are included:**
   - `data/csv/letterboxd_movies_dataset.csv` (3.4MB)
   - `data/csv/tv_shows_only_multi_year.csv` (434KB)

3. **Follow the setup steps below**

---

## Complete Setup Instructions

### Part 1: Python Backend (5 minutes)

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate
# On Windows: venv\Scripts\activate

# 3. Install Python packages
pip install -r requirements.txt

# 4. Create database tables
python manage.py migrate

# 5. Import data from CSV files
python import_all_csv.py
```

**Expected output:**
```
Imported 15549 films
Imported 605 shows
```

### Part 2: Node.js Frontend (2 minutes)

```bash
# 1. Install Node.js packages
npm install

# 2. (Optional) Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
```

### Part 3: Run the Application

**You need TWO terminal windows:**

**Terminal 1 - Start Django:**
```bash
cd databases_proj
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Start Next.js:**
```bash
cd databases_proj
npm run dev
```

### Part 4: Open Website

Visit: **http://localhost:3000**

---

## Quick Verification

1. **Check database:** http://localhost:8000/api/testdb
   - Should show film_count: ~15549
   - Should show show_count: ~605

2. **Check website:**
   - Movies tab should show many movies
   - TV Shows tab should show many shows
   - Filters should work

---

## What Files Are Needed?

**Required CSV files** (must be in `data/csv/` folder):
- `letterboxd_movies_dataset.csv` - Movies data
- `tv_shows_only_multi_year.csv` - TV Shows data

**If CSV files are missing:**
- The import will fail or show 0 records
- Make sure both files are in the `data/csv/` folder before running `python import_all_csv.py`

---

## Common Issues

| Issue | Solution |
|-------|----------|
| "No module named django" | Activate venv: `source venv/bin/activate` |
| "Port 8000 in use" | Use port 8001: `python manage.py runserver 8001` |
| "No data showing" | Run: `python import_all_csv.py` |
| "CSV files not found" | Check files are in `data/csv/` folder |
| "CORS errors" | Make sure Django server is running |

---

## File Checklist

Before sharing the repo, make sure these are included:
- `data/csv/letterboxd_movies_dataset.csv`
- `data/csv/tv_shows_only_multi_year.csv`
- `requirements.txt`
- `package.json`
- All Python files in `api/` and `databases_proj/`
- All React files in `src/`

**Note:** `db.sqlite3` will be created automatically, don't need to include it.

---

## Summary

**The process is:**
1. Install Python packages → `pip install -r requirements.txt`
2. Create database → `python manage.py migrate`
3. Import data → `python import_all_csv.py`
4. Install Node packages → `npm install`
5. Run Django → `python manage.py runserver`
6. Run Next.js → `npm run dev`
7. Open browser → http://localhost:3000

**Total time: ~10 minutes**

---

For more details, see:
- `QUICK_START.md` - Fast setup guide
- `STARTUP_GUIDE.md` - Detailed instructions
- `SETUP_CHECKLIST.md` - Verification checklist

