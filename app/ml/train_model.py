import os
import joblib
import logging
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score
from app.ml.generate_dataset import SyntheticDataGenerator
from app.ml.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Orchestrates pipeline generation, model training, evaluation, and serialization."""
    def __init__(self, model_dir=None):
        if not model_dir:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_dir = os.path.join(current_dir, 'models')
            
        self.model_dir = os.path.normpath(model_dir)
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.scaler_path = os.path.join(self.model_dir, 'feature_scaler.joblib')
        self.encoder_path = os.path.join(self.model_dir, 'label_encoder.joblib')
        self.model_path = os.path.join(self.model_dir, 'candidate_classifier.joblib')
        
        self.feature_engineer = FeatureEngineer()

    def train(self, dataset_path=None, sample_count=1000):
        """Train models on synthetic data, evaluate accuracy/F1 metrics, and save best model."""
        # 1. Load or generate data
        if dataset_path and os.path.exists(dataset_path):
            logger.info(f"Loading training data from {dataset_path}")
            df = pd.read_csv(dataset_path)
        else:
            logger.info(f"Generating {sample_count} synthetic candidate data rows...")
            generator = SyntheticDataGenerator()
            df = generator.generate_candidates(n=sample_count)
            # Optionally save synthetic data for manual inspection
            csv_path = os.path.join(self.model_dir, 'synthetic_training_data.csv')
            generator.save_dataset(df, csv_path)
            
        # 2. Extract features and labels
        X, y = self.feature_engineer.prepare_training_data(df)
        
        # Encode string labels (highly_suitable, suitable, etc.)
        encoder = LabelEncoder()
        y_encoded = encoder.fit_transform(y)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 3. Train-test Split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # 4. Fit classifiers
        lr = LogisticRegression(multi_class='multinomial', max_iter=1000, random_state=42)
        rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        
        lr.fit(X_train, y_train)
        rf.fit(X_train, y_train)
        
        # 5. Evaluate models
        y_pred_lr = lr.predict(X_test)
        y_pred_rf = rf.predict(X_test)
        
        acc_lr = accuracy_score(y_test, y_pred_lr)
        acc_rf = accuracy_score(y_test, y_pred_rf)
        
        f1_lr = f1_score(y_test, y_pred_lr, average='weighted')
        f1_rf = f1_score(y_test, y_pred_rf, average='weighted')
        
        logger.info(f"Logistic Regression: Accuracy={acc_lr:.4f}, F1-Weighted={f1_lr:.4f}")
        logger.info(f"Random Forest: Accuracy={acc_rf:.4f}, F1-Weighted={f1_rf:.4f}")
        
        # Determine the winner
        if f1_rf >= f1_lr:
            best_model = rf
            model_type = "Random Forest Classifier"
            best_f1 = f1_rf
            best_acc = acc_rf
            y_pred_best = y_pred_rf
        else:
            best_model = lr
            model_type = "Logistic Regression"
            best_f1 = f1_lr
            best_acc = acc_lr
            y_pred_best = y_pred_lr

        # 6. Save assets
        joblib.dump(scaler, self.scaler_path)
        joblib.dump(encoder, self.encoder_path)
        joblib.dump(best_model, self.model_path)
        logger.info(f"Saved best model ({model_type}) to {self.model_path}")
        
        # Generate stats dictionary for UI visualization
        eval_report = classification_report(y_test, y_pred_best, target_names=encoder.classes_, output_dict=True)
        
        results = {
            'best_model_type': model_type,
            'accuracy': float(best_acc),
            'f1_score': float(best_f1),
            'feature_names': self.feature_engineer.get_feature_names(),
            'classification_report': eval_report,
            'classes': list(encoder.classes_),
            'feature_importances': list(best_model.feature_importances_) if hasattr(best_model, 'feature_importances_') else list(np.abs(best_model.coef_[0])),
            'logistic_regression_f1': float(f1_lr),
            'random_forest_f1': float(f1_rf)
        }
        
        return results

    def load_model(self):
        """Loads and returns model pipeline assets. Raises exception if missing."""
        if not (os.path.exists(self.model_path) and os.path.exists(self.scaler_path) and os.path.exists(self.encoder_path)):
            raise FileNotFoundError("Model assets are missing. Please run train() first.")
            
        model = joblib.load(self.model_path)
        scaler = joblib.load(self.scaler_path)
        encoder = joblib.load(self.encoder_path)
        
        return model, scaler, encoder
