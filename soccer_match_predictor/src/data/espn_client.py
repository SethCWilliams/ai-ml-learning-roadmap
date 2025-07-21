"""ESPN API client for soccer data collection."""

import time
import requests
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ESPNSoccerClient:
    """Client for accessing ESPN Soccer API data."""
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer"
    RATE_LIMIT_DELAY = 1.0  # seconds between requests
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self._last_request_time = 0
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make rate-limited request to ESPN API."""
        self._rate_limit()
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"ESPN API request failed: {e}")
            raise
    
    def get_fixtures_by_date(self, date: str, league: str = "eng.1") -> List[Dict[str, Any]]:
        """
        Get soccer fixtures for a specific date.
        
        Args:
            date: Date in YYYYMMDD format (e.g., "20240721")
            league: League code (default: "eng.1" for Premier League)
                   Other options: "usa.1" for MLS
        
        Returns:
            List of fixture dictionaries with match details
        """
        url = f"{self.BASE_URL}/{league}/scoreboard"
        params = {"dates": date}
        
        logger.info(f"Getting fixtures for {date} in league {league}")
        data = self._make_request(url, params)
        
        fixtures = []
        events = data.get("events", [])
        
        for event in events:
            try:
                fixture = self._parse_fixture(event)
                fixtures.append(fixture)
            except Exception as e:
                logger.error(f"Failed to parse event {event.get('id', 'unknown')}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                continue
        
        logger.info(f"Found {len(fixtures)} fixtures for {date}")
        return fixtures
    
    def _parse_fixture(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse ESPN event data into standardized fixture format."""
        competitions = event.get("competitions", [{}])
        competition = competitions[0] if competitions else {}
        competitors = competition.get("competitors", [])
        
        home_team = None
        away_team = None
        
        for competitor in competitors:
            if competitor.get("homeAway") == "home":
                home_team = competitor
            elif competitor.get("homeAway") == "away":
                away_team = competitor
        
        return {
            "id": event.get("id"),
            "date": event.get("date"),
            "status": competition.get("status", {}).get("type", {}).get("name"),
            "home_team": {
                "id": home_team.get("id") if home_team else None,
                "name": home_team.get("team", {}).get("displayName") if home_team else None,
                "abbreviation": home_team.get("team", {}).get("abbreviation") if home_team else None,
                "score": home_team.get("score") if home_team else None,
            },
            "away_team": {
                "id": away_team.get("id") if away_team else None,
                "name": away_team.get("team", {}).get("displayName") if away_team else None,
                "abbreviation": away_team.get("team", {}).get("abbreviation") if away_team else None,
                "score": away_team.get("score") if away_team else None,
            },
            "venue": competition.get("venue", {}).get("fullName"),
            "league": event.get("season", {}).get("slug", ""),
        }
    
    def get_team_season_stats(self, team_id: str, league: str = "eng.1") -> Dict[str, Any]:
        """
        Get team's season statistics.
        
        Args:
            team_id: ESPN team ID
            league: League code
        
        Returns:
            Dictionary with team season stats
        """
        url = f"{self.BASE_URL}/{league}/teams/{team_id}"
        
        logger.info(f"Getting season stats for team {team_id}")
        data = self._make_request(url)
        
        team_data = data.get("team", {})
        record = team_data.get("record", {}).get("items", [{}])[0] if team_data.get("record", {}).get("items") else {}
        
        return {
            "team_id": team_id,
            "name": team_data.get("displayName"),
            "wins": record.get("stats", [{}])[0].get("value") if record.get("stats") and len(record.get("stats", [])) > 0 else 0,
            "losses": record.get("stats", [{}])[1].get("value") if record.get("stats") and len(record.get("stats", [])) > 1 else 0,
            "draws": record.get("stats", [{}])[2].get("value") if record.get("stats") and len(record.get("stats", [])) > 2 else 0,
            "goals_for": record.get("stats", [{}])[3].get("value") if record.get("stats") and len(record.get("stats", [])) > 3 else 0,
            "goals_against": record.get("stats", [{}])[4].get("value") if record.get("stats") and len(record.get("stats", [])) > 4 else 0,
            "points": record.get("stats", [{}])[5].get("value") if record.get("stats") and len(record.get("stats", [])) > 5 else 0,
        }
    
    def get_team_recent_form(self, team_id: str, league: str = "eng.1", games: int = 5) -> List[Dict[str, Any]]:
        """
        Get team's recent match results for form analysis using team schedule endpoint.
        
        Args:
            team_id: ESPN team ID
            league: League code
            games: Number of recent games to retrieve (default: 5)
        
        Returns:
            List of recent match results with performance data
        """
        logger.info(f"Getting recent form for team {team_id} from schedule")
        
        try:
            # Get team's full season schedule (much more efficient than date searching)
            url = f"{self.BASE_URL}/{league}/teams/{team_id}/schedule"
            schedule_data = self._make_request(url)
            
            events = schedule_data.get('events', [])
            recent_matches = []
            
            # Process events in chronological order (most recent first)
            for event in events:
                # Only process completed matches with scores
                if not self._is_match_completed(event):
                    continue
                
                # Extract match details
                match_result = self._extract_team_result_from_schedule(event, team_id)
                if match_result:
                    recent_matches.append(match_result)
                    
                    # Stop when we have enough recent matches
                    if len(recent_matches) >= games:
                        break
            
            logger.info(f"Found {len(recent_matches)} recent completed matches for team {team_id}")
            return recent_matches
            
        except Exception as e:
            logger.error(f"Failed to get team schedule for {team_id}: {e}")
            return []
    
    def _is_match_completed(self, event: Dict[str, Any]) -> bool:
        """Check if a match is completed and has scores."""
        competitions = event.get('competitions', [])
        if not competitions:
            return False
        
        competition = competitions[0]
        competitors = competition.get('competitors', [])
        
        # Check if both teams have scores
        if len(competitors) != 2:
            return False
        
        for competitor in competitors:
            score = competitor.get('score')
            if not score or not isinstance(score, dict) or 'value' not in score:
                return False
        
        return True
    
    def _extract_team_result_from_schedule(self, event: Dict[str, Any], team_id: str) -> Dict[str, Any]:
        """Extract team's result from a schedule event."""
        competitions = event.get('competitions', [])
        if not competitions:
            return None
        
        competition = competitions[0]
        competitors = competition.get('competitors', [])
        
        # Find this team and opponent
        team_competitor = None
        opponent_competitor = None
        
        for competitor in competitors:
            if str(competitor.get('id')) == str(team_id):
                team_competitor = competitor
            else:
                opponent_competitor = competitor
        
        if not team_competitor or not opponent_competitor:
            return None
        
        # Extract scores
        team_score = int(team_competitor.get('score', {}).get('value', 0))
        opponent_score = int(opponent_competitor.get('score', {}).get('value', 0))
        
        # Determine result
        if team_score > opponent_score:
            result = "W"
            points = 3
        elif team_score < opponent_score:
            result = "L"
            points = 0
        else:
            result = "D"
            points = 1
        
        # Extract additional details
        opponent_team = opponent_competitor.get('team', {})
        venue = competition.get('venue', {}).get('fullName', 'Unknown Venue')
        is_home = team_competitor.get('homeAway') == 'home'
        
        return {
            "date": event.get('date', ''),
            "opponent": opponent_team.get('displayName', 'Unknown'),
            "home_away": "H" if is_home else "A",
            "result": result,
            "score": f"{team_score}-{opponent_score}",
            "goals_for": team_score,
            "goals_against": opponent_score,
            "points": points,
            "venue": venue,
        }
    
    def _analyze_team_performance(self, fixture: Dict[str, Any], team_id: str) -> Dict[str, Any]:
        """Analyze team's performance in a specific match."""
        # Convert team_id to string for comparison (ESPN returns string IDs)
        team_id_str = str(team_id)
        home_id_str = str(fixture["home_team"]["id"]) if fixture["home_team"]["id"] else None
        
        is_home = home_id_str == team_id_str
        team_info = fixture["home_team"] if is_home else fixture["away_team"]
        opponent_info = fixture["away_team"] if is_home else fixture["home_team"]
        
        team_score = int(team_info["score"]) if team_info["score"] else 0
        opponent_score = int(opponent_info["score"]) if opponent_info["score"] else 0
        
        # Determine result
        if team_score > opponent_score:
            result = "W"
            points = 3
        elif team_score < opponent_score:
            result = "L"
            points = 0
        else:
            result = "D"
            points = 1
        
        return {
            "date": fixture["date"],
            "opponent": opponent_info["name"],
            "home_away": "H" if is_home else "A",
            "result": result,
            "score": f"{team_score}-{opponent_score}",
            "goals_for": team_score,
            "goals_against": opponent_score,
            "points": points,
            "venue": fixture["venue"],
        }