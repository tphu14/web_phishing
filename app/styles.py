"""
CSS Styling
"""

import streamlit as st

def apply_custom_css():
    """Apply custom CSS"""
    st.markdown("""
    <style>
        /* Main container */
        .main {
            padding: 2rem;
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            font-weight: bold;
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: bold;
        }
        
        /* Cards */
        .element-container {
            border-radius: 8px;
        }
        
        /* Success/Error boxes */
        .stSuccess, .stError {
            border-radius: 8px;
            padding: 1.5rem;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            font-weight: bold;
            font-size: 1.1rem;
        }
    </style>
    """, unsafe_allow_html=True)