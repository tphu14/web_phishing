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