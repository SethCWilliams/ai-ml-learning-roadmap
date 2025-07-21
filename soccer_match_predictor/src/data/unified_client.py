"""
Unified Data Client - Abstraction Layer for Soccer Data

This client provides a clean interface for soccer data that currently uses ESPN
but is designed to easily accommodate additional data sources in the future.

Current Data Sources:
- ESPN API: Match fixtures, team records, form strings, venues

Future Extensions (when budget/data allows):
- Advanced statistics providers
- Player injury data
- Weather data
- Betting odds

Design Principles:
- Single interface for all soccer data needs
- Extensible for multiple data sources
- Rich feature engineering from available data
- Caching for performance
- Error handling and fallbacks
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import time

from .espn_client import ESPNSoccerClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MatchInfo:
    """Structured match information."""
    match_id: str
    date: str
    league: str
    home_team: str
    away_team: str
    home_score: Optional[int]
    away_score: Optional[int]
    status: str
    venue: Optional[str]
    season: Optional[str]


@dataclass
class TeamStats:
    """Comprehensive team statistics."""
    team_name: str
    league: str
    
    # Basic record
    games_played: int
    wins: int
    draws: int
    losses: int
    points: int
    
    # Goal statistics
    goals_for: int
    goals_against: int
    goal_difference: int
    
    # Calculated metrics
    win_rate: float
    points_per_game: float
    goals_per_game: float
    goals_against_per_game: float
    
    # Form and momentum
    recent_form: str  # e.g., "WWDLW"
    form_points: int
    form_trend: str  # "Improving", "Declining", "Stable"
    
    # Home/Away (when available)
    home_record: Optional[str]
    away_record: Optional[str]
    
    # Metadata
    last_updated: str
    data_source: str


@dataclass
class PredictionFeatures:
    """Features engineered for ML prediction."""
    home_team: str
    away_team: str
    league: str
    venue: str
    
    # Team strength indicators
    home_team_strength: float
    away_team_strength: float
    strength_difference: float
    
    # Form indicators
    home_recent_form_points: int
    away_recent_form_points: int
    form_momentum_diff: float
    
    # Head-to-head (when available)
    h2h_home_wins: int
    h2h_away_wins: int
    h2h_draws: int
    
    # Context
    days_since_last_match_home: Optional[int]
    days_since_last_match_away: Optional[int]
    is_derby: bool
    venue_advantage: float


class UnifiedDataClient:
    """
    Unified interface for soccer data collection and feature engineering.
    
    Currently uses ESPN as the primary data source, but designed to easily
    accommodate additional sources as they become available.
    """
    
    def __init__(self, cache_duration_minutes: int = 30):
        """
        Initialize the unified data client.
        
        Args:
            cache_duration_minutes: How long to cache data to avoid redundant API calls
        """
        self.espn_client = ESPNSoccerClient()
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        
        # Data caches
        self._team_stats_cache: Dict[str, Tuple[TeamStats, datetime]] = {}
        self._match_cache: Dict[str, Tuple[List[MatchInfo], datetime]] = {}
        self._form_cache: Dict[str, Tuple[Dict[str, Any], datetime]] = {}
        
        # League mappings
        self.league_names = {
            'eng.1': 'Premier League',
            'usa.1': 'MLS'
        }
        
        logger.info("Unified Data Client initialized with ESPN as primary source")
    
    def get_matches_for_date(self, date: Optional[str] = None, 
                           league: Optional[str] = None) -> List[MatchInfo]:
        """
        Get matches for a specific date and league.
        
        Args:
            date: Date in YYYYMMDD format, or None for today
            league: League code ('eng.1', 'usa.1'), or None for all
            
        Returns:
            List of MatchInfo objects
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        
        leagues_to_check = [league] if league else ['eng.1', 'usa.1']
        all_matches = []
        
        for lg in leagues_to_check:
            cache_key = f"{lg}_{date}"
            
            # Check cache first
            if cache_key in self._match_cache:
                cached_matches, cached_time = self._match_cache[cache_key]
                if datetime.now() - cached_time < self.cache_duration:
                    logger.debug(f"Using cached match data for {lg} on {date}")
                    all_matches.extend(cached_matches)
                    continue
            
            # Fetch fresh data from ESPN
            logger.info(f"Fetching match data for {lg} on {date}")
            api_date = None if date == datetime.now().strftime("%Y%m%d") else date
            scoreboard = self.espn_client.get_scoreboard(lg, api_date)
            
            matches = []
            if scoreboard and scoreboard.get('events'):
                for event in scoreboard['events']:
                    match_info = self._parse_espn_match(event, lg)
                    if match_info:
                        matches.append(match_info)
            
            # Cache the results
            self._match_cache[cache_key] = (matches, datetime.now())
            all_matches.extend(matches)
        
        return all_matches
    
    def get_team_stats(self, team_name: str, league: str) -> Optional[TeamStats]:
        """
        Get comprehensive team statistics.
        
        Args:
            team_name: Name of the team
            league: League code ('eng.1', 'usa.1')
            
        Returns:
            TeamStats object or None if not found
        """
        cache_key = f"{team_name}_{league}"
        
        # Check cache first
        if cache_key in self._team_stats_cache:
            cached_stats, cached_time = self._team_stats_cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                logger.debug(f"Using cached team stats for {team_name}")
                return cached_stats
        
        # Find team in recent matches to get current data
        logger.info(f"Fetching team stats for {team_name} in {league}")
        
        # Get recent scoreboard data to find team
        scoreboard = self.espn_client.get_scoreboard(league)
        if not scoreboard or not scoreboard.get('events'):
            logger.warning(f"No recent matches found for league {league}")
            return None
        
        # Look for the team in recent events
        team_data = None
        for event in scoreboard['events']:
            if 'competitions' not in event:
                continue
            
            comp = event['competitions'][0]
            for competitor in comp.get('competitors', []):
                team = competitor['team']
                if team_name.lower() in team['displayName'].lower():
                    team_data = competitor
                    break
            
            if team_data:
                break
        
        if not team_data:
            logger.warning(f"Team {team_name} not found in recent {league} matches")
            return None
        
        # Parse team statistics
        stats = self._parse_espn_team_stats(team_data, league)
        
        # Cache the results
        if stats:
            self._team_stats_cache[cache_key] = (stats, datetime.now())
        
        return stats
    
    def get_prediction_features(self, home_team: str, away_team: str, 
                               league: str, match_date: Optional[str] = None) -> Optional[PredictionFeatures]:
        """
        Extract ML features for match prediction.
        
        Args:
            home_team: Home team name
            away_team: Away team name  
            league: League code
            match_date: Match date (for context), or None for current
            
        Returns:
            PredictionFeatures object ready for ML model
        """
        logger.info(f"Generating prediction features for {home_team} vs {away_team}")
        
        # Get team statistics
        home_stats = self.get_team_stats(home_team, league)
        away_stats = self.get_team_stats(away_team, league)
        
        if not home_stats or not away_stats:
            logger.error(f"Could not get stats for both teams")
            return None
        
        # Calculate team strength (goals difference + form)
        home_strength = self._calculate_team_strength(home_stats)
        away_strength = self._calculate_team_strength(away_stats)
        
        # Form momentum
        home_momentum = self._calculate_form_momentum(home_stats.recent_form)
        away_momentum = self._calculate_form_momentum(away_stats.recent_form)
        
        # Basic head-to-head (placeholder for future enhancement)
        h2h_data = self._get_head_to_head_basic(home_team, away_team, league)
        
        # Context features
        is_derby = self._is_derby_match(home_team, away_team, league)
        venue_advantage = self._calculate_venue_advantage(home_stats, away_stats)
        
        return PredictionFeatures(
            home_team=home_team,
            away_team=away_team,
            league=league,
            venue=f"{home_team} Stadium",  # Simplified for now
            
            # Strength indicators
            home_team_strength=home_strength,
            away_team_strength=away_strength,
            strength_difference=home_strength - away_strength,
            
            # Form indicators  
            home_recent_form_points=home_stats.form_points,
            away_recent_form_points=away_stats.form_points,
            form_momentum_diff=home_momentum - away_momentum,
            
            # Head-to-head
            h2h_home_wins=h2h_data['home_wins'],
            h2h_away_wins=h2h_data['away_wins'], 
            h2h_draws=h2h_data['draws'],
            
            # Context
            days_since_last_match_home=None,  # Future enhancement
            days_since_last_match_away=None,  # Future enhancement
            is_derby=is_derby,
            venue_advantage=venue_advantage
        )
    
    def _parse_espn_match(self, event: Dict[str, Any], league: str) -> Optional[MatchInfo]:
        """Parse ESPN event data into MatchInfo object."""
        try:
            if 'competitions' not in event:
                return None
            
            comp = event['competitions'][0]
            competitors = comp.get('competitors', [])
            
            if len(competitors) != 2:
                return None
            
            home_team = None
            away_team = None
            home_score = None
            away_score = None
            
            for competitor in competitors:
                team_name = competitor['team']['displayName']
                score = competitor.get('score')
                
                if competitor.get('homeAway') == 'home':
                    home_team = team_name
                    home_score = score
                else:
                    away_team = team_name
                    away_score = score
            
            return MatchInfo(
                match_id=event.get('id', ''),
                date=event.get('date', ''),
                league=league,
                home_team=home_team or '',
                away_team=away_team or '',
                home_score=home_score,
                away_score=away_score,
                status=event.get('status', {}).get('type', {}).get('name', 'Unknown'),
                venue=event.get('venue', {}).get('fullName'),
                season=event.get('season', {}).get('year')
            )
            
        except Exception as e:
            logger.error(f"Error parsing ESPN match data: {e}")
            return None
    
    def _parse_espn_team_stats(self, team_data: Dict[str, Any], league: str) -> Optional[TeamStats]:
        """Parse ESPN team data into TeamStats object."""
        try:
            team = team_data['team']
            team_name = team['displayName']
            
            # Parse record
            records = team_data.get('records', [])
            main_record = None
            for record in records:
                if 'All Splits' in record.get('name', ''):
                    main_record = record
                    break
            
            if not main_record:
                logger.warning(f"No main record found for {team_name}")
                return None
            
            summary = main_record.get('summary', '0-0-0')
            if '-' not in summary or summary.count('-') != 2:
                logger.warning(f"Invalid record format for {team_name}: {summary}")
                return None
            
            wins, draws, losses = map(int, summary.split('-'))
            games_played = wins + draws + losses
            points = (wins * 3) + draws
            
            # Parse form
            form = team_data.get('form', '')
            form_points = sum(3 if c == 'W' else 1 if c == 'D' else 0 for c in form)
            
            # Calculate trend
            recent_form = form[-5:] if len(form) >= 5 else form
            if len(recent_form) >= 3:
                recent_points = sum(3 if c == 'W' else 1 if c == 'D' else 0 for c in recent_form)
                recent_avg = recent_points / len(recent_form)
                
                if recent_avg >= 2.0:
                    trend = "Improving"
                elif recent_avg >= 1.5:
                    trend = "Stable"
                else:
                    trend = "Declining"
            else:
                trend = "Unknown"
            
            return TeamStats(
                team_name=team_name,
                league=league,
                games_played=games_played,
                wins=wins,
                draws=draws,
                losses=losses,
                points=points,
                goals_for=0,  # Not available in ESPN basic data
                goals_against=0,  # Not available in ESPN basic data
                goal_difference=0,  # Not available in ESPN basic data
                win_rate=wins / max(games_played, 1),
                points_per_game=points / max(games_played, 1),
                goals_per_game=0.0,  # Not available
                goals_against_per_game=0.0,  # Not available
                recent_form=form,
                form_points=form_points,
                form_trend=trend,
                home_record=None,  # Future enhancement
                away_record=None,  # Future enhancement
                last_updated=datetime.now().isoformat(),
                data_source="ESPN"
            )
            
        except Exception as e:
            logger.error(f"Error parsing ESPN team stats: {e}")
            return None
    
    def _calculate_team_strength(self, stats: TeamStats) -> float:
        """Calculate overall team strength from available stats."""
        # Weight: 70% win rate, 30% recent form
        win_rate_component = stats.win_rate * 0.7
        
        # Form component (0-3 scale normalized)
        max_form_points = len(stats.recent_form) * 3
        form_component = (stats.form_points / max(max_form_points, 1)) * 0.3
        
        return win_rate_component + form_component
    
    def _calculate_form_momentum(self, form: str) -> float:
        """Calculate form momentum (positive = improving, negative = declining)."""
        if len(form) < 3:
            return 0.0
        
        # Compare first half vs second half of form string
        mid_point = len(form) // 2
        first_half = form[:mid_point]
        second_half = form[mid_point:]
        
        first_avg = sum(3 if c == 'W' else 1 if c == 'D' else 0 for c in first_half) / len(first_half)
        second_avg = sum(3 if c == 'W' else 1 if c == 'D' else 0 for c in second_half) / len(second_half)
        
        return second_avg - first_avg
    
    def _get_head_to_head_basic(self, home_team: str, away_team: str, league: str) -> Dict[str, int]:
        """Basic head-to-head placeholder (future enhancement)."""
        # For now, return neutral H2H until we implement historical match lookup
        return {
            'home_wins': 0,
            'away_wins': 0,
            'draws': 0
        }
    
    def _is_derby_match(self, home_team: str, away_team: str, league: str) -> bool:
        """Detect if this is a derby/rivalry match."""
        # Simple city-based detection
        derby_pairs = {
            'eng.1': [
                ('Liverpool', 'Everton'),
                ('Manchester United', 'Manchester City'),
                ('Arsenal', 'Tottenham'),
                ('Chelsea', 'Arsenal'),
                ('Liverpool', 'Manchester United')
            ],
            'usa.1': [
                ('LA Galaxy', 'LAFC'),
                ('Seattle Sounders', 'Portland Timbers'),
                ('New York Red Bulls', 'New York City FC')
            ]
        }
        
        pairs = derby_pairs.get(league, [])
        for pair in pairs:
            if (home_team in pair[0] and away_team in pair[1]) or \
               (home_team in pair[1] and away_team in pair[0]):
                return True
        
        return False
    
    def _calculate_venue_advantage(self, home_stats: TeamStats, away_stats: TeamStats) -> float:
        """Calculate home venue advantage."""
        # Simple advantage based on home team strength vs away team strength
        # In the future, this could use actual home/away records
        return (home_stats.win_rate - away_stats.win_rate) * 0.1  # Small home advantage modifier
    
    def clear_cache(self):
        """Clear all cached data to force fresh API calls."""
        self._team_stats_cache.clear()
        self._match_cache.clear()
        self._form_cache.clear()
        logger.info("All caches cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about current cache state."""
        return {
            'team_stats_cached': len(self._team_stats_cache),
            'matches_cached': len(self._match_cache),
            'form_data_cached': len(self._form_cache),
            'cache_duration_minutes': self.cache_duration.total_seconds() / 60
        }