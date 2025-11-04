"""
Sonarr API Integration for ZulianTV Bot
"""
import requests
from typing import List, Dict, Optional
import config


class SonarrAPI:
    """Interface for Sonarr API operations"""

    def __init__(self):
        self.base_url = config.SONARR_URL
        self.api_key = config.SONARR_API_KEY
        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make an API request to Sonarr"""
        url = f"{self.base_url}/api/v3/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Sonarr API error: {str(e)}")

    def search_series(self, query: str) -> List[Dict]:
        """Search for TV series by name"""
        return self._make_request('GET', f'series/lookup?term={query}')

    def get_root_folders(self) -> List[Dict]:
        """Get available root folders for TV shows"""
        return self._make_request('GET', 'rootfolder')

    def get_quality_profiles(self) -> List[Dict]:
        """Get available quality profiles"""
        return self._make_request('GET', 'qualityprofile')

    def add_series(self, series_data: Dict, root_folder_path: str, quality_profile_id: int,
                   monitor: str = 'all', search_for_missing: bool = True) -> Dict:
        """
        Add a series to Sonarr

        Args:
            series_data: Series info from search_series()
            root_folder_path: Path where series will be stored
            quality_profile_id: Quality profile to use
            monitor: What to monitor ('all', 'future', 'missing', 'existing', 'none')
            search_for_missing: Whether to search for missing episodes immediately
        """
        payload = {
            'tvdbId': series_data.get('tvdbId'),
            'title': series_data.get('title'),
            'qualityProfileId': quality_profile_id,
            'titleSlug': series_data.get('titleSlug'),
            'images': series_data.get('images', []),
            'seasons': series_data.get('seasons', []),
            'rootFolderPath': root_folder_path,
            'monitored': True,
            'addOptions': {
                'monitor': monitor,
                'searchForMissingEpisodes': search_for_missing
            }
        }

        return self._make_request('POST', 'series', payload)

    def add_series_by_id(self, tvdb_id: int) -> Dict:
        """
        Quick add series using default settings
        Automatically uses first root folder and quality profile
        """
        # Get the series info
        search_results = self._make_request('GET', f'series/lookup?term=tvdb:{tvdb_id}')
        if not search_results:
            raise Exception(f"Series with TVDB ID {tvdb_id} not found")

        series_data = search_results[0]

        # Get default root folder and quality profile
        root_folders = self.get_root_folders()
        quality_profiles = self.get_quality_profiles()

        if not root_folders or not quality_profiles:
            raise Exception("No root folders or quality profiles configured in Sonarr")

        return self.add_series(
            series_data,
            root_folders[0]['path'],
            quality_profiles[0]['id']
        )

    def get_series_list(self) -> List[Dict]:
        """Get all series currently in Sonarr"""
        return self._make_request('GET', 'series')

    def search_episode(self, episode_id: int) -> Dict:
        """Trigger a search for a specific episode"""
        payload = {'episodeIds': [episode_id]}
        return self._make_request('POST', 'command', {
            'name': 'EpisodeSearch',
            'episodeIds': [episode_id]
        })

    def get_series_by_id(self, series_id: int) -> Dict:
        """Get series details by Sonarr series ID"""
        return self._make_request('GET', f'series/{series_id}')
