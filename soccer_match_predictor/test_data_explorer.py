"""
ESPN API Data Explorer - Interactive Testing Tool

Keep this file as a handy utility to explore ESPN API data at any time.
Modify the dates, leagues, and parameters below to test different scenarios.

Usage: python test_data_explorer.py
"""

import json
from src.data.espn_client import ESPNSoccerClient
from datetime import datetime, timedelta

def main():
    """Main exploration function - modify as needed."""
    client = ESPNSoccerClient()
    
    # ===== CONFIGURATION SECTION =====
    # Modify these parameters to test different scenarios
    
    LEAGUE = 'eng.1'  # 'eng.1' for Premier League, 'usa.1' for MLS
    
    # Test specific dates (YYYYMMDD format)
    DATES_TO_TEST = [
        "20240428",  # Late April 2024 - good historical data
        "20240421",  # Mid April 2024
        "20240506",  # Early May 2024
        None,        # Current date
    ]
    
    # Teams to focus on (optional filtering)
    TEAMS_OF_INTEREST = ['Liverpool', 'Arsenal', 'Manchester City', 'Chelsea']
    
    SHOW_DETAILED_RECORDS = True
    SHOW_FORM_ANALYSIS = True
    SHOW_MATCH_DETAILS = True
    
    # ===== EXPLORATION SECTION =====
    
    print("=" * 70)
    print(f"ESPN API DATA EXPLORER - {LEAGUE.upper()}")
    print("=" * 70)
    
    for date in DATES_TO_TEST:
        date_label = date if date else "CURRENT"
        print(f"\n{'='*20} {date_label} {'='*20}")
        
        scoreboard = client.get_scoreboard(LEAGUE, date)
        
        if not scoreboard or not scoreboard.get('events'):
            print(f"❌ No events found for {date_label}")
            continue
            
        events = scoreboard['events']
        print(f"📅 Found {len(events)} events")
        
        for i, event in enumerate(events):
            print(f"\n--- MATCH {i+1}: {event.get('name')} ---")
            print(f"Date: {event.get('date')}")
            print(f"Status: {event.get('status', {}).get('type', {}).get('name', 'Unknown')}")
            
            if 'competitions' not in event:
                continue
                
            comp = event['competitions'][0]
            competitors = comp.get('competitors', [])
            
            for competitor in competitors:
                team = competitor['team']
                team_name = team['displayName']
                
                # Skip if filtering by specific teams
                if TEAMS_OF_INTEREST and team_name not in TEAMS_OF_INTEREST:
                    continue
                
                print(f"\n🏟️  {team_name} ({competitor.get('homeAway', 'unknown').upper()})")
                print(f"   Score: {competitor.get('score', 0)}")
                
                if SHOW_DETAILED_RECORDS:
                    records = competitor.get('records', [])
                    for record in records:
                        summary = record.get('summary', 'N/A')
                        if summary != '0-0-0':  # Only show meaningful records
                            print(f"   Record: {summary} ({record.get('name', 'Unknown')})")
                            
                            # Calculate additional stats
                            if '-' in summary:
                                parts = summary.split('-')
                                if len(parts) == 3:
                                    wins, draws, losses = map(int, parts)
                                    total_games = wins + draws + losses
                                    points = (wins * 3) + draws
                                    win_rate = (wins / total_games * 100) if total_games > 0 else 0
                                    print(f"   Points: {points} | Win Rate: {win_rate:.1f}% | Games: {total_games}")
                
                if SHOW_FORM_ANALYSIS:
                    form = competitor.get('form', '')
                    if form:
                        print(f"   Form: {form}")
                        # Calculate form points
                        form_points = sum(3 if c == 'W' else 1 if c == 'D' else 0 for c in form)
                        print(f"   Form Points: {form_points}/15 (last 5 games)")
        
        print(f"\n{'='*50}")

def quick_team_lookup():
    """Quick function to look up specific team data."""
    client = ESPNSoccerClient()
    
    # Modify these as needed
    TEAM_NAME = "Liverpool"
    DATE = "20240428"
    
    print(f"\n🔍 QUICK LOOKUP: {TEAM_NAME} on {DATE}")
    print("-" * 40)
    
    scoreboard = client.get_scoreboard('eng.1', DATE)
    if scoreboard and 'events' in scoreboard:
        for event in scoreboard['events']:
            if 'competitions' in event:
                comp = event['competitions'][0]
                for competitor in comp.get('competitors', []):
                    team = competitor['team']
                    if TEAM_NAME.lower() in team['displayName'].lower():
                        print(f"Found: {team['displayName']}")
                        print(f"Records: {competitor.get('records', [])}")
                        print(f"Form: {competitor.get('form', 'N/A')}")
                        print(f"Score: {competitor.get('score', 0)}")
                        return
    
    print(f"❌ {TEAM_NAME} not found on {DATE}")

def compare_leagues():
    """Compare data structure between Premier League and MLS."""
    client = ESPNSoccerClient()
    
    print("\n🆚 LEAGUE COMPARISON")
    print("-" * 40)
    
    for league, name in [('eng.1', 'Premier League'), ('usa.1', 'MLS')]:
        print(f"\n{name}:")
        scoreboard = client.get_scoreboard(league)
        
        if scoreboard and 'events' in scoreboard:
            events = scoreboard['events']
            print(f"  Events: {len(events)}")
            
            if events:
                # Sample first team
                try:
                    comp = events[0]['competitions'][0]
                    team_data = comp['competitors'][0]
                    team = team_data['team']
                    
                    print(f"  Sample team: {team['displayName']}")
                    print(f"  Records: {team_data.get('records', [])}")
                    print(f"  Form: {team_data.get('form', 'N/A')}")
                except (KeyError, IndexError):
                    print("  Error parsing team data")
        else:
            print("  No events found")

if __name__ == "__main__":
    # Uncomment the function you want to run:
    
    main()                  # Full exploration
    # quick_team_lookup()   # Quick team lookup
    # compare_leagues()     # League comparison