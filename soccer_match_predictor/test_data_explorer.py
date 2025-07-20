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
from src.data.espn_client import ESPNSoccerClient
from datetime import datetime, timedelta
from typing import List, Optional, Union

def explore_data(dates: Optional[List[str]] = None, 
                leagues: Optional[List[str]] = None, 
                teams: Optional[List[str]] = None,
                show_detailed_records: bool = True,
                show_form_analysis: bool = True,
                show_match_details: bool = True):
    """
    Explore ESPN API data with flexible parameters.
    
    Args:
        dates: List of dates in YYYYMMDD format, or None for today
        leagues: List of league codes ('eng.1', 'usa.1'), or None for both
        teams: List of team names to filter by, or None for all teams
        show_detailed_records: Whether to show detailed team records
        show_form_analysis: Whether to analyze team form
        show_match_details: Whether to show match details
    """
    client = ESPNSoccerClient()
    
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
            print(f"🎮 Found {len(events)} matches")
            
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

def main():
    """Main function with example configurations."""
    
    # ===== CONFIGURATION EXAMPLES =====
    # Uncomment the scenario you want to test:
    
    # Example 1: Today's matches for all leagues and teams
    explore_data()
    
    # Example 2: Specific historical date
    # explore_data(dates=['20240428'])
    
    # Example 3: Multiple dates for Premier League only
    # explore_data(dates=['20240428', '20240421'], leagues=['eng.1'])
    
    # Example 4: Focus on specific teams
    # explore_data(dates=['20240428'], teams=['Liverpool', 'Arsenal', 'Manchester City'])
    
    # Example 5: MLS data only
    # explore_data(leagues=['usa.1'])
    
    # Example 6: Minimal output for quick checks
    # explore_data(
    #     dates=['20240428'], 
    #     teams=['Liverpool'], 
    #     show_detailed_records=False, 
    #     show_form_analysis=True
    # )
    

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