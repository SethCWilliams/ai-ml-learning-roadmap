"""Match outcome prediction model."""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import logging

from .feature_engineering import MatchFeatures

logger = logging.getLogger(__name__)


@dataclass
class MatchPrediction:
    """Prediction results for a single match."""
    fixture_id: str
    home_team: str
    away_team: str
    match_date: str
    
    # Probabilities (should sum to 1.0)
    prob_home_win: float
    prob_draw: float
    prob_away_win: float
    
    # Most likely outcome
    predicted_outcome: str  # "Home Win", "Draw", "Away Win"
    confidence: float
    
    # Additional insights
    key_factors: List[str]
    expected_goals_home: float
    expected_goals_away: float


class MatchPredictor:
    """Predicts match outcomes using team performance features."""
    
    def __init__(self, model_type: str = "rule_based"):
        """
        Initialize match predictor.
        
        Args:
            model_type: Type of prediction model ("rule_based" or "ml")
        """
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        if model_type == "ml":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            self.scaler = StandardScaler()
    
    def predict_match(self, match_features: MatchFeatures) -> MatchPrediction:
        """
        Predict outcome for a single match.
        
        Args:
            match_features: MatchFeatures object with engineered features
        
        Returns:
            MatchPrediction with probabilities and analysis
        """
        if self.model_type == "rule_based":
            return self._rule_based_prediction(match_features)
        else:
            return self._ml_prediction(match_features)
    
    def predict_matches(self, matches_features: List[MatchFeatures]) -> List[MatchPrediction]:
        """Predict outcomes for multiple matches."""
        predictions = []
        
        for match_features in matches_features:
            try:
                prediction = self.predict_match(match_features)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Failed to predict match {match_features.fixture_id}: {e}")
                continue
        
        return predictions
    
    def _rule_based_prediction(self, match_features: MatchFeatures) -> MatchPrediction:
        """
        Rule-based prediction using engineered features.
        This provides immediate functionality while we build ML training data.
        """
        features = match_features.features
        
        # Key factors for prediction
        home_strength = features.get('home_strength', 0.5)
        away_strength = features.get('away_strength', 0.5)
        weighted_points_diff = features.get('weighted_points_diff', 0.0)
        recent_form_diff = features.get('recent_points_diff', 0.0)
        home_advantage = 0.1  # Standard home advantage
        
        # Calculate base probabilities using team strengths and form
        strength_factor = weighted_points_diff / 3.0  # Normalize to -1 to 1 range
        form_factor = recent_form_diff / 3.0
        
        # Combine factors with weights
        combined_factor = (
            0.4 * strength_factor +     # 40% season performance
            0.4 * form_factor +         # 40% recent form
            0.2 * home_advantage        # 20% home advantage
        )
        
        # Convert to probabilities using logistic-like function
        # Map combined_factor (-1 to 1) to probabilities
        if combined_factor > 0.3:
            # Home favored
            prob_home = 0.5 + 0.3 * min(1.0, combined_factor / 0.5)
            prob_away = 0.3 - 0.1 * min(1.0, combined_factor / 0.5)
            prob_draw = 1.0 - prob_home - prob_away
        elif combined_factor < -0.3:
            # Away favored
            prob_away = 0.5 + 0.3 * min(1.0, abs(combined_factor) / 0.5)
            prob_home = 0.3 - 0.1 * min(1.0, abs(combined_factor) / 0.5)
            prob_draw = 1.0 - prob_home - prob_away
        else:
            # Close match - higher draw probability
            prob_draw = 0.4 - 0.1 * abs(combined_factor) / 0.3
            prob_home = 0.35 + 0.05 * (combined_factor / 0.3)
            prob_away = 1.0 - prob_home - prob_draw
        
        # Ensure probabilities are valid
        prob_home = max(0.05, min(0.85, prob_home))
        prob_away = max(0.05, min(0.85, prob_away))
        prob_draw = max(0.05, min(0.80, prob_draw))
        
        # Normalize to sum to 1.0
        total = prob_home + prob_draw + prob_away
        prob_home /= total
        prob_draw /= total
        prob_away /= total
        
        # Determine most likely outcome
        max_prob = max(prob_home, prob_draw, prob_away)
        if max_prob == prob_home:
            predicted_outcome = "Home Win"
            confidence = prob_home
        elif max_prob == prob_away:
            predicted_outcome = "Away Win"
            confidence = prob_away
        else:
            predicted_outcome = "Draw"
            confidence = prob_draw
        
        # Generate key factors
        key_factors = self._generate_prediction_factors(features, match_features)
        
        return MatchPrediction(
            fixture_id=match_features.fixture_id,
            home_team=match_features.home_team,
            away_team=match_features.away_team,
            match_date=match_features.match_date,
            prob_home_win=round(prob_home, 3),
            prob_draw=round(prob_draw, 3),
            prob_away_win=round(prob_away, 3),
            predicted_outcome=predicted_outcome,
            confidence=round(confidence, 3),
            key_factors=key_factors,
            expected_goals_home=features.get('expected_total_goals', 2.5) * prob_home + 1.0,
            expected_goals_away=features.get('expected_total_goals', 2.5) * prob_away + 1.0,
        )
    
    def _ml_prediction(self, match_features: MatchFeatures) -> MatchPrediction:
        """ML-based prediction using trained model."""
        if self.model is None:
            raise ValueError("ML model not trained. Use train_model() first or switch to rule_based mode.")
        
        # Prepare features
        feature_vector = self._prepare_feature_vector(match_features.features)
        feature_vector_scaled = self.scaler.transform([feature_vector])
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(feature_vector_scaled)[0]
        
        # Map to home/draw/away (depends on how classes were encoded during training)
        prob_away, prob_draw, prob_home = probabilities  # Assuming alphabetical class order
        
        # Determine predicted outcome
        max_prob = max(prob_home, prob_draw, prob_away)
        if max_prob == prob_home:
            predicted_outcome = "Home Win"
            confidence = prob_home
        elif max_prob == prob_away:
            predicted_outcome = "Away Win"
            confidence = prob_away
        else:
            predicted_outcome = "Draw"
            confidence = prob_draw
        
        key_factors = self._generate_prediction_factors(match_features.features, match_features)
        
        return MatchPrediction(
            fixture_id=match_features.fixture_id,
            home_team=match_features.home_team,
            away_team=match_features.away_team,
            match_date=match_features.match_date,
            prob_home_win=round(prob_home, 3),
            prob_draw=round(prob_draw, 3),
            prob_away_win=round(prob_away, 3),
            predicted_outcome=predicted_outcome,
            confidence=round(confidence, 3),
            key_factors=key_factors,
            expected_goals_home=match_features.features.get('expected_total_goals', 2.5) * 0.55,
            expected_goals_away=match_features.features.get('expected_total_goals', 2.5) * 0.45,
        )
    
    def _generate_prediction_factors(self, features: Dict[str, float], match_features: MatchFeatures) -> List[str]:
        """Generate human-readable factors influencing the prediction."""
        factors = []
        
        # Team strength factors
        if features.get('weighted_points_diff', 0) > 0.5:
            factors.append(f"{match_features.home_team} stronger season performance")
        elif features.get('weighted_points_diff', 0) < -0.5:
            factors.append(f"{match_features.away_team} stronger season performance")
        
        # Recent form factors
        if features.get('recent_points_diff', 0) > 0.5:
            factors.append(f"{match_features.home_team} better recent form")
        elif features.get('recent_points_diff', 0) < -0.5:
            factors.append(f"{match_features.away_team} better recent form")
        
        # Form trend factors
        if features.get('home_form_improving', 0) == 1:
            factors.append(f"{match_features.home_team} improving form")
        if features.get('away_form_improving', 0) == 1:
            factors.append(f"{match_features.away_team} improving form")
        if features.get('home_form_declining', 0) == 1:
            factors.append(f"{match_features.home_team} declining form")
        if features.get('away_form_declining', 0) == 1:
            factors.append(f"{match_features.away_team} declining form")
        
        # Goal difference factors
        if features.get('weighted_goal_difference_diff', 0) > 0.5:
            factors.append(f"{match_features.home_team} much better goal difference")
        elif features.get('weighted_goal_difference_diff', 0) < -0.5:
            factors.append(f"{match_features.away_team} much better goal difference")
        
        # Home advantage
        factors.append("Home advantage factor")
        
        return factors[:5]  # Return top 5 factors
    
    def train_model(self, training_data: pd.DataFrame, target_column: str = 'result'):
        """
        Train ML model on historical match data.
        
        Args:
            training_data: DataFrame with features and results
            target_column: Column name containing match results ('Home Win', 'Draw', 'Away Win')
        """
        if self.model_type != "ml":
            raise ValueError("Model type must be 'ml' to train ML model")
        
        # Prepare features and target
        feature_columns = [col for col in training_data.columns 
                          if col not in ['fixture_id', 'home_team', 'away_team', 'match_date', target_column]]
        
        X = training_data[feature_columns]
        y = training_data[target_column]
        
        # Store feature names for consistency
        self.feature_names = feature_columns
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        logger.info(f"Model trained on {len(training_data)} matches with {len(feature_columns)} features")
    
    def _prepare_feature_vector(self, features: Dict[str, float]) -> List[float]:
        """Prepare feature vector for ML model prediction."""
        if self.feature_names is None:
            raise ValueError("Feature names not set. Train model first.")
        
        return [features.get(name, 0.0) for name in self.feature_names]
    
    def save_model(self, filepath: str):
        """Save trained model and scaler to disk."""
        if self.model is None:
            raise ValueError("No model to save. Train model first.")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model and scaler from disk."""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        
        logger.info(f"Model loaded from {filepath}")