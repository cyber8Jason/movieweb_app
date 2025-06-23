from abc import ABC, abstractmethod
from typing import List, Optional, Dict

class DataManagerInterface(ABC):
    @abstractmethod
    def add_user(self, name: str) -> int:
        """Add a new user and return their ID"""
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        pass

    @abstractmethod
    def add_movie(self, name: str, director: str, year: int, rating: float) -> int:
        """Add a new movie and return its ID"""
        pass

    @abstractmethod
    def get_movie(self, movie_id: int) -> Optional[Dict]:
        """Get movie by ID"""
        pass

    @abstractmethod
    def get_all_movies(self) -> List[Dict]:
        """Get all movies"""
        pass

    @abstractmethod
    def update_movie(self, movie_id: int, name: str, director: str, year: int, rating: float) -> bool:
        """Update movie details"""
        pass

    @abstractmethod
    def delete_movie(self, movie_id: int) -> bool:
        """Delete a movie"""
        pass

    @abstractmethod
    def get_all_users(self) -> List[Dict]:
        """Get all users from the database"""
        pass

    @abstractmethod
    def get_user_movies(self, user_id: int) -> List[Dict]:
        """Get all movies associated with a specific user"""
        pass

    @abstractmethod
    def add_user_movie(self, user_id: int, movie_id: int) -> bool:
        """Associate a movie with a user"""
        pass

    @abstractmethod
    def remove_user_movie(self, user_id: int, movie_id: int) -> bool:
        """Remove a movie association from a user"""
        pass
