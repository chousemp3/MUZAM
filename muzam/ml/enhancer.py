"""
Machine Learning Enhancement Module

Advanced ML algorithms to improve audio recognition accuracy
and reduce false positives.
"""

import numpy as np
import time
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass

# ML imports (would be installed via requirements)
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class MLModel:
    """ML model configuration and state"""
    model_type: str
    model: Optional[object] = None
    scaler: Optional[object] = None
    is_trained: bool = False
    accuracy: float = 0.0


class MLEnhancer:
    """
    Machine Learning enhancement for audio recognition
    
    Features:
    - False positive reduction
    - Confidence score improvement
    - Pattern learning from user feedback
    - Adaptive recognition optimization
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize ML enhancer
        
        Args:
            model_path: Path to pre-trained model
        """
        self.logger = logging.getLogger(__name__)
        self.models = {}
        
        if not SKLEARN_AVAILABLE:
            self.logger.warning("Scikit-learn not available. ML features disabled.")
            return
            
        # Initialize models
        self._init_models()
        
        # Load pre-trained model if available
        if model_path:
            self._load_model(model_path)
    
    def _init_models(self):
        """Initialize ML models"""
        if not SKLEARN_AVAILABLE:
            return
            
        # Confidence enhancement model
        self.models['confidence'] = MLModel(
            model_type='confidence',
            model=RandomForestClassifier(n_estimators=100, random_state=42),
            scaler=StandardScaler()
        )
        
        # Match quality model
        self.models['quality'] = MLModel(
            model_type='quality',
            model=MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42),
            scaler=StandardScaler()
        )
    
    def enhance_matches(self, matches: List, audio_data: np.ndarray) -> List:
        """
        Enhance recognition matches using ML
        
        Args:
            matches: List of recognition results
            audio_data: Original audio data
            
        Returns:
            Enhanced list of recognition results
        """
        if not SKLEARN_AVAILABLE or not matches:
            return matches
            
        try:
            # Extract features for ML enhancement
            features = self._extract_audio_features(audio_data)
            
            # Enhance each match
            enhanced_matches = []
            for match in matches:
                enhanced_match = self._enhance_single_match(match, features)
                enhanced_matches.append(enhanced_match)
            
            # Sort by enhanced confidence
            enhanced_matches.sort(key=lambda x: x.confidence, reverse=True)
            
            return enhanced_matches
            
        except Exception as e:
            self.logger.error(f"Error enhancing matches: {e}")
            return matches
    
    def _enhance_single_match(self, match, audio_features: np.ndarray):
        """Enhance a single match using ML models"""
        if not self.models['confidence'].is_trained:
            return match
            
        try:
            # Prepare features for ML model
            match_features = np.concatenate([
                audio_features,
                [match.confidence, match.fingerprint_matches, match.match_time]
            ]).reshape(1, -1)
            
            # Scale features
            scaled_features = self.models['confidence'].scaler.transform(match_features)
            
            # Predict enhanced confidence
            enhanced_confidence = self.models['confidence'].model.predict_proba(scaled_features)[0][1]
            
            # Update match confidence
            match.confidence = min(1.0, enhanced_confidence * 1.2)  # Boost good matches
            
            return match
            
        except Exception as e:
            self.logger.warning(f"Error enhancing single match: {e}")
            return match
    
    def _extract_audio_features(self, audio_data: np.ndarray) -> np.ndarray:
        """Extract ML features from audio data"""
        try:
            import librosa
            
            # Basic statistical features
            features = [
                np.mean(audio_data),
                np.std(audio_data),
                np.max(audio_data),
                np.min(audio_data),
                np.median(audio_data)
            ]
            
            # Spectral features
            if len(audio_data) > 1024:
                spectral_centroids = librosa.feature.spectral_centroid(y=audio_data)[0]
                features.extend([
                    np.mean(spectral_centroids),
                    np.std(spectral_centroids)
                ])
                
                # Zero crossing rate
                zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
                features.extend([
                    np.mean(zcr),
                    np.std(zcr)
                ])
            else:
                # Pad with zeros if audio too short
                features.extend([0.0, 0.0, 0.0, 0.0])
            
            return np.array(features)
            
        except Exception as e:
            self.logger.warning(f"Error extracting audio features: {e}")
            return np.zeros(9)  # Return default feature vector
    
    def train_from_feedback(self, feedback_data: List[Dict]):
        """
        Train models from user feedback
        
        Args:
            feedback_data: List of feedback dictionaries with features and labels
        """
        if not SKLEARN_AVAILABLE or not feedback_data:
            return
            
        try:
            # Prepare training data
            X, y = self._prepare_training_data(feedback_data)
            
            if len(X) < 10:  # Need minimum samples
                self.logger.warning("Insufficient training data for ML model")
                return
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train confidence model
            confidence_model = self.models['confidence']
            
            # Scale features
            confidence_model.scaler.fit(X_train)
            X_train_scaled = confidence_model.scaler.transform(X_train)
            X_test_scaled = confidence_model.scaler.transform(X_test)
            
            # Train model
            confidence_model.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            accuracy = confidence_model.model.score(X_test_scaled, y_test)
            confidence_model.accuracy = accuracy
            confidence_model.is_trained = True
            
            self.logger.info(f"ML model trained with accuracy: {accuracy:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error training ML model: {e}")
    
    def _prepare_training_data(self, feedback_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from feedback"""
        features_list = []
        labels_list = []
        
        for feedback in feedback_data:
            # Extract features
            features = [
                feedback.get('confidence', 0.0),
                feedback.get('match_count', 0),
                feedback.get('match_time', 0.0),
                feedback.get('audio_quality', 0.0),
                feedback.get('noise_level', 0.0)
            ]
            
            # Add audio features if available
            if 'audio_features' in feedback:
                features.extend(feedback['audio_features'])
            else:
                features.extend([0.0] * 9)  # Pad with zeros
            
            features_list.append(features)
            labels_list.append(1 if feedback.get('correct', False) else 0)
        
        return np.array(features_list), np.array(labels_list)
    
    def save_model(self, model_path: str):
        """Save trained models to disk"""
        if not SKLEARN_AVAILABLE:
            return
            
        try:
            import pickle
            
            model_data = {
                'models': self.models,
                'version': '1.0'
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
                
            self.logger.info(f"ML models saved to {model_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving ML models: {e}")
    
    def _load_model(self, model_path: str):
        """Load pre-trained models from disk"""
        if not SKLEARN_AVAILABLE:
            return
            
        try:
            import pickle
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.models = model_data['models']
            self.logger.info(f"ML models loaded from {model_path}")
            
        except Exception as e:
            self.logger.warning(f"Could not load ML models: {e}")
    
    def get_model_stats(self) -> Dict:
        """Get ML model statistics"""
        stats = {}
        
        for name, model in self.models.items():
            stats[name] = {
                'trained': model.is_trained,
                'accuracy': model.accuracy,
                'type': model.model_type
            }
        
        return stats
    
    def record_feedback(self, match_result, user_feedback: bool, audio_data: np.ndarray):
        """
        Record user feedback for model improvement
        
        Args:
            match_result: Recognition result
            user_feedback: True if correct, False if incorrect
            audio_data: Original audio data
        """
        try:
            # Extract features
            audio_features = self._extract_audio_features(audio_data)
            
            # Create feedback record
            feedback = {
                'confidence': match_result.confidence,
                'match_count': match_result.fingerprint_matches,
                'match_time': match_result.match_time,
                'audio_features': audio_features.tolist(),
                'correct': user_feedback,
                'timestamp': time.time()
            }
            
            # Store for training (could be database or file)
            self._store_feedback(feedback)
            
        except Exception as e:
            self.logger.error(f"Error recording feedback: {e}")
    
    def _store_feedback(self, feedback: Dict):
        """Store feedback for later training"""
        # Implementation would store to database or file
        # For now, just log it
        self.logger.info(f"Feedback recorded: {feedback['correct']}")
    
    def auto_tune_parameters(self, recognition_history: List[Dict]):
        """
        Automatically tune recognition parameters based on history
        
        Args:
            recognition_history: Historical recognition data
        """
        if not recognition_history:
            return
            
        try:
            # Analyze performance patterns
            success_rate = sum(1 for h in recognition_history if h.get('success', False)) / len(recognition_history)
            avg_confidence = np.mean([h.get('confidence', 0) for h in recognition_history])
            avg_time = np.mean([h.get('recognition_time', 0) for h in recognition_history])
            
            self.logger.info(f"Performance analysis: {success_rate:.2f} success rate, "
                           f"{avg_confidence:.2f} avg confidence, {avg_time:.2f}s avg time")
            
            # Auto-tune based on performance
            if success_rate < 0.8:
                self.logger.info("Low success rate detected - recommend parameter tuning")
            
        except Exception as e:
            self.logger.error(f"Error in auto-tuning: {e}")
