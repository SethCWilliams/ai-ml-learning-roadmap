#!/usr/bin/env python3
"""
API Usage Calculator for Soccer Match Predictor

Estimates daily API requests needed for our ML project to determine
if 100 free requests/day is sufficient or if we need multiple keys/paid plan.
"""

def calculate_daily_usage():
    """Calculate estimated daily API requests for our soccer predictor."""
    
    print("🧮 API USAGE CALCULATOR")
    print("=" * 50)
    
    # Core data collection needs
    usage_scenarios = {
        "Development & Testing": {
            "League data (2 leagues)": 2,
            "Team data (40 teams total)": 2,  # Cached daily
            "Recent matches (last 10 per league)": 2,
            "Standings (2 leagues)": 2,
            "Match statistics sampling": 5,
            "Testing/debugging": 10,
            "Total": 23
        },
        
        "Daily Prediction Pipeline": {
            "Today's fixtures (2 leagues)": 2,
            "Team current form (updated daily)": 2,
            "Current standings": 2,
            "Injury/lineup updates": 2,
            "Match statistics for model": 5,
            "Total": 13
        },
        
        "Historical Data Collection": {
            "Season fixtures (one-time)": 10,
            "Historical team stats": 20,
            "Player statistics": 15,
            "Head-to-head records": 10,
            "Total": 55
        },
        
        "Model Training Period": {
            "Feature engineering experiments": 20,
            "Data validation": 10,
            "Model evaluation": 5,
            "Total": 35
        }
    }
    
    print("\n📋 USAGE BREAKDOWN BY PHASE:")
    
    max_daily = 0
    for phase, requests in usage_scenarios.items():
        total = requests.pop("Total")
        max_daily = max(max_daily, total)
        
        print(f"\n🔹 {phase}: {total} requests/day")
        for task, count in requests.items():
            print(f"   {task}: {count}")
    
    print(f"\n🎯 PEAK USAGE: {max_daily} requests/day")
    print(f"Free tier limit: 100 requests/day")
    
    if max_daily <= 100:
        print("✅ Single free API key is SUFFICIENT!")
    elif max_daily <= 300:
        print("⚠️  Need 2-3 free keys OR upgrade to Pro ($19/month)")
    else:
        print("🚨 Definitely need paid plan")
    
    print("\n💡 OPTIMIZATION STRATEGIES:")
    print("✅ Cache team/league data (update weekly)")
    print("✅ Batch requests efficiently") 
    print("✅ Only fetch match stats for recent games")
    print("✅ Use local storage for historical data")
    
    optimized_daily = 15  # Realistic optimized usage
    print(f"\n🚀 OPTIMIZED DAILY USAGE: ~{optimized_daily} requests/day")
    print("✅ Well within free tier limits!")
    
    return max_daily, optimized_daily

def compare_options():
    """Compare different API access strategies."""
    
    print("\n" + "=" * 60)
    print("💰 COST-BENEFIT ANALYSIS")
    print("=" * 60)
    
    options = {
        "Single Free Key": {
            "cost": "$0/month",
            "requests": "100/day",
            "pros": ["Completely free", "Simple setup", "Sufficient for learning"],
            "cons": ["Limited requests", "May hit limits during development"]
        },
        
        "3 Free Keys": {
            "cost": "$0/month", 
            "requests": "300/day",
            "pros": ["Still free", "More development headroom"],
            "cons": ["Complex key management", "May violate ToS", "Requires multiple accounts"]
        },
        
        "Pro Plan": {
            "cost": "$19/month",
            "requests": "7,500/day", 
            "pros": ["Legitimate", "No limits worry", "Better support"],
            "cons": ["Monthly cost", "Overkill for learning project"]
        }
    }
    
    for option, details in options.items():
        print(f"\n🔹 {option}")
        print(f"   Cost: {details['cost']}")
        print(f"   Requests: {details['requests']}")
        print("   Pros:")
        for pro in details['pros']:
            print(f"     ✅ {pro}")
        print("   Cons:")
        for con in details['cons']:
            print(f"     ❌ {con}")

def main():
    """Main calculator function."""
    max_usage, optimized_usage = calculate_daily_usage()
    compare_options()
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDATION")
    print("=" * 60)
    
    if optimized_usage <= 100:
        print("✅ START with single free API key")
        print("✅ Implement smart caching and batching")
        print("✅ Monitor usage during development")
        print("✅ Upgrade only if actually needed")
    else:
        print("⚠️  Consider multiple keys OR Pro plan")
        print("💡 Test with free key first to validate approach")

if __name__ == "__main__":
    main()