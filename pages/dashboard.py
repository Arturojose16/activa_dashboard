"""
ActivaGroup Business Intelligence Dashboard
Main Dashboard Page - Modern Sleek Design
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
    create_kpi_card, apply_dark_theme, create_revenue_cost_chart
)

# Page configuration
st.set_page_config(
    page_title="Dashboard - ActivaGroup",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply dark theme styling
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
st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">
        <h1 style="margin-bottom: 0.25rem;">ActivaGroup Dashboard</h1>
        <p style="margin-top: 0.25rem; margin-bottom: 0;">Vista consolidada de métricas clave de negocio y indicadores de rendimiento</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Modern Navigation Bar with active state
st.markdown("""
<div class="nav-container">
    <a href="/" class="nav-link-active">Dashboard</a>
    <a href="/Client_Overview" class="nav-link">Visión de Clientes</a>
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
        
        # Get top clients
        top_clients = connector.get_top_clients(limit=10)
        
        # Get industry breakdown
        industry_breakdown = connector.get_industry_breakdown()
        
        # Get budget vs actual
        budget_vs_actual = connector.get_budget_vs_actual()
        
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

# Key Financial Metrics Section
st.markdown('<h2>Métricas Financieras Clave</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    create_kpi_card(
        "Ingresos Totales", 
        summary.get("total_income", 0), 
        is_currency=True,
        icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'
    )

with col2:
    create_kpi_card(
        "Costos Totales", 
        summary.get("total_costs", 0), 
        is_currency=True,
        icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line></svg>'
    )

with col3:
    create_kpi_card(
        "Ganancia Bruta", 
        summary.get("gross_profit", 0), 
        is_currency=True,
        icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>'
    )

with col4:
    create_kpi_card(
        "Margen Bruto", 
        summary.get("gross_margin_percentage", 0), 
        subtitle="Porcentaje de ganancia sobre ingresos",
        icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><polyline points="8 14 12 16 16 14"></polyline><line x1="12" y1="16" x2="12" y2="8"></line></svg>'
    )

# Performance Analysis Section
st.markdown('<h2>Análisis de Rendimiento</h2>', unsafe_allow_html=True)

# Monthly Revenue & Industry Breakdown
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    # Verify we have valid data before attempting to create chart
    if not monthly_costs_data.empty and "revenue" in monthly_costs_data.columns and monthly_costs_data["revenue"].sum() > 0:
        try:
            # Make sure costs column exists
            if "costs" not in monthly_costs_data.columns:
                monthly_costs_data["costs"] = monthly_costs_data["revenue"] * 0.7
                
            # Create a simple line chart as fallback if create_revenue_cost_chart fails
            fig = create_revenue_cost_chart(
                monthly_costs_data,
                title="Ingresos vs Costos Mensuales"
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            # Fallback to a simple line chart if the function fails
            try:
                st.markdown('<div class="chart-title">Ingresos Mensuales</div>', unsafe_allow_html=True)
                
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
                st.info("No se pudieron visualizar los datos de ingresos mensuales")
    else:
        st.info("No hay datos de ingresos mensuales disponibles")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    if not industry_breakdown.empty and industry_breakdown["revenue"].sum() > 0:
        try:
            st.markdown('<div class="chart-title">Distribución de Ingresos por Industria</div>', unsafe_allow_html=True)
            
            # Create a standard bar chart instead of pie to avoid opacity errors
            # Take up to 6 industries for better visualization
            top_industries = industry_breakdown.sort_values("revenue", ascending=True).tail(6)
            
            fig = px.bar(
                top_industries,
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
                marker=dict(line=dict(width=0))
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error al crear gráfico de industrias: {str(e)}")
            st.info("No se pudieron visualizar los datos de industrias")
    else:
        st.info("No hay datos de industrias disponibles")
    st.markdown('</div>', unsafe_allow_html=True)

# Budget Utilization Section
st.markdown('<h2>Utilización del Presupuesto</h2>', unsafe_allow_html=True)

if not budget_vs_actual.empty and len(budget_vs_actual) > 0:
    # Calculate overall budget utilization
    total_budget = budget_vs_actual["budget"].sum()
    total_actual = budget_vs_actual["actual"].sum()
    
    # Avoid division by zero
    if total_budget > 0:
        overall_utilization = round((total_actual / total_budget * 100), 1)
    else:
        overall_utilization = 0
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Utilización Total del Presupuesto</div>', unsafe_allow_html=True)
        
        # Create enhanced gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall_utilization,
            gauge={
                "axis": {
                    "range": [0, 120],
                    "tickwidth": 1,
                    "tickcolor": COLORS['secondary_text'],
                    "tickfont": {"size": 10, "color": COLORS['secondary_text']}
                },
                "bar": {"color": COLORS['secondary'] if overall_utilization < 100 else COLORS['success'] if overall_utilization <= 110 else COLORS['danger']},
                "bgcolor": 'rgba(255,255,255,0.05)',
                "borderwidth": 0,
                "bordercolor": 'rgba(255,255,255,0.1)',
                "steps": [
                    {"range": [0, 70], "color": 'rgba(255,255,255,0.03)'},
                    {"range": [70, 90], "color": 'rgba(255,255,255,0.04)'},
                    {"range": [90, 110], "color": 'rgba(255,255,255,0.05)'},
                    {"range": [110, 120], "color": 'rgba(255,255,255,0.06)'}
                ],
                "threshold": {
                    "line": {"color": "white", "width": 2},
                    "thickness": 0.75,
                    "value": 100
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
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add utilization explanation with better styling
        if overall_utilization >= 100:
            st.markdown('<div class="info-box">La ejecución presupuestaria está por encima de lo planificado. Revise las varianzas por cliente para identificar oportunidades de optimización.</div>', unsafe_allow_html=True)
        elif overall_utilization >= 90:
            st.markdown('<div class="info-box" style="background-color: rgba(54, 211, 153, 0.1); border-left-color: #36D399;">Utilización óptima del presupuesto.</div>', unsafe_allow_html=True)
        elif overall_utilization >= 70:
            st.markdown('<div class="warning-box">Utilización por debajo del objetivo. Revise las estrategias para mejorar la ejecución.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">Baja utilización del presupuesto. Se requiere atención inmediata en la ejecución presupuestaria.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Format table data - get top clients by budget
        if len(budget_vs_actual) > 0:
            try:
                # Safely get top 7 clients by budget
                display_data = budget_vs_actual.sort_values("budget", ascending=False).head(7)
                
                # Create styled dataframe
                st.markdown('<div class="chart-title">Top 7 Clientes por Presupuesto</div>', unsafe_allow_html=True)
                st.markdown("""
                <table class="budget-table">
                    <thead>
                        <tr>
                            <th>Cliente</th>
                            <th style="text-align: right;">Presupuesto</th>
                            <th style="text-align: right;">Ejecución</th>
                            <th style="text-align: right;">Utilización</th>
                        </tr>
                    </thead>
                    <tbody>
                """, unsafe_allow_html=True)
                
                for _, row in display_data.iterrows():
                    # Skip rows with missing or zero values
                    if pd.isna(row["utilization"]) or pd.isna(row["budget"]) or pd.isna(row["actual"]):
                        continue
                        
                    util_class = ""
                    if row["utilization"] >= 100:
                        util_class = "util-high"
                    elif row["utilization"] >= 70:
                        util_class = "util-medium"
                    else:
                        util_class = "util-low"
                        
                    st.markdown(f"""
                    <tr>
                        <td>{row["cliente"]}</td>
                        <td style="text-align: right;">${row["budget"]:,.0f}</td>
                        <td style="text-align: right;">${row["actual"]:,.0f}</td>
                        <td class="util-cell {util_class}">{row["utilization"]:.1f}%</td>
                    </tr>
                    """, unsafe_allow_html=True)
                    
                st.markdown("</tbody></table>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error al mostrar tabla de presupuesto: {str(e)}")
                st.info("No se pudo mostrar la tabla de clientes por presupuesto")
        else:
            st.info("No hay suficientes datos para mostrar la tabla de presupuesto")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No hay datos de presupuesto disponibles")

# Top clients bar chart with enhanced styling
st.markdown('<h2>Clientes Principales por Ingresos</h2>', unsafe_allow_html=True)
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
if not top_clients.empty and len(top_clients) > 0:
    st.markdown('<div class="chart-title">Top 10 Clientes por Ingresos</div>', unsafe_allow_html=True)
    
    # Check if all the data we need is available
    valid_revenue = "revenue" in top_clients.columns and top_clients["revenue"].sum() > 0
    valid_budget = "budget" in top_clients.columns and top_clients["budget"].sum() > 0
    
    if valid_revenue and valid_budget:
        try:
            # Create a grouped bar chart
            fig = go.Figure()
            
            # Add revenue bars
            fig.add_trace(go.Bar(
                x=top_clients["cliente"],
                y=top_clients["revenue"],
                name="Ingresos",
                marker_color=COLORS['secondary'],
                marker_line=dict(width=0),
                hovertemplate='<b>%{x}</b><br>Ingresos: $%{y:,.0f}'
            ))
            
            # Add budget bars
            fig.add_trace(go.Bar(
                x=top_clients["cliente"],
                y=top_clients["budget"],
                name="Presupuesto",
                marker_color=COLORS['primary'],
                marker_line=dict(width=0),
                hovertemplate='<b>%{x}</b><br>Presupuesto: $%{y:,.0f}'
            ))
            
            # Update layout with enhanced styling
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
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            # Fallback to simple bar chart
            try:
                # Create a simple revenue-only bar chart as fallback
                fig = px.bar(
                    top_clients,
                    x="cliente",
                    y="revenue",
                    labels={"revenue": "Ingresos ($)", "cliente": "Cliente"},
                    color_discrete_sequence=[COLORS['secondary']]
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=20, b=60),
                    xaxis_tickangle=45
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("No se pudieron visualizar los datos de clientes principales")
    elif valid_revenue:
        try:
            # Create a single bar chart for revenue with gradient colors
            fig = px.bar(
                top_clients,
                x="cliente",
                y="revenue",
                color="revenue",
                color_continuous_scale=[[0, COLORS['info']], [0.5, COLORS['accent3']], [1, COLORS['secondary']]],
                labels={"revenue": "Ingresos ($)", "cliente": "Cliente"}
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
        except Exception as e:
            st.error(f"Error al crear gráfico de clientes: {str(e)}")
            st.info("No se pudieron visualizar los datos de clientes principales")
    else:
        st.info("No hay datos suficientes para mostrar los clientes principales")
else:
    st.info("No hay datos de clientes disponibles")
st.markdown('</div>', unsafe_allow_html=True)

# Detailed Analysis Section with clickable cards - FIXED VERSION
st.markdown('<h2>Análisis Detallado</h2>', unsafe_allow_html=True)
st.markdown("Explore secciones específicas para un análisis más profundo:")

# Add custom CSS for better styling of the cards
st.markdown("""
<style>
    .dashboard-card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px;
        margin-top: 16px;
        margin-bottom: 24px;
    }

    .dashboard-card {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 20px;
        transition: all 0.3s ease;
        border-left: 3px solid #F36F21;
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .dashboard-card:hover {
        background-color: rgba(255, 255, 255, 0.1);
        transform: translateY(-5px);
    }
    
    .dashboard-card h3 {
        color: white;
        margin-top: 10px;
        font-size: 1.2rem;
        margin-bottom: 8px;
    }
    
    .dashboard-card p {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        text-align: center;
    }
    
    .dashboard-card-icon {
        color: #F36F21;
        font-size: 36px;
        margin-bottom: 10px;
    }
    
    .dashboard-btn {
        background-color: #F36F21;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        margin-top: 12px;
        transition: background-color 0.2s;
    }
    
    .dashboard-btn:hover {
        background-color: #d85a15;
    }
</style>
""", unsafe_allow_html=True)

# Create the card grid using Streamlit columns
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.markdown("""
    <div class="dashboard-card">
        <div class="dashboard-card-icon">👥</div>
        <h3>Visión de Clientes</h3>
        <p>Análisis detallado de clientes, marcas e industrias.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ver detalles de Clientes", key="client_btn"):
        st.switch_page("pages/Client_Overview.py")

with col2:
    st.markdown("""
    <div class="dashboard-card">
        <div class="dashboard-card-icon">📈</div>
        <h3>Análisis de Ingresos</h3>
        <p>Tendencias, comparativas y proyecciones de ingresos.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ver análisis de Ingresos", key="revenue_btn"):
        st.switch_page("pages/Revenue_Analysis.py")

with col3:
    st.markdown("""
    <div class="dashboard-card">
        <div class="dashboard-card-icon">💼</div>
        <h3>Gestión de Presupuesto</h3>
        <p>Presupuesto vs real, análisis de varianzas y proyecciones.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ver gestión de Presupuesto", key="budget_btn"):
        st.switch_page("pages/Budget_Management.py")

with col4:
    st.markdown("""
    <div class="dashboard-card">
        <div class="dashboard-card-icon">📊</div>
        <h3>Rendimiento Financiero</h3>
        <p>Estado de resultados, análisis de costos y métricas financieras.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ver rendimiento Financiero", key="financial_btn"):
        st.switch_page("pages/Financial_Performance.py")

# Footer with modern styling
st.markdown("""
<div class="footer">
    <p>ActivaGroup Business Intelligence Dashboard © 2025</p>
</div>
""", unsafe_allow_html=True)

# Add floating AI Assistant button
st.markdown("""
<style>
    /* Floating AI button with improved styling */
    .ai-floating-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #F36F21, #FF7E3E);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 9999;
        animation: pulse 2s infinite;
        transition: transform 0.3s ease;
    }
    
    /* Pulse animation */
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(243, 111, 33, 0.4);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(243, 111, 33, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(243, 111, 33, 0);
        }
    }
    
    .ai-floating-button:hover {
        transform: scale(1.1);
    }
    
    /* The chat icon styling */
    .ai-chat-icon {
        font-size: 24px;
    }
</style>

<a href="AI_Agent" target="_self">
    <div class="ai-floating-button">
        <div class="ai-chat-icon">💬</div>
    </div>
</a>
""", unsafe_allow_html=True)
