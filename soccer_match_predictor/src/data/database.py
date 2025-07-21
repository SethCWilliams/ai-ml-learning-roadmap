"""Database client and caching layer for Soccer Match Predictor."""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Cache duration configuration for different data types."""
    fixtures: int = 1  # hours - live match data changes frequently
    team_stats: int = 24  # hours - season stats change daily
    team_schedules: int = 6  # hours - schedules updated periodically
    default: int = 6  # hours - general API responses


class DatabaseClient:
    """Supabase client with intelligent caching for ESPN API responses."""
    
    def __init__(self):
        """Initialize Supabase client with connection pooling."""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not all([self.supabase_url, self.supabase_anon_key]):
            raise ValueError(
                "Missing Supabase configuration. Please set SUPABASE_URL and SUPABASE_ANON_KEY "
                "environment variables."
            )
        
        # Use service key for full access (anon key for read-only operations)
        key = self.supabase_service_key or self.supabase_anon_key
        
        # Configure client options for better performance
        options = ClientOptions(
            postgrest_client_timeout=30,
            storage_client_timeout=30,
            schema="public"
        )
        
        self.client: Client = create_client(self.supabase_url, key, options)
        self.cache_config = CacheConfig()
        
        logger.info("Database client initialized successfully")
    
    # === Cache Management ===
    
    def _generate_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Generate unique hash for cache key."""
        cache_data = {
            'endpoint': endpoint,
            'params': params or {}
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_cached_response(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Retrieve cached API response if still valid."""
        cache_key = self._generate_cache_key(endpoint, params)
        
        try:
            result = self.client.table('api_cache').select('*').eq('endpoint_hash', cache_key).execute()
            
            if result.data:
                cache_entry = result.data[0]
                expires_at = datetime.fromisoformat(cache_entry['expires_at'].replace('Z', '+00:00'))
                
                if datetime.now(expires_at.tzinfo) < expires_at:
                    logger.debug(f"Cache hit for {endpoint}")
                    return cache_entry['response_data']
                else:
                    # Cache expired, clean it up
                    self._delete_expired_cache_entry(cache_key)
                    logger.debug(f"Cache expired for {endpoint}")
            
        except Exception as e:
            logger.warning(f"Error retrieving cache: {e}")
        
        return None
    
    def cache_response(
        self, 
        endpoint: str, 
        response_data: Dict, 
        cache_hours: Optional[int] = None,
        params: Optional[Dict] = None
    ) -> None:
        """Cache API response with expiration."""
        if not response_data:
            return
        
        cache_key = self._generate_cache_key(endpoint, params)
        cache_hours = cache_hours or self.cache_config.default
        expires_at = datetime.utcnow() + timedelta(hours=cache_hours)
        
        try:
            # Use upsert to handle duplicate keys
            self.client.table('api_cache').upsert({
                'endpoint_hash': cache_key,
                'response_data': response_data,
                'expires_at': expires_at.isoformat()
            }).execute()
            
            logger.debug(f"Cached response for {endpoint} (expires in {cache_hours}h)")
            
        except Exception as e:
            logger.warning(f"Error caching response: {e}")
    
    def _delete_expired_cache_entry(self, cache_key: str) -> None:
        """Delete expired cache entry."""
        try:
            self.client.table('api_cache').delete().eq('endpoint_hash', cache_key).execute()
        except Exception as e:
            logger.warning(f"Error deleting expired cache: {e}")
    
    def clear_cache(self, older_than_hours: int = 24) -> int:
        """Clear old cache entries. Returns number of entries cleared."""
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        try:
            result = self.client.table('api_cache').delete().lt(
                'expires_at', 
                cutoff_time.isoformat()
            ).execute()
            
            count = len(result.data) if result.data else 0
            logger.info(f"Cleared {count} expired cache entries")
            return count
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0
    
    # === League Management ===
    
    def get_leagues(self, active_only: bool = True) -> List[Dict]:
        """Get all leagues."""
        query = self.client.table('leagues').select('*')
        
        if active_only:
            query = query.eq('active', True)
        
        result = query.execute()
        return result.data or []
    
    def get_league_by_espn_code(self, espn_code: str) -> Optional[Dict]:
        """Get league by ESPN code (e.g., 'eng.1', 'usa.1')."""
        result = self.client.table('leagues').select('*').eq('espn_code', espn_code).execute()
        return result.data[0] if result.data else None
    
    # === Team Management ===
    
    def upsert_team(self, team_data: Dict) -> Dict:
        """Insert or update team data."""
        result = self.client.table('teams').upsert(team_data).execute()
        return result.data[0] if result.data else {}
    
    def get_teams_by_league(self, league_id: int, active_only: bool = True) -> List[Dict]:
        """Get all teams in a league."""
        query = self.client.table('teams').select('*').eq('league_id', league_id)
        
        if active_only:
            query = query.eq('active', True)
        
        result = query.execute()
        return result.data or []
    
    def get_team_by_espn_id(self, espn_id: str, league_id: Optional[int] = None) -> Optional[Dict]:
        """Get team by ESPN ID."""
        query = self.client.table('teams').select('*').eq('espn_id', espn_id)
        
        if league_id:
            query = query.eq('league_id', league_id)
        
        result = query.execute()
        return result.data[0] if result.data else None
    
    # === Fixture Management ===
    
    def upsert_fixtures(self, fixtures_data: List[Dict]) -> List[Dict]:
        """Insert or update multiple fixtures."""
        if not fixtures_data:
            return []
        
        result = self.client.table('fixtures').upsert(fixtures_data).execute()
        return result.data or []
    
    def get_fixtures_by_date(
        self, 
        date: str, 
        league_id: Optional[int] = None,
        include_team_names: bool = True
    ) -> List[Dict]:
        """Get fixtures for a specific date."""
        if include_team_names:
            # Use the view that includes team names
            query = self.client.from_('fixture_details').select('*')
        else:
            query = self.client.table('fixtures').select('*')
        
        # Filter by date (assuming date is in YYYY-MM-DD format)
        query = query.gte('date', f"{date}T00:00:00Z").lt('date', f"{date}T23:59:59Z")
        
        if league_id:
            if include_team_names:
                # fixture_details view doesn't have league_id directly
                league = self.client.table('leagues').select('code').eq('id', league_id).execute()
                if league.data:
                    query = query.eq('league_code', league.data[0]['code'])
            else:
                query = query.eq('league_id', league_id)
        
        result = query.execute()
        return result.data or []
    
    # === Team Season Stats ===
    
    def upsert_team_season_stats(self, stats_data: Dict) -> Dict:
        """Insert or update team season statistics."""
        result = self.client.table('team_season_stats').upsert(stats_data).execute()
        return result.data[0] if result.data else {}
    
    def get_team_season_stats(
        self, 
        team_id: int, 
        season: str,
        league_id: Optional[int] = None
    ) -> Optional[Dict]:
        """Get team's season statistics."""
        query = self.client.table('team_season_stats').select('*').eq('team_id', team_id).eq('season', season)
        
        if league_id:
            query = query.eq('league_id', league_id)
        
        result = query.execute()
        return result.data[0] if result.data else None
    
    # === Predictions ===
    
    def save_prediction(self, prediction_data: Dict) -> Dict:
        """Save a match prediction."""
        result = self.client.table('predictions').insert(prediction_data).execute()
        return result.data[0] if result.data else {}
    
    def get_predictions_by_fixture(self, fixture_id: int) -> List[Dict]:
        """Get all predictions for a fixture (different model versions)."""
        result = self.client.table('predictions').select('*').eq('fixture_id', fixture_id).order('created_at', desc=True).execute()
        return result.data or []
    
    def get_recent_predictions(self, limit: int = 100) -> List[Dict]:
        """Get recent predictions for analysis."""
        result = self.client.table('predictions').select('*').order('created_at', desc=True).limit(limit).execute()
        return result.data or []
    
    # === Utility Methods ===
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            total_result = self.client.table('api_cache').select('id', count='exact').execute()
            total_count = total_result.count or 0
            
            expired_count = self.client.table('api_cache').select('id', count='exact').lt(
                'expires_at', 
                datetime.utcnow().isoformat()
            ).execute().count or 0
            
            return {
                'total_entries': total_count,
                'expired_entries': expired_count,
                'active_entries': total_count - expired_count,
                'cache_hit_rate': 'Unknown'  # Would need to track hits/misses
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check database connection and basic functionality."""
        try:
            # Simple query to test connection
            result = self.client.table('leagues').select('id').limit(1).execute()
            
            return {
                'status': 'healthy',
                'connection': 'ok',
                'leagues_table': 'accessible',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Global database client instance
_db_client: Optional[DatabaseClient] = None


def get_database_client() -> DatabaseClient:
    """Get or create the global database client instance."""
    global _db_client
    
    if _db_client is None:
        _db_client = DatabaseClient()
    
    return _db_client


def close_database_client() -> None:
    """Close the global database client."""
    global _db_client
    _db_client = None  # Supabase client doesn't need explicit closing