from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db.models import Q, Avg, Count
from django.db import connection
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from .models import (
    AllFilms, MovieGenre, MovieDirector, MovieLanguage,
    Actors, MovieAverageRating, ShowAverageRating,
    AllShows, ShowGenre, ShowCertificate, ActedIn,
    User, AuditLog, WatchLaterMovie, WatchLaterShow,
    WatchedMovie, WatchedShow, Favorites,
    MovieRating, ShowUserRating
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


@csrf_exempt
def signup(request):
    """User registration endpoint"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        # Handle request body - decode if bytes
        try:
            body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
        except (AttributeError, UnicodeDecodeError):
            body = str(request.body)
        data = json.loads(body)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            response = JsonResponse({
                'success': False,
                'error': 'Email and password are required'
            }, status=400)
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            response = JsonResponse({
                'success': False,
                'error': 'User with this email already exists'
            }, status=400)
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        # Create user
        try:
            user = User.objects.create_user(email=email, password=password)
            # Log to audit log
            AuditLog.objects.create(
                changes_to_data=f"Authorization event - User signup: New user created with email {email} (User ID: {user.user_id})"
            )
        except Exception as create_error:
            response = JsonResponse({
                'success': False,
                'error': f'Failed to create user: {str(create_error)}'
            }, status=500)
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        response = JsonResponse({
            'success': True,
            'message': 'User created successfully',
            'user_id': user.user_id
        })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except json.JSONDecodeError:
        response = JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as error:
        import traceback
        error_msg = str(error)
        error_stack = traceback.format_exc() if settings.DEBUG else None
        response = JsonResponse({
            'success': False,
            'error': f'Server error: {error_msg}',
            'stack': error_stack
        }, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response


@csrf_exempt
def signin(request):
    """User login endpoint"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    if request.method != 'POST':
        response = JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    try:
        # Handle request body - decode if bytes
        try:
            body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
        except (AttributeError, UnicodeDecodeError):
            body = str(request.body)
        data = json.loads(body)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            response = JsonResponse({
                'success': False,
                'error': 'Email and password are required'
            }, status=400)
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        # Authenticate user
        try:
            user = authenticate(request, username=email, password=password)
        except Exception as auth_error:
            response = JsonResponse({
                'success': False,
                'error': f'Authentication error: {str(auth_error)}'
            }, status=500)
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        if user is not None:
            try:
                login(request, user)
                # Log to audit log
                AuditLog.objects.create(
                    changes_to_data=f"Authorization event - User signin: User {user.email} (User ID: {user.user_id}) signed in successfully"
                )
            except Exception as login_error:
                response = JsonResponse({
                    'success': False,
                    'error': f'Login error: {str(login_error)}'
                }, status=500)
                response['Access-Control-Allow-Origin'] = '*'
                return response
            
            response = JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user_id': user.user_id,
                'email': user.email
            })
            response['Access-Control-Allow-Origin'] = '*'
            return response
        else:
            response = JsonResponse({
                'success': False,
                'error': 'Invalid email or password'
            }, status=401)
            response['Access-Control-Allow-Origin'] = '*'
            return response
    except json.JSONDecodeError:
        response = JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as error:
        import traceback
        error_msg = str(error)
        error_stack = traceback.format_exc() if settings.DEBUG else None
        response = JsonResponse({
            'success': False,
            'error': f'Server error: {error_msg}',
            'stack': error_stack
        }, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response


@require_http_methods(["GET"])
def check_auth(request):
    """Check if user is authenticated"""
    try:
        if request.user.is_authenticated:
            return JsonResponse({
                'success': True,
                'authenticated': True,
                'user_id': request.user.user_id,
                'email': request.user.email
            })
        else:
            return JsonResponse({
                'success': True,
                'authenticated': False
            })
    except Exception as error:
        return JsonResponse({
            'success': False,
            'error': str(error)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def signout(request):
    """User logout endpoint"""
    try:
        if request.user.is_authenticated:
            # Log to audit log
            AuditLog.objects.create(
                changes_to_data=f"Authorization event - User signout: User {request.user.email} (User ID: {request.user.user_id}) signed out"
            )
            from django.contrib.auth import logout
            logout(request)
        
        response = JsonResponse({
            'success': True,
            'message': 'Logged out successfully'
        })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as error:
        response = JsonResponse({
            'success': False,
            'error': str(error)
        }, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response


@require_http_methods(["GET"])
def audit_logs(request):
    """Get audit logs"""
    try:
        # Get limit parameter (default 100, max 1000)
        limit_param = request.GET.get("limit", "100")
        try:
            limit = max(1, min(1000, int(limit_param)))
        except:
            limit = 100
        
        # Get logs ordered by date (newest first)
        logs = AuditLog.objects.all().order_by('-date')[:limit]
        
        logs_data = []
        for log in logs:
            logs_data.append({
                'table_id': log.table_id,
                'date': log.date.isoformat(),
                'changes_to_data': log.changes_to_data
            })
        
        return JsonResponse({
            'success': True,
            'logs': logs_data,
            'count': len(logs_data)
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
        limit_param = request.GET.get("limit", "100")
        
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
                'film_id': film.film_id,
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
        limit_param = request.GET.get("limit", "100")
        
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
                'show_id': show.show_id,
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
# ==================== WATCH LATER ENDPOINTS ====================

@csrf_exempt
@require_http_methods(["POST", "DELETE", "GET"])
def watch_later_movie(request, film_id=None):
    """Add/remove/get watch later movie"""
    if not request.user.is_authenticated:
        response = JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    try:
        if request.method == 'POST':
            # Add to watch later
            film = AllFilms.objects.get(film_id=film_id)
            watch_later, created = WatchLaterMovie.objects.get_or_create(
                user_id=request.user,
                film_id=film
            )
            if created:
                AuditLog.objects.create(
                    changes_to_data=f"User {request.user.email} added movie '{film.film_name}' to watch later"
                )
            response = JsonResponse({
                'success': True,
                'message': 'Added to watch later',
                'added': created
            })
        elif request.method == 'DELETE':
            # Remove from watch later
            film = AllFilms.objects.get(film_id=film_id)
            deleted = WatchLaterMovie.objects.filter(
                user_id=request.user,
                film_id=film
            ).delete()[0]
            if deleted:
                AuditLog.objects.create(
                    changes_to_data=f"User {request.user.email} removed movie '{film.film_name}' from watch later"
                )
            response = JsonResponse({
                'success': True,
                'message': 'Removed from watch later',
                'deleted': deleted > 0
            })
        else:  # GET
            # Get all watch later movies for user
            watch_later_list = WatchLaterMovie.objects.filter(user_id=request.user).select_related('film_id')
            movies_data = []
            for item in watch_later_list:
                film = item.film_id
                movies_data.append({
                    'film_id': film.film_id,
                    'title': film.film_name,
                    'year': film.year,
                    'runtime': film.duration or 0,
                    'genre': film.genre_id.genre_name if film.genre_id else None,
                    'director': film.director_id.director_name if film.director_id else None,
                })
            response = JsonResponse({
                'success': True,
                'movies': movies_data,
                'count': len(movies_data)
            })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except AllFilms.DoesNotExist:
        response = JsonResponse({'success': False, 'error': 'Movie not found'}, status=404)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as error:
        response = JsonResponse({'success': False, 'error': str(error)}, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response


@csrf_exempt
@require_http_methods(["POST", "DELETE", "GET"])
def watch_later_show(request, show_id=None):
    """Add/remove/get watch later show"""
    if not request.user.is_authenticated:
        response = JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    try:
        if request.method == 'POST':
            show = AllShows.objects.get(show_id=show_id)
            watch_later, created = WatchLaterShow.objects.get_or_create(
                user_id=request.user,
                show_id=show
            )
            if created:
                AuditLog.objects.create(
                    changes_to_data=f"User {request.user.email} added show '{show.show_name}' to watch later"
                )
            response = JsonResponse({
                'success': True,
                'message': 'Added to watch later',
                'added': created
            })
        elif request.method == 'DELETE':
            show = AllShows.objects.get(show_id=show_id)
            deleted = WatchLaterShow.objects.filter(
                user_id=request.user,
                show_id=show
            ).delete()[0]
            if deleted:
                AuditLog.objects.create(
                    changes_to_data=f"User {request.user.email} removed show '{show.show_name}' from watch later"
                )
            response = JsonResponse({
                'success': True,
                'message': 'Removed from watch later',
                'deleted': deleted > 0
            })
        else:  # GET
            watch_later_list = WatchLaterShow.objects.filter(user_id=request.user).select_related('show_id')
            shows_data = []
            for item in watch_later_list:
                show = item.show_id
                shows_data.append({
                    'show_id': show.show_id,
                    'title': show.show_name,
                    'years': show.years,
                    'runtime': show.duration or 0,
                    'genre': show.genre_id.genre_name if show.genre_id else None,
                    'rating': show.cert_id.cert_rating if show.cert_id else None,
                })
            response = JsonResponse({
                'success': True,
                'shows': shows_data,
                'count': len(shows_data)
            })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except AllShows.DoesNotExist:
        response = JsonResponse({'success': False, 'error': 'Show not found'}, status=404)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as error:
        response = JsonResponse({'success': False, 'error': str(error)}, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response


# ==================== FAVORITES ENDPOINTS ====================

@csrf_exempt
@require_http_methods(["GET", "POST", "PUT"])
def favorites(request):
    """Get or update user favorites"""
    if not request.user.is_authenticated:
        response = JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    try:
        if request.method == 'GET':
            fav, created = Favorites.objects.get_or_create(user_id=request.user)
            response = JsonResponse({
                'success': True,
                'favorites': {
                    'fav_director': fav.fav_director.director_id if fav.fav_director else None,
                    'fav_director_name': fav.fav_director.director_name if fav.fav_director else None,
                    'fav_actor': fav.fav_actor,
                    'fav_genre': fav.fav_genre.genre_id if fav.fav_genre else None,
                    'fav_genre_name': fav.fav_genre.genre_name if fav.fav_genre else None,
                    'fav_decade': fav.fav_decade,
                }
            })
        else:  # POST or PUT
            body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            data = json.loads(body)
            fav, created = Favorites.objects.get_or_create(user_id=request.user)
            
            if 'fav_director' in data and data['fav_director']:
                try:
                    fav.fav_director = MovieDirector.objects.get(director_id=data['fav_director'])
                except MovieDirector.DoesNotExist:
                    pass
            if 'fav_actor' in data:
                fav.fav_actor = data['fav_actor']
            if 'fav_genre' in data and data['fav_genre']:
                try:
                    fav.fav_genre = MovieGenre.objects.get(genre_id=data['fav_genre'])
                except MovieGenre.DoesNotExist:
                    pass
            if 'fav_decade' in data:
                fav.fav_decade = data['fav_decade']
            
            fav.save()
            AuditLog.objects.create(
                changes_to_data=f"User {request.user.email} updated favorites"
            )
            response = JsonResponse({
                'success': True,
                'message': 'Favorites updated',
                'favorites': {
                    'fav_director': fav.fav_director.director_id if fav.fav_director else None,
                    'fav_director_name': fav.fav_director.director_name if fav.fav_director else None,
                    'fav_actor': fav.fav_actor,
                    'fav_genre': fav.fav_genre.genre_id if fav.fav_genre else None,
                    'fav_genre_name': fav.fav_genre.genre_name if fav.fav_genre else None,
                    'fav_decade': fav.fav_decade,
                }
            })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as error:
        response = JsonResponse({'success': False, 'error': str(error)}, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response


@csrf_exempt
@require_http_methods(["GET"])
def user_top_rated(request):
    """Get user's top-rated movies and shows"""
    if not request.user.is_authenticated:
        response = JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    try:
        # Get top-rated movies (rating >= 8)
        top_movie_reviews = MovieRating.objects.filter(
            user_id=request.user,
            user_rating__gte=8
        ).select_related('film_id').order_by('-user_rating')[:10]
        
        top_movies = []
        for review in top_movie_reviews:
            film = review.film_id
            top_movies.append({
                'film_id': film.film_id,
                'title': film.film_name,
                'year': film.year,
                'rating': review.user_rating,
                'review': review.user_review,
                'genre': film.genre_id.genre_name if film.genre_id else None,
            })
        
        # Get top-rated shows (rating >= 8)
        top_show_reviews = ShowUserRating.objects.filter(
            user_id=request.user,
            user_rating__gte=8
        ).select_related('show_id').order_by('-user_rating')[:10]
        
        top_shows = []
        for review in top_show_reviews:
            show = review.show_id
            top_shows.append({
                'show_id': show.show_id,
                'title': show.show_name,
                'years': show.years,
                'rating': review.user_rating,
                'review': review.user_review,
                'genre': show.genre_id.genre_name if show.genre_id else None,
            })
        
        response = JsonResponse({
            'success': True,
            'top_movies': top_movies,
            'top_shows': top_shows,
            'total_movies': len(top_movies),
            'total_shows': len(top_shows)
        })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as error:
        response = JsonResponse({'success': False, 'error': str(error)}, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response


@csrf_exempt
@require_http_methods(["GET"])
def personalized_recommendations(request):
    """Get personalized recommendations based on user favorites"""
    if not request.user.is_authenticated:
        response = JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    try:
        # Get user favorites
        fav, _ = Favorites.objects.get_or_create(user_id=request.user)
        
        # Build query based on favorites
        movies_query = AllFilms.objects.all()
        
        if fav.fav_genre:
            movies_query = movies_query.filter(genre_id=fav.fav_genre)
        
        if fav.fav_director:
            movies_query = movies_query.filter(director_id=fav.fav_director)
        
        if fav.fav_decade:
            # Parse decade (e.g., "1990s" -> 1990-1999)
            decade_start = int(fav.fav_decade.replace('s', ''))
            movies_query = movies_query.filter(year__gte=decade_start, year__lt=decade_start + 10)
        
        # Get recommended movies (limit 20, order by rating)
        recommended = movies_query.select_related('genre_id', 'director_id')[:20]
        
        recommendations_data = []
        for film in recommended:
            # Get average rating
            try:
                avg_rating = MovieAverageRating.objects.get(film_id=film)
                rating = float(avg_rating.average_score)
            except:
                rating = 0.0
            
            recommendations_data.append({
                'film_id': film.film_id,
                'title': film.film_name,
                'year': film.year,
                'runtime': film.duration or 0,
                'genre': film.genre_id.genre_name if film.genre_id else None,
                'director': film.director_id.director_name if film.director_id else None,
                'rating': rating,
            })
        
        # Sort by rating
        recommendations_data.sort(key=lambda x: x['rating'], reverse=True)
        
        response = JsonResponse({
            'success': True,
            'recommendations': recommendations_data[:10],
            'count': len(recommendations_data)
        })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as error:
        response = JsonResponse({'success': False, 'error': str(error)}, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response


# ==================== REVIEWS ENDPOINTS ====================

@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def movie_reviews(request, film_id=None):
    """Get, post, update, or delete movie reviews"""
    if not request.user.is_authenticated and request.method != 'GET':
        response = JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    try:
        if request.method == 'GET':
            # Get all reviews for a movie, or all reviews if no film_id
            if film_id:
                reviews = MovieRating.objects.filter(film_id=film_id).select_related('user_id', 'film_id')
            else:
                reviews = MovieRating.objects.all().select_related('user_id', 'film_id')[:100]
            
            reviews_data = []
            for review in reviews:
                reviews_data.append({
                    'review_id': review.id,
                    'film_id': review.film_id.film_id,
                    'film_name': review.film_id.film_name,
                    'user_id': review.user_id.user_id,
                    'user_email': review.user_id.email,
                    'rating': review.user_rating,
                    'review': review.user_review,
                    'date': review.id,  # Using id as proxy for date
                })
            response = JsonResponse({
                'success': True,
                'reviews': reviews_data,
                'count': len(reviews_data)
            })
        elif request.method == 'POST':
            # Create new review
            body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            data = json.loads(body)
            film = AllFilms.objects.get(film_id=film_id)
            rating = data.get('rating', 5)
            review_text = data.get('review', '')
            
            review, created = MovieRating.objects.update_or_create(
                film_id=film,
                user_id=request.user,
                defaults={
                    'user_rating': rating,
                    'user_review': review_text
                }
            )
            AuditLog.objects.create(
                changes_to_data=f"User {request.user.email} posted review for movie '{film.film_name}' (Rating: {rating})"
            )
            response = JsonResponse({
                'success': True,
                'message': 'Review posted' if created else 'Review updated',
                'review': {
                    'review_id': review.id,
                    'film_id': film.film_id,
                    'film_name': film.film_name,
                    'user_id': request.user.user_id,
                    'rating': review.user_rating,
                    'review': review.user_review,
                }
            })
        elif request.method == 'PUT':
            # Update review
            body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            data = json.loads(body)
            review = MovieRating.objects.get(film_id=film_id, user_id=request.user)
            review.user_rating = data.get('rating', review.user_rating)
            review.user_review = data.get('review', review.user_review)
            review.save()
            AuditLog.objects.create(
                changes_to_data=f"User {request.user.email} updated review for movie '{review.film_id.film_name}'"
            )
            response = JsonResponse({
                'success': True,
                'message': 'Review updated',
                'review': {
                    'review_id': review.id,
                    'film_id': review.film_id.film_id,
                    'rating': review.user_rating,
                    'review': review.user_review,
                }
            })
        else:  # DELETE
            review = MovieRating.objects.get(film_id=film_id, user_id=request.user)
            film_name = review.film_id.film_name
            review.delete()
            AuditLog.objects.create(
                changes_to_data=f"User {request.user.email} deleted review for movie '{film_name}'"
            )
            response = JsonResponse({
                'success': True,
                'message': 'Review deleted'
            })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except AllFilms.DoesNotExist:
        response = JsonResponse({'success': False, 'error': 'Movie not found'}, status=404)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except MovieRating.DoesNotExist:
        response = JsonResponse({'success': False, 'error': 'Review not found'}, status=404)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as error:
        response = JsonResponse({'success': False, 'error': str(error)}, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def show_reviews(request, show_id=None):
    """Get, post, update, or delete show reviews"""
    if not request.user.is_authenticated and request.method != 'GET':
        response = JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    try:
        if request.method == 'GET':
            if show_id:
                reviews = ShowUserRating.objects.filter(show_id=show_id).select_related('user_id', 'show_id')
            else:
                reviews = ShowUserRating.objects.all().select_related('user_id', 'show_id')[:100]
            
            reviews_data = []
            for review in reviews:
                reviews_data.append({
                    'review_id': review.id,
                    'show_id': review.show_id.show_id,
                    'show_name': review.show_id.show_name,
                    'user_id': review.user_id.user_id,
                    'user_email': review.user_id.email,
                    'rating': review.user_rating,
                    'review': review.user_review,
                })
            response = JsonResponse({
                'success': True,
                'reviews': reviews_data,
                'count': len(reviews_data)
            })
        elif request.method == 'POST':
            body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            data = json.loads(body)
            show = AllShows.objects.get(show_id=show_id)
            rating = data.get('rating', 5)
            review_text = data.get('review', '')
            
            review, created = ShowUserRating.objects.update_or_create(
                show_id=show,
                user_id=request.user,
                defaults={
                    'user_rating': rating,
                    'user_review': review_text
                }
            )
            AuditLog.objects.create(
                changes_to_data=f"User {request.user.email} posted review for show '{show.show_name}' (Rating: {rating})"
            )
            response = JsonResponse({
                'success': True,
                'message': 'Review posted' if created else 'Review updated',
                'review': {
                    'review_id': review.id,
                    'show_id': show.show_id,
                    'show_name': show.show_name,
                    'user_id': request.user.user_id,
                    'rating': review.user_rating,
                    'review': review.user_review,
                }
            })
        elif request.method == 'PUT':
            body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            data = json.loads(body)
            review = ShowUserRating.objects.get(show_id=show_id, user_id=request.user)
            review.user_rating = data.get('rating', review.user_rating)
            review.user_review = data.get('review', review.user_review)
            review.save()
            AuditLog.objects.create(
                changes_to_data=f"User {request.user.email} updated review for show '{review.show_id.show_name}'"
            )
            response = JsonResponse({
                'success': True,
                'message': 'Review updated',
                'review': {
                    'review_id': review.id,
                    'show_id': review.show_id.show_id,
                    'rating': review.user_rating,
                    'review': review.user_review,
                }
            })
        else:  # DELETE
            review = ShowUserRating.objects.get(show_id=show_id, user_id=request.user)
            show_name = review.show_id.show_name
            review.delete()
            AuditLog.objects.create(
                changes_to_data=f"User {request.user.email} deleted review for show '{show_name}'"
            )
            response = JsonResponse({
                'success': True,
                'message': 'Review deleted'
            })
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except AllShows.DoesNotExist:
        response = JsonResponse({'success': False, 'error': 'Show not found'}, status=404)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except ShowUserRating.DoesNotExist:
        response = JsonResponse({'success': False, 'error': 'Review not found'}, status=404)
        response['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as error:
        response = JsonResponse({'success': False, 'error': str(error)}, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response

