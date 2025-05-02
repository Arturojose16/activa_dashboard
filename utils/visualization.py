"""
ActivaGroup Visualization Utilities
Enhanced module for professional, sleek dashboard design
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Define ActivaGroup brand colors (improved sleek dark theme with vibrant accents)
COLORS = {
    'background': '#0F1117',          # Darker, more professional background
    'card_bg': '#1A1C24',             # Card background with slight blue tint
    'card_bg_hover': '#21232D',       # Lighter card background for hover
    'panel_bg': '#252836',            # Panel background
    'text': '#FFFFFF',                # White text
    'secondary_text': '#A2A5B9',      # Light blue-gray text
    'muted_text': '#6E7191',          # Muted text
    'border': '#2E303E',              # Border color
    
    # Brand colors (refined for better aesthetics)
    'primary': '#0A2463',             # Navy blue (primary brand color)
    'secondary': '#F36F21',           # Orange (secondary brand color)
    'accent1': '#E53935',             # Red accent
    'accent2': '#FFCC33',             # Gold accent
    'accent3': '#3ABFF8',             # Light blue accent
    'teal': '#36D399',                # Teal color
    'purple': '#6B21A8',              # Purple color
    
    # Status colors
    'success': '#36D399',             # Green (positive values)
    'danger': '#F87272',              # Red (negative values)
    'warning': '#FBBD23',             # Yellow (warning)
    'info': '#3ABFF8',                # Blue (info)
    
    # Chart colors
    'chart_bg': 'rgba(26, 28, 36, 0.8)'  # Semi-transparent panel background
}

# Improved chart colors as a list for sequential use (more harmonious palette)
CHART_COLORS = [
    COLORS['secondary'],        # Orange
    COLORS['accent3'],          # Light blue
    COLORS['teal'],             # Teal
    COLORS['purple'],           # Purple
    COLORS['accent2'],          # Gold
    COLORS['accent1'],          # Red
    '#6419E6',                  # Electric purple
    '#34D399',                  # Green
    '#F59E0B',                  # Amber
    '#3B82F6'                   # Blue
]

# Enhanced transparent version of chart colors with better opacity
CHART_COLORS_TRANSPARENT = [
    'rgba(243, 111, 33, 0.85)',   # Orange (secondary) with transparency
    'rgba(58, 191, 248, 0.85)',   # Light blue (accent3) with transparency
    'rgba(54, 211, 153, 0.85)',   # Teal with transparency
    'rgba(107, 33, 168, 0.85)',   # Purple with transparency
    'rgba(255, 204, 51, 0.85)',   # Gold (accent2) with transparency
    'rgba(229, 57, 53, 0.85)',    # Red (accent1) with transparency
    'rgba(100, 25, 230, 0.85)',   # Electric purple with transparency
    'rgba(52, 211, 153, 0.85)',   # Green with transparency
    'rgba(245, 158, 11, 0.85)',   # Amber with transparency
    'rgba(59, 130, 246, 0.85)'    # Blue with transparency
]

# Apply enhanced styling for sleek, modern dashboard
def apply_dark_theme():
    """Apply ActivaGroup sleek, professional dark theme to the Streamlit app"""
    st.markdown(f"""
        <style>
            /* Main theme colors and layout */
            .stApp {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
            
            .main .block-container {{
                padding-top: 1rem;
                padding-bottom: 1rem;
                max-width: 1200px;
            }}
            
            /* Hide hamburger menu and footer */
            #MainMenu, footer, header {{
                visibility: hidden;
            }}
            
            /* Typography - Enhanced readability */
            h1, h2, h3, h4, h5, h6 {{
                color: {COLORS['text']};
                font-weight: 600;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                letter-spacing: -0.02em;
            }}
            
            h1 {{
                font-size: 2.25rem;
                letter-spacing: -0.04em;
                margin-bottom: 0.5rem;
                line-height: 1.2;
                background: linear-gradient(90deg, #FFFFFF, #F5F6FA);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            h2 {{
                font-size: 1.75rem;
                letter-spacing: -0.03em;
                margin-top: 1.5rem;
                margin-bottom: 1rem;
                color: #FFFFFF;
                border-left: 4px solid {COLORS['secondary']};
                padding-left: 0.75rem;
            }}
            
            h3 {{
                font-size: 1.35rem;
                letter-spacing: -0.02em;
                margin-top: 1.2rem;
                margin-bottom: 0.8rem;
                color: #F5F6FA;
            }}
            
            p {{
                color: {COLORS['secondary_text']};
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
                font-size: 0.95rem;
            }}
            
            /* Improved Metric Cards with subtle animations */
            .metric-card {{
                background-color: {COLORS['card_bg']};
                background-image: linear-gradient(135deg, rgba(26, 28, 36, 0.9) 0%, rgba(33, 35, 45, 0.9) 100%);
                border-radius: 0.75rem;
                padding: 1.4rem;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                height: 100%;
                margin-bottom: 1rem;
                border: 1px solid {COLORS['border']};
                transition: all 0.3s ease-in-out;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                position: relative;
                overflow: hidden;
            }}
            
            .metric-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, {COLORS['secondary']}, {COLORS['accent3']});
                opacity: 0;
                transition: opacity 0.3s ease;
            }}
            
            .metric-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
                background-color: {COLORS['card_bg_hover']};
                border-color: rgba(58, 191, 248, 0.3);
            }}
            
            .metric-card:hover::before {{
                opacity: 1;
            }}
            
            .metric-icon {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 40px;
                width: 40px;
                border-radius: 12px;
                margin-bottom: 0.8rem;
                background-color: rgba(243, 111, 33, 0.15);
                color: {COLORS['secondary']};
                transition: all 0.3s ease;
            }}
            
            .metric-card:hover .metric-icon {{
                transform: scale(1.1);
                background-color: rgba(243, 111, 33, 0.25);
            }}
            
            .metric-value {{
                font-size: 2.5rem;
                font-weight: 700;
                color: {COLORS['text']};
                margin: 0.3rem 0;
                line-height: 1.1;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(90deg, #FFFFFF, #F5F6FA);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .metric-label {{
                font-size: 1rem;
                color: {COLORS['secondary_text']};
                font-weight: 500;
                margin-bottom: 0.5rem;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 0.85rem;
            }}
            
            .metric-subtitle {{
                font-size: 0.85rem;
                color: {COLORS['muted_text']};
                margin-top: 0.25rem;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            
            /* Improved Delta indicators with animations */
            .stat-delta-positive {{
                color: {COLORS['success']};
                font-weight: 500;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 4px;
                font-size: 0.9rem;
                margin-top: 4px;
                transition: all 0.3s ease;
            }}
            
            .stat-delta-negative {{
                color: {COLORS['danger']};
                font-weight: 500;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 4px;
                font-size: 0.9rem;
                margin-top: 4px;
                transition: all 0.3s ease;
            }}
            
            .metric-card:hover .stat-delta-positive,
            .metric-card:hover .stat-delta-negative {{
                transform: scale(1.05);
            }}
            
            /* Enhanced Chart Containers with subtle gradients */
            .chart-container {{
                background-color: {COLORS['card_bg']};
                background-image: linear-gradient(135deg, rgba(26, 28, 36, 0.95) 0%, rgba(33, 35, 45, 0.95) 100%);
                border-radius: 0.75rem;
                padding: 1.25rem;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                margin-bottom: 1.5rem;
                border: 1px solid {COLORS['border']};
                transition: all 0.3s ease-in-out;
                overflow: hidden;
                position: relative;
            }}
            
            .chart-container::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']});
                opacity: 0;
                transition: opacity 0.3s ease;
            }}
            
            .chart-container:hover {{
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
                border-color: rgba(58, 191, 248, 0.2);
                transform: translateY(-2px);
            }}
            
            .chart-container:hover::before {{
                opacity: 1;
            }}
            
            /* Enhanced Chart title styling */
            .chart-title {{
                font-size: 1.1rem;
                color: {COLORS['text']};
                font-weight: 600;
                margin-bottom: 1rem;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            
            .chart-title::before {{
                content: '';
                display: inline-block;
                width: 3px;
                height: 1rem;
                background-color: {COLORS['secondary']};
                margin-right: 0.5rem;
                border-radius: 2px;
            }}
            
            /* Improved Data tables */
            .dataframe, div[data-testid="stDataFrame"] table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                background-color: {COLORS['card_bg']};
                color: {COLORS['text']};
                border-radius: 0.5rem;
                overflow: hidden;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                border: 1px solid {COLORS['border']};
                margin-top: 0.5rem;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            }}
            
            .dataframe th, div[data-testid="stDataFrame"] th {{
                background-color: {COLORS['panel_bg']};
                color: {COLORS['text']};
                padding: 0.75rem 1rem;
                text-align: left;
                font-weight: 600;
                border-bottom: 1px solid {COLORS['border']};
                font-size: 0.85rem;
                white-space: nowrap;
                letter-spacing: 0.03em;
                text-transform: uppercase;
            }}
            
            .dataframe td, div[data-testid="stDataFrame"] td {{
                padding: 0.75rem 1rem;
                border-bottom: 1px solid rgba(46, 48, 62, 0.6);
                font-size: 0.85rem;
                transition: background-color 0.15s ease;
            }}
            
            .dataframe tr:hover, div[data-testid="stDataFrame"] tr:hover {{
                background-color: rgba(46, 48, 62, 0.3);
            }}
            
            /* Enhanced Streamlit elements - buttons, inputs, etc. */
            .stButton > button {{
                background-color: {COLORS['secondary']};
                background-image: linear-gradient(135deg, {COLORS['secondary']}, #FF7E3E);
                color: {COLORS['text']};
                border: none;
                font-weight: 500;
                border-radius: 0.5rem;
                padding: 0.6rem 1.2rem;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                transition: all 0.3s ease;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                letter-spacing: 0.02em;
            }}
            
            .stButton > button:hover {{
                background-color: #FF7E3E; /* Lighter orange */
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            }}
            
            /* Enhanced Download button */
            .stDownloadButton > button {{
                background-color: {COLORS['primary']};
                background-image: linear-gradient(135deg, {COLORS['primary']}, #0E2F7D);
                color: {COLORS['text']};
                border: none;
                font-weight: 500;
                border-radius: 0.5rem;
                padding: 0.6rem 1.2rem;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                transition: all 0.3s ease;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                letter-spacing: 0.02em;
            }}
            
            .stDownloadButton > button:hover {{
                background-color: #0E2F7D; /* Lighter blue */
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            }}
            
            /* Enhanced Input fields */
            .stTextInput > div > div > input {{
                background-color: {COLORS['panel_bg']};
                color: {COLORS['text']};
                border-radius: 0.5rem;
                border: 1px solid {COLORS['border']};
                padding: 0.7rem 1rem;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                transition: all 0.2s ease;
            }}
            
            .stTextInput > div > div > input:focus {{
                border-color: {COLORS['secondary']};
                box-shadow: 0 0 0 2px rgba(243, 111, 33, 0.2);
                transform: translateY(-1px);
            }}
            
            /* Enhanced Select boxes */
            .stSelectbox {{
                color: {COLORS['text']};
            }}
            
            .stSelectbox > div > div > div {{
                background-color: {COLORS['panel_bg']};
                border-radius: 0.5rem;
                border: 1px solid {COLORS['border']};
                transition: all 0.2s ease;
            }}
            
            .stSelectbox > div > div > div:focus-within {{
                border-color: {COLORS['secondary']};
                box-shadow: 0 0 0 2px rgba(243, 111, 33, 0.2);
                transform: translateY(-1px);
            }}
            
            /* Enhanced Tab styling */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px;
                background-color: {COLORS['panel_bg']};
                padding: 0.5rem;
                border-radius: 0.75rem;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                height: 40px;
                white-space: pre-wrap;
                background-color: transparent;
                border-radius: 0.5rem;
                gap: 1px;
                padding: 0.5rem 1rem;
                color: {COLORS['secondary_text']};
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                font-weight: 500;
                transition: all 0.2s ease;
            }}
            
            .stTabs [aria-selected="true"] {{
                background-color: rgba(243, 111, 33, 0.15);
                color: {COLORS['secondary']};
                transform: translateY(-1px);
            }}
            
            /* Enhanced Sidebar */
            section[data-testid="stSidebar"] {{
                background-color: {COLORS['panel_bg']};
                border-right: 1px solid {COLORS['border']};
            }}
            
            section[data-testid="stSidebar"] h1 {{
                font-size: 1.5rem;
                padding-left: 1rem;
                margin-bottom: 1rem;
            }}
            
            /* Improved Modern Navigation Menu */
            .nav-container {{
                display: flex;
                background-color: {COLORS['panel_bg']};
                border-radius: 0.75rem;
                margin-bottom: 1.5rem;
                padding: 0.3rem;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                overflow-x: auto;
                scrollbar-width: none;
                border: 1px solid {COLORS['border']};
                align-items: center;
                flex-wrap: nowrap;
                position: relative;
            }}
            
            .nav-container::-webkit-scrollbar {{
                display: none;
            }}
            
            .nav-link {{
                color: {COLORS['secondary_text']};
                text-decoration: none;
                padding: 0.75rem 1.2rem;
                margin: 0.2rem;
                border-radius: 0.5rem;
                font-weight: 500;
                transition: all 0.3s;
                white-space: nowrap;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 0.9rem;
                letter-spacing: 0.02em;
                border: 1px solid transparent;
            }}
            
            .nav-link:hover {{
                background-color: rgba(255, 255, 255, 0.05);
                color: {COLORS['text']};
                transform: translateY(-1px);
                border-color: rgba(255, 255, 255, 0.1);
            }}
            
            .nav-link-active {{
                color: {COLORS['secondary']};
                text-decoration: none;
                padding: 0.75rem 1.2rem;
                margin: 0.2rem;
                background-color: rgba(243, 111, 33, 0.15);
                border-radius: 0.5rem;
                font-weight: 500;
                white-space: nowrap;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 0.9rem;
                letter-spacing: 0.02em;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(243, 111, 33, 0.3);
            }}

            /* Improved Modern Dashboard Cards */
            .card-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 1rem;
                margin-top: 1rem;
                margin-bottom: 1.5rem;
            }}
            
            .nav-card {{
                flex: 1;
                min-width: 220px;
                background-color: {COLORS['card_bg']};
                background-image: linear-gradient(135deg, rgba(26, 28, 36, 0.95) 0%, rgba(33, 35, 45, 0.95) 100%);
                border-radius: 0.75rem;
                padding: 1.5rem;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
                border: 1px solid {COLORS['border']};
                text-align: center;
                cursor: pointer;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }}
            
            .nav-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, {COLORS['secondary']}, {COLORS['accent3']});
                opacity: 0;
                transition: opacity 0.3s ease;
            }}
            
            .nav-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
                background-color: {COLORS['card_bg_hover']};
                border-color: rgba(58, 191, 248, 0.25);
            }}
            
            .nav-card:hover::before {{
                opacity: 1;
            }}
            
            .nav-card h3 {{
                color: white;
                font-size: 1.2rem;
                margin-bottom: 0.6rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            
            .nav-card:hover h3 {{
                transform: scale(1.05);
                color: #FFFFFF;
            }}
            
            .nav-card p {{
                color: {COLORS['secondary_text']};
                font-size: 0.9rem;
                margin-bottom: 0;
                line-height: 1.5;
                transition: all 0.3s ease;
            }}
            
            .nav-card:hover p {{
                color: #A2A5B9;
            }}
            
            .nav-card svg {{
                width: 2.5rem;
                height: 2.5rem;
                margin-bottom: 1rem;
                fill: {COLORS['secondary']};
                transition: all 0.3s ease;
            }}
            
            .nav-card:hover svg {{
                transform: scale(1.1) rotate(5deg);
            }}
            
            /* Enhanced Info, warning, and error containers */
            .info-box, div.stAlert {{
                background-color: rgba(58, 191, 248, 0.1);
                border-left: 4px solid {COLORS['info']};
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
                position: relative;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }}
            
            .info-box:hover, div.stAlert:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}
            
            .warning-box, div.stWarning {{
                background-color: rgba(251, 189, 35, 0.1);
                border-left: 4px solid {COLORS['warning']};
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
                position: relative;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }}
            
            .warning-box:hover, div.stWarning:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}
            
            .error-box, div.stError {{
                background-color: rgba(248, 114, 114, 0.1);
                border-left: 4px solid {COLORS['danger']};
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
                position: relative;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }}
            
            .error-box:hover, div.stError:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}
            
            /* Enhanced Footer styling */
            .footer {{
                text-align: center;
                margin-top: 3rem;
                padding: 1rem;
                color: {COLORS['muted_text']};
                font-size: 0.8rem;
                border-top: 1px solid {COLORS['border']};
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background-image: linear-gradient(to right, transparent, {COLORS['border']}, transparent);
                background-size: 100% 1px;
                background-position: top;
                background-repeat: no-repeat;
            }}
            
            /* Make sure plotly charts look consistent */
            .js-plotly-plot, .plotly, .plot-container {{
                border-radius: 0.5rem;
                overflow: hidden;
            }}
            
            /* Improved Budget table */
            .budget-table {{
                width: 100%;
                border-collapse: collapse;
                border-radius: 0.5rem;
                overflow: hidden;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                border: 1px solid {COLORS['border']};
                background-image: linear-gradient(135deg, rgba(26, 28, 36, 0.95) 0%, rgba(33, 35, 45, 0.95) 100%);
            }}
            
            .budget-table th {{
                background-color: {COLORS['panel_bg']};
                color: white;
                padding: 1rem;
                text-align: left;
                font-weight: 500;
                font-size: 0.9rem;
                border-bottom: 1px solid {COLORS['border']};
                letter-spacing: 0.03em;
                text-transform: uppercase;
            }}
            
            .budget-table td {{
                padding: 0.9rem 1rem;
                border-bottom: 1px solid rgba(46, 48, 62, 0.6);
                font-size: 0.9rem;
                transition: all 0.2s ease;
            }}
            
            .budget-table tr:hover {{
                background-color: rgba(46, 48, 62, 0.3);
            }}
            
            .util-cell {{
                text-align: right;
                font-weight: 500;
            }}
            
            .util-high {{
                color: {COLORS['success']};
                position: relative;
            }}
            
            .util-high::after {{
                content: '';
                display: inline-block;
                width: 8px;
                height: 8px;
                background-color: {COLORS['success']};
                border-radius: 50%;
                margin-left: 8px;
                opacity: 0.7;
            }}
            
            .util-medium {{
                color: {COLORS['secondary']};
                position: relative;
            }}
            
            .util-medium::after {{
                content: '';
                display: inline-block;
                width: 8px;
                height: 8px;
                background-color: {COLORS['secondary']};
                border-radius: 50%;
                margin-left: 8px;
                opacity: 0.7;
            }}
            
            .util-low {{
                color: {COLORS['danger']};
                position: relative;
            }}
            
            .util-low::after {{
                content: '';
                display: inline-block;
                width: 8px;
                height: 8px;
                background-color: {COLORS['danger']};
                border-radius: 50%;
                margin-left: 8px;
                opacity: 0.7;
            }}
            
            /* Enhanced Dashboard Header Section */
            .dashboard-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
                padding-bottom: 0.75rem;
                border-bottom: 1px solid {COLORS['border']};
                background-image: linear-gradient(to right, transparent, {COLORS['border']}, transparent);
                background-size: 100% 1px;
                background-position: bottom;
                background-repeat: no-repeat;
            }}
            
            .dashboard-title {{
                display: flex;
                flex-direction: column;
            }}
            
            .dashboard-title h1 {{
                margin-bottom: 0.25rem;
            }}
            
            .dashboard-title p {{
                margin-top: 0.25rem;
                margin-bottom: 0;
                font-size: 0.95rem;
                max-width: 600px;
            }}
            
            .dashboard-actions {{
                display: flex;
                gap: 0.5rem;
            }}
            
            /* Enhanced Row divider */
            .row-divider {{
                height: 1px;
                background-color: {COLORS['border']};
                margin: 2rem 0;
                opacity: 0.6;
                background-image: linear-gradient(to right, transparent, {COLORS['border']}, transparent);
            }}
            
            /* Search box styling */
            .search-container {{
                background-color: {COLORS['panel_bg']};
                border-radius: 0.5rem;
                padding: 0.25rem 0.5rem;
                margin-bottom: 1rem;
                border: 1px solid {COLORS['border']};
                display: flex;
                align-items: center;
                transition: all 0.3s ease;
            }}
            
            .search-container:focus-within {{
                border-color: {COLORS['secondary']};
                box-shadow: 0 0 0 2px rgba(243, 111, 33, 0.2);
                transform: translateY(-1px);
            }}
            
            .search-icon {{
                color: {COLORS['secondary_text']};
                margin-right: 0.5rem;
                display: flex;
                align-items: center;
            }}
            
            .search-input {{
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: {COLORS['text']} !important;
                width: 100%;
            }}
            
            .search-input:focus {{
                outline: none !important;
                box-shadow: none !important;
            }}
        </style>
    """, unsafe_allow_html=True)

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

def create_kpi_card(title, value, subtitle=None, is_currency=False, delta=None, icon=None):
    """Create a modern KPI card with hover effects for dark theme"""
    if is_currency:
        formatted_value = f"${value:,.0f}" if isinstance(value, (int, float)) and not pd.isna(value) else "N/A"
    else:
        if isinstance(value, float) and not pd.isna(value):
            if title.lower().find('margen') >= 0 or title.lower().find('porcentaje') >= 0 or subtitle and subtitle.lower().find('porcentaje') >= 0:
                formatted_value = f"{value:.1f}%"
            else:
                formatted_value = f"{value:,.1f}"
        elif isinstance(value, (int)) and not pd.isna(value):
            formatted_value = f"{value:,}"
        else:
            formatted_value = "N/A"
    
    delta_html = ""
    if delta is not None:
        if delta > 0:
            delta_html = f'<div class="stat-delta-positive">↑ {abs(delta):.1f}%</div>'
        elif delta < 0:
            delta_html = f'<div class="stat-delta-negative">↓ {abs(delta):.1f}%</div>'
    
    subtitle_html = f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ''
    
    icon_html = ""
    if icon:
        icon_html = f'<div class="metric-icon">{icon}</div>'
    
    st.markdown(f"""
        <div class="metric-card">
            {icon_html}
            <div class="metric-label">{title}</div>
            <div class="metric-value">{formatted_value}</div>
            {subtitle_html}
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def create_revenue_line_chart(data, x_col="month", y_col="revenue", title="Ingresos Mensuales"):
    """Create a sleek line chart for revenue data with dark theme"""
    if data.empty:
        return go.Figure()
        
    # Create the figure
    fig = go.Figure()
    
    # Add line trace
    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[y_col],
        mode='lines+markers',
        name='Ingresos',
        line=dict(color=COLORS['secondary'], width=3, shape='spline'),
        marker=dict(size=8, color=COLORS['secondary'], line=dict(width=1, color='white')),
        fill='tozeroy',
        fillcolor=f'rgba(243, 111, 33, 0.1)'
    ))
    
    # Update layout
    fig.update_layout(
        title=None,  # We'll use HTML title instead
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(
            showgrid=False,
            title="",
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
            color=COLORS['secondary_text'],
            tickangle=0
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title="",
            tickprefix="$",
            tickformat=",",
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
            color=COLORS['secondary_text']
        ),
        font=dict(
            family="Inter, sans-serif", 
            size=12,
            color=COLORS['text']
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=COLORS['panel_bg'],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    # Add chart title using HTML
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    
    return fig

# New enhanced funnel chart for client concentration
def create_client_concentration_chart(data, title="Concentración de Ingresos por Clientes"):
    """Create a sleek funnel chart for client concentration analysis"""
    if data.empty:
        return go.Figure()
    
    # Create figure
    fig = go.Figure()
    
    # Add funnel bars
    fig.add_trace(go.Funnel(
        y=data["category"],
        x=data["revenue"],
        textposition="inside",
        textinfo="value+percent initial",
        opacity=0.8,
        marker={
            "color": [COLORS["secondary"], COLORS["info"], COLORS["teal"], COLORS["primary"]],
            "line": {"width": [0, 0, 0, 0], "color": ["white", "white", "white", "white"]}
        },
        textfont={"family": "Inter, sans-serif", "size": 12, "color": "white"},
        connector={"line": {"color": "rgba(255, 255, 255, 0.2)", "width": 1}}
    ))
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family="Inter, sans-serif", size=12, color=COLORS['text']),
        showlegend=False,
        hoverlabel=dict(
            bgcolor=COLORS['panel_bg'],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    # Add a title using HTML
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    
    return fig

# New enhanced search box to replace standard text_input
def create_search_box(label="Buscar", key=None):
    """Create a styled search box"""
    st.markdown(f'''
    <div class="search-container">
        <div class="search-icon">
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # The actual input will still be created by Streamlit
    return st.text_input(label, key=key, label_visibility="collapsed")

# Enhanced brand analysis chart
def create_brand_analysis_chart(data, title="Análisis de Marcas por Cliente"):
    """Create an enhanced bar chart for brand analysis"""
    if data.empty:
        return go.Figure()
    
    # Create figure
    fig = px.bar(
        data,
        x="cliente",
        y="brand_count",
        color="brand_count",
        color_continuous_scale=[[0, COLORS['info']], [0.5, COLORS['accent2']], [1, COLORS['secondary']]],
        labels={"brand_count": "Número de Marcas", "cliente": "Cliente"}
    )
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=60),
        xaxis=dict(
            showgrid=False,
            tickangle=45,
            title="",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title="",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        coloraxis_showscale=False,
        hoverlabel=dict(
            bgcolor=COLORS['panel_bg'],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    # Add value labels to the bars
    fig.update_traces(
        texttemplate='%{y}',
        textposition='outside',
        textfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
        marker=dict(line=dict(width=0))
    )
    
    # Add a title using HTML
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    
    return fig

# Enhanced margin trend chart
def create_margin_trend_chart(data, title="Tendencia de Margen Bruto Mensual"):
    """Create an enhanced line chart for margin trends"""
    if data.empty:
        return go.Figure()
    
    # Create figure
    fig = go.Figure()
    
    # Add line trace
    fig.add_trace(go.Scatter(
        x=data["month"],
        y=data["margin"],
        mode='lines+markers',
        line=dict(
            color=COLORS['primary'],
            width=3,
            shape='spline'
        ),
        marker=dict(
            size=8,
            color=COLORS['primary'],
            symbol='circle',
            line=dict(
                color='white',
                width=1
            )
        ),
        fill='tozeroy',
        fillcolor=f'rgba(10, 36, 99, 0.1)'
    ))
    
    # Add a reference line at 0%
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=1,
        y1=0,
        xref="paper",
        yref="y",
        line=dict(
            color="rgba(255, 255, 255, 0.3)",
            width=1,
            dash="dot"
        )
    )
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=40),
        xaxis=dict(
            showgrid=False,
            title="",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title="",
            ticksuffix="%",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
            zeroline=False
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=COLORS['panel_bg'],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    # Add chart title using HTML
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    
    return fig
    
    return fig

def create_industry_pie_chart(data, value_col="revenue", name_col="industry", title="Distribución de Ingresos por Industria"):
    """Create a modern pie chart for industry data with dark theme"""
    if data.empty:
        return go.Figure()
    
    # Sort data by value for better visual presentation
    data = data.sort_values(by=value_col, ascending=False)
    
    # Create the figure
    fig = px.pie(
        data,
        values=value_col,
        names=name_col,
        color_discrete_sequence=CHART_COLORS,  # Use solid colors instead of transparent ones
        hole=0.65
    )
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(
            font=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            itemclick=False,
            itemdoubleclick=False,
            traceorder="normal"
        ),
        hoverlabel=dict(
            bgcolor=COLORS['panel_bg'],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    # Update trace styling
    fig.update_traces(
        textposition='inside',
        textinfo='percent',
        textfont=dict(family="Inter, sans-serif", size=12, color=COLORS['text']),
        marker=dict(
            line=dict(color=COLORS['card_bg'], width=1),
            opacity=0.9
        ),
        hovertemplate='<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}'
    )
    
    # Add a title using HTML
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    
    return fig

def create_top_clients_bar_chart(data, x_col="cliente", y_cols=None, title="Top Clientes por Ingresos"):
    """Create a sleek bar chart for top clients with dark theme"""
    if data.empty:
        return go.Figure()
    
    # Determine y columns to use
    if y_cols is None or not isinstance(y_cols, list):
        # Default to single column mode
        if "revenue" in data.columns:
            y_cols = ["revenue"]
        elif "facturacion_x" in data.columns:
            y_cols = ["facturacion_x"]
        else:
            # Try to find a revenue column
            revenue_cols = [col for col in data.columns if 'facturacion' in col.lower() or 'revenue' in col.lower()]
            if revenue_cols:
                y_cols = [revenue_cols[0]]
            else:
                return go.Figure()
    
    # Create figure
    fig = go.Figure()
    
    # If we have multiple y columns, create a grouped bar chart
    if len(y_cols) > 1:
        # Add traces for each y column
        for i, y_col in enumerate(y_cols):
            fig.add_trace(go.Bar(
                x=data[x_col],
                y=data[y_col],
                name=y_col.replace('_', ' ').title(),
                marker_color=CHART_COLORS[i % len(CHART_COLORS)],
                marker_line=dict(width=0),
                hovertemplate='<b>%{x}</b><br>%{y:$,.0f}'
            ))
        
        # Set barmode to group
        fig.update_layout(barmode='group')
    else:
        # Single column mode with gradient color based on value
        fig.add_trace(go.Bar(
            x=data[x_col],
            y=data[y_cols[0]],
            marker=dict(
                color=data[y_cols[0]],
                colorscale=[[0, COLORS['info']], [1, COLORS['secondary']]],
                line=dict(width=0)
            ),
            name=y_cols[0].replace('_', ' ').title(),
            hovertemplate='<b>%{x}</b><br>%{y:$,.0f}'
        ))
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=60),
        xaxis=dict(
            showgrid=False,
            tickangle=45,
            title="",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title="",
            tickprefix="$",
            tickformat=",",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color=COLORS['secondary_text'], family="Inter, sans-serif"),
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        ),
        hoverlabel=dict(
            bgcolor=COLORS['panel_bg'],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    # Add chart title using HTML
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    
    return fig

def create_gauge_chart(value, title="Utilización de Presupuesto", min_val=0, max_val=120, threshold=100):
    """Create a sleek gauge chart for KPI visualization with dark theme"""
    # Determine color based on value
    if value >= threshold:
        color = COLORS['success']
    elif value >= threshold * 0.7:
        color = COLORS['secondary']
    else:
        color = COLORS['danger']
    
    # Create figure
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        gauge={
            "axis": {
                "range": [min_val, max_val],
                "tickwidth": 1,
                "tickcolor": COLORS['secondary_text'],
                "tickfont": {"size": 10, "color": COLORS['secondary_text']}
            },
            "bar": {"color": color},
            "bgcolor": 'rgba(255,255,255,0.05)',
            "borderwidth": 0,
            "bordercolor": 'rgba(255,255,255,0.1)',
            "steps": [
                {"range": [min_val, max_val * 0.7], "color": 'rgba(255,255,255,0.03)'},
                {"range": [max_val * 0.7, max_val], "color": 'rgba(255,255,255,0.05)'}
            ],
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75,
                "value": threshold
            }
        },
        number={"suffix": "%", "font": {"size": 24, "color": COLORS['text'], "family": "Inter, sans-serif"}}
    ))
    
    # Update layout
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Add a title using HTML
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    
    return fig

def create_waterfall_chart(data, title="Análisis de Estado de Resultados"):
    """Create a modern waterfall chart for financial data with dark theme"""
    if data.empty:
        return go.Figure()
    
    # Prepare data for waterfall chart
    measure = []
    y = []
    text = []
    names = []
    
    # First and last rows are totals, others are relative
    for i, (_, row) in enumerate(data.iterrows()):
        # Determine if this is a total row
        is_total = i == 0 or i == len(data) - 1
        measure.append("total" if is_total else "relative")
        
        # Get name/label from data
        if "name" in data.columns:
            name = row["name"]
        elif "concepto" in data.columns:
            name = row["concepto"]
        else:
            name = f"Item {i+1}"
        names.append(name)
        
        # Get value, handling potential NaN/None
        if "value" in data.columns and pd.notna(row["value"]):
            value = row["value"]
        elif "amount" in data.columns and pd.notna(row["amount"]):
            value = row["amount"]
        else:
            # Try to find a numeric column with non-NaN value
            numeric_cols = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])]
            value = None
            for col in numeric_cols:
                if pd.notna(row[col]):
                    value = row[col]
                    break
            
            # If no valid value found, use 0
            if value is None:
                value = 0
        
        y.append(value)
        text.append(f"${value:,.0f}")
    
    # Create the figure
    fig = go.Figure(go.Waterfall(
        name="Waterfall",
        orientation="v",
        measure=measure,
        x=names,
        textposition="outside",
        text=text,
        y=y,
        connector={"line": {"color": "rgba(255, 255, 255, 0.2)", "width": 1}},
        decreasing={"marker": {"color": COLORS['danger'], "line": {"width": 0}}},
        increasing={"marker": {"color": COLORS['success'], "line": {"width": 0}}},
        totals={"marker": {"color": COLORS['secondary'], "line": {"width": 0}}}
    ))
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=60),
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            title="",
            color=COLORS['secondary_text'],
            tickangle=45,
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title="",
            tickprefix="$",
            tickformat=",",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        hoverlabel=dict(
            bgcolor=COLORS['panel_bg'],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    # Add a title using HTML
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    
    return fig

def create_budget_vs_actual_chart(data, client_col="cliente", budget_col="budget", actual_col="actual", title="Presupuesto vs Ejecución"):
    """Create a sleek comparative bar chart for budget vs actual"""
    if data.empty:
        return go.Figure()
    
    # Limit to top 10 clients for readability
    if len(data) > 10:
        data = data.head(10)
    
    # Create figure
    fig = go.Figure()
    
    # Add budget bars
    fig.add_trace(go.Bar(
        x=data[client_col],
        y=data[budget_col],
        name="Presupuesto",
        marker_color=COLORS['primary'],
        marker_line=dict(width=0),
        hovertemplate='<b>%{x}</b><br>Presupuesto: $%{y:,.0f}'
    ))
    
    # Add actual bars
    fig.add_trace(go.Bar(
        x=data[client_col],
        y=data[actual_col],
        name="Ejecución",
        marker_color=COLORS['secondary'],
        marker_line=dict(width=0),
        hovertemplate='<b>%{x}</b><br>Ejecución: $%{y:,.0f}'
    ))
    
    # Update layout
    fig.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=60),
        xaxis=dict(
            showgrid=False,
            tickangle=45,
            title="",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title="",
            tickprefix="$",
            tickformat=",",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color=COLORS['secondary_text'], family="Inter, sans-serif"),
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        ),
        hoverlabel=dict(
            bgcolor=COLORS['panel_bg'],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    # Add a title using HTML
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    
    return fig

def create_stacked_bar_chart(data, x_col, y_cols, colors=None, title="Datos Apilados"):
    """Create a sleek stacked bar chart with dark theme"""
    if data.empty or not y_cols:
        return go.Figure()
    
    # Set colors
    if colors is None:
        colors = CHART_COLORS[:len(y_cols)]
    
    # Create figure
    fig = go.Figure()
    
    # Add each y column as a separate trace
    for i, y_col in enumerate(y_cols):
        fig.add_trace(go.Bar(
            x=data[x_col],
            y=data[y_col],
            name=y_col.replace('_', ' ').title(),
            marker_color=colors[i % len(colors)],
            marker_line=dict(width=0),
            hovertemplate='<b>%{x}</b><br>%{y:$,.0f}'
        ))
    
    # Update layout
    fig.update_layout(
        barmode='stack',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=60),
        xaxis=dict(
            showgrid=False,
            title="",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title="",
            tickprefix="$",
            tickformat=",",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color=COLORS['secondary_text'], family="Inter, sans-serif"),
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        ),
        hoverlabel=dict(
            bgcolor=COLORS['panel_bg'],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    # Add a title using HTML
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    
    return fig

def format_dataframe_for_display(df, currency_cols=None, percentage_cols=None):
    """Format a DataFrame for display in Streamlit"""
    formatted_df = df.copy()
    
    # Format currency columns
    if currency_cols:
        for col in currency_cols:
            if col in formatted_df.columns:
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: format_currency(x) if pd.notna(x) else "N/A"
                )
    
    # Format percentage columns
    if percentage_cols:
        for col in percentage_cols:
            if col in formatted_df.columns:
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: format_percentage(x) if pd.notna(x) else "N/A"
                )
    
    return formatted_df

def create_dashboard_header(title, subtitle=None):
    """Create a styled dashboard header with title and subtitle"""
    subtitle_html = f'<p style="margin-top: 0.25rem; margin-bottom: 0;">{subtitle}</p>' if subtitle else ''
    
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="dashboard-title">
            <h1 style="margin-bottom: 0.25rem;">{title}</h1>
            {subtitle_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_modern_navigation():
    """Create a modern navigation bar for consistency across pages"""
    st.markdown("""
    <div class="nav-container">
        <a href="/" class="nav-link-active">Dashboard</a>
        <a href="/Client_Overview" class="nav-link">Visión de Clientes</a>
        <a href="/Revenue_Analysis" class="nav-link">Análisis de Ingresos</a>
        <a href="/Budget_Management" class="nav-link">Gestión de Presupuesto</a>
        <a href="/Financial_Performance" class="nav-link">Rendimiento Financiero</a>
    </div>
    """, unsafe_allow_html=True)

# New enhanced chart for revenue and cost comparison
def create_revenue_cost_chart(data, title="Ingresos vs Costos Mensuales"):
    """Create a dual line chart for revenue and cost comparison with dark theme"""
    if data.empty:
        return go.Figure()
    
    # Create figure
    fig = go.Figure()
    
    # Add revenue line
    if "revenue" in data.columns:
        fig.add_trace(go.Scatter(
            x=data["month"],
            y=data["revenue"],
            name="Ingresos",
            mode='lines+markers',
            line=dict(color=COLORS['secondary'], width=3, shape='spline'),
            marker=dict(size=8, color=COLORS['secondary'], line=dict(width=1, color='white')),
            fill='tozeroy',
            fillcolor=f'rgba(243, 111, 33, 0.1)'
        ))
    
    # Add cost line
    if "costs" in data.columns:
        fig.add_trace(go.Scatter(
            x=data["month"],
            y=data["costs"],
            name="Costos",
            mode='lines+markers',
            line=dict(color=COLORS['danger'], width=3, shape='spline'),
            marker=dict(size=8, color=COLORS['danger'], line=dict(width=1, color='white'))
        ))
    
    # Add profit area (if both revenue and costs exist)
    if "revenue" in data.columns and "costs" in data.columns:
        profit_data = data.copy()
        profit_data["profit"] = profit_data["revenue"] - profit_data["costs"]
        
        fig.add_trace(go.Scatter(
            x=profit_data["month"],
            y=profit_data["profit"],
            name="Ganancia Bruta",
            mode='lines',
            line=dict(color=COLORS['success'], width=2, dash='dot'),
            marker=dict(size=6, color=COLORS['success'])
        ))
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=40),
        xaxis=dict(
            showgrid=False,
            title="",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title="",
            tickprefix="$",
            tickformat=",",
            color=COLORS['secondary_text'],
            tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=COLORS['panel_bg'],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor='rgba(255,255,255,0.1)'
        )
    )
    
    # Add chart title using HTML
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    