from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailView,
    ReviewListCreateView,
    ReviewDetailView,
    RandomMovieView,
    ApiRootView,
)

urlpatterns = [
    # API root landing page
    path('', ApiRootView.as_view(), name='api-root'),

    # User endpoints
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # Review endpoints
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),

    # Random movie endpoint (TMDb)
    path('movies/random/', RandomMovieView.as_view(), name='random-movie'),
]
