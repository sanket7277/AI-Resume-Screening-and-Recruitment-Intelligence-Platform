import os
import joblib
import numpy as np
import logging
from app.ml.feature_engineering import FeatureEngineer
from app.ml.train_model import ModelTrainer

logger = logging.getLogger(__name__)

class MLPredictor:
    """Uses serialized ML models to classify candidates and explain classification weights."""
    def __init__(self, model_dir=None):
        if not model_dir:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_dir = os.path.join(current_dir, '..', 'ml', 'models')
            
        self.model_dir = os.path.normpath(model_dir)
        self.feature_engineer = FeatureEngineer()
        
        self.model = None
        self.scaler = None
        self.encoder = None

    def _load_assets(self):
        """Lazy-loads model, scaler, and encoder files on prediction query."""
        if self.model is None:
            scaler_path = os.path.join(self.model_dir, 'feature_scaler.joblib')
            encoder_path = os.path.join(self.model_dir, 'label_encoder.joblib')
            model_path = os.path.join(self.model_dir, 'candidate_classifier.joblib')
            
            if not (os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(encoder_path)):
                # Auto train if missing (student friendly dev helper)
                logger.info("ML model assets not found. Initiating auto-training...")
                trainer = ModelTrainer(self.model_dir)
                trainer.train()
                
            try:
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.encoder = joblib.load(encoder_path)
            except Exception as e:
                logger.error(f"Failed to load ML assets: {e}")
                raise RuntimeError(f"ML engine initialization error: {e}")

    def predict_suitability(self, candidate_profile, job_description, match_result=None):
        """Predicts classification label (Highly Suitable, Suitable, etc.) and returns decision factors."""
        self._load_assets()
        
        # 1. Compile candidate features
        raw_features = self.feature_engineer.extract_features(candidate_profile, job_description, match_result)
        
        # 2. Scale features
        scaled_features = self.scaler.transform([raw_features])
        
        # 3. Predict class label and probability
        pred_idx = self.model.predict(scaled_features)[0]
        label = self.encoder.inverse_transform([pred_idx])[0]
        
        prob = 100.0
        if hasattr(self.model, "predict_proba"):
            prob = float(np.max(self.model.predict_proba(scaled_features)[0]) * 100.0)
            
        # 4. Generate decision feature explanations
        explanation = self._explain(raw_features, label)
        
        # Map label names cleanly
        display_label = label.replace('_', ' ').title()
        
        return {
            'prediction_label': display_label,
            'prediction_raw': label,
            'prediction_confidence': round(prob, 1),
            'feature_values': dict(zip(self.feature_engineer.get_feature_names(), raw_features.tolist())),
            'explanation': explanation
        }

    def _explain(self, raw_features, prediction):
        """Explain the classification decision based on feature weight bounds."""
        feature_names = self.feature_engineer.get_feature_names()
        f_dict = dict(zip(feature_names, raw_features.tolist()))
        
        reasons = []
        
        # Heuristic-based rule explanation backing the model weights
        if prediction == 'highly_suitable':
            reasons.append(f"Candidate matches {f_dict['skill_match_pct']:.1f}% of required skills.")
            if f_dict['years_experience'] >= 5.0:
                reasons.append(f"Strong industry tenure of {f_dict['years_experience']:.1f} years.")
            if f_dict['education_level'] >= 2:
                reasons.append("Higher academic credentials (Master's or PhD) aligned with position constraints.")
            if f_dict['semantic_similarity'] >= 0.70:
                reasons.append("High semantic syntax overlap showing strong candidate job context understanding.")
        elif prediction == 'suitable':
            reasons.append(f"Solid skill matching profile ({f_dict['skill_match_pct']:.1f}%).")
            if f_dict['years_experience'] > 2.0:
                reasons.append(f"Competent work experience length of {f_dict['years_experience']:.1f} years.")
            if f_dict['num_projects'] > 2:
                reasons.append(f"Active project portfolio containing {int(f_dict['num_projects'])} highlights.")
        elif prediction == 'average':
            reasons.append(f"Moderate skill overlap ({f_dict['skill_match_pct']:.1f}%).")
            if f_dict['years_experience'] < 2.0:
                reasons.append("Junior experience length makes candidate suit entry level roles better.")
            if f_dict['num_skills'] < 8:
                reasons.append("Limited tech stack listed. Expanding key skills is advised.")
        else: # not_suitable
            if f_dict['skill_match_pct'] < 30.0:
                reasons.append(f"Critically low core skill alignment ({f_dict['skill_match_pct']:.1f}%).")
            if f_dict['years_experience'] == 0.0:
                reasons.append("Candidate lists no professional work experience history.")
            if f_dict['semantic_similarity'] < 0.40:
                reasons.append("Resume contains unrelated vocabulary themes not matching job objectives.")

        # Default fallback
        if not reasons:
            reasons.append("Model evaluated candidate experience, skills, and semantic scores as average overall.")

        return {
            'reasons': reasons,
            'top_factor': "Skill Match %" if f_dict['skill_match_pct'] > 50 else "Experience Gap"
        }

    def get_model_info(self):
        """Retrieve model type and status metadata."""
        try:
            self._load_assets()
            return {
                'model_type': type(self.model).__name__,
                'is_trained': True,
                'num_features': len(self.feature_engineer.get_feature_names()),
                'classes': self.encoder.classes_.tolist()
            }
        except Exception:
            return {
                'is_trained': False
            }
