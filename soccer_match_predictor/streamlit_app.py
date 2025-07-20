"""
Soccer Match Predictor - Streamlit Web Interface

This app provides an interactive interface for soccer match predictions
with detailed explanations of the ML models and their decisions.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure page
st.set_page_config(
    page_title="Soccer Match Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("⚽ Soccer Match Predictor")
    st.subtitle("ML-powered predictions for Premier League & MLS matches")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "🔮 Predictions", "📊 Model Analysis", "📚 Learning Dashboard", "⚙️ Settings"]
    )
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "🔮 Predictions":
        show_predictions_page()
    elif page == "📊 Model Analysis":
        show_analysis_page()
    elif page == "📚 Learning Dashboard":
        show_learning_page()
    elif page == "⚙️ Settings":
        show_settings_page()

def show_home_page():
    """Home page with project overview and quick stats"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Welcome to the Soccer Match Predictor!
        
        This project focuses on **learning machine learning concepts** through soccer match prediction.
        We're predicting outcomes for:
        
        - 🏴󠁧󠁢󠁥󠁮󠁧󠁿 **Premier League** matches
        - 🇺🇸 **MLS** matches
        
        ### Learning Focus
        This isn't just about predictions - it's about understanding:
        - How different ML algorithms work
        - Feature engineering for sports data
        - Model evaluation and interpretation
        - Real-world data challenges
        """)
        
        # Show recent predictions or stats (placeholder)
        st.info("📊 Model training in progress... Check back soon for live predictions!")
    
    with col2:
        st.markdown("### Quick Stats")
        # Placeholder metrics
        st.metric("Model Accuracy", "Training...", "")
        st.metric("Matches Analyzed", "Loading...", "")
        st.metric("Features Used", "TBD", "")
        
        st.markdown("### Data Sources")
        st.markdown("""
        - ESPN API (free tier)
        - FBref.com (web scraping)
        - Weather APIs
        """)

def show_predictions_page():
    """Match prediction interface"""
    st.header("🔮 Match Predictions")
    
    # League selection
    league = st.selectbox("Select League:", ["Premier League", "MLS"])
    
    st.warning("⚠️ Prediction system not yet implemented. Currently in development phase.")
    
    # Placeholder for prediction interface
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upcoming Matches")
        st.info("Match data will be loaded from APIs")
        
    with col2:
        st.subheader("Prediction Results")
        st.info("Model predictions will appear here")

def show_analysis_page():
    """Model analysis and insights"""
    st.header("📊 Model Analysis & Insights")
    
    tab1, tab2, tab3 = st.tabs(["Feature Importance", "Model Performance", "Data Insights"])
    
    with tab1:
        st.subheader("Feature Importance Analysis")
        st.info("Feature importance charts will be generated after model training")
        
    with tab2:
        st.subheader("Model Performance Metrics")
        st.info("Performance metrics will be displayed after model validation")
        
    with tab3:
        st.subheader("Data Insights")
        st.info("Data analysis and insights will be shown here")

def show_learning_page():
    """Learning dashboard with explanations"""
    st.header("📚 Learning Dashboard")
    
    st.markdown("""
    This page explains the machine learning concepts used in this project.
    Each algorithm and technique includes detailed explanations.
    """)
    
    # Learning sections
    with st.expander("🌳 Random Forest Algorithm"):
        st.markdown("""
        **Random Forest** is an ensemble method that combines multiple decision trees.
        
        **Why it works for soccer prediction:**
        - Handles both numerical and categorical features
        - Resistant to overfitting
        - Provides feature importance scores
        - Works well with incomplete data
        
        **How it works:**
        1. Creates multiple decision trees using random subsets of data
        2. Each tree votes on the prediction
        3. Final prediction is the majority vote
        """)
    
    with st.expander("🚀 XGBoost Algorithm"):
        st.markdown("""
        **XGBoost** (Extreme Gradient Boosting) builds models sequentially.
        
        **Why it's effective:**
        - Excellent performance on tabular data
        - Handles missing values automatically
        - Built-in regularization prevents overfitting
        - Fast training and prediction
        
        **Key concept:**
        Each new tree corrects the errors of previous trees.
        """)
    
    with st.expander("🎯 Feature Engineering for Soccer"):
        st.markdown("""
        **Important features for soccer prediction:**
        
        - **Team Form:** Recent performance (last 5-10 games)
        - **Home Advantage:** Historical home vs away performance
        - **Head-to-Head:** Previous meetings between teams
        - **Goals For/Against:** Offensive and defensive strength
        - **Advanced Stats:** Expected Goals (xG), possession, shots
        """)

def show_settings_page():
    """Settings and configuration"""
    st.header("⚙️ Settings")
    
    st.subheader("Data Sources")
    espn_key = st.text_input("ESPN API Key", type="password")
    api_football_key = st.text_input("API-Football Key", type="password")
    
    st.subheader("Model Parameters")
    test_size = st.slider("Test Set Size", 0.1, 0.4, 0.2)
    random_state = st.number_input("Random State", value=42)
    
    if st.button("Save Settings"):
        st.success("Settings saved!")

if __name__ == "__main__":
    main()