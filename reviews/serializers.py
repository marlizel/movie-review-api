from rest_framework import serializers
from .models import Review, Movie
from django.contrib.auth.models import User

class ReviewSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'movie', 'movie_title', 'comment', 'rating', 'user', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
