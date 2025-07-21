#!/usr/bin/env python3
"""
Demo: Unified Data Client

Demonstrates the unified data client that currently uses ESPN but is designed
to easily accommodate additional data sources in the future.

This shows how we can build rich ML features from limited data sources
through intelligent feature engineering.
"""

from src.data.unified_client import UnifiedDataClient
from datetime import datetime
import json

def demo_basic_functionality():
    """Demonstrate basic unified client functionality."""
    print("🔄 UNIFIED DATA CLIENT DEMO")
    print("=" * 60)
    print("Current Data Sources: ESPN API")
    print("Future Extensions: API-Football, Sportradar, etc.")
    print("=" * 60)
    
    # Initialize client
    client = UnifiedDataClient(cache_duration_minutes=15)
    
    # Demo 1: Get today's matches
    print("\n📅 1. GETTING TODAY'S MATCHES")
    print("-" * 40)
    
    matches = client.get_matches_for_date(league='eng.1')
    if matches:
        print(f"✅ Found {len(matches)} Premier League matches")
        for match in matches[:2]:  # Show first 2
            print(f"   ⚽ {match.home_team} vs {match.away_team}")
            print(f"      📅 {match.date}")
            print(f"      🏟️  {match.venue}")
            print(f"      📊 Status: {match.status}")
            if match.home_score is not None:
                print(f"      🎯 Score: {match.home_score}-{match.away_score}")
    else:
        print("❌ No matches found for today")
        
        # Try a specific date with matches
        print("\n📅 Trying specific date (2024-04-21)...")
        matches = client.get_matches_for_date(date='20240421', league='eng.1')
        if matches:
            print(f"✅ Found {len(matches)} matches on 2024-04-21")
            sample_match = matches[0]
            print(f"   ⚽ Sample: {sample_match.home_team} vs {sample_match.away_team}")

def demo_team_statistics():
    """Demonstrate team statistics extraction."""
    print("\n📊 2. TEAM STATISTICS ANALYSIS")
    print("-" * 40)
    
    client = UnifiedDataClient()
    
    # Test with known teams
    test_teams = [
        ('Liverpool', 'eng.1'),
        ('Manchester City', 'eng.1'),
        ('Inter Miami CF', 'usa.1')
    ]
    
    for team_name, league in test_teams:
        print(f"\n🏟️  {team_name} ({client.league_names[league]})")
        
        stats = client.get_team_stats(team_name, league)
        if stats:
            print(f"   📈 Record: {stats.wins}-{stats.draws}-{stats.losses} ({stats.games_played} games)")
            print(f"   🎯 Points: {stats.points} ({stats.points_per_game:.2f} per game)")
            print(f"   📊 Win Rate: {stats.win_rate:.1%}")
            print(f"   🔥 Form: {stats.recent_form} ({stats.form_points} points)")
            print(f"   📈 Trend: {stats.form_trend}")
            print(f"   🗓️  Last Updated: {stats.last_updated[:16]}")
            print(f"   📡 Source: {stats.data_source}")
        else:
            print(f"   ❌ No statistics available")

def demo_prediction_features():
    """Demonstrate ML feature generation."""
    print("\n🤖 3. ML PREDICTION FEATURES")
    print("-" * 40)
    
    client = UnifiedDataClient()
    
    # Test matchups
    test_matchups = [
        ('Liverpool', 'Manchester City', 'eng.1'),
        ('Arsenal', 'Chelsea', 'eng.1'),
        ('LA Galaxy', 'LAFC', 'usa.1')
    ]
    
    for home_team, away_team, league in test_matchups:
        print(f"\n⚽ {home_team} vs {away_team} ({client.league_names[league]})")
        
        features = client.get_prediction_features(home_team, away_team, league)
        if features:
            print(f"   🏠 Home Strength: {features.home_team_strength:.3f}")
            print(f"   ✈️  Away Strength: {features.away_team_strength:.3f}")
            print(f"   ⚖️  Strength Diff: {features.strength_difference:+.3f}")
            print(f"   🔥 Form Points: {features.home_recent_form_points} vs {features.away_recent_form_points}")
            print(f"   📈 Momentum Diff: {features.form_momentum_diff:+.3f}")
            print(f"   🏟️  Venue Advantage: {features.venue_advantage:+.3f}")
            print(f"   🤝 Derby Match: {'Yes' if features.is_derby else 'No'}")
            print(f"   📊 H2H: {features.h2h_home_wins}-{features.h2h_draws}-{features.h2h_away_wins}")
        else:
            print(f"   ❌ Could not generate features")

def demo_extensibility():
    """Show how the client is designed for future extensions."""
    print("\n🔮 4. FUTURE EXTENSIBILITY")
    print("-" * 40)
    
    print("🏗️  Current Architecture:")
    print("   📡 Data Sources: ESPN API only")
    print("   🧠 Feature Engineering: Form, strength, momentum")
    print("   💾 Caching: 15-minute cache for performance")
    print("   🔌 Interface: Clean, extensible methods")
    
    print("\n🚀 Easy Future Extensions:")
    print("   📊 Advanced Stats: Add API-Football, Sportradar")
    print("   🏥 Injury Data: Add player availability")
    print("   🌤️  Weather: Add match-day conditions")
    print("   💰 Betting Odds: Add market sentiment")
    print("   🎯 Machine Learning: Add model predictions")
    
    print("\n💡 Implementation Strategy:")
    print("   1. Add new data source classes (e.g., APIFootballClient)")
    print("   2. Extend UnifiedDataClient to use multiple sources")
    print("   3. Enhance feature engineering with new data")
    print("   4. Maintain same interface for ML models")
    print("   5. Add fallbacks when premium sources unavailable")

def demo_caching():
    """Demonstrate caching functionality."""
    print("\n💾 5. CACHING PERFORMANCE")
    print("-" * 40)
    
    client = UnifiedDataClient(cache_duration_minutes=5)
    
    print("📊 Cache Info:")
    cache_info = client.get_cache_info()
    for key, value in cache_info.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔄 Testing cache performance...")
    
    # First call (will hit API)
    start_time = datetime.now()
    stats1 = client.get_team_stats('Liverpool', 'eng.1')
    first_call_time = datetime.now() - start_time
    
    # Second call (should use cache)
    start_time = datetime.now()
    stats2 = client.get_team_stats('Liverpool', 'eng.1')
    second_call_time = datetime.now() - start_time
    
    if stats1 and stats2:
        print(f"   📡 First call (API): {first_call_time.total_seconds():.2f}s")
        print(f"   💾 Second call (cache): {second_call_time.total_seconds():.2f}s")
        print(f"   ⚡ Speed improvement: {first_call_time.total_seconds() / max(second_call_time.total_seconds(), 0.001):.1f}x")
        print(f"   ✅ Data consistency: {'✓' if stats1.team_name == stats2.team_name else '✗'}")
    
    # Clear cache demo
    print(f"\n🧹 Clearing cache...")
    client.clear_cache()
    final_cache_info = client.get_cache_info()
    print(f"   Cache cleared: {final_cache_info['team_stats_cached']} items remaining")

def main():
    """Run all demos."""
    demo_basic_functionality()
    demo_team_statistics()
    demo_prediction_features()
    demo_extensibility()
    demo_caching()
    
    print("\n" + "=" * 60)
    print("✅ UNIFIED CLIENT DEMO COMPLETE")
    print("=" * 60)
    print("Key Benefits:")
    print("✅ Clean abstraction over data sources")
    print("✅ Rich feature engineering from basic data")
    print("✅ Built for easy future extensions")
    print("✅ Performance optimized with caching")
    print("✅ Ready for ML model development")

if __name__ == "__main__":
    main()