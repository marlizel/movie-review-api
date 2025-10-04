from django.test import TestCase
from django.contrib.auth.models import User
from .models import Movie, Review

class BasicTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Create a movie
        self.movie = Movie.objects.create(title='Test Movie', description='Test desc', genre='Action', release_year=2020)
    
    def test_user_created(self):
        user_count = User.objects.count()
        self.assertEqual(user_count, 1)
    
    def test_movie_created(self):
        movie_count = Movie.objects.count()
        self.assertEqual(movie_count, 1)
    
    def test_review_creation(self):
        review = Review.objects.create(user=self.user, movie=self.movie, rating=5, comment='Great movie!')
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great movie!')
        self.assertEqual(review.user.username, 'testuser')
        self.assertEqual(review.movie.title, 'Test Movie')
