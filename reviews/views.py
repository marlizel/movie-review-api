import random
import requests
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Review, Movie
from .serializers import ReviewSerializer, UserSerializer
from django.conf import settings

# -------------------------------
# User Views
# -------------------------------

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # anyone can create an account

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # only authenticated users can view/update

# -------------------------------
# Review Views
# -------------------------------

class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # automatically link review to logged-in user
        serializer.save(user=self.request.user)

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        # ensure only review owner can update
        if self.get_object().user != self.request.user:
            raise permissions.PermissionDenied("You can only edit your own reviews.")
        serializer.save()

    def perform_destroy(self, instance):
        # ensure only review owner can delete
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own reviews.")
        instance.delete()

# -------------------------------
# Random Movie View with TMDb
# -------------------------------

class RandomMovieView(APIView):
    """
    Returns a random movie from local DB or TMDb.
    Optionally filter by genre using ?genre=<genre_name>.
    """
    TMDB_API_URL = "https://api.themoviedb.org/3/discover/movie"
    TMDB_API_KEY = settings.TMDB_API_KEY  # Use key from settings.py

    def get(self, request, format=None):
        genre_filter = request.query_params.get('genre', None)

        # 1️⃣ Try local database first
        if genre_filter:
            local_movies = Movie.objects.filter(genre__icontains=genre_filter)
        else:
            local_movies = Movie.objects.all()

        if local_movies.exists():
            movie = random.choice(list(local_movies))
            data = {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "genre": movie.genre,
                "release_year": movie.release_year
            }
            return Response(data, status=status.HTTP_200_OK)

        # 2️⃣ If local DB is empty or no matching genre, fetch from TMDb
        params = {
            "api_key": self.TMDB_API_KEY,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "include_adult": False,
            "include_video": False,
            "page": 1,
        }

        if genre_filter:
            # TMDb uses numeric genre IDs; map genre names to IDs
            genre_id = self.get_tmdb_genre_id(genre_filter)
            if genre_id:
                params["with_genres"] = genre_id

        response = requests.get(self.TMDB_API_URL, params=params)
        if response.status_code != 200:
            return Response({"detail": "TMDb API error."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        results = response.json().get("results", [])
        if not results:
            return Response({"detail": "No movies found from TMDb for this filter."}, status=status.HTTP_404_NOT_FOUND)

        movie = random.choice(results)
        data = {
            "id": movie.get("id"),
            "title": movie.get("title"),
            "description": movie.get("overview"),
            "genre": ", ".join([str(g) for g in movie.get("genre_ids", [])]),
            "release_year": movie.get("release_date", "")[:4]
        }
        return Response(data, status=status.HTTP_200_OK)

    def get_tmdb_genre_id(self, genre_name):
        """Map common genre names to TMDb genre IDs"""
        mapping = {
            "action": 28,
            "adventure": 12,
            "animation": 16,
            "comedy": 35,
            "crime": 80,
            "documentary": 99,
            "drama": 18,
            "family": 10751,
            "fantasy": 14,
            "history": 36,
            "horror": 27,
            "music": 10402,
            "mystery": 9648,
            "romance": 10749,
            "science fiction": 878,
            "thriller": 53,
            "war": 10752,
            "western": 37
        }
        return mapping.get(genre_name.lower())
