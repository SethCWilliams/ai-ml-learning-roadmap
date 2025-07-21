#!/usr/bin/env python3
"""Test script to validate Supabase database integration."""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_database_connection():
    """Test basic database connection."""
    print("🔍 Testing Database Connection...")
    
    try:
        from src.data.database import get_database_client
        
        db = get_database_client()
        health = db.health_check()
        
        if health['status'] == 'healthy':
            print("✅ Database connection successful")
            print(f"   Connection: {health['connection']}")
            return True
        else:
            print("❌ Database connection failed")
            print(f"   Error: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_leagues_table():
    """Test leagues table and initial data."""
    print("\n🏆 Testing Leagues Table...")
    
    try:
        from src.data.database import get_database_client
        
        db = get_database_client()
        leagues = db.get_leagues()
        
        if leagues:
            print(f"✅ Found {len(leagues)} leagues")
            for league in leagues:
                print(f"   - {league['name']} ({league['code']}) -> {league['espn_code']}")
            return True
        else:
            print("❌ No leagues found - check if database_schema.sql was run")
            return False
            
    except Exception as e:
        print(f"❌ Leagues table test failed: {e}")
        return False

def test_cache_functionality():
    """Test API caching functionality."""
    print("\n💾 Testing Cache Functionality...")
    
    try:
        from src.data.database import get_database_client
        
        db = get_database_client()
        
        # Test cache storage
        test_endpoint = "test://example.com/api"
        test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
        
        # Cache the test data
        db.cache_response(test_endpoint, test_data, cache_hours=1)
        print("✅ Cache storage successful")
        
        # Retrieve cached data
        cached = db.get_cached_response(test_endpoint)
        
        if cached and cached.get('test') == 'data':
            print("✅ Cache retrieval successful")
            print(f"   Cached data: {cached['test']}")
            return True
        else:
            print("❌ Cache retrieval failed")
            return False
            
    except Exception as e:
        print(f"❌ Cache functionality test failed: {e}")
        return False

def test_espn_client_with_caching():
    """Test ESPN client with database caching enabled."""
    print("\n🏈 Testing ESPN Client with Caching...")
    
    try:
        from src.data.espn_client import ESPNSoccerClient
        
        # Test with caching enabled
        espn_client = ESPNSoccerClient(use_cache=True)
        
        if espn_client.use_cache and espn_client.db_client:
            print("✅ ESPN client initialized with caching")
            
            # Test a simple request (this will use cache if available)
            print("   Testing cached API request...")
            league = 'eng.1'  # Use Premier League as test
            
            # Make a request that should be cached
            url = f"{espn_client.BASE_URL}/{league}/teams"
            response = espn_client._make_request(url, cache_hours=1)
            
            if response:
                print("✅ Cached API request successful")
                print(f"   Response keys: {list(response.keys())}")
                return True
            else:
                print("❌ API request failed")
                return False
        else:
            print("❌ ESPN client caching not enabled")
            return False
            
    except Exception as e:
        print(f"❌ ESPN client test failed: {e}")
        return False

def test_cache_stats():
    """Test cache statistics and cleanup."""
    print("\n📊 Testing Cache Statistics...")
    
    try:
        from src.data.database import get_database_client
        
        db = get_database_client()
        stats = db.get_cache_stats()
        
        if 'total_entries' in stats:
            print("✅ Cache statistics retrieved")
            print(f"   Total entries: {stats['total_entries']}")
            print(f"   Active entries: {stats['active_entries']}")
            print(f"   Expired entries: {stats['expired_entries']}")
            
            # Test cache cleanup
            if stats['expired_entries'] > 0:
                cleared = db.clear_cache(older_than_hours=0)  # Clear all expired
                print(f"   Cleared {cleared} expired entries")
            
            return True
        else:
            print("❌ Cache statistics failed")
            print(f"   Error: {stats.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Cache statistics test failed: {e}")
        return False

def main():
    """Run all database integration tests."""
    print("🚀 SUPABASE DATABASE INTEGRATION TESTS")
    print("=" * 60)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and configure Supabase settings")
        return 1
    
    # Run tests
    tests = [
        ("Database Connection", test_database_connection),
        ("Leagues Table", test_leagues_table),
        ("Cache Functionality", test_cache_functionality),
        ("ESPN Client Caching", test_espn_client_with_caching),
        ("Cache Statistics", test_cache_stats),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if failed == 0:
        print(f"✅ All {passed} tests passed!")
        print("\n🎉 Database integration is working correctly!")
        print("   Your ESPN API calls will now be cached automatically")
        print("   Run predictions as normal - caching happens transparently")
        return 0
    else:
        print(f"❌ {failed} test(s) failed, {passed} passed")
        print("\n🔧 Troubleshooting:")
        print("   1. Check SUPABASE_SETUP.md for configuration help")
        print("   2. Verify .env file has correct Supabase credentials")
        print("   3. Ensure database_schema.sql was run in Supabase dashboard")
        print("   4. Check Supabase project is running (dashboard shows green)")
        return 1

if __name__ == "__main__":
    exit(main())