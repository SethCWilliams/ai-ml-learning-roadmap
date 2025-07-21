"""Feature engineering pipeline for match prediction."""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

from ..data.espn_client import ESPNSoccerClient
from .performance_analyzer import TeamPerformanceAnalyzer, TeamPerformanceMetrics

logger = logging.getLogger(__name__)


@dataclass
class MatchFeatures:
    """ML-ready features for a single match prediction."""
    fixture_id: str
    home_team: str
    away_team: str
    league: str
    match_date: str
    
    # Feature vector for ML model
    features: Dict[str, float]
    
    # Human-readable analysis
    home_team_metrics: TeamPerformanceMetrics
    away_team_metrics: TeamPerformanceMetrics
    match_analysis: Dict[str, Any]


class MatchFeatureEngineer:
    """Generates ML features for match prediction."""
    
    def __init__(self, espn_client: ESPNSoccerClient = None, recent_form_weight: float = 0.7):
        """
        Initialize feature engineer.
        
        Args:
            espn_client: ESPN API client (will create new one if None)
            recent_form_weight: Weight for recent form vs season stats
        """
        self.espn_client = espn_client or ESPNSoccerClient()
        self.performance_analyzer = TeamPerformanceAnalyzer(recent_form_weight)
    
    def generate_match_features(self, fixture: Dict[str, Any], league: str = "eng.1") -> MatchFeatures:
        """
        Generate ML features for a single fixture.
        
        Args:
            fixture: Fixture data from ESPN
            league: League code
        
        Returns:
            MatchFeatures object with ML-ready feature vector
        """
        home_team_id = fixture["home_team"]["id"]
        away_team_id = fixture["away_team"]["id"]
        
        logger.info(f"Generating features for {fixture['home_team']['name']} vs {fixture['away_team']['name']}")
        logger.debug(f"Home team ID: {home_team_id} (type: {type(home_team_id)})")
        logger.debug(f"Away team ID: {away_team_id} (type: {type(away_team_id)})")
        
        # Get team performance data
        home_metrics = self._get_team_performance(home_team_id, league)
        away_metrics = self._get_team_performance(away_team_id, league)
        
        # Generate comparison features
        comparison_features = self.performance_analyzer.compare_teams(home_metrics, away_metrics)
        
        # Add additional contextual features
        contextual_features = self._generate_contextual_features(fixture, home_metrics, away_metrics)
        
        # Combine all features
        all_features = {**comparison_features, **contextual_features}
        
        # Generate match analysis for human interpretation
        match_analysis = self._generate_match_analysis(fixture, home_metrics, away_metrics)
        
        return MatchFeatures(
            fixture_id=fixture["id"],
            home_team=fixture["home_team"]["name"],
            away_team=fixture["away_team"]["name"],
            league=league,
            match_date=fixture["date"],
            features=all_features,
            home_team_metrics=home_metrics,
            away_team_metrics=away_metrics,
            match_analysis=match_analysis
        )
    
    def generate_features_for_date(self, date: str, league: str = "eng.1") -> List[MatchFeatures]:
        """
        Generate features for all fixtures on a given date.
        
        Args:
            date: Date in YYYYMMDD format
            league: League code
        
        Returns:
            List of MatchFeatures for all fixtures on the date
        """
        logger.info(f"Generating features for all fixtures on {date}")
        
        # Get fixtures for the date
        fixtures = self.espn_client.get_fixtures_by_date(date, league)
        
        # Generate features for each fixture
        match_features = []
        for fixture in fixtures:
            try:
                features = self.generate_match_features(fixture, league)
                match_features.append(features)
            except Exception as e:
                logger.error(f"Failed to generate features for fixture {fixture.get('id')}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                continue
        
        logger.info(f"Generated features for {len(match_features)} matches")
        return match_features
    
    def _get_team_performance(self, team_id: str, league: str) -> TeamPerformanceMetrics:
        """Get comprehensive team performance metrics."""
        try:
            logger.debug(f"Getting performance for team {team_id} in league {league}")
            
            # Get season stats
            season_stats = self.espn_client.get_team_season_stats(team_id, league)
            logger.debug(f"Season stats keys: {list(season_stats.keys()) if isinstance(season_stats, dict) else type(season_stats)}")
            
            # Get recent form (last 5 matches)
            recent_form = self.espn_client.get_team_recent_form(team_id, league, games=5)
            logger.debug(f"Recent form count: {len(recent_form) if recent_form else 0}")
            
            # Analyze performance
            return self.performance_analyzer.analyze_team_performance(season_stats, recent_form)
            
        except Exception as e:
            logger.error(f"Failed to get performance data for team {team_id}: {e}")
            # Return empty metrics as fallback
            return self._create_empty_metrics(team_id, "Unknown Team")
    
    def _generate_contextual_features(
        self, 
        fixture: Dict[str, Any], 
        home_metrics: TeamPerformanceMetrics, 
        away_metrics: TeamPerformanceMetrics
    ) -> Dict[str, float]:
        """Generate additional contextual features for the match."""
        
        # Match timing features (if available)
        contextual = {
            # Combined team strength indicator
            'combined_team_strength': (home_metrics.weighted_points_per_game + away_metrics.weighted_points_per_game) / 2,
            
            # Goal expectation features
            'expected_total_goals': home_metrics.weighted_goals_for_per_game + away_metrics.weighted_goals_for_per_game,
            'home_defensive_strength': 3.0 - home_metrics.weighted_goals_against_per_game,  # Inverse of goals conceded
            'away_defensive_strength': 3.0 - away_metrics.weighted_goals_against_per_game,
            
            # Form momentum
            'home_recent_form_points': home_metrics.recent_points_per_game,
            'away_recent_form_points': away_metrics.recent_points_per_game,
            
            # Performance consistency (difference between season and recent form)
            'home_form_consistency': abs(home_metrics.season_points_per_game - home_metrics.recent_points_per_game),
            'away_form_consistency': abs(away_metrics.season_points_per_game - away_metrics.recent_points_per_game),
            
            # Offensive vs defensive balance
            'home_attack_defense_ratio': home_metrics.weighted_goals_for_per_game / max(0.1, home_metrics.weighted_goals_against_per_game),
            'away_attack_defense_ratio': away_metrics.weighted_goals_for_per_game / max(0.1, away_metrics.weighted_goals_against_per_game),
        }
        
        return contextual
    
    def _generate_match_analysis(
        self, 
        fixture: Dict[str, Any], 
        home_metrics: TeamPerformanceMetrics, 
        away_metrics: TeamPerformanceMetrics
    ) -> Dict[str, Any]:
        """Generate human-readable match analysis."""
        
        # Determine likely outcome based on weighted metrics
        home_advantage = 0.1  # Small home advantage
        home_strength = home_metrics.weighted_points_per_game + home_advantage
        away_strength = away_metrics.weighted_points_per_game
        
        strength_diff = home_strength - away_strength
        
        if strength_diff > 0.5:
            predicted_outcome = "Home Win"
            confidence = min(0.9, 0.6 + abs(strength_diff) * 0.2)
        elif strength_diff < -0.5:
            predicted_outcome = "Away Win"
            confidence = min(0.9, 0.6 + abs(strength_diff) * 0.2)
        else:
            predicted_outcome = "Draw"
            confidence = 0.4 + (0.5 - abs(strength_diff)) * 0.3
        
        return {
            'predicted_outcome': predicted_outcome,
            'confidence': round(confidence, 3),
            'home_form_trend': home_metrics.form_trend,
            'away_form_trend': away_metrics.form_trend,
            'home_recent_form': home_metrics.recent_form_string,
            'away_recent_form': away_metrics.recent_form_string,
            'key_factors': self._identify_key_factors(home_metrics, away_metrics),
            'expected_goals_home': round(home_metrics.weighted_goals_for_per_game, 2),
            'expected_goals_away': round(away_metrics.weighted_goals_for_per_game, 2),
        }
    
    def _identify_key_factors(
        self, 
        home_metrics: TeamPerformanceMetrics, 
        away_metrics: TeamPerformanceMetrics
    ) -> List[str]:
        """Identify key factors that might influence the match outcome."""
        factors = []
        
        # Form analysis
        if home_metrics.form_trend == "improving":
            factors.append(f"{home_metrics.team_name} improving form")
        elif home_metrics.form_trend == "declining":
            factors.append(f"{home_metrics.team_name} declining form")
            
        if away_metrics.form_trend == "improving":
            factors.append(f"{away_metrics.team_name} improving form")
        elif away_metrics.form_trend == "declining":
            factors.append(f"{away_metrics.team_name} declining form")
        
        # Performance differences
        if abs(home_metrics.weighted_points_per_game - away_metrics.weighted_points_per_game) > 1.0:
            stronger_team = home_metrics.team_name if home_metrics.weighted_points_per_game > away_metrics.weighted_points_per_game else away_metrics.team_name
            factors.append(f"{stronger_team} significantly stronger")
        
        # Recent form vs season performance
        if abs(home_metrics.recent_points_per_game - home_metrics.season_points_per_game) > 0.8:
            if home_metrics.recent_points_per_game > home_metrics.season_points_per_game:
                factors.append(f"{home_metrics.team_name} recent form above season average")
            else:
                factors.append(f"{home_metrics.team_name} recent form below season average")
        
        if abs(away_metrics.recent_points_per_game - away_metrics.season_points_per_game) > 0.8:
            if away_metrics.recent_points_per_game > away_metrics.season_points_per_game:
                factors.append(f"{away_metrics.team_name} recent form above season average")
            else:
                factors.append(f"{away_metrics.team_name} recent form below season average")
        
        return factors[:5]  # Limit to top 5 factors
    
    def _create_empty_metrics(self, team_id: str, team_name: str) -> TeamPerformanceMetrics:
        """Create empty metrics for error handling."""
        return TeamPerformanceMetrics(
            team_id=team_id,
            team_name=team_name,
            season_win_rate=0.0,
            season_points_per_game=0.0,
            season_goals_for_per_game=0.0,
            season_goals_against_per_game=0.0,
            season_goal_difference_per_game=0.0,
            recent_win_rate=0.0,
            recent_points_per_game=0.0,
            recent_goals_for_per_game=0.0,
            recent_goals_against_per_game=0.0,
            recent_goal_difference_per_game=0.0,
            weighted_win_rate=0.0,
            weighted_points_per_game=0.0,
            weighted_goals_for_per_game=0.0,
            weighted_goals_against_per_game=0.0,
            weighted_goal_difference_per_game=0.0,
            form_trend="unknown",
            recent_form_string="",
        )
    
    def features_to_dataframe(self, match_features_list: List[MatchFeatures]) -> pd.DataFrame:
        """Convert list of MatchFeatures to pandas DataFrame for ML model."""
        data = []
        
        for match_features in match_features_list:
            row = {
                'fixture_id': match_features.fixture_id,
                'home_team': match_features.home_team,
                'away_team': match_features.away_team,
                'league': match_features.league,
                'match_date': match_features.match_date,
                **match_features.features
            }
            data.append(row)
        
        return pd.DataFrame(data)