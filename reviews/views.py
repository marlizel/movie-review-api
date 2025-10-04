from rest_framework import generics, permissions
from django.contrib.auth.models import User
from .models import Review
from .serializers import ReviewSerializer, UserSerializer

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
