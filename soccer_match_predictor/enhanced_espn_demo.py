#!/usr/bin/env python3
"""
Enhanced ESPN API Demo

Demonstrates the most valuable ESPN endpoints discovered and shows how they
can enhance our soccer match predictor with player statistics and team data.
"""

import requests
import time
from typing import Dict, List, Optional
from collections import defaultdict
import json

class EnhancedESPNClient:
    """Enhanced ESPN client demonstrating newly discovered valuable endpoints."""
    
    BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/soccer"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Soccer-ML-Learning-Project/1.0 (Educational Purpose)'
        })
    
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make rate-limited request."""
        try:
            print(f"📡 Fetching: {endpoint}")
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            time.sleep(1)  # Rate limiting
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_team_metadata(self, league: str) -> List[Dict]:
        """
        Get comprehensive team metadata including venues, colors, logos.
        Works for both Premier League (eng.1) and MLS (usa.1).
        """
        endpoint = f"{self.BASE_URL}/{league}/teams"
        data = self._make_request(endpoint)
        
        if not data or 'sports' not in data:
            return []
        
        teams = []
        try:
            sport = data['sports'][0]
            league_data = sport['leagues'][0]
            team_list = league_data.get('teams', [])
            
            for team_data in team_list:
                team = team_data['team']
                teams.append({
                    'id': team['id'],
                    'name': team['displayName'],
                    'abbreviation': team['abbreviation'],
                    'color': team.get('color'),
                    'venue': team.get('venue', {}).get('fullName'),
                    'city': team.get('venue', {}).get('address', {}).get('city'),
                    'logos': team.get('logos', [])
                })
        except (KeyError, IndexError) as e:
            print(f"⚠️  Error parsing team data: {e}")
        
        return teams
    
    def get_player_statistics(self, league: str = 'usa.1') -> Dict:
        """
        Get detailed player statistics. Currently only works reliably for MLS.
        
        Returns goals and assists leaders with team affiliations and performance metrics.
        This is the most valuable new endpoint discovered.
        """
        if league != 'usa.1':
            print(f"⚠️  Player statistics only available for MLS (usa.1), not {league}")
            return {}
        
        endpoint = f"{self.BASE_URL}/{league}/statistics"
        data = self._make_request(endpoint)
        
        if not data or 'stats' not in data:
            return {}
        
        result = {
            'season': data.get('season', {}),
            'timestamp': data.get('timestamp'),
            'goals_leaders': [],
            'assists_leaders': []
        }
        
        for stat_category in data['stats']:
            category_name = stat_category.get('name', '')
            
            if 'goals' in category_name.lower():
                result['goals_leaders'] = self._parse_player_leaders(stat_category)
            elif 'assists' in category_name.lower():
                result['assists_leaders'] = self._parse_player_leaders(stat_category)
        
        return result
    
    def _parse_player_leaders(self, stat_category: Dict) -> List[Dict]:
        """Parse player leader data from statistics endpoint."""
        players = []
        
        # The leaders array contains individual player objects directly
        leaders = stat_category.get('leaders', [])
        for athlete_data in leaders:
            if 'athlete' not in athlete_data:
                continue
            
            athlete = athlete_data['athlete']
            team_data = athlete.get('team', {})
            
            # Parse the shortDisplayValue: "M: 24, G: 18: A: 4"
            display_value = athlete_data.get('shortDisplayValue', '')
            matches, goals, assists = self._parse_display_value(display_value)
            
            players.append({
                'player_id': athlete['id'],
                'name': athlete['displayName'],
                'team_id': team_data.get('id'),
                'team_name': team_data.get('displayName'),
                'team_abbreviation': team_data.get('abbreviation'),
                'stat_value': athlete_data.get('value', 0),  # Primary stat (goals or assists)
                'matches_played': matches,
                'goals': goals,
                'assists': assists,
                'jersey_number': athlete.get('jersey')
            })
        
        return players
    
    def _parse_display_value(self, display_value: str) -> tuple:
        """Parse 'M: 24, G: 18: A: 4' format into separate values."""
        matches = goals = assists = 0
        
        try:
            # Handle format like "M: 24, G: 11: A: 14" where the second part contains both G and A
            import re
            
            # Extract matches (always in first part)
            match_pattern = r'M:\s*(\d+)'
            match_match = re.search(match_pattern, display_value)
            if match_match:
                matches = int(match_match.group(1))
            
            # Extract goals
            goals_pattern = r'G:\s*(\d+)'
            goals_match = re.search(goals_pattern, display_value)
            if goals_match:
                goals = int(goals_match.group(1))
            
            # Extract assists
            assists_pattern = r'A:\s*(\d+)'
            assists_match = re.search(assists_pattern, display_value)
            if assists_match:
                assists = int(assists_match.group(1))
                
        except (ValueError, IndexError):
            pass  # Keep defaults of 0
        
        return matches, goals, assists
    
    def calculate_team_offensive_stats(self, league: str = 'usa.1') -> Dict:
        """
        Calculate team-level offensive statistics from individual player data.
        This demonstrates how to create ML features from the player statistics.
        """
        player_stats = self.get_player_statistics(league)
        
        if not player_stats:
            return {}
        
        team_stats = defaultdict(lambda: {
            'total_goals': 0,
            'total_assists': 0,
            'active_scorers': 0,
            'active_assisters': 0,
            'top_scorer_goals': 0,
            'top_assister_assists': 0,
            'squad_depth_goals': 0,  # Number of players with goals
            'squad_depth_assists': 0  # Number of players with assists
        })
        
        # Process goals leaders
        for player in player_stats.get('goals_leaders', []):
            team_id = player['team_id']
            if not team_id:
                continue
            
            goals = player['goals']
            team_stats[team_id]['total_goals'] += goals
            if goals > 0:
                team_stats[team_id]['active_scorers'] += 1
                team_stats[team_id]['squad_depth_goals'] += 1
            
            team_stats[team_id]['top_scorer_goals'] = max(
                team_stats[team_id]['top_scorer_goals'], goals
            )
        
        # Process assists leaders  
        for player in player_stats.get('assists_leaders', []):
            team_id = player['team_id']
            if not team_id:
                continue
            
            assists = player['assists']
            team_stats[team_id]['total_assists'] += assists
            if assists > 0:
                team_stats[team_id]['active_assisters'] += 1
                team_stats[team_id]['squad_depth_assists'] += 1
            
            team_stats[team_id]['top_assister_assists'] = max(
                team_stats[team_id]['top_assister_assists'], assists
            )
        
        # Calculate derived metrics
        for team_id, stats in team_stats.items():
            # Goal concentration - how dependent on top scorer
            if stats['total_goals'] > 0:
                stats['top_scorer_dependency'] = stats['top_scorer_goals'] / stats['total_goals']
            else:
                stats['top_scorer_dependency'] = 0
            
            # Assist concentration
            if stats['total_assists'] > 0:
                stats['top_assister_dependency'] = stats['top_assister_assists'] / stats['total_assists']
            else:
                stats['top_assister_dependency'] = 0
        
        return dict(team_stats)


def demo_enhanced_espn_features():
    """Demonstrate the enhanced ESPN API features for ML."""
    client = EnhancedESPNClient()
    
    print("🚀 Enhanced ESPN API Demo")
    print("=" * 60)
    
    # Demo 1: Team Metadata (works for both leagues)
    print("\n📋 Demo 1: Team Metadata")
    print("-" * 30)
    
    for league, name in [('eng.1', 'Premier League'), ('usa.1', 'MLS')]:
        print(f"\n{name} Teams:")
        teams = client.get_team_metadata(league)
        
        if teams:
            print(f"Found {len(teams)} teams")
            sample_team = teams[0]
            print(f"Sample: {sample_team['name']} ({sample_team['abbreviation']})")
            print(f"  Venue: {sample_team['venue']}")
            print(f"  City: {sample_team['city']}")
            print(f"  Color: #{sample_team['color']}")
        else:
            print("No team data available")
    
    # Demo 2: Player Statistics (MLS only)
    print("\n\n📊 Demo 2: MLS Player Statistics")
    print("-" * 40)
    
    player_stats = client.get_player_statistics('usa.1')
    
    if player_stats:
        goals_leaders = player_stats.get('goals_leaders', [])
        assists_leaders = player_stats.get('assists_leaders', [])
        
        print(f"Season: {player_stats.get('season', {}).get('displayName', 'Unknown')}")
        print(f"Goals leaders: {len(goals_leaders)} players")
        print(f"Assists leaders: {len(assists_leaders)} players")
        
        # Show top 5 goal scorers
        print("\n🥅 Top 5 Goal Scorers:")
        for i, player in enumerate(goals_leaders[:5]):
            print(f"  {i+1}. {player['name']} ({player['team_abbreviation']}) - "
                  f"{player['goals']} goals in {player['matches_played']} matches")
        
        # Show top 5 assist providers
        print("\n🎯 Top 5 Assist Providers:")
        for i, player in enumerate(assists_leaders[:5]):
            print(f"  {i+1}. {player['name']} ({player['team_abbreviation']}) - "
                  f"{player['assists']} assists in {player['matches_played']} matches")
    
    # Demo 3: Team Offensive Statistics
    print("\n\n⚽ Demo 3: Team Offensive Statistics (ML Features)")
    print("-" * 50)
    
    team_stats = client.calculate_team_offensive_stats('usa.1')
    
    if team_stats:
        # Get team names for display
        teams_metadata = client.get_team_metadata('usa.1')
        team_names = {team['id']: team['name'] for team in teams_metadata}
        
        # Sort teams by total goals
        sorted_teams = sorted(team_stats.items(), 
                            key=lambda x: x[1]['total_goals'], reverse=True)
        
        print(f"Calculated offensive stats for {len(sorted_teams)} teams")
        print("\n🏆 Top 5 Most Prolific Teams:")
        
        for i, (team_id, stats) in enumerate(sorted_teams[:5]):
            team_name = team_names.get(team_id, f"Team {team_id}")
            print(f"\n{i+1}. {team_name}")
            print(f"   Total Goals: {stats['total_goals']}")
            print(f"   Total Assists: {stats['total_assists']}")
            print(f"   Squad Depth (goal scorers): {stats['squad_depth_goals']}")
            print(f"   Top Scorer Dependency: {stats['top_scorer_dependency']:.2%}")
            print(f"   Goal/Assist Ratio: {stats['total_goals']/max(1, stats['total_assists']):.2f}")
    
    print("\n" + "=" * 60)
    print("✅ Enhanced ESPN API Demo Complete")
    print("\n💡 Key ML Features Unlocked:")
    print("   • Team offensive strength (goals/assists)")
    print("   • Squad depth and balance metrics") 
    print("   • Star player dependency ratios")
    print("   • Player performance tracking")
    print("   • Team metadata for venue effects")


if __name__ == "__main__":
    demo_enhanced_espn_features()