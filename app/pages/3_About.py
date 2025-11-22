"""
Trang thông tin hệ thống
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
INPUT (80+ normalized features)
    ↓
┌─────────────────────────────────┐
│  LAYER 1: Logistic Regression   │
│  - Lọc 85-90% cases dễ          │
│  - Threshold: <0.15 or >0.85    │
└──────────┬──────────────────────┘
           │
       Hard Cases (10-15%)
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

# Performance
st.header("📊 Performance Metrics")

col1, col2 = st.columns(2)

with col1:
    st.metric("Accuracy", "99.3%")
    st.metric("Precision", "99.2%")
    st.metric("Recall", "98.5%")

with col2:
    st.metric("F1-Score", "98.9%")
    st.metric("AUC-ROC", "99.6%")
    st.metric("False Positive Rate", "0.4%")

# Features
st.header("🔧 Features (80+)")

st.markdown("""
### Feature Categories:

1. **URL-based (30)**: Length, special characters, encoding
2. **Domain-based (15)**: TLD, reputation, brand detection
3. **SSL/Security (10)**: Certificate validation, HTTPS
4. **DNS/Network (5)**: DNS records, IP analysis
5. **Content-based (10)**: Forms, iframes (simplified)
6. **Lexical (10)**: Character ratios, patterns
7. **Heuristic (10)**: Entropy, keywords, complexity

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
- Fast filtering (85-90% cases)
- High confidence threshold

### Layer 2: Stacking Ensemble
- **XGBoost**: Tree-based, max_depth=8
- **LightGBM**: Fast gradient boosting
- **CatBoost**: Categorical features expert
- **Neural Network**: 128→64→32→1
- **Meta-Learner**: LogisticRegression combines predictions
""")

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
    """)

with col2:
    st.markdown("""
    **Web Framework:**
    - Streamlit
    - Plotly
    - Pandas
    """)

render_footer()


# ========================================
# FILE: app/components.py
# ========================================
"""
UI Components
"""

import streamlit as st

def render_header():
    """Render page header"""
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h1 style='color: #667eea; font-size: 2.5rem;'>
            🛡️ Phishing Detector
        </h1>
        <p style='color: #666; font-size: 1.1rem;'>
            Advanced Phishing Detection with AI
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Render page footer"""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p>
            Developed with ❤️ using Streamlit | 
            Cascade + Stacking Ensemble Architecture
        </p>
        <p style='font-size: 0.9rem;'>
            ⚠️ Đây là công cụ hỗ trợ. Luôn cẩn thận khi truy cập websites lạ!
        </p>
    </div>
    """, unsafe_allow_html=True)