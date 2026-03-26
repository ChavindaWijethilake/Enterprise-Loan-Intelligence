# =============================================================================
# dashboard.py — Enterprise Loan AI Admin Dashboard
# =============================================================================
# PURPOSE:
#   Industrial-themed Streamlit dashboard for monitoring, reviewing, and
#   acting on loan applications. Features glassmorphism aesthetics, a
#   collapsible sidebar with session-state-driven navigation, and five
#   views: Overview, Credit Engine, Email Ops, Analytics, and Audit Log.
#
# RUN:
#   streamlit run dashboard.py
#
# REQUIRES:
#   - PostgreSQL database with tables created via src/create_table.py
#   - FastAPI server (uvicorn api.main:app --reload) for action endpoints
# =============================================================================

import streamlit as st
import pandas as pd
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.db_service import get_connection, release_connection

st.set_page_config(
    page_title="Enterprise Loan AI Dashboard",
    page_icon="🏦",
    layout="wide",
)

# Initialize Session State
if "h_page" not in st.session_state: st.session_state.h_page = 1
if "p_page" not in st.session_state: st.session_state.p_page = 1
if "password_correct" not in st.session_state: st.session_state.password_correct = False

# ---------------------------------------------------------------------------
# CUSTOM CSS — Industrial Glassmorphism Design System
# ---------------------------------------------------------------------------
# CSS Variables (--fin-indigo, --fin-text-primary, etc.) and --sidebar-w
# drive the entire theme. The sidebar width toggles between 72px (mini)
# and 264px (full) based on session_state.sidebar_view. Key visual layers:
#   1. Sidebar rail with brand header and radio-button navigation.
#   2. Glassmorphism cards (backdrop-filter: blur) for metrics and tables.
#   3. Responsive breakpoints at 1200px and 768px for tight layouts.
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {{
        --fin-indigo: #4F46E5;
        --fin-text-primary: #020617;
        --fin-text-secondary: #0f172a;
        --fin-glass-border: #e2e8f0;
        --sidebar-w: 264px;
    }}

    /* Global Reset & Animations */
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.4); }} 70% {{ box-shadow: 0 0 0 10px rgba(79, 70, 229, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); }} }}

    .stApp {{ background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); color: var(--fin-text-primary); font-family: 'Inter', sans-serif; overflow-x: hidden; }}
    [data-testid="stMain"] > div {{ animation: fadeIn 0.6s ease-out; }}
    
    /* Plotly Container Borders (Depth) — no hover jitter */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.06) !important;
        margin-bottom: 1rem !important;
    }}
    
    /* =====================================================
       INDUSTRIAL SIDEBAR — Tight Alignment
       ===================================================== */
    
    section[data-testid="stSidebar"] {{
        width: var(--sidebar-w) !important;
        min-width: var(--sidebar-w) !important;
        max-width: var(--sidebar-w) !important;
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
        border-right: 1px solid var(--fin-glass-border) !important;
        transition: width 0.1s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 0 !important;
    }}

    section[data-testid="stSidebar"] > div:first-child {{
        padding: 0 !important;
    }}

    [data-testid="stSidebarUserContent"] {{
        padding: 0.75rem 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        overflow-x: hidden !important;
        height: 100vh !important;
    }}

    [data-testid="stMain"] {{ 
        transition: margin-left 0.1s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    
    .main .block-container {{
        max-width: 1400px !important;
        padding: 1.5rem 2.5rem !important;
        transition: all 0.3s ease !important;
        margin: 0 auto !important;
    }}

    /* Responsive Tightening */
    @media (max-width: 1200px) {{
        .main .block-container {{ padding: 1rem 1.5rem !important; }}
    }}
    @media (max-width: 768px) {{
        .main .block-container {{ padding: 0.5rem 0.75rem !important; }}
    }}
    [data-testid="stSidebarNav"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] {{ 
        display: none !important; 
    }}

    /* Fix: Overlapping labels */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {{ display: none !important; }}

    /* --- Brand Header --- */
    .sidebar-header-lock {{
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center !important;
        height: 48px;
        padding: 0 !important;
        margin-bottom: 16px;
        width: 100%;
        gap: 0;
    }}

    .sidebar-brand {{
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        font-family: 'Poppins', sans-serif;
        font-weight: 800 !important;
        color: var(--fin-text-primary) !important;
        flex-grow: 1;
    }}

    .brand-dot {{ 
        width: 10px; 
        height: 10px; 
        background: var(--fin-indigo); 
        border-radius: 50%; 
        animation: pulse 2s infinite;
    }}

    /* --- Navigation Rail --- */
    .stRadio [role="radiogroup"] {{
        gap: 4px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        padding: 0 !important;
        width: 100% !important;
    }}

    /* Aggressive Marker Suppression */
    [data-testid="stSidebar"] .stRadio label > div:first-child {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }}

    [data-testid="stSidebar"] .stRadio label {{
        background: transparent !important;
        border-radius: 10px !important;
        padding: 0 12px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        cursor: pointer !important;
        width: calc(100% - 16px) !important;
        height: 42px !important;
        margin: 4px auto !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 1rem !important;
        color: var(--fin-text-secondary) !important;
    }}

    [data-testid="stSidebar"] .stRadio label:hover {{
        background: rgba(79, 70, 229, 0.06) !important;
    }}

    /* Nav label typography */
    [data-testid="stSidebar"] .stRadio label p {{
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        color: var(--fin-text-secondary) !important;
        margin: 0 !important;
        white-space: nowrap !important;
        display: block !important;
        text-align: left !important;
    }}

    /* Active State Polish */
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {{
        background: rgba(79, 70, 229, 0.08) !important;
        border-left: 4px solid var(--fin-indigo) !important;
        border-radius: 4px 12px 12px 4px !important;
        padding-left: 8px !important;
    }}
    [data-testid="stSidebar"] .stRadio label:has(input:checked) p {{
        color: var(--fin-indigo) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }}
    
    [data-testid="stSidebar"] .stRadio label:hover {{
        background: rgba(79, 70, 229, 0.04) !important;
        color: var(--fin-indigo) !important;
    }}
    [data-testid="stSidebar"] .stButton:last-of-type button:hover p {{
        color: #E11D48 !important;
    }}

    /* Global Buttons (Industrial Slate/Indigo) */
    .stButton button {{
        background: white !important;
        border: 1px solid var(--fin-glass-border) !important;
        color: var(--fin-text-primary) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }}

    .stButton button:hover {{
        border-color: var(--fin-indigo) !important;
        color: var(--fin-indigo) !important;
        background: rgba(79, 70, 229, 0.02) !important;
        transform: translateY(-1px);
    }}

    .stButton button[kind="primary"] {{
        background: var(--fin-indigo) !important;
        border-color: var(--fin-indigo) !important;
        color: white !important;
    }}

    .stButton button[kind="primary"]:hover {{
        background: #4338CA !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2) !important;
    }}

    /* Section Label */
    .nav-section-label {{
        font-size: 0.65rem;
        font-weight: 800;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 12px 0 6px 16px;
        display: block;
    }}

    /* Logout container positioning */
    div:has(> button[key="logout_polish"]) {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        padding: 0 8px !important;
        margin-top: auto !important;
        margin-bottom: 1.5rem !important;
    }}

    /* =====================================================
       INDUSTRIAL COMPONENTS — Aesthetic Restoration
       ===================================================== */
    
    .fin-card {{ 
        background: rgba(255, 255, 255, 0.97) !important; 
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important; 
        border-radius: 14px; 
        padding: 1.5rem; 
        margin-bottom: 12px;
        box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.06);
        transition: box-shadow 0.2s ease;
    }}
    .fin-card:hover {{ box-shadow: 0 6px 16px -4px rgba(0, 0, 0, 0.1); }}

    .metric-card {{
        background: white !important;
        padding: 1.25rem 1.5rem;
        border-radius: 14px;
        border: 1px solid rgba(226, 232, 240, 0.7) !important;
        border-left: 4px solid var(--fin-indigo) !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 120px;
        gap: 6px;
        transition: box-shadow 0.2s ease;
    }}
    .metric-card:hover {{ box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.08); }}

    .metric-label {{ font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }}
    .metric-value {{ font-size: 1.75rem; font-weight: 800; color: var(--fin-text-primary); letter-spacing: -0.02em; }}
    .metric-delta {{ font-size: 0.8rem; font-weight: 600; padding: 4px 10px; border-radius: 20px; width: fit-content; }}
    .delta-plus {{ background: rgba(16, 185, 129, 0.1); color: #059669; }}
    .delta-stable {{ background: rgba(148, 163, 184, 0.1); color: #475569; }}

    .glowing-badge {{
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-flex;
        align-items: center;
        letter-spacing: 0.05em;
    }}

    .badge-approved {{ background: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2); }}
    .badge-rejected {{ background: rgba(244, 63, 94, 0.1); color: #E11D48; border: 1px solid rgba(244, 63, 94, 0.2); }}
    .badge-pending {{ background: rgba(245, 158, 11, 0.1); color: #D97706; border: 1px solid rgba(245, 158, 11, 0.2); }}
    .badge-email-sent {{ background: rgba(14, 165, 233, 0.1); color: #0284C7; border: 1px solid rgba(14, 165, 233, 0.2); }}

    .table-container {{ overflow-x: auto; width: 100%; border-radius: 10px; }}
    .bloomberg-table {{ width: 100%; border-collapse: separate; border-spacing: 0 6px; min-width: 600px; }}
    .bloomberg-table th {{ text-align: left; padding: 12px 16px; color: #64748b; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; border-bottom: 2px solid #e2e8f0; white-space: nowrap; }}
    .bloomberg-table td {{ padding: 14px 16px; background: white; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; white-space: nowrap; }}
    .bloomberg-table tr:nth-child(even) td {{ background: #fafbfc; }}
    .bloomberg-table tr:hover td {{ background: #f1f5f9 !important; cursor: default; }}
    .bloomberg-table tr td:first-child {{ border-left: 1px solid #f1f5f9; border-radius: 10px 0 0 10px; }}
    .bloomberg-table tr td:last-child {{ border-right: 1px solid #f1f5f9; border-radius: 0 10px 10px 0; }}

    .institutional-box {{
        text-align: center;
        padding: 3rem 2rem;
        background: white;
        border-radius: 24px;
        border: 1px solid var(--fin-glass-border);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }}
    .institutional-box img {{ width: 80px; margin-bottom: 1.5rem; }}
    .institutional-box h1 {{ font-size: 1.75rem; font-weight: 800; color: var(--fin-text-primary); margin-bottom: 0.5rem; }}
    .institutional-box p {{ color: var(--fin-text-secondary); font-size: 0.95rem; }}

    /* =====================================================
       TEXT INPUTS — Clean White with Indigo Solid Focus
       ===================================================== */
    
    .stTextInput input, .stTextInput input[type="text"], .stTextInput input[type="password"] {{
        background: #ffffff !important;
        color: var(--fin-text-primary) !important;
        border: 1.5px solid var(--fin-glass-border) !important;
        border-radius: 10px !important;
        padding: 0.7rem 1rem !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        outline: none !important;
        caret-color: var(--fin-indigo) !important;
    }}

    .stTextInput input:focus, .stTextInput input:focus-visible,
    .stTextInput input[type="text"]:focus, .stTextInput input[type="password"]:focus {{
        border-color: var(--fin-indigo) !important;
        box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.15) !important;
        outline: none !important;
        background: #ffffff !important;
    }}

    /* Override Streamlit's default red/dashed focus ring */
    .stTextInput div[data-baseweb="input"] {{
        border: none !important;
        box-shadow: none !important;
    }}

    .stTextInput input::placeholder {{
        color: #94a3b8 !important;
        opacity: 1 !important;
    }}

    /* Input labels — keep dark and legible */
    .stTextInput label, .stTextInput label p {{
        color: var(--fin-text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* =====================================================
       FORM SUBMIT BUTTON — Indigo Primary
       ===================================================== */
    
    [data-testid="stFormSubmitButton"] button {{
        background: var(--fin-indigo) !important;
        border: none !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.7rem 1.5rem !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.25) !important;
    }}

    [data-testid="stFormSubmitButton"] button:hover {{
        background: #4338CA !important;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.35) !important;
        transform: translateY(-1px) !important;
    }}

    /* =====================================================
       DASHBOARD-WIDE ALIGNMENT FIXES
       ===================================================== */

    /* Force columns to align flush */
    [data-testid="stHorizontalBlock"] {{
        gap: 1rem !important;
        align-items: stretch !important;
    }}

    /* Ensure metric cards fill column height evenly */
    [data-testid="stColumn"] {{
        display: flex !important;
        flex-direction: column !important;
    }}

    [data-testid="stColumn"] > div {{
        flex: 1 !important;
    }}

    /* Page Header Component */
    .page-header {{
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 1.75rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f1f5f9;
    }}
    .page-header .ph-icon {{
        font-size: 1.75rem;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        flex-shrink: 0;
    }}
    .page-header .ph-text h3 {{
        font-family: 'Poppins', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0 !important;
        letter-spacing: -0.02em;
    }}
    .page-header .ph-text p {{
        font-size: 0.85rem;
        color: #64748b;
        margin: 2px 0 0 0;
        font-weight: 500;
    }}

    /* Tabs and expanders: consistent padding */
    .stExpander {{
        border: 1px solid var(--fin-glass-border) !important;
        border-radius: 12px !important;
        margin-bottom: 0.75rem !important;
        background: white !important;
    }}
    .stExpander summary {{
        font-weight: 600 !important;
        color: var(--fin-text-secondary) !important;
    }}

    /* Streamlit built-in metric override for alignment */
    [data-testid="stMetric"] {{
        background: white !important;
        border: 1px solid var(--fin-glass-border) !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
    }}

    [data-testid="stMetric"] label {{
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}

    /* Fix header margins for consistent section spacing */
    .stApp h3 {{
        margin-top: 0 !important;
        margin-bottom: 1rem !important;
    }}

    .stApp h4 {{
        margin-top: 0.5rem !important;
        margin-bottom: 0.75rem !important;
    }}

    /* Divider spacing */
    .stApp hr {{
        margin: 0.75rem 0 !important;
        border-color: var(--fin-glass-border) !important;
    }}

    /* Navbar Glassmorphism */
    header[data-testid="stHeader"] {{
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid var(--fin-glass-border) !important;
        transition: all 0.3s ease !important;
    }}

    [data-testid="stToolbar"] {{
        right: 1.5rem !important;
        top: 0.75rem !important;
    }}

</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000/api"

# ---------------------------------------------------------------------------
# Data Fetching — PostgreSQL via Connection Pool
# ---------------------------------------------------------------------------
# Uses the psycopg2 SimpleConnectionPool managed in src/db_service.py.
# Returns two DataFrames: loan_applications and loan_predictions.
# ---------------------------------------------------------------------------
def fetch_data():
    conn = get_connection()
    if not conn: return None, None
    try:
        apps_df = pd.read_sql("SELECT * FROM loan_applications ORDER BY created_at DESC", conn)
        preds_df = pd.read_sql("SELECT * FROM loan_predictions", conn)
        return apps_df, preds_df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None
    finally:
        if conn: release_connection(conn)

def metric_card(label, value, delta=None, delta_type="plus"):
    delta_html = ""
    if delta:
        cls = "delta-plus" if delta_type == "plus" else "delta-stable"
        icon = "↑" if delta_type == "plus" else "→"
        delta_html = f"<div class='metric-delta {cls}'>{icon} {delta}</div>"
        
    return f"""<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div>{delta_html}</div>"""

def glowing_badge(text, status_type="pending"):
    icon_map = {
        "APPROVED": "✓",
        "REJECTED": "✕",
        "PENDING": "⧗",
        "SENT": "✉",
        "DELIVERED": "✓",
        "FAILED": "!"
    }
    style_map = {
        "APPROVED": "badge-approved",
        "REJECTED": "badge-rejected",
        "PENDING": "badge-pending",
        "SENT": "badge-email-sent",
        "DELIVERED": "badge-approved",
        "FAILED": "badge-rejected"
    }
    
    text_up = text.upper()
    css_class = style_map.get(text_up, "badge-pending")
    icon = icon_map.get(text_up, "•")
    
    return f'<span class="glowing-badge {css_class}"><span style="margin-right: 6px; font-size: 0.8rem;">{icon}</span>{text}</span>'

# ---------------------------------------------------------------------------
# Actions — API Calls to FastAPI Backend
# ---------------------------------------------------------------------------
# These functions call the FastAPI endpoints to trigger AI predictions,
# batch processing, or manual overrides. Each endpoint runs background
# tasks for LLM email generation and database persistence.
# ---------------------------------------------------------------------------
def process_auto(loan_id):
    with st.spinner("🤖 Running AI Models..."):
        try:
            res = requests.post(f"{API_URL}/process-auto/{loan_id}")
            if res.status_code == 200:
                data = res.json()
                st.success(f"Processed successfully! Decision: {data['decision']}")
            else:
                st.error(f"Failed to process: {res.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")

def process_batch():
    with st.status("🚀 Processing Batch Applications...", expanded=True) as status:
        try:
            res = requests.post(f"{API_URL}/process-batch")
            if res.status_code == 200:
                data = res.json()
                st.write(f"🤖 {data['message']}")
                status.update(label="✅ Batch processing complete!", state="complete", expanded=False)
                st.toast(f"Processed {data['count']} applications!")
            else:
                st.error(f"Failed to start batch: {res.text}")
                status.update(label="❌ Batch failed", state="error")
        except Exception as e:
            st.error(f"Connection error: {e}")

def process_manual(loan_id, decision):
    with st.spinner(f"📝 Manually marking as {decision}..."):
        try:
            res = requests.post(f"{API_URL}/process-manual/{loan_id}", json={"decision": decision})
            if res.status_code == 200:
                st.success(f"Loan manually {decision.lower()}!")
            else:
                st.error(f"Failed: {res.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")

# ---------------------------------------------------------------------------
# Authentication System — Session + Query Param Persistence
# ---------------------------------------------------------------------------
# Uses st.session_state["password_correct"] with query param ?auth=true
# to persist login across Streamlit reruns and page refreshes.
# Default credentials: admin / admin  (configurable for production).
# ---------------------------------------------------------------------------
def check_password():
    # Persistence: Use query params to maintain session across refreshes
    if not st.session_state.get("password_correct"):
        if st.query_params.get("auth") == "true":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        # Ensure the URL stays primed for next refresh
        if st.query_params.get("auth") != "true":
            st.query_params["auth"] = "true"
        return True

    # Centered Institutional Login — hide sidebar on login screen
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
        [data-testid="stMain"] { margin-left: 0 !important; width: 100% !important; }
        
        /* Remove the outer white container on login page */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            backdrop-filter: none !important;
        }

        /* Top-aligned centering with navbar spacing */
        [data-testid="stMainBlockContainer"] {
            max-width: 580px !important;
            margin: 0 auto !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
            padding: 6vh 2rem 2rem 2rem !important;
            gap: 0 !important;
        }

        /* Mobile Responsiveness — fill most of the screen */
        @media (max-width: 700px) {
            [data-testid="stMainBlockContainer"] {
                max-width: 96% !important;
                padding: 4vh 1rem 1rem 1rem !important;
            }
            .login-glass-card h1 { font-size: 1.8rem !important; }
        }

        /* Force all nested containers to fill the width */
        [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"],
        [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] > div {
            width: 100% !important;
            max-width: none !important;
        }
        
        .login-glass-card {
            background: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(24px) !important;
            border: 1px solid rgba(226, 232, 240, 0.9) !important;
            border-bottom: none !important;
            border-radius: 24px 24px 0 0 !important;
            padding: 3.5rem 3rem 2rem 3rem !important;
            box-shadow: 0 10px 15px -10px rgba(0, 0, 0, 0.05) !important;
            text-align: center;
            margin-bottom: 0 !important;
            position: relative;
            z-index: 2;
        }

        /* Form styling to merge with card */
        [data-testid="stForm"] {
            border: 1px solid rgba(226, 232, 240, 0.9) !important;
            border-top: none !important; 
            padding: 1rem 3rem 3rem 3rem !important;
            background: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(24px) !important;
            border-radius: 0 0 24px 24px !important;
            box-shadow: 0 20px 25px -10px rgba(0, 0, 0, 0.1) !important;
            margin-top: -1px !important;
            z-index: 1;
        }

        /* Vertical spacing adjustment between inputs */
        [data-testid="stForm"] > div:first-child {
            gap: 1.25rem !important;
        }

        /* Error message visibility fix */
        [data-testid="stAlert"] {
            background-color: #fee2e2 !important;
            border: 1px solid #f87171 !important;
            margin-top: 1rem !important;
            border-radius: 10px !important;
        }
        [data-testid="stAlert"] p {
            color: #991b1b !important;
            font-weight: 600 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-glass-card">
        <img src='https://img.icons8.com/isometric/150/bank.png' style='width: 90px; margin-bottom: 1.5rem; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.05));'>
        <h1 style='font-family: Poppins, sans-serif; font-size: 2.2rem; font-weight: 800; color: #0f172a; margin: 0; letter-spacing: -0.03em; white-space: nowrap;'>Institutional Access</h1>
        <p style='color: #475569; font-size: 1.1rem; font-weight: 500; margin-top: 0.75rem; letter-spacing: 0.01em;'>Secure Decisioning Protocol</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("institutional_login"):
        username = st.text_input("Administrator Identifier", placeholder="admin")
        password = st.text_input("Security Protocol Key", type="password", placeholder="••••••••")
        if st.form_submit_button("Authenticate into Portal", use_container_width=True):
            if username == "admin" and password == "admin":
                st.session_state["password_correct"] = True
                st.query_params["auth"] = "true"
                st.rerun()
            else:
                st.error("Authentication Matrix Mismatch.")
    return False

if not check_password():
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar Controller — Collapsible Navigation Rail
# ---------------------------------------------------------------------------
# The sidebar toggles between 'full' (264px, labels visible) and 'mini'
# (72px, icon-only) modes. Navigation radio buttons map HTML icon+label
# strings back to clean route names for routing logic below.
# ---------------------------------------------------------------------------

with st.sidebar:
    # --- Flex-Lock Header ---
    st.markdown(f"""
    <div class="sidebar-header-lock">
        <div class="sidebar-brand">
            <div class="brand-dot"></div>
            <span>LI — SYS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Navigation ---
    st.markdown('<div class="nav-section-label">Institutional Portal</div>', unsafe_allow_html=True)

    nav_icons = ["⬡", "🛡️", "✉", "📊", "📜"]
    nav_labels = ["Overview", "Credit Engine", "Email Ops", "Analytics", "Audit Log"]
    
    html_labels = [f"{i}  {l}" for i, l in zip(nav_icons, nav_labels)]

    # Use a unique key and handle index mapping
    current_page = st.session_state.get('page', 'Overview')
    try:
        current_idx = nav_labels.index(current_page)
    except ValueError:
        current_idx = 0

    menu_choice = st.radio(
        "SIDEBAR_NAV",
        html_labels,
        index=current_idx,
        label_visibility="collapsed"
    )
    
    # Map back to clean labels for routing
    st.session_state.page = nav_labels[html_labels.index(menu_choice)]

    st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
    
    if st.button("⏻  Logout", key="logout_polish", use_container_width=True, type="primary"):
        st.session_state.password_correct = False
        st.query_params["auth"] = "false"
        st.rerun()

apps_df, preds_df = fetch_data()

# ---------------------------------------------------------------------------
# Data Preparation — Merge Applications + Predictions
# ---------------------------------------------------------------------------
# Joins the latest prediction per loan_id onto apps_df. Falls back to
# defaults (email_sent=False, prediction_id=0) when no predictions exist.
# ---------------------------------------------------------------------------
if apps_df is not None and not apps_df.empty:
    if preds_df is not None and not preds_df.empty:
        latest_preds = preds_df.sort_values('prediction_id').groupby('loan_id').last().reset_index()
        apps_df = apps_df.merge(latest_preds[['loan_id', 'email_sent', 'prediction_id']], on='loan_id', how='left')
    else:
        apps_df['email_sent'] = False
        apps_df['prediction_id'] = 0
    
    apps_df['email_sent'] = apps_df['email_sent'].fillna(False)
    apps_df['prediction_id'] = apps_df['prediction_id'].fillna(0)
    
    pending_df = apps_df[apps_df['status'] == 'PENDING']
    processed_df = apps_df[apps_df['status'] != 'PENDING'].sort_values('prediction_id', ascending=False)

    # -----------------------------------------------------------------------
    # NAVIGATION ROUTING
    # -----------------------------------------------------------------------
    _page = st.session_state.get('page', 'Overview')
    is_dashboard = _page == "Overview"
    is_prediction = _page == "Credit Engine"
    is_email = _page == "Email Ops"
    is_analytics = _page == "Analytics"
    is_history = _page == "Audit Log"

    if is_dashboard:
        st.markdown("""
        <div class='page-header'>
            <div class='ph-icon' style='background: rgba(79, 70, 229, 0.08); color: #4F46E5;'>🏦</div>
            <div class='ph-text'>
                <h3 style='color: #4F46E5;'>Executive Overview</h3>
                <p>Real-time institutional portfolio summary</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(metric_card("Pending Matrix", len(pending_df)), unsafe_allow_html=True)
        with c2: st.markdown(metric_card("Total Vault Assets", f"Rs.{apps_df['loan_amount'].sum()/1e7:.1f}Cr"), unsafe_allow_html=True)
        with c3: st.markdown(metric_card("System Health", "Optimal", "98.2%", "plus"), unsafe_allow_html=True)
        with c4: st.markdown(metric_card("AI Confidence", "89%", "Stable", "stable"), unsafe_allow_html=True)
        
        st.write("")
        st.markdown("### 📋 Recent Bloomberg Panel")
        recent = processed_df.head(10).copy()
        
        table_html = "<div class='fin-card'><div class='table-container'><table class='bloomberg-table'><thead><tr><th class='col-id'>ID</th><th class='col-applicant'>APPLICANT</th><th class='col-amount'>AMOUNT</th><th class='col-decision'>DECISION</th></tr></thead><tbody>"
        
        for _, r in recent.iterrows():
            table_html += f"<tr><td class='col-id'>{r['loan_id']}</td><td class='col-applicant' style='font-weight: 600;'>{r['applicant_name']}</td><td class='col-amount'>Rs.{r['loan_amount']:,.0f}</td><td class='col-decision'>{glowing_badge(r['status'])}</td></tr>"
        
        table_html += "</tbody></table></div></div>"
        st.markdown(table_html, unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # 2. LOAN PREDICTIONS (PENDING)
    # -----------------------------------------------------------------------
    elif is_prediction:
        st.markdown("""
        <div class='page-header'>
            <div class='ph-icon' style='background: rgba(244, 63, 94, 0.08); color: #F43F5E;'>🛡️</div>
            <div class='ph-text'>
                <h3 style='color: #F43F5E;'>Credit Prediction Gateway</h3>
                <p>Evaluate and process pending loan applications</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_h1, col_h2 = st.columns([1, 4])
        if not pending_df.empty:
            if st.button("🚀 Execute Batch Intelligence", type="primary"):
                process_batch()
                st.rerun()

        if pending_df.empty:
            st.success("✨ All caught up! No pending evaluations required.")
        else:
            items_per_page = 5
            pages = (len(pending_df) - 1) // items_per_page + 1
            if "p_page" not in st.session_state: st.session_state.p_page = 1
            
            start_idx = (st.session_state.p_page - 1) * items_per_page
            current_p_df = pending_df.iloc[start_idx:start_idx + items_per_page]
            
            for _, r in current_p_df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class='fin-card' style='padding: 1.25rem 1.5rem; border-left: 4px solid #F43F5E;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <h4 style='margin: 0; font-size: 1.05rem; font-weight: 700;'>{r['applicant_name']}</h4>
                                <div style='font-size: 0.82rem; color: #475569; font-weight: 600; margin-top: 4px;'>Protocol ID: #{r['loan_id']} &nbsp;•&nbsp; Rs.{r['loan_amount']:,.0f} Requested</div>
                            </div>
                            {glowing_badge(r['status'])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("🔍 View System Metadata / Form Data", expanded=False):
                        m1, m2 = st.columns(2)
                        with m1:
                            st.markdown(f"**Contact:** `{r['applicant_email']}`")
                            st.markdown(f"**Dependents:** {r['no_of_dependents']}")
                            st.markdown(f"**Education:** {r['education']}")
                        with m2:
                            st.markdown(f"**Income:** Rs.{r['income_annum']:,.0f}")
                            st.markdown(f"**Term:** {r['loan_term']} Months")
                            st.markdown(f"**CIBIL:** `{r['cibil_score']}`")
                        
                        st.markdown("<div style='margin: 10px 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)
                        st.markdown("**Asset Audit (Lakhs):**")
                        a1, a2, a3, a4 = st.columns(4)
                        a1.metric("Resid.", f"{r['residential_assets_value']/1e5:.1f}L")
                        a2.metric("Comm.", f"{r['commercial_assets_value']/1e5:.1f}L")
                        a3.metric("Luxury", f"{r['luxury_assets_value']/1e5:.1f}L")
                        a4.metric("Bank", f"{r['bank_asset_value']/1e5:.1f}L")
                    
                    ac1, ac2, ac3 = st.columns([1, 1, 1])
                    if ac1.button(f"🤖 AI Flow", key=f"auto_{r['loan_id']}", use_container_width=True):
                        process_auto(r['loan_id']); st.rerun()
                    if ac2.button("✅ Approve", key=f"app_{r['loan_id']}", use_container_width=True):
                        process_manual(r['loan_id'], "APPROVED"); st.rerun()
                    if ac3.button("❌ Reject", key=f"rej_{r['loan_id']}", use_container_width=True):
                        process_manual(r['loan_id'], "REJECTED"); st.rerun()
                    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

            if pages > 1:
                st.divider()
                p1, p2, p3 = st.columns([1, 2, 1])
                if p1.button("⬅️ Prev", disabled=st.session_state.p_page == 1): st.session_state.p_page -= 1; st.rerun()
                p2.markdown(f"<center>Page {st.session_state.p_page} of {pages}</center>", unsafe_allow_html=True)
                if p3.button("Next ➡️", disabled=st.session_state.p_page == pages): st.session_state.p_page += 1; st.rerun()

    # -----------------------------------------------------------------------
    # 3. EMAIL TRACKING
    # -----------------------------------------------------------------------
    elif is_email:
        st.markdown("""
        <div class='page-header'>
            <div class='ph-icon' style='background: rgba(14, 165, 233, 0.08); color: #0EA5E9;'>📨</div>
            <div class='ph-text'>
                <h3 style='color: #0EA5E9;'>Dispatch Control Center</h3>
                <p>Track email notifications for processed applications</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        tracked = apps_df[apps_df['status'] != 'PENDING'].copy()
        
        if tracked.empty:
            st.info("No dispatches processed in the current epoch.")
        else:
            # KPI summary row
            sent_count = tracked['email_sent'].sum()
            pending_count = len(tracked) - sent_count
            ek1, ek2, ek3 = st.columns(3)
            with ek1: st.markdown(metric_card("Total Dispatched", len(tracked)), unsafe_allow_html=True)
            with ek2: st.markdown(metric_card("Emails Sent", int(sent_count), None, "plus"), unsafe_allow_html=True)
            with ek3: st.markdown(metric_card("Pending Dispatch", int(pending_count)), unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            
            for _, r in tracked.iterrows():
                email_color = '#10B981' if r['email_sent'] else '#F59E0B'
                st.markdown(f"""
                <div class='fin-card' style='padding: 1.25rem 1.5rem; border-left: 4px solid {email_color};'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='font-weight: 700; font-size: 1rem;'>{r['applicant_name']}</span>
                            <span style='color:#64748b; font-size: 0.85rem; margin-left: 8px;'>{r['applicant_email']}</span>
                        </div>
                        {glowing_badge('SENT' if r['email_sent'] else 'PENDING')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # 4. MARKET ANALYTICS
    # -----------------------------------------------------------------------
    elif is_analytics:
        st.markdown("""
        <div class='page-header'>
            <div class='ph-icon' style='background: rgba(16, 185, 129, 0.08); color: #10B981;'>📊</div>
            <div class='ph-text'>
                <h3 style='color: #10B981;'>Quantitative Intelligence</h3>
                <p>Data-driven insights and portfolio analytics</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if processed_df.empty:
            st.warning("Insufficient data for quantitative discovery.")
        else:
            # KPI Row
            k1, k2, k3, k4 = st.columns(4)
            app_rate = (len(processed_df[processed_df['status'] == 'APPROVED']) / len(processed_df) * 100)
            avg_amount = processed_df['loan_amount'].mean()
            
            with k1: st.markdown(metric_card("Analyzed Assets", len(processed_df)), unsafe_allow_html=True)
            with k2: st.markdown(metric_card("Approval Rate", f"{app_rate:.1f}%", "Target 85%", "plus"), unsafe_allow_html=True)
            with k3: st.markdown(metric_card("Avg Exposure", f"Rs.{avg_amount/1e5:.1f}L"), unsafe_allow_html=True)
            with k4: st.markdown(metric_card("Risk Vector", "Stability", "Optimal", "stable"), unsafe_allow_html=True)
            
            st.write("")
            ch1, ch2 = st.columns([2, 3])
            with ch1:
                with st.container(border=True):
                    st.markdown("### 🎯 Decision Mix")
                    fig = px.pie(processed_df, names='status', hole=0.7, color='status', color_discrete_map={'APPROVED': '#10B981', 'REJECTED': '#F43F5E', 'PENDING': '#F59E0B'})
                    fig.update_layout(
                        template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                        showlegend=True, margin=dict(t=10, b=10, l=10, r=10),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
                        font=dict(family="Inter", color="#0f172a")
                    )
                    st.plotly_chart(fig, use_container_width=True, theme=None)
            with ch2:
                with st.container(border=True):
                    st.markdown("### 🔥 Credit Index Distribution")
                    fig2 = px.histogram(processed_df, x="cibil_score", color="status", nbins=20, color_discrete_map={'APPROVED': '#10B981', 'REJECTED': '#F43F5E', 'PENDING': '#F59E0B'})
                    fig2.update_layout(
                        template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        bargap=0.1, margin=dict(t=10, b=10, l=10, r=10),
                        xaxis_title="CIBIL Score Spectrum", yaxis_title="Volume",
                        font=dict(family="Inter", color="#0f172a")
                    )
                    st.plotly_chart(fig2, use_container_width=True, theme=None)
            
            st.write("")
            with st.container(border=True):
                st.markdown("### 🏛️ Collateral Value Variance")
                melted = processed_df.melt(id_vars=['status'], value_vars=['residential_assets_value', 'commercial_assets_value', 'luxury_assets_value'])
                fig3 = px.box(melted, x="variable", y="value", color="status", color_discrete_map={'APPROVED': '#10B981', 'REJECTED': '#F43F5E', 'PENDING': '#F59E0B'})
                fig3.update_layout(
                    template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                    boxmode="group", margin=dict(t=10, b=10, l=10, r=10),
                    xaxis_title="Collateral Asset Pool", yaxis_title="Valuation (Rs.)",
                    font=dict(family="Inter", color="#0f172a")
                )
                st.plotly_chart(fig3, use_container_width=True, theme=None)

    # -----------------------------------------------------------------------
    # 5. DECISION HISTORY
    # -----------------------------------------------------------------------
    elif is_history:
        st.markdown("""
        <div class='page-header'>
            <div class='ph-icon' style='background: rgba(245, 158, 11, 0.08); color: #F59E0B;'>📜</div>
            <div class='ph-text'>
                <h3 style='color: #F59E0B;'>Institutional Ledger</h3>
                <p>Complete record of all processed decisions</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if processed_df.empty:
            st.info("Ledger is currently empty.")
        else:
            h_items_per_page = 15
            h_total = len(processed_df)
            h_pages = (h_total - 1) // h_items_per_page + 1
            
            if "h_page" not in st.session_state: st.session_state.h_page = 1
            
            h_start = (st.session_state.h_page - 1) * h_items_per_page
            h_df_display = processed_df.iloc[h_start:h_start + h_items_per_page]
            
            st.markdown(f"#### 📜 Institutional Ledger Slice (Page {st.session_state.h_page})")
            
            ledger_html = "<div class='fin-card'><div class='table-container'><table class='bloomberg-table'><thead><tr><th class='col-id'>ID</th><th class='col-applicant'>APPLICANT</th><th class='col-amount'>AMOUNT</th><th class='col-decision'>DECISION</th><th class='col-email'>EMAIL</th></tr></thead><tbody>"
            
            for _, r in h_df_display.iterrows():
                email_status = "SENT" if r['email_sent'] else "PENDING"
                ledger_html += f"<tr><td class='col-id'>{r['loan_id']}</td><td class='col-applicant' style='font-weight: 600;'>{r['applicant_name']}</td><td class='col-amount'>Rs.{r['loan_amount']:,.0f}</td><td class='col-decision'>{glowing_badge(r['status'])}</td><td class='col-email'>{glowing_badge(email_status, 'sent' if r['email_sent'] else 'pending')}</td></tr>"
            
            ledger_html += "</tbody></table></div></div>"
            st.markdown(ledger_html, unsafe_allow_html=True)
            
            if h_pages > 1:
                hc1, hc2, hc3 = st.columns([1, 2, 1])
                if hc1.button("⬅️ Previous", disabled=st.session_state.h_page == 1): st.session_state.h_page -= 1; st.rerun()
                hc2.markdown(f"<center style='color: #475569; font-size: 0.9rem; margin-top: 0.5rem;'>Repository Page {st.session_state.h_page} / {h_pages}</center>", unsafe_allow_html=True)
                if hc3.button("Next ➡️", disabled=st.session_state.h_page == h_pages): st.session_state.h_page += 1; st.rerun()

else:
    st.markdown("""
    <div style='background: rgba(79, 70, 229, 0.06); padding: 4rem 2rem; border-radius: 20px; text-align: center; border: 2px dashed rgba(79, 70, 229, 0.3);'>
        <div style='font-size: 3rem; margin-bottom: 1rem;'>🏦</div>
        <h2 style='color: #4F46E5; font-family: Poppins, sans-serif; font-weight: 700; margin-bottom: 0.75rem;'>System Primed & Ready</h2>
        <p style='color: #64748b; font-size: 1rem; max-width: 400px; margin: 0 auto;'>No institutional applications detected in the current epoch. Submit applications through the Customer Portal to get started.</p>
    </div>
    """, unsafe_allow_html=True)
