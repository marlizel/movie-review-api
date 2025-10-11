# Movie Review API

This is a Django + Django REST Framework (DRF) API for managing movie reviews. Users can create accounts, add reviews for movies, and view or update their own reviews. The API supports authentication and permission controls for secure access.

## Features

- User management: create, update, and view users.
- Review management (CRUD):
  - Create a review for a movie
  - Read reviews (all or by specific movie)
  - Update and delete only your own reviews
- Movie information linked to reviews
- RESTful API endpoints
- Authentication with Django built-in user system

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/movie-review-api.git
   cd movie-review-api
