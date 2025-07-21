"""Team performance analysis with weighted form calculation."""

import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TeamPerformanceMetrics:
    """Standardized team performance metrics."""
    team_id: str
    team_name: str
    
    # Season-wide metrics
    season_win_rate: float
    season_points_per_game: float
    season_goals_for_per_game: float
    season_goals_against_per_game: float
    season_goal_difference_per_game: float
    
    # Recent form metrics (last 5 games)
    recent_win_rate: float
    recent_points_per_game: float
    recent_goals_for_per_game: float
    recent_goals_against_per_game: float
    recent_goal_difference_per_game: float
    
    # Weighted combined metrics (recent form weighted more heavily)
    weighted_win_rate: float
    weighted_points_per_game: float
    weighted_goals_for_per_game: float
    weighted_goals_against_per_game: float
    weighted_goal_difference_per_game: float
    
    # Form trend indicators
    form_trend: str  # "improving", "declining", "stable"
    recent_form_string: str  # e.g., "WWLWD"


class TeamPerformanceAnalyzer:
    """Analyzes team performance with weighted form calculation."""
    
    def __init__(self, recent_form_weight: float = 0.7):
        """
        Initialize performance analyzer.
        
        Args:
            recent_form_weight: Weight given to recent form vs season (0.7 = 70% recent, 30% season)
        """
        self.recent_form_weight = recent_form_weight
        self.season_weight = 1.0 - recent_form_weight
    
    def analyze_team_performance(
        self, 
        season_stats: Dict[str, Any], 
        recent_form: List[Dict[str, Any]]
    ) -> TeamPerformanceMetrics:
        """
        Analyze team performance combining season stats and recent form.
        
        Args:
            season_stats: Team's season statistics from ESPN
            recent_form: List of recent match results
        
        Returns:
            TeamPerformanceMetrics with weighted calculations
        """
        logger.info(f"Analyzing performance for team {season_stats.get('name')}")
        
        # Calculate season metrics
        season_metrics = self._calculate_season_metrics(season_stats)
        
        # Calculate recent form metrics
        recent_metrics = self._calculate_recent_form_metrics(recent_form)
        
        # Calculate weighted combined metrics
        weighted_metrics = self._calculate_weighted_metrics(season_metrics, recent_metrics)
        
        # Analyze form trend
        form_trend = self._analyze_form_trend(recent_form)
        form_string = self._get_form_string(recent_form)
        
        return TeamPerformanceMetrics(
            team_id=season_stats.get('team_id'),
            team_name=season_stats.get('name'),
            
            # Season metrics
            season_win_rate=season_metrics['win_rate'],
            season_points_per_game=season_metrics['points_per_game'],
            season_goals_for_per_game=season_metrics['goals_for_per_game'],
            season_goals_against_per_game=season_metrics['goals_against_per_game'],
            season_goal_difference_per_game=season_metrics['goal_difference_per_game'],
            
            # Recent form metrics
            recent_win_rate=recent_metrics['win_rate'],
            recent_points_per_game=recent_metrics['points_per_game'],
            recent_goals_for_per_game=recent_metrics['goals_for_per_game'],
            recent_goals_against_per_game=recent_metrics['goals_against_per_game'],
            recent_goal_difference_per_game=recent_metrics['goal_difference_per_game'],
            
            # Weighted metrics
            weighted_win_rate=weighted_metrics['win_rate'],
            weighted_points_per_game=weighted_metrics['points_per_game'],
            weighted_goals_for_per_game=weighted_metrics['goals_for_per_game'],
            weighted_goals_against_per_game=weighted_metrics['goals_against_per_game'],
            weighted_goal_difference_per_game=weighted_metrics['goal_difference_per_game'],
            
            # Form analysis
            form_trend=form_trend,
            recent_form_string=form_string,
        )
    
    def _calculate_season_metrics(self, season_stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate normalized season performance metrics."""
        wins = season_stats.get('wins', 0)
        losses = season_stats.get('losses', 0)
        draws = season_stats.get('draws', 0)
        goals_for = season_stats.get('goals_for', 0)
        goals_against = season_stats.get('goals_against', 0)
        points = season_stats.get('points', 0)
        
        total_games = wins + losses + draws
        
        if total_games == 0:
            logger.warning(f"No games played for team {season_stats.get('name')}")
            return self._empty_metrics()
        
        return {
            'win_rate': wins / total_games,
            'points_per_game': points / total_games,
            'goals_for_per_game': goals_for / total_games,
            'goals_against_per_game': goals_against / total_games,
            'goal_difference_per_game': (goals_for - goals_against) / total_games,
        }
    
    def _calculate_recent_form_metrics(self, recent_form: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate metrics from recent form data."""
        if not recent_form:
            logger.warning("No recent form data available")
            return self._empty_metrics()
        
        total_games = len(recent_form)
        wins = sum(1 for match in recent_form if match['result'] == 'W')
        total_points = sum(match['points'] for match in recent_form)
        total_goals_for = sum(match['goals_for'] for match in recent_form)
        total_goals_against = sum(match['goals_against'] for match in recent_form)
        
        return {
            'win_rate': wins / total_games,
            'points_per_game': total_points / total_games,
            'goals_for_per_game': total_goals_for / total_games,
            'goals_against_per_game': total_goals_against / total_games,
            'goal_difference_per_game': (total_goals_for - total_goals_against) / total_games,
        }
    
    def _calculate_weighted_metrics(
        self, 
        season_metrics: Dict[str, float], 
        recent_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate weighted combination of season and recent form metrics."""
        weighted = {}
        
        for metric in season_metrics.keys():
            weighted[metric] = (
                self.season_weight * season_metrics[metric] + 
                self.recent_form_weight * recent_metrics[metric]
            )
        
        return weighted
    
    def _analyze_form_trend(self, recent_form: List[Dict[str, Any]]) -> str:
        """Analyze whether team form is improving, declining, or stable."""
        if len(recent_form) < 3:
            return "insufficient_data"
        
        # Split recent form into first half and second half
        mid_point = len(recent_form) // 2
        early_form = recent_form[mid_point:]  # Earlier games
        late_form = recent_form[:mid_point]   # More recent games
        
        early_points = sum(match['points'] for match in early_form) / len(early_form)
        late_points = sum(match['points'] for match in late_form) / len(late_form)
        
        diff = late_points - early_points
        
        if diff > 0.5:
            return "improving"
        elif diff < -0.5:
            return "declining"
        else:
            return "stable"
    
    def _get_form_string(self, recent_form: List[Dict[str, Any]]) -> str:
        """Generate form string (e.g., 'WWLWD') from recent matches."""
        return ''.join(match['result'] for match in recent_form)
    
    def _empty_metrics(self) -> Dict[str, float]:
        """Return empty metrics dictionary for edge cases."""
        return {
            'win_rate': 0.0,
            'points_per_game': 0.0,
            'goals_for_per_game': 0.0,
            'goals_against_per_game': 0.0,
            'goal_difference_per_game': 0.0,
        }
    
    def compare_teams(
        self, 
        home_metrics: TeamPerformanceMetrics, 
        away_metrics: TeamPerformanceMetrics
    ) -> Dict[str, Any]:
        """
        Compare two teams and generate features for prediction.
        
        Args:
            home_metrics: Home team performance metrics
            away_metrics: Away team performance metrics
        
        Returns:
            Dictionary with comparison features for ML model
        """
        return {
            # Weighted performance differences
            'weighted_win_rate_diff': home_metrics.weighted_win_rate - away_metrics.weighted_win_rate,
            'weighted_points_diff': home_metrics.weighted_points_per_game - away_metrics.weighted_points_per_game,
            'weighted_goals_for_diff': home_metrics.weighted_goals_for_per_game - away_metrics.weighted_goals_for_per_game,
            'weighted_goals_against_diff': home_metrics.weighted_goals_against_per_game - away_metrics.weighted_goals_against_per_game,
            'weighted_goal_difference_diff': home_metrics.weighted_goal_difference_per_game - away_metrics.weighted_goal_difference_per_game,
            
            # Recent form differences
            'recent_win_rate_diff': home_metrics.recent_win_rate - away_metrics.recent_win_rate,
            'recent_points_diff': home_metrics.recent_points_per_game - away_metrics.recent_points_per_game,
            'recent_goals_diff': home_metrics.recent_goals_for_per_game - away_metrics.recent_goals_for_per_game,
            
            # Form trend indicators
            'home_form_improving': 1 if home_metrics.form_trend == 'improving' else 0,
            'home_form_declining': 1 if home_metrics.form_trend == 'declining' else 0,
            'away_form_improving': 1 if away_metrics.form_trend == 'improving' else 0,
            'away_form_declining': 1 if away_metrics.form_trend == 'declining' else 0,
            
            # Home advantage (implicit - home team gets slight boost)
            'home_advantage': 1,
            
            # Team strength ratings (0-1 scale)
            'home_strength': min(1.0, home_metrics.weighted_points_per_game / 3.0),
            'away_strength': min(1.0, away_metrics.weighted_points_per_game / 3.0),
        }