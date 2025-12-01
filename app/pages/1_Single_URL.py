"""
Trang phân tích URL đơn lẻ - PHIÊN BẢN ĐẦY ĐỦ
Bao gồm: Biểu đồ predictions của tất cả models, radar chart, comparison table
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from urllib.parse import urlparse

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.predictor import PhishingPredictor
from app.components import render_header, render_footer
from app.styles import apply_custom_css

st.set_page_config(page_title="Single URL Analysis", page_icon="🔍", layout="wide")
apply_custom_css()
render_header()

st.title("🔍 Phân tích URL đơn lẻ")

# Load predictor
@st.cache_resource
def load_predictor():
    try:
        return PhishingPredictor(model_dir='models/')
    except Exception as e:
        st.error(f"Không thể load models: {str(e)}")
        st.info("Hãy đảm bảo các file models đã có trong thư mục models/")
        st.stop()

predictor = load_predictor()
st.success("✅ Models đã sẵn sàng!")

# Sidebar - Examples
with st.sidebar:
    st.header("📝 URL mẫu")
    examples = {
        "Safe example 1": "rabble.ca/babble/national-news/dmitri-soudas-falls-radio-canada-facebook-hoaxsters",
        "Safe example 2": "thewhiskeydregs.com/wp-content/themes/widescreen/includes/temp/promocoessmiles/?84784787824HDJNDJDSJSHD//2724782784/",
        "Phishing example 1": "https://id144247.webhosting.optonline.net/~m4d1/inc/costumer/",
        "Phishing example 2": "https://www.google.ro/url?sa=t&rct=j&q=&esrc=s&source=web&cd=5&cad=rja&uact=8&ved=0CD0QFjAEahUKEwj8ueqQ45HIAhXFQBQKHcPFAvk&url=https%3A%2F%2Fwww.rbsdigital.com%2F&usg=AFQjCNHQHOrLeA_8uqToEYDFCxjJWEzy_A",
    }
    
    selected_example = st.selectbox(
        "Chọn URL mẫu:",
        [""] + list(examples.keys())
    )
    
    if selected_example:
        st.code(examples[selected_example], language="text")

# Input
url_input = st.text_input(
    "Nhập URL cần kiểm tra:",
    placeholder="https://example.com",
    value=examples.get(selected_example, "")
)

analyze_button = st.button("🚀 Phân tích", type="primary", use_container_width=True)

# Analysis
if analyze_button and url_input:
    with st.spinner('🔄 Đang phân tích URL...'):
        result = predictor.predict(url_input)
    
    # Results
    st.markdown("---")
    st.subheader("📊 Kết quả phân tích")
    
    is_phishing = result['prediction'] == 'phishing'
    phishing_score = result['phishing_score']
    
    # Main result box
    if is_phishing:
        st.error(f"""
        ### ⚠️ CẢNH BÁO: WEBSITE NGUY HIỂM
        
        **Độ tin cậy:** {phishing_score*100:.1f}%
        
        Website này có dấu hiệu lừa đảo (phishing). **KHÔNG NÊN TRUY CẬP!**
        """)
    else:
        st.success(f"""
        ### ✅ WEBSITE AN TOÀN
        
        **Độ tin cậy:** {(1-phishing_score)*100:.1f}%
        
        Website này có vẻ an toàn.
        """)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🛡️ An toàn", f"{result['legitimate_score']*100:.1f}%")
    
    with col2:
        st.metric("⚠️ Nguy hiểm", f"{result['phishing_score']*100:.1f}%")
    
    with col3:
        st.metric("📊 Confidence", result['confidence'].upper())
    
    with col4:
        st.metric("🎯 Risk Level", result['risk_level'].upper())
    
    # Visualization
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = phishing_score * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Phishing Score (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkred" if is_phishing else "green"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        # Base models predictions
        st.markdown("#### 🤖 Dự đoán từng Model")
        
        # Lấy predictions từ base models
        features = result['features']
        features_df = pd.DataFrame([features])[predictor.feature_names]
        features_scaled = predictor.scaler.transform(features_df)
        
        xgb_prob = predictor.xgb_model.predict_proba(features_df)[0, 1] * 100
        lgb_prob = predictor.lgb_model.predict_proba(features_df)[0, 1] * 100
        cat_prob = predictor.cat_model.predict_proba(features_df)[0, 1] * 100
        nn_prob = predictor.nn_model.predict(features_scaled, verbose=0).flatten()[0] * 100
        
        # Bar chart
        models_data = pd.DataFrame({
            'Model': ['XGBoost', 'LightGBM', 'CatBoost', 'Neural Network'],
            'Phishing Score (%)': [xgb_prob, lgb_prob, cat_prob, nn_prob]
        })
        
        fig2 = px.bar(
            models_data,
            x='Model',
            y='Phishing Score (%)',
            color='Phishing Score (%)',
            color_continuous_scale=['green', 'yellow', 'red'],
            text='Phishing Score (%)',
            range_color=[0, 100]
        )
        
        fig2.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )
        
        fig2.update_layout(
            height=350,
            showlegend=False,
            yaxis_range=[0, 110],
            xaxis_title="",
            yaxis_title="Phishing Score (%)"
        )
        
        # Add threshold line
        fig2.add_hline(
            y=50,
            line_dash="dash",
            line_color="red",
            annotation_text="Threshold (50%)",
            annotation_position="right"
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    # Comparison table
    st.markdown("---")
    st.subheader("📊 So sánh chi tiết các Models")
    
    comparison_df = pd.DataFrame({
        'Model': ['XGBoost', 'LightGBM', 'CatBoost', 'Neural Network', 'Meta-Learner (Final)'],
        'Phishing Score (%)': [
            f"{xgb_prob:.2f}%",
            f"{lgb_prob:.2f}%",
            f"{cat_prob:.2f}%",
            f"{nn_prob:.2f}%",
            f"{phishing_score*100:.2f}%"
        ],
        'Prediction': [
            '⚠️ Phishing' if xgb_prob > 50 else '✅ Legitimate',
            '⚠️ Phishing' if lgb_prob > 50 else '✅ Legitimate',
            '⚠️ Phishing' if cat_prob > 50 else '✅ Legitimate',
            '⚠️ Phishing' if nn_prob > 50 else '✅ Legitimate',
            '⚠️ Phishing' if phishing_score > 0.5 else '✅ Legitimate'
        ]
    })
    
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Radar chart - Model agreement
    st.markdown("---")
    st.subheader("🎯 Độ đồng thuận giữa các Models")
    
    fig3 = go.Figure()
    
    fig3.add_trace(go.Scatterpolar(
        r=[xgb_prob, lgb_prob, cat_prob, nn_prob, phishing_score*100],
        theta=['XGBoost', 'LightGBM', 'CatBoost', 'Neural Network', 'Final'],
        fill='toself',
        name='Phishing Score',
        line_color='red' if is_phishing else 'green'
    ))
    
    fig3.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # Details
    with st.expander("📋 Chi tiết kỹ thuật"):
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Method used:** {result['method']}")
            st.write(f"**Is easy case:** {result['is_easy_case']}")
            st.write(f"**Risk level:** {result['risk_level']}")
            
            # Decision flow
            st.markdown("##### 🔄 Decision Flow:")
            if result['is_easy_case']:
                st.info(f"""
                **Layer 1: Logistic Regression**
                - Confidence: Very High
                - Score: {phishing_score*100:.1f}%
                - Decision: {"Phishing" if is_phishing else "Legitimate"}
                
                ✅ Case dễ, không cần Layer 2
                """)
            else:
                st.warning(f"""
                **Layer 1: Logistic Regression**
                - Confidence: Medium
                - Score: {phishing_score*100:.1f}%
                
                ⚠️ Case khó → Chuyển sang Layer 2
                
                **Layer 2: Stacking Ensemble**
                - XGBoost: {xgb_prob:.1f}%
                - LightGBM: {lgb_prob:.1f}%
                - CatBoost: {cat_prob:.1f}%
                - Neural Net: {nn_prob:.1f}%
                - Meta-Learner: {phishing_score*100:.1f}%
                """)
        
        with col2:
            # Feature sample
            st.markdown("##### 📊 Sample Features (first 10):")
            sample_features = dict(list(result['features'].items())[:10])
            df_features = pd.DataFrame([sample_features]).T
            df_features.columns = ['Value']
            df_features['Status'] = df_features['Value'].apply(
                lambda x: '✅ Safe' if x == 1 else ('⚠️ Suspicious' if x == -1 else '➖ Neutral')
            )
            st.dataframe(df_features, use_container_width=True)
    
    # Model weights visualization
    with st.expander("⚖️ Trọng số Meta-Learner"):
        st.markdown("""
        Meta-Learner kết hợp predictions từ 4 base models với các trọng số đã học:
        """)
        
        # Lấy weights từ meta-learner
        weights = predictor.meta_model.coef_[0]
        
        weights_df = pd.DataFrame({
            'Model': ['XGBoost', 'LightGBM', 'CatBoost', 'Neural Network'],
            'Weight': weights,
            'Contribution (%)': [
                f"{xgb_prob * weights[0] / 100:.2f}",
                f"{lgb_prob * weights[1] / 100:.2f}",
                f"{cat_prob * weights[2] / 100:.2f}",
                f"{nn_prob * weights[3] / 100:.2f}"
            ]
        })
        
        # Bar chart weights
        fig_weights = px.bar(
            weights_df,
            x='Model',
            y='Weight',
            color='Weight',
            color_continuous_scale=['red', 'yellow', 'green'],
            text='Weight'
        )
        
        fig_weights.update_traces(
            texttemplate='%{text:.3f}',
            textposition='outside'
        )
        
        fig_weights.update_layout(
            height=300,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Weight"
        )
        
        st.plotly_chart(fig_weights, use_container_width=True)
        
        st.dataframe(weights_df, use_container_width=True, hide_index=True)
        
        st.info("""
        **Giải thích:**
        - Weight > 0: Model đóng góp tích cực
        - Weight < 0: Model đóng góp tiêu cực (cân bằng)
        - Weight càng lớn = ảnh hưởng càng mạnh
        """)
    
    # URL info
    with st.expander("🔗 Thông tin URL"):
        try:
            parsed = urlparse(url_input)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Scheme:** {parsed.scheme}")
                st.write(f"**Domain:** {parsed.netloc}")
                st.write(f"**Path:** {parsed.path}")
            
            with col2:
                st.write(f"**Query:** {parsed.query if parsed.query else 'None'}")
                st.write(f"**Fragment:** {parsed.fragment if parsed.fragment else 'None'}")
                st.write(f"**URL Length:** {len(url_input)} chars")
        except:
            st.write("Không thể phân tích URL")

elif analyze_button:
    st.warning("⚠️ Vui lòng nhập URL!")

render_footer()