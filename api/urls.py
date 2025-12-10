from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.movies, name='movies'),
    path('shows/', views.shows, name='shows'),
    path('genres/', views.genres, name='genres'),
    path('show-genres/', views.show_genres, name='show_genres'),
    path('actors/', views.actors, name='actors'),
    path('testdb/', views.testdb, name='testdb'),
]

