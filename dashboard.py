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
if "sidebar_view" not in st.session_state: st.session_state.sidebar_view = "full"
if "h_page" not in st.session_state: st.session_state.h_page = 1
if "p_page" not in st.session_state: st.session_state.p_page = 1
if "password_correct" not in st.session_state: st.session_state.password_correct = False

# ---------------------------------------------------------------------------
# CUSTOM CSS FOR PREMIUM LOOK
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --fin-indigo: #4F46E5;
        --fin-rose: #F43F5E;
        --fin-emerald: #10B981;
        --fin-amber: #F59E0B;
        --fin-sky: #0EA5E9;
        
        --fin-bg-gradient: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        --fin-glass-surface: rgba(30, 41, 59, 0.7);
        --fin-glass-border: rgba(255, 255, 255, 0.1);
        --fin-glass-glow: rgba(79, 70, 229, 0.15);
        
        --fin-text-primary: #f8fafc;
        --fin-text-secondary: #94a3b8;
        /* High-Performance Typography */
    .stApp {
        background: var(--fin-bg-gradient);
        color: var(--fin-text-primary);
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 { 
        font-family: 'Poppins', sans-serif !important; 
        font-weight: 700 !important; 
        color: var(--fin-text-primary);
        letter-spacing: -0.02em;
    }

    .stripe-header { 
        color: var(--fin-indigo); 
        font-weight: 800; 
        letter-spacing: -0.05em; 
        font-size: 2.2rem;
        margin-bottom: 2rem;
    }

    /* Glassmorphism System */
    .fin-card {
        background: var(--fin-glass-surface);
        backdrop-filter: blur(20px);
        border: 1px solid var(--fin-glass-border);
        border-radius: 1.25rem;
        padding: 1.5rem;
        box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.4);
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .fin-card:hover { 
        border-color: var(--fin-indigo); 
        transform: translateY(-4px);
        box-shadow: 0 20px 40px -10px rgba(79, 70, 229, 0.2);
    }

    /* Vertical Navigation Rail System - Absolute Hard-Lock */
    section[data-testid="stSidebar"], 
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarUserContent"] {
        width: {"64px" if st.session_state.get("sidebar_view") == "mini" else "300px"} !important;
        min-width: {"64px" if st.session_state.get("sidebar_view") == "mini" else "300px"} !important;
        max-width: {"64px" if st.session_state.get("sidebar_view") == "mini" else "300px"} !important;
        flex-basis: {"64px" if st.session_state.get("sidebar_view") == "mini" else "300px"} !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        overflow-x: hidden !important;
    }

    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 1) !important;
        border-right: 1px solid var(--fin-glass-border) !important;
        z-index: 1000 !important;
        display: {"none" if not st.session_state.get("password_correct") else "block"} !important;
    }

    /* Padding sync for Ultra-Slim Rail vs Full */
    [data-testid="stSidebarUserContent"], 
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding: {"0px !important" if st.session_state.get("sidebar_view") == "mini" else "1.5rem 1rem !important"};
        gap: {"0px !important" if st.session_state.get("sidebar_view") == "mini" else "1rem !important"};
    }

    /* Main Content Hard-Shift */
    [data-testid="stMain"] {
        margin-left: {"0px" if not st.session_state.get("password_correct") else "64px" if st.session_state.get("sidebar_view") == "mini" else "300px"} !important;
        transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    [data-testid="stSidebarNav"] { display: none !important; }

    .stRadio [role="radiogroup"] {
        gap: 0.8rem;
        padding: 1rem 10px;
    }

    .stRadio label {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid transparent;
        border-radius: 14px;
        padding: 0.9rem !important;
        color: var(--fin-text-secondary) !important;
        transition: all 0.3s ease;
        cursor: pointer;
        width: 100%;
        display: flex;
        align-items: center;
        white-space: nowrap;
    }

    /* Mini State Refinements - Button-Style Navigation Sync */
    {"[data-testid='stSidebar'] .stRadio { padding: 0 !important; margin: 0 !important; overflow: visible !important; }" if st.session_state.get("sidebar_view") == "mini" else ""}
    {"[data-testid='stSidebar'] .stRadio label { justify-content: center !important; padding: 0 !important; border-radius: 12px !important; height: 52px !important; width: 52px !important; margin: 0.6rem auto !important; display: flex !important; align-items: center !important; border: 1px solid var(--fin-glass-border) !important; background: rgba(255,255,255,0.03) !important; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important; position: relative !important; left: -2px !important; }" if st.session_state.get("sidebar_view") == "mini" else ""}
    {"[data-testid='stSidebar'] .stRadio label p { font-size: 1.8rem !important; display: flex !important; justify-content: center !important; align-items: center !important; width: 100% !important; margin: 0 !important; line-height: 1 !important; text-align: center !important; opacity: 1 !important; visibility: visible !important; color: white !important; }" if st.session_state.get("sidebar_view") == "mini" else ""}
    
    /* Highlight the selected "Button" */
    {"[data-testid='stSidebar'] .stRadio label:has(input:checked) { border-color: var(--fin-indigo) !important; background: rgba(79, 70, 229, 0.2) !important; box-shadow: 0 0 15px rgba(79, 70, 229, 0.2) !important; }" if st.session_state.get("sidebar_view") == "mini" else ""}

    /* Absolute Marker Removal - Circles only */
    [data-testid="stSidebar"] [data-testid="stMarker"] { 
        display: none !important; 
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
    }

    /* Hide default radio circle container specifically */
    [data-testid="stSidebar"] div[role="radiogroup"] > div > label > div:first-child { 
        display: none !important; 
        width: 0 !important; 
    }
    
    {"[data-testid='stSidebar'] .stripe-header, [data-testid='stSidebar'] [data-testid='stWidgetLabel'], [data-testid='stSidebar'] .fin-divider { opacity: 0; height: 0; margin: 0; padding: 0; overflow: hidden; visibility: hidden; pointer-events: none; }" if st.session_state.get("sidebar_view") == "mini" else ""}

    .stRadio label:hover {
        background: rgba(79, 70, 229, 0.1) !important;
        border-color: rgba(79, 70, 229, 0.3) !important;
    }

    .stRadio [data-testid="stWidgetLabel"] p {
        color: var(--fin-indigo) !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        font-size: 0.65rem;
        letter-spacing: 0.12rem;
        margin-bottom: 0.5rem;
    }

    /* Button Refinement */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid var(--fin-glass-border) !important;
        color: var(--fin-text-primary) !important;
        width: 100%;
    }

    .stButton > button:hover {
        border-color: var(--fin-indigo) !important;
        background: rgba(79, 70, 229, 0.15) !important;
        transform: translateY(-2px);
    }

    .stButton > button[kind="primary"] {
        background: var(--fin-indigo) !important;
        border: none !important;
        box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.4);
    }

    .stButton > button[kind="primary"]:hover {
        background: #4338CA !important;
        box-shadow: 0 15px 25px -5px rgba(79, 70, 229, 0.6);
    }

    /* Metric Refinement - Custom Card Overrides */
    .metric-card {
        background: var(--fin-glass-surface);
        backdrop-filter: blur(12px);
        border: 1px solid var(--fin-glass-border);
        border-left: 4px solid var(--fin-indigo);
        border-radius: 1rem;
        padding: 1.25rem;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: var(--fin-indigo);
        background: rgba(79, 70, 229, 0.1);
        transform: translateY(-2px);
    }
    .metric-label { color: var(--fin-text-secondary); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
    .metric-value { color: var(--fin-text-primary); font-size: 1.75rem; font-weight: 800; line-height: 1.2; }
    .metric-delta { font-size: 0.8rem; font-weight: 600; margin-top: 0.25rem; }
    .delta-plus { color: var(--fin-emerald); }
    .delta-stable { color: var(--fin-sky); }

    /* Bloomberg Table Precision */
    .bloomberg-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    .bloomberg-table th { 
        text-align: left; 
        padding: 15px 12px; 
        color: var(--fin-text-secondary); 
        font-size: 0.75rem; 
        text-transform: uppercase; 
        letter-spacing: 0.1em;
        border-bottom: 2px solid var(--fin-glass-border);
    }
    .bloomberg-table td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.03); }
    .bloomberg-table tr:last-child td { border-bottom: none; }
    .col-id { width: 8%; }
    .col-applicant { width: 35%; }
    .col-amount { width: 17%; }
    .col-decision { width: 20%; }
    .col-email { width: 20%; }

    /* Custom Gradient Divider */
    .fin-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--fin-glass-border), transparent);
        margin: 2rem 0;
    }

    /* Glowing Status Badges */
    .glowing-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border: 1px solid transparent;
        animation: glow-pulse 2s infinite ease-in-out;
    }

    @keyframes glow-pulse {
        0% { transform: scale(1); box-shadow: 0 0 5px transparent; }
        50% { transform: scale(1.02); box-shadow: 0 0 15px currentColor; }
        100% { transform: scale(1); box-shadow: 0 0 5px transparent; }
    }

    .badge-approved { background: rgba(16, 185, 129, 0.1); color: var(--fin-emerald); border-color: var(--fin-emerald); }
    .badge-rejected { background: rgba(244, 63, 94, 0.1); color: var(--fin-rose); border-color: var(--fin-rose); }
    .badge-pending { background: rgba(245, 158, 11, 0.1); color: var(--fin-amber); border-color: var(--fin-amber); }
    .badge-email-sent { background: rgba(79, 70, 229, 0.1); color: var(--fin-indigo); border-color: var(--fin-indigo); }

    /* Forms and Inputs */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid var(--fin-glass-border) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    .stTextInput input:focus { border-color: var(--fin-indigo) !important; }

    /* Hide default radio circle */
    [data-testid="stRadio"] div[role="radiogroup"] > div > label > div:first-child { display: none !important; }

    /* Institutional Login Portal - Precision Balanced */
    .institutional-box {
        max-width: 360px;
        margin: 5rem auto 1rem auto;
        padding: 2rem;
        border-radius: 1.5rem;
        background: rgba(15, 23, 42, 0.95);
        border: 2px solid var(--fin-indigo);
        box-shadow: 0 0 50px rgba(79, 70, 229, 0.2);
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .institutional-box h1 { font-size: 1.2rem !important; margin-top: 0.75rem !important; color: white !important; text-align: center; }
    .institutional-box p { font-size: 0.7rem !important; color: #94a3b8 !important; margin-bottom: 1rem !important; text-align: center; }
    .institutional-box img { width: 40px !important; margin-bottom: 0.5rem; }

    /* Main Container Padding */
    .main .block-container { padding-top: 3rem !important; }
</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000/api"

# ---------------------------------------------------------------------------
# Data Fetching
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
# Actions
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
# Authentication System
# ---------------------------------------------------------------------------
def check_password():
    if "password_correct" not in st.session_state:
        if st.query_params.get("auth") == "true":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Centered Institutional Login
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div class='institutional-box'>
            <img src='https://img.icons8.com/isometric/150/bank.png'>
            <h1>Institutional Access</h1>
            <p>AI-Powered Credit Decisioning Protocol</p>
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
        st.markdown("</div>", unsafe_allow_html=True)
    return False

if not check_password():
    st.stop()

# Sidebar Controller
with st.sidebar:
    if st.session_state.sidebar_view == "full":
        sc1, sc2 = st.columns([3, 1])
        with sc1:
            st.markdown("<h1 class='stripe-header' style='margin-bottom:0;'>LI-SYS</h1>", unsafe_allow_html=True)
        with sc2:
            if st.button("←", help="Collapse Sidebar"):
                st.session_state.sidebar_view = "mini"
                st.rerun()
    else:
        if st.button("≡", help="Expand Sidebar"):
            st.session_state.sidebar_view = "full"
            st.rerun()

    st.markdown("<div class='fin-divider'></div>", unsafe_allow_html=True)
    
    # Navigation Layout
    if st.session_state.sidebar_view == "mini":
        st.write("") # Tiny vertical spacer
    
    nav_icons = ["🏛️", "🔍", "📬", "📊", "📜"]
    nav_labels = ["Dashboard Overview", "Credit Prediction", "Email Tracking", "Market Analytics", "Decision History"]
    
    # Inject icons into labels for CSS access
    html_labels = []
    for icon, label in zip(nav_icons, nav_labels):
        if st.session_state.sidebar_view == "mini":
            html_labels.append(f"{icon}")
        else:
            html_labels.append(f"{icon} {label}")

    menu = st.radio(
        "NETWORK NAVIGATION",
        html_labels,
        index=0,
        label_visibility="collapsed" if st.session_state.sidebar_view == "mini" else "visible"
    )
    
    # Force full labels to have consistent icon sizing via span injection if needed, 
    # but radio labels handle text well. We'll add a CSS rule for the radio label font size.
    st.markdown("<style>.stRadio label p { font-size: 1.1rem; }</style>", unsafe_allow_html=True)
    st.markdown("<div class='fin-divider'></div>", unsafe_allow_html=True)
    
    if st.session_state.sidebar_view == "full":
        if st.button("🔓 End Session", use_container_width=True):
            st.session_state["password_correct"] = False
            st.query_params["auth"] = "false"
            st.rerun()
    else:
        if st.button("🔓", help="End Session"):
            st.session_state["password_correct"] = False
            st.query_params["auth"] = "false"
            st.rerun()

apps_df, preds_df = fetch_data()

# Data Preparation Logic
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
    is_dashboard = menu.startswith("🏛️")
    is_prediction = menu.startswith("🔍")
    is_email = menu.startswith("📬")
    is_analytics = menu.startswith("📊")
    is_history = menu.startswith("📜")

    if is_dashboard:
        st.markdown("<h2 style='color: #4F46E5;'>Executive Overview</h2>", unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(metric_card("Pending Matrix", len(pending_df)), unsafe_allow_html=True)
        with c2: st.markdown(metric_card("Total Vault Assets", f"₹{apps_df['loan_amount'].sum()/1e7:.1f}Cr"), unsafe_allow_html=True)
        with c3: st.markdown(metric_card("System Health", "Optimal", "98.2%", "plus"), unsafe_allow_html=True)
        with c4: st.markdown(metric_card("AI Confidence", "89%", "Stable", "stable"), unsafe_allow_html=True)
        
        st.write("")
        st.markdown("### 📋 Recent Bloomberg Panel")
        recent = processed_df.head(10).copy()
        
        table_html = "<div class='fin-card'><table class='bloomberg-table'><thead><tr><th class='col-id'>ID</th><th class='col-applicant'>APPLICANT</th><th class='col-amount'>AMOUNT</th><th class='col-decision'>DECISION</th></tr></thead><tbody>"
        
        for _, r in recent.iterrows():
            table_html += f"<tr><td class='col-id'>{r['loan_id']}</td><td class='col-applicant' style='font-weight: 600;'>{r['applicant_name']}</td><td class='col-amount'>₹{r['loan_amount']:,.0f}</td><td class='col-decision'>{glowing_badge(r['status'])}</td></tr>"
        
        table_html += "</tbody></table></div>"
        st.markdown(table_html, unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # 2. LOAN PREDICTIONS (PENDING)
    # -----------------------------------------------------------------------
    elif is_prediction:
        st.markdown("<h2 style='color: #F43F5E;'>Credit Prediction Gateway</h2>", unsafe_allow_html=True)
        
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
                    <div class='fin-card' style='padding: 1rem; margin-bottom: 0.5rem; border-left: 4px solid #F43F5E;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <h4 style='margin: 0; font-size: 1rem;'>{r['applicant_name']}</h4>
                                <div style='font-size: 0.8rem; color: #94a3b8; font-weight: 600;'>Protocol ID: #{r['loan_id']} | ₹{r['loan_amount']:,.0f} Requested</div>
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
                            st.markdown(f"**Income:** ₹{r['income_annum']:,.0f}")
                            st.markdown(f"**Term:** {r['loan_term']} Months")
                            st.markdown(f"**CIBIL:** `{r['cibil_score']}`")
                        
                        st.markdown("<div style='margin: 10px 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)
                        st.markdown("**Asset Audit (Lakhs):**")
                        a1, a2, a3, a4 = st.columns(4)
                        a1.metric("Resid.", f"{r['residential_assets_value']/1e5:.1f}L")
                        a2.metric("Comm.", f"{r['commercial_assets_value']/1e5:.1f}L")
                        a3.metric("Luxury", f"{r['luxury_assets_value']/1e5:.1f}L")
                        a4.metric("Bank", f"{r['bank_asset_value']/1e5:.1f}L")
                    
                    ac1, ac2, ac3 = st.columns([2, 1, 1])
                    if ac1.button(f"🤖 AI Flow #{r['loan_id']}", key=f"auto_{r['loan_id']}", use_container_width=True):
                        process_auto(r['loan_id']); st.rerun()
                    if ac2.button("✅ Appr", key=f"app_{r['loan_id']}", use_container_width=True):
                        process_manual(r['loan_id'], "APPROVED"); st.rerun()
                    if ac3.button("❌ Rej", key=f"rej_{r['loan_id']}", use_container_width=True):
                        process_manual(r['loan_id'], "REJECTED"); st.rerun()
                    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

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
        st.markdown("<h2 style='color: #0EA5E9;'>Dispatch Control Center</h2>", unsafe_allow_html=True)
        tracked = apps_df[apps_df['status'] != 'PENDING'].copy()
        
        if tracked.empty:
            st.info("No dispatches processed in the current epoch.")
        else:
            for _, r in tracked.iterrows():
                st.markdown(f"""
                <div class='fin-card' style='margin-bottom: 10px; padding: 1rem;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <span><b>{r['applicant_name']}</b> <small style='color:#94a3b8;'>({r['applicant_email']})</small></span>
                        {glowing_badge('SENT' if r['email_sent'] else 'PENDING')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # 4. MARKET ANALYTICS
    # -----------------------------------------------------------------------
    elif is_analytics:
        st.markdown("<h2 style='color: #10B981;'>Quantitative Insights</h2>", unsafe_allow_html=True)
        if processed_df.empty:
            st.warning("Insufficient data for quantitative analysis.")
        else:
            ch1, ch2 = st.columns(2)
            with ch1:
                st.markdown("### 🎯 Decision Mix")
                fig = px.pie(processed_df, names='status', hole=0.7, color_discrete_sequence=['#4F46E5', '#F43F5E', '#10B981'])
                fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
            with ch2:
                st.markdown("### 🔥 Credit Indexing")
                fig2 = px.histogram(processed_df, x="cibil_score", color="status", nbins=20, color_discrete_sequence=['#4F46E5', '#F43F5E'])
                fig2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
            
            # Asset Ratio
            st.write("")
            st.markdown("### 🏛️ Asset-to-Loan Exposure")
            melted = processed_df.melt(id_vars=['status'], value_vars=['residential_assets_value', 'commercial_assets_value', 'luxury_assets_value'])
            fig3 = px.box(melted, x="variable", y="value", color="status", color_discrete_sequence=['#4F46E5', '#F43F5E'])
            fig3.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', boxmode="overlay")
            st.plotly_chart(fig3, use_container_width=True)

    # -----------------------------------------------------------------------
    # 5. DECISION HISTORY
    # -----------------------------------------------------------------------
    elif is_history:
        st.markdown("<h2 style='color: #F59E0B;'>Institutional Ledger</h2>", unsafe_allow_html=True)
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
            
            ledger_html = "<div class='fin-card'><table class='bloomberg-table'><thead><tr><th class='col-id'>ID</th><th class='col-applicant'>APPLICANT</th><th class='col-amount'>AMOUNT</th><th class='col-decision'>DECISION</th><th class='col-email'>EMAIL</th></tr></thead><tbody>"
            
            for _, r in h_df_display.iterrows():
                email_status = "SENT" if r['email_sent'] else "PENDING"
                ledger_html += f"<tr><td class='col-id'>{r['loan_id']}</td><td class='col-applicant' style='font-weight: 600;'>{r['applicant_name']}</td><td class='col-amount'>₹{r['loan_amount']:,.0f}</td><td class='col-decision'>{glowing_badge(r['status'])}</td><td class='col-email'>{glowing_badge(email_status, 'sent' if r['email_sent'] else 'pending')}</td></tr>"
            
            ledger_html += "</tbody></table></div>"
            st.markdown(ledger_html, unsafe_allow_html=True)
            
            if h_pages > 1:
                hc1, hc2, hc3 = st.columns([1, 2, 1])
                if hc1.button("⬅️ Previous", disabled=st.session_state.h_page == 1): st.session_state.h_page -= 1; st.rerun()
                hc2.markdown(f"<center style='color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;'>Repository Page {st.session_state.h_page} / {h_pages}</center>", unsafe_allow_html=True)
                if hc3.button("Next ➡️", disabled=st.session_state.h_page == h_pages): st.session_state.h_page += 1; st.rerun()

else:
    st.markdown("""
    <div style='background: rgba(79, 70, 229, 0.1); padding: 3rem; border-radius: 1.5rem; text-align: center; border: 2px dashed #4F46E5;'>
        <h2 style='color: #4F46E5;'>System Primed & Ready</h2>
        <p style='color: #94a3b8;'>No institutional applications detected in the current epoch.</p>
    </div>
    """, unsafe_allow_html=True)
