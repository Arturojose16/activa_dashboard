"""
ActivaGroup Business Intelligence Dashboard
Login Page
"""
import streamlit as st
import base64
import os
from PIL import Image

#------------------------------------------------------------------------------
# CONSTANTS AND STYLING
#------------------------------------------------------------------------------

# ActivaGroup brand colors
COLORS = {
    'navy': '#0A2463',       # Primary color for headers, backgrounds
    'orange': '#FF7F11',     # Secondary color for highlights, buttons
    'white': '#FFFFFF',      # Text color on dark backgrounds
    'light_gray': '#F8F9FA', # Background for cards
    'dark_gray': '#6C757D',  # Subdued text
    
    # Extended palette for charts
    'navy_light': '#4D69A0',
    'orange_light': '#FFA755',
    'teal': '#38B2AC',
    'red': '#E53E3E',
    'green': '#48BB78',
    'purple': '#9F7AEA',
    'yellow': '#F6E05E'
}

# Chart colors as a list for sequential use
CHART_COLORS = [
    COLORS['navy'],
    COLORS['orange'],
    COLORS['teal'],
    COLORS['navy_light'],
    COLORS['orange_light'],
    COLORS['purple'],
    COLORS['green'],
    COLORS['red'],
    COLORS['yellow']
]

#------------------------------------------------------------------------------
# UTILITY FUNCTIONS
#------------------------------------------------------------------------------

def apply_custom_styling():
    """Apply ActivaGroup custom styling to the Streamlit app"""
    # Custom CSS
    st.markdown(f"""
        <style>
            /* Main theme colors */
            :root {{
                --navy: {COLORS['navy']};
                --orange: {COLORS['orange']};
                --white: {COLORS['white']};
                --light-gray: {COLORS['light_gray']};
                --dark-gray: {COLORS['dark_gray']};
            }}
            
            /* Header styling */
            .main .block-container {{
                padding-top: 1rem;
                padding-bottom: 1rem;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                color: var(--navy);
                font-weight: 600;
            }}
            
            /* Sidebar styling */
            .css-1v3fvcr, .css-163ttbj, .css-1helkxk {{
                background-color: #F0F2F6;
            }}
            
            /* KPI Card styling */
            .kpi-card {{
                background-color: var(--light-gray);
                border-radius: 10px;
                padding: 1.5rem;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
                transition: all 0.3s cubic-bezier(.25,.8,.25,1);
                height: 100%;
            }}
            
            .kpi-card:hover {{
                box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);
            }}
            
            .kpi-value {{
                font-size: 2.2rem;
                font-weight: 700;
                color: var(--navy);
                margin: 0.5rem 0;
            }}
            
            .kpi-label {{
                font-size: 1rem;
                color: var(--dark-gray);
                font-weight: 400;
            }}
            
            .kpi-change-positive {{
                color: {COLORS['green']};
                font-weight: 500;
            }}
            
            .kpi-change-negative {{
                color: {COLORS['red']};
                font-weight: 500;
            }}
            
            /* Chart container styling */
            .chart-container {{
                background-color: var(--white);
                border-radius: 10px;
                padding: 1rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
                margin-bottom: 1rem;
            }}
            
            /* Card title styling */
            .card-title {{
                color: var(--navy);
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }}
            
            /* Button styling */
            .stButton>button {{
                background-color: var(--navy);
                color: var(--white);
                border: none;
                font-weight: 500;
                border-radius: 5px;
            }}
            
            .stButton>button:hover {{
                background-color: var(--orange);
                color: var(--white);
            }}
            
            /* Tab styling */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 10px;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                height: 50px;
                white-space: pre-wrap;
                background-color: #F0F2F6;
                border-radius: 5px 5px 0px 0px;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
            }}
            
            .stTabs [aria-selected="true"] {{
                background-color: var(--navy);
                color: white;
            }}
            
            /* Custom Components */
            .stat-delta-positive {{
                color: #10b981;
                font-weight: 500;
            }}

            .stat-delta-negative {{
                color: #ef4444;
                font-weight: 500;
            }}
            
            /* Metric Card styling */
            .metric-card {{
                background-color: var(--card-background);
                border-radius: 8px;
                padding: 1.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                margin: 0.5rem 0;
                border: 1px solid rgba(0,0,0,0.05);
            }}
            
            .metric-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                border-color: var(--primary-color);
            }}

            .metric-value {{
                font-size: 2rem;
                font-weight: 600;
                color: var(--primary-color);
                margin: 0.5rem 0;
            }}

            .metric-label {{
                font-size: 0.875rem;
                color: #64748b;
                font-weight: 500;
            }}
        </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_api_data(endpoint):
    """
    Fetch data from API with caching
    
    Args:
        endpoint (str): API endpoint path
    
    Returns:
        dict: API response data or None if failed
    """
    import requests
    import json
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("Invalid JSON response from API")
        return None

def create_kpi_card(title, value, subtitle=None, is_currency=False, delta=None):
    """Create a modern KPI card with hover effects"""
    if is_currency:
        formatted_value = f"${value:,.0f}" if isinstance(value, (int, float)) else "N/A"
    else:
        formatted_value = f"{value:,.1f}" if isinstance(value, float) else f"{value:,}" if isinstance(value, (int, float)) else "N/A"
    
    delta_html = ""
    if delta is not None:
        if delta > 0:
            delta_html = f'<div class="stat-delta-positive">↑ {abs(delta):.1f}%</div>'
        elif delta < 0:
            delta_html = f'<div class="stat-delta-negative">↓ {abs(delta):.1f}%</div>'
    
    subtitle_html = f'<div class="metric-label">{subtitle}</div>' if subtitle else ''
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{formatted_value}</div>
            {subtitle_html}
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def build_dataframe_from_api(data_list):
    """Convert API list data to pandas DataFrame"""
    if not data_list:
        return pd.DataFrame()
    
    df = pd.DataFrame(data_list)
    
    # Convert any nested lists/dicts to string representation
    for col in df.columns:
        if df[col].dtype == 'object' and len(df) > 0:
            if isinstance(df[col].iloc[0], (list, dict)):
                df[col] = df[col].apply(lambda x: x if x is not None else [])
    
    # Handle numeric columns with 'facturacion' or 'presupuesto' in name
    for col in df.columns:
        if ('facturacion' in col.lower() or 'presupuesto' in col.lower() or 
            'revenue' in col.lower() or 'budget' in col.lower()):
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def format_currency(value):
    """Format a value as currency"""
    if pd.isna(value) or value is None:
        return "N/A"
    return f"${value:,.0f}"

def format_percentage(value, decimal_places=1):
    """Format a value as percentage"""
    if pd.isna(value) or value is None:
        return "N/A"
    
    format_str = f"{{:.{decimal_places}f}}%"
    return format_str.format(value)

# --- Fake Credentials ---
USERNAME = "activa"
PASSWORD = "admin123"

# --- Background Image Loader ---
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                background-attachment: fixed;
                background-color: #2e2e2e;
            }}
            
            /* Hide Streamlit elements */
            #MainMenu, footer, header {{
                visibility: hidden;
            }}
            
            /* Input field styling */
            .stTextInput > div > div > input {{
                background-color: rgba(60, 60, 60, 0.7);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 0.6rem 1rem;
                width: 100%;
            }}
            
            /* Button styling */
            .stButton > button {{
                background-color: #f36f21;
                color: white;
                font-weight: bold;
                width: 100%;
                padding: 0.6rem;
                border-radius: 4px;
                border: none;
            }}
            
            .stButton > button:hover {{
                background-color: #cf5200;
            }}
            
            /* Login header */
            .login-header {{
                color: white;
                text-align: center;
                margin-bottom: 20px;
                font-size: 20px;
                font-weight: 300;
            }}
            
            /* Center form fields */
            div[data-testid="column"] {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }}
            
            /* Hide standard streamlit label */
            .css-1outwu0 {{
                display: none;
            }}
            
            /* Form container - no background */
            .form-container {{
                max-width: 350px;
                width: 100%;
                margin: 0 auto;
                margin-top: 300px; /* Push form down */
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error loading background image: {e}")

# --- Main Function ---
def main():
    # Page configuration
    st.set_page_config(
        page_title="Login | ActivaGroup",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Apply background - Updated to use the specific path you provided
    background_path = "/Users/ajcamarena/Desktop/activa_dashboard/LANDING_MAIN.png"
    
    try:
        # First try with the specific path
        set_background(background_path)
    except Exception as e:
        # If that fails, try with the relative path as before
        try:
            set_background(os.path.join(os.getcwd(), "assets/LANDING_MAIN.png"))
        except:
            # If both fail, show a warning
            st.warning(f"Background image not found. Tried paths:\n1. {background_path}\n2. {os.path.join(os.getcwd(), 'assets/LANDING_MAIN.png')}")
    
    # --- Session State ---
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    # --- Page Switch Logic ---
    if st.session_state.logged_in:
        st.switch_page("pages/dashboard.py")
    
    # Create columns for centering the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        username = st.text_input("", placeholder="Usuario")
        password = st.text_input("", placeholder="Contraseña", type="password")
        
        if st.button("Entrar"):
            if username == USERNAME and password == PASSWORD:
                st.session_state.logged_in = True
                st.switch_page("pages/landing.py")
            else:
                st.error("Usuario o contraseña incorrectos.")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()