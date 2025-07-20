#!/usr/bin/env python3
"""
API-Football.com Test Script

Tests API-Football.com endpoints to evaluate if it can replace our ESPN + FBref approach
with a unified data source for both Premier League and MLS.

Usage:
    python test_api_football.py

Note: You'll need to get a free API key from api-football.com
Set the API key in your .env file as: API_FOOTBALL_KEY=your_key_here
"""

import requests
import time
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APIFootballTester:
    """Test client for API-Football.com to evaluate data quality and coverage."""
    
    BASE_URL = "https://v3.football.api-sports.io"
    
    # League IDs for our target leagues (from API-Football documentation)
    LEAGUES = {
        'premier_league': 39,   # England Premier League
        'mls': 253             # USA MLS  
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize API-Football tester.
        
        Args:
            api_key: API-Football.com API key (or get from environment)
        """
        self.api_key = api_key or os.getenv('API_FOOTBALL_KEY')
        if not self.api_key:
            raise ValueError("API_FOOTBALL_KEY not found in environment or parameters")
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io'
        })
        
        # Track API usage
        self.requests_made = 0
        self.rate_limit_delay = 1.0  # 1 second between requests
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make rate-limited request to API-Football."""
        time.sleep(self.rate_limit_delay)
        
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            print(f"🔍 Request #{self.requests_made + 1}: {endpoint}")
            
            response = self.session.get(url, params=params or {})
            response.raise_for_status()
            
            self.requests_made += 1
            data = response.json()
            
            # Check API response status
            if 'response' in data:
                print(f"✅ Success: {len(data['response'])} results")
                return data['response']
            else:
                print(f"❌ No 'response' field in data: {list(data.keys())}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def test_leagues_coverage(self):
        """Test if Premier League and MLS are available using known league IDs."""
        print("\n" + "="*60)
        print("🏆 TESTING LEAGUE COVERAGE")
        print("="*60)
        
        found_leagues = {}
        
        # Test each league by ID
        for league_key, league_id in self.LEAGUES.items():
            print(f"\n🔍 Testing {league_key} (ID: {league_id})...")
            
            # Get league info to verify it exists
            leagues_data = self._make_request("leagues", {"id": league_id})
            
            if leagues_data and len(leagues_data) > 0:
                league_info = leagues_data[0]
                league = league_info.get('league', {})
                country = league_info.get('country', {})
                
                found_leagues[league_key] = {
                    'id': league_id,
                    'name': league.get('name', 'Unknown'),
                    'country': country.get('name', 'Unknown')
                }
                
                print(f"✅ {league_key.upper()}: {league.get('name')} ({country.get('name')})")
            else:
                print(f"❌ {league_key.upper()}: League ID {league_id} not found")
        
        return found_leagues
    
    def test_team_data(self, league_id: int, league_name: str):
        """Test team data quality for a specific league."""
        print(f"\n📊 TESTING TEAM DATA - {league_name}")
        print("-" * 40)
        
        # First, check what seasons are available
        seasons_to_try = [2024, 2023, 2025]  # Try multiple seasons
        teams_data = None
        working_season = None
        
        for season in seasons_to_try:
            print(f"   Trying season {season}...")
            teams_data = self._make_request("teams", {
                "league": league_id,
                "season": season
            })
            
            if teams_data and len(teams_data) > 0:
                working_season = season
                print(f"   ✅ Found data for season {season}")
                break
            else:
                print(f"   ❌ No data for season {season}")
        
        if not teams_data:
            print(f"❌ No team data found for league {league_id} in any tested season")
            return
        
        print(f"🏟️  Found {len(teams_data)} teams for season {working_season}")
        
        # Show sample team data
        if teams_data:
            sample_team = teams_data[0]
            team = sample_team.get('team', {})
            venue = sample_team.get('venue', {})
            
            print(f"\n📋 Sample Team: {team.get('name', 'Unknown')}")
            print(f"   Founded: {team.get('founded', 'Unknown')}")
            print(f"   Country: {team.get('country', 'Unknown')}")
            print(f"   Venue: {venue.get('name', 'Unknown')} (capacity: {venue.get('capacity', 'Unknown')})")
            
            # Show available fields
            print(f"   Team fields: {list(team.keys())}")
            print(f"   Venue fields: {list(venue.keys())}")
        
        return working_season  # Return the working season for other tests
    
    def test_match_data(self, league_id: int, league_name: str, season: int):
        """Test match data and statistics."""
        print(f"\n⚽ TESTING MATCH DATA - {league_name}")
        print("-" * 40)
        
        # Get recent fixtures
        fixtures_data = self._make_request("fixtures", {
            "league": league_id,
            "season": season,
            "last": 5  # Last 5 matches
        })
        
        if not fixtures_data:
            print(f"❌ No fixture data for league {league_id}")
            return
        
        print(f"🗓️  Found {len(fixtures_data)} recent matches")
        
        if fixtures_data:
            sample_match = fixtures_data[0]
            fixture = sample_match.get('fixture', {})
            teams = sample_match.get('teams', {})
            goals = sample_match.get('goals', {})
            
            print(f"\n📋 Sample Match:")
            print(f"   Date: {fixture.get('date', 'Unknown')}")
            print(f"   Status: {fixture.get('status', {}).get('long', 'Unknown')}")
            print(f"   Teams: {teams.get('home', {}).get('name', 'Unknown')} vs {teams.get('away', {}).get('name', 'Unknown')}")
            print(f"   Score: {goals.get('home', 'Unknown')} - {goals.get('away', 'Unknown')}")
            
            # Show available fields
            print(f"   Available fixture fields: {list(sample_match.keys())}")
            
            # Try to get detailed statistics for this match
            fixture_id = fixture.get('id')
            if fixture_id:
                stats_data = self._make_request("fixtures/statistics", {
                    "fixture": fixture_id
                })
                
                if stats_data:
                    print(f"📊 Match statistics available! {len(stats_data)} team stats")
                    if stats_data:
                        sample_stats = stats_data[0]
                        team_name = sample_stats.get('team', {}).get('name', 'Unknown')
                        statistics = sample_stats.get('statistics', [])
                        print(f"   {team_name} stats categories: {len(statistics)}")
                        
                        # Show first few stat types
                        for stat in statistics[:5]:
                            stat_type = stat.get('type', 'Unknown')
                            stat_value = stat.get('value', 'Unknown')
                            print(f"     {stat_type}: {stat_value}")
                else:
                    print("❌ No detailed match statistics available")
    
    def test_standings_data(self, league_id: int, league_name: str, season: int):
        """Test league standings data."""
        print(f"\n🏆 TESTING STANDINGS DATA - {league_name}")
        print("-" * 40)
        
        standings_data = self._make_request("standings", {
            "league": league_id,
            "season": season
        })
        
        if not standings_data:
            print(f"❌ No standings data for league {league_id}")
            return
        
        if standings_data:
            league_standings = standings_data[0]
            standings = league_standings.get('league', {}).get('standings', [])
            
            if standings and len(standings) > 0:
                teams = standings[0]  # Main standings table
                print(f"📊 Standings available: {len(teams)} teams")
                
                if teams:
                    sample_team = teams[0]
                    team_info = sample_team.get('team', {})
                    stats = {k: v for k, v in sample_team.items() if k != 'team'}
                    
                    print(f"📋 Sample team: {team_info.get('name', 'Unknown')}")
                    print(f"   Available stats: {list(stats.keys())}")
                    
                    # Show key stats
                    if 'all' in stats:
                        all_stats = stats['all']
                        print(f"   Overall record: {all_stats.get('played', 0)}P {all_stats.get('win', 0)}W {all_stats.get('draw', 0)}D {all_stats.get('lose', 0)}L")
                        print(f"   Goals: {all_stats.get('goals', {}).get('for', 0)} for, {all_stats.get('goals', {}).get('against', 0)} against")
            else:
                print("❌ No standings data found")
    
    def run_comprehensive_test(self):
        """Run comprehensive test of API-Football capabilities."""
        print("🚀 API-FOOTBALL.COM COMPREHENSIVE TEST")
        print("=" * 60)
        print(f"API Key configured: {'✅' if self.api_key else '❌'}")
        print(f"Rate limit: {self.rate_limit_delay}s between requests")
        
        # Test 1: League coverage
        found_leagues = self.test_leagues_coverage()
        
        # Test 2-4: For each found league, test data types
        for league_key, league_info in (found_leagues or {}).items():
            league_id = league_info['id']
            league_name = league_info['name']
            
            working_season = self.test_team_data(league_id, league_name)
            if working_season:
                self.test_match_data(league_id, league_name, working_season)
                self.test_standings_data(league_id, league_name, working_season)
            else:
                print(f"⏭️  Skipping match and standings tests for {league_name} (no working season found)")
        
        # Final summary
        print(f"\n🏁 TEST COMPLETE")
        print("=" * 60)
        print(f"Total API requests made: {self.requests_made}")
        print(f"Free tier remaining today: ~{100 - self.requests_made}")
        
        if self.requests_made < 20:
            print("✅ Efficient API usage - plenty of requests left for development")
        elif self.requests_made < 50:
            print("⚠️  Moderate API usage - be mindful of daily limits")
        else:
            print("🚨 High API usage - consider upgrading for development")

def main():
    """Main test function."""
    try:
        # Initialize tester
        tester = APIFootballTester()
        
        # Run comprehensive test
        tester.run_comprehensive_test()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Sign up for free at api-football.com")
        print("2. Get your API key from the dashboard") 
        print("3. Add to .env file: API_FOOTBALL_KEY=your_key_here")
        print("4. Run this script again")
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()