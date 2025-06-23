import os
import requests
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OMDBService:
    def __init__(self, api_key: str = None):
        """
        Initialize the OMDB service with an API key.
        The key can be passed directly or read from OMDB_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('OMDB_API_KEY')
        if not self.api_key:
            raise ValueError("OMDB API key is required. Set it in .env file or pass it directly.")

        self.base_url = "https://www.omdbapi.com/"

    def search_movie(self, title: str) -> Optional[Dict]:
        """
        Search for a movie by title and return its details.
        Returns None if the movie is not found.
        """
        params = {
            'apikey': self.api_key,
            't': title,
            'type': 'movie',
            'r': 'json'  # Explizit JSON-Response anfordern
        }

        try:
            print(f"Making request to OMDB for {title} with API key: {self.api_key}")  # Debug
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10,
                verify=True
            )
            print(f"Response status code: {response.status_code}")  # Debug
            print(f"Response content: {response.text}")  # Debug

            response.raise_for_status()
            data = response.json()

            if data.get('Response') == 'True':
                try:
                    rating = float(data.get('imdbRating', '0').replace('N/A', '0'))
                except ValueError:
                    rating = 0.0

                movie_data = {
                    'title': data.get('Title', title),
                    'director': data.get('Director', 'Unknown'),
                    'year': data.get('Year', 'N/A'),
                    'rating': rating,
                    'poster': data.get('Poster', 'N/A')
                }
                print(f"Processed movie data: {movie_data}")  # Debug
                return movie_data

            print(f"No data found for movie: {title}, Response: {data}")  # Debug
            return None

        except requests.RequestException as e:
            print(f"Error making request for {title}: {str(e)}")  # Debug
            return None
        except Exception as e:
            print(f"Unexpected error for {title}: {str(e)}")  # Debug
            return None

    @classmethod
    def create_from_env(cls) -> 'OMDBService':
        """
        Factory method to create an OMDBService from environment variables
        """
        api_key = os.getenv('OMDB_API_KEY')
        if not api_key:
            raise ValueError("OMDB_API_KEY must be set in .env file")
        return cls(api_key)
