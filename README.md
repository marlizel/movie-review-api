# Movie Review API

A Django + Django REST Framework (DRF) API for managing movie reviews. Users can create accounts, add reviews for movies, and view or update their own reviews. The API includes authentication and permission controls for secure access.

## Features

- **User management**: create, update, and view users  
- **Review management (CRUD)**:  
  - Create a review for a movie  
  - Read reviews (all or by specific movie)  
  - Update and delete only your own reviews  
- **Random Movie endpoint**: fetch random movies from TMDb, optionally filtered by genre  
- **RESTful API endpoints**  
- **Authentication**: Django built-in user system (session or basic auth)  

## API Endpoints

- **Users**:  
  - `GET /api/users/` – list users  
  - `POST /api/users/` – create user  
  - `GET /api/users/<id>/` – retrieve user  
  - `PUT/PATCH /api/users/<id>/` – update user (authenticated)  
  - `DELETE /api/users/<id>/` – delete user (authenticated)  

- **Reviews**:  
  - `GET /api/reviews/` – list all reviews  
  - `POST /api/reviews/` – create review (authenticated)  
  - `GET /api/reviews/<id>/` – retrieve review  
  - `PUT/PATCH /api/reviews/<id>/` – update review (owner only)  
  - `DELETE /api/reviews/<id>/` – delete review (owner only)  

- **Random Movie**:  
  - `GET /api/movies/random/` – fetch random movie  
  - `GET /api/movies/random/?genre=<genre>` – fetch random movie filtered by genre  

## Setup

```bash
git clone https://github.com/your-username/movie-review-api.git
cd movie-review-api
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
