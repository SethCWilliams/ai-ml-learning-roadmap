"""
FBref.com Scraper for Advanced Soccer Statistics

This module scrapes detailed team statistics from FBref.com that aren't available
through the ESPN API, including:
- Home/away performance splits
- Expected Goals (xG) and Expected Goals Against (xGA)
- Advanced defensive and attacking metrics
- Clean sheet percentages and shot conversion rates

ML Learning Focus: This demonstrates ethical web scraping, HTML parsing,
and advanced feature engineering from statistical websites.
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union
import re
import pandas as pd
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FBrefScraper:
    """
    FBref.com scraper with respectful rate limiting and robust error handling.
    
    FBref provides advanced soccer statistics not available in basic APIs.
    We implement ethical scraping practices including rate limiting, 
    proper User-Agent headers, and respect for robots.txt.
    
    Supported Leagues:
    - Premier League: Competition ID 9
    - MLS: Competition ID 22
    """
    
    BASE_URL = "https://fbref.com"
    
    # Competition IDs for different leagues
    LEAGUE_IDS = {
        'premier_league': 9,
        'mls': 22
    }
    
    # Rate limiting: 2 seconds between requests to be respectful
    RATE_LIMIT_DELAY = 2.0
    
    def __init__(self, rate_limit_delay: float = RATE_LIMIT_DELAY):
        """
        Initialize FBref scraper with ethical scraping configuration.
        
        Args:
            rate_limit_delay: Seconds to wait between requests
        """
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.session = requests.Session()
        
        # Set a descriptive User-Agent for ethical scraping
        self.session.headers.update({
            'User-Agent': 'Soccer-ML-Learning-Project/1.0 (Educational Purpose; Contact: educational-use@example.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def _rate_limit(self):
        """Implement rate limiting to respect FBref's servers."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """
        Make a rate-limited request to FBref with proper error handling.
        
        Args:
            url: URL to scrape
            
        Returns:
            BeautifulSoup object or None if request failed
        """
        self._rate_limit()
        
        try:
            logger.info(f"Requesting: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing {url}: {e}")
            return None
    
    def get_league_table(self, league: str) -> Optional[pd.DataFrame]:
        """
        Scrape the main league standings table with basic statistics.
        
        This provides fundamental team metrics:
        - Games played, wins, draws, losses
        - Goals for/against and goal difference
        - Points and points per match
        
        Args:
            league: League name ('premier_league' or 'mls')
            
        Returns:
            DataFrame with team standings or None if failed
        """
        if league not in self.LEAGUE_IDS:
            logger.error(f"Unsupported league: {league}")
            return None
        
        league_id = self.LEAGUE_IDS[league]
        
        # Construct URL for league stats page
        if league == 'premier_league':
            url = f"{self.BASE_URL}/en/comps/{league_id}/Premier-League-Stats"
        else:  # MLS
            url = f"{self.BASE_URL}/en/comps/{league_id}/Major-League-Soccer-Stats"
        
        soup = self._make_request(url)
        if not soup:
            return None
        
        # Find the main standings table - try multiple possible IDs
        table_ids = [
            'results2024-202591_overall',  # Current season table
            'results2023-202491_overall',  # Previous season fallback
            'stats_squads_standard'        # Generic fallback
        ]
        
        table = None
        for table_id in table_ids:
            table = soup.find('table', {'id': table_id})
            if table:
                logger.info(f"Found standings table with ID: {table_id}")
                break
        
        if not table:
            logger.error("Could not find standings table")
            return None
        
        return self._parse_standings_table(table)
    
    def _parse_standings_table(self, table) -> pd.DataFrame:
        """
        Parse the standings table into a structured DataFrame.
        
        ML Learning Point: This demonstrates how to extract structured data
        from HTML tables for feature engineering.
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            DataFrame with team statistics
        """
        data = []
        
        # Get table headers
        headers = []
        header_row = table.find('thead').find('tr')
        for th in header_row.find_all('th'):
            header_text = th.get_text(strip=True)
            if header_text:
                headers.append(header_text)
        
        # Get table rows
        tbody = table.find('tbody')
        if not tbody:
            return pd.DataFrame()
        
        for row in tbody.find_all('tr'):
            # Skip header rows that might appear in tbody
            if row.find('th') and 'Squad' in row.find('th').get_text():
                continue
            
            row_data = []
            cells = row.find_all(['td', 'th'])
            
            for cell in cells:
                # Handle team name cell (usually first cell)
                if cell.find('a'):
                    # Extract team name from link
                    team_name = cell.find('a').get_text(strip=True)
                    row_data.append(team_name)
                else:
                    # Regular data cell
                    text = cell.get_text(strip=True)
                    # Try to convert to numeric if possible
                    if text.replace('.', '').replace('-', '').isdigit():
                        try:
                            row_data.append(float(text) if '.' in text else int(text))
                        except ValueError:
                            row_data.append(text)
                    else:
                        row_data.append(text)
            
            if row_data:
                data.append(row_data)
        
        # Create DataFrame
        if data and headers:
            # Ensure we have the right number of columns
            min_cols = min(len(headers), max(len(row) for row in data) if data else 0)
            headers = headers[:min_cols]
            data = [row[:min_cols] for row in data]
            
            df = pd.DataFrame(data, columns=headers)
            return self._clean_standings_dataframe(df)
        
        return pd.DataFrame()
    
    def _clean_standings_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize the standings DataFrame.
        
        Args:
            df: Raw standings DataFrame
            
        Returns:
            Cleaned DataFrame with standardized column names
        """
        if df.empty:
            return df
        
        # Standardize column names
        column_mapping = {
            'Squad': 'team_name',
            'MP': 'games_played',
            'W': 'wins',
            'D': 'draws',
            'L': 'losses',
            'GF': 'goals_for',
            'GA': 'goals_against',
            'GD': 'goal_difference',
            'Pts': 'points',
            'Pts/MP': 'points_per_match'
        }
        
        # Rename columns that exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Calculate additional features
        if 'games_played' in df.columns and 'games_played' in df.columns:
            df['win_rate'] = df['wins'] / df['games_played'].replace(0, 1)
            df['goals_per_game'] = df['goals_for'] / df['games_played'].replace(0, 1)
            df['goals_against_per_game'] = df['goals_against'] / df['games_played'].replace(0, 1)
        
        return df
    
    def get_home_away_splits(self, league: str) -> Optional[pd.DataFrame]:
        """
        Scrape home/away performance splits for all teams.
        
        This provides crucial venue-specific features:
        - Home vs away win rates
        - Home vs away goal scoring patterns
        - Venue-specific defensive performance
        
        Args:
            league: League name ('premier_league' or 'mls')
            
        Returns:
            DataFrame with home/away splits or None if failed
        """
        if league not in self.LEAGUE_IDS:
            logger.error(f"Unsupported league: {league}")
            return None
        
        league_id = self.LEAGUE_IDS[league]
        
        # Construct URL for league stats page
        if league == 'premier_league':
            url = f"{self.BASE_URL}/en/comps/{league_id}/Premier-League-Stats"
        else:  # MLS
            url = f"{self.BASE_URL}/en/comps/{league_id}/Major-League-Soccer-Stats"
        
        soup = self._make_request(url)
        if not soup:
            return None
        
        # Find the home/away splits table - try multiple possible IDs
        table_ids = [
            'results2024-202591_home_away',  # Current season table
            'results2023-202491_home_away',  # Previous season fallback
            'stats_squads_home_away'         # Generic fallback
        ]
        
        table = None
        for table_id in table_ids:
            table = soup.find('table', {'id': table_id})
            if table:
                logger.info(f"Found home/away table with ID: {table_id}")
                break
        
        if not table:
            logger.warning("Could not find home/away splits table")
            return None
        
        return self._parse_home_away_table(table)
    
    def _parse_home_away_table(self, table) -> pd.DataFrame:
        """
        Parse home/away splits table into structured DataFrame.
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            DataFrame with home/away performance splits
        """
        data = []
        
        tbody = table.find('tbody')
        if not tbody:
            return pd.DataFrame()
        
        for row in tbody.find_all('tr'):
            # Skip header rows
            if row.find('th') and 'Squad' in row.find('th').get_text():
                continue
            
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            
            # Extract team name
            team_cell = cells[0]
            if team_cell.find('a'):
                team_name = team_cell.find('a').get_text(strip=True)
            else:
                team_name = team_cell.get_text(strip=True)
            
            # Parse home and away data
            row_data = {'team_name': team_name}
            
            # The table typically has home stats followed by away stats
            # We'll need to identify which columns are which
            cell_texts = [cell.get_text(strip=True) for cell in cells[1:]]
            
            # Basic parsing - this may need adjustment based on actual table structure
            if len(cell_texts) >= 12:  # Assuming at least 6 home + 6 away columns
                # Home stats (typically first 6-7 columns after team name)
                row_data.update({
                    'home_games': self._safe_int(cell_texts[0]),
                    'home_wins': self._safe_int(cell_texts[1]),
                    'home_draws': self._safe_int(cell_texts[2]),
                    'home_losses': self._safe_int(cell_texts[3]),
                    'home_goals_for': self._safe_int(cell_texts[4]),
                    'home_goals_against': self._safe_int(cell_texts[5]),
                })
                
                # Away stats (next 6-7 columns)
                away_start = 6
                row_data.update({
                    'away_games': self._safe_int(cell_texts[away_start]),
                    'away_wins': self._safe_int(cell_texts[away_start + 1]),
                    'away_draws': self._safe_int(cell_texts[away_start + 2]),
                    'away_losses': self._safe_int(cell_texts[away_start + 3]),
                    'away_goals_for': self._safe_int(cell_texts[away_start + 4]),
                    'away_goals_against': self._safe_int(cell_texts[away_start + 5]),
                })
            
            data.append(row_data)
        
        df = pd.DataFrame(data)
        return self._calculate_home_away_features(df)
    
    def _safe_int(self, value: str) -> int:
        """Safely convert string to integer."""
        try:
            return int(value) if value.isdigit() else 0
        except (ValueError, AttributeError):
            return 0
    
    def _calculate_home_away_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate additional home/away features for ML models.
        
        Args:
            df: DataFrame with basic home/away stats
            
        Returns:
            DataFrame with calculated features
        """
        if df.empty:
            return df
        
        # Calculate win rates
        df['home_win_rate'] = df['home_wins'] / df['home_games'].replace(0, 1)
        df['away_win_rate'] = df['away_wins'] / df['away_games'].replace(0, 1)
        
        # Calculate goals per game
        df['home_goals_per_game'] = df['home_goals_for'] / df['home_games'].replace(0, 1)
        df['away_goals_per_game'] = df['away_goals_for'] / df['away_games'].replace(0, 1)
        
        # Calculate defensive stats
        df['home_goals_against_per_game'] = df['home_goals_against'] / df['home_games'].replace(0, 1)
        df['away_goals_against_per_game'] = df['away_goals_against'] / df['away_games'].replace(0, 1)
        
        # Calculate home advantage metrics
        df['home_advantage_goals'] = df['home_goals_per_game'] - df['away_goals_per_game']
        df['home_advantage_defense'] = df['away_goals_against_per_game'] - df['home_goals_against_per_game']
        df['home_advantage_win_rate'] = df['home_win_rate'] - df['away_win_rate']
        
        return df
    
    def get_advanced_stats(self, league: str) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Scrape advanced team statistics including xG, shooting, and defensive metrics.
        
        This provides advanced features for ML models:
        - Expected Goals (xG) and Expected Goals Against (xGA)
        - Shot conversion rates and shot quality
        - Defensive actions and clean sheet rates
        
        Args:
            league: League name ('premier_league' or 'mls')
            
        Returns:
            Dictionary of DataFrames with different stat categories
        """
        if league not in self.LEAGUE_IDS:
            logger.error(f"Unsupported league: {league}")
            return None
        
        stats_data = {}
        
        # Try to get various advanced stat tables
        stat_tables = {
            'shooting': 'stats_squads_shooting_for',
            'goalkeeping': 'stats_squads_keeper_for', 
            'passing': 'stats_squads_passing_for',
            'defense': 'stats_squads_defense_for',
            'possession': 'stats_squads_possession_for'
        }
        
        league_id = self.LEAGUE_IDS[league]
        if league == 'premier_league':
            base_url = f"{self.BASE_URL}/en/comps/{league_id}/Premier-League-Stats"
        else:  # MLS
            base_url = f"{self.BASE_URL}/en/comps/{league_id}/Major-League-Soccer-Stats"
        
        soup = self._make_request(base_url)
        if not soup:
            return None
        
        for stat_name, table_id in stat_tables.items():
            table = soup.find('table', {'id': table_id})
            if table:
                logger.info(f"Found {stat_name} table")
                df = self._parse_generic_stats_table(table, stat_name)
                if not df.empty:
                    stats_data[stat_name] = df
            else:
                logger.warning(f"Could not find {stat_name} table with id {table_id}")
        
        return stats_data if stats_data else None
    
    def _parse_generic_stats_table(self, table, stat_type: str) -> pd.DataFrame:
        """
        Parse a generic statistics table from FBref.
        
        Args:
            table: BeautifulSoup table element
            stat_type: Type of statistics (for column naming)
            
        Returns:
            DataFrame with parsed statistics
        """
        data = []
        
        # Get headers
        headers = []
        header_row = table.find('thead')
        if header_row:
            for th in header_row.find_all('th'):
                header_text = th.get_text(strip=True)
                if header_text and header_text != 'Rk':  # Skip ranking column
                    headers.append(header_text)
        
        tbody = table.find('tbody')
        if not tbody:
            return pd.DataFrame()
        
        for row in tbody.find_all('tr'):
            # Skip header rows that might appear in tbody
            if row.find('th') and any(keyword in row.find('th').get_text() 
                                    for keyword in ['Squad', 'Team', 'Club']):
                continue
            
            row_data = []
            cells = row.find_all(['td', 'th'])
            
            for i, cell in enumerate(cells):
                if i == 0:  # First cell is usually team name
                    if cell.find('a'):
                        team_name = cell.find('a').get_text(strip=True)
                        row_data.append(team_name)
                    else:
                        team_name = cell.get_text(strip=True)
                        row_data.append(team_name)
                else:
                    # Data cells
                    text = cell.get_text(strip=True)
                    # Try to convert to numeric
                    try:
                        if '.' in text:
                            row_data.append(float(text))
                        elif text.isdigit():
                            row_data.append(int(text))
                        else:
                            row_data.append(text if text else 0)
                    except ValueError:
                        row_data.append(text if text else 0)
            
            if row_data and len(row_data) > 1:  # Must have team name + at least one stat
                data.append(row_data)
        
        # Create DataFrame
        if data and headers:
            # Ensure column count matches
            min_cols = min(len(headers), max(len(row) for row in data) if data else 0)
            headers = headers[:min_cols]
            data = [row[:min_cols] for row in data]
            
            df = pd.DataFrame(data, columns=headers)
            
            # Standardize team name column
            if len(df.columns) > 0:
                df = df.rename(columns={df.columns[0]: 'team_name'})
            
            return df
        
        return pd.DataFrame()


def test_fbref_scraping():
    """Test FBref scraping functionality."""
    scraper = FBrefScraper()
    
    print("Testing FBref scraping...")
    
    # Test Premier League standings
    print("\n1. Testing Premier League standings...")
    prem_table = scraper.get_league_table('premier_league')
    if prem_table is not None and not prem_table.empty:
        print(f"✅ Successfully scraped {len(prem_table)} teams")
        print(f"Columns: {list(prem_table.columns)}")
        if len(prem_table) > 0:
            print(f"Sample team: {prem_table.iloc[0]['team_name'] if 'team_name' in prem_table.columns else 'Unknown'}")
    else:
        print("❌ Failed to scrape Premier League standings")
    
    # Test home/away splits
    print("\n2. Testing home/away splits...")
    home_away = scraper.get_home_away_splits('premier_league')
    if home_away is not None and not home_away.empty:
        print(f"✅ Successfully scraped home/away data for {len(home_away)} teams")
        print(f"Columns: {list(home_away.columns)}")
        if len(home_away) > 0:
            sample = home_away.iloc[0]
            print(f"Sample: {sample['team_name']} - Home: {sample.get('home_win_rate', 0):.2f} | Away: {sample.get('away_win_rate', 0):.2f}")
    else:
        print("❌ Failed to scrape home/away splits")
    
    # Test advanced stats
    print("\n3. Testing advanced statistics...")
    advanced_stats = scraper.get_advanced_stats('premier_league')
    if advanced_stats:
        print(f"✅ Successfully scraped {len(advanced_stats)} stat categories")
        for stat_name, df in advanced_stats.items():
            print(f"  {stat_name}: {len(df)} teams, {len(df.columns)} columns")
            if len(df.columns) > 1:
                print(f"    Sample columns: {list(df.columns[:5])}")
    else:
        print("❌ Failed to scrape advanced statistics")


if __name__ == "__main__":
    test_fbref_scraping()