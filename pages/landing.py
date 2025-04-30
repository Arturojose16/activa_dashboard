"""
ActivaGroup Business Intelligence Dashboard
Landing Page
"""
import streamlit as st
import base64
import os

# --- MUST be first ---
st.set_page_config(
    page_title="ActivaGroup Landing",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Session state for navigation ---
if "go_dashboard" not in st.session_state:
    st.session_state.go_dashboard = False

if "go_assistant" not in st.session_state:
    st.session_state.go_assistant = False

# Page navigation
if st.session_state.go_dashboard:
    st.session_state.go_dashboard = False
    st.switch_page("pages/dashboard.py")

if st.session_state.go_assistant:
    st.session_state.go_assistant = False
    st.switch_page("pages/AI_Assistant.py")

# --- Background Image ---
def set_background(image_file):
    """Set a background image for the landing page"""
    try:
        # Check if file exists
        if not os.path.exists(image_file):
            st.error(f"Background image not found at: {image_file}")
            return False
            
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            
            /* Hide default Streamlit elements */
            #MainMenu, footer, header {{
                visibility: hidden;
            }}
            
            /* Content styling */
            .centered-content {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding-top: 20vh;
            }}
            
            /* Title styling */
            .title {{
                font-size: 4.5rem;
                color: white !important;
                font-weight: 500;
                margin-bottom: 0.5rem;
            }}
            
            /* Subtitle styling */
            .subtitle {{
                font-size: 1.5rem;
                color: white;
                margin-bottom: 2rem;
            }}
            
            /* Button container styling */
            .button-row {{
                display: flex;
                justify-content: center;
                gap: 2rem;
                margin-top: 1rem;
            }}
            
            /* Button styling */
            .stButton > button {{
                background-color: #f36f21;
                color: white;
                font-weight: 500;
                border: none;
                padding: 0.8rem 2.5rem;
                border-radius: 8px;
                font-size: 1.1rem;
                transition: all 0.3s ease;
            }}
            
            .stButton > button:hover {{
                background-color: #cf5200;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }}
            
            /* Override Streamlit's default padding */
            .block-container {{
                padding-top: 0 !important;
                padding-bottom: 0 !important;
                max-width: 100% !important;
            }}
            
            /* Hide fullscreen button and other controls */
            .viewerBadge_link__1S137 {{
                display: none !important;
            }}
            
            [data-testid="stToolbar"] {{
                display: none !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        return True
    except Exception as e:
        st.error(f"Error loading background image: {str(e)}")
        return False

# Primary background path
background_path = "/Users/ajcamarena/Desktop/activa_dashboard/landing-activa.png"

# --- Main function ---
def main():
    """Main function for the landing page"""
    # Check if user is logged in (if necessary)
    if "logged_in" in st.session_state and not st.session_state.logged_in:
        st.switch_page("main.py")
        return
    
    # Set background image
    success = set_background(background_path)
    
    # If primary path fails, try alternative paths
    if not success:
        alternative_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets/landing-activa.png"),
            os.path.join(os.getcwd(), "assets/landing-activa.png"),
            "./landing-activa.png"
        ]
        
        for alt_path in alternative_paths:
            if set_background(alt_path):
                break
    
    # Create custom layout with HTML
    st.markdown(
        """
        <div class="centered-content">
            <h1 class="title">ActivaGroup</h1>
            <p class="subtitle">Bienvenido a tu plataforma de inteligencia de datos</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Add a small spacer
    st.write("")
    
    # Create buttons with columns for proper centering
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Create button row
        button_cols = st.columns([1, 1])
        
        with button_cols[0]:
            if st.button("Ver Dashboard", use_container_width=True):
                st.session_state.go_dashboard = True
                st.rerun()
        
        with button_cols[1]:
            if st.button("AI Assistant", use_container_width=True):
                st.session_state.go_assistant = True
                st.rerun()

if __name__ == "__main__":
    main()
    