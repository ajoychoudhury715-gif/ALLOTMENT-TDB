import streamlit as st  # pyright: ignore[reportUndefinedVariable]
import pandas as pd # pyright: ignore[reportMissingModuleSource]
from datetime import datetime, time, timezone, timedelta
import os
import time as time_module  # for retry delays
import zipfile  # for BadZipFile exception handling
# Add missing import
import hashlib
import re  # for creating safe keys for buttons
import uuid  # for generating stable row IDs
import json

# Supabase integration (Postgres) for persistent cloud storage (no Google)
try:
    from supabase import create_client  # type: ignore
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False

# Google Sheets integration for persistent cloud storage
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

# To install required packages, run in your terminal:
# pip install --upgrade pip
# pip install pandas openpyxl streamlit streamlit-autorefresh gspread google-auth
# pip install streamlit

# Additional import for auto-refresh (optional)
try:
    from streamlit_autorefresh import st_autorefresh # pyright: ignore[reportMissingImports]
except Exception:
    st.error("Missing package 'streamlit-autorefresh'. Install with: pip install -r requirements.txt")
    # fallback no-op to avoid crashing if package is missing
    def st_autorefresh(interval=60000, debounce=True, key=None):
        return None

# Page config
st.set_page_config(page_title="ALLOTMENT", layout="wide", initial_sidebar_state="collapsed")

# ===== COLOR CUSTOMIZATION SECTION =====
# Easily modify these colors to change the entire theme
COLORS = {
    "bg_primary": "#ffffff",      # Main background (white)
    "bg_secondary": "#f5f5f5",    # Secondary background (light gray)
    "text_primary": "#111b26",    # Main text (dark)
    "text_secondary": "#99582f",  # Secondary text (brown)
    "button_bg": "#99582f",       # Button background (brown)
    "button_text": "#f9f9f9",     # Button text (light)
    "accent": "#c9bbb0",          # Accent color (beige)
    "success": "#10b981",         # Green for success
    "warning": "#f59e0b",         # Amber for warnings
    "danger": "#ef4444",          # Red for danger
    "info": "#3b82f6",            # Blue for info
}

# Custom CSS with customizable colors
st.markdown(
    f"""
    <style>
    :root {{
        --bg-primary: {COLORS['bg_primary']};
        --bg-secondary: {COLORS['bg_secondary']};
        --text-primary: {COLORS['text_primary']};
        --text-secondary: {COLORS['text_secondary']};
        --accent: {COLORS['accent']};
    }}
    
    * {{
        margin: 0;
        padding: 0;
    }}
    
    body, .stApp {{
        background: linear-gradient(135deg, #ffffff 0%, #f9f8f6 100%) !important;
        color: {COLORS['text_primary']} !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }}
    
    header {{
        background-color: {COLORS['bg_primary']} !important;
        border-bottom: none !important;
        padding: 1rem 0 !important;
    }}
    
    [data-testid="stHeader"] {{
        background-color: {COLORS['bg_primary']} !important;
    }}

    /* Hide GitHub/logo link in Streamlit header (Streamlit Cloud toolbar) */
    [data-testid="stToolbar"] a[href*="github.com"],
    [data-testid="stToolbar"] a[aria-label*="View source"],
    [data-testid="stToolbar"] a[title*="View source"],
    [data-testid="stToolbar"] a[aria-label*="GitHub"],
    [data-testid="stToolbar"] a[title*="GitHub"],
    [data-testid="stToolbar"] button[aria-label*="View source"],
    [data-testid="stToolbar"] button[title*="View source"] {{
        display: none !important;
    }}
    
    /* Professional main container */
    .main {{
        padding: 2rem 3rem !important;
    }}
    
    /* Professional header styling */
    .header-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
        padding: 2rem 0;
        border-bottom: none;
    }}
    
    .header-logo {{
        width: 80px;
        height: auto;
    }}
    
    .header-title {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['text_primary']};
        letter-spacing: 0.5px;
    }}
    
    .st-bw, .st-cq, .st-dx, .stDataFrame, .stDataFrame th, .stDataFrame td {{
        background-color: {COLORS['bg_secondary']} !important;
        color: {COLORS['text_primary']} !important;
    }}
    
    /* Premium Status-based row background colors with dynamic effects */
    /* Upcoming rows - Light blue */
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("WAITING")) {{
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.3) 0%, rgba(59, 130, 246, 0.1) 100%) !important;
        border-left: 5px solid {COLORS['info']} !important;
    }}
    
    /* Ongoing rows - Light green */
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("ON GOING")) {{
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.3) 0%, rgba(16, 185, 129, 0.1) 100%) !important;
        border-left: 5px solid {COLORS['success']} !important;
    }}
    
    /* Arrived rows - Light yellow */
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("ARRIVED")) {{
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.3) 0%, rgba(245, 158, 11, 0.1) 100%) !important;
        border-left: 5px solid {COLORS['warning']} !important;
    }}

    /* Shifted rows - Yellow */
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("SHIFTED")) {{
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.3) 0%, rgba(245, 158, 11, 0.1) 100%) !important;
        border-left: 5px solid {COLORS['warning']} !important;
    }}
    
    /* Cancelled rows - Light red */
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("CANCELLED")) {{
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.3) 0%, rgba(239, 68, 68, 0.1) 100%) !important;
        border-left: 5px solid {COLORS['danger']} !important;
    }}
    
    /* Enhanced Hover effect with shadow lift */
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("WAITING")):hover {{
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.5) 0%, rgba(59, 130, 246, 0.2) 100%) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) inset !important;
    }}
    
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("ON GOING")):hover {{
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.5) 0%, rgba(16, 185, 129, 0.2) 100%) !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) inset !important;
    }}
    
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("ARRIVED")):hover {{
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.5) 0%, rgba(245, 158, 11, 0.2) 100%) !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3) inset !important;
    }}

    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("SHIFTED")):hover {{
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.5) 0%, rgba(245, 158, 11, 0.2) 100%) !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3) inset !important;
    }}
    
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("CANCELLED")):hover {{
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.5) 0%, rgba(239, 68, 68, 0.2) 100%) !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) inset !important;
    }}
    
    /* Table Header Styling - Premium & Elegant */
    [data-testid="stDataFrameContainer"] thead {{
        background: linear-gradient(135deg, #99582f 0%, #99582f 100%) !important;
        border-bottom: 4px solid #f9f9f9 !important;
        box-shadow: 0 6px 18px rgba(153, 88, 47, 0.18) !important;
    }}
    
    [data-testid="stDataFrameContainer"] thead th {{
        color: #f9f9f9 !important;
        font-weight: 800 !important;
        padding: 18px 16px !important;
        text-align: center !important;
        font-size: 0.99rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        background: linear-gradient(135deg, #99582f 0%, #99582f 100%) !important;
        position: relative !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
        box-shadow: inset 0 1px 0 rgba(249, 249, 249, 0.18) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border-right: 1px solid rgba(249, 249, 249, 0.22) !important;
    }}
    
    [data-testid="stDataFrameContainer"] thead th:last-child {{
        border-right: none !important;
    }}
    
    [data-testid="stDataFrameContainer"] thead th:hover {{
        filter: brightness(1.08) !important;
        transform: translateY(-2px) !important;
        box-shadow: inset 0 1px 0 rgba(249, 249, 249, 0.28), 0 10px 22px rgba(153, 88, 47, 0.20) !important;
    }}
    
    /* Premium Table Rows */
    [data-testid="stDataFrameContainer"] tbody tr {{
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border-radius: 0 !important;
        position: relative !important;
    }}
    
    /* Alternating row background for better readability */
    [data-testid="stDataFrameContainer"] tbody tr:nth-child(even) {{
        background-color: rgba(201, 187, 176, 0.08) !important;
    }}
    
    [data-testid="stDataFrameContainer"] tbody tr:hover {{
        background-color: rgba(201, 187, 176, 0.14) !important;
        box-shadow: 0 2px 10px rgba(153, 88, 47, 0.10) inset !important;
    }}
    
    /* Premium Table Cells */
    [data-testid="stDataFrameContainer"] tbody td {{
        padding: 12px 14px !important;
        border-bottom: 1px solid rgba(201, 187, 176, 0.55) !important;
        border-right: 1px solid rgba(201, 187, 176, 0.35) !important;
        font-size: 0.93rem !important;
        line-height: 1.25 !important;
        vertical-align: middle !important;
        transition: all 0.2s ease !important;
        position: relative !important;
    }}

    [data-testid="stDataFrameContainer"] tbody td:last-child {{
        border-right: none !important;
    }}
    
    /* Dropdown and Select Styling */
    [data-baseweb="select"] {{
        background-color: {COLORS['bg_secondary']} !important;
        border-radius: 6px !important;
    }}
    
    [data-baseweb="select"] button {{
        color: {COLORS['text_primary']} !important;
        background-color: {COLORS['bg_secondary']} !important;
        border: 1px solid #d3c3b0 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }}
    
    [data-baseweb="select"] button:hover {{
        border-color: #99582f !important;
        box-shadow: 0 2px 4px rgba(153, 88, 47, 0.15) !important;
    }}
    
    [data-baseweb="select"] button span {{
        color: {COLORS['text_primary']} !important;
    }}
    
    [data-baseweb="popover"] {{
        background-color: {COLORS['bg_secondary']} !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }}
    
    [data-baseweb="menu"] {{
        background-color: {COLORS['bg_secondary']} !important;
        border-radius: 8px !important;
    }}
    
    [data-baseweb="menu"] li {{
        color: {COLORS['text_primary']} !important;
        background-color: {COLORS['bg_secondary']} !important;
        padding: 8px 12px !important;
    }}
    
    [data-baseweb="menu"] li:hover {{
        background-color: #99582f !important;
        color: #f5f5f5 !important;
    }}
    
    [role="option"] {{
        color: {COLORS['text_primary']} !important;
        background-color: {COLORS['bg_secondary']} !important;
        padding: 8px 12px !important;
    }}
    
    [role="option"]:hover {{
        background-color: #99582f !important;
        color: #f5f5f5 !important;
    }}
    
    [role="listbox"] {{
        background-color: {COLORS['bg_secondary']} !important;
        border-radius: 8px !important;
        border: 1px solid #d3c3b0 !important;
    }}
    
    /* Data editor dropdown text visibility */
    div[data-testid="stDataFrameContainer"] [role="button"] {{
        color: {COLORS['text_primary']} !important;
    }}
    
    div[data-testid="stDataFrameContainer"] [role="option"] {{
        color: {COLORS['text_primary']} !important;
        background-color: {COLORS['bg_secondary']} !important;
    }}
    
    div[data-testid="stDataFrameContainer"] [role="option"]:hover {{
        background-color: #99582f !important;
        color: #f5f5f5 !important;
    }}
    
    /* Button Styling - Premium & Attractive */
    .stButton>button {{
        background: linear-gradient(135deg, {COLORS['button_bg']} 0%, {COLORS['text_primary']} 160%) !important;
        color: {COLORS['button_text']} !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 12px 28px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(153, 88, 47, 0.25) !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        cursor: pointer !important;
    }}
    
    .stButton>button:hover {{
        background: linear-gradient(135deg, {COLORS['text_primary']} 0%, {COLORS['button_bg']} 100%) !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 25px rgba(153, 88, 47, 0.4) !important;
        letter-spacing: 1px !important;
    }}
    
    .stButton>button:active {{
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(153, 88, 47, 0.3) !important;
    }}
    
    .stButton>button:focus {{
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(153, 88, 47, 0.2) !important;
    }}

    /* Targeted hover animation: Add Patient + Save only (via unique tooltip/title) */
    button[title="Add a new patient row (uses selected patient if chosen)"] {{
        position: relative !important;
        overflow: hidden !important;
        background: #99582f !important;
        color: #f9f9f9 !important;
    }}

    button[title="Save changes to storage"] {{
        position: relative !important;
        overflow: hidden !important;
        background: #99582f !important;
        color: #f9f9f9 !important;
    }}

    button[title="Add a new patient row (uses selected patient if chosen)"]:hover,
    button[title="Save changes to storage"]:hover {{
        background: #111b26 !important;
        color: #f9f9f9 !important;
        animation: pulse-glow 1.4s ease-out infinite !important;
    }}

    button[title="Add a new patient row (uses selected patient if chosen)"]:active,
    button[title="Save changes to storage"]:active {{
        background: #111b26 !important;
        color: #f9f9f9 !important;
    }}
    
    .st-bv, .st-cv, .st-cw {{
        background-color: {COLORS['bg_secondary']} !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['text_primary']} !important;
        font-weight: 600 !important;
    }}
    
    h1 {{
        font-size: 2rem !important;
        margin-bottom: 1.5rem !important;
    }}
    
    h2 {{
        font-size: 1.5rem !important;
        margin-bottom: 1rem !important;
        margin-top: 1.5rem !important;
    }}
    
    .stMarkdown {{
        color: {COLORS['text_primary']} !important;
    }}
    
    /* Data Frame Container - Premium & Beautiful */
    [data-testid="stDataFrameContainer"] {{
        background-color: {COLORS['bg_secondary']} !important;
        border-radius: 12px !important;
        border: 1px solid rgba(201, 187, 176, 0.65) !important;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.55) !important;
        overflow: hidden !important;
        transition: all 0.3s ease !important;
    }}
    
    [data-testid="stDataFrameContainer"]:hover {{
        box-shadow: 0 10px 26px rgba(0, 0, 0, 0.10), inset 0 1px 0 rgba(255, 255, 255, 0.55) !important;
    }}
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: transparent !important;
        border-bottom: 2px solid #d3c3b0 !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {COLORS['text_secondary']} !important;
        padding: 12px 20px !important;
        border-bottom: 3px solid transparent !important;
        transition: all 0.3s ease !important;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        color: #99582f !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {COLORS['button_bg']} !important;
        border-bottom: 3px solid {COLORS['button_bg']} !important;
    }}
    
    /* Alert/Message Styling */
    .st-info {{
        background-color: rgba(59, 130, 246, 0.1) !important;
        border-left: 4px solid {COLORS['info']} !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
    }}
    
    .st-success {{
        background-color: rgba(16, 185, 129, 0.1) !important;
        border-left: 4px solid {COLORS['success']} !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
    }}
    
    .st-warning {{
        background-color: rgba(245, 158, 11, 0.1) !important;
        border-left: 4px solid {COLORS['warning']} !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
    }}
    
    .st-error {{
        background-color: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid {COLORS['danger']} !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
    }}
    
    /* Animations */
    @keyframes bounce-click {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.2); }}
        100% {{ transform: scale(1); }}
    }}
    
    @keyframes pulse-glow {{
        0% {{ box-shadow: 0 0 0 0 rgba(153, 88, 47, 0.7); }}
        70% {{ box-shadow: 0 0 0 10px rgba(153, 88, 47, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(153, 88, 47, 0); }}
    }}
    
    @keyframes spin-check {{
        0% {{ transform: rotate(-10deg) scale(0.8); }}
        50% {{ transform: rotate(5deg) scale(1.1); }}
        100% {{ transform: rotate(0deg) scale(1); }}
    }}
    
    /* Checkbox Styling */
    input[type="checkbox"] {{
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        width: 18px !important;
        height: 18px !important;
        accent-color: #99582f !important;
    }}
    
    input[type="checkbox"]:hover {{
        filter: brightness(1.15) !important;
    }}
    
    input[type="checkbox"]:active {{
        animation: bounce-click 0.4s ease !important;
    }}
    
    input[type="checkbox"]:checked {{
        animation: spin-check 0.5s ease !important;
    }}
    
    /* Style checkbox containers */
    [data-testid="stDataFrameContainer"] input[type="checkbox"] {{
        width: 20px !important;
        height: 20px !important;
        cursor: pointer !important;
    }}
    
    /* Divider styling */
    hr {{
        border: none !important;
        border-top: 2px solid #d3c3b0 !important;
        margin: 2rem 0 !important;
    }}
    
    /* Section cards */
    .section-card {{
        background-color: {COLORS['bg_secondary']} !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
        border: 1px solid #d3c3b0 !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    }}
    
    /* Save button styling - aesthetic and smooth */
    button[key="manual_save_btn"] {{
        background: linear-gradient(135deg, {COLORS['button_bg']} 0%, {COLORS['text_primary']} 160%) !important;
        color: {COLORS['button_text']} !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(153, 88, 47, 0.3) !important;
        padding: 10px 20px !important;
    }}
    
    button[key="manual_save_btn"]:hover {{
        background: linear-gradient(135deg, {COLORS['text_primary']} 0%, {COLORS['button_bg']} 100%) !important;
        box-shadow: 0 4px 14px rgba(153, 88, 47, 0.4) !important;
        transform: translateY(-2px) !important;
    }}
    
    button[key="manual_save_btn"]:active {{
        transform: translateY(0) !important;
        box-shadow: 0 2px 6px rgba(153, 88, 47, 0.3) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Professional Header with Logo
col_logo, col_title, col_space = st.columns([0.3, 2, 0.3])

with col_logo:
    st.image("The Dental Bond LOGO_page-0001.jpg", width=140)

with col_title:
    st.markdown("""
        <style>
        .header-container {
            padding: 2rem 2.5rem;
            background: linear-gradient(135deg, rgba(153, 88, 47, 0.12) 0%, rgba(201, 187, 176, 0.1) 100%);
            border-radius: 12px;
            border: 1px solid rgba(201, 187, 176, 0.3);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            text-align: center;
        }
        .dashboard-title {
            margin: 0;
            padding: 0;
            font-size: 2.3rem;
            font-weight: 700;
            color: #111b26;
            letter-spacing: 1.5px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
            word-spacing: 0.1em;
        }
        .dashboard-subtitle {
            margin-top: 1rem;
            font-size: 0.9rem;
            color: #99582f;
            letter-spacing: 0.5px;
            font-weight: 500;
        }
        </style>
        <div class="header-container">
            <div class="dashboard-title">
                ALLOTMENT DASHBOARD
            </div>
            <div class="dashboard-subtitle">
                Real-time Scheduling Management System
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    .divider-line {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #99582f 50%, transparent 100%);
        margin: 0.8rem 0;
        border-radius: 1px;
    }
    </style>
    <div class="divider-line"></div>
""", unsafe_allow_html=True)

# Indian Standard Time (IST = UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))
now = datetime.now(IST)
st.markdown(f" {now.strftime('%B %d, %Y - %I:%M:%S %p')} IST")

# Epoch seconds (used for 30-second snooze timing)
now_epoch = int(time_module.time())

# --- Reminder settings in sidebar ---
with st.sidebar:
    st.markdown("## 🔔 Notifications")
    st.checkbox("Enable 15-minute reminders", value=True, key="enable_reminders")
    st.checkbox(
        "Pause auto-refresh while editing",
        value=True,
        key="pause_autorefresh_while_editing",
        help="Keeps the table stable while you edit (recommended).",
    )
    st.selectbox(
        "Default snooze (seconds)",
        options=[30, 60, 90, 120, 150, 180, 300],
        index=0,
        key="default_snooze_seconds",
    )
    st.write("💡 Reminders alert 15 minutes before a patient's In Time.")

# ================ Data Storage Configuration ================
# Determine whether to use Google Sheets (cloud) or local Excel file
USE_SUPABASE = False
USE_GOOGLE_SHEETS = False

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Putt Allotment.xlsx")

supabase_client = None
supabase_table_name = "tdb_allotment_state"
supabase_row_id = "main"

gsheet_client = None
gsheet_worksheet = None


def _normalize_service_account_info(raw_info: dict) -> dict:
    """Normalize Streamlit secrets into a dict suitable for google-auth.

    Streamlit secrets are often pasted with either literal "\n" sequences or
    TOML multiline strings. This normalizes the private key so google-auth can
    parse it reliably.
    """
    info = dict(raw_info or {})
    private_key = info.get("private_key")
    if isinstance(private_key, str):
        # Strip surrounding whitespace
        private_key = private_key.strip()
        # Handle accidental bytes-literal formatting: b'...'
        if (private_key.startswith("b'") and private_key.endswith("'")) or (
            private_key.startswith('b"') and private_key.endswith('"')
        ):
            private_key = private_key[2:-1]
        # Convert escaped newlines into real newlines if needed
        if "\\n" in private_key and "\n" not in private_key:
            private_key = private_key.replace("\\n", "\n")
        # Normalize Windows newlines
        private_key = private_key.replace("\r\n", "\n").replace("\r", "\n")
        # Remove accidental leading/trailing quotes from copy/paste
        if (private_key.startswith('"') and private_key.endswith('"')) or (
            private_key.startswith("'") and private_key.endswith("'")
        ):
            private_key = private_key[1:-1]

        # If the key is multi-line, strip per-line indentation/spaces.
        # Streamlit Secrets UI and some editors sometimes add leading spaces.
        if "\n" in private_key:
            lines = private_key.split("\n")
            cleaned_lines: list[str] = []
            for line in lines:
                if not line:
                    cleaned_lines.append("")
                    continue
                stripped = line.strip()
                # Remove interior spaces from base64 lines (but not header/footer)
                if not stripped.startswith("-----BEGIN") and not stripped.startswith("-----END"):
                    stripped = stripped.replace(" ", "")
                cleaned_lines.append(stripped)
            private_key = "\n".join(cleaned_lines).strip("\n")

        # If BEGIN/END are present but the key is pasted on one line, force newlines.
        # This frequently happens when pasting into Streamlit Secrets.
        if "BEGIN PRIVATE KEY" in private_key and "END PRIVATE KEY" in private_key:
            private_key = re.sub(r"-----BEGIN PRIVATE KEY-----\s*", "-----BEGIN PRIVATE KEY-----\n", private_key)
            private_key = re.sub(r"\s*-----END PRIVATE KEY-----", "\n-----END PRIVATE KEY-----", private_key)
            private_key = re.sub(r"\n{3,}", "\n\n", private_key)
            if not private_key.endswith("\n"):
                private_key += "\n"
        info["private_key"] = private_key
    return info


def _get_service_account_info_from_secrets(secrets_obj) -> dict:
    """Support multiple Streamlit secrets shapes.

    Supported:
    - [gcp_service_account] table (dict)
    - gcp_service_account_json = "{...}" (string containing JSON)
    - gcp_service_account = "{...}" (string containing JSON)
    """
    if not secrets_obj:
        raise ValueError("Streamlit secrets are not available.")

    if "gcp_service_account" in secrets_obj:
        sa = secrets_obj["gcp_service_account"]
        if isinstance(sa, dict):
            return sa
        if isinstance(sa, str):
            try:
                return json.loads(sa)
            except json.JSONDecodeError as e:
                raise ValueError(
                    "`gcp_service_account` is present but is not a TOML table/dict and is not valid JSON. "
                    f"JSON error at line {e.lineno}, column {e.colno}: {e.msg}. "
                    "Prefer using a TOML table: [gcp_service_account]."
                ) from e
            except Exception as e:
                raise ValueError(
                    "`gcp_service_account` is present but could not be parsed. Prefer using a TOML table: [gcp_service_account]."
                ) from e

    if "gcp_service_account_json" in secrets_obj:
        sa_json = secrets_obj.get("gcp_service_account_json")
        # Some users paste an inline TOML table instead of a JSON string; Streamlit may parse it as a dict.
        if isinstance(sa_json, dict):
            return sa_json
        if isinstance(sa_json, str) and sa_json.strip():
            try:
                return json.loads(sa_json)
            except json.JSONDecodeError as e:
                raise ValueError(
                    "`gcp_service_account_json` is not valid JSON. "
                    f"JSON error at line {e.lineno}, column {e.colno}: {e.msg}. "
                    "Fix common issues: use double-quotes, remove trailing commas, keep the outer { } braces."
                ) from e
            except Exception as e:
                raise ValueError(
                    "`gcp_service_account_json` could not be parsed. Paste the full service account JSON exactly."
                ) from e

    raise ValueError(
        "Missing Google service account secrets. Add a [gcp_service_account] section (recommended) "
        "or `gcp_service_account_json`."
    )


def _open_spreadsheet(client, spreadsheet_ref: str):
    """Open a spreadsheet by URL or by key/id.

    `spreadsheet_ref` may be:
    - Full URL: https://docs.google.com/spreadsheets/d/<ID>/edit
    - Just the ID/key: <ID>
    """
    ref = (spreadsheet_ref or "").strip()
    if not ref:
        raise ValueError("Missing `spreadsheet_url`. Paste the Google Sheet URL or its Spreadsheet ID.")
    if ref.startswith("http://") or ref.startswith("https://"):
        return client.open_by_url(ref)
    # Looks like a spreadsheet key/id
    return client.open_by_key(ref)


def _get_supabase_config_from_secrets_or_env():
    """Return (url, key, table, row_id) from Streamlit secrets/env vars."""
    url = ""
    key = ""
    service_key = ""
    table = supabase_table_name
    row_id = supabase_row_id

    try:
        if hasattr(st, 'secrets'):
            url = str(st.secrets.get("supabase_url", "") or "").strip()
            key = str(st.secrets.get("supabase_key", "") or "").strip()
            service_key = str(st.secrets.get("supabase_service_role_key", "") or "").strip()
            table = str(st.secrets.get("supabase_table", table) or table).strip() or table
            row_id = str(st.secrets.get("supabase_row_id", row_id) or row_id).strip() or row_id
    except Exception:
        pass

    if not url:
        url = os.getenv("SUPABASE_URL", "").strip()
    if not key:
        key = os.getenv("SUPABASE_KEY", "").strip()
    if not service_key:
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if os.getenv("SUPABASE_TABLE"):
        table = os.getenv("SUPABASE_TABLE", table).strip() or table
    if os.getenv("SUPABASE_ROW_ID"):
        row_id = os.getenv("SUPABASE_ROW_ID", row_id).strip() or row_id

    # Prefer service role key when present (avoids RLS setup for server-side app).
    effective_key = service_key or key
    return url, effective_key, table, row_id


def _get_expected_columns():
    return [
        "Patient ID", "Patient Name", "In Time", "Out Time", "Procedure", "DR.",
        "FIRST", "SECOND", "Third", "CASE PAPER", "OP",
        "SUCTION", "CLEANING", "STATUS", "REMINDER_ROW_ID",
        "REMINDER_SNOOZE_UNTIL", "REMINDER_DISMISSED",
    ]


def _get_patients_config_from_secrets_or_env():
    """Return (patients_table, id_col, name_col)."""
    patients_table = "patients"
    id_col = "id"
    name_col = "name"

    try:
        if hasattr(st, 'secrets'):
            patients_table = str(st.secrets.get("supabase_patients_table", patients_table) or patients_table).strip() or patients_table
            id_col = str(st.secrets.get("supabase_patients_id_col", id_col) or id_col).strip() or id_col
            name_col = str(st.secrets.get("supabase_patients_name_col", name_col) or name_col).strip() or name_col
    except Exception:
        pass

    patients_table = os.getenv("SUPABASE_PATIENTS_TABLE", patients_table).strip() or patients_table
    id_col = os.getenv("SUPABASE_PATIENTS_ID_COL", id_col).strip() or id_col
    name_col = os.getenv("SUPABASE_PATIENTS_NAME_COL", name_col).strip() or name_col
    return patients_table, id_col, name_col


@st.cache_data(ttl=60)
def search_patients_from_supabase(
    _url: str,
    _key: str,
    _patients_table: str,
    _id_col: str,
    _name_col: str,
    _query: str,
    _limit: int = 50,
):
    """Search patients (id + name) from a Supabase table."""
    q = (_query or "").strip()
    client = create_client(_url, _key)

    def _is_simple_ident(name: str) -> bool:
        return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", str(name or "")))

    def _quote_ident(name: str) -> str:
        n = str(name or "")
        # Quote if it has spaces, punctuation, or uppercase/lowercase sensitivity.
        if _is_simple_ident(n) and n == n.lower():
            return n
        return '"' + n.replace('"', '""') + '"'

    def _run(_id: str, _name: str, *, server_filter: bool) -> list[dict] | None:
        select_str = f"{_quote_ident(_id)},{_quote_ident(_name)}"
        query = client.table(_patients_table).select(select_str)

        # Only apply server-side ilike/order if the column name is a simple identifier.
        if server_filter and q and _is_simple_ident(_name):
            query = query.ilike(_name, f"%{q}%")
        if server_filter and _is_simple_ident(_name):
            query = query.order(_name)

        resp = query.limit(_limit).execute()
        err = getattr(resp, "error", None)
        if err:
            raise RuntimeError(str(err))
        data = getattr(resp, "data", None)
        return data

    # PostgREST supports ilike and order.
    try:
        data = _run(_id_col, _name_col, server_filter=True)
    except Exception as e:
        # Common case: columns are not named exactly `id`/`name`.
        # Postgres error code for unknown column is 42703.
        err_text = str(e)
        if "42703" not in err_text and "does not exist" not in err_text:
            raise

        # First try to infer actual column names by sampling 1 row.
        inferred_id: str | None = None
        inferred_name: str | None = None
        try:
            probe = client.table(_patients_table).select("*").limit(1).execute()
            probe_err = getattr(probe, "error", None)
            if probe_err:
                raise RuntimeError(str(probe_err))
            probe_data = getattr(probe, "data", None)
            if isinstance(probe_data, list) and probe_data and isinstance(probe_data[0], dict):
                keys = [str(k) for k in probe_data[0].keys()]
                keys_l = {k.lower(): k for k in keys}

                # Heuristics: prefer exact matches, else keys containing patient+id/name.
                for cand in ["id", "patient_id", "patientid", "uhid", "pid", "patient id"]:
                    if cand in keys_l:
                        inferred_id = keys_l[cand]
                        break
                for cand in ["name", "patient_name", "patientname", "full_name", "fullname", "patient name"]:
                    if cand in keys_l:
                        inferred_name = keys_l[cand]
                        break
        except Exception:
            inferred_id = None
            inferred_name = None

        if inferred_id and inferred_name:
            data = _run(inferred_id, inferred_name, server_filter=_is_simple_ident(inferred_name))
            _id_col, _name_col = inferred_id, inferred_name
        else:
            # Fall back to trying a broader set of common column names.
            id_candidates = [
                _id_col,
                "id",
                "ID",
                "patient_id",
                "patientId",
                "patientid",
                "uhid",
                "UHID",
                "pid",
                "PID",
                "patient id",
                "Patient ID",
            ]
            name_candidates = [
                _name_col,
                "name",
                "NAME",
                "patient_name",
                "patientName",
                "patientname",
                "full_name",
                "fullName",
                "fullname",
                "patient name",
                "Patient Name",
            ]

            last_err: Exception | None = None
            data = None
            for cid in id_candidates:
                for cname in name_candidates:
                    if not cid or not cname:
                        continue
                    try:
                        data = _run(cid, cname, server_filter=_is_simple_ident(cname))
                        _id_col = cid
                        _name_col = cname
                        last_err = None
                        break
                    except Exception as inner:
                        last_err = inner
                        continue
                if last_err is None and data is not None:
                    break
            if data is None:
                raise last_err if last_err is not None else e

    if not isinstance(data, list):
        return []
    out = []
    for row in data:
        pid = row.get(_id_col)
        name = row.get(_name_col)
        if pid is None or name is None:
            continue
        out.append({"id": str(pid), "name": str(name)})

    # If we couldn't do server-side filtering (e.g., quoted column names), filter locally.
    if q and out:
        ql = q.lower()
        out = [p for p in out if ql in str(p.get("name", "")).lower()]
    return out


@st.cache_data(ttl=30)
def load_data_from_supabase(_url: str, _key: str, _table: str, _row_id: str):
    """Load dataframe payload from Supabase.

    Storage model: a single row with `id` and `payload` (jsonb).
    payload = {"columns": [...], "rows": [ {col: val, ...}, ... ]}
    """
    try:
        client = create_client(_url, _key)
        resp = client.table(_table).select("payload").eq("id", _row_id).execute()

        data = getattr(resp, "data", None)
        if not data:
            return pd.DataFrame(columns=_get_expected_columns())
        payload = data[0].get("payload") if isinstance(data, list) else None
        if not payload:
            return pd.DataFrame(columns=_get_expected_columns())

        columns = payload.get("columns") or _get_expected_columns()
        rows = payload.get("rows") or []
        df = pd.DataFrame(rows)
        # Ensure expected columns are present and ordered
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df = df[columns]
        return df
    except Exception as e:
        st.error(f"Error loading from Supabase: {e}")
        return None


def save_data_to_supabase(_url: str, _key: str, _table: str, _row_id: str, df: pd.DataFrame) -> bool:
    """Save dataframe payload to Supabase (upsert)."""
    try:
        client = create_client(_url, _key)

        df_clean = df.copy().fillna("")
        # Convert to JSON-serializable primitives; avoid pandas NA
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(object)

        payload = {
            "columns": df_clean.columns.tolist(),
            "rows": df_clean.to_dict(orient="records"),
        }
        client.table(_table).upsert({"id": _row_id, "payload": payload}).execute()
        load_data_from_supabase.clear()
        return True
    except Exception as e:
        st.error(f"Error saving to Supabase: {e}")
        return False


def _validate_service_account_info(info: dict) -> list[str]:
    missing: list[str] = []
    if not isinstance(info, dict) or not info:
        return ["gcp_service_account"]
    required = ["type", "project_id", "private_key", "client_email"]
    for k in required:
        if not str(info.get(k, "")).strip():
            missing.append(k)
    return missing

# Try to connect to Google Sheets if credentials are available
if SUPABASE_AVAILABLE:
    try:
        sup_url, sup_key, sup_table, sup_row = _get_supabase_config_from_secrets_or_env()
        if sup_url and sup_key:
            supabase_client = create_client(sup_url, sup_key)
            supabase_table_name = sup_table
            supabase_row_id = sup_row
            # Quick connectivity check (will also validate credentials)
            _ = supabase_client.table(supabase_table_name).select("id").limit(1).execute()
            USE_SUPABASE = True
            st.sidebar.success("🗄️ Connected to Supabase")
        else:
            # Not configured; show a quick setup helper.
            with st.sidebar.expander("✅ Quick setup (Supabase)", expanded=False):
                st.markdown(
                    "Add these secrets in Streamlit Cloud → Settings → Secrets:\n"
                    "- `supabase_url`\n"
                    "- `supabase_key` (anon key) **or** `supabase_service_role_key` (recommended for server-side apps)\n"
                    "\nThen create the table in Supabase (SQL Editor):"
                )
                st.code(
                    "create table if not exists tdb_allotment_state (\n"
                    "  id text primary key,\n"
                    "  payload jsonb not null,\n"
                    "  updated_at timestamptz not null default now()\n"
                    ");\n",
                    language="sql",
                )
                st.markdown(
                    "If you use the **anon key**, you may need to adjust Row Level Security (RLS). "
                    "Simplest (not recommended for public apps):"
                )
                st.code(
                    "alter table tdb_allotment_state disable row level security;\n",
                    language="sql",
                )
    except Exception as e:
        # Safe diagnostics: only presence of keys, not values.
        present = {}
        try:
            if hasattr(st, 'secrets'):
                interesting = ["supabase_url", "supabase_key", "supabase_service_role_key", "supabase_table", "supabase_row_id"]
                present = {k: (k in st.secrets and bool(str(st.secrets.get(k, '')).strip())) for k in interesting}
        except Exception:
            pass

        st.sidebar.error(
            f"⚠️ Supabase connection failed: {e}"
            + ("\n\nSecrets keys (safe): " + ", ".join([f"{k}={v}" for k, v in present.items()]) if present else "")
            + "\n\nTip: If you are using `supabase_key` (anon key), RLS may block reads/writes. "
              "Either add a server-side `supabase_service_role_key` in Streamlit Secrets or disable RLS for this table."
        )
        USE_SUPABASE = False

# Try to connect to Google Sheets if credentials are available (fallback)
if (not USE_SUPABASE) and GSHEETS_AVAILABLE:
    try:
        # Check if running on Streamlit Cloud with secrets
        service_account_info = None
        spreadsheet_ref = ""

        if hasattr(st, 'secrets'):
            if (('gcp_service_account' in st.secrets) or ('gcp_service_account_json' in st.secrets)):
                service_account_info = _normalize_service_account_info(_get_service_account_info_from_secrets(st.secrets))
            spreadsheet_ref = str(st.secrets.get("spreadsheet_url", "") or "").strip()

        # Optional env-var support (useful for local runs or advanced deployments)
        if not service_account_info:
            env_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON", "").strip()
            if env_json:
                try:
                    service_account_info = _normalize_service_account_info(json.loads(env_json))
                except Exception as e:
                    raise ValueError("GCP_SERVICE_ACCOUNT_JSON is set but is not valid JSON.") from e
        if not spreadsheet_ref:
            spreadsheet_ref = os.getenv("SPREADSHEET_URL", "").strip()

        if service_account_info:
            missing_fields = _validate_service_account_info(service_account_info)
            if missing_fields:
                raise ValueError(f"Service account is missing required fields: {', '.join(missing_fields)}")

            # Basic validation to provide clearer errors than "Invalid base64..."
            pk = str(service_account_info.get("private_key", ""))
            # Safe diagnostics (no secret values) to help users self-debug Streamlit secrets.
            _sa_diag = {
                "has_type": bool(str(service_account_info.get("type", "")).strip()),
                "type": str(service_account_info.get("type", ""))[:40],
                "has_client_email": bool(str(service_account_info.get("client_email", "")).strip()),
                "has_project_id": bool(str(service_account_info.get("project_id", "")).strip()),
                "private_key_len": len(pk) if isinstance(pk, str) else 0,
                "private_key_has_begin": "BEGIN PRIVATE KEY" in pk,
                "private_key_has_end": "END PRIVATE KEY" in pk,
            }

            if _sa_diag["type"] and _sa_diag["type"] != "service_account":
                raise ValueError(
                    "Secrets do not look like a Google *service account* JSON (type is not 'service_account'). "
                    "Make sure you downloaded a Service Account key (JSON) from Google Cloud Console."
                )
            if "BEGIN PRIVATE KEY" not in pk or "END PRIVATE KEY" not in pk:
                raise ValueError(
                    "Service account private_key is missing BEGIN/END markers. "
                    "In Streamlit secrets, paste it as a TOML multiline string using triple quotes (\"\"\")."
                )

            credentials = Credentials.from_service_account_info(
                service_account_info,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
            gsheet_client = gspread.authorize(credentials)
            
            # Open spreadsheet by URL or ID
            if spreadsheet_ref:
                spreadsheet = _open_spreadsheet(gsheet_client, spreadsheet_ref)
                gsheet_worksheet = spreadsheet.sheet1
                USE_GOOGLE_SHEETS = True
                st.sidebar.success("☁️ Connected to Google Sheets")
    except Exception as e:
        # Show a more actionable hint for the most common failure mode.
        msg = str(e)
        hint = ""
        if "Invalid base64" in msg or "base64" in msg.lower():
            hint = (
                "\n\nHint: This usually means the service account `private_key` was pasted with broken newlines "
                "or an extra character. Re-download a NEW JSON key from Google Cloud and paste the `private_key` "
                "using TOML triple quotes (\"\"\")."
            )
        elif "No key could be detected" in msg or "Could not deserialize key data" in msg:
            hint = (
                "\n\nHint: Your `private_key` value is not being parsed as a valid PEM key. "
                "In Streamlit secrets, paste `private_key` as a multiline TOML string using triple quotes (\"\"\"). "
                "Make sure it contains the exact lines '-----BEGIN PRIVATE KEY-----' and '-----END PRIVATE KEY-----'."
            )
        # Add safe diagnostics to reduce guesswork without exposing secrets.
        diag_text = ""
        try:
            if 'service_account_info' in locals() and isinstance(service_account_info, dict):
                pk_local = str(service_account_info.get("private_key", ""))
                diag = {
                    "has_gcp_service_account": True,
                    "type": str(service_account_info.get("type", ""))[:40],
                    "has_client_email": bool(str(service_account_info.get("client_email", "")).strip()),
                    "has_project_id": bool(str(service_account_info.get("project_id", "")).strip()),
                    "private_key_len": len(pk_local),
                    "has_begin": "BEGIN PRIVATE KEY" in pk_local,
                    "has_end": "END PRIVATE KEY" in pk_local,
                }
                diag_text = "\n\nDiagnostics (safe): " + ", ".join([f"{k}={v}" for k, v in diag.items()])
            else:
                diag_text = "\n\nDiagnostics (safe): has_gcp_service_account=False"
        except Exception:
            pass

        # Safe view of which *secret keys* Streamlit can see (names only, no values)
        secrets_keys_text = ""
        try:
            if hasattr(st, 'secrets'):
                keys = sorted(list(st.secrets.keys()))
                # Avoid dumping a huge list; this app only cares about these.
                interesting = [
                    "spreadsheet_url",
                    "gcp_service_account",
                    "gcp_service_account_json",
                ]
                present = {k: (k in st.secrets) for k in interesting}
                secrets_keys_text = "\n\nSecrets keys (safe): " + ", ".join([f"{k}={v}" for k, v in present.items()])
            else:
                secrets_keys_text = "\n\nSecrets keys (safe): st.secrets not available"
        except Exception:
            pass

        st.sidebar.error(f"⚠️ Google Sheets connection failed: {msg}{hint}{diag_text}{secrets_keys_text}")
        USE_GOOGLE_SHEETS = False

        # Simple guided help (no secrets displayed)
        with st.sidebar.expander("✅ Quick setup (simple)", expanded=False):
            st.markdown(
                "Use **one secret** instead of many fields:\n"
                "- Add `spreadsheet_url` (full URL or just the sheet ID)\n"
                "- Add `gcp_service_account_json` (paste the FULL service account JSON)\n\n"
                "Example (Streamlit Cloud → Settings → Secrets):"
            )
            st.code(
                'spreadsheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"\n\n'
                'gcp_service_account_json = """{\n'
                '  "type": "service_account",\n'
                '  "project_id": "...",\n'
                '  "private_key_id": "...",\n'
                '  "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",\n'
                '  "client_email": "...",\n'
                '  "client_id": "...",\n'
                '  "auth_uri": "https://accounts.google.com/o/oauth2/auth",\n'
                '  "token_uri": "https://oauth2.googleapis.com/token",\n'
                '  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",\n'
                '  "client_x509_cert_url": "..."\n'
                '}"""\n',
                language="toml",
            )
            st.markdown(
                "Also ensure:\n"
                "- The Google Sheet is **shared** with the service account email (Editor)\n"
                "- Google Sheets API + Google Drive API are enabled in Google Cloud"
            )

        # Optional: one-click test button (re-runs same logic and shows a concise result)
        if st.sidebar.button("🔎 Test Google Sheets connection", key="test_gsheets_connection"):
            try:
                if not GSHEETS_AVAILABLE:
                    raise RuntimeError("Google Sheets packages are not installed.")

                # Re-read secrets/env inside the button click
                _sa = None
                _ref = ""
                if hasattr(st, 'secrets'):
                    if (('gcp_service_account' in st.secrets) or ('gcp_service_account_json' in st.secrets)):
                        _sa = _normalize_service_account_info(_get_service_account_info_from_secrets(st.secrets))
                    _ref = str(st.secrets.get("spreadsheet_url", "") or "").strip()
                if not _sa:
                    env_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON", "").strip()
                    if env_json:
                        _sa = _normalize_service_account_info(json.loads(env_json))
                if not _ref:
                    _ref = os.getenv("SPREADSHEET_URL", "").strip()

                if not _sa:
                    raise ValueError("Missing service account secret. Add [gcp_service_account] or gcp_service_account_json.")
                missing = _validate_service_account_info(_sa)
                if missing:
                    raise ValueError(f"Service account missing fields: {', '.join(missing)}")

                _pk = str(_sa.get("private_key", ""))
                if "BEGIN PRIVATE KEY" not in _pk or "END PRIVATE KEY" not in _pk:
                    raise ValueError("private_key missing BEGIN/END markers")

                _creds = Credentials.from_service_account_info(
                    _sa,
                    scopes=[
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"
                    ],
                )
                _client = gspread.authorize(_creds)
                _sheet = _open_spreadsheet(_client, _ref)
                _ws = _sheet.sheet1
                _ = _ws.row_values(1)
                st.sidebar.success("✅ Test OK: connected and read the sheet")
            except Exception as test_e:
                # Add safe view of which secret keys exist to help diagnose missing secrets.
                try:
                    if hasattr(st, 'secrets'):
                        interesting = [
                            "spreadsheet_url",
                            "gcp_service_account",
                            "gcp_service_account_json",
                        ]
                        present = {k: (k in st.secrets) for k in interesting}
                        st.sidebar.error(
                            f"❌ Test failed: {test_e}\n\nSecrets keys (safe): "
                            + ", ".join([f"{k}={v}" for k, v in present.items()])
                        )
                    else:
                        st.sidebar.error(f"❌ Test failed: {test_e}\n\nSecrets keys (safe): st.secrets not available")
                except Exception:
                    st.sidebar.error(f"❌ Test failed: {test_e}")

# Helper functions for Google Sheets
@st.cache_data(ttl=30)  # Cache for 30 seconds to reduce API calls
def load_data_from_gsheets(_worksheet):
    """Load data from Google Sheets worksheet"""
    try:
        data = _worksheet.get_all_records()
        if not data:
            # Return empty dataframe with expected columns
            return pd.DataFrame(columns=[
                "Patient Name", "In Time", "Out Time", "Procedure", "DR.", 
                "FIRST", "SECOND", "Third", "CASE PAPER", "OP", 
                "SUCTION", "CLEANING", "STATUS", "REMINDER_ROW_ID",
                "REMINDER_SNOOZE_UNTIL", "REMINDER_DISMISSED"
            ])
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Error loading from Google Sheets: {e}")
        return None

def save_data_to_gsheets(worksheet, df):
    """Save dataframe to Google Sheets worksheet"""
    try:
        # Clear existing data
        worksheet.clear()
        
        # Convert dataframe to list of lists for gspread
        # Handle NaN/None values
        df_clean = df.fillna("")
        
        # Convert all values to strings to avoid serialization issues
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).replace('nan', '').replace('None', '').replace('NaT', '')
        
        # Write headers
        headers = df_clean.columns.tolist()
        
        # Write data
        values = [headers] + df_clean.values.tolist()
        worksheet.update(values, 'A1')
        
        # Clear the cache so next load gets fresh data
        load_data_from_gsheets.clear()
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False

def _data_editor_has_pending_edits(editor_key: str) -> bool:
    """Detect pending edits without touching widget state.

    Streamlit stores data_editor widget edits in st.session_state[editor_key]
    as a dict with keys like edited_rows/added_rows/deleted_rows.
    """
    try:
        state = st.session_state.get(editor_key)
        if not isinstance(state, dict):
            return False
        return bool(state.get("edited_rows") or state.get("added_rows") or state.get("deleted_rows"))
    except Exception:
        return False


def _should_pause_autorefresh_for_editing() -> bool:
    keys: list[str] = ["full_schedule_editor", "doctor_editor"]
    # OP editors are dynamic keys like op_OP_1_editor, etc.
    for k in st.session_state.keys():
        if isinstance(k, str) and k.startswith("op_") and k.endswith("_editor"):
            keys.append(k)
    return any(_data_editor_has_pending_edits(k) for k in keys)


# Auto-refresh every 30 seconds to support 30-second snoozes.
# Pause while editing so the table stays stable and doesn't interrupt typing.
_pause_autorefresh = bool(st.session_state.get("pause_autorefresh_while_editing", True)) and _should_pause_autorefresh_for_editing()
if _pause_autorefresh:
    st.caption("⏸ Auto-refresh paused while editing")
else:
    st_autorefresh(interval=30000, debounce=True, key="autorefresh")

# ================ Load Data ================
df_raw = None

if USE_SUPABASE:
    sup_url, sup_key, sup_table, sup_row = _get_supabase_config_from_secrets_or_env()
    df_raw = load_data_from_supabase(sup_url, sup_key, sup_table, sup_row)
    if df_raw is None:
        st.error("⚠️ Failed to load data from Supabase.")
        st.stop()
elif USE_GOOGLE_SHEETS:
    # Load from Google Sheets
    df_raw = load_data_from_gsheets(gsheet_worksheet)
    if df_raw is None:
        st.error("⚠️ Failed to load data from Google Sheets.")
        st.stop()
else:
    # Fallback to local Excel file
    if not os.path.exists(file_path):
        st.error("⚠️ 'Putt Allotment.xlsx' not found. For cloud deployment, configure Supabase (recommended) or Google Sheets in Streamlit secrets.")
        st.info("💡 See README for Supabase setup instructions.")
        st.stop()
    
    # Retry logic to handle temporary file corruption during concurrent writes
    max_retries = 3
    retry_delay = 0.5  # seconds
    
    for attempt in range(max_retries):
        try:
            df_raw = pd.read_excel(file_path, sheet_name="Sheet1")
            break  # Success, exit retry loop
        except (zipfile.BadZipFile, Exception) as e:
            if "BadZipFile" in str(type(e).__name__) or "Truncated" in str(e) or "corrupt" in str(e).lower():
                if attempt < max_retries - 1:
                    time_module.sleep(retry_delay)  # Wait before retry
                    continue
                else:
                    st.error("⚠️ The Excel file appears to be corrupted or is being modified.")
                    st.stop()
            else:
                raise e
    
    if df_raw is None:
        st.error("⚠️ Failed to load the Excel file after multiple attempts.")
        st.stop()

# Clean column names
df_raw.columns = [col.strip() for col in df_raw.columns]


# Process data
df = df_raw.copy()
# Don't force numeric conversion yet - handle both formats
df["In Time"] = df["In Time"]
df["Out Time"] = df["Out Time"]


# Convert various time formats to HH:MM string
def dec_to_time(time_value):
    t = _coerce_to_time_obj(time_value)
    if t is None:
        return "N/A"
    return f"{t.hour:02d}:{t.minute:02d}"


def _coerce_to_time_obj(time_value):
    """Best-effort coercion of many time representations into a datetime.time.

    Supports:
    - datetime.time, datetime
    - strings: HH:MM, HH:MM:SS, HH.MM, and 12-hour formats like '09:30 AM'
    - numbers: 9.30 (meaning 09:30), or Excel serial time 0-1
    """
    if time_value is None or pd.isna(time_value) or time_value == "":
        return None
    if isinstance(time_value, time):
        return time(time_value.hour, time_value.minute)
    if isinstance(time_value, datetime):
        return time(time_value.hour, time_value.minute)

    # Strings
    if isinstance(time_value, str):
        s = " ".join(time_value.strip().split())
        if s == "" or s.upper() in {"N/A", "NAT", "NONE"}:
            return None

        # 12-hour formats (e.g., 09:30 AM, 9:30PM, 09:30:00 PM)
        if re.search(r"\b(AM|PM)\b", s, flags=re.IGNORECASE) or re.search(r"(AM|PM)$", s, flags=re.IGNORECASE):
            s_norm = re.sub(r"\s*(AM|PM)\s*$", r" \1", s, flags=re.IGNORECASE).upper()
            for fmt in ("%I:%M %p", "%I:%M:%S %p"):
                try:
                    dt = datetime.strptime(s_norm, fmt)
                    return time(dt.hour, dt.minute)
                except ValueError:
                    pass

        # HH:MM or HH:MM:SS
        if ":" in s:
            parts = s.split(":")
            if len(parts) >= 2:
                try:
                    h = int(parts[0])
                    m_part = re.sub(r"\D.*$", "", parts[1])
                    m = int(m_part)
                    if 0 <= h < 24 and 0 <= m < 60:
                        return time(h, m)
                except (ValueError, TypeError):
                    pass

        # HH.MM
        if "." in s:
            parts = s.split(".")
            if len(parts) == 2:
                try:
                    h = int(parts[0])
                    m = int(parts[1])
                    if 0 <= h < 24 and 0 <= m < 60:
                        return time(h, m)
                except (ValueError, TypeError):
                    pass

        return None

    # Numeric formats
    try:
        num_val = float(time_value)
    except (ValueError, TypeError):
        return None

    # Excel serial time format (0.625 = 15:00)
    if 0 <= num_val <= 1:
        total_minutes = round(num_val * 1440)
        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60
        return time(hours, minutes)

    # 9.30 meaning 09:30 (decimal part is minutes directly)
    if 0 <= num_val < 24:
        hours = int(num_val)
        decimal_part = num_val - hours
        minutes = round(decimal_part * 100)
        if minutes > 59:
            minutes = round(decimal_part * 60)
        if minutes >= 60:
            hours = (hours + 1) % 24
            minutes = 0
        if 0 <= hours < 24 and 0 <= minutes < 60:
            return time(hours, minutes)

    return None

# Define all time conversion functions first
def safe_str_to_time_obj(time_str):
    """Convert time string to time object safely"""
    return _coerce_to_time_obj(time_str)

def time_obj_to_str(t):
    """Convert time object to 24-hour HH:MM string for Excel"""
    if pd.isna(t) or t is None:
        return "N/A"
    try:
        if isinstance(t, time):
            return f"{t.hour:02d}:{t.minute:02d}"
        elif isinstance(t, str):
            return t
    except (ValueError, AttributeError):
        pass
    return "N/A"

def time_obj_to_str_12hr(t):
    """Convert time object to 12-hour format with AM/PM"""
    if pd.isna(t) or t is None:
        return "N/A"
    try:
        if isinstance(t, time):
            return t.strftime("%I:%M %p")
        elif isinstance(t, str):
            return t
    except (ValueError, AttributeError):
        pass
    return "N/A"

df["In Time Str"] = df["In Time"].apply(dec_to_time)
df["Out Time Str"] = df["Out Time"].apply(dec_to_time)

# Create time objects for picker
df["In Time Obj"] = df["In Time Str"].apply(safe_str_to_time_obj)
df["Out Time Obj"] = df["Out Time Str"].apply(safe_str_to_time_obj)

# Convert checkbox columns (SUCTION, CLEANING) - checkmark or content to boolean
def str_to_checkbox(val):
    """Convert string values to boolean for checkboxes"""
    # Preserve actual booleans
    if isinstance(val, bool):
        return val

    # Handle numbers (0/1)
    try:
        if isinstance(val, (int, float)) and not pd.isna(val):
            return bool(int(val))
    except Exception:
        pass

    if pd.isna(val):
        return False

    s = str(val).strip()
    if s == "":
        return False

    su = s.upper()
    if su in {"FALSE", "F", "0", "NO", "N", "NONE", "NAN"}:
        return False
    if su in {"TRUE", "T", "1", "YES", "Y"}:
        return True
    if s == "✓":
        return True

    # Any other non-empty content is treated as checked (legacy behavior)
    return True

# Convert existing checkbox data
if "SUCTION" in df.columns:
    df["SUCTION"] = df["SUCTION"].apply(str_to_checkbox)
if "CLEANING" in df.columns:
    df["CLEANING"] = df["CLEANING"].apply(str_to_checkbox)


# Convert time values to minutes since midnight for comparison
def time_to_minutes(time_value):
    t = _coerce_to_time_obj(time_value)
    if t is None:
        return pd.NA
    return t.hour * 60 + t.minute

df["In_min"] = df["In Time"].apply(time_to_minutes).astype('Int64')
df["Out_min"] = df["Out Time"].apply(time_to_minutes).astype('Int64')

# Handle possible overnight cases
df.loc[df["Out_min"] < df["In_min"], "Out_min"] += 1440

# Current time in minutes (same day)
current_min = now.hour * 60 + now.minute

# ================ Reminder Persistence Setup ================
# Add stable row IDs and reminder columns if they don't exist
if 'Patient ID' not in df_raw.columns:
    df_raw['Patient ID'] = ""

if 'REMINDER_ROW_ID' not in df_raw.columns:
    df_raw['REMINDER_ROW_ID'] = [str(uuid.uuid4()) for _ in range(len(df_raw))]
    # Save IDs immediately - will use save_data after it's defined
    _needs_id_save = True
else:
    # Backfill missing/blank IDs so every row (including blank rows) can be targeted for delete/reminders.
    _needs_id_save = False
    try:
        rid_series = df_raw['REMINDER_ROW_ID'].astype(str)
        missing_mask = df_raw['REMINDER_ROW_ID'].isna() | rid_series.str.strip().eq("") | rid_series.str.lower().eq("nan")
        if bool(missing_mask.any()):
            df_raw.loc[missing_mask, 'REMINDER_ROW_ID'] = [str(uuid.uuid4()) for _ in range(int(missing_mask.sum()))]
            _needs_id_save = True
    except Exception:
        # If anything goes wrong, keep dashboard usable; IDs will be handled elsewhere.
        pass

if 'REMINDER_SNOOZE_UNTIL' not in df_raw.columns:
    df_raw['REMINDER_SNOOZE_UNTIL'] = pd.NA
if 'REMINDER_DISMISSED' not in df_raw.columns:
    df_raw['REMINDER_DISMISSED'] = False

# Refresh df with new columns
df = df_raw.copy()

# Re-process time columns after df reassignment
df["In Time Str"] = df["In Time"].apply(dec_to_time)
df["Out Time Str"] = df["Out Time"].apply(dec_to_time)
df["In Time Obj"] = df["In Time Str"].apply(safe_str_to_time_obj)
df["Out Time Obj"] = df["Out Time Str"].apply(safe_str_to_time_obj)

# Re-convert checkbox columns
if "SUCTION" in df.columns:
    df["SUCTION"] = df["SUCTION"].apply(str_to_checkbox)
if "CLEANING" in df.columns:
    df["CLEANING"] = df["CLEANING"].apply(str_to_checkbox)

# Ensure In_min/Out_min exist
df["In_min"] = df["In Time"].apply(time_to_minutes).astype('Int64')
df["Out_min"] = df["Out Time"].apply(time_to_minutes).astype('Int64')
# Handle possible overnight cases
df.loc[df["Out_min"] < df["In_min"], "Out_min"] += 1440

# Mark ongoing
df["Is_Ongoing"] = (df["In_min"] <= current_min) & (current_min <= df["Out_min"])

# ================ Unified Save Function ================
def save_data(dataframe, show_toast=True, message="Data saved!"):
    """Save dataframe to Google Sheets or Excel based on configuration"""
    try:
        if USE_SUPABASE:
            sup_url, sup_key, sup_table, sup_row = _get_supabase_config_from_secrets_or_env()
            success = save_data_to_supabase(sup_url, sup_key, sup_table, sup_row, dataframe)
            if success and show_toast:
                st.toast(f"🗄️ {message}", icon="✅")
            return success
        elif USE_GOOGLE_SHEETS:
            success = save_data_to_gsheets(gsheet_worksheet, dataframe)
            if success and show_toast:
                st.toast(f"☁️ {message}", icon="✅")
            return success
        else:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                dataframe.to_excel(writer, sheet_name='Sheet1', index=False)
            if show_toast:
                st.toast(f"💾 {message}", icon="✅")
            return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# Helper to persist reminder state
def _persist_reminder_to_storage(row_id, until, dismissed):
    """Persist snooze/dismiss fields back to storage by row ID."""
    try:
        match = df_raw[df_raw.get('REMINDER_ROW_ID') == row_id]
        if not match.empty:
            ix = match.index[0]
            df_raw.at[ix, 'REMINDER_SNOOZE_UNTIL'] = int(until) if until is not None else pd.NA
            df_raw.at[ix, 'REMINDER_DISMISSED'] = bool(dismissed)
            return save_data(df_raw, show_toast=False)
    except Exception as e:
        st.error(f"Error persisting reminder: {e}")
    return False

# Save reminder IDs if they were just generated
if _needs_id_save:
    save_data(df_raw, message="Generated stable row IDs for reminders")

# ================ Change Detection & Notifications ================
if 'prev_hash' not in st.session_state:
    st.session_state.prev_hash = None
    st.session_state.prev_ongoing = set()
    st.session_state.prev_upcoming = set()
    st.session_state.prev_raw = pd.DataFrame()
    st.session_state.reminder_sent = set()  # Track reminders by row ID
    st.session_state.snoozed = {}  # Map row_id -> snooze_until_epoch_seconds

# Load persisted reminders from storage
for idx, row in df_raw.iterrows():
    try:
        row_id = row.get('REMINDER_ROW_ID')
        if pd.notna(row_id):
            until_raw = row.get('REMINDER_SNOOZE_UNTIL')
            until_epoch = None
            if pd.notna(until_raw) and until_raw != "":
                try:
                    # Normalize numeric strings
                    if isinstance(until_raw, str) and until_raw.strip().isdigit():
                        until_raw = int(until_raw.strip())

                    if isinstance(until_raw, (int, float)):
                        val = int(until_raw)
                        # Legacy values were stored as minutes since midnight (small numbers)
                        if val < 100000:
                            midnight_ist = datetime(now.year, now.month, now.day, tzinfo=IST)
                            until_epoch = int(midnight_ist.timestamp()) + (val * 60)
                        else:
                            until_epoch = val
                    elif isinstance(until_raw, str):
                        s = until_raw.strip().replace("Z", "+00:00")
                        dt = datetime.fromisoformat(s)
                        until_epoch = int(dt.timestamp())
                except Exception:
                    until_epoch = None

            if until_epoch is not None and until_epoch > now_epoch:
                st.session_state.snoozed[row_id] = until_epoch
            dismissed = row.get('REMINDER_DISMISSED')
            if str(dismissed).strip().upper() in ['TRUE','1','T','YES']:
                st.session_state.reminder_sent.add(row_id)
    except Exception:
        continue

# Compute hash to detect file changes
current_hash = hashlib.md5(pd.util.hash_pandas_object(df_raw).values.tobytes()).hexdigest()

if st.session_state.prev_hash != current_hash:
    st.toast("📊 ALLOTMENT UPDATED", icon="🔄")
    # Reset tracked sets on file change
    st.session_state.prev_ongoing = set()
    st.session_state.prev_upcoming = set()
    st.session_state.reminder_sent = set()
    st.session_state.snoozed = {}

st.session_state.prev_hash = current_hash

# Ensure Is_Ongoing column exists before using it
if "Is_Ongoing" not in df.columns:
    df["Is_Ongoing"] = (df["In_min"] <= current_min) & (current_min <= df["Out_min"])

# Currently Ongoing (filtered)
ongoing_df = df[
    df["Is_Ongoing"] &
    ~df["STATUS"].astype(str).str.upper().str.contains("CANCELLED|DONE|SHIFTED", na=True)
]

current_ongoing = set(ongoing_df["Patient Name"].dropna())

# New ongoing (either from time passing or manual status update)
new_ongoing = current_ongoing - st.session_state.prev_ongoing
for patient in new_ongoing:
    row = ongoing_df[ongoing_df["Patient Name"] == patient].iloc[0]
    st.toast(f"🚨 NOW ONGOING: {patient} – {row['Procedure']} with {row['DR.']} (Chair {row['OP']})", icon="🟢")

# Upcoming in next 15 minutes
upcoming_min = current_min + 15
upcoming_df = df[
    (df["In_min"] > current_min) &
    (df["In_min"] <= upcoming_min) &
    ~df["STATUS"].astype(str).str.upper().str.contains("CANCELLED|DONE|SHIFTED", na=True)
]

current_upcoming = set(upcoming_df["Patient Name"].dropna())

# New upcoming (just entered the 15-minute window)
new_upcoming = current_upcoming - st.session_state.prev_upcoming
for patient in new_upcoming:
    row = upcoming_df[upcoming_df["Patient Name"] == patient].iloc[0]
    mins_left = row["In_min"] - current_min
    st.toast(f"⏰ Upcoming in ~{mins_left} min: {patient} – {row['Procedure']} with {row['DR.']}", icon="⚠️")

# ================ 15-Minute Reminder System ================
if st.session_state.get("enable_reminders", True):
    # Clean up expired snoozes
    expired = [rid for rid, until in list(st.session_state.snoozed.items()) if until <= now_epoch]
    for rid in expired:
        del st.session_state.snoozed[rid]
        # Don't persist clears on natural expiry; we'll overwrite when re-snoozing.
    
    # Find patients needing reminders (0-15 min before In Time)
    reminder_df = df[
        (df["In_min"].notna()) &
        (df["In_min"] - current_min > 0) &
        (df["In_min"] - current_min <= 15) &
        ~df["STATUS"].astype(str).str.upper().str.contains("CANCELLED|DONE|SHIFTED|ARRIVED|ON GOING|ONGOING", na=True)
    ].copy()
    
    # Show toast for new reminders (not snoozed, not dismissed)
    for idx, row in reminder_df.iterrows():
        row_id = row.get('REMINDER_ROW_ID')
        if pd.isna(row_id):
            continue
        patient = row.get("Patient Name", "Unknown")
        mins_left = int(row["In_min"] - current_min)
        
        # Skip if snoozed (still active) or dismissed
        snooze_until = st.session_state.snoozed.get(row_id)
        if (snooze_until is not None and snooze_until > now_epoch) or (row_id in st.session_state.reminder_sent):
            continue

        assistants = ", ".join(
            [
                a
                for a in [
                    str(row.get("FIRST", "")).strip(),
                    str(row.get("SECOND", "")).strip(),
                    str(row.get("Third", "")).strip(),
                ]
                if a and a.lower() not in {"nan", "none"}
            ]
        )
        assistants_text = f" | Assist: {assistants}" if assistants else ""
        
        st.toast(
            f"🔔 Reminder: {patient} in ~{mins_left} min at {row['In Time Str']} with {row.get('DR.','')} (OP {row.get('OP','')}){assistants_text}",
            icon="🔔",
        )

        # Auto-snooze for 30 seconds, and re-alert until status changes.
        next_until = now_epoch + 30
        st.session_state.snoozed[row_id] = next_until
        _persist_reminder_to_storage(row_id, next_until, False)
    
    # Reminder management UI
    def _safe_key(s):
        return re.sub(r"\W+", "_", str(s))
    
    with st.expander("🔔 Manage Reminders", expanded=False):
        if reminder_df.empty:
            st.caption("No upcoming appointments in the next 15 minutes.")
        else:
            for idx, row in reminder_df.iterrows():
                row_id = row.get('REMINDER_ROW_ID')
                if pd.isna(row_id):
                    continue
                patient = row.get('Patient Name', 'Unknown')
                mins_left = int(row["In_min"] - current_min)

                assistants = ", ".join(
                    [
                        a
                        for a in [
                            str(row.get("FIRST", "")).strip(),
                            str(row.get("SECOND", "")).strip(),
                            str(row.get("Third", "")).strip(),
                        ]
                        if a and a.lower() not in {"nan", "none"}
                    ]
                )
                assistants_text = f" — Assist: {assistants}" if assistants else ""
                
                col1, col2, col3, col4, col5 = st.columns([4,1,1,1,1])
                col1.markdown(
                    f"**{patient}** — {row.get('Procedure','')} (in ~{mins_left} min at {row.get('In Time Str','')}){assistants_text}"
                )  
                
                default_snooze_seconds = int(st.session_state.get("default_snooze_seconds", 30))
                if col2.button(f"💤 {default_snooze_seconds}s", key=f"snooze_{_safe_key(row_id)}_default"):
                    until = now_epoch + default_snooze_seconds
                    st.session_state.snoozed[row_id] = until
                    st.session_state.reminder_sent.discard(row_id)
                    _persist_reminder_to_storage(row_id, until, False)
                    st.toast(f"😴 Snoozed {patient} for {default_snooze_seconds} sec", icon="💤")
                    st.rerun()
                    
                if col3.button("💤 30s", key=f"snooze_{_safe_key(row_id)}_30s"):
                    until = now_epoch + 30
                    st.session_state.snoozed[row_id] = until
                    st.session_state.reminder_sent.discard(row_id)
                    _persist_reminder_to_storage(row_id, until, False)
                    st.toast(f"😴 Snoozed {patient} for 30 sec", icon="💤")
                    st.rerun()
                    
                if col4.button("💤 60s", key=f"snooze_{_safe_key(row_id)}_60s"):
                    until = now_epoch + 60
                    st.session_state.snoozed[row_id] = until
                    st.session_state.reminder_sent.discard(row_id)
                    _persist_reminder_to_storage(row_id, until, False)
                    st.toast(f"😴 Snoozed {patient} for 60 sec", icon="💤")
                    st.rerun()
                    
                if col5.button("🗑️", key=f"dismiss_{_safe_key(row_id)}"):
                    st.session_state.reminder_sent.add(row_id)
                    _persist_reminder_to_storage(row_id, None, True)
                    st.toast(f"✅ Dismissed reminder for {patient}", icon="✅")
                    st.rerun()
            
            # Show snoozed reminders
            if st.session_state.snoozed:
                st.markdown("---")
                st.markdown("**Snoozed Reminders**")
                for row_id, until in list(st.session_state.snoozed.items()):
                    remaining_sec = int(until - now_epoch)
                    if remaining_sec > 0:
                        match_row = df[df.get('REMINDER_ROW_ID') == row_id]
                        if not match_row.empty:
                            name = match_row.iloc[0].get('Patient Name', row_id)
                            c1, c2 = st.columns([4,1])
                            c1.write(f"🕐 {name} — {remaining_sec} sec remaining")
                            if c2.button("Cancel", key=f"cancel_{_safe_key(row_id)}"):
                                del st.session_state.snoozed[row_id]
                                _persist_reminder_to_storage(row_id, None, False)
                                st.toast(f"✅ Cancelled snooze for {name}", icon="✅")
                                st.rerun()

# New arrivals (manual status change in Excel)
current_arrived = set(df_raw[df_raw["STATUS"].astype(str).str.upper() == "ARRIVED"]["Patient Name"].dropna())
if ("STATUS" in st.session_state.prev_raw.columns) and ("Patient Name" in st.session_state.prev_raw.columns):
    prev_arrived = set(
        st.session_state.prev_raw[
            st.session_state.prev_raw["STATUS"].astype(str).str.upper() == "ARRIVED"
        ]["Patient Name"].dropna()
    )
else:
    prev_arrived = set()
new_arrived = current_arrived - prev_arrived
for patient in new_arrived:
    row = df[df["Patient Name"] == patient].iloc[0]
    st.toast(f"👤 Patient ARRIVED: {patient} – {row['Procedure']}", icon="🟡")

# Update session state for next run
st.session_state.prev_ongoing = current_ongoing
st.session_state.prev_upcoming = current_upcoming
st.session_state.prev_raw = df_raw.copy()

# ================ Status Colors ================
def get_status_background(status):
    # Return subtle styling without bright backgrounds
    s = str(status).strip().upper()
    if "ON GOING" in s or "ONGOING" in s:
        return "border-left: 4px solid #10b981"
    elif "DONE" in s:
        return "border-left: 4px solid #3b82f6"
    elif "CANCELLED" in s:
        return "border-left: 4px solid #ef4444"
    elif "ARRIVED" in s:
        return "border-left: 4px solid #f59e0b"
    elif "SHIFTED" in s:
        return "border-left: 4px solid #99582f"
    return ""

def highlight_row(row):
    color = get_status_background(row["STATUS"])
    return [color for _ in row]

# ================ Full Schedule ================
st.markdown("### 📅 Full Today's Schedule")

# Add new patient button and save button
col_add, col_save, col_del_pick, col_del_btn, col_search = st.columns([0.20, 0.16, 0.18, 0.07, 0.39])

# Selected patient from external patient DB (optional)
if "selected_patient_id" not in st.session_state:
    st.session_state.selected_patient_id = ""
if "selected_patient_name" not in st.session_state:
    st.session_state.selected_patient_name = ""

with col_add:
    if st.button(
        "➕ Add Patient",
        key="add_patient_btn",
        help="Add a new patient row (uses selected patient if chosen)",
        use_container_width=True,
    ):
        # Create a new empty row
        new_row = {
            "Patient ID": str(st.session_state.selected_patient_id or "").strip(),
            "Patient Name": str(st.session_state.selected_patient_name or "").strip(),
            "In Time": None,
            "Out Time": None,
            "Procedure": "",
            "DR.": "",
            "FIRST": "",
            "SECOND": "",
            "Third": "",
            "CASE PAPER": "",
            "OP": "",
            "SUCTION": False,
            "CLEANING": False,
            "STATUS": "WAITING",
            "REMINDER_ROW_ID": str(uuid.uuid4()),
            "REMINDER_SNOOZE_UNTIL": pd.NA,
            "REMINDER_DISMISSED": False
        }
        # Append to the original dataframe
        new_row_df = pd.DataFrame([new_row])
        df_raw_with_new = pd.concat([df_raw, new_row_df], ignore_index=True)
        # Save immediately
        save_data(df_raw_with_new, message="New patient row added!")
        st.rerun()

with col_save:
    if st.button(
        "💾 Save",
        key="manual_save_btn",
        help="Save changes to storage",
        use_container_width=True,
    ):
        try:
            # Manually save current data
            save_data(df_raw, message="Data saved successfully!")
        except Exception as e:
            st.error(f"Error saving: {e}")

with col_del_pick:
    # Compact delete row control (uses stable REMINDER_ROW_ID)
    try:
        candidates = df_raw.copy()
        if "Patient Name" in candidates.columns:
            candidates["Patient Name"] = candidates["Patient Name"].astype(str).replace("nan", "").fillna("")
        if "REMINDER_ROW_ID" in candidates.columns:
            candidates["REMINDER_ROW_ID"] = candidates["REMINDER_ROW_ID"].astype(str).replace("nan", "").fillna("")

        candidates = candidates[
            (candidates.get("REMINDER_ROW_ID", "").astype(str).str.strip() != "")
        ]

        option_map: dict[str, str] = {}
        if not candidates.empty:
            for row_ix, r in candidates.iterrows():
                rid = str(r.get("REMINDER_ROW_ID", "")).strip()
                if not rid:
                    continue
                pname_raw = str(r.get("Patient Name", "")).strip()
                pname = pname_raw if pname_raw else "(blank row)"
                in_t = str(r.get("In Time", "")).strip()
                op = str(r.get("OP", "")).strip()
                row_no = f"#{int(row_ix) + 1}" if str(row_ix).isdigit() else str(row_ix)
                label = " · ".join([p for p in [row_no, pname, in_t, op] if p])
                # Make option text unique even if labels repeat.
                opt = f"{label} — {rid[:8]}" if label else rid[:8]
                option_map[opt] = rid

        if "delete_row_id" not in st.session_state:
            st.session_state.delete_row_id = ""

        if option_map:
            # Use a visible sentinel option instead of `placeholder` for wider Streamlit compatibility.
            # Also: guard against Streamlit selectbox failing when the previously selected value
            # is no longer present in the new options list (common after edits/deletes).
            sentinel = "Select row to delete…"
            options = [sentinel] + sorted(option_map.keys())

            # IMPORTANT: Do not mutate st.session_state["delete_row_select"] here.
            # Streamlit raises if you modify a widget key after it has been instantiated.
            prev_choice = st.session_state.get("delete_row_select", sentinel)
            default_index = options.index(prev_choice) if prev_choice in options else 0

            chosen = st.selectbox(
                "Delete row",
                options=options,
                key="delete_row_select",
                label_visibility="collapsed",
                index=default_index,
            )
            if chosen and chosen != sentinel:
                st.session_state.delete_row_id = option_map.get(chosen, "")
            else:
                st.session_state.delete_row_id = ""
        else:
            st.session_state.delete_row_id = ""
            st.caption("Delete row")
    except Exception:
        # Keep dashboard usable even if data is incomplete
        st.caption("Delete row")

with col_del_btn:
    if st.button("⌫", key="delete_row_btn", help="Delete selected row"):
        rid = str(st.session_state.get("delete_row_id", "") or "").strip()
        if not rid:
            st.warning("Select a row to delete")
        else:
            try:
                if "REMINDER_ROW_ID" not in df_raw.columns:
                    raise ValueError("Missing REMINDER_ROW_ID column")
                df_updated = df_raw[df_raw["REMINDER_ROW_ID"].astype(str) != rid].copy()

                # Clear local reminder state for this row id.
                try:
                    if "snoozed" in st.session_state and rid in st.session_state.snoozed:
                        del st.session_state.snoozed[rid]
                    if "reminder_sent" in st.session_state:
                        st.session_state.reminder_sent.discard(rid)
                except Exception:
                    pass

                save_data(df_updated, message="Row deleted")
                st.session_state.delete_row_id = ""
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting row: {e}")

with col_search:
    if USE_SUPABASE and SUPABASE_AVAILABLE:
        sup_url, sup_key, _, _ = _get_supabase_config_from_secrets_or_env()
        patients_table, id_col, name_col = _get_patients_config_from_secrets_or_env()

        s_col, m_col = st.columns([0.55, 0.45], vertical_alignment="bottom")

        with s_col:
            patient_query = st.text_input(
                "Patient search",
                value="",
                key="patient_search",
                placeholder="Search patient…",
                label_visibility="collapsed",
            )

        q = str(patient_query or "").strip()
        try:
            results = search_patients_from_supabase(
                sup_url, sup_key, patients_table, id_col, name_col, q, 20
            )
        except Exception as e:
            err_text = str(e)
            st.error("Patient search is not connected.")
            st.caption(f"Error: {err_text}")

            # Common case: table doesn't exist yet.
            if "PGRST205" in err_text or "Could not find the table" in err_text:
                with st.expander("✅ Fix: Create the patients table", expanded=True):
                    st.markdown(
                        "Your Supabase project does not have the patient master table yet. "
                        "Create it in Supabase → SQL Editor, then reload the app."
                    )
                    st.code(
                        "create table if not exists patients (\n"
                        "  id text primary key,\n"
                        "  name text not null\n"
                        ");\n\n"
                        "create index if not exists patients_name_idx on patients (name);\n",
                        language="sql",
                    )
                    st.markdown(
                        "If your patient table/columns have different names, set these in Streamlit Secrets:"
                    )
                    st.code(
                        "supabase_patients_table = \"patients\"\n"
                        "supabase_patients_id_col = \"id\"\n"
                        "supabase_patients_name_col = \"name\"\n",
                        language="toml",
                    )
            else:
                st.warning(
                    f"Check Supabase table/columns: {patients_table}({id_col}, {name_col}). "
                    "If you are using an anon key, RLS may block reads; add `supabase_service_role_key` in Secrets "
                    "or create an RLS policy for the patients table."
                )
            results = []

        with m_col:
            if results:
                option_map = {f"{p['name']} · {p['id']}": (p["id"], p["name"]) for p in results}
                option_strings = [""] + list(option_map.keys())

                chosen_str = st.selectbox(
                    "Matches",
                    options=option_strings,
                    key="patient_select",
                    label_visibility="collapsed",
                )
                if chosen_str and chosen_str in option_map:
                    pid, pname = option_map[chosen_str]
                    st.session_state.selected_patient_id = str(pid)
                    st.session_state.selected_patient_name = str(pname)
            else:
                st.caption("Matches")

        if (not results) and q:
            st.caption("No matches")

        if st.session_state.selected_patient_id or st.session_state.selected_patient_name:
            st.caption(
                f"Selected: {st.session_state.selected_patient_id} - {st.session_state.selected_patient_name}"
            )

all_sorted = df
display_all = all_sorted[["Patient Name", "In Time Obj", "Out Time Obj", "Procedure", "DR.", "FIRST", "SECOND", "Third", "CASE PAPER", "OP", "SUCTION", "CLEANING", "STATUS"]].copy()
display_all = display_all.rename(columns={"In Time Obj": "In Time", "Out Time Obj": "Out Time"})
# Preserve original index for mapping edits back to df_raw
display_all["_orig_idx"] = display_all.index
display_all = display_all.reset_index(drop=True)

# Convert text columns to string to avoid type compatibility issues (BUT NOT TIME/BOOL COLUMNS)
for col in ["Patient Name", "Procedure", "DR.", "FIRST", "SECOND", "Third", "CASE PAPER", "OP", "STATUS"]:
    if col in display_all.columns:
        display_all[col] = display_all[col].astype(str).replace('nan', '')

# Keep In Time and Out Time as time objects for proper display
display_all["In Time"] = display_all["In Time"].apply(lambda v: v if isinstance(v, time) else None)
display_all["Out Time"] = display_all["Out Time"].apply(lambda v: v if isinstance(v, time) else None)

edited_all = st.data_editor(
    display_all, 
    width="stretch", 
    key="full_schedule_editor", 
    hide_index=True,
    column_config={
        "_orig_idx": None,  # Hide the original index column
        "Patient Name": st.column_config.TextColumn(label="Patient Name"),
        "In Time": st.column_config.TimeColumn(label="In Time", format="hh:mm A"),
        "Out Time": st.column_config.TimeColumn(label="Out Time", format="hh:mm A"),
        "Procedure": st.column_config.TextColumn(label="Procedure"),
        "DR.": st.column_config.SelectboxColumn(
            label="DR.",
            options=["DR.HUSAIN", "DR.FARHATH", "DR.KALPANA", "DR.SHIFA", "DR.SHRUTI", "DR.NIMAI", "DR.MANVEEN", "DR.NEHA"],
            required=False
        ),
        "OP": st.column_config.SelectboxColumn(
            label="OP",
            options=["OP 1", "OP 2", "OP 3", "OP 4"],
            required=False
        ),
        "FIRST": st.column_config.SelectboxColumn(
            label="FIRST",
            options=["RAJA", "NITIN", "BABU", "PRAMOTH", "RESHMA", "ANSHIKA", "ARCHANA", "LAVNYA", "SAKSHI", "MUKHILA", "ROHINI", "SUHASNI"],
            required=False
        ),
        "SECOND": st.column_config.SelectboxColumn(
            label="SECOND",
            options=["RAJA", "NITIN", "BABU", "PRAMOTH", "RESHMA", "ANSHIKA", "ARCHANA", "LAVNYA", "SAKSHI", "MUKHILA", "ROHINI", "SUHASNI"],
            required=False
        ),
        "Third": st.column_config.SelectboxColumn(
            label="Third",
            options=["RAJA", "NITIN", "BABU", "PRAMOTH", "RESHMA", "ANSHIKA", "ARCHANA", "LAVNYA", "SAKSHI", "MUKHILA", "ROHINI", "SUHASNI"],
            required=False
        ),
        "CASE PAPER": st.column_config.SelectboxColumn(
            label="CASE PAPER",
            options=["RAJA", "NITIN", "BABU", "PRAMOTH", "RESHMA", "ANSHIKA", "ARCHANA", "LAVNYA", "SAKSHI", "MUKHILA", "ROHINI", "SUHASNI"],
            required=False
        ),
        "SUCTION": st.column_config.CheckboxColumn(label="✨ SUCTION"),
        "CLEANING": st.column_config.CheckboxColumn(label="🧹 CLEANING"),
        "STATUS": st.column_config.SelectboxColumn(
            label="STATUS",
            options=["WAITING", "ARRIVED", "ON GOING", "CANCELLED", "SHIFTED", "DONE"],
            required=False
        )
    }
)

# ================ Auto-save edited data to Excel ================
if edited_all is not None:
    # Compare non-time columns to detect changes (time columns need special handling due to object type)
    has_changes = False
    if not edited_all.equals(display_all):
        # Check actual value differences (skip _orig_idx which is for internal tracking)
        for col in edited_all.columns:
            if col not in ["In Time", "Out Time", "_orig_idx"]:
                if not (edited_all[col] == display_all[col]).all():
                    has_changes = True
                    break
        # For time columns, compare the string representation
        if not has_changes:
            for col in ["In Time", "Out Time"]:
                if col in edited_all.columns:
                    edited_times = edited_all[col].astype(str)
                    display_times = display_all[col].astype(str)
                    if not (edited_times == display_times).all():
                        has_changes = True
                        break
    
    if has_changes:
        try:
            # Create a copy of the raw data to update
            df_updated = df_raw.copy()
            
            # Process edited data and convert back to original format
            for idx, row in edited_all.iterrows():
                # Use the preserved original index to map back to df_raw
                orig_idx = row.get("_orig_idx", idx)
                if pd.isna(orig_idx):
                    orig_idx = idx
                orig_idx = int(orig_idx)
                
                if orig_idx < len(df_updated):
                    try:
                        # Handle Patient ID (optional)
                        if "Patient ID" in row.index and "Patient ID" in df_updated.columns:
                            pid = str(row.get("Patient ID", "")).strip()
                            if pid.lower() in {"nan", "none"}:
                                pid = ""
                            df_updated.iloc[orig_idx, df_updated.columns.get_loc("Patient ID")] = pid

                        # Handle Patient Name
                        patient_name = str(row["Patient Name"]).strip() if row["Patient Name"] and str(row["Patient Name"]) != "" else ""
                        if patient_name == "":
                            # Clear row if patient name is empty, but preserve stable row id
                            # so users can still delete the blank row from the dropdown.
                            for col in df_updated.columns:
                                if col == "REMINDER_ROW_ID":
                                    continue
                                if col == "REMINDER_SNOOZE_UNTIL":
                                    df_updated.iloc[orig_idx, df_updated.columns.get_loc(col)] = pd.NA
                                    continue
                                if col == "REMINDER_DISMISSED":
                                    df_updated.iloc[orig_idx, df_updated.columns.get_loc(col)] = False
                                    continue
                                df_updated.iloc[orig_idx, df_updated.columns.get_loc(col)] = ""
                            continue
                        df_updated.iloc[orig_idx, df_updated.columns.get_loc("Patient Name")] = patient_name
                        
                        # Handle In Time - properly convert time object to HH:MM string for Excel
                        if "In Time" in row.index:
                            in_time_val = row["In Time"]
                            t = _coerce_to_time_obj(in_time_val)
                            time_str = f"{t.hour:02d}:{t.minute:02d}" if t is not None else ""
                            df_updated.iloc[orig_idx, df_updated.columns.get_loc("In Time")] = time_str
                        
                        # Handle Out Time - properly convert time object to HH:MM string for Excel
                        if "Out Time" in row.index:
                            out_time_val = row["Out Time"]
                            t = _coerce_to_time_obj(out_time_val)
                            time_str = f"{t.hour:02d}:{t.minute:02d}" if t is not None else ""
                            df_updated.iloc[orig_idx, df_updated.columns.get_loc("Out Time")] = time_str
                        
                        # Handle other columns
                        for col in ["Procedure", "DR.", "FIRST", "SECOND", "Third", "CASE PAPER", "OP", "STATUS"]:
                            if col in row.index and col in df_updated.columns:
                                val = row[col]
                                clean_val = str(val).strip() if val and str(val) != "nan" else ""
                                df_updated.iloc[orig_idx, df_updated.columns.get_loc(col)] = clean_val
                        
                        # Handle checkbox columns (SUCTION, CLEANING) - convert boolean to check mark or empty
                        for col in ["SUCTION", "CLEANING"]:
                            if col in row.index and col in df_updated.columns:
                                val = row[col]
                                # Store True as "✓" checkmark, False/None as empty string
                                if pd.isna(val) or val is None or val == False:
                                    df_updated.iloc[orig_idx, df_updated.columns.get_loc(col)] = ""
                                elif val == True:
                                    df_updated.iloc[orig_idx, df_updated.columns.get_loc(col)] = "✓"
                                else:
                                    df_updated.iloc[orig_idx, df_updated.columns.get_loc(col)] = ""
                    except Exception as col_error:
                        st.warning(f"Warning updating row {orig_idx}: {str(col_error)}")
                        continue
            
            # Write back to storage
            save_data(df_updated, message="Schedule updated!")
            # Auto-refresh all views after saving
            st.rerun()
        except Exception as e:
            st.error(f"Error saving: {e}")

# ================ Per Chair Tabs ================
st.markdown("###  Schedule by OP")
unique_ops = sorted(df["OP"].dropna().unique())

if unique_ops:
    tabs = st.tabs([str(op) for op in unique_ops])
    for tab, op in zip(tabs, unique_ops):
        with tab:
            op_df = df[
                (df["OP"] == op)
                & ~df["STATUS"].astype(str).str.upper().str.contains("CANCELLED|DONE", na=True)
            ]
            display_op = op_df[["Patient ID", "Patient Name", "In Time Obj", "Out Time Obj", "Procedure", "DR.", "OP", "FIRST", "SECOND", "Third", "CASE PAPER", "SUCTION", "CLEANING", "STATUS"]].copy()
            display_op = display_op.rename(columns={"In Time Obj": "In Time", "Out Time Obj": "Out Time"})
            # Preserve original index for mapping edits back to df_raw
            display_op["_orig_idx"] = display_op.index
            display_op = display_op.reset_index(drop=True)
            # Ensure time objects are preserved; Streamlit TimeColumn edits best with None for missing
            display_op["In Time"] = display_op["In Time"].apply(lambda v: v if isinstance(v, time) else None)
            display_op["Out Time"] = display_op["Out Time"].apply(lambda v: v if isinstance(v, time) else None)
            
            edited_op = st.data_editor(
                display_op, 
                width="stretch", 
                key=f"op_{str(op).replace(' ', '_')}_editor", 
                hide_index=True,
                column_config={
                    "_orig_idx": None,
                    "Patient ID": st.column_config.TextColumn(label="Patient ID", required=False),
                    "In Time": st.column_config.TimeColumn(label="In Time", format="hh:mm A"),
                    "Out Time": st.column_config.TimeColumn(label="Out Time", format="hh:mm A"),
                    "DR.": st.column_config.SelectboxColumn(
                        label="DR.",
                        options=["DR.HUSAIN", "DR.FARHATH", "DR.KALPANA", "DR.SHIFA", "DR.SHRUTI", "DR.NIMAI", "DR.MANVEEN", "DR.NEHA"],
                        required=False
                    ),
                    "OP": st.column_config.SelectboxColumn(
                        label="OP",
                        options=["OP 1", "OP 2", "OP 3", "OP 4"],
                        required=False
                    ),
                    "FIRST": st.column_config.SelectboxColumn(
                        label="FIRST",
                        options=["RAJA", "NITIN", "BABU", "PRAMOTH", "RESHMA", "ANSHIKA", "ARCHANA", "LAVNYA", "SAKSHI", "MUKHILA", "ROHINI", "SUHASNI"],
                        required=False
                    ),
                    "SECOND": st.column_config.SelectboxColumn(
                        label="SECOND",
                        options=["RAJA", "NITIN", "BABU", "PRAMOTH", "RESHMA", "ANSHIKA", "ARCHANA", "LAVNYA", "SAKSHI", "MUKHILA", "ROHINI", "SUHASNI"],
                        required=False
                    ),
                    "Third": st.column_config.SelectboxColumn(
                        label="Third",
                        options=["RAJA", "NITIN", "BABU", "PRAMOTH", "RESHMA", "ANSHIKA", "ARCHANA", "LAVNYA", "SAKSHI", "MUKHILA", "ROHINI", "SUHASNI"],
                        required=False
                    ),
                    "CASE PAPER": st.column_config.SelectboxColumn(
                        label="CASE PAPER",
                        options=["RAJA", "NITIN", "BABU", "PRAMOTH", "RESHMA", "ANSHIKA", "ARCHANA", "LAVNYA", "SAKSHI", "MUKHILA", "ROHINI", "SUHASNI"],
                        required=False
                    ),
                    "STATUS": st.column_config.SelectboxColumn(
                        label="STATUS",
                        options=["WAITING", "ARRIVED", "ON GOING", "CANCELLED", "SHIFTED", "DONE"],
                        required=False
                    )
                }
            )

            # Persist edits from OP tabs (previously this editor had no save path)
            if edited_op is not None:
                op_has_changes = False
                if not edited_op.equals(display_op):
                    for col in edited_op.columns:
                        if col not in ["In Time", "Out Time", "_orig_idx"]:
                            if not (edited_op[col] == display_op[col]).all():
                                op_has_changes = True
                                break
                    if not op_has_changes:
                        for col in ["In Time", "Out Time"]:
                            if col in edited_op.columns:
                                edited_times = edited_op[col].astype(str)
                                display_times = display_op[col].astype(str)
                                if not (edited_times == display_times).all():
                                    op_has_changes = True
                                    break

                if op_has_changes:
                    try:
                        df_updated = df_raw.copy()
                        for _, row in edited_op.iterrows():
                            orig_idx = row.get("_orig_idx")
                            if pd.isna(orig_idx):
                                continue
                            orig_idx = int(orig_idx)
                            if orig_idx < 0 or orig_idx >= len(df_updated):
                                continue

                            # Patient ID
                            patient_id = str(row.get("Patient ID", "")).strip()
                            if "Patient ID" in df_updated.columns:
                                df_updated.iloc[orig_idx, df_updated.columns.get_loc("Patient ID")] = patient_id

                            # Patient Name
                            patient_name = str(row.get("Patient Name", "")).strip()
                            if patient_name == "":
                                for c in df_updated.columns:
                                    df_updated.iloc[orig_idx, df_updated.columns.get_loc(c)] = ""
                                continue
                            if "Patient Name" in df_updated.columns:
                                df_updated.iloc[orig_idx, df_updated.columns.get_loc("Patient Name")] = patient_name

                            # Times -> canonical HH:MM strings
                            if "In Time" in df_updated.columns:
                                t = _coerce_to_time_obj(row.get("In Time"))
                                df_updated.iloc[orig_idx, df_updated.columns.get_loc("In Time")] = (
                                    f"{t.hour:02d}:{t.minute:02d}" if t is not None else ""
                                )
                            if "Out Time" in df_updated.columns:
                                t = _coerce_to_time_obj(row.get("Out Time"))
                                df_updated.iloc[orig_idx, df_updated.columns.get_loc("Out Time")] = (
                                    f"{t.hour:02d}:{t.minute:02d}" if t is not None else ""
                                )

                            for c in ["Procedure", "DR.", "OP", "FIRST", "SECOND", "Third", "CASE PAPER", "STATUS"]:
                                if c in row.index and c in df_updated.columns:
                                    val = row.get(c)
                                    clean_val = str(val).strip() if val and str(val) != "nan" else ""
                                    df_updated.iloc[orig_idx, df_updated.columns.get_loc(c)] = clean_val

                            for c in ["SUCTION", "CLEANING"]:
                                if c in row.index and c in df_updated.columns:
                                    val = row.get(c)
                                    if pd.isna(val) or val is None or val is False:
                                        df_updated.iloc[orig_idx, df_updated.columns.get_loc(c)] = ""
                                    elif val is True:
                                        df_updated.iloc[orig_idx, df_updated.columns.get_loc(c)] = "✓"
                                    else:
                                        df_updated.iloc[orig_idx, df_updated.columns.get_loc(c)] = ""

                        save_data(df_updated, message=f"Schedule updated for {op}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving {op} edits: {e}")
else:
    st.info("No chair data available.")


# ================ Doctor Statistics ================
st.markdown("### 👨‍⚕️ Schedule Summary by Doctor")
groupby_column = "DR."
if groupby_column in df.columns and not df[groupby_column].isnull().all():
    try:
        doctor_procedures = df[df["DR."].notna()].groupby("DR.").size().reset_index(name="Total Procedures")
        doctor_procedures = doctor_procedures.reset_index(drop=True)
        if not doctor_procedures.empty:
            edited_doctor = st.data_editor(doctor_procedures, width="stretch", key="doctor_editor", hide_index=True)
        else:
            st.info(f"No data available for '{groupby_column}'.")
    except Exception as e:
        st.error(f"Error processing doctor data: {e}")
else:
    st.info(f"Column '{groupby_column}' not found or contains only empty values.")