"""
ActivaGroup Business Intelligence Dashboard
Client Overview Page
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
    create_kpi_card, create_industry_pie_chart, apply_dark_theme
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

# Page header with smaller bottom margin
st.markdown("""
    <h1 style='margin-bottom:0.5rem;'>Visión General de Clientes</h1>
    <p style='margin-bottom:2rem;'>Análisis detallado del portafolio de clientes de ActivaGroup</p>
""", unsafe_allow_html=True)

# Add simple navigation tabs
st.markdown("""
    <div style="display: flex; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
        <a href="/dashboard" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;">Dashboard</a>
        <a href="/Client_Overview" target="_self" style="color: white; text-decoration: none; padding: 8px 16px; margin-right: 8px; background: rgba(243, 111, 33, 0.2); border-bottom: 2px solid #F36F21; border-radius: 4px 4px 0 0;">Visión de Clientes</a>
        <a href="/Revenue_Analysis" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;">Análisis de Ingresos</a>
        <a href="/Budget_Management" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;">Gestión de Presupuesto</a>
        <a href="/Financial_Performance" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px;">Rendimiento Financiero</a>
    </div>
""", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.title("Filtros")

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
    all_industries = ["Todas las Industrias"] + sorted(df["industria"].unique().tolist())
    selected_industry = st.sidebar.selectbox("Industria", all_industries)
    
    # Filter data based on selection
    if selected_industry != "Todas las Industrias":
        df = df[df["industria"] == selected_industry]

# Key Client Metrics
st.header("Métricas de Clientes")

col1, col2, col3, col4 = st.columns(4)

with col1:
    create_kpi_card(
        "Total Clientes", 
        len(df)
    )

with col2:
    # Count total brands across all clients
    if not brand_data.empty:
        total_brands = len(brand_data)
        create_kpi_card(
            "Total Marcas", 
            total_brands
        )
    else:
        create_kpi_card(
            "Total Marcas", 
            "N/A"
        )

with col3:
    # Average revenue per client
    if "facturacion_x" in df.columns:
        avg_revenue = df["facturacion_x"].mean()
        create_kpi_card(
            "Ingreso Promedio", 
            avg_revenue,
            is_currency=True
        )
    else:
        create_kpi_card(
            "Ingreso Promedio", 
            "N/A",
            is_currency=True
        )

with col4:
    # Count industries
    if "industria" in df.columns:
        industry_count = df["industria"].nunique()
        create_kpi_card(
            "Total Industrias", 
            industry_count
        )
    else:
        create_kpi_card(
            "Total Industrias", 
            "N/A"
        )

# Client Distribution by Industry
st.header("Distribución de Clientes por Industria")

col1, col2 = st.columns(2)

with col1:
    # Create pie chart for client distribution by industry
    if not industry_counts.empty:
        fig = px.pie(
            industry_counts,
            values="count",
            names="industria",
            title="Clientes por Industria",
            color_discrete_sequence=CHART_COLORS_TRANSPARENT,
            hole=0.5
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=60, b=20),
            font=dict(family="Arial", size=12, color=COLORS['text']),
            title_font=dict(size=16, color=COLORS['text']),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color=COLORS['text'])
            )
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont=dict(color=COLORS['text'], size=12),
            hovertemplate='<b>%{label}</b><br>%{value} clientes<br>%{percent}'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de industrias disponibles")

with col2:
    # Create bar chart for client distribution by industry
    if not industry_counts.empty:
        fig = px.bar(
            industry_counts.head(10),  # Top 10 industries
            x="industria",
            y="count",
            title="Top 10 Industrias por Número de Clientes",
            color_discrete_sequence=[COLORS['secondary']]
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=60, b=100),
            xaxis=dict(
                showgrid=False,
                tickangle=45,
                title="",
                color=COLORS['text']
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                title="Número de Clientes",
                color=COLORS['text']
            ),
            font=dict(family="Arial", size=12, color=COLORS['text']),
            title_font=dict(size=16, color=COLORS['text'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de industrias disponibles")

# Top Clients by Revenue
st.header("Clientes Principales por Ingresos")

# Create a bar chart of top clients by revenue
if "facturacion_x" in df.columns:
    top_clients = df.sort_values("facturacion_x", ascending=False).head(10)
    
    fig = px.bar(
        top_clients,
        x="cliente",
        y="facturacion_x",
        title="Top 10 Clientes por Ingresos",
        color_discrete_sequence=[COLORS['secondary']]
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=100),
        xaxis=dict(
            showgrid=False,
            tickangle=45,
            title="",
            color=COLORS['text']
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="Ingresos ($)",
            tickprefix="$",
            tickformat=",",
            color=COLORS['text']
        ),
        font=dict(family="Arial", size=12, color=COLORS['text']),
        title_font=dict(size=16, color=COLORS['text'])
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hay datos de ingresos disponibles")

# Brand Analysis (only show if we have brand data)
if not brand_data.empty:
    st.header("Análisis de Marcas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top clients by brand count
        client_brand_counts = brand_data.groupby("cliente").size().reset_index(name="brand_count")
        top_brand_clients = client_brand_counts.sort_values("brand_count", ascending=False).head(10)
        
        fig = px.bar(
            top_brand_clients,
            x="cliente",
            y="brand_count",
            title="Top Clientes por Número de Marcas",
            color_discrete_sequence=[COLORS['primary']]
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=60, b=100),
            xaxis=dict(
                showgrid=False,
                tickangle=45,
                title="",
                color=COLORS['text']
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                title="Número de Marcas",
                color=COLORS['text']
            ),
            font=dict(family="Arial", size=12, color=COLORS['text']),
            title_font=dict(size=16, color=COLORS['text'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Brands by industry
        if "industria" in brand_data.columns:
            industry_brand_counts = brand_data.groupby("industria").size().reset_index(name="brand_count")
            industry_brand_counts = industry_brand_counts.sort_values("brand_count", ascending=False)
            
            fig = px.pie(
                industry_brand_counts,
                values="brand_count",
                names="industria",
                title="Distribución de Marcas por Industria",
                color_discrete_sequence=CHART_COLORS_TRANSPARENT,
                hole=0.5
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=60, b=20),
                font=dict(family="Arial", size=12, color=COLORS['text']),
                title_font=dict(size=16, color=COLORS['text']),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(color=COLORS['text'])
                )
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont=dict(color=COLORS['text'], size=12),
                hovertemplate='<b>%{label}</b><br>%{value} marcas<br>%{percent}'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de distribución de marcas por industria")

# Client Details Table
st.header("Detalles de Clientes")

# Prepare client data for display
if not df.empty:
    # Add search box for filtering the table
    search_term = st.text_input("Buscar Cliente", "")
    
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
    if "facturacion_x" in df.columns:
        display_df = display_df.sort_values(by="Ingresos", key=lambda x: pd.to_numeric(x.str.replace('$', '').str.replace(',', ''), errors='coerce'), ascending=False)
    
    # Filter by search term
    if search_term:
        display_df = display_df[display_df["Cliente"].str.contains(search_term, case=False, na=False)]
    
    # Display the table
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Export options
    st.download_button(
        label="Exportar a CSV",
        data=display_df.to_csv(index=False).encode('utf-8'),
        file_name="activagroup_clientes.csv",
        mime="text/csv",
        help="Descargar la tabla de clientes en formato CSV"
    )
else:
    st.info("No hay datos de clientes disponibles")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: rgba(255,255,255,0.5); font-size: 0.8rem;">
    <p>ActivaGroup Business Intelligence Dashboard © 2025</p>
</div>
""", unsafe_allow_html=True)
