# Unified Data Strategy: ESPN + API-Football

## Overview
Clean, unified approach using two complementary data sources with clear responsibilities to avoid data inconsistencies and ensure both Premier League and MLS get identical feature treatment.

## Data Source Responsibilities

### 🏟️ **ESPN API** - Basic Match Data (Free)
**Use for both Premier League and MLS:**
- ✅ Match fixtures and schedules
- ✅ Live scores and results  
- ✅ Basic team records (wins/draws/losses)
- ✅ Team form strings (WWDLL)
- ✅ Match venues and dates
- ✅ Competition/season information

**Why ESPN for basics:**
- Proven reliable and fast
- Already implemented and working
- Good coverage for both leagues
- Free with no rate limits

### ⚽ **API-Football** - Advanced Statistics (Free Tier)
**Use for both Premier League and MLS:**
- ✅ Detailed team standings with advanced metrics
- ✅ Player statistics and performance data
- ✅ Head-to-head historical records
- ✅ Match statistics (when available)
- ✅ Team metadata (venues, founded dates, etc.)
- ✅ Injury and lineup information

**Why API-Football for advanced:**
- Professional API with comprehensive data
- Uniform data structure across leagues
- Advanced statistics not available in ESPN
- 100 requests/day sufficient for our needs

## Strict Data Consistency Rules

### ❌ **What We Will NOT Do**
- Mix advanced stats from different sources
- Use FBref for one league, API-Football for another
- Get basic data from API-Football when ESPN has it
- Create features that only work for one league

### ✅ **What We WILL Do**
- If a statistic isn't available from API-Football for both leagues, we skip it
- Use ESPN for all basic match/fixture data consistently
- Use API-Football only for advanced features available in both leagues
- Ensure feature engineering works identically for Premier League and MLS

## Implementation Strategy

### Phase 1: ESPN Foundation (✅ Complete)
```python
# Current ESPN usage - keep as-is
espn_client.get_scoreboard(league, date)  # Fixtures, scores
espn_client.get_team_records_from_scoreboard()  # Basic records
espn_client.get_team_form()  # Form strings
```

### Phase 2: API-Football Enhancement (🔧 In Progress)
```python
# New API-Football client for advanced data
api_football_client.get_team_statistics(league, season)
api_football_client.get_player_statistics(league, season)  
api_football_client.get_head_to_head(team1, team2)
api_football_client.get_standings(league, season)
```

### Phase 3: Unified Data Layer (📋 Planned)
```python
# Combined client that manages both sources
unified_client.get_match_data(league, date)  # ESPN + API-Football combined
unified_client.get_team_features(team, league)  # All features for ML
```

## Expected Features by Source

### ESPN Features (Both Leagues)
- `team_record`: "22-8-3" format
- `form`: "WWDLL" last 5 games
- `home_away`: HOME/AWAY indicator
- `venue`: Match venue
- `match_date`: ISO format dates

### API-Football Features (Both Leagues)  
- `goals_for_season`: Total goals scored
- `goals_against_season`: Total goals conceded
- `clean_sheets`: Clean sheet count
- `avg_goals_per_match`: Scoring rate
- `win_percentage`: Win rate as decimal
- `h2h_record`: Head-to-head vs opponent
- `recent_form_points`: Points from last N games

### Combined Features (Calculated)
- `form_momentum`: Trend analysis using both sources
- `venue_advantage`: Home performance vs away
- `attacking_strength`: Goals relative to league average
- `defensive_strength`: Goals conceded relative to league

## API Usage Budget

### Daily Estimates
- **ESPN**: Unlimited requests (free)
- **API-Football**: ~15 requests/day (well under 100 limit)
  - 2 leagues × 2 standings requests = 4
  - 2 leagues × 1 team metadata = 2  
  - 5 match statistics requests = 5
  - 4 testing/development requests = 4
  - **Total**: 15/100 requests used

### Data Refresh Strategy
- **ESPN**: Real-time for fixtures and live scores
- **API-Football**: Cache team stats (weekly refresh), standings (daily refresh)
- **Local Storage**: Historical data cached permanently

## Quality Assurance

### Data Validation Rules
1. Every feature must work for both Premier League and MLS
2. No missing data allowed - fill with league averages if needed
3. Consistent data types and formats across leagues
4. All timestamps in UTC
5. Team names standardized between sources

### Testing Requirements
- Unit tests for each data source
- Integration tests for combined features
- Validation that same feature engineering works for both leagues
- Performance tests to ensure we stay under API limits

## Success Metrics
- ✅ Identical feature set for both Premier League and MLS
- ✅ Sub-15 API-Football requests per day
- ✅ Zero FBref dependencies
- ✅ Consistent data quality across leagues
- ✅ Clean separation of basic vs advanced data sources

This strategy ensures we get the best of both worlds: reliable basic data from ESPN and comprehensive advanced statistics from API-Football, with perfect consistency across both leagues.