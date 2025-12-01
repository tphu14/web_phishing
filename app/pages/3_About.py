"""
Trang thông tin hệ thống - Kết quả training thực tế
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.components import render_header, render_footer
from app.styles import apply_custom_css

st.set_page_config(page_title="About", page_icon="📈", layout="wide")
apply_custom_css()
render_header()

st.title("📈 Thông tin hệ thống")

# Architecture
st.header("🏗️ Kiến trúc")

st.markdown("""
```
INPUT (90 normalized features)
    ↓
┌─────────────────────────────────┐
│  LAYER 1: Logistic Regression   │
│  - Lọc 75.5% cases dễ            │
│  - Threshold: <0.01 or >0.99    │
└──────────┬──────────────────────┘
           │
       Hard Cases (24.5%)
           │
           ▼
┌─────────────────────────────────┐
│  LAYER 2: Stacking Ensemble     │
│  ┌───────────────────────────┐  │
│  │ • XGBoost                 │  │
│  │ • LightGBM                │  │
│  │ • CatBoost                │  │
│  │ • Neural Network          │  │
│  └───────────┬───────────────┘  │
│              ▼                   │
│  Meta-Learner (Logistic Reg)    │
└──────────────┬──────────────────┘
               │
               ▼
        FINAL PREDICTION
```
""")

# Performance - Kết quả thực tế từ training
st.header("📊 Performance Metrics (Test Set)")

col1, col2 = st.columns(2)

with col1:
    st.metric("Accuracy", "99.50%", "+0.11%")
    st.metric("Precision", "99.49%")
    st.metric("Recall", "98.94%")

with col2:
    st.metric("F1-Score", "99.21%")
    st.metric("AUC-ROC", "99.80%")
    st.metric("False Positive Rate", "0.24%")

# Cascade Distribution
st.header("⚖️ Cascade Distribution")

col1, col2 = st.columns(2)

with col1:
    st.metric("Easy Cases (LR)", "75.5%", "✅ Perfect!")
    st.info("Được xử lý bởi Layer 1 với độ tin cậy cao")

with col2:
    st.metric("Hard Cases (Stacking)", "24.5%")
    st.info("Được xử lý bởi Layer 2 với ensemble models")

# Cross-Validation
st.header("🎯 Cross-Validation (5-Fold)")

cv_scores = {
    "Fold 1": 0.992110,
    "Fold 2": 0.992263,
    "Fold 3": 0.992450,
    "Fold 4": 0.992908,
    "Fold 5": 0.992210
}

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Fold 1-2", "99.22%")
with col2:
    st.metric("Fold 3-4", "99.27%")
with col3:
    st.metric("Mean ± Std", "99.24% ± 0.03%")

# Confusion Matrix
st.header("📊 Confusion Matrix (Test Set)")

st.markdown("""
|                | **Predicted Legitimate** | **Predicted Phishing** |
|----------------|--------------------------|------------------------|
| **Actual Legitimate** | 68,985 (✅)              | 163 (❌ FP: 0.24%)     |
| **Actual Phishing**   | 338 (❌ FN: 1.06%)       | 31,501 (✅)            |

**Tổng test set: 100,987 samples**
- Legitimate: 69,148 (68.5%)
- Phishing: 31,839 (31.5%)
""")

# Features
st.header("🔧 Features (90)")

st.markdown("""
### Feature Categories:

1. **URL-based (30)**: Length, special characters, encoding
2. **Domain-based (15)**: TLD, reputation, brand detection
3. **SSL/Security (10)**: Certificate validation, HTTPS
4. **DNS/Network (5)**: DNS records, IP analysis
5. **Content-based (10)**: Forms, iframes (simplified)
6. **Lexical (10)**: Character ratios, patterns
7. **Heuristic (10)**: Entropy, keywords, complexity

### Top 5 Most Important Features:
1. **Has_WWW**: 72.88% importance
2. **Has_HTTPS**: 13.64%
3. **Has_Valid_SSL**: 7.90%
4. **TLD_Type**: 0.27%
5. **Path_Entropy**: 0.27%

### Normalization:
- `1` = Safe/Good/Normal
- `0` = Medium/Neutral/Unknown
- `-1` = Suspicious/Bad/Dangerous
""")

# Models
st.header("🤖 Models")

st.markdown("""
### Layer 1: Cascade
- **Logistic Regression**
- F1-Score: 99.24% (CV)
- Fast filtering (75.5% cases)

### Layer 2: Stacking Ensemble
- **XGBoost**: Validation Acc 98.15%, F1 96.38%
- **LightGBM**: Validation Acc 98.20%, F1 96.46%
- **CatBoost**: Validation Acc 98.09%, F1 96.24%
- **Neural Network**: Validation Acc 97.91%, F1 95.89%

### Meta-Learner Weights:
- **XGBoost**: +3.65
- **LightGBM**: +6.76 (highest impact)
- **CatBoost**: -5.04 (balancing)
- **Neural Network**: +4.75
""")

# Comparison
st.header("📈 Model Comparison")

comparison_data = {
    "Model": ["LR Only", "Cascade + Stacking"],
    "Accuracy": ["99.39%", "99.50%"],
    "F1-Score": ["99.03%", "99.21%"],
    "Improvement": ["-", "+0.11%"]
}

st.table(comparison_data)

# Tech Stack
st.header("💻 Tech Stack")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **ML Libraries:**
    - scikit-learn
    - XGBoost
    - LightGBM
    - CatBoost
    - TensorFlow/Keras
    - imbalanced-learn (SMOTE)
    """)

with col2:
    st.markdown("""
    **Web Framework:**
    - Streamlit
    - Plotly
    - Pandas
    - NumPy
    """)

# Dataset Info
st.header("📁 Dataset Information")

st.markdown("""
- **Total samples**: 504,932 URLs
- **Training set**: 403,945 (80%)
- **Test set**: 100,987 (20%)
- **After SMOTE**: 553,178 balanced samples
- **Encoding**: latin1 (auto-detected)
- **Features**: 90 normalized values
""")

render_footer()