"""
CSS Styling - Ẩn UI không cần thiết cho production
"""

import streamlit as st

def apply_custom_css():
    """Apply custom CSS - Ẩn manage app và UI elements"""
    st.markdown("""
    <style>
        /* ========== Ẩn Streamlit Branding & Controls ========== */
        
        /* Ẩn menu hamburger */
        #MainMenu {visibility: hidden;}
        
        /* Ẩn footer "Made with Streamlit" */
        footer {visibility: hidden;}
        
        /* Ẩn header toolbar */
        header {visibility: hidden;}
        
        /* ========== Ẩn nút Manage App (CHÍNH XÁC) ========== */
        button[data-testid="manage-app-button"] {display: none !important;}
        button[class*="terminalButton"] {display: none !important;}
        
        /* Ẩn Deploy button */
        .stDeployButton {display: none !important;}
        div[data-testid="stToolbar"] {display: none !important;}
        div[data-testid="stDecoration"] {display: none !important;}
        div[data-testid="stStatusWidget"] {display: none !important;}
        
        /* Ẩn các action buttons */
        button[kind="header"] {display: none !important;}
        button[kind="headerNoPadding"] {display: none !important;}
        
        /* Ẩn settings và menu buttons */
        .stActionButton {display: none !important;}
        
        /* Ẩn GitHub icon và toolbar */
        .css-1kyxreq {display: none !important;}
        .viewerBadge_container__1QSob {display: none !important;}
        .styles_viewerBadge__1yB5_ {display: none !important;}
        
        /* Ẩn Streamlit Cloud Status iframe */
        iframe[src*="streamlitstatus.com"] {display: none !important;}
        
        /* ========== Layout Styling ========== */
        
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
        
        /* ========== Remove Padding ========== */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)