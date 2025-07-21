#!/usr/bin/env python3
"""Simple test script for the soccer match predictor."""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import SoccerMatchPredictor


def test_predictor():
    """Test the prediction pipeline with a recent date."""
    print("🏆 Testing Soccer Match Predictor")
    print("=" * 50)
    
    # Initialize predictor
    predictor = SoccerMatchPredictor(recent_form_weight=0.7, model_type="rule_based")
    
    # Test with various dates to find matches
    test_dates = []
    
    # Add some recent dates
    for days_ago in range(0, 7):
        date = datetime.now() - timedelta(days=days_ago)
        test_dates.append(date.strftime("%Y%m%d"))
    
    # Test Premier League
    print("\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 Testing Premier League...")
    found_matches = False
    
    for date in test_dates:
        try:
            print(f"\nTrying date: {date}")
            predictions = predictor.predict_date(date, league="eng.1")
            
            if predictions:
                print(f"✅ Found {len(predictions)} matches!")
                output = predictor.format_predictions(predictions, detailed=True)
                print(output)
                found_matches = True
                break
            else:
                print(f"❌ No matches found for {date}")
                
        except Exception as e:
            print(f"❌ Error with {date}: {e}")
    
    if not found_matches:
        print("⚠️ No Premier League matches found in recent dates")
    
    # Test MLS
    print("\n🇺🇸 Testing MLS...")
    found_mls = False
    
    for date in test_dates:
        try:
            print(f"\nTrying MLS date: {date}")
            predictions = predictor.predict_date(date, league="usa.1")
            
            if predictions:
                print(f"✅ Found {len(predictions)} MLS matches!")
                output = predictor.format_predictions(predictions, detailed=True)
                print(output)
                found_mls = True
                break
            else:
                print(f"❌ No MLS matches found for {date}")
                
        except Exception as e:
            print(f"❌ MLS Error with {date}: {e}")
    
    if not found_mls:
        print("⚠️ No MLS matches found in recent dates")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")
    
    if found_matches or found_mls:
        print("✅ Predictor is working!")
    else:
        print("⚠️ No matches found - may be off-season")


if __name__ == "__main__":
    test_predictor()