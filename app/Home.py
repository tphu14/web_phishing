"""
Streamlit App - Trang chủ
Chạy: streamlit run app/Home.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from components import render_header, render_footer
from styles import apply_custom_css

# Config
st.set_page_config(
    page_title="Phishing Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS
apply_custom_css()

# Header
render_header()

# Main content
st.markdown("## Chào mừng đến với Phishing Detector!")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🔍 Phân tích đơn lẻ
    Kiểm tra nhanh một URL
    """)
    if st.button("Bắt đầu →", key="single", use_container_width=True):
        st.switch_page("pages/1_Single_URL.py")

with col2:
    st.markdown("""
    ### 📊 Phân tích hàng loạt
    Upload file CSV với nhiều URLs
    """)
    if st.button("Bắt đầu →", key="batch", use_container_width=True):
        st.switch_page("pages/2_Batch_Analysis.py")

with col3:
    st.markdown("""
    ### 📈 Thông tin hệ thống
    Chi tiết về models và performance
    """)
    if st.button("Xem →", key="about", use_container_width=True):
        st.switch_page("pages/3_About.py")

# Info boxes
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Độ chính xác", "99.3%", "")

with col2:
    st.metric("Số features", "80+", "")

with col3:
    st.metric("Models", "4 base + 1 meta", "")

with col4:
    st.metric("Kiến trúc", "Cascade + Stacking", "")

# Description
st.markdown("""
---

### Hệ thống hoạt động như thế nào?

1. **Trích xuất features**: 80+ đặc trưng từ URL (domain, SSL, DNS...)
2. **Cascade Layer 1**: Logistic Regression lọc 85% cases dễ
3. **Stacking Layer 2**: XGBoost + LightGBM + CatBoost + NN xử lý cases khó
4. **Meta-Learner**: Kết hợp predictions tối ưu

**Tất cả features được chuẩn hóa về {-1, 0, 1} để đảm bảo ổn định!**
""")

# Footer
render_footer()