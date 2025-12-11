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

