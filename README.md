# WhatToWatch

Movie and TV show recommendation website with search and filtering.

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+

### Setup

1. **Backend (Django)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python import_all_csv.py
   ```

2. **Frontend (Next.js)**
   ```bash
   npm install
   ```

3. **Run**
   ```bash
   # Terminal 1
   source venv/bin/activate
   python manage.py runserver
   
   # Terminal 2
   npm run dev
   ```

4. **Open** http://localhost:3000

## Required Files

Make sure these CSV files are in `data/csv/`:
- `letterboxd_movies_dataset.csv`
- `tv_shows_only_multi_year.csv`

## Troubleshooting

- **No data showing?** Run `python import_all_csv.py`
- **Port in use?** Change port: `python manage.py runserver 8001`
- **Module errors?** Make sure virtual environment is activated

For detailed setup instructions, see `HOW_TO_START.md`.
