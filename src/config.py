"""
Cấu hình hệ thống
"""

import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Model files
MODEL_FILES = {
    'lr_cascade': MODELS_DIR / 'lr_cascade.pkl',
    'xgboost': MODELS_DIR / 'xgboost_stacking.pkl',
    'lightgbm': MODELS_DIR / 'lightgbm_stacking.pkl',
    'catboost': MODELS_DIR / 'catboost_stacking.pkl',
    'neural_network': MODELS_DIR / 'neural_network.h5',
    'meta_learner': MODELS_DIR / 'meta_learner.pkl',
    'scaler': MODELS_DIR / 'scaler.pkl',
    'feature_names': MODELS_DIR / 'feature_names.pkl',
    'config': MODELS_DIR / 'config.pkl'
}
# Cascade thresholds
EASY_THRESHOLD_LOW = 0.15
EASY_THRESHOLD_HIGH = 0.85

# Feature extraction
ANALYZE_CONTENT = False  # Set True nếu muốn crawl content
REQUEST_TIMEOUT = 3  # seconds

# Random state
RANDOM_STATE = 42