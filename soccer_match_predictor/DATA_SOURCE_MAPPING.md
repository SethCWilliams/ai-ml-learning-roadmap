# Data Source Mapping for Soccer Match Predictor

## Overview
This document maps our core features to specific data sources with implementation details.

## ESPN API (Free - No Authentication)

### Premier League: `eng.1` | MLS: `usa.1`

### 1. Scoreboard Endpoint
**URL:** `http://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard`
**Provides:**
- Recent match results
- Upcoming fixtures
- Live match status
- Basic team info

**Sample Response Structure:**
```json
{
  "events": [
    {
      "id": "12345",
      "date": "2023-10-20T15:00:00Z",
      "competitions": [
        {
          "competitors": [
            {
              "homeAway": "home",
              "team": {"displayName": "Arsenal", "abbreviation": "ARS"},
              "score": "2"
            },
            {
              "homeAway": "away", 
              "team": {"displayName": "Chelsea", "abbreviation": "CHE"},
              "score": "1"
            }
          ]
        }
      ]
    }
  ]
}
```

**Maps to Features:**
- ✅ Current form calculation (last 5 results)
- ✅ Home/away result patterns
- ✅ Recent scoring patterns

### 2. Standings Endpoint
**URL:** `http://site.api.espn.com/apis/site/v2/sports/soccer/{league}/standings`
**Provides:**
- League table position
- Points, wins, losses, draws
- Goals for/against
- Recent form

**Maps to Features:**
- ✅ League position
- ✅ Win percentage
- ✅ Goals per game
- ✅ Points per game

### 3. News Endpoint
**URL:** `http://site.api.espn.com/apis/site/v2/sports/soccer/{league}/news`
**Provides:**
- Injury updates (inconsistent)
- Transfer news
- Match previews

**Maps to Features:**
- ⚠️ Injury information (limited, text-based)

## FBref.com (Web Scraping Required)

### Premier League Pages
- **Main Stats:** `https://fbref.com/en/comps/9/Premier-League-Stats`
- **Standings:** `https://fbref.com/en/comps/9/Premier-League-Stats#stats_squads_standard`
- **Team Stats:** `https://fbref.com/en/squads/{team-id}/{team-name}-Stats`

### MLS Pages  
- **Main Stats:** `https://fbref.com/en/comps/22/Major-League-Soccer-Stats`
- **Standings:** `https://fbref.com/en/comps/22/Major-League-Soccer-Stats#stats_squads_standard`

### Key Data Tables

#### 1. League Standings Table
**CSS Selector:** `#stats_squads_standard tbody tr`
**Columns Available:**
- Squad name
- Games played
- Wins, draws, losses  
- Goals for/against
- Goal difference
- Points
- Points per match

**Maps to Features:**
- ✅ Team records (W/D/L)
- ✅ Goal difference per game
- ✅ Points per game
- ✅ League position

#### 2. Home/Away Performance Table
**CSS Selector:** `#stats_squads_home_away tbody tr`
**Columns Available:**
- Home: MP, W, D, L, GF, GA
- Away: MP, W, D, L, GF, GA

**Maps to Features:**
- ✅ Home win rate, away win rate
- ✅ Home goals average, away goals average
- ✅ Home/away defensive records

#### 3. Advanced Team Stats
**CSS Selector:** `#stats_squads_shooting tbody tr`
**Columns Available:**
- Expected Goals (xG)
- Expected Goals Against (xGA) 
- Shots for/against
- Clean sheets

**Maps to Features:**
- ✅ Expected goals metrics
- ✅ Clean sheet percentage
- ✅ Shot conversion rates

## Implementation Mapping by Feature

### ✅ High Confidence (Good Data Available)

#### Team Identity & Strength
- **Source:** FBref standings + ESPN standings
- **Implementation:** Team rating based on points per game + goal difference
- **Update Frequency:** Weekly

#### Overall Records
- **Source:** FBref league table
- **Implementation:** Direct from standings data
- **Update Frequency:** After each match day

#### Home Advantage
- **Source:** FBref home/away splits
- **Implementation:** Calculate venue-specific performance metrics
- **Update Frequency:** Weekly

#### Current Form
- **Source:** ESPN scoreboard (last 5 results)
- **Implementation:** Rolling window calculation
- **Update Frequency:** After each match

### ⚠️ Medium Confidence (Limited Data)

#### Squad Strength
- **Source:** FBref player stats (aggregated)
- **Implementation:** Team-level averages, not individual lineups
- **Limitation:** No real-time lineup quality

#### Tactical Formations
- **Source:** Manual research + FBref averages
- **Implementation:** Season-long formation preferences
- **Limitation:** Not match-specific

### ❌ Low Confidence (Poor Data Quality)

#### Real-time Lineups
- **Issue:** Only available close to match time
- **Workaround:** Use average team strength instead

#### Injury Impact
- **Issue:** Inconsistent reporting across sources
- **Workaround:** Focus on overall squad depth metrics

## Data Collection Strategy

### Phase 1: Team-Level Foundation (Week 1-2)
1. **FBref Scraping:** League tables, home/away splits
2. **ESPN API:** Recent results for form calculation
3. **Storage:** SQLite database with team statistics

### Phase 2: Enhanced Metrics (Week 3-4)
1. **Advanced Stats:** xG, xGA from FBref
2. **Weather Integration:** Match-day weather APIs
3. **Historical Analysis:** Season-over-season trends

### Phase 3: Refinement (Future)
1. **Player Aggregation:** Team-level player quality metrics
2. **Real-time Updates:** Live form adjustments
3. **Transfer Impact:** Squad change analysis

## Sample Implementation Code Structure

```python
# Data collectors
class ESPNAPIClient:
    def get_recent_results(self, league, team_id):
        # Get last 5 matches for form calculation
        pass
    
    def get_standings(self, league):
        # Get current league table
        pass

class FBrefScraper:
    def scrape_team_stats(self, league):
        # Get detailed team statistics
        pass
    
    def scrape_home_away_splits(self, league):
        # Get venue-specific performance
        pass

# Feature engineering
class FeatureEngineer:
    def calculate_form_metrics(self, recent_results):
        # Calculate points from last 5 games
        pass
    
    def calculate_team_strength(self, season_stats):
        # Create team rating from multiple metrics
        pass
```

## Rate Limiting & Ethics

### ESPN API
- **Rate Limit:** ~100 requests/hour (observed)
- **Caching:** Cache results for 1 hour minimum
- **Ethics:** Public API, no restrictions observed

### FBref Scraping
- **Rate Limit:** 1 request per 2 seconds minimum
- **Caching:** Cache daily for team stats
- **Ethics:** Respect robots.txt, add User-Agent, educational use

## Next Steps

1. **Start with FBref scraping** - Most valuable data
2. **Build ESPN API client** - Real-time updates
3. **Create feature engineering pipeline** - Transform raw data
4. **Implement caching strategy** - Avoid redundant requests
5. **Build validation system** - Ensure data quality

This provides a clear path from data sources to ML features with realistic expectations about what's achievable.