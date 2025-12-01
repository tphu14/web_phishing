"""
Trang phân tích hàng loạt - Chỉ cho Admin
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.predictor import PhishingPredictor
from app.components import render_header, render_footer
from app.styles import apply_custom_css
from app.auth import is_authenticated

st.set_page_config(page_title="Batch Analysis", page_icon="📊", layout="wide")
apply_custom_css()
render_header()

st.title("📊 Phân tích hàng loạt")

# Check authentication
if not is_authenticated():
    st.warning("🔒 Tính năng này chỉ dành cho Admin")
    st.info("Vui lòng đăng nhập để sử dụng tính năng này")
    
    if st.button("🔐 Login", use_container_width=True):
        st.switch_page("pages/4_Admin.py")
    
    st.stop()

# Load predictor
@st.cache_resource
def load_predictor():
    return PhishingPredictor(model_dir='models/')

predictor = load_predictor()
st.success("✅ Models ready!")

# Instructions
st.info("""
**Hướng dẫn:**
1. Upload file CSV với cột 'url'
2. Hệ thống sẽ phân tích tất cả URLs
3. Xem kết quả và tải về
""")

# File upload
uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

if uploaded_file:
    # Read CSV
    df = pd.read_csv(uploaded_file)
    
    if 'url' not in df.columns:
        st.error("❌ File CSV phải có cột 'url'!")
        st.stop()
    
    st.write(f"📊 Tìm thấy {len(df)} URLs")
    st.dataframe(df.head(), use_container_width=True)
    
    # Analyze button
    if st.button("🚀 Phân tích tất cả", type="primary", use_container_width=True):
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        
        for idx, url in enumerate(df['url']):
            status_text.text(f"Đang phân tích {idx+1}/{len(df)}: {url[:50]}...")
            progress_bar.progress((idx + 1) / len(df))
            
            try:
                result = predictor.predict(url)
                results.append({
                    'url': url,
                    'prediction': result['prediction'],
                    'phishing_score': result['phishing_score'],
                    'confidence': result['confidence'],
                    'risk_level': result['risk_level']
                })
            except Exception as e:
                results.append({
                    'url': url,
                    'prediction': 'error',
                    'phishing_score': -1,
                    'confidence': 'error',
                    'risk_level': 'error'
                })
        
        status_text.text("✅ Hoàn thành!")
        progress_bar.empty()
        
        # Results DataFrame
        results_df = pd.DataFrame(results)
        
        # Display results
        st.markdown("---")
        st.subheader("📊 Kết quả")
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = len(results_df)
            st.metric("Tổng URLs", total)
        
        with col2:
            phishing_count = (results_df['prediction'] == 'phishing').sum()
            st.metric("Phishing", phishing_count, delta=f"{phishing_count/total*100:.1f}%")
        
        with col3:
            legitimate_count = (results_df['prediction'] == 'legitimate').sum()
            st.metric("Legitimate", legitimate_count, delta=f"{legitimate_count/total*100:.1f}%")
        
        with col4:
            error_count = (results_df['prediction'] == 'error').sum()
            st.metric("Errors", error_count)
        
        # Chart
        fig = px.pie(
            results_df[results_df['prediction'] != 'error'],
            names='prediction',
            title='Distribution',
            color='prediction',
            color_discrete_map={'phishing': 'red', 'legitimate': 'green'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(results_df, use_container_width=True)
        
        # Download
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="💾 Tải kết quả (CSV)",
            data=csv,
            file_name="phishing_analysis_results.csv",
            mime="text/csv",
            use_container_width=True
        )

render_footer()