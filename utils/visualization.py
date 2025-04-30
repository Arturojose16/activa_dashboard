"""
ActivaGroup Visualization Utilities
Helper functions for creating charts and visualizations
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Define ActivaGroup brand colors (dark theme with vibrant accents)
COLORS = {
    'background': '#121212',       # Dark background
    'card_bg': '#1E1E1E',          # Slightly lighter card background
    'text': '#FFFFFF',             # White text
    'secondary_text': '#CCCCCC',   # Light gray text
    
    # Brand colors
    'primary': '#0A2463',          # Navy blue 
    'secondary': '#F36F21',        # Orange (primary accent)
    'accent1': '#E53935',          # Red accent
    'accent2': '#FFD54F',          # Beige/gold accent
    'accent3': '#64B5F6',          # Light blue accent
    
    # Status colors
    'success': '#4CAF50',          # Green (positive values)
    'danger': '#F44336',           # Red (negative values)
    'warning': '#FFC107',          # Yellow (warning)
    'info': '#2196F3',             # Blue (info)
    
    # Chart colors
    'chart_bg': 'rgba(26, 26, 26, 0.8)'  # Semi-transparent dark background for charts
}

# Chart colors as a list for sequential use (vibrant colors that pop against dark background)
CHART_COLORS = [
    COLORS['secondary'],        # Orange
    COLORS['accent3'],          # Light blue
    COLORS['accent2'],          # Beige/gold
    COLORS['accent1'],          # Red
    '#9C27B0',                  # Purple
    '#26A69A',                  # Teal
    '#7CB342',                  # Light green
    '#8D6E63',                  # Brown
    '#78909C'                   # Blue gray
]

# Transparent version of chart colors for use in charts
CHART_COLORS_TRANSPARENT = [
    'rgba(243, 111, 33, 0.8)',   # Orange (secondary) with transparency
    'rgba(100, 181, 246, 0.8)',  # Light blue (accent3) with transparency
    'rgba(255, 213, 79, 0.8)',   # Beige/gold (accent2) with transparency
    'rgba(229, 57, 53, 0.8)',    # Red (accent1) with transparency
    'rgba(156, 39, 176, 0.8)',   # Purple with transparency
    'rgba(38, 166, 154, 0.8)',   # Teal with transparency
    'rgba(124, 179, 66, 0.8)',   # Light green with transparency
    'rgba(141, 110, 99, 0.8)',   # Brown with transparency
    'rgba(120, 144, 156, 0.8)'   # Blue gray with transparency
]

# Apply custom styling for dark theme
def apply_dark_theme():
    """Apply ActivaGroup dark theme styling to the Streamlit app"""
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
            }}
            
            /* Typography */
            h1, h2, h3, h4, h5, h6 {{
                color: {COLORS['text']};
                font-weight: 600;
            }}
            
            p {{
                color: {COLORS['secondary_text']};
            }}
            
            /* Metric Cards */
            .metric-card {{
                background-color: {COLORS['card_bg']};
                border-radius: 10px;
                padding: 1.5rem;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                height: 100%;
                margin-bottom: 1rem;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            }}
            
            .metric-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
            }}
            
            .metric-value {{
                font-size: 2.5rem;
                font-weight: 700;
                color: {COLORS['text']};
                margin: 0.5rem 0;
            }}
            
            .metric-label {{
                font-size: 1rem;
                color: {COLORS['secondary_text']};
                font-weight: 400;
                margin-bottom: 0.75rem;
            }}
            
            .metric-subtitle {{
                font-size: 0.875rem;
                color: {COLORS['secondary_text']};
                margin-top: 0.25rem;
            }}
            
            /* Delta indicators */
            .stat-delta-positive {{
                color: {COLORS['success']};
                font-weight: 500;
            }}
            
            .stat-delta-negative {{
                color: {COLORS['danger']};
                font-weight: 500;
            }}
            
            /* Chart Containers */
            .chart-container {{
                background-color: {COLORS['card_bg']};
                border-radius: 10px;
                padding: 1rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;
            }}
            
            /* Data tables */
            .dataframe {{
                width: 100%;
                border-collapse: collapse;
                background-color: {COLORS['card_bg']};
                color: {COLORS['text']};
                border-radius: 8px;
                overflow: hidden;
            }}
            
            .dataframe th {{
                background-color: {COLORS['primary']};
                color: {COLORS['text']};
                padding: 0.75rem;
                text-align: left;
                font-weight: 600;
            }}
            
            .dataframe td {{
                padding: 0.75rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .dataframe tr:hover {{
                background-color: rgba(255, 255, 255, 0.05);
            }}
            
            /* Button styling */
            .stButton > button {{
                background-color: {COLORS['secondary']};
                color: {COLORS['text']};
                border: none;
                font-weight: 500;
                border-radius: 5px;
                padding: 0.5rem 1rem;
            }}
            
            .stButton > button:hover {{
                background-color: {COLORS['primary']};
                color: {COLORS['text']};
            }}
            
            /* Input fields */
            .stTextInput > div > div > input {{
                background-color: rgba(255, 255, 255, 0.05);
                color: {COLORS['text']};
                border-radius: 5px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .stTextInput > div > div > input:focus {{
                border-color: {COLORS['secondary']};
                box-shadow: 0 0 0 2px rgba(243, 111, 33, 0.2);
            }}
            
            /* Tab styling */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 10px;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                height: 50px;
                white-space: pre-wrap;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 5px 5px 0px 0px;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
                color: {COLORS['secondary_text']};
            }}
            
            .stTabs [aria-selected="true"] {{
                background-color: {COLORS['secondary']};
                color: {COLORS['text']};
            }}
            
            /* Sidebar */
            .css-1d391kg {{
                background-color: {COLORS['card_bg']};
            }}
            
            /* Widgets */
            .stSelectbox label, .stSlider label {{
                color: {COLORS['text']};
            }}
            
            .stSelectbox > div[data-baseweb="select"] > div {{
                background-color: rgba(255, 255, 255, 0.05);
                border-color: rgba(255, 255, 255, 0.1);
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

def create_kpi_card(title, value, subtitle=None, is_currency=False, delta=None):
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
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{formatted_value}</div>
            {subtitle_html}
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def create_revenue_line_chart(data, x_col="month", y_col="revenue", title="Ingresos Mensuales"):
    """Create a line chart for revenue data with dark theme"""
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
        line=dict(color=COLORS['secondary'], width=3),
        marker=dict(size=9, color=COLORS['secondary']),
        fill='tozeroy',
        fillcolor=f'rgba(243, 111, 33, 0.1)'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(
            showgrid=False,
            title="",
            color=COLORS['secondary_text']
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="Ingresos ($)",
            tickprefix="$",
            tickformat=",",
            color=COLORS['secondary_text']
        ),
        font=dict(
            family="Arial", 
            size=12,
            color=COLORS['text']
        ),
        title_font=dict(
            size=16,
            color=COLORS['text']
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color=COLORS['text'])
        ),
        hovermode="x unified"
    )
    
    return fig

def create_industry_pie_chart(data, value_col="revenue", name_col="industry", title="Distribución de Ingresos por Industria"):
    """Create a pie chart for industry data with dark theme"""
    if data.empty:
        return go.Figure()
    
    # Create the figure
    fig = px.pie(
        data,
        values=value_col,
        names=name_col,
        title=title,
        color_discrete_sequence=CHART_COLORS_TRANSPARENT,
        hole=0.5
    )
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(
            family="Arial", 
            size=12,
            color=COLORS['text']
        ),
        title_font=dict(
            size=16,
            color=COLORS['text']
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color=COLORS['text'])
        )
    )
    
    # Update trace styling
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont=dict(color=COLORS['text'], size=12),
        hovertemplate='<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}'
    )
    
    return fig

def create_top_clients_bar_chart(data, x_col="cliente", y_cols=None, title="Top Clientes por Ingresos"):
    """Create a bar chart for top clients with dark theme"""
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
                marker_color=CHART_COLORS_TRANSPARENT[i % len(CHART_COLORS_TRANSPARENT)]
            ))
        
        # Set barmode to group
        fig.update_layout(barmode='group')
    else:
        # Single column mode
        fig.add_trace(go.Bar(
            x=data[x_col],
            y=data[y_cols[0]],
            marker_color=CHART_COLORS_TRANSPARENT[0],
            name=y_cols[0].replace('_', ' ').title()
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=100),
        xaxis=dict(
            showgrid=False,
            tickangle=45,
            title="",
            color=COLORS['secondary_text']
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="Monto ($)",
            tickprefix="$",
            tickformat=",",
            color=COLORS['secondary_text']
        ),
        font=dict(
            family="Arial", 
            size=12,
            color=COLORS['text']
        ),
        title_font=dict(
            size=16,
            color=COLORS['text']
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(color=COLORS['text'])
        ),
        hovermode="x unified"
    )
    
    return fig

def create_gauge_chart(value, title="Utilización de Presupuesto", min_val=0, max_val=100, threshold=100):
    """Create a gauge chart for KPI visualization with dark theme"""
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
        title={"text": title, "font": {"size": 16, "color": COLORS['text']}},
        gauge={
            "axis": {
                "range": [min_val, max_val],
                "tickwidth": 1,
                "tickcolor": COLORS['secondary_text']
            },
            "bar": {"color": color},
            "bgcolor": 'rgba(255,255,255,0.1)',
            "borderwidth": 2,
            "bordercolor": 'rgba(255,255,255,0.2)',
            "steps": [
                {"range": [min_val, max_val * 0.7], "color": 'rgba(255,255,255,0.05)'},
                {"range": [max_val * 0.7, max_val], "color": 'rgba(255,255,255,0.1)'}
            ],
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75,
                "value": threshold
            }
        },
        number={"suffix": "%", "font": {"size": 20, "color": COLORS['text']}}
    ))
    
    # Update layout
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=50, b=30),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={"color": COLORS['text'], "family": "Arial"}
    )
    
    return fig

def create_waterfall_chart(data, title="Análisis de Estado de Resultados"):
    """Create a waterfall chart for financial data with dark theme and null value handling"""
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
        textposition="auto",
        text=text,
        y=y,
        connector={"line": {"color": "rgb(255, 255, 255, 0.5)"}},
        decreasing={"marker": {"color": COLORS['danger']}},
        increasing={"marker": {"color": COLORS['success']}},
        totals={"marker": {"color": COLORS['secondary']}}
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=60),
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            title="",
            color=COLORS['secondary_text']
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="Monto ($)",
            tickprefix="$",
            tickformat=",",
            color=COLORS['secondary_text']
        ),
        font=dict(
            family="Arial", 
            size=12,
            color=COLORS['text']
        ),
        title_font=dict(
            size=16,
            color=COLORS['text']
        )
    )
    
    return fig

def create_budget_vs_actual_chart(data, client_col="cliente", budget_col="budget", actual_col="actual", title="Presupuesto vs Ejecución"):
    """Create a comparative bar chart for budget vs actual with dark theme"""
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
        marker_color=COLORS['primary']
    ))
    
    # Add actual bars
    fig.add_trace(go.Bar(
        x=data[client_col],
        y=data[actual_col],
        name="Ejecución",
        marker_color=COLORS['secondary']
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=100),
        xaxis=dict(
            showgrid=False,
            tickangle=45,
            title="",
            color=COLORS['secondary_text']
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="Monto ($)",
            tickprefix="$",
            tickformat=",",
            color=COLORS['secondary_text']
        ),
        font=dict(
            family="Arial", 
            size=12,
            color=COLORS['text']
        ),
        title_font=dict(
            size=16,
            color=COLORS['text']
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(color=COLORS['text'])
        ),
        hovermode="x unified"
    )
    
    return fig

def create_stacked_bar_chart(data, x_col, y_cols, colors=None, title="Datos Apilados"):
    """Create a stacked bar chart with dark theme"""
    if data.empty or not y_cols:
        return go.Figure()
    
    # Set colors
    if colors is None:
        colors = CHART_COLORS_TRANSPARENT[:len(y_cols)]
    
    # Create figure
    fig = go.Figure()
    
    # Add each y column as a separate trace
    for i, y_col in enumerate(y_cols):
        fig.add_trace(go.Bar(
            x=data[x_col],
            y=data[y_col],
            name=y_col.replace('_', ' ').title(),
            marker_color=colors[i % len(colors)]
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        barmode='stack',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=60),
        xaxis=dict(
            showgrid=False,
            title="",
            color=COLORS['secondary_text']
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="Monto ($)",
            tickprefix="$",
            tickformat=",",
            color=COLORS['secondary_text']
        ),
        font=dict(
            family="Arial", 
            size=12,
            color=COLORS['text']
        ),
        title_font=dict(
            size=16,
            color=COLORS['text']
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(color=COLORS['text'])
        ),
        hovermode="x unified"
    )
    
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
