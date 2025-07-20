"""
ESPN API Client for Soccer Match Predictor

This module provides a client for accessing ESPN's free soccer API to retrieve:
- Match results and fixtures (scoreboard endpoint)
- League standings and team records (standings endpoint)
- Basic team information and form data

ML Learning Focus: This demonstrates real-world API integration and rate limiting
strategies essential for production ML systems.
"""

import requests
import time
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ESPNSoccerClient:
    """
    ESPN Soccer API client with rate limiting and caching support.
    
    The ESPN API provides free access to soccer data without authentication.
    We implement respectful rate limiting and caching to avoid overloading
    their servers while maintaining data freshness for ML training.
    
    Supported Leagues:
    - Premier League: 'eng.1'
    - MLS: 'usa.1'
    """
    
    BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/soccer"
    
    # Rate limiting: ~1 request per second to be respectful
    RATE_LIMIT_DELAY = 1.0
    
    def __init__(self, rate_limit_delay: float = RATE_LIMIT_DELAY):
        """
        Initialize ESPN Soccer API client.
        
        Args:
            rate_limit_delay: Seconds to wait between API requests
        """
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.session = requests.Session()
        
        # Set a descriptive User-Agent for ethical scraping
        self.session.headers.update({
            'User-Agent': 'Soccer-ML-Learning-Project/1.0 (Educational Purpose)'
        })
    
    def _rate_limit(self):
        """Implement rate limiting to be respectful to ESPN's servers."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """
        Make a rate-limited request to ESPN API.
        
        Args:
            endpoint: API endpoint URL
            
        Returns:
            JSON response data or None if request failed
        """
        self._rate_limit()
        
        try:
            logger.info(f"Requesting: {endpoint}")
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
    
    def get_team_records_from_scoreboard(self, league: str) -> List[Dict]:
        """
        Extract team records from scoreboard data since standings endpoint is empty.
        
        This provides team strength features by extracting records from match data:
        - Team records (W/L/D)
        - Recent form
        - Team identifiers
        
        Args:
            league: League identifier ('eng.1' for Premier League, 'usa.1' for MLS)
            
        Returns:
            List of team record dictionaries
        """
        scoreboard = self.get_scoreboard(league)
        teams_data = []
        
        if not scoreboard or 'events' not in scoreboard:
            return teams_data
        
        for event in scoreboard['events']:
            try:
                competition = event['competitions'][0]
                competitors = competition['competitors']
                
                for competitor in competitors:
                    team_info = {
                        'team_id': competitor['team']['id'],
                        'team_name': competitor['team']['displayName'],
                        'abbreviation': competitor['team']['abbreviation'],
                        'records': competitor.get('records', []),
                        'form': competitor.get('form', ''),
                        'home_away': competitor.get('homeAway'),
                        'score': competitor.get('score', 0)
                    }
                    teams_data.append(team_info)
                    
            except (KeyError, IndexError) as e:
                logger.warning(f"Failed to extract team data: {e}")
                continue
        
        return teams_data
    
    def get_scoreboard(self, league: str, date: Optional[str] = None) -> Optional[Dict]:
        """
        Get match results and fixtures for a specific date or current matchday.
        
        This provides form calculation data:
        - Recent match results
        - Home/away performance
        - Goal scoring patterns
        - Match dates for temporal features
        
        Args:
            league: League identifier
            date: Optional date in YYYY-MM-DD format (defaults to current)
            
        Returns:
            Dictionary containing match data or None if failed
        """
        endpoint = f"{self.BASE_URL}/{league}/scoreboard"
        
        if date:
            endpoint += f"?dates={date}"
            
        return self._make_request(endpoint)
    
    def get_recent_results(self, league: str, days_back: int = 30) -> List[Dict]:
        """
        Get recent match results for form calculation.
        
        ML Learning Point: This demonstrates how to collect temporal data
        for time-series features like current form and momentum.
        
        Args:
            league: League identifier
            days_back: Number of days of history to collect
            
        Returns:
            List of match results
        """
        results = []
        
        # Get results from the last N days
        for i in range(days_back):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            scoreboard = self.get_scoreboard(league, date)
            
            if scoreboard and 'events' in scoreboard:
                for event in scoreboard['events']:
                    # Only include completed matches
                    if event.get('status', {}).get('type', {}).get('name') == 'STATUS_FINAL':
                        results.append(self._extract_match_data(event))
        
        return results
    
    def _extract_match_data(self, event: Dict) -> Dict:
        """
        Extract structured match data from ESPN API response.
        
        This transforms the raw API response into clean data suitable
        for feature engineering.
        
        Args:
            event: Raw match event from ESPN API
            
        Returns:
            Cleaned match data dictionary
        """
        try:
            competition = event['competitions'][0]
            competitors = competition['competitors']
            
            # Find home and away teams
            home_team = next(c for c in competitors if c['homeAway'] == 'home')
            away_team = next(c for c in competitors if c['homeAway'] == 'away')
            
            return {
                'match_id': event['id'],
                'date': event['date'],
                'home_team': {
                    'name': home_team['team']['displayName'],
                    'abbreviation': home_team['team']['abbreviation'],
                    'id': home_team['team']['id'],
                    'score': int(home_team.get('score', 0))
                },
                'away_team': {
                    'name': away_team['team']['displayName'],
                    'abbreviation': away_team['team']['abbreviation'],
                    'id': away_team['team']['id'],
                    'score': int(away_team.get('score', 0))
                },
                'status': event.get('status', {}).get('type', {}).get('name'),
                'venue': competition.get('venue', {}).get('fullName'),
                'attendance': competition.get('attendance')
            }
            
        except (KeyError, IndexError, ValueError) as e:
            logger.warning(f"Failed to extract match data: {e}")
            return {}
    
    def get_team_form(self, league: str, team_id: str, num_games: int = 5) -> Dict:
        """
        Calculate team form from recent matches.
        
        ML Learning Point: This shows how to engineer temporal features
        from raw match data - a crucial skill for sports prediction models.
        
        Args:
            league: League identifier
            team_id: ESPN team ID
            num_games: Number of recent games to analyze
            
        Returns:
            Dictionary with form metrics
        """
        recent_results = self.get_recent_results(league, days_back=60)
        team_matches = []
        
        # Filter matches involving this team
        for match in recent_results:
            if (match.get('home_team', {}).get('id') == team_id or 
                match.get('away_team', {}).get('id') == team_id):
                team_matches.append(match)
        
        # Sort by date and take most recent
        team_matches.sort(key=lambda x: x['date'], reverse=True)
        recent_matches = team_matches[:num_games]
        
        if not recent_matches:
            return {'points': 0, 'goals_for': 0, 'goals_against': 0, 'matches': 0}
        
        # Calculate form metrics
        points = 0
        goals_for = 0
        goals_against = 0
        
        for match in recent_matches:
            home_team = match['home_team']
            away_team = match['away_team']
            
            if home_team['id'] == team_id:
                # Team played at home
                goals_for += home_team['score']
                goals_against += away_team['score']
                
                if home_team['score'] > away_team['score']:
                    points += 3  # Win
                elif home_team['score'] == away_team['score']:
                    points += 1  # Draw
                    
            else:
                # Team played away
                goals_for += away_team['score']
                goals_against += home_team['score']
                
                if away_team['score'] > home_team['score']:
                    points += 3  # Win
                elif away_team['score'] == home_team['score']:
                    points += 1  # Draw
        
        return {
            'points': points,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'matches': len(recent_matches),
            'points_per_game': points / len(recent_matches) if recent_matches else 0,
            'goals_for_per_game': goals_for / len(recent_matches) if recent_matches else 0,
            'goals_against_per_game': goals_against / len(recent_matches) if recent_matches else 0
        }


# Example usage and testing functions
def test_api_connection():
    """Test basic API connectivity and data structure."""
    client = ESPNSoccerClient()
    
    print("Testing ESPN API connection...")
    
    # Test Premier League team records from scoreboard
    prem_teams = client.get_team_records_from_scoreboard('eng.1')
    if prem_teams:
        print("✅ Premier League team data retrieved successfully")
        print(f"Found {len(prem_teams)} team records")
        if prem_teams:
            sample_team = prem_teams[0]
            print(f"Sample team: {sample_team['team_name']} (ID: {sample_team['team_id']})")
            print(f"Records available: {len(sample_team.get('records', []))}")
            print(f"Form: {sample_team.get('form', 'N/A')}")
    else:
        print("❌ Failed to get Premier League team data")
    
    # Test MLS team records
    mls_teams = client.get_team_records_from_scoreboard('usa.1')
    if mls_teams:
        print("✅ MLS team data retrieved successfully")
        print(f"Found {len(mls_teams)} team records")
    else:
        print("❌ Failed to get MLS team data")
    
    # Test scoreboard
    prem_scoreboard = client.get_scoreboard('eng.1')
    if prem_scoreboard:
        print("✅ Premier League scoreboard retrieved successfully")
        print(f"Found {len(prem_scoreboard.get('events', []))} matches")
    else:
        print("❌ Failed to get Premier League scoreboard")
    
    # Test form calculation
    if prem_teams:
        sample_team_id = prem_teams[0]['team_id']
        team_form = client.get_team_form('eng.1', sample_team_id)
        print(f"✅ Form calculation test: {team_form}")


if __name__ == "__main__":
    test_api_connection()