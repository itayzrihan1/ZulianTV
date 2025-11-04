"""
Radarr API Integration for ZulianTV Bot
"""
import requests
from typing import List, Dict, Optional
import config


class RadarrAPI:
    """Interface for Radarr API operations"""

    def __init__(self):
        self.base_url = config.RADARR_URL
        self.api_key = config.RADARR_API_KEY
        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make an API request to Radarr"""
        url = f"{self.base_url}/api/v3/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Radarr API error: {str(e)}")

    def search_movies(self, query: str) -> List[Dict]:
        """Search for movies by name"""
        return self._make_request('GET', f'movie/lookup?term={query}')

    def get_root_folders(self) -> List[Dict]:
        """Get available root folders for movies"""
        return self._make_request('GET', 'rootfolder')

    def get_quality_profiles(self) -> List[Dict]:
        """Get available quality profiles"""
        return self._make_request('GET', 'qualityprofile')

    def add_movie(self, movie_data: Dict, root_folder_path: str, quality_profile_id: int,
                  monitored: bool = True, search_for_movie: bool = True) -> Dict:
        """
        Add a movie to Radarr

        Args:
            movie_data: Movie info from search_movies()
            root_folder_path: Path where movie will be stored
            quality_profile_id: Quality profile to use
            monitored: Whether to monitor the movie
            search_for_movie: Whether to search for the movie immediately
        """
        payload = {
            'tmdbId': movie_data.get('tmdbId'),
            'title': movie_data.get('title'),
            'year': movie_data.get('year'),
            'qualityProfileId': quality_profile_id,
            'titleSlug': movie_data.get('titleSlug'),
            'images': movie_data.get('images', []),
            'rootFolderPath': root_folder_path,
            'monitored': monitored,
            'addOptions': {
                'searchForMovie': search_for_movie
            }
        }

        return self._make_request('POST', 'movie', payload)

    def add_movie_by_id(self, tmdb_id: int) -> Dict:
        """
        Quick add movie using default settings
        Automatically uses first root folder and quality profile
        """
        # Get the movie info
        search_results = self._make_request('GET', f'movie/lookup/tmdb?tmdbId={tmdb_id}')
        if not search_results:
            raise Exception(f"Movie with TMDB ID {tmdb_id} not found")

        movie_data = search_results

        # Get default root folder and quality profile
        root_folders = self.get_root_folders()
        quality_profiles = self.get_quality_profiles()

        if not root_folders or not quality_profiles:
            raise Exception("No root folders or quality profiles configured in Radarr")

        return self.add_movie(
            movie_data,
            root_folders[0]['path'],
            quality_profiles[0]['id']
        )

    def get_movies_list(self) -> List[Dict]:
        """Get all movies currently in Radarr"""
        return self._make_request('GET', 'movie')

    def search_movie(self, movie_id: int) -> Dict:
        """Trigger a search for a specific movie"""
        return self._make_request('POST', 'command', {
            'name': 'MoviesSearch',
            'movieIds': [movie_id]
        })

    def get_movie_by_id(self, movie_id: int) -> Dict:
        """Get movie details by Radarr movie ID"""
        return self._make_request('GET', f'movie/{movie_id}')
