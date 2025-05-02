"""
ActivaGroup Business Intelligence Dashboard
Client Overview Page - Modern Sleek Design
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add parent directory to path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import custom utilities
from utils.data_connector import ActivaDataConnector
from utils.visualization import (
    COLORS, CHART_COLORS, CHART_COLORS_TRANSPARENT,
    create_kpi_card, apply_dark_theme,
    create_dashboard_header, create_brand_analysis_chart
)

# Page configuration
st.set_page_config(
    page_title="Visión de Clientes - ActivaGroup",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply dark theme
apply_dark_theme()

# Initialize data connector
@st.cache_resource
def get_connector():
    return ActivaDataConnector()

connector = get_connector()

# Check if user is logged in (if using login system)
if "logged_in" in st.session_state and not st.session_state.logged_in:
    st.warning("Por favor inicie sesión para acceder al dashboard")
    st.stop()

# Dashboard Header
create_dashboard_header(
    "Visión General de Clientes", 
    "Análisis detallado del portafolio de clientes de ActivaGroup"
)

# Modern Navigation Bar with active state
st.markdown("""
<div class="nav-container">
    <a href="/" class="nav-link">Dashboard</a>
    <a href="/Client_Overview" class="nav-link-active">Visión de Clientes</a>
    <a href="/Revenue_Analysis" class="nav-link">Análisis de Ingresos</a>
    <a href="/Budget_Management" class="nav-link">Gestión de Presupuesto</a>
    <a href="/Financial_Performance" class="nav-link">Rendimiento Financiero</a>
</div>
""", unsafe_allow_html=True)

# Sidebar filters
with st.sidebar:
    st.markdown('<h3 style="font-size: 1.3rem; margin-bottom: 1rem;">Filtros</h3>', unsafe_allow_html=True)

# Load Data
with st.spinner("Cargando datos..."):
    try:
        # Get client data
        client_data = connector.get_combined_metrics()
        
        # Convert to DataFrame
        if client_data:
            df = pd.DataFrame(client_data)
        else:
            st.error("No se pudo cargar la información de clientes")
            st.stop()
        
        # Get industry counts if "industria" column exists
        industry_counts = pd.DataFrame()
        if "industria" in df.columns:
            industry_counts = df.groupby("industria").size().reset_index(name="count")
            industry_counts = industry_counts.sort_values("count", ascending=False)
        
        # Create a simple brand_data DataFrame if "marcas" column exists
        brand_data = pd.DataFrame()
        if "marcas" in df.columns:
            # Extract brand data safely
            brand_rows = []
            for _, row in df.iterrows():
                cliente = row.get("cliente", "Unknown")
                industria = row.get("industria", "Unknown")
                marcas = row.get("marcas", [])
                
                # Handle different possible formats of marcas
                if isinstance(marcas, list):
                    for marca in marcas:
                        brand_rows.append({
                            "cliente": cliente,
                            "industria": industria,
                            "marca": marca
                        })
                elif isinstance(marcas, str):
                    # If it's a string, try to parse it as a list
                    try:
                        import ast
                        marca_list = ast.literal_eval(marcas)
                        if isinstance(marca_list, list):
                            for marca in marca_list:
                                brand_rows.append({
                                    "cliente": cliente,
                                    "industria": industria,
                                    "marca": marca
                                })
                    except:
                        # If parsing fails, just use it as a single brand
                        brand_rows.append({
                            "cliente": cliente,
                            "industria": industria,
                            "marca": marcas
                        })
            
            if brand_rows:
                brand_data = pd.DataFrame(brand_rows)
    
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        st.stop()

# Add industry filter if data is available
if "industria" in df.columns:
    with st.sidebar:
        all_industries = ["Todas las Industrias"] + sorted(df["industria"].unique().tolist())
        selected_industry = st.selectbox("Industria", all_industries)
        
        # Filter data based on selection
        if selected_industry != "Todas las Industrias":
            df = df[df["industria"] == selected_industry]
            # Also filter brand data if it exists
            if not brand_data.empty:
                brand_data = brand_data[brand_data["industria"] == selected_industry]

# Key Client Metrics
st.markdown('<h2>Métricas de Clientes</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    create_kpi_card(
        "Total Clientes", 
        len(df),
        icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>'
    )

with col2:
    # Count total brands across all clients
    if not brand_data.empty:
        total_brands = len(brand_data)
        create_kpi_card(
            "Total Marcas", 
            total_brands,
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>'
        )
    else:
        create_kpi_card(
            "Total Marcas", 
            "N/A",
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>'
        )

with col3:
    # Average revenue per client
    if "facturacion_x" in df.columns:
        avg_revenue = df["facturacion_x"].mean()
        create_kpi_card(
            "Ingreso Promedio", 
            avg_revenue,
            is_currency=True,
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>'
        )
    else:
        create_kpi_card(
            "Ingreso Promedio", 
            "N/A",
            is_currency=True,
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>'
        )

with col4:
    # Count industries
    if "industria" in df.columns:
        industry_count = df["industria"].nunique()
        create_kpi_card(
            "Total Industrias", 
            industry_count,
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>'
        )
    else:
        create_kpi_card(
            "Total Industrias", 
            "N/A",
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>'
        )

# Client Distribution by Industry
st.markdown('<h2>Distribución de Clientes por Industria</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Create a ribbon chart for industry distribution
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    if not industry_counts.empty:
        st.markdown('<div class="chart-title">Distribución de Clientes por Industria</div>', unsafe_allow_html=True)
        
        # Use top 7 industries for better visualization
        industry_sorted = industry_counts.sort_values("count", ascending=False).head(7)
        
        # Create a ribbon chart 
        fig = go.Figure()
        
        # Add area chart (ribbon)
        fig.add_trace(go.Scatter(
            x=industry_sorted["industria"],
            y=industry_sorted["count"],
            mode='lines',
            fill='tozeroy',
            line=dict(shape='spline', smoothing=1.3, width=0),
            fillcolor='rgba(58, 191, 248, 0.6)',
            hoverinfo='skip'
        ))
        
        # Add markers on top of ribbon
        fig.add_trace(go.Scatter(
            x=industry_sorted["industria"],
            y=industry_sorted["count"],
            mode='markers',
            marker=dict(
                size=12,
                color=COLORS['secondary'],
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>%{x}</b><br>%{y} clientes<extra></extra>'
        ))
        
        # Add value annotations
        for i, row in industry_sorted.iterrows():
            fig.add_annotation(
                x=row["industria"],
                y=row["count"],
                text=str(row["count"]),
                showarrow=False,
                yshift=15,
                font=dict(family="Inter, sans-serif", size=11, color=COLORS['text'])
            )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=40),
            xaxis=dict(
                showgrid=False,
                title="",
                color=COLORS['secondary_text'],
                tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
                tickangle=45
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.05)',
                title="",
                color=COLORS['secondary_text'],
                tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
            ),
            hoverlabel=dict(
                bgcolor=COLORS['panel_bg'],
                font_size=12,
                font_family="Inter, sans-serif",
                bordercolor='rgba(255,255,255,0.1)'
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de industrias disponibles")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Create bar chart for client distribution by industry
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    if not industry_counts.empty:
        st.markdown('<div class="chart-title">Top 10 Industrias por Número de Clientes</div>', unsafe_allow_html=True)
        
        # Sort data for better visualization
        industry_counts_sorted = industry_counts.sort_values("count", ascending=True).tail(10)
        
        fig = px.bar(
            industry_counts_sorted,
            x="count",
            y="industria",
            orientation='h',
            color="count",
            color_continuous_scale=[[0, COLORS['info']], [0.5, COLORS['accent3']], [1, COLORS['secondary']]]
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.05)',
                title="",
                color=COLORS['secondary_text'],
                tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
            ),
            yaxis=dict(
                showgrid=False,
                title="",
                categoryorder="total ascending",
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
            texttemplate='%{x}',
            textposition='outside',
            textfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
            marker=dict(line=dict(width=0))
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de industrias disponibles")
    st.markdown('</div>', unsafe_allow_html=True)

# Top Clients by Revenue
st.markdown('<h2>Clientes Principales por Ingresos</h2>', unsafe_allow_html=True)

# Create a bar chart of top clients by revenue
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
if "facturacion_x" in df.columns:
    st.markdown('<div class="chart-title">Top 10 Clientes por Ingresos</div>', unsafe_allow_html=True)
    
    # Make sure we have data to plot
    if len(df) > 0 and df["facturacion_x"].sum() > 0:
        top_clients = df.sort_values("facturacion_x", ascending=False).head(10)
        
        # Create an enhanced bar chart with gradient colors
        fig = px.bar(
            top_clients,
            x="cliente",
            y="facturacion_x",
            color="facturacion_x",
            color_continuous_scale=[[0, COLORS['info']], [0.5, COLORS['accent3']], [1, COLORS['secondary']]],
            labels={"facturacion_x": "Ingresos ($)", "cliente": "Cliente"}
        )
        
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
            texttemplate='$%{y:,.0f}',
            textposition='outside',
            textfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
            marker=dict(line=dict(width=0))
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos suficientes para mostrar clientes por ingresos")
else:
    st.info("No hay datos de ingresos disponibles")
st.markdown('</div>', unsafe_allow_html=True)

# Geographic Distribution Map - FIXED VERSION
st.markdown('<h2>Distribución Geográfica de Clientes</h2>', unsafe_allow_html=True)

# Create sample location data for our clients based on the provided information
def create_location_data():
    # Create a DataFrame with location information
    location_data = []
    
    # Add location data for the clients
    # This would normally come from your database, but we're creating it manually for this example
    clients = [
        # Most clients are in Santo Domingo
        {"cliente": "CND", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "DISTRIBUIDORA CORRIPIO", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "BANCO POPULAR", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "NESTLE", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "LABORATORIOS AMADITA", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "TEXACO", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "BANCO SANTA CRUZ", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        # MLB is in Mexico
        {"cliente": "MLB", "location": "México", "lat": 19.4326, "lon": -99.1332, "count": 1},
        # Grupo Punta Cana in Punta Cana
        {"cliente": "GRUPO PUNTA CANA", "location": "Punta Cana", "lat": 18.5601, "lon": -68.3725, "count": 1},
        # Asociacion Cibao in Santiago
        {"cliente": "ASOCIACION CIBAO DE AHORROS Y PRESTAMOS", "location": "Santiago", "lat": 19.4517, "lon": -70.6986, "count": 1},
        # Adding the rest of clients to Santo Domingo
        {"cliente": "HUMANO SEGUROS", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "INDUSTRIAS TUCAN", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "PEÑA IZQUIERDO", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "BANCO VIMENCA", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "REMESAS VIMENCA", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "DATA VIMENCA", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "RON BARCELO", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "EMBAJADA DE PAISES BAJOS", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "MERCASID", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "SUIPHAR", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "TD DOMINICANA", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "CESAR IGLESIAS", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "BANCO DE RESERVAS", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "INVERSIONES & RESERVAS", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "AFP RESERVAS", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "FUNDACION RESERVAS", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "SEGUROS BF", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "BANCO MULTIPLE CARIBE", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "MAVERICK FOODS (MUNNE)", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "PRODUCTOS CHEF", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "PORTAL", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "SENASA", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "RICA", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "CASA PACO (PACO FISH)", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "MOTOR CREDITO", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "CORTES / HNOS.", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "PRO DOMINICANA", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "FUNDACION RESERVAS", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "CONSULTORA LA COLECTIVA", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "OTRO LEVEL", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "PERSIO ABREU", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "GLOWTOUCH, SRL", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "PLAZA LAMA", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "INESPRE", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "VIDA INTEGRA", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
        {"cliente": "YO TAMBIEN PUEDO", "location": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "count": 1},
    ]
    
    # Create DataFrame
    location_df = pd.DataFrame(clients)
    
    # Group by location to get counts
    location_summary = location_df.groupby(['location', 'lat', 'lon']).size().reset_index(name='client_count')
    
    return location_df, location_summary

# Get location data
client_locations, location_summary = create_location_data()

# Create map visualization
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.markdown('<div class="chart-title">Distribución de Clientes por Ubicación</div>', unsafe_allow_html=True)

# Create a map using plotly
fig = go.Figure()

# Add the Dominican Republic map background with a dark style
fig.update_layout(
    mapbox=dict(
        style="carto-darkmatter",
        zoom=6.0,
        center=dict(lat=19.0, lon=-70.3),  # Centered on Dominican Republic
    )
)

# Add client location markers with improved styling
for _, location in location_summary.iterrows():
    # Adjust marker size based on count, but keep it reasonable
    marker_size = min(30, max(15, location['client_count'] * 10))
    
    # Color based on location
    if location['location'] == 'Santo Domingo':
        marker_color = COLORS['secondary']  # Orange
    elif location['location'] == 'Santiago':
        marker_color = COLORS['accent3']    # Blue
    elif location['location'] == 'Punta Cana':
        marker_color = COLORS['info']       # Light blue
    else:  # México
        marker_color = COLORS['warning']    # Yellow
    
    # Add marker with better visibility
    fig.add_trace(go.Scattermapbox(
        lat=[location['lat']],
        lon=[location['lon']],
        mode='markers+text',
        marker=dict(
            size=marker_size,
            color=marker_color,
            opacity=0.8,
            sizemode='diameter'
        ),
        text=f"{location['client_count']}",
        textfont=dict(
            family="Inter, sans-serif",
            size=10, 
            color="white"
        ),
        textposition="middle center",
        hoverinfo='text',
        hovertext=f"{location['location']}: {location['client_count']} cliente{'s' if location['client_count'] > 1 else ''}"
    ))

# Improve legend placement and styling
fig.add_annotation(
    x=0.01,
    y=0.99,
    xref="paper",
    yref="paper",
    text="Ubicaciones:",
    showarrow=False,
    font=dict(family="Inter, sans-serif", size=14, color="white"),
    align="left",
    bgcolor="rgba(30,30,30,0.7)",
    bordercolor="rgba(255,255,255,0.3)",
    borderwidth=1,
    borderpad=4,
    xanchor="left",
    yanchor="top"
)

# Add custom legend entries with better positioning
legend_entries = [
    {"text": "Santo Domingo (43 clientes)", "color": COLORS['secondary'], "y": 0.93},
    {"text": "Santiago (1 cliente)", "color": COLORS['accent3'], "y": 0.89},
    {"text": "Punta Cana (1 cliente)", "color": COLORS['info'], "y": 0.85},
    {"text": "México (1 cliente)", "color": COLORS['warning'], "y": 0.81}
]

for entry in legend_entries:
    fig.add_annotation(
        x=0.01,
        y=entry["y"],
        xref="paper",
        yref="paper",
        text=entry["text"],
        showarrow=False,
        font=dict(family="Inter, sans-serif", size=12, color="white"),
        align="left",
        bgcolor="rgba(30,30,30,0.7)",
        bordercolor=entry["color"],
        borderwidth=2,
        borderpad=4,
        xanchor="left"
    )

# Customize layout
fig.update_layout(
    height=500,
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    mapbox_accesstoken=None,  # No token needed for carto style
)

st.plotly_chart(fig, use_container_width=True)

# Add explanatory text below map
st.markdown("""
<div class="map-explanation" style="padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 5px; margin-top: 10px;">
    <p style="margin: 0;">La mayoría de los clientes (43) están ubicados en <b>Santo Domingo</b>, con presencia adicional en <b>Santiago</b> (Asociación Cibao de Ahorros y Préstamos), <b>Punta Cana</b> (Grupo Punta Cana) y <b>México</b> (MLB).</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Brand Analysis (only show if we have brand data)
if not brand_data.empty:
    st.markdown('<h2>Análisis de Marcas</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top clients by brand count
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        client_brand_counts = brand_data.groupby("cliente").size().reset_index(name="brand_count")
        top_brand_clients = client_brand_counts.sort_values("brand_count", ascending=False).head(10)
        
        # Create enhanced brand analysis chart
        fig = create_brand_analysis_chart(
            top_brand_clients,
            title="Top Clientes por Número de Marcas"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Brands by industry - use bar chart instead of pie
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        if "industria" in brand_data.columns:
            industry_brand_counts = brand_data.groupby("industria").size().reset_index(name="brand_count")
            industry_brand_counts = industry_brand_counts.sort_values("brand_count", ascending=False).head(7)
            
            st.markdown('<div class="chart-title">Distribución de Marcas por Industria</div>', unsafe_allow_html=True)
            
            # Create bar chart instead of pie chart
            fig = px.bar(
                industry_brand_counts,
                y="industria",
                x="brand_count",
                orientation='h',
                color="brand_count",
                color_continuous_scale=[[0, COLORS['info']], [0.5, COLORS['secondary']], [1, COLORS['accent3']]],
                text="brand_count"
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.05)',
                    title="",
                    color=COLORS['secondary_text'],
                    tickfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
                ),
                yaxis=dict(
                    showgrid=False,
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
            
            fig.update_traces(
                textposition='outside',
                marker=dict(line=dict(width=0)),
                hovertemplate='<b>%{y}</b><br>%{x} marcas'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de distribución de marcas por industria")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Add a third visualization: brand cloud or network graph
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Relaciones Cliente-Marca</div>', unsafe_allow_html=True)
    
    # Show brands by client in an interactive format
    # This could be a network graph, but since it's complex, let's use a simplified approach
    top_clients_with_brands = client_brand_counts.nlargest(5, "brand_count")
    
    # Get brands for these top clients
    top_client_brands = []
    for client in top_clients_with_brands["cliente"]:
        client_brands = brand_data[brand_data["cliente"] == client]["marca"].unique().tolist()
        top_client_brands.append({
            "cliente": client,
            "marcas": ", ".join(client_brands[:5]) + ("..." if len(client_brands) > 5 else "")
        })
    
    # Display as a table with rich formatting
    if top_client_brands:
        st.markdown("<div style='overflow-x: auto;'>", unsafe_allow_html=True)
        st.markdown("<table class='budget-table' style='width: 100%;'>", unsafe_allow_html=True)
        st.markdown("<tr><th>Cliente</th><th>Marcas Principales</th></tr>", unsafe_allow_html=True)
        
        for item in top_client_brands:
            st.markdown(f"<tr><td><b>{item['cliente']}</b></td><td>{item['marcas']}</td></tr>", unsafe_allow_html=True)
        
        st.markdown("</table>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No hay datos suficientes para mostrar relaciones cliente-marca")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Client Details Table
st.markdown('<h2>Detalles de Clientes</h2>', unsafe_allow_html=True)

# Prepare client data for display
if not df.empty:
    # Add search box for filtering the table
    search_box_container = st.container()
    with search_box_container:
        st.markdown('<div style="margin-bottom: 1rem;">', unsafe_allow_html=True)
        search_term = st.text_input("🔍 Buscar Cliente", "")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Select relevant columns
    display_cols = ["cliente", "industria"]
    
    # Add revenue column if available
    if "facturacion_x" in df.columns:
        display_cols.append("facturacion_x")
    
    # Add budget column if available
    if "presupuesto_x" in df.columns:
        display_cols.append("presupuesto_x")
    
    # Add brand count if available
    if not brand_data.empty:
        # Count brands per client
        brand_counts = brand_data.groupby("cliente").size().reset_index(name="marcas_count")
        # Merge with df
        df = pd.merge(df, brand_counts, on="cliente", how="left")
        df["marcas_count"] = df["marcas_count"].fillna(0).astype(int)
        display_cols.append("marcas_count")
    
    # Create display DataFrame with only the columns we have
    available_cols = [col for col in display_cols if col in df.columns]
    display_df = df[available_cols].copy()
    
    # Rename columns for display
    rename_dict = {
        "cliente": "Cliente",
        "industria": "Industria",
        "facturacion_x": "Ingresos",
        "presupuesto_x": "Presupuesto",
        "marcas_count": "# Marcas"
    }
    
    # Only rename columns that exist
    rename_cols = {k: v for k, v in rename_dict.items() if k in display_df.columns}
    display_df = display_df.rename(columns=rename_cols)
    
    # Format currency columns
    currency_cols = ["Ingresos", "Presupuesto"]
    for col in currency_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
            )
    
    # Sort by revenue if available
    if "Ingresos" in display_df.columns:
        # Create a numeric version for sorting
        display_df["Ingresos_num"] = df["facturacion_x"]
        display_df = display_df.sort_values("Ingresos_num", ascending=False)
        display_df = display_df.drop(columns=["Ingresos_num"])
    
    # Filter by search term
    if search_term:
        display_df = display_df[display_df["Cliente"].str.contains(search_term, case=False, na=False)]
    
    # Display the table
    st.markdown('<div class="chart-container" style="padding: 0;">', unsafe_allow_html=True)
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export options
    col1, col2 = st.columns([3, 1])
    with col2:
        st.download_button(
            label="Exportar a CSV",
            data=display_df.to_csv(index=False).encode('utf-8'),
            file_name="activagroup_clientes.csv",
            mime="text/csv",
            help="Descargar la tabla de clientes en formato CSV"
        )
else:
    st.info("No hay datos de clientes disponibles")

# Footer with modern styling
st.markdown("""
<div class="footer">
    <p>ActivaGroup Business Intelligence Dashboard © 2025</p>
</div>
""", unsafe_allow_html=True)
