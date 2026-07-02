import streamlit as st
import requests
import json


st.set_page_config(
    page_title="Multi-Agent Financial Research",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Multi-Agent Financial Research System")
st.markdown("Powered by 4 specialised AI agents: Researcher · Analyst · News · Critic")



st.sidebar.header("Analysis Settings")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").upper()
company_name = st.sidebar.text_input("Company Name", value="Apple")

if st.sidebar.button("Run Analysis", type="primary"):
    with st.spinner("Running 4-agent pipeline... this takes ~60 seconds"):
        try:
            response = requests.post(
                "http://localhost:8000/analyse",
                json={"ticker": ticker, "company_name": company_name}
            )
            result = response.json()
            st.session_state['result'] = result
        except Exception as e:
            st.error(f"Error: {str(e)}")



if 'result' in st.session_state:
    result = st.session_state['result']
    
    st.success(f"Analysis complete — Run ID: {result['run_id']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Confidence Score", f"{result['confidence_score']:.0%}")
    
    with col2:
        st.metric("News Sentiment", f"{result['news_sentiment']:.2f}")
    
    with col3:
        st.metric("Errors", len(result['errors']))
    
    st.subheader("📊 Financial Metrics")
    st.write(result['analyst_summary'])
    
    st.subheader("🔍 Critic Analysis")
    st.write(result['critique_summary'])
    
    if result['errors']:
        st.subheader("⚠️ Errors")
        for error in result['errors']:
            st.error(error)