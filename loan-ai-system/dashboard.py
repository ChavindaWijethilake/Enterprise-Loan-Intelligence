import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from dotenv import load_dotenv

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import get_connection

# Page configuration
st.set_page_config(
    page_title="Enterprise Loan AI Dashboard",
    page_icon="🏦",
    layout="wide",
)

# Load environment variables
load_dotenv(".env")

# ---------------------------------------------------------------------------
# Data Fetching
# ---------------------------------------------------------------------------
def fetch_data():
    conn = get_connection()
    if not conn:
        return None, None
    
    try:
        # Fetch applications
        apps_query = "SELECT * FROM loan_applications ORDER BY created_at DESC"
        apps_df = pd.read_sql(apps_query, conn)
        
        # Fetch predictions
        preds_query = "SELECT * FROM loan_predictions"
        preds_df = pd.read_sql(preds_query, conn)
        
        conn.close()
        return apps_df, preds_df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None

# ---------------------------------------------------------------------------
# Dashboard UI
# ---------------------------------------------------------------------------
st.title("🏦 Enterprise Loan Approval Dashboard")
st.markdown("### Real-time AI decision monitoring and analytics")

# Sidebar for refreshes
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

apps_df, preds_df = fetch_data()

if apps_df is not None and not apps_df.empty:
    # -----------------------------------------------------------------------
    # Metrics Row
    # -----------------------------------------------------------------------
    total_apps = len(apps_df)
    approved_apps = len(apps_df[apps_df['status'] == 'APPROVED'])
    approval_rate = (approved_apps / total_apps) * 100 if total_apps > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Applications", total_apps)
    col2.metric("Approval Rate", f"{approval_rate:.1f}%")
    col3.metric("Approved", approved_apps)
    col4.metric("Average CIBIL", f"{apps_df['cibil_score'].mean():.0f}")

    st.markdown("---")

    # -----------------------------------------------------------------------
    # Charts Row
    # -----------------------------------------------------------------------
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Application Status Distribution")
        status_counts = apps_df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig = px.pie(status_counts, values='Count', names='Status', 
                     color='Status',
                     color_discrete_map={'APPROVED': '#28a745', 'REJECTED': '#dc3545', 'CONDITIONAL': '#ffc107', 'PENDING': '#6c757d'})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Loan Amount vs. CIBIL Score")
        fig2 = px.scatter(apps_df, x="cibil_score", y="loan_amount", color="status",
                          hover_data=['applicant_name'],
                          labels={"cibil_score": "CIBIL Score", "loan_amount": "Loan Amount (₹)"},
                          color_discrete_map={'APPROVED': '#28a745', 'REJECTED': '#dc3545', 'CONDITIONAL': '#ffc107'})
        st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------------------------------------------------
    # Recent Applications Table
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📋 Recent Loan Applications")
    
    # Merge with predictions for more detail
    if preds_df is not None and not preds_df.empty:
        display_df = apps_df.merge(preds_df[['loan_id', 'probability', 'email_sent']], on='loan_id', how='left')
    else:
        display_df = apps_df.copy()
        display_df['probability'] = 0.0
        display_df['email_sent'] = False

    # Format dataframe for display
    display_df = display_df[['loan_id', 'applicant_name', 'loan_amount', 'cibil_score', 'status', 'probability', 'created_at']]
    display_df['loan_amount'] = display_df['loan_amount'].apply(lambda x: f"₹{x:,.0f}")
    display_df['probability'] = display_df['probability'].apply(lambda x: f"{x:.2%}" if pd.notnull(x) else "N/A")
    
    st.dataframe(display_df, use_container_width=True)

else:
    st.info("No loan applications found in the database. Submit an application via the API to see data here!")
    st.markdown("""
    **To populate this dashboard:**
    1. Ensure your FastAPI server is running (`uvicorn api.main:app`).
    2. Go to `http://127.0.0.1:8000/docs`.
    3. Execute the `/predict` endpoint with sample data.
    """)
