"""
ESPN API Data Explorer - Interactive Testing Tool

Keep this file as a handy utility to explore ESPN API data at any time.
Modify the parameters in the main() function or call explore_data() directly.

Usage: 
    python test_data_explorer.py
    
Or import and use directly:
    from test_data_explorer import explore_data
    explore_data(dates=['20240428'], leagues=['eng.1'], teams=['Liverpool'])
"""

import json
import argparse
from src.data.espn_client import ESPNSoccerClient
from src.data.fbref_scraper import FBrefScraper
from datetime import datetime, timedelta
from typing import List, Optional, Union, Dict
import pandas as pd

def get_team_fbref_data(team_name: str, fbref_data: Dict, league: str) -> Dict:
    """
    Extract FBref data for a specific team.
    
    Args:
        team_name: Name of the team
        fbref_data: Cached FBref data
        league: League code
        
    Returns:
        Dictionary with team's FBref statistics
    """
    team_data = {}
    
    if not fbref_data.get(league):
        return team_data
    
    # Get data from league table
    if fbref_data[league]['table'] is not None:
        table = fbref_data[league]['table']
        team_row = table[table['team_name'].str.contains(team_name, case=False, na=False)]
        if not team_row.empty:
            row = team_row.iloc[0]
            team_data.update({
                'xG': row.get('xG', 0),
                'xGA': row.get('xGA', 0),
                'xGD': row.get('xGD', 0),
                'goals_per_game': row.get('goals_per_game', 0),
                'goals_against_per_game': row.get('goals_against_per_game', 0)
            })
    
    # Get home/away data
    if fbref_data[league]['home_away'] is not None:
        home_away = fbref_data[league]['home_away']
        team_row = home_away[home_away['team_name'].str.contains(team_name, case=False, na=False)]
        if not team_row.empty:
            row = team_row.iloc[0]
            team_data.update({
                'home_win_rate': row.get('home_win_rate', 0),
                'away_win_rate': row.get('away_win_rate', 0),
                'home_advantage_goals': row.get('home_advantage_goals', 0),
                'home_advantage_defense': row.get('home_advantage_defense', 0)
            })
    
    return team_data

def explore_data(dates: Optional[List[str]] = None, 
                leagues: Optional[List[str]] = None, 
                teams: Optional[List[str]] = None,
                show_detailed_records: bool = True,
                show_form_analysis: bool = True,
                show_match_details: bool = True,
                include_fbref_data: bool = True):
    """
    Explore ESPN API data with FBref advanced statistics integration.
    
    Args:
        dates: List of dates in YYYYMMDD format, or None for today
        leagues: List of league codes ('eng.1', 'usa.1'), or None for both
        teams: List of team names to filter by, or None for all teams
        show_detailed_records: Whether to show detailed team records
        show_form_analysis: Whether to analyze team form
        show_match_details: Whether to show match details
        include_fbref_data: Whether to include FBref advanced statistics
    """
    client = ESPNSoccerClient()
    
    # Initialize FBref data cache
    fbref_data = {}
    if include_fbref_data:
        fbref_scraper = FBrefScraper()
        print("🔄 Loading FBref advanced statistics...")
        
        # Pre-load FBref data for leagues we'll analyze
        for league in (leagues or ['eng.1', 'usa.1']):
            league_key = 'premier_league' if league == 'eng.1' else 'mls'
            try:
                # Get league table with xG data
                league_table = fbref_scraper.get_league_table(league_key)
                # Get home/away splits
                home_away = fbref_scraper.get_home_away_splits(league_key)
                # Get advanced stats
                advanced_stats = fbref_scraper.get_advanced_stats(league_key)
                
                fbref_data[league] = {
                    'table': league_table,
                    'home_away': home_away,
                    'advanced': advanced_stats
                }
                print(f"✅ Loaded {league_key} data from FBref")
            except Exception as e:
                print(f"⚠️  Failed to load {league_key} FBref data: {e}")
                fbref_data[league] = None
    
    # Set defaults
    if dates is None:
        dates = [datetime.now().strftime("%Y%m%d")]
    
    if leagues is None:
        leagues = ['eng.1', 'usa.1']
    
    # Convert teams to lowercase for case-insensitive matching
    teams_lower = [team.lower() for team in teams] if teams else None
    
    league_names = {
        'eng.1': 'Premier League',
        'usa.1': 'MLS'
    }

    print("=" * 80)
    print("ESPN API DATA EXPLORER")
    print("=" * 80)
    print(f"📅 Dates: {', '.join(dates) if dates != [datetime.now().strftime('%Y%m%d')] else 'TODAY'}")
    print(f"🏟️  Leagues: {', '.join([league_names.get(l, l) for l in leagues])}")
    print(f"👥 Teams: {', '.join(teams) if teams else 'ALL TEAMS'}")
    if include_fbref_data:
        print("📊 FBref Integration: ENABLED")
    print("=" * 80)
    
    for league in leagues:
        league_name = league_names.get(league, league.upper())
        
        print(f"\n🏆 {league_name}")
        print("=" * 60)
        
        for date in dates:
            date_label = date if date != datetime.now().strftime("%Y%m%d") else "TODAY"
            print(f"\n📅 {date_label}")
            print("-" * 40)
            
            # Handle "today" case
            api_date = None if date == datetime.now().strftime("%Y%m%d") else date
            
            scoreboard = client.get_scoreboard(league, api_date)
            
            if not scoreboard or not scoreboard.get('events'):
                print(f"❌ No events found for {league_name} on {date_label}")
                continue
                
            events = scoreboard['events']
            print(f"⚽ Found {len(events)} matches")
            
            for i, event in enumerate(events):
                match_name = event.get('name', 'Unknown Match')
                print(f"\n--- MATCH {i+1}: {match_name} ---")
                
                if show_match_details:
                    print(f"Date: {event.get('date')}")
                    print(f"Status: {event.get('status', {}).get('type', {}).get('name', 'Unknown')}")
                    venue = event.get('venue', {}).get('fullName')
                    if venue:
                        print(f"Venue: {venue}")
                
                if 'competitions' not in event:
                    continue
                    
                comp = event['competitions'][0]
                competitors = comp.get('competitors', [])
                
                # Track teams found for filtering
                teams_in_match = []
                
                for competitor in competitors:
                    team = competitor['team']
                    team_name = team['displayName']
                    teams_in_match.append(team_name.lower())
                
                # Check if we should show this match based on team filter
                if teams_lower and not any(team in teams_in_match for team in teams_lower):
                    print(f"⏭️  Skipping (no teams of interest)")
                    continue
                
                # Show team details
                for competitor in competitors:
                    team = competitor['team']
                    team_name = team['displayName']
                    
                    # Skip if filtering by specific teams and this isn't one
                    if teams_lower and team_name.lower() not in teams_lower:
                        continue
                    
                    home_away = competitor.get('homeAway', 'unknown').upper()
                    score = competitor.get('score', 0)
                    
                    print(f"\n🏟️  {team_name} ({home_away})")
                    print(f"   Score: {score}")
                    
                    # Add FBref advanced statistics
                    if include_fbref_data and fbref_data:
                        team_fbref = get_team_fbref_data(team_name, fbref_data, league)
                        if team_fbref:
                            print(f"   📊 FBref Analysis:")
                            
                            # Expected Goals analysis
                            if 'xG' in team_fbref and 'xGA' in team_fbref:
                                try:
                                    xg = float(team_fbref['xG'])
                                    xga = float(team_fbref['xGA']) 
                                    xgd = team_fbref.get('xGD', xg - xga)
                                    if isinstance(xgd, str):
                                        xgd = float(xgd)
                                    print(f"      Expected Goals: {xg:.1f} xG | {xga:.1f} xGA | {xgd:+.1f} xGD")
                                    
                                    # Quality analysis
                                    if xgd > 10:
                                        quality = "🔥 Elite"
                                    elif xgd > 5:
                                        quality = "💪 Strong" 
                                    elif xgd > 0:
                                        quality = "👍 Solid"
                                    elif xgd > -5:
                                        quality = "⚠️ Struggling"
                                    else:
                                        quality = "🚨 Poor"
                                    print(f"      Team Quality: {quality}")
                                except (ValueError, TypeError):
                                    print(f"      Expected Goals: {team_fbref['xG']} xG | {team_fbref['xGA']} xGA")
                            
                            # Home/Away advantage
                            if home_away == 'HOME' and 'home_win_rate' in team_fbref:
                                home_wr = team_fbref['home_win_rate']
                                away_wr = team_fbref.get('away_win_rate', 0)
                                advantage = team_fbref.get('home_advantage_goals', 0)
                                print(f"      Home Performance: {home_wr:.2f} win rate (vs {away_wr:.2f} away)")
                                if advantage > 0.3:
                                    print(f"      🏠 Strong home advantage (+{advantage:.2f} goals/game)")
                                elif advantage > 0.1:
                                    print(f"      🏠 Moderate home advantage (+{advantage:.2f} goals/game)")
                            
                            elif home_away == 'AWAY' and 'away_win_rate' in team_fbref:
                                away_wr = team_fbref['away_win_rate']
                                home_wr = team_fbref.get('home_win_rate', 0)
                                print(f"      Away Performance: {away_wr:.2f} win rate (vs {home_wr:.2f} home)")
                                if away_wr > home_wr:
                                    print(f"      ✈️ Surprisingly good away form")
                    
                    if show_detailed_records:
                        records = competitor.get('records', [])
                        for record in records:
                            summary = record.get('summary', 'N/A')
                            record_name = record.get('name', 'Unknown')
                            
                            if summary and summary != '0-0-0':  # Only show meaningful records
                                print(f"   Record: {summary} ({record_name})")
                                
                                # Calculate additional stats
                                if '-' in summary and summary.count('-') == 2:
                                    try:
                                        wins, draws, losses = map(int, summary.split('-'))
                                        total_games = wins + draws + losses
                                        if total_games > 0:
                                            points = (wins * 3) + draws
                                            win_rate = (wins / total_games * 100)
                                            print(f"   📊 Points: {points} | Win Rate: {win_rate:.1f}% | Games: {total_games}")
                                    except ValueError:
                                        pass
                    
                    if show_form_analysis:
                        form = competitor.get('form', '')
                        if form:
                            print(f"   Form: {form}")
                            # Calculate form points (W=3, D=1, L=0)
                            form_points = sum(3 if c == 'W' else 1 if c == 'D' else 0 for c in form)
                            max_points = len(form) * 3
                            print(f"   🔥 Form Points: {form_points}/{max_points} (last {len(form)} games)")
                            
                            # Form trend analysis
                            recent_form = form[-3:] if len(form) >= 3 else form
                            recent_points = sum(3 if c == 'W' else 1 if c == 'D' else 0 for c in recent_form)
                            if len(recent_form) > 0:
                                recent_avg = recent_points / len(recent_form)
                                trend = "🔥 Hot" if recent_avg >= 2.0 else "📈 Good" if recent_avg >= 1.5 else "📉 Poor"
                                print(f"   Recent Trend: {trend} ({recent_avg:.1f} pts/game)")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='ESPN API Data Explorer - Flexible soccer data analysis tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_data_explorer.py                                    # Today's matches, all leagues
  python test_data_explorer.py --dates 20240428                   # Specific date
  python test_data_explorer.py --dates 20240428 20240421          # Multiple dates
  python test_data_explorer.py --leagues eng.1                    # Premier League only
  python test_data_explorer.py --leagues usa.1                    # MLS only
  python test_data_explorer.py --teams Liverpool Arsenal          # Specific teams
  python test_data_explorer.py --dates 20240428 --teams Liverpool # Liverpool on specific date
  python test_data_explorer.py --minimal                          # Minimal output
  python test_data_explorer.py --quick-lookup Liverpool 20240428  # Quick team lookup
  python test_data_explorer.py --compare-leagues 20240428         # Compare leagues
        """
    )
    
    # Main exploration options
    parser.add_argument('--dates', nargs='*', 
                       help='Dates to explore (YYYYMMDD format). Leave empty for today.')
    parser.add_argument('--leagues', nargs='*', choices=['eng.1', 'usa.1'],
                       help='Leagues to explore (eng.1=Premier League, usa.1=MLS). Leave empty for both.')
    parser.add_argument('--teams', nargs='*',
                       help='Team names to filter by. Leave empty for all teams.')
    
    # Output control
    parser.add_argument('--no-records', action='store_true',
                       help='Hide detailed team records')
    parser.add_argument('--no-form', action='store_true', 
                       help='Hide form analysis')
    parser.add_argument('--no-details', action='store_true',
                       help='Hide match details (date, venue, etc.)')
    parser.add_argument('--minimal', action='store_true',
                       help='Minimal output (equivalent to --no-records --no-details)')
    parser.add_argument('--no-fbref', action='store_true',
                       help='Skip FBref advanced statistics (faster but less detailed)')
    
    # Alternative functions
    parser.add_argument('--quick-lookup', nargs=2, metavar=('TEAM', 'DATE'),
                       help='Quick lookup for specific team on specific date')
    parser.add_argument('--compare-leagues', nargs='?', const='today', metavar='DATE',
                       help='Compare leagues (optionally on specific date)')
    
    return parser.parse_args()

def main():
    """Main function with command line argument parsing."""
    args = parse_args()
    
    # Handle alternative functions first
    if args.quick_lookup:
        team_name, date = args.quick_lookup
        quick_team_lookup(team_name, date)
        return
    
    if args.compare_leagues is not None:
        date = None if args.compare_leagues == 'today' else args.compare_leagues
        compare_leagues(date)
        return
    
    # Handle main exploration
    dates = args.dates
    leagues = args.leagues
    teams = args.teams
    
    # Handle minimal flag
    if args.minimal:
        show_detailed_records = False
        show_match_details = False
        show_form_analysis = True  # Keep form analysis even in minimal mode
    else:
        show_detailed_records = not args.no_records
        show_form_analysis = not args.no_form
        show_match_details = not args.no_details
    
    # Call main exploration function
    explore_data(
        dates=dates,
        leagues=leagues,
        teams=teams,
        show_detailed_records=show_detailed_records,
        show_form_analysis=show_form_analysis,
        show_match_details=show_match_details,
        include_fbref_data=not args.no_fbref
    )
    

def quick_team_lookup(team_name: str = "Liverpool", 
                     date: str = "20240428", 
                     league: str = "eng.1"):
    """
    Quick function to look up specific team data.
    
    Args:
        team_name: Name of team to search for
        date: Date in YYYYMMDD format  
        league: League code ('eng.1' or 'usa.1')
    """
    client = ESPNSoccerClient()
    
    print(f"\n🔍 QUICK LOOKUP: {team_name} on {date}")
    print("-" * 50)
    
    scoreboard = client.get_scoreboard(league, date)
    if scoreboard and 'events' in scoreboard:
        for event in scoreboard['events']:
            if 'competitions' in event:
                comp = event['competitions'][0]
                for competitor in comp.get('competitors', []):
                    team = competitor['team']
                    if team_name.lower() in team['displayName'].lower():
                        print(f"✅ Found: {team['displayName']}")
                        print(f"Records: {competitor.get('records', [])}")
                        print(f"Form: {competitor.get('form', 'N/A')}")
                        print(f"Score: {competitor.get('score', 0)}")
                        print(f"Home/Away: {competitor.get('homeAway', 'Unknown')}")
                        return
    
    print(f"❌ {team_name} not found on {date}")

def compare_leagues(date: Optional[str] = None):
    """
    Compare data structure between Premier League and MLS.
    
    Args:
        date: Date in YYYYMMDD format, or None for current
    """
    client = ESPNSoccerClient()
    
    print(f"\n🆚 LEAGUE COMPARISON")
    if date:
        print(f"📅 Date: {date}")
    print("-" * 50)
    
    for league, name in [('eng.1', 'Premier League'), ('usa.1', 'MLS')]:
        print(f"\n🏟️  {name}:")
        scoreboard = client.get_scoreboard(league, date)
        
        if scoreboard and 'events' in scoreboard:
            events = scoreboard['events']
            print(f"  📊 Events: {len(events)}")
            
            if events:
                # Sample first team
                try:
                    comp = events[0]['competitions'][0]
                    team_data = comp['competitors'][0]
                    team = team_data['team']
                    
                    print(f"  👥 Sample team: {team['displayName']}")
                    records = team_data.get('records', [])
                    if records:
                        print(f"  📈 Records: {records[0].get('summary', 'N/A')}")
                    print(f"  🔥 Form: {team_data.get('form', 'N/A')}")
                except (KeyError, IndexError):
                    print("  ❌ Error parsing team data")
        else:
            print("  ❌ No events found")

if __name__ == "__main__":
    # Default: run main exploration
    main()
    
    # Uncomment for other functions:
    # quick_team_lookup("Arsenal", "20240428")
    # compare_leagues("20240428")