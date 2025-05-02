"""
ActivaGroup Business Intelligence Dashboard
Revenue Analysis Page - Modern Sleek Design
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sys

# Add parent directory to path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import custom utilities
from utils.data_connector import ActivaDataConnector
from utils.visualization import (
    COLORS, CHART_COLORS, CHART_COLORS_TRANSPARENT,
    create_kpi_card, apply_dark_theme, create_dashboard_header,
    create_revenue_cost_chart, create_client_concentration_chart
)

# Page configuration
st.set_page_config(
    page_title="Análisis de Ingresos - ActivaGroup",
    page_icon="📈",
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

# Helper function to extract monthly revenue from P&L data
def extract_monthly_revenue_from_pl(pl_data):
    """Extract monthly revenue data from the P&L table."""
    try:
        # Check if we have valid P&L data
        if pl_data.empty or "concepto" not in pl_data.columns:
            return None
        
        # Look for total revenue row in P&L data
        revenue_keywords = ["total ingreso", "ingresos totales", "total revenue", "revenue total"]
        total_revenue_row = None
        
        for keyword in revenue_keywords:
            matches = pl_data[pl_data["concepto"].str.contains(keyword, case=False, na=False)]
            if not matches.empty:
                total_revenue_row = matches.iloc[0]
                break
        
        if total_revenue_row is None:
            return None
        
        # Find month columns (excluding 'concepto' and 'CONSOLIDADO')
        month_cols = [col for col in pl_data.columns if col not in ["concepto", "CONSOLIDADO"] and 
                    not col.startswith("Unnamed:")]
        
        if not month_cols:
            return None
        
        # Define month order mapping
        month_order = {
            "ENERO": 1, "ENE": 1, "JAN": 1, "JANUARY": 1,
            "FEBRERO": 2, "FEB": 2, "FEBRUARY": 2,
            "MARZO": 3, "MAR": 3, "MARCH": 3,
            "ABRIL": 4, "ABR": 4, "APR": 4, "APRIL": 4,
            "MAYO": 5, "MAY": 5,
            "JUNIO": 6, "JUN": 6, "JUNE": 6,
            "JULIO": 7, "JUL": 7, "JULY": 7,
            "AGOSTO": 8, "AGO": 8, "AUG": 8, "AUGUST": 8,
            "SEPTIEMBRE": 9, "SEP": 9, "SEPTEMBER": 9,
            "OCTUBRE": 10, "OCT": 10, "OCTOBER": 10,
            "NOVIEMBRE": 11, "NOV": 11, "NOVEMBER": 11,
            "DICIEMBRE": 12, "DIC": 12, "DEC": 12, "DECEMBER": 12
        }
        
        # Create monthly data
        monthly_data = []
        
        for month in month_cols:
            value = total_revenue_row[month]
            # Skip if value is not a valid number
            if pd.isna(value) or not isinstance(value, (int, float)):
                continue
                
            # Determine month order
            month_name_upper = month.upper()
            month_order_value = 0
            
            # Try to match the month name to get the order
            for key, order in month_order.items():
                if key in month_name_upper:
                    month_order_value = order
                    break
            
            monthly_data.append({
                "month": month,
                "revenue": float(value),
                "month_order": month_order_value
            })
        
        # Convert to DataFrame
        result_df = pd.DataFrame(monthly_data)
        
        # Sort by month_order if it exists
        if not result_df.empty and "month_order" in result_df.columns:
            result_df = result_df.sort_values("month_order")
        
        return result_df
    
    except Exception as e:
        print(f"Error extracting monthly revenue: {str(e)}")
        return None

# Check if user is logged in (if using login system)
if "logged_in" in st.session_state and not st.session_state.logged_in:
    st.warning("Por favor inicie sesión para acceder al dashboard")
    st.stop()

# Dashboard Header
create_dashboard_header(
    "Análisis de Ingresos", 
    "Análisis detallado de ingresos, tendencias y distribución"
)

# Modern Navigation Bar with active state
st.markdown("""
<div class="nav-container">
    <a href="/" class="nav-link">Dashboard</a>
    <a href="/Client_Overview" class="nav-link">Visión de Clientes</a>
    <a href="/Revenue_Analysis" class="nav-link-active">Análisis de Ingresos</a>
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
        # Get financial summary
        financial = connector.get_financial_summary()
        summary = financial.get("summary", {})
        
        # Get P&L data for cost information (and potentially monthly revenue)
        pl_data = connector.get_profit_loss_data()
        
        # Try to extract monthly revenue from P&L data first (more reliable)
        monthly_revenue = None
        if not pl_data.empty:
            monthly_revenue = extract_monthly_revenue_from_pl(pl_data)
        
        # If P&L extraction failed, fall back to the connector method
        if monthly_revenue is None or monthly_revenue.empty:
            monthly_revenue = connector.get_monthly_revenue()
            
            # Ensure month names are in Spanish for consistency
            if not monthly_revenue.empty and "month" in monthly_revenue.columns:
                # Map of month names from any language to Spanish
                month_mapping = {
                    "JANUARY": "ENERO", "JAN": "ENERO", "1": "ENERO", 
                    "FEBRUARY": "FEBRERO", "FEB": "FEBRERO", "2": "FEBRERO",
                    "MARCH": "MARZO", "MAR": "MARZO", "3": "MARZO",
                    "APRIL": "ABRIL", "APR": "ABRIL", "4": "ABRIL",
                    "MAY": "MAYO", "5": "MAYO",
                    "JUNE": "JUNIO", "JUN": "JUNIO", "6": "JUNIO",
                    "JULY": "JULIO", "JUL": "JULIO", "7": "JULIO",
                    "AUGUST": "AGOSTO", "AUG": "AGOSTO", "8": "AGOSTO",
                    "SEPTEMBER": "SEPTIEMBRE", "SEP": "SEPTIEMBRE", "9": "SEPTIEMBRE",
                    "OCTOBER": "OCTUBRE", "OCT": "OCTUBRE", "10": "OCTUBRE",
                    "NOVEMBER": "NOVIEMBRE", "NOV": "NOVIEMBRE", "11": "NOVIEMBRE",
                    "DECEMBER": "DICIEMBRE", "DEC": "DICIEMBRE", "12": "DICIEMBRE"
                }
                
                # Function to standardize month names
                def standardize_month(month_name):
                    month_upper = str(month_name).upper().strip()
                    for key, value in month_mapping.items():
                        if key in month_upper:
                            return value
                    return month_upper  # Return as-is if no match
                
                # Apply standardization
                monthly_revenue["display_month"] = monthly_revenue["month"].apply(standardize_month)
        
        # Get combined metrics
        combined = connector.get_combined_metrics()
        
        if combined:
            df = pd.DataFrame(combined)
        else:
            st.error("No se pudo cargar la información de ingresos")
            st.stop()
        
        # Get industry breakdown
        industry_breakdown = pd.DataFrame()
        if "industria" in df.columns and "facturacion_x" in df.columns:
            industry_data = df.groupby("industria")["facturacion_x"].sum().reset_index()
            industry_data = industry_data.sort_values("facturacion_x", ascending=False)
            industry_breakdown = industry_data.rename(columns={
                "facturacion_x": "revenue",
                "industria": "industry"
            })
        
        # Create revenue vs costs data for the chart
        monthly_costs_data = pd.DataFrame()
        if not monthly_revenue.empty and "revenue" in monthly_revenue.columns:
            # Create a copy to avoid modifying the original
            monthly_costs_data = monthly_revenue.copy()
            
            # Generate cost estimates based on gross margin if available
            if "gross_margin_percentage" in summary and summary["gross_margin_percentage"] > 0:
                margin = summary["gross_margin_percentage"]
                cost_ratio = 1 - (margin / 100)
                monthly_costs_data["costs"] = monthly_costs_data["revenue"] * cost_ratio
            else:
                # Default to 70% cost ratio
                monthly_costs_data["costs"] = monthly_costs_data["revenue"] * 0.7
    
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

# Key Revenue Metrics
st.markdown('<h2>Métricas de Ingresos</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Total Revenue
    total_revenue = summary.get("total_income", 0)
    create_kpi_card(
        "Ingresos Totales", 
        total_revenue,
        is_currency=True,
        icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'
    )

with col2:
    # Average Monthly Revenue
    if not monthly_revenue.empty and "revenue" in monthly_revenue.columns:
        avg_monthly = monthly_revenue["revenue"].mean()
        create_kpi_card(
            "Promedio Mensual", 
            avg_monthly,
            is_currency=True,
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>'
        )
    else:
        create_kpi_card(
            "Promedio Mensual", 
            "N/A",
            is_currency=True,
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>'
        )

with col3:
    # Revenue per Client
    if "facturacion_x" in df.columns and len(df) > 0:
        revenue_per_client = df["facturacion_x"].sum() / len(df)
        create_kpi_card(
            "Ingreso por Cliente", 
            revenue_per_client,
            is_currency=True,
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>'
        )
    else:
        create_kpi_card(
            "Ingreso por Cliente", 
            "N/A",
            is_currency=True,
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>'
        )

with col4:
    # Top Client Contribution
    if "facturacion_x" in df.columns and len(df) > 0:
        total_facturacion = df["facturacion_x"].sum()
        if total_facturacion > 0:
            top_client_revenue = df["facturacion_x"].max()
            top_client_pct = round((top_client_revenue / total_facturacion * 100), 1)
            create_kpi_card(
                "Contrib. Cliente Principal", 
                top_client_pct,
                subtitle=f"${top_client_revenue:,.0f}",
                icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
            )
        else:
            create_kpi_card(
                "Contrib. Cliente Principal", 
                "N/A",
                icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
            )
    else:
        create_kpi_card(
            "Contrib. Cliente Principal", 
            "N/A",
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
        )

# Monthly Revenue Analysis
st.markdown('<h2>Análisis de Ingresos Mensuales</h2>', unsafe_allow_html=True)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
# Verify we have valid data before attempting to create chart
if not monthly_costs_data.empty and "revenue" in monthly_costs_data.columns and monthly_costs_data["revenue"].sum() > 0:
    try:
        # Make sure costs column exists
        if "costs" not in monthly_costs_data.columns:
            monthly_costs_data["costs"] = monthly_costs_data["revenue"] * 0.7
            
        # Create enhanced revenue vs costs chart
        fig = create_revenue_cost_chart(
            monthly_costs_data,
            title="Tendencia de Ingresos y Costos Mensuales"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        # Fallback to a simple line chart if the function fails
        try:
            st.markdown('<div class="chart-title">Tendencia de Ingresos Mensuales</div>', unsafe_allow_html=True)
            
            # Create a basic line chart
            fig = go.Figure()
            
            # Add revenue line
            fig.add_trace(go.Scatter(
                x=monthly_costs_data["month"],
                y=monthly_costs_data["revenue"],
                mode='lines+markers',
                name='Ingresos',
                line=dict(color=COLORS['secondary'], width=3),
                marker=dict(size=8)
            ))
            
            # Simple layout
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=40),
                xaxis_title="",
                yaxis_title="",
                yaxis_tickprefix="$",
                yaxis_tickformat=",",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e2:
            st.error(f"Error al crear gráfico de ingresos mensuales: {str(e2)}")
            st.info("No se pudieron visualizar los datos de ingresos mensuales")
else:
    st.info("No hay datos de ingresos mensuales disponibles")
st.markdown('</div>', unsafe_allow_html=True)

# Monthly statistics - fixed to properly show month names
st.subheader("Estadísticas Mensuales")

if not monthly_revenue.empty and "revenue" in monthly_revenue.columns and len(monthly_revenue) > 1:
    try:
        # Find highest month
        highest_idx = monthly_revenue['revenue'].idxmax()
        highest_month_row = monthly_revenue.loc[highest_idx]
        
        # Check if we have a display_month column, otherwise use month
        month_column = 'display_month' if 'display_month' in monthly_revenue.columns else 'month'
        
        # Make sure we convert to string and make uppercase for consistency
        highest_month = str(highest_month_row[month_column]).upper()
        highest_value = highest_month_row['revenue']
        
        # Find lowest month
        lowest_idx = monthly_revenue['revenue'].idxmin()
        lowest_month_row = monthly_revenue.loc[lowest_idx]
        lowest_month = str(lowest_month_row[month_column]).upper()
        lowest_value = lowest_month_row['revenue']
        
        # Calculate average monthly growth
        sorted_revenue = monthly_revenue.sort_values('month_order') if 'month_order' in monthly_revenue.columns else monthly_revenue
        
        # Calculate month-to-month percentage changes
        pct_changes = []
        prev_revenue = None
        
        for _, row in sorted_revenue.iterrows():
            if prev_revenue is not None and prev_revenue > 0:
                pct_change = ((row['revenue'] - prev_revenue) / prev_revenue) * 100
                pct_changes.append(pct_change)
            prev_revenue = row['revenue']
        
        # Calculate average growth (if we have enough data points)
        avg_growth = round(sum(pct_changes) / len(pct_changes), 1) if pct_changes else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Highest month - we explicitly use the month name as the main value
            create_kpi_card(
                "Mes con Mayor Ingreso", 
                highest_month,  # This should be the name like "MARZO"
                subtitle=f"${highest_value:,.0f}",
                icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
            )
        
        with col2:
            # Lowest month - we explicitly use the month name as the main value
            create_kpi_card(
                "Mes con Menor Ingreso", 
                lowest_month,  # This should be the name like "ENERO"
                subtitle=f"${lowest_value:,.0f}",
                icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>'
            )
        
        with col3:
            # Average growth
            create_kpi_card(
                "Crecimiento Promedio", 
                avg_growth,
                subtitle="Promedio mensual",
                icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
            )
    
    except Exception as e:
        # Fallback to showing default cards if calculation fails
        st.error(f"Error al calcular estadísticas mensuales: {str(e)}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            create_kpi_card(
                "Mes con Mayor Ingreso", 
                "N/A",
                icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
            )
        
        with col2:
            create_kpi_card(
                "Mes con Menor Ingreso", 
                "N/A",
                icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>'
            )
        
        with col3:
            create_kpi_card(
                "Crecimiento Promedio", 
                "N/A",
                subtitle="Promedio mensual",
                icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
            )
else:
    # If no data, show empty cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_kpi_card(
            "Mes con Mayor Ingreso", 
            "N/A",
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
        )
    
    with col2:
        create_kpi_card(
            "Mes con Menor Ingreso", 
            "N/A",
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>'
        )
    
    with col3:
        create_kpi_card(
            "Crecimiento Promedio", 
            "N/A",
            subtitle="Promedio mensual",
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
        )

# Revenue Distribution Analysis
st.markdown('<h2>Distribución de Ingresos</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Revenue by Industry - use bar chart instead of pie chart to avoid opacity error
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    if not industry_breakdown.empty and industry_breakdown["revenue"].sum() > 0:
        try:
            # Create bar chart instead of pie chart
            st.markdown('<div class="chart-title">Distribución de Ingresos por Industria</div>', unsafe_allow_html=True)
            
            # Sort industries by revenue
            industry_top = industry_breakdown.head(7)
            
            fig = px.bar(
                industry_top,
                y="industry",
                x="revenue",
                orientation='h',
                color="revenue",
                color_continuous_scale=[[0, COLORS['info']], [0.5, COLORS['accent3']], [1, COLORS['secondary']]],
                labels={"revenue": "Ingresos ($)", "industry": "Industria"}
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.05)',
                    title="",
                    tickprefix="$",
                    tickformat=",",
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
            
            # Add value labels
            fig.update_traces(
                texttemplate='$%{x:,.0f}',
                textposition='outside',
                textfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
                marker=dict(line=dict(width=0)),
                hovertemplate='<b>%{y}</b><br>$%{x:,.0f}'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error al crear gráfico de industrias: {str(e)}")
            st.info("No se pudieron visualizar los datos de distribución por industria")
    else:
        st.info("No hay datos de distribución por industria disponibles")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Client Concentration
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    if "facturacion_x" in df.columns and len(df) > 0 and df["facturacion_x"].sum() > 0:
        try:
            # Create client concentration data
            total_revenue = df["facturacion_x"].sum()
            
            # Group clients into categories
            sorted_clients = df.sort_values("facturacion_x", ascending=False)
            
            # Define client segments
            top_5_clients = sorted_clients.iloc[:5]
            clients_6_10 = sorted_clients.iloc[5:10] if len(sorted_clients) > 5 else pd.DataFrame()
            clients_11_20 = sorted_clients.iloc[10:20] if len(sorted_clients) > 10 else pd.DataFrame()
            other_clients = sorted_clients.iloc[20:] if len(sorted_clients) > 20 else pd.DataFrame()
            
            # Calculate revenue by segment
            top_5 = top_5_clients["facturacion_x"].sum()
            top_10 = clients_6_10["facturacion_x"].sum() if not clients_6_10.empty else 0
            top_20 = clients_11_20["facturacion_x"].sum() if not clients_11_20.empty else 0
            others = other_clients["facturacion_x"].sum() if not other_clients.empty else 0
            
            # Create data for visualization
            concentration_data = pd.DataFrame([
                {"category": "Top 5 Clientes", "revenue": top_5, "order": 1},
                {"category": "Clientes 6-10", "revenue": top_10, "order": 2},
                {"category": "Clientes 11-20", "revenue": top_20, "order": 3},
                {"category": "Otros Clientes", "revenue": others, "order": 4}
            ])
            
            # Create enhanced funnel chart
            fig = create_client_concentration_chart(
                concentration_data,
                title="Concentración de Ingresos por Clientes"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error al crear gráfico de concentración: {str(e)}")
            st.info("No se pudieron visualizar los datos de concentración de ingresos")
    else:
        st.info("No hay datos suficientes para mostrar la concentración de clientes")
    st.markdown('</div>', unsafe_allow_html=True)

# Top Clients by Revenue
st.markdown('<h2>Clientes Principales por Ingresos</h2>', unsafe_allow_html=True)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
if "facturacion_x" in df.columns and len(df) > 0 and df["facturacion_x"].sum() > 0:
    try:
        # Get top 15 clients
        top_clients = df.nlargest(15, "facturacion_x")[["cliente", "industria", "facturacion_x"]]
        
        st.markdown('<div class="chart-title">Top 15 Clientes por Ingresos</div>', unsafe_allow_html=True)
        
        # Create horizontal bar chart with enhanced styling
        fig = px.bar(
            top_clients,
            y="cliente",
            x="facturacion_x",
            color="industria",
            labels={"facturacion_x": "Ingresos ($)", "cliente": "Cliente", "industria": "Industria"},
            color_discrete_sequence=CHART_COLORS,
            orientation="h"
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.05)',
                title="",
                tickprefix="$",
                tickformat=",",
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
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=-0.15, 
                xanchor="center", 
                x=0.5,
                title="",
                font=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
            ),
            hoverlabel=dict(
                bgcolor=COLORS['panel_bg'],
                font_size=12,
                font_family="Inter, sans-serif",
                bordercolor='rgba(255,255,255,0.1)'
            )
        )
        
        # Add value labels to the bars
        for i in range(len(fig.data)):
            fig.data[i].texttemplate = '$%{x:,.0f}'
            fig.data[i].textposition = 'outside'
            fig.data[i].textfont = dict(family="Inter, sans-serif", size=10, color=COLORS['secondary_text'])
            fig.data[i].marker.line.width = 0
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error al crear gráfico de clientes principales: {str(e)}")
        st.info("No se pudieron visualizar los datos de clientes principales")
else:
    st.info("No hay datos suficientes para mostrar los clientes principales")
st.markdown('</div>', unsafe_allow_html=True)

# Revenue Table - Detailed breakdown
st.markdown('<h2>Detalles de Ingresos por Cliente</h2>', unsafe_allow_html=True)

# Prepare revenue data for display
if "facturacion_x" in df.columns and len(df) > 0:
    # Add search box for filtering the table
    search_box_container = st.container()
    with search_box_container:
        st.markdown('<div style="margin-bottom: 1rem;">', unsafe_allow_html=True)
        search_term = st.text_input("🔍 Buscar Cliente", "")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Select relevant columns - base columns plus any monthly revenue columns
    display_cols = ["cliente", "industria", "facturacion_x"]
    
    # Find monthly revenue columns
    monthly_cols = [col for col in df.columns if col.startswith("facturacion_") and col != "facturacion_x"]
    display_cols.extend(monthly_cols)
    
    # Add budget column if available
    if "presupuesto_x" in df.columns:
        display_cols.append("presupuesto_x")
    
    # Ensure all columns exist before creating display df
    available_cols = [col for col in display_cols if col in df.columns]
    display_df = df[available_cols].copy()
    
    # Rename columns for display
    rename_dict = {
        "cliente": "Cliente",
        "industria": "Industria",
        "facturacion_x": "Total Ingresos",
        "presupuesto_x": "Presupuesto"
    }
    
    # Add month names to rename dictionary
    month_names = {
        "facturacion_ene": "Enero",
        "facturacion_feb": "Febrero",
        "facturacion_mar": "Marzo",
        "facturacion_abr": "Abril",
        "facturacion_may": "Mayo",
        "facturacion_jun": "Junio",
        "facturacion_jul": "Julio",
        "facturacion_ago": "Agosto",
        "facturacion_sep": "Septiembre",
        "facturacion_oct": "Octubre",
        "facturacion_nov": "Noviembre",
        "facturacion_dic": "Diciembre"
    }
    
    # Only add month names that exist in our columns
    for col, name in month_names.items():
        if col in display_df.columns:
            rename_dict[col] = name
    
    # Only rename columns that exist
    rename_cols = {k: v for k, v in rename_dict.items() if k in display_df.columns}
    display_df = display_df.rename(columns=rename_cols)
    
    # Sort by total revenue descending
    display_df = display_df.sort_values(by="Total Ingresos", ascending=False)
    
    # Format currency columns - any column except Cliente and Industria
    currency_cols = [col for col in display_df.columns if col not in ["Cliente", "Industria"]]
    for col in currency_cols:
        display_df[col] = display_df[col].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
        )
    
    # Filter by search term
    if search_term:
        display_df = display_df[display_df["Cliente"].str.contains(search_term, case=False, na=False)]
    
    # Display the table with enhanced styling
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
            file_name="activagroup_ingresos.csv",
            mime="text/csv",
            help="Descargar la tabla de ingresos en formato CSV"
        )
else:
    st.info("No hay datos de ingresos disponibles")

# Footer with modern styling
st.markdown("""
<div class="footer">
    <p>ActivaGroup Business Intelligence Dashboard © 2025</p>
</div>
""", unsafe_allow_html=True)
