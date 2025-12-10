from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator


# User Management
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=128)  # Django handles hashing
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        db_table = 'User'
    
    def __str__(self):
        return self.email


# Audit and System Tables
class AllTables(models.Model):
    table_id = models.AutoField(primary_key=True, db_column='Table_id')
    table_name = models.CharField(max_length=255, db_column='Table_name')
    
    class Meta:
        db_table = 'All_tables'
    
    def __str__(self):
        return self.table_name


class AuditLog(models.Model):
    table_id = models.AutoField(primary_key=True, db_column='Table_id')
    date = models.DateTimeField(auto_now_add=True, db_column='date')
    changes_to_data = models.TextField(db_column='changes_to_data')
    
    class Meta:
        db_table = 'Audit_log'
    
    def __str__(self):
        return f"Audit {self.table_id} - {self.date}"


# Movie Directors
class MovieDirector(models.Model):
    director_id = models.AutoField(primary_key=True, db_column='Director_id')
    director_name = models.CharField(max_length=255, db_column='Director_name')
    
    class Meta:
        db_table = 'Movie_Directors'
    
    def __str__(self):
        return self.director_name


# Movie Genres
class MovieGenre(models.Model):
    genre_id = models.AutoField(primary_key=True, db_column='Genre_id')
    genre_name = models.CharField(max_length=100, db_column='Genre_name')
    
    class Meta:
        db_table = 'Movie_Genre'
    
    def __str__(self):
        return self.genre_name


# Movie Languages
class MovieLanguage(models.Model):
    language_id = models.AutoField(primary_key=True, db_column='Language_id')
    language_name = models.CharField(max_length=100, db_column='Language_name')
    
    class Meta:
        db_table = 'Movie_Language'
    
    def __str__(self):
        return self.language_name


# All Films
class AllFilms(models.Model):
    film_id = models.AutoField(primary_key=True, db_column='Film_id')
    film_name = models.CharField(max_length=255, db_column='Film_name')
    director_id = models.ForeignKey(MovieDirector, on_delete=models.SET_NULL, null=True, db_column='Director_id')
    year = models.IntegerField(null=True, blank=True, db_column='Year')
    duration = models.IntegerField(null=True, blank=True, db_column='Duration')  # in minutes
    genre_id = models.ForeignKey(MovieGenre, on_delete=models.SET_NULL, null=True, db_column='Genre_id')
    language_id = models.ForeignKey(MovieLanguage, on_delete=models.SET_NULL, null=True, db_column='Language_id')
    
    class Meta:
        db_table = 'All_Films'
    
    def __str__(self):
        return self.film_name


# Movie Ratings
class MovieRating(models.Model):
    film_id = models.ForeignKey(AllFilms, on_delete=models.CASCADE, db_column='Film_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='User_id')
    user_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        db_column='User_rating'
    )
    user_review = models.TextField(blank=True, null=True, db_column='User_review')
    
    class Meta:
        db_table = 'Movie_rating'
        unique_together = [['film_id', 'user_id']]
    
    def __str__(self):
        return f"{self.user_id.email} - {self.film_id.film_name}: {self.user_rating}"


# Movie Average Rating
class MovieAverageRating(models.Model):
    film_name = models.CharField(max_length=255, db_column='Film_name')
    film_id = models.OneToOneField(AllFilms, on_delete=models.CASCADE, primary_key=True, db_column='Film_id')
    average_score = models.DecimalField(max_digits=3, decimal_places=2, db_column='Average_score')
    
    class Meta:
        db_table = 'Movie_Average_rating'
    
    def __str__(self):
        return f"{self.film_name}: {self.average_score}"


# Watched Movies
class WatchedMovie(models.Model):
    film_id = models.ForeignKey(AllFilms, on_delete=models.CASCADE, db_column='Film_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='User_id')
    
    class Meta:
        db_table = 'Watched_movie'
        unique_together = [['film_id', 'user_id']]
    
    def __str__(self):
        return f"{self.user_id.email} watched {self.film_id.film_name}"


# Watch Later Movies
class WatchLaterMovie(models.Model):
    film_id = models.ForeignKey(AllFilms, on_delete=models.CASCADE, db_column='Film_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='User_id')
    
    class Meta:
        db_table = 'Watch_later_movie'
        unique_together = [['film_id', 'user_id']]
    
    def __str__(self):
        return f"{self.user_id.email} wants to watch {self.film_id.film_name}"


# Previous Searches
class PreviousSearches(models.Model):
    search_id = models.AutoField(primary_key=True, db_column='Search_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='User_id')
    director_id = models.ForeignKey(MovieDirector, on_delete=models.SET_NULL, null=True, blank=True, db_column='Director_id')
    film_id = models.ForeignKey(AllFilms, on_delete=models.SET_NULL, null=True, blank=True, db_column='Film_id')
    
    class Meta:
        db_table = 'Previous_Searches'
    
    def __str__(self):
        return f"Search {self.search_id} by {self.user_id.email}"


# Favorites
class Favorites(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, db_column='User_id')
    fav_director = models.ForeignKey(MovieDirector, on_delete=models.SET_NULL, null=True, blank=True, db_column='Fav_director')
    fav_actor = models.CharField(max_length=255, blank=True, null=True, db_column='Fav_actor')
    fav_genre = models.ForeignKey(MovieGenre, on_delete=models.SET_NULL, null=True, blank=True, db_column='Fav_genre')
    fav_decade = models.CharField(max_length=20, blank=True, null=True, db_column='Fav_decade')  # e.g., "1990s"
    
    class Meta:
        db_table = 'Favorites'
    
    def __str__(self):
        return f"Favorites for {self.user_id.email}"


# Show Certificate
class ShowCertificate(models.Model):
    cert_id = models.AutoField(primary_key=True, db_column='cert_id')
    cert_rating = models.CharField(max_length=20, db_column='cert_rating')  # G, PG, PG-13, R, etc.
    
    class Meta:
        db_table = 'Show_certificate'
    
    def __str__(self):
        return self.cert_rating


# Show Genre
class ShowGenre(models.Model):
    genre_id = models.AutoField(primary_key=True, db_column='genre_id')
    genre_name = models.CharField(max_length=100, db_column='genre_name')
    
    class Meta:
        db_table = 'Show_genre'
    
    def __str__(self):
        return self.genre_name


# All Shows
class AllShows(models.Model):
    show_id = models.AutoField(primary_key=True, db_column='Show_id')
    show_name = models.CharField(max_length=255, db_column='Show_name')
    duration = models.IntegerField(null=True, blank=True, db_column='Duration')  # in minutes
    cert_id = models.ForeignKey(ShowCertificate, on_delete=models.SET_NULL, null=True, db_column='Cert_id')
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, db_column='rating')
    genre_id = models.ForeignKey(ShowGenre, on_delete=models.SET_NULL, null=True, db_column='Genre_id')
    years = models.CharField(max_length=50, blank=True, null=True, db_column='Years')  # e.g., "2020-2024"
    
    class Meta:
        db_table = 'All_shows'
    
    def __str__(self):
        return self.show_name


# Show User Rating
class ShowUserRating(models.Model):
    show_id = models.ForeignKey(AllShows, on_delete=models.CASCADE, db_column='Show_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='User_id')
    user_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        db_column='User_rating'
    )
    user_review = models.TextField(blank=True, null=True, db_column='User_review')
    
    class Meta:
        db_table = 'Show_user_rating'
        unique_together = [['show_id', 'user_id']]
    
    def __str__(self):
        return f"{self.user_id.email} - {self.show_id.show_name}: {self.user_rating}"


# Show Average Rating
class ShowAverageRating(models.Model):
    show_name = models.CharField(max_length=255, db_column='Film_name')  # Note: keeping original column name
    show_id = models.OneToOneField(AllShows, on_delete=models.CASCADE, primary_key=True, db_column='Film_id')  # Note: keeping original column name
    average_score = models.DecimalField(max_digits=3, decimal_places=2, db_column='Average_score')
    
    class Meta:
        db_table = 'Show_average_rating'
    
    def __str__(self):
        return f"{self.show_name}: {self.average_score}"


# Actors
class Actors(models.Model):
    actor_id = models.AutoField(primary_key=True, db_column='Actor_id')
    actor_name = models.CharField(max_length=255, db_column='Actor_name')
    film_id = models.ForeignKey(AllFilms, on_delete=models.SET_NULL, null=True, blank=True, db_column='film_id')
    
    class Meta:
        db_table = 'Actors'
    
    def __str__(self):
        return self.actor_name


# Acted In (Shows)
class ActedIn(models.Model):
    show_id = models.ForeignKey(AllShows, on_delete=models.CASCADE, db_column='Show_id')
    actor_name = models.CharField(max_length=255, db_column='Actor_name')
    actor_id = models.ForeignKey(Actors, on_delete=models.CASCADE, db_column='Actor_id')
    
    class Meta:
        db_table = 'Acted_in'
        unique_together = [['show_id', 'actor_id']]
    
    def __str__(self):
        return f"{self.actor_name} in {self.show_id.show_name}"


# Watched Shows
class WatchedShow(models.Model):
    show_id = models.ForeignKey(AllShows, on_delete=models.CASCADE, db_column='Show_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    
    class Meta:
        db_table = 'Watched_show'
        unique_together = [['show_id', 'user_id']]
    
    def __str__(self):
        return f"{self.user_id.email} watched {self.show_id.show_name}"


# Watch Later Shows
class WatchLaterShow(models.Model):
    show_id = models.ForeignKey(AllShows, on_delete=models.CASCADE, db_column='Show_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='User_id')
    
    class Meta:
        db_table = 'Watch_later_show'
        unique_together = [['show_id', 'user_id']]
    
    def __str__(self):
        return f"{self.user_id.email} wants to watch {self.show_id.show_name}"

