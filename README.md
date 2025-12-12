# WhatToWatch

WhatToWatch is a movie and TV show recommendation system. The user can enter their information to create an account on the platform. Once your account is created, you can now start searching the platform for something to watch! There are two sections to the platform, a TV show section and a movie section. If the user wants to watch something, they can sort by different features to help them decide. Both sections of the website allow the user to filter by genre, certification, and decade released. The user can also add movies to a watch later list to save interesting movies that they might want to come back to. The website also has a favorites section where the user can select their favorite genre, actor, and decade to get a few recommendations for a movie or show to watch. Finally, the app has a review system where users can rate and review the app.


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


## Datasets
https://www.kaggle.com/datasets/kutayahin/letterboxd-movies-dataset/data

https://www.kaggle.com/code/payamamanat/imdb-movies

https://www.kaggle.com/datasets/shivamb/netflix-shows
