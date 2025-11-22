"""
Script đánh giá models
Usage: python scripts/evaluate.py --data data/processed/features.csv --models models/
"""

import argparse
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.predictor import PhishingPredictor
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                            f1_score, roc_auc_score, confusion_matrix,
                            classification_report)

def evaluate_models(data_path, model_dir):
    """Evaluate trained models"""
    
    print(f"\n{'='*70}")
    print("MODEL EVALUATION")
    print(f"{'='*70}\n")
    
    # Load data
    print(f"📂 Loading test data: {data_path}")
    df = pd.read_csv(data_path)
    
    # Get test set (last 20%)
    test_size = int(len(df) * 0.2)
    df_test = df.tail(test_size)
    
    print(f"📊 Test set: {len(df_test)} samples")
    
    # Load predictor
    print(f"\n🤖 Loading models from: {model_dir}")
    predictor = PhishingPredictor(model_dir=model_dir)
    
    # Predict
    print("\n⏳ Running predictions...")
    y_true = df_test['class'].map({1: 0, -1: 1}).values
    y_pred = []
    y_proba = []
    
    for idx, row in df_test.iterrows():
        if idx % 100 == 0:
            print(f"   Progress: {idx}/{len(df_test)}")
        
        result = predictor.predict(row['url'])
        y_pred.append(1 if result['prediction'] == 'phishing' else 0)
        y_proba.append(result['phishing_score'])
    
    y_pred = np.array(y_pred)
    y_proba = np.array(y_proba)
    
    # Calculate metrics
    print(f"\n{'='*60}")
    print("📊 RESULTS")
    print(f"{'='*60}\n")
    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    auc = roc_auc_score(y_true, y_proba)
    
    print(f"Accuracy:  {accuracy:.6f} ({accuracy*100:.2f}%)")
    print(f"Precision: {precision:.6f}")
    print(f"Recall:    {recall:.6f}")
    print(f"F1-Score:  {f1:.6f}")
    print(f"AUC-ROC:   {auc:.6f}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    print(f"\n📊 Confusion Matrix:")
    print(f"                 Predicted")
    print(f"                 Leg      Phish")
    print(f"   Actual  Leg   {cm[0,0]:6d}  {cm[0,1]:6d}")
    print(f"           Phish {cm[1,0]:6d}  {cm[1,1]:6d}")
    
    fpr = cm[0,1] / (cm[0,0] + cm[0,1])
    fnr = cm[1,0] / (cm[1,0] + cm[1,1])
    
    print(f"\n📉 Error Rates:")
    print(f"   False Positive Rate: {fpr*100:.3f}%")
    print(f"   False Negative Rate: {fnr*100:.3f}%")
    
    # Classification Report
    print(f"\n📋 Classification Report:")
    print(classification_report(y_true, y_pred, 
                               target_names=['Legitimate', 'Phishing'],
                               digits=4))
    
    print(f"\n{'='*70}")
    print("✅ EVALUATION COMPLETED!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate phishing detection models')
    parser.add_argument('--data', required=True, help='Processed features CSV')
    parser.add_argument('--models', default='models/', help='Models directory')
    
    args = parser.parse_args()
    
    evaluate_models(args.data, args.models)