from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db.models import Q, Avg, Count
from django.db import connection
from .models import (
    AllFilms, MovieGenre, MovieDirector, MovieLanguage,
    Actors, MovieAverageRating, ShowAverageRating,
    AllShows, ShowGenre, ShowCertificate, ActedIn
)
import json
import re


def safe_int(value, default=0):
    """Safely convert value to int, handling comma-separated numbers and None"""
    if value is None:
        return default
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        return int(value) if value else default
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Safely convert value to float, handling comma-separated numbers and None"""
    if value is None:
        return default
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        return float(value) if value else default
    except (ValueError, TypeError):
        return default


def testdb(request):
    """Test database connection"""
    try:
        # Test SQLite connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 + 1 AS result")
            row = cursor.fetchone()
        
        # Test Django ORM
        film_count = AllFilms.objects.count()
        show_count = AllShows.objects.count()
        genre_count = MovieGenre.objects.count()
        
        return JsonResponse({
            'connected': True,
            'testQuery': [{'result': row[0]}],
            'database': 'SQLite',
            'film_count': film_count,
            'show_count': show_count,
            'genre_count': genre_count
        })
    except Exception as error:
        import traceback
        return JsonResponse({
            'connected': False,
            'error': str(error),
            'stack': traceback.format_exc() if settings.DEBUG else None
        }, status=500)


@require_http_methods(["GET"])
def genres(request):
    """Get all unique movie genres from the database"""
    try:
        genres_list = MovieGenre.objects.values_list('genre_name', flat=True).distinct().order_by('genre_name')
        
        return JsonResponse({
            'success': True,
            'genres': list(genres_list)
        })
    except Exception as error:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(error),
            'stack': traceback.format_exc() if settings.DEBUG else None
        }, status=500)


@require_http_methods(["GET"])
def show_genres(request):
    """Get all unique show genres from the database"""
    try:
        genres_list = ShowGenre.objects.values_list('genre_name', flat=True).distinct().order_by('genre_name')
        
        return JsonResponse({
            'success': True,
            'genres': list(genres_list)
        })
    except Exception as error:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(error),
            'stack': traceback.format_exc() if settings.DEBUG else None
        }, status=500)


@require_http_methods(["GET"])
def actors(request):
    """Get all unique actors from the database"""
    try:
        # Get actors from both Actors table and ActedIn table
        actors_from_films = Actors.objects.values_list('actor_name', flat=True).distinct()
        
        # Also get actors from ActedIn (shows)
        actors_from_shows = ActedIn.objects.values_list('actor_name', flat=True).distinct()
        
        # Combine and deduplicate
        all_actors = set(actors_from_films) | set(actors_from_shows)
        
        # Filter and clean actor names
        cleaned_actors = []
        for actor in all_actors:
            if actor:
                actor_clean = actor.strip()
                if (actor_clean and 
                    len(actor_clean) >= 2 and 
                    len(actor_clean) < 50 and
                    actor_clean != "Documentary" and 
                    actor_clean != "N/A" and
                    not actor_clean.isdigit() and
                    "documentary" not in actor_clean.lower() and
                    "n/a" not in actor_clean.lower()):
                    cleaned_actors.append(actor_clean)
        
        cleaned_actors = sorted(cleaned_actors)[:200]  # Limit to top 200
        
        return JsonResponse({
            'success': True,
            'actors': cleaned_actors
        })
    except Exception as error:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(error),
            'stack': traceback.format_exc() if settings.DEBUG else None
        }, status=500)


@require_http_methods(["GET"])
def movies(request):
    """Get movies with filtering using Django ORM - ONLY MOVIES"""
    try:
        # Get filter parameters
        genre = request.GET.get("genre", "")
        max_rating = request.GET.get("maxRating", "")
        year_from = request.GET.get("yearFrom", "")
        year_to = request.GET.get("yearTo", "")
        min_rating = request.GET.get("minRating", "")
        min_votes = request.GET.get("minVotes", "")  # Note: We don't have votes in new schema
        title_search = request.GET.get("titleSearch", "")
        sort_by = request.GET.get("sortBy", "rating")
        actors_param = request.GET.get("actors", "")
        limit_param = request.GET.get("limit", "100")
        
        # Parse actors
        actors_list = []
        if actors_param:
            actors_list = [a.strip() for a in actors_param.split(",") if a.strip()]
        
        # Parse limit
        try:
            limit = max(1, min(500, int(limit_param)))
        except:
            limit = 100
        
        # Start with base queryset - ONLY MOVIES
        queryset = AllFilms.objects.select_related('director_id', 'genre_id', 'language_id').all()
        
        # Title search filter
        if title_search and title_search.strip():
            queryset = queryset.filter(film_name__icontains=title_search.strip())
        
        # Genre filter
        if genre and genre != "" and genre != "Any":
            queryset = queryset.filter(genre_id__genre_name__icontains=genre)
        
        # Year filter
        if year_from and safe_int(year_from) > 0:
            queryset = queryset.filter(
                Q(year__gte=safe_int(year_from)) | Q(year__isnull=True)
            )
        if year_to and safe_int(year_to) > 0 and safe_int(year_to) < 3000:
            queryset = queryset.filter(
                Q(year__lte=safe_int(year_to)) | Q(year__isnull=True)
            )
        
        # Actor filter - check if any actor in the film matches
        if actors_list:
            actor_filter = Q()
            for actor in actors_list:
                # Check in Actors table (films) - using reverse relationship
                actor_filter |= Q(actors__actor_name__icontains=actor)
            queryset = queryset.filter(actor_filter).distinct()
        
        # Get average ratings for sorting
        # We'll annotate with average rating if available
        queryset = queryset.annotate(
            avg_rating=Avg('movierating__user_rating')
        )
        
        # Sort by based on sortBy parameter
        if sort_by == "votes":
            # Since we don't have votes, sort by number of ratings instead
            queryset = queryset.annotate(
                rating_count=Count('movierating')
            ).order_by('-rating_count', '-avg_rating')
        elif sort_by == "year":
            queryset = queryset.order_by('-year', '-avg_rating')
        elif sort_by == "year_old":
            queryset = queryset.order_by('year', '-avg_rating')
        elif sort_by == "runtime":
            queryset = queryset.order_by('duration', '-avg_rating')
        elif sort_by == "runtime_long":
            queryset = queryset.order_by('-duration', '-avg_rating')
        else:  # rating (default)
            queryset = queryset.order_by('-avg_rating', '-year')
        
        # Apply limit
        films = queryset[:limit]
        
        # Transform to match frontend format
        movies_data = []
        for film in films:
            # Get genres (we have one genre per film, but frontend expects array)
            genres = []
            if film.genre_id:
                genres = [film.genre_id.genre_name]
            
            # Get cast/actors - using reverse relationship
            cast = []
            film_actors = film.actors_set.values_list('actor_name', flat=True)[:3]
            cast = list(film_actors)
            
            # Get average rating
            avg_rating = film.avg_rating if hasattr(film, 'avg_rating') and film.avg_rating else None
            if not avg_rating:
                # Try to get from MovieAverageRating table
                try:
                    avg_rating_obj = MovieAverageRating.objects.get(film_id=film)
                    avg_rating = float(avg_rating_obj.average_score)
                except MovieAverageRating.DoesNotExist:
                    avg_rating = 0.0
            
            # Rating certificate - we don't have this in films, use default
            rating = "Unrated"
            
            # Get synopsis - we don't have description in new schema
            synopsis = "No description available."
            
            movie = {
                'title': film.film_name or "Unknown",
                'genres': genres,
                'runtime': film.duration or 0,
                'rating': rating,
                'score': safe_float(avg_rating, 0),
                'synopsis': synopsis,
                'cast': cast,
                'director': film.director_id.director_name if film.director_id else "Unknown",
                'year': film.year or None,
                'votes': 0,  # We don't have votes in new schema
                'rating_value': safe_float(avg_rating, 0)
            }
            movies_data.append(movie)
        
        return JsonResponse({
            'success': True,
            'movies': movies_data,
            'count': len(movies_data)
        })
        
    except Exception as error:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(error),
            'stack': traceback.format_exc() if settings.DEBUG else None
        }, status=500)


@require_http_methods(["GET"])
def shows(request):
    """Get shows with filtering using Django ORM - ONLY SHOWS"""
    try:
        # Get filter parameters
        genre = request.GET.get("genre", "")
        max_rating = request.GET.get("maxRating", "")
        year_from = request.GET.get("yearFrom", "")
        year_to = request.GET.get("yearTo", "")
        min_rating = request.GET.get("minRating", "")
        title_search = request.GET.get("titleSearch", "")
        sort_by = request.GET.get("sortBy", "rating")
        actors_param = request.GET.get("actors", "")
        limit_param = request.GET.get("limit", "100")
        
        # Parse actors
        actors_list = []
        if actors_param:
            actors_list = [a.strip() for a in actors_param.split(",") if a.strip()]
        
        # Parse limit
        try:
            limit = max(1, min(500, int(limit_param)))
        except:
            limit = 100
        
        # Start with base queryset - ONLY SHOWS
        queryset = AllShows.objects.select_related('cert_id', 'genre_id').all()
        
        # Title search filter
        if title_search and title_search.strip():
            queryset = queryset.filter(show_name__icontains=title_search.strip())
        
        # Genre filter
        if genre and genre != "" and genre != "Any":
            queryset = queryset.filter(genre_id__genre_name__icontains=genre)
        
        # Certificate/Rating filter
        if max_rating:
            rating_order = {"G": 1, "PG": 2, "PG-13": 3, "R": 4, "NC-17": 5, "TV-G": 1, "TV-PG": 2, "TV-14": 3, "TV-MA": 4}
            max_rating_value = rating_order.get(max_rating, 4)
            allowed_ratings = [r for r, v in rating_order.items() if v <= max_rating_value]
            
            if allowed_ratings:
                queryset = queryset.filter(
                    Q(cert_id__cert_rating__in=allowed_ratings) | Q(cert_id__isnull=True)
                )
        
        # Year filter - parse from years field (format: "20152022" or "2008-2013")
        # For shows, we need to extract the start year and check if it falls in range
        if year_from and safe_int(year_from) > 0:
            year_from_val = safe_int(year_from)
            # Show must start in or after year_from, or we can't determine (include it)
            # We'll filter in Python since SQL can't easily parse "20152022" format
            pass  # Will filter after querying
        
        if year_to and safe_int(year_to) > 0 and safe_int(year_to) < 3000:
            year_to_val = safe_int(year_to)
            # Show must start before or in year_to, or we can't determine (include it)
            pass  # Will filter after querying
        
        # Actor filter
        if actors_list:
            actor_filter = Q()
            for actor in actors_list:
                actor_filter |= Q(actedin__actor_name__icontains=actor)
            queryset = queryset.filter(actor_filter).distinct()
        
        # Get average ratings for sorting
        queryset = queryset.annotate(
            avg_rating=Avg('showuserrating__user_rating')
        )
        
        # Sort by based on sortBy parameter
        if sort_by == "votes":
            queryset = queryset.annotate(
                rating_count=Count('showuserrating')
            ).order_by('-rating_count', '-avg_rating')
        elif sort_by == "year":
            queryset = queryset.order_by('-years', '-avg_rating')
        elif sort_by == "year_old":
            queryset = queryset.order_by('years', '-avg_rating')
        elif sort_by == "runtime":
            queryset = queryset.order_by('duration', '-avg_rating')
        elif sort_by == "runtime_long":
            queryset = queryset.order_by('-duration', '-avg_rating')
        else:  # rating (default)
            queryset = queryset.order_by('-rating', '-avg_rating')
        
        # Get all shows first (before year filtering)
        all_shows = list(queryset)
        
        # Apply year filtering in Python (since years field format is complex)
        filtered_shows = []
        for show in all_shows:
            show_start_year = None
            
            # Parse years field - handle formats like "20152022", "2008-2013", "(20082013)"
            if show.years:
                years_str = str(show.years).strip().replace('(', '').replace(')', '')
                # Try to extract first 4-digit year
                import re
                year_match = re.search(r'(\d{4})', years_str)
                if year_match:
                    show_start_year = int(year_match.group(1))
            
            # Apply year filters
            if year_from and safe_int(year_from) > 0:
                if show_start_year and show_start_year < safe_int(year_from):
                    continue  # Show starts before year_from, exclude it
            
            if year_to and safe_int(year_to) > 0 and safe_int(year_to) < 3000:
                if show_start_year and show_start_year > safe_int(year_to):
                    continue  # Show starts after year_to, exclude it
            
            filtered_shows.append(show)
            if len(filtered_shows) >= limit:
                break
        
        # Transform to match frontend format
        shows_data = []
        for show in filtered_shows:
            # Get genres
            genres = []
            if show.genre_id:
                genres = [show.genre_id.genre_name]
            
            # Get cast/actors
            cast = []
            show_actors = ActedIn.objects.filter(show_id=show).values_list('actor_name', flat=True)[:3]
            cast = list(show_actors)
            
            # Get rating
            avg_rating = show.avg_rating if hasattr(show, 'avg_rating') and show.avg_rating else None
            if not avg_rating:
                avg_rating = float(show.rating) if show.rating else 0.0
            
            # Certificate
            rating = show.cert_id.cert_rating if show.cert_id else "Unrated"
            
            # Parse year from years field
            year = None
            if show.years:
                import re
                year_match = re.search(r'(\d{4})', str(show.years))
                if year_match:
                    year = int(year_match.group(1))
            
            show_data = {
                'title': show.show_name or "Unknown",
                'genres': genres,
                'runtime': show.duration or 0,
                'rating': rating,
                'score': safe_float(avg_rating, 0),
                'synopsis': "No description available.",
                'cast': cast,
                'director': "N/A",  # Shows don't have directors
                'year': year,
                'votes': 0,
                'rating_value': safe_float(avg_rating, 0)
            }
            shows_data.append(show_data)
        
        return JsonResponse({
            'success': True,
            'movies': shows_data,  # Use 'movies' key for frontend compatibility
            'count': len(shows_data)
        })
        
    except Exception as error:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(error),
            'stack': traceback.format_exc() if settings.DEBUG else None
        }, status=500)
