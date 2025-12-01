"""
Trang admin - Quản lý hệ thống
Đường dẫn: WEB_PHISHING/app/pages/4_Admin.py
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.components import render_header, render_footer
from app.styles import apply_custom_css
from app.auth import check_password

st.set_page_config(page_title="Admin", page_icon="🔐", layout="wide")
apply_custom_css()
render_header()

st.title("🔐 Admin Panel")

if check_password():
    st.success("✅ Authenticated successfully!")
    
    st.markdown("---")
    
    # Admin features
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Batch Analysis")
        st.info("Phân tích hàng loạt URLs từ file CSV")
        if st.button("Go to Batch Analysis", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Batch_Analysis.py")
    
    with col2:
        st.subheader("📈 System Info")
        st.info("Xem thông tin chi tiết về hệ thống")
        if st.button("View System Info", use_container_width=True):
            st.switch_page("pages/3_About.py")
    
    st.markdown("---")
    
    st.subheader("⚙️ System Status")
    
    # Hiển thị thông tin hệ thống
    try:
        from src.predictor import PhishingPredictor
        
        @st.cache_resource
        def load_predictor():
            return PhishingPredictor(model_dir='models/')
        
        predictor = load_predictor()
        
        st.success("✅ All models loaded successfully")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Features", len(predictor.feature_names))
        with col2:
            st.metric("Models", "5")
        with col3:
            st.metric("Status", "🟢 Online")
        
        # Hiển thị thêm thông tin
        with st.expander("📋 Model Details"):
            st.write("**Layer 1 (Cascade):**")
            st.write("- Logistic Regression")
            st.write("- Filters 75.5% easy cases")
            
            st.write("\n**Layer 2 (Stacking):**")
            st.write("- XGBoost")
            st.write("- LightGBM")
            st.write("- CatBoost")
            st.write("- Neural Network")
            st.write("- Meta-Learner (Logistic Regression)")
            
            st.write("\n**Performance:**")
            st.write("- Accuracy: 99.50%")
            st.write("- F1-Score: 99.21%")
            st.write("- AUC-ROC: 99.80%")
        
        with st.expander("🔧 Configuration"):
            st.write("**Cascade Thresholds:**")
            st.write(f"- Easy Low: {predictor.easy_low}")
            st.write(f"- Easy High: {predictor.easy_high}")
            
            st.write("\n**Feature Normalization:**")
            st.write("- Safe/Good: +1")
            st.write("- Neutral: 0")
            st.write("- Suspicious: -1")
            
    except Exception as e:
        st.error(f"❌ Error loading models: {str(e)}")
        st.info("Vui lòng kiểm tra thư mục models/ có đầy đủ file models chưa")

else:
    st.info("👈 Please login to access admin features")
    st.markdown("---")
    
    # Hiển thị hướng dẫn
    st.markdown("""
    ### 📝 Admin Features
    
    Sau khi đăng nhập thành công, bạn có thể:
    
    1. **📊 Batch Analysis**: Upload file CSV với nhiều URLs để phân tích hàng loạt
    2. **📈 System Info**: Xem thông tin chi tiết về models và performance
    3. **⚙️ System Status**: Kiểm tra trạng thái hệ thống
    
    ---
    
    ⚠️ **Lưu ý**: Tính năng admin chỉ dành cho người quản trị hệ thống.
    """)

render_footer()