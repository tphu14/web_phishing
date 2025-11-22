"""
Prediction pipeline
"""

import pickle
import numpy as np
import pandas as pd
from tensorflow import keras
from pathlib import Path
from .features import extract_features
from .config import MODEL_FILES, EASY_THRESHOLD_LOW, EASY_THRESHOLD_HIGH

class PhishingPredictor:
    """Production phishing predictor"""
    
    def __init__(self, model_dir='models/'):
        """
        Initialize predictor
        
        Parameters:
        model_dir: str or Path - Directory chứa models
        """
        self.model_dir = Path(model_dir)
        self.load_models()
    
    def load_models(self):
        """Load tất cả models"""
        print("Loading models...")
        
        with open(self.model_dir / 'feature_names.pkl', 'rb') as f:
            self.feature_names = pickle.load(f)
        
        with open(self.model_dir / 'config.pkl', 'rb') as f:
            config = pickle.load(f)
            self.easy_low = config.get('easy_threshold_low', EASY_THRESHOLD_LOW)
            self.easy_high = config.get('easy_threshold_high', EASY_THRESHOLD_HIGH)
        
        with open(self.model_dir / 'lr_cascade.pkl', 'rb') as f:
            self.lr_model = pickle.load(f)
        
        with open(self.model_dir / 'xgboost_stacking.pkl', 'rb') as f:
            self.xgb_model = pickle.load(f)
        
        with open(self.model_dir / 'lightgbm_stacking.pkl', 'rb') as f:
            self.lgb_model = pickle.load(f)
        
        with open(self.model_dir / 'catboost_stacking.pkl', 'rb') as f:
            self.cat_model = pickle.load(f)
        
        self.nn_model = keras.models.load_model(
            self.model_dir / 'neural_network.h5',
            compile=False
        )
        
        with open(self.model_dir / 'meta_learner.pkl', 'rb') as f:
            self.meta_model = pickle.load(f)
        
        with open(self.model_dir / 'scaler.pkl', 'rb') as f:
            self.scaler = pickle.load(f)
        
        print(f"✅ Models loaded ({len(self.feature_names)} features)")
    
    def predict(self, url):
        """
        Predict single URL
        
        Parameters:
        url: str - URL to analyze
        
        Returns:
        dict - Prediction result
        """
        # Extract features
        features = extract_features(url)
        features_df = pd.DataFrame([features])[self.feature_names]
        features_scaled = self.scaler.transform(features_df)
        
        # Layer 1: LR Cascade
        lr_proba = self.lr_model.predict_proba(features_scaled)[0, 1]
        is_easy = (lr_proba < self.easy_low or lr_proba > self.easy_high)
        
        if is_easy:
            prediction = self.lr_model.predict(features_scaled)[0]
            final_proba = lr_proba
            method = 'cascade_lr'
            confidence = 'very_high' if (lr_proba < 0.05 or lr_proba > 0.95) else 'high'
        else:
            # Layer 2: Stacking
            xgb_prob = self.xgb_model.predict_proba(features_df)[0, 1]
            lgb_prob = self.lgb_model.predict_proba(features_df)[0, 1]
            cat_prob = self.cat_model.predict_proba(features_df)[0, 1]
            nn_prob = self.nn_model.predict(features_scaled, verbose=0).flatten()[0]
            
            meta_features = np.array([[xgb_prob, lgb_prob, cat_prob, nn_prob]])
            prediction = self.meta_model.predict(meta_features)[0]
            final_proba = self.meta_model.predict_proba(meta_features)[0, 1]
            
            method = 'stacking_ensemble'
            confidence = 'high' if (final_proba < 0.3 or final_proba > 0.7) else 'medium'
        
        return {
            'url': url,
            'prediction': 'phishing' if prediction == 1 else 'legitimate',
            'phishing_score': float(final_proba),
            'legitimate_score': float(1 - final_proba),
            'confidence': confidence,
            'method': method,
            'is_easy_case': is_easy,
            'risk_level': self._get_risk_level(final_proba),
            'features': features
        }
    
    def predict_batch(self, urls):
        """
        Predict multiple URLs
        
        Parameters:
        urls: list - List of URLs
        
        Returns:
        list - List of prediction results
        """
        results = []
        for url in urls:
            try:
                result = self.predict(url)
                results.append(result)
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e),
                    'prediction': 'error'
                })
        return results
    
    def _get_risk_level(self, proba):
        """Determine risk level"""
        if proba >= 0.9:
            return 'critical'
        elif proba >= 0.7:
            return 'high'
        elif proba >= 0.5:
            return 'medium'
        else:
            return 'low'