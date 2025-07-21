#!/usr/bin/env python3
"""
Test Unified Client with Historical Match Data

Test the unified client using a date when we know there were matches
to show the full functionality with real team statistics.
"""

from src.data.unified_client import UnifiedDataClient

def test_with_known_match_date():
    """Test with a date that had actual matches."""
    print("🧪 TESTING UNIFIED CLIENT WITH REAL MATCH DATA")
    print("=" * 60)
    
    client = UnifiedDataClient()
    
    # Use April 21, 2024 - we know Liverpool played
    test_date = '20240421'
    
    print(f"📅 Testing with date: {test_date}")
    print("-" * 40)
    
    # Get matches
    matches = client.get_matches_for_date(date=test_date, league='eng.1')
    
    if matches:
        print(f"✅ Found {len(matches)} matches")
        
        for match in matches:
            print(f"\n⚽ {match.home_team} vs {match.away_team}")
            print(f"   📅 {match.date}")
            print(f"   🎯 Score: {match.home_score}-{match.away_score}")
            print(f"   📊 Status: {match.status}")
            
            # Try to get team stats for teams in this match
            home_stats = client.get_team_stats(match.home_team, 'eng.1')
            away_stats = client.get_team_stats(match.away_team, 'eng.1')
            
            if home_stats:
                print(f"   🏠 {home_stats.team_name}:")
                print(f"      📊 Record: {home_stats.wins}-{home_stats.draws}-{home_stats.losses}")
                print(f"      🔥 Form: {home_stats.recent_form}")
                print(f"      📈 Trend: {home_stats.form_trend}")
            
            if away_stats:
                print(f"   ✈️ {away_stats.team_name}:")
                print(f"      📊 Record: {away_stats.wins}-{away_stats.draws}-{away_stats.losses}")
                print(f"      🔥 Form: {away_stats.recent_form}")
                print(f"      📈 Trend: {away_stats.form_trend}")
            
            # Generate prediction features if both teams found
            if home_stats and away_stats:
                print(f"\n🤖 ML FEATURES for {match.home_team} vs {match.away_team}:")
                features = client.get_prediction_features(
                    match.home_team, match.away_team, 'eng.1'
                )
                
                if features:
                    print(f"   🏠 Home Strength: {features.home_team_strength:.3f}")
                    print(f"   ✈️ Away Strength: {features.away_team_strength:.3f}")
                    print(f"   ⚖️ Advantage: {features.strength_difference:+.3f} (home)")
                    print(f"   🔥 Form: {features.home_recent_form_points} vs {features.away_recent_form_points}")
                    print(f"   📈 Momentum: {features.form_momentum_diff:+.3f}")
                    print(f"   🏟️ Venue: {features.venue_advantage:+.3f}")
                    print(f"   🏆 Derby: {'Yes' if features.is_derby else 'No'}")
                    
                    # Show what this means for prediction
                    if features.strength_difference > 0.1:
                        prediction = f"🏠 {match.home_team} favored"
                    elif features.strength_difference < -0.1:
                        prediction = f"✈️ {match.away_team} favored"
                    else:
                        prediction = "⚖️ Even match"
                    
                    print(f"   🎯 Basic Prediction: {prediction}")
    else:
        print("❌ No matches found for this date")

if __name__ == "__main__":
    test_with_known_match_date()