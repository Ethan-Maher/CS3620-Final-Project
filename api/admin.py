from django.contrib import admin
from .models import (
    User, AllTables, AuditLog,
    MovieDirector, MovieGenre, MovieLanguage, AllFilms,
    MovieRating, MovieAverageRating, WatchedMovie, WatchLaterMovie,
    PreviousSearches, Favorites,
    ShowCertificate, ShowGenre, AllShows,
    ShowUserRating, ShowAverageRating,
    Actors, ActedIn,
    WatchedShow, WatchLaterShow
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email')
    search_fields = ('email',)


@admin.register(AllTables)
class AllTablesAdmin(admin.ModelAdmin):
    list_display = ('table_id', 'table_name')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('table_id', 'date', 'changes_to_data')
    list_filter = ('date',)
    readonly_fields = ('date',)


@admin.register(MovieDirector)
class MovieDirectorAdmin(admin.ModelAdmin):
    list_display = ('director_id', 'director_name')
    search_fields = ('director_name',)


@admin.register(MovieGenre)
class MovieGenreAdmin(admin.ModelAdmin):
    list_display = ('genre_id', 'genre_name')
    search_fields = ('genre_name',)


@admin.register(MovieLanguage)
class MovieLanguageAdmin(admin.ModelAdmin):
    list_display = ('language_id', 'language_name')
    search_fields = ('language_name',)


@admin.register(AllFilms)
class AllFilmsAdmin(admin.ModelAdmin):
    list_display = ('film_id', 'film_name', 'director_id', 'year', 'duration', 'genre_id')
    list_filter = ('year', 'genre_id', 'language_id')
    search_fields = ('film_name',)
    raw_id_fields = ('director_id', 'genre_id', 'language_id')


@admin.register(MovieRating)
class MovieRatingAdmin(admin.ModelAdmin):
    list_display = ('film_id', 'user_id', 'user_rating')
    list_filter = ('user_rating',)
    search_fields = ('film_id__film_name', 'user_id__email')


@admin.register(MovieAverageRating)
class MovieAverageRatingAdmin(admin.ModelAdmin):
    list_display = ('film_name', 'film_id', 'average_score')
    search_fields = ('film_name',)


@admin.register(WatchedMovie)
class WatchedMovieAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'film_id')
    list_filter = ('user_id',)


@admin.register(WatchLaterMovie)
class WatchLaterMovieAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'film_id')
    list_filter = ('user_id',)


@admin.register(PreviousSearches)
class PreviousSearchesAdmin(admin.ModelAdmin):
    list_display = ('search_id', 'user_id', 'director_id', 'film_id')
    list_filter = ('user_id',)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'fav_director', 'fav_actor', 'fav_genre', 'fav_decade')
    search_fields = ('user_id__email',)


@admin.register(ShowCertificate)
class ShowCertificateAdmin(admin.ModelAdmin):
    list_display = ('cert_id', 'cert_rating')


@admin.register(ShowGenre)
class ShowGenreAdmin(admin.ModelAdmin):
    list_display = ('genre_id', 'genre_name')
    search_fields = ('genre_name',)


@admin.register(AllShows)
class AllShowsAdmin(admin.ModelAdmin):
    list_display = ('show_id', 'show_name', 'duration', 'cert_id', 'rating', 'genre_id', 'years')
    list_filter = ('cert_id', 'genre_id', 'years')
    search_fields = ('show_name',)
    raw_id_fields = ('cert_id', 'genre_id')


@admin.register(ShowUserRating)
class ShowUserRatingAdmin(admin.ModelAdmin):
    list_display = ('show_id', 'user_id', 'user_rating')
    list_filter = ('user_rating',)
    search_fields = ('show_id__show_name', 'user_id__email')


@admin.register(ShowAverageRating)
class ShowAverageRatingAdmin(admin.ModelAdmin):
    list_display = ('show_name', 'show_id', 'average_score')
    search_fields = ('show_name',)


@admin.register(Actors)
class ActorsAdmin(admin.ModelAdmin):
    list_display = ('actor_id', 'actor_name', 'film_id')
    search_fields = ('actor_name',)
    raw_id_fields = ('film_id',)


@admin.register(ActedIn)
class ActedInAdmin(admin.ModelAdmin):
    list_display = ('show_id', 'actor_name', 'actor_id')
    list_filter = ('show_id', 'actor_id')
    search_fields = ('actor_name', 'show_id__show_name')


@admin.register(WatchedShow)
class WatchedShowAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'show_id')
    list_filter = ('user_id',)


@admin.register(WatchLaterShow)
class WatchLaterShowAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'show_id')
    list_filter = ('user_id',)

