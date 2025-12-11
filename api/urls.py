from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.movies, name='movies'),
    path('shows/', views.shows, name='shows'),
    path('genres/', views.genres, name='genres'),
    path('show-genres/', views.show_genres, name='show_genres'),
    path('actors/', views.actors, name='actors'),
    path('testdb/', views.testdb, name='testdb'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('check-auth/', views.check_auth, name='check_auth'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    # Watch later endpoints
    path('watch-later/movie/', views.watch_later_movie, name='watch_later_movie'),
    path('watch-later/movie/<int:film_id>/', views.watch_later_movie, name='watch_later_movie_id'),
    path('watch-later/show/', views.watch_later_show, name='watch_later_show'),
    path('watch-later/show/<int:show_id>/', views.watch_later_show, name='watch_later_show_id'),
    # Favorites endpoints
    path('favorites/', views.favorites, name='favorites'),
    path('favorites/top-rated/', views.user_top_rated, name='user_top_rated'),
    path('favorites/recommendations/', views.personalized_recommendations, name='personalized_recommendations'),
    # Reviews endpoints
    path('reviews/movie/', views.movie_reviews, name='movie_reviews'),
    path('reviews/movie/<int:film_id>/', views.movie_reviews, name='movie_reviews_id'),
    path('reviews/show/', views.show_reviews, name='show_reviews'),
    path('reviews/show/<int:show_id>/', views.show_reviews, name='show_reviews_id'),
    # Also handle without trailing slash for POST requests
    path('signup', views.signup, name='signup_no_slash'),
    path('signin', views.signin, name='signin_no_slash'),
]

