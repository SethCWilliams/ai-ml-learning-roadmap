"""Main prediction pipeline for soccer match outcomes."""

import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any

from .data.espn_client import ESPNSoccerClient
from .models.feature_engineering import MatchFeatureEngineer
from .models.predictor import MatchPredictor, MatchPrediction

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SoccerMatchPredictor:
    """Main class for predicting soccer match outcomes."""
    
    def __init__(self, recent_form_weight: float = 0.7, model_type: str = "rule_based"):
        """
        Initialize the soccer match predictor.
        
        Args:
            recent_form_weight: Weight given to recent form vs season stats (0.7 = 70% recent)
            model_type: Type of prediction model ("rule_based" or "ml")
        """
        self.espn_client = ESPNSoccerClient()
        self.feature_engineer = MatchFeatureEngineer(self.espn_client, recent_form_weight)
        self.predictor = MatchPredictor(model_type)
        
        logger.info(f"Initialized predictor with {recent_form_weight:.1%} recent form weight")
    
    def predict_date(self, date: str, league: str = "eng.1") -> List[MatchPrediction]:
        """
        Predict outcomes for all matches on a given date.
        
        Args:
            date: Date in YYYYMMDD format (e.g., "20240721")
            league: League code ("eng.1" for Premier League, "usa.1" for MLS)
        
        Returns:
            List of MatchPrediction objects with probabilities and analysis
        """
        logger.info(f"Predicting matches for {date} in league {league}")
        
        try:
            # Generate features for all matches on the date
            match_features = self.feature_engineer.generate_features_for_date(date, league)
            
            if not match_features:
                logger.warning(f"No fixtures found for {date} in {league}")
                return []
            
            # Generate predictions for all matches
            predictions = self.predictor.predict_matches(match_features)
            
            logger.info(f"Generated {len(predictions)} predictions for {date}")
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to predict matches for {date}: {e}")
            raise
    
    def predict_fixture(self, fixture_id: str, league: str = "eng.1") -> MatchPrediction:
        """
        Predict outcome for a specific fixture.
        
        Args:
            fixture_id: ESPN fixture ID
            league: League code
        
        Returns:
            MatchPrediction for the specific fixture
        """
        # This would require additional ESPN API endpoint for single fixture
        # For now, we'll implement via date-based search
        raise NotImplementedError("Single fixture prediction not yet implemented")
    
    def format_predictions(self, predictions: List[MatchPrediction], detailed: bool = False) -> str:
        """
        Format predictions for display.
        
        Args:
            predictions: List of match predictions
            detailed: Include detailed analysis
        
        Returns:
            Formatted string with predictions
        """
        if not predictions:
            return "No matches found for the specified date."
        
        output = []
        output.append(f"SOCCER MATCH PREDICTIONS")
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("=" * 60)
        
        for i, pred in enumerate(predictions, 1):
            output.append(f"\n{i}. {pred.home_team} vs {pred.away_team}")
            output.append(f"   Date: {pred.match_date}")
            output.append(f"   Predicted: {pred.predicted_outcome} ({pred.confidence:.1%} confidence)")
            
            # Probabilities
            output.append(f"   Probabilities:")
            output.append(f"     Home Win: {pred.prob_home_win:.1%}")
            output.append(f"     Draw:     {pred.prob_draw:.1%}")
            output.append(f"     Away Win: {pred.prob_away_win:.1%}")
            
            if detailed:
                output.append(f"   Expected Goals: {pred.expected_goals_home:.1f} - {pred.expected_goals_away:.1f}")
                output.append(f"   Key Factors:")
                for factor in pred.key_factors:
                    output.append(f"     • {factor}")
        
        return "\n".join(output)


def main():
    """Command-line interface for the soccer match predictor."""
    parser = argparse.ArgumentParser(description="Predict soccer match outcomes")
    parser.add_argument("date", help="Date in YYYYMMDD format (e.g., 20240721)")
    parser.add_argument(
        "--league", 
        default="eng.1", 
        choices=["eng.1", "usa.1"],
        help="League code (eng.1=Premier League, usa.1=MLS)"
    )
    parser.add_argument(
        "--detailed", 
        action="store_true", 
        help="Show detailed analysis"
    )
    parser.add_argument(
        "--form-weight", 
        type=float, 
        default=0.7, 
        help="Weight for recent form vs season stats (0.0-1.0)"
    )
    parser.add_argument(
        "--model", 
        choices=["rule_based", "ml"], 
        default="rule_based",
        help="Prediction model type"
    )
    
    args = parser.parse_args()
    
    # Validate date format
    try:
        datetime.strptime(args.date, "%Y%m%d")
    except ValueError:
        print("Error: Date must be in YYYYMMDD format (e.g., 20240721)")
        return 1
    
    # Validate form weight
    if not 0.0 <= args.form_weight <= 1.0:
        print("Error: Form weight must be between 0.0 and 1.0")
        return 1
    
    try:
        # Initialize predictor
        predictor = SoccerMatchPredictor(
            recent_form_weight=args.form_weight,
            model_type=args.model
        )
        
        # Generate predictions
        predictions = predictor.predict_date(args.date, args.league)
        
        # Display results
        output = predictor.format_predictions(predictions, detailed=args.detailed)
        print(output)
        
        return 0
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())