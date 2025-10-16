import random
import requests
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from .models import Review
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
        serializer.save(user=self.request.user)

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        if self.get_object().user != self.request.user:
            raise permissions.PermissionDenied("You can only edit your own reviews.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own reviews.")
        instance.delete()

# -------------------------------
# Random Movie View with TMDb
# -------------------------------

class RandomMovieView(APIView):
    """
    Returns a random movie from TMDb.
    Optionally filter by genre using ?genre=<genre_name>.
    """
    TMDB_DISCOVER_URL = "https://api.themoviedb.org/3/discover/movie"
    TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie"
    TMDB_API_KEY = getattr(settings, "TMDB_API_KEY", None)

    def get(self, request, format=None):
        if not self.TMDB_API_KEY:
            return Response({"detail": "TMDB API key not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        genre_filter = request.query_params.get('genre', None)
        params = {
            "api_key": self.TMDB_API_KEY,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "include_adult": False,
            "include_video": False,
            "page": 1,
        }

        if genre_filter:
            genre_id = self.get_tmdb_genre_id(genre_filter)
            if genre_id:
                params["with_genres"] = genre_id

        r = requests.get(self.TMDB_DISCOVER_URL, params=params, timeout=10)
        if r.status_code != 200:
            return Response({"detail": "TMDb API error."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        data = r.json()
        results = data.get("results", [])
        total_pages = data.get("total_pages", 1)

        if not results:
            return Response({"detail": "No movies found from TMDb for this filter."}, status=status.HTTP_404_NOT_FOUND)

        if total_pages > 1:
            try:
                page = random.randint(1, min(total_pages, 20))
                params["page"] = page
                r = requests.get(self.TMDB_DISCOVER_URL, params=params, timeout=10)
                results = r.json().get("results", []) or results
            except Exception:
                pass

        movie = random.choice(results)
        movie_id = movie.get("id")

        try:
            details = requests.get(f"{self.TMDB_MOVIE_URL}/{movie_id}", params={"api_key": self.TMDB_API_KEY}, timeout=10)
            movie_details = details.json() if details.status_code == 200 else movie
        except Exception:
            movie_details = movie

        response_data = {
            "id": movie_details.get("id"),
            "title": movie_details.get("title") or movie_details.get("name"),
            "overview": movie_details.get("overview"),
            "genres": [g.get("name") for g in movie_details.get("genres", [])] if isinstance(movie_details.get("genres"), list) else movie_details.get("genre_ids", []),
            "release_date": movie_details.get("release_date") or movie_details.get("first_air_date"),
            "tmdb_url": f"https://www.themoviedb.org/movie/{movie_details.get('id')}" if movie_details.get('id') else None
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def get_tmdb_genre_id(self, genre_name):
        mapping = {
            "action": 28, "adventure": 12, "animation": 16, "comedy": 35,
            "crime": 80, "documentary": 99, "drama": 18, "family": 10751,
            "fantasy": 14, "history": 36, "horror": 27, "music": 10402,
            "mystery": 9648, "romance": 10749, "science fiction": 878,
            "sci-fi": 878, "thriller": 53, "war": 10752, "western": 37
        }
        return mapping.get(genre_name.lower())

# -------------------------------
# API Root View
# -------------------------------

class ApiRootView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        return Response({
            "users": reverse('user-list-create', request=request, format=format),
            "reviews": reverse('review-list-create', request=request, format=format),
            "random_movie": reverse('random-movie', request=request, format=format),
        })
