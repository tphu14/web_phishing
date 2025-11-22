"""
Script training tất cả models
Usage: python scripts/train_models.py --data data/processed/features.csv --output models/
"""

import argparse
import pandas as pd
import numpy as np
import pickle
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
from tensorflow import keras
from tensorflow.keras import layers, callbacks
from imblearn.over_sampling import SMOTE

from src.config import EASY_THRESHOLD_LOW, EASY_THRESHOLD_HIGH, RANDOM_STATE

def train_cascade_stacking(data_path, output_dir):
    """Train Cascade + Stacking models"""
    
    print(f"\n{'='*70}")
    print("TRAINING CASCADE + STACKING MODELS")
    print(f"{'='*70}\n")
    
    # Load data
    print(f"📂 Loading data: {data_path}")
    df = pd.read_csv(data_path)
    
    non_feature_cols = ['url', 'class']
    feature_names = [col for col in df.columns if col not in non_feature_cols]
    
    X = df[feature_names]
    y = df['class']
    
    # Convert labels
    y = y.map({1: 0, -1: 1})
    
    print(f"📊 Dataset: {X.shape}")
    print(f"   Features: {len(feature_names)}")
    print(f"   Legitimate: {sum(y==0):,}")
    print(f"   Phishing: {sum(y==1):,}")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    
    # SMOTE if needed
    imbalance_ratio = sum(y_train==1) / sum(y_train==0)
    if imbalance_ratio < 0.5 or imbalance_ratio > 2.0:
        print("\n⚖️ Applying SMOTE...")
        smote = SMOTE(random_state=RANDOM_STATE)
        X_train, y_train = smote.fit_resample(X_train, y_train)
    
    # Scale
    print("\n📏 Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # ===== LAYER 1: LR CASCADE =====
    print(f"\n{'='*60}")
    print("🎯 LAYER 1: LOGISTIC REGRESSION")
    print(f"{'='*60}")
    
    lr_model = LogisticRegression(
        random_state=RANDOM_STATE,
        max_iter=2000,
        C=0.5,
        class_weight='balanced',
        solver='saga'
    )
    
    # CV
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(lr_model, X_train_scaled, y_train, cv=cv, scoring='f1')
    print(f"CV F1: {cv_scores.mean():.6f} (±{cv_scores.std():.6f})")
    
    # Train
    lr_model.fit(X_train_scaled, y_train)
    
    lr_train_proba = lr_model.predict_proba(X_train_scaled)[:, 1]
    lr_test_pred = lr_model.predict(X_test_scaled)
    lr_test_proba = lr_model.predict_proba(X_test_scaled)[:, 1]
    
    print(f"Test Accuracy: {accuracy_score(y_test, lr_test_pred):.6f}")
    print(f"Test F1: {f1_score(y_test, lr_test_pred):.6f}")
    
    # Split easy/hard
    easy_train_mask = (lr_train_proba < EASY_THRESHOLD_LOW) | (lr_train_proba > EASY_THRESHOLD_HIGH)
    hard_train_mask = ~easy_train_mask
    
    X_hard_train = X_train_scaled[hard_train_mask]
    y_hard_train = y_train.iloc[hard_train_mask] if isinstance(y_train, pd.Series) else y_train[hard_train_mask]
    
    print(f"\nEasy cases: {easy_train_mask.sum():,} ({easy_train_mask.sum()/len(X_train)*100:.1f}%)")
    print(f"Hard cases: {hard_train_mask.sum():,} ({hard_train_mask.sum()/len(X_train)*100:.1f}%)")
    
    # ===== LAYER 2: STACKING =====
    print(f"\n{'='*60}")
    print("🚀 LAYER 2: STACKING ENSEMBLE")
    print(f"{'='*60}")
    
    # Split for meta
    X_train_base, X_val_meta, y_train_base, y_val_meta = train_test_split(
        X_hard_train, y_hard_train,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y_hard_train
    )
    
    print(f"Base train: {X_train_base.shape}")
    print(f"Meta val: {X_val_meta.shape}")
    
    # XGBoost
    print("\n🌳 Training XGBoost...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.05,
        random_state=RANDOM_STATE,
        eval_metric='logloss',
        use_label_encoder=False
    )
    xgb_model.fit(X_train_base, y_train_base, verbose=False)
    
    xgb_train_proba = xgb_model.predict_proba(X_train_base)[:, 1]
    xgb_val_proba = xgb_model.predict_proba(X_val_meta)[:, 1]
    
    # LightGBM
    print("💡 Training LightGBM...")
    lgb_model = lgb.LGBMClassifier(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.05,
        random_state=RANDOM_STATE,
        verbose=-1
    )
    lgb_model.fit(X_train_base, y_train_base)
    
    lgb_train_proba = lgb_model.predict_proba(X_train_base)[:, 1]
    lgb_val_proba = lgb_model.predict_proba(X_val_meta)[:, 1]
    
    # CatBoost
    print("🐱 Training CatBoost...")
    cat_model = cb.CatBoostClassifier(
        iterations=300,
        depth=8,
        learning_rate=0.05,
        random_state=RANDOM_STATE,
        verbose=False
    )
    cat_model.fit(X_train_base, y_train_base)
    
    cat_train_proba = cat_model.predict_proba(X_train_base)[:, 1]
    cat_val_proba = cat_model.predict_proba(X_val_meta)[:, 1]
    
    # Neural Network
    print("🧠 Training Neural Network...")
    nn_model = keras.Sequential([
        layers.Input(shape=(X_train_base.shape[1],)),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(1, activation='sigmoid')
    ])
    
    nn_model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    nn_model.fit(
        X_train_base, y_train_base,
        validation_data=(X_val_meta, y_val_meta),
        epochs=50,
        batch_size=128,
        verbose=0
    )
    
    nn_train_proba = nn_model.predict(X_train_base, verbose=0).flatten()
    nn_val_proba = nn_model.predict(X_val_meta, verbose=0).flatten()
    
    # Meta-learner
    print("\n🎯 Training Meta-Learner...")
    meta_train = np.column_stack([xgb_train_proba, lgb_train_proba, cat_train_proba, nn_train_proba])
    meta_val = np.column_stack([xgb_val_proba, lgb_val_proba, cat_val_proba, nn_val_proba])
    
    meta_model = LogisticRegression(random_state=RANDOM_STATE, max_iter=2000)
    meta_model.fit(meta_train, y_train_base)
    
    print(f"Meta weights: XGB={meta_model.coef_[0][0]:.3f}, "
          f"LGB={meta_model.coef_[0][1]:.3f}, "
          f"Cat={meta_model.coef_[0][2]:.3f}, "
          f"NN={meta_model.coef_[0][3]:.3f}")
    
    # ===== SAVE MODELS =====
    print(f"\n{'='*60}")
    print("💾 SAVING MODELS")
    print(f"{'='*60}")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save all models
    with open(output_dir / 'lr_cascade.pkl', 'wb') as f:
        pickle.dump(lr_model, f)
    
    with open(output_dir / 'xgboost_stacking.pkl', 'wb') as f:
        pickle.dump(xgb_model, f)
    
    with open(output_dir / 'lightgbm_stacking.pkl', 'wb') as f:
        pickle.dump(lgb_model, f)
    
    with open(output_dir / 'catboost_stacking.pkl', 'wb') as f:
        pickle.dump(cat_model, f)
    
    nn_model.save(output_dir / 'neural_network.h5')
    
    with open(output_dir / 'meta_learner.pkl', 'wb') as f:
        pickle.dump(meta_model, f)
    
    with open(output_dir / 'scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    with open(output_dir / 'feature_names.pkl', 'wb') as f:
        pickle.dump(feature_names, f)
    
    config = {
        'easy_threshold_low': EASY_THRESHOLD_LOW,
        'easy_threshold_high': EASY_THRESHOLD_HIGH,
        'num_features': len(feature_names),
        'random_state': RANDOM_STATE
    }
    with open(output_dir / 'config.pkl', 'wb') as f:
        pickle.dump(config, f)
    
    print("\n✅ All models saved!")
    print(f"\n{'='*70}")
    print("🎉 TRAINING COMPLETED!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train phishing detection models')
    parser.add_argument('--data', required=True, help='Processed features CSV')
    parser.add_argument('--output', default='models/', help='Output directory')
    
    args = parser.parse_args()
    
    train_cascade_stacking(args.data, args.output)