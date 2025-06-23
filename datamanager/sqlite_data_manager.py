from typing import List, Optional, Dict
from .data_manager_interface import DataManagerInterface
from .models import db, User, Movie
from sqlalchemy.exc import SQLAlchemyError

class DatabaseError(Exception):
    """Base class for database errors"""
    pass

class UserNotFoundError(DatabaseError):
    """Raised when a user is not found"""
    pass

class MovieNotFoundError(DatabaseError):
    """Raised when a movie is not found"""
    pass

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the data manager with the Flask app"""
        try:
            with app.app_context():
                db.create_all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error initializing database: {str(e)}")

    def add_user(self, name: str) -> int:
        try:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()
            return user.id
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Error adding user: {str(e)}")

    def get_user(self, user_id: int) -> Optional[Dict]:
        try:
            user = User.query.get(user_id)
            if user:
                return {"id": user.id, "name": user.name}
            raise UserNotFoundError(f"User with ID {user_id} not found")
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {str(e)}")

    def add_movie(self, name: str, director: str, year: int, rating: float, poster: str = None) -> int:
        try:
            movie = Movie(name=name, director=director, year=year, rating=rating, poster=poster)
            db.session.add(movie)
            db.session.commit()
            return movie.id
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Error adding movie: {str(e)}")

    def get_movie(self, movie_id: int) -> Optional[Dict]:
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                return {
                    "id": movie.id,
                    "name": movie.name,
                    "director": movie.director,
                    "year": movie.year,
                    "rating": movie.rating,
                    "poster": movie.poster
                }
            raise MovieNotFoundError(f"Movie with ID {movie_id} not found")
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {str(e)}")

    def get_all_movies(self) -> List[Dict]:
        try:
            movies = Movie.query.all()
            return [{
                "id": movie.id,
                "name": movie.name,
                "director": movie.director,
                "year": movie.year,
                "rating": movie.rating,
                "poster": movie.poster
            } for movie in movies]
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {str(e)}")

    def update_movie(self, movie_id: int, name: str, director: str, year: int, rating: float, poster: str = None) -> bool:
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                movie.name = name
                movie.director = director
                movie.year = year
                movie.rating = rating
                if poster:
                    movie.poster = poster
                db.session.commit()
                return True
            raise MovieNotFoundError(f"Movie with ID {movie_id} not found")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Error updating movie: {str(e)}")

    def get_all_users(self) -> List[Dict]:
        try:
            users = User.query.all()
            return [{"id": user.id, "name": user.name} for user in users]
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {str(e)}")

    def get_user_movies(self, user_id: int) -> List[Dict]:
        try:
            user = User.query.get(user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            return [{
                "id": movie.id,
                "name": movie.name,
                "director": movie.director,
                "year": movie.year,
                "rating": movie.rating,
                "poster": movie.poster
            } for movie in user.movies]
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {str(e)}")

    def add_user_movie(self, user_id: int, movie_id: int) -> bool:
        try:
            user = User.query.get(user_id)
            movie = Movie.query.get(movie_id)

            if not user or not movie:
                return False

            user.movies.append(movie)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Error adding movie to user: {str(e)}")

    def remove_user_movie(self, user_id: int, movie_id: int) -> bool:
        try:
            user = User.query.get(user_id)
            movie = Movie.query.get(movie_id)

            if not user or not movie:
                return False

            user.movies.remove(movie)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Error removing movie from user: {str(e)}")

    def delete_movie(self, movie_id: int) -> bool:
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                db.session.delete(movie)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Error deleting movie: {str(e)}")

    def search_movies(self, search_query: str) -> List[Dict]:
        try:
            # Suche nach Filmen, die den Suchbegriff im Namen enthalten (case-insensitive)
            search_pattern = f"%{search_query}%"
            movies = Movie.query.filter(Movie.name.ilike(search_pattern)).all()

            return [{
                "id": movie.id,
                "name": movie.name,
                "director": movie.director,
                "year": movie.year,
                "rating": movie.rating,
                "poster": movie.poster
            } for movie in movies]
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {str(e)}")
