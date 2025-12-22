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
# To install required packages, run in your terminal:
# pip install --upgrade pip
# pip install pandas openpyxl streamlit streamlit-autorefresh
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
    "button_text": "#f5f5f5",     # Button text (light)
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
        border-left: 5px solid #3b82f6 !important;
    }}
    
    /* Ongoing rows - Light green */
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("ON GOING")) {{
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.3) 0%, rgba(16, 185, 129, 0.1) 100%) !important;
        border-left: 5px solid #10b981 !important;
    }}
    
    /* Arrived rows - Light yellow */
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("ARRIVED")) {{
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.3) 0%, rgba(245, 158, 11, 0.1) 100%) !important;
        border-left: 5px solid #f59e0b !important;
    }}
    
    /* Cancelled rows - Light red */
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("CANCELLED")) {{
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.3) 0%, rgba(239, 68, 68, 0.1) 100%) !important;
        border-left: 5px solid #ef4444 !important;
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
    
    [data-testid="stDataFrameContainer"] tbody tr:has(td:contains("CANCELLED")):hover {{
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.5) 0%, rgba(239, 68, 68, 0.2) 100%) !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) inset !important;
    }}
    
    /* Table Header Styling - Premium & Elegant */
    [data-testid="stDataFrameContainer"] thead {{
        background: linear-gradient(135deg, #99582f 0%, #7a4629 100%) !important;
        border-bottom: 4px solid #c9bbb0 !important;
        box-shadow: 0 2px 8px rgba(153, 88, 47, 0.15) !important;
    }}
    
    [data-testid="stDataFrameContainer"] thead th {{
        color: #ffffff !important;
        font-weight: 800 !important;
        padding: 18px 16px !important;
        text-align: center !important;
        font-size: 0.99rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        background: linear-gradient(135deg, #99582f 0%, #7a4629 100%) !important;
        position: relative !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border-right: 1px solid rgba(0, 0, 0, 0.1) !important;
    }}
    
    [data-testid="stDataFrameContainer"] thead th:last-child {{
        border-right: none !important;
    }}
    
    [data-testid="stDataFrameContainer"] thead th:hover {{
        background: linear-gradient(135deg, #7a4629 0%, #99582f 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25), 0 4px 12px rgba(153, 88, 47, 0.3) !important;
    }}
    
    /* Premium Table Rows */
    [data-testid="stDataFrameContainer"] tbody tr {{
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border-radius: 0 !important;
        position: relative !important;
    }}
    
    /* Alternating row background for better readability */
    [data-testid="stDataFrameContainer"] tbody tr:nth-child(even) {{
        background-color: rgba(245, 245, 245, 0.6) !important;
    }}
    
    [data-testid="stDataFrameContainer"] tbody tr:hover {{
        background-color: rgba(201, 187, 176, 0.15) !important;
        box-shadow: 0 2px 8px rgba(153, 88, 47, 0.1) inset !important;
        transform: scaleY(1.02) !important;
    }}
    
    /* Premium Table Cells */
    [data-testid="stDataFrameContainer"] tbody td {{
        padding: 15px 16px !important;
        border-bottom: 1px solid #e5ddd0 !important;
        font-size: 0.92rem !important;
        transition: all 0.2s ease !important;
        position: relative !important;
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
        background: linear-gradient(135deg, {COLORS['button_bg']} 0%, #7a4629 100%) !important;
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
        background: linear-gradient(135deg, #7a4629 0%, {COLORS['button_bg']} 100%) !important;
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
        border-radius: 10px !important;
        border: 2px solid #d3c3b0 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
        overflow: hidden !important;
        transition: all 0.3s ease !important;
    }}
    
    [data-testid="stDataFrameContainer"]:hover {{
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
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
        background: linear-gradient(135deg, {COLORS['button_bg']} 0%, #7a4629 100%) !important;
        color: {COLORS['button_text']} !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(153, 88, 47, 0.3) !important;
        padding: 10px 20px !important;
    }}
    
    button[key="manual_save_btn"]:hover {{
        background: linear-gradient(135deg, #7a4629 0%, {COLORS['button_bg']} 100%) !important;
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

# --- Reminder settings in sidebar ---
with st.sidebar:
    st.markdown("## 🔔 Notifications")
    st.checkbox("Enable 15-minute reminders", value=True, key="enable_reminders")
    st.selectbox("Default snooze (minutes)", options=[5,10,15,30], index=0, key="default_snooze")
    st.write("💡 Reminders alert 15 minutes before a patient's In Time.")

# File check using absolute path
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Putt Allotment.xlsx")
if not os.path.exists(file_path):
    st.error(f"⚠️ 'Putt Allotment.xlsx' not found in the same folder as this script: {file_path}. Place the file there and restart.")
    st.stop()

# Auto-refresh every 60 seconds (with countdown visible)
st_autorefresh(interval=60000, debounce=True, key="autorefresh")

# Load raw data (fresh every run for real-time accuracy)
# Retry logic to handle temporary file corruption during concurrent writes
max_retries = 3
retry_delay = 0.5  # seconds
df_raw = None

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
                st.error("⚠️ The Excel file appears to be corrupted or is being modified. Please try refreshing the page in a few seconds.")
                st.info("💡 If this persists, check if the 'Putt Allotment.xlsx' file is valid and not open in another application.")
                st.stop()
        else:
            # Re-raise non-corruption related errors
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
    if pd.isna(time_value) or time_value == "":
        return "N/A"
    
    try:
        # Handle datetime.time objects (from Excel/openpyxl reading time as datetime.time)
        if isinstance(time_value, time):
            return f"{time_value.hour:02d}:{time_value.minute:02d}"
        
        # Handle datetime objects (in case Excel interprets as datetime)
        if isinstance(time_value, datetime):
            return f"{time_value.hour:02d}:{time_value.minute:02d}"
        
        # If it's already a string in HH.MM or HH:MM format
        if isinstance(time_value, str):
            time_str = time_value.strip()
            # Handle HH.MM format (from Excel)
            if "." in time_str:
                parts = time_str.split(".")
                if len(parts) == 2:
                    try:
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        return f"{hours:02d}:{minutes:02d}"
                    except ValueError:
                        pass
            # Handle HH:MM format
            if ":" in time_str:
                parts = time_str.split(":")
                if len(parts) == 2:
                    try:
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        return f"{hours:02d}:{minutes:02d}"
                    except ValueError:
                        pass
        
        # Handle numeric formats (could be float or int)
        try:
            num_val = float(time_value)
            # Check if it's a time value between 0-24 with decimal (like 9.30)
            # IMPORTANT: The decimal part represents MINUTES directly (e.g., 9.30 = 9:30, NOT 9 + 0.30*60)
            if 0 <= num_val < 24:
                hours = int(num_val)
                # Get decimal part - this IS the minutes (e.g., .30 = 30 minutes)
                decimal_part = num_val - hours
                # Multiply by 100 to get minutes directly (9.30 -> 0.30 -> 30 minutes)
                minutes = round(decimal_part * 100)
                if minutes >= 60:
                    # If someone entered 9.75 meaning 9:45, handle both interpretations
                    # Check if it looks like it was meant to be minutes (30, 45, etc.)
                    if minutes <= 99:
                        # It's likely meant as direct minutes (e.g., 9.30 = 9:30)
                        pass
                    else:
                        # Fallback: treat as fractional hours
                        minutes = round(decimal_part * 60)
                if minutes >= 60:
                    hours += 1
                    minutes = 0
                return f"{hours:02d}:{minutes:02d}"
            # Handle Excel serial time format (0.625 = 15:00)
            elif 0 <= num_val <= 1:
                total_minutes = round(num_val * 1440)
                hours = total_minutes // 60
                minutes = total_minutes % 60
                return f"{hours:02d}:{minutes:02d}"
        except (ValueError, TypeError):
            pass
            
    except (ValueError, TypeError, AttributeError):
        pass
    
    return "N/A"

# Define all time conversion functions first
def safe_str_to_time_obj(time_str):
    """Convert time string to time object safely"""
    if pd.isna(time_str) or time_str == "N/A" or time_str == "" or time_str is None:
        return None
    try:
        # If it's already a time object, return it directly
        if isinstance(time_str, time):
            return time_str
        
        # Handle datetime objects (extract time part)
        if isinstance(time_str, datetime):
            return time(time_str.hour, time_str.minute)
        
        time_str = str(time_str).strip()
        
        # Handle HH:MM format (with colon)
        if ":" in time_str:
            parts = time_str.split(":")
            if len(parts) == 2:
                try:
                    h = int(parts[0])
                    m = int(parts[1])
                    if 0 <= h < 24 and 0 <= m < 60:
                        return time(h, m)
                except (ValueError, TypeError):
                    pass
        
        # Handle HH.MM format (from Excel - dot separator)
        if "." in time_str:
            parts = time_str.split(".")
            if len(parts) == 2:
                try:
                    h = int(parts[0])
                    m = int(parts[1])
                    if 0 <= h < 24 and 0 <= m < 60:
                        return time(h, m)
                except (ValueError, TypeError):
                    pass
    except (ValueError, IndexError, AttributeError, TypeError):
        pass
    
    return None

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
    if pd.isna(val) or val == "" or val == "False":
        return False
    elif val == "✓" or str(val).strip().upper() == "TRUE":
        return True
    # Any other content is considered as True (was marked)
    elif str(val).strip() != "":
        return True
    return False

# Convert existing checkbox data
if "SUCTION" in df.columns:
    df["SUCTION"] = df["SUCTION"].apply(str_to_checkbox)
if "CLEANING" in df.columns:
    df["CLEANING"] = df["CLEANING"].apply(str_to_checkbox)


# Convert time values to minutes since midnight for comparison
def time_to_minutes(time_value):
    if pd.isna(time_value) or time_value == "":
        return pd.NA
    
    try:
        # Handle datetime.time objects (from Excel/openpyxl reading time as datetime.time)
        if isinstance(time_value, time):
            return time_value.hour * 60 + time_value.minute
        
        # Handle datetime objects (in case Excel interprets as datetime)
        if isinstance(time_value, datetime):
            return time_value.hour * 60 + time_value.minute
        
        # If it's a string in HH.MM or HH:MM format
        if isinstance(time_value, str):
            time_str = time_value.strip()
            # Handle HH.MM format
            if "." in time_str:
                parts = time_str.split(".")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    return hours * 60 + minutes
            # Handle HH:MM format
            elif ":" in time_str:
                parts = time_str.split(":")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    return hours * 60 + minutes
        
        # Handle numeric format (e.g., 9.3 or 9.30 from Excel)
        dec_float = float(time_value)
        # Check if it's an Excel serial time (0-1 range)
        if 0 <= dec_float <= 1:
            return round(dec_float * 1440)
        # Handle HH.MM format as number (e.g., 9.30 = 9 hours, 30 minutes)
        elif 0 < dec_float < 24:
            hours = int(dec_float)
            # Decimal part represents minutes directly (e.g., .30 = 30 minutes)
            decimal_part = dec_float - hours
            minutes = round(decimal_part * 100)
            # Ensure minutes are valid
            if minutes > 59:
                minutes = round(decimal_part * 60)  # Fallback to fractional interpretation
            return hours * 60 + minutes
    except (ValueError, TypeError, AttributeError):
        pass
    
    return pd.NA

df["In_min"] = df["In Time"].apply(time_to_minutes).astype('Int64')
df["Out_min"] = df["Out Time"].apply(time_to_minutes).astype('Int64')

# Handle possible overnight cases
df.loc[df["Out_min"] < df["In_min"], "Out_min"] += 1440

# Current time in minutes (same day)
current_min = now.hour * 60 + now.minute

# ================ Reminder Persistence Setup ================
# Add stable row IDs and reminder columns if they don't exist
if 'REMINDER_ROW_ID' not in df_raw.columns:
    df_raw['REMINDER_ROW_ID'] = [str(uuid.uuid4()) for _ in range(len(df_raw))]
    # Save IDs immediately
    try:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df_raw.to_excel(writer, sheet_name='Sheet1', index=False)
        st.toast("🆔 Generated stable row IDs for reminders", icon="✅")
    except Exception:
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

# Helper to persist reminder state
def _persist_reminder_to_excel(row_id, until, dismissed):
    """Persist snooze/dismiss fields back to Excel by row ID."""
    try:
        match = df_raw[df_raw.get('REMINDER_ROW_ID') == row_id]
        if not match.empty:
            ix = match.index[0]
            df_raw.at[ix, 'REMINDER_SNOOZE_UNTIL'] = int(until) if until is not None else pd.NA
            df_raw.at[ix, 'REMINDER_DISMISSED'] = bool(dismissed)
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_raw.to_excel(writer, sheet_name='Sheet1', index=False)
            return True
    except Exception as e:
        st.error(f"Error persisting reminder: {e}")
    return False

# ================ Change Detection & Notifications ================
if 'prev_hash' not in st.session_state:
    st.session_state.prev_hash = None
    st.session_state.prev_ongoing = set()
    st.session_state.prev_upcoming = set()
    st.session_state.prev_raw = pd.DataFrame()
    st.session_state.reminder_sent = set()  # Track reminders by row ID
    st.session_state.snoozed = {}  # Map row_id -> snooze_until_min

# Load persisted reminders from Excel
for idx, row in df_raw.iterrows():
    try:
        row_id = row.get('REMINDER_ROW_ID')
        if pd.notna(row_id):
            until = row.get('REMINDER_SNOOZE_UNTIL')
            if pd.notna(until) and int(until) > current_min:
                st.session_state.snoozed[row_id] = int(until)
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
    expired = [rid for rid, until in list(st.session_state.snoozed.items()) if until <= current_min]
    for rid in expired:
        del st.session_state.snoozed[rid]
        _persist_reminder_to_excel(rid, None, False)
    
    # Find patients needing reminders (0-15 min before In Time)
    reminder_df = df[
        (df["In_min"].notna()) &
        (df["In_min"] - current_min > 0) &
        (df["In_min"] - current_min <= 15) &
        ~df["STATUS"].astype(str).str.upper().str.contains("CANCELLED|DONE|SHIFTED", na=True)
    ].copy()
    
    # Show toast for new reminders (not snoozed, not dismissed)
    for idx, row in reminder_df.iterrows():
        row_id = row.get('REMINDER_ROW_ID')
        if pd.isna(row_id):
            continue
        patient = row.get("Patient Name", "Unknown")
        mins_left = int(row["In_min"] - current_min)
        
        # Skip if snoozed or already reminded
        if row_id in st.session_state.snoozed or row_id in st.session_state.reminder_sent:
            continue
        
        st.toast(f"🔔 Reminder: {patient} in ~{mins_left} min at {row['In Time Str']} with {row.get('DR.','')} (OP {row.get('OP','')})", icon="🔔")
        st.session_state.reminder_sent.add(row_id)
    
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
                
                col1, col2, col3, col4, col5 = st.columns([4,1,1,1,1])
                col1.markdown(f"**{patient}** — {row.get('Procedure','')} (in ~{mins_left} min at {row.get('In Time Str','')})")  
                
                default_snooze = int(st.session_state.get("default_snooze", 5))
                if col2.button(f"💤 {default_snooze}min", key=f"snooze_{_safe_key(row_id)}_default"):
                    until = current_min + default_snooze
                    st.session_state.snoozed[row_id] = until
                    st.session_state.reminder_sent.discard(row_id)
                    _persist_reminder_to_excel(row_id, until, False)
                    st.toast(f"😴 Snoozed {patient} for {default_snooze} min", icon="💤")
                    st.rerun()
                    
                if col3.button("💤 5", key=f"snooze_{_safe_key(row_id)}_5"):
                    until = current_min + 5
                    st.session_state.snoozed[row_id] = until
                    st.session_state.reminder_sent.discard(row_id)
                    _persist_reminder_to_excel(row_id, until, False)
                    st.toast(f"😴 Snoozed {patient} for 5 min", icon="💤")
                    st.rerun()
                    
                if col4.button("💤 10", key=f"snooze_{_safe_key(row_id)}_10"):
                    until = current_min + 10
                    st.session_state.snoozed[row_id] = until
                    st.session_state.reminder_sent.discard(row_id)
                    _persist_reminder_to_excel(row_id, until, False)
                    st.toast(f"😴 Snoozed {patient} for 10 min", icon="💤")
                    st.rerun()
                    
                if col5.button("🗑️", key=f"dismiss_{_safe_key(row_id)}"):
                    st.session_state.reminder_sent.add(row_id)
                    _persist_reminder_to_excel(row_id, None, True)
                    st.toast(f"✅ Dismissed reminder for {patient}", icon="✅")
                    st.rerun()
            
            # Show snoozed reminders
            if st.session_state.snoozed:
                st.markdown("---")
                st.markdown("**Snoozed Reminders**")
                for row_id, until in list(st.session_state.snoozed.items()):
                    remaining = until - current_min
                    if remaining > 0:
                        match_row = df[df.get('REMINDER_ROW_ID') == row_id]
                        if not match_row.empty:
                            name = match_row.iloc[0].get('Patient Name', row_id)
                            c1, c2 = st.columns([4,1])
                            c1.write(f"🕐 {name} — {remaining} min remaining")
                            if c2.button("Cancel", key=f"cancel_{_safe_key(row_id)}"):
                                del st.session_state.snoozed[row_id]
                                _persist_reminder_to_excel(row_id, None, False)
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
col1, col2, col3 = st.columns([0.15, 0.15, 0.7])
with col1:
    if st.button("➕ Add Patient", width="stretch"):
        # Create a new empty row
        new_row = {
            "Patient Name": "",
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
        # Save immediately to Excel
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df_raw_with_new.to_excel(writer, sheet_name="Sheet1", index=False)
        st.toast("✅ New patient row added with WAITING status!", icon="➕")
        st.rerun()

with col2:
    if st.button("💾 Save", width="stretch", key="manual_save_btn"):
        try:
            # Manually save current data to Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_raw.to_excel(writer, sheet_name="Sheet1", index=False)
            st.toast("💾 Data saved successfully!", icon="✅")
        except Exception as e:
            st.error(f"Error saving: {e}")

all_sorted = df
display_all = all_sorted[["Patient Name", "In Time Obj", "Out Time Obj", "Procedure", "DR.", "FIRST", "SECOND", "Third", "CASE PAPER", "OP", "SUCTION", "CLEANING", "STATUS"]].copy()
display_all = display_all.rename(columns={"In Time Obj": "In Time", "Out Time Obj": "Out Time"})
# Preserve original index for mapping edits back to df_raw
display_all["_orig_idx"] = display_all.index
display_all = display_all.reset_index(drop=True)

# Convert all text columns to string to avoid type compatibility issues (BUT NOT TIME COLUMNS)
for col in ["Patient Name", "Procedure", "DR.", "FIRST", "SECOND", "Third", "CASE PAPER", "OP", "SUCTION", "CLEANING", "STATUS"]:
    if col in display_all.columns:
        display_all[col] = display_all[col].astype(str).replace('nan', '')

# Keep In Time and Out Time as time objects for proper display
display_all["In Time"] = display_all["In Time"].fillna(pd.NaT)
display_all["Out Time"] = display_all["Out Time"].fillna(pd.NaT)

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
            options=["WAITING", "ARRIVED", "ON GOING", "CANCELLED"],
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
                        # Handle Patient Name
                        patient_name = str(row["Patient Name"]).strip() if row["Patient Name"] and str(row["Patient Name"]) != "" else ""
                        if patient_name == "":
                            # Clear entire row if patient name is empty
                            for col in df_updated.columns:
                                df_updated.iloc[orig_idx, df_updated.columns.get_loc(col)] = ""
                            continue
                        df_updated.iloc[orig_idx, df_updated.columns.get_loc("Patient Name")] = patient_name
                        
                        # Handle In Time - properly convert time object to HH:MM string for Excel
                        if "In Time" in row.index:
                            in_time_val = row["In Time"]
                            time_str = ""
                            if in_time_val is not None and not pd.isna(in_time_val) and str(in_time_val) != "NaT":
                                if isinstance(in_time_val, time):
                                    # Use colon format (HH:MM) so Excel preserves it as text
                                    time_str = f"{in_time_val.hour:02d}:{in_time_val.minute:02d}"
                                else:
                                    time_str = str(in_time_val)
                            df_updated.iloc[orig_idx, df_updated.columns.get_loc("In Time")] = time_str
                        
                        # Handle Out Time - properly convert time object to HH:MM string for Excel
                        if "Out Time" in row.index:
                            out_time_val = row["Out Time"]
                            time_str = ""
                            if out_time_val is not None and not pd.isna(out_time_val) and str(out_time_val) != "NaT":
                                if isinstance(out_time_val, time):
                                    # Use colon format (HH:MM) so Excel preserves it as text
                                    time_str = f"{out_time_val.hour:02d}:{out_time_val.minute:02d}"
                                else:
                                    time_str = str(out_time_val)
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
            
            # Write back to Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_updated.to_excel(writer, sheet_name="Sheet1", index=False)
            
            st.toast("✅ Schedule updated in Excel!", icon="💾")
            # Auto-refresh all views after saving
            st.rerun()
        except Exception as e:
            st.error(f"Error saving to Excel: {e}")

# ================ Per Chair Tabs ================
st.markdown("###  Schedule by OP")
unique_ops = sorted(df["OP"].dropna().unique())

if unique_ops:
    tabs = st.tabs([str(op) for op in unique_ops])
    for tab, op in zip(tabs, unique_ops):
        with tab:
            op_df = df[df["OP"] == op]
            display_op = op_df[["Patient Name", "In Time Obj", "Out Time Obj", "Procedure", "DR.", "FIRST", "SECOND", "Third", "CASE PAPER", "SUCTION", "CLEANING", "STATUS"]].copy()
            display_op = display_op.rename(columns={"In Time Obj": "In Time", "Out Time Obj": "Out Time"})
            display_op = display_op.reset_index(drop=True)
            # Ensure time objects are preserved
            display_op["In Time"] = display_op["In Time"].fillna(pd.NaT)
            display_op["Out Time"] = display_op["Out Time"].fillna(pd.NaT)
            
            edited_op = st.data_editor(
                display_op, 
                width="stretch", 
                key=f"op_{str(op).replace(' ', '_')}_editor", 
                hide_index=True,
                column_config={
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
                        options=["WAITING", "ARRIVED", "ON GOING", "CANCELLED"],
                        required=False
                    )
                }
            )
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