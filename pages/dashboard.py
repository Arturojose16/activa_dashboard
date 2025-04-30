"""
ActivaGroup Business Intelligence Dashboard
Main Dashboard Page
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
    create_kpi_card, create_revenue_line_chart, create_industry_pie_chart,
    create_top_clients_bar_chart, create_gauge_chart, apply_dark_theme
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

# Check if user is logged in (if using login system)
if "logged_in" in st.session_state and not st.session_state.logged_in:
    st.warning("Por favor inicie sesión para acceder al dashboard")
    st.stop()

# Page header with smaller bottom margin
st.markdown("""
    <h1 style='margin-bottom:0.5rem;'>ActivaGroup Dashboard</h1>
    <p style='margin-bottom:2rem;'>Vista consolidada de métricas clave de negocio y indicadores de rendimiento</p>
""", unsafe_allow_html=True)

# Custom navigation tabs - using HTML to create a more stylish tab bar
st.markdown("""
<style>
    .nav-tabs {
        display: flex;
        overflow-x: auto;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .nav-tab {
        padding: 0.75rem 1.25rem;
        margin-right: 0.25rem;
        color: rgba(255,255,255,0.7);
        text-decoration: none;
        border-radius: 4px 4px 0 0;
        transition: all 0.2s ease;
        white-space: nowrap;
        font-weight: 500;
        font-size: 0.95rem;
    }
    .nav-tab:hover {
        color: white;
        background: rgba(255,255,255,0.05);
    }
    .nav-tab.active {
        color: white;
        background: rgba(243, 111, 33, 0.2);
        border-bottom: 2px solid #F36F21;
    }
</style>

<div class="nav-tabs">
    <a href="#" class="nav-tab active" id="tab-dashboard">Dashboard</a>
    <a href="#" class="nav-tab" id="tab-clients">Visión de Clientes</a>
    <a href="#" class="nav-tab" id="tab-revenue">Análisis de Ingresos</a>
    <a href="#" class="nav-tab" id="tab-budget">Gestión de Presupuesto</a>
    <a href="#" class="nav-tab" id="tab-finance">Rendimiento Financiero</a>
</div>

<script>
    // JavaScript to handle tab clicks
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Get the tab ID and send to Streamlit
            const tabId = this.id.replace('tab-', '');
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: tabId
            }, '*');
        });
    });
</script>
""", unsafe_allow_html=True)

# Handle navigation in Python
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "dashboard"

# Create a placeholder for receiving the tab click
tab_receiver = st.empty()
received_tab = tab_receiver.text_input("", key="tab_receiver", label_visibility="collapsed")

if received_tab and received_tab != st.session_state.current_tab:
    st.session_state.current_tab = received_tab
    
    # Redirect to appropriate page
    if received_tab == "clients":
        st.switch_page("pages/Client_Overview.py")
    elif received_tab == "revenue":
        st.switch_page("pages/Revenue_Analysis.py")
    elif received_tab == "budget":
        st.switch_page("pages/Budget_Management.py")
    elif received_tab == "finance":
        st.switch_page("pages/Financial_Performance.py")
    # Dashboard tab is handled in this file

# Load Data
with st.spinner("Cargando datos..."):
    # Get financial summary
    financial = connector.get_financial_summary()
    summary = financial.get("summary", {})
    
    # Get monthly revenue
    monthly_revenue = connector.get_monthly_revenue()
    
    # Get top clients
    top_clients = connector.get_top_clients(limit=10)
    
    # Get industry breakdown
    industry_breakdown = connector.get_industry_breakdown()
    
    # Get budget vs actual
    budget_vs_actual = connector.get_budget_vs_actual()

# Key Financial Metrics Section
st.header("Métricas Financieras Clave")

col1, col2, col3, col4 = st.columns(4)

with col1:
    create_kpi_card(
        "Ingresos Totales", 
        summary.get("total_income", 0), 
        is_currency=True
    )

with col2:
    create_kpi_card(
        "Costos Totales", 
        summary.get("total_costs", 0), 
        is_currency=True
    )

with col3:
    create_kpi_card(
        "Ganancia Bruta", 
        summary.get("gross_profit", 0), 
        is_currency=True
    )

with col4:
    create_kpi_card(
        "Margen Bruto", 
        summary.get("gross_margin_percentage", 0), 
        subtitle="Porcentaje de ganancia sobre ingresos"
    )

# Performance Analysis Section
st.header("Análisis de Rendimiento")

# Monthly Revenue & Industry Breakdown
col1, col2 = st.columns(2)

with col1:
    st.subheader("Ingresos Mensuales")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    if not monthly_revenue.empty:
        fig = create_revenue_line_chart(
            monthly_revenue, 
            x_col="month", 
            y_col="revenue", 
            title="Ingresos Mensuales"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de ingresos mensuales disponibles")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.subheader("Ingresos por Industria")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    if not industry_breakdown.empty:
        fig = create_industry_pie_chart(
            industry_breakdown,
            value_col="revenue",
            name_col="industry",
            title="Distribución de Ingresos por Industria"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de industrias disponibles")
    st.markdown('</div>', unsafe_allow_html=True)

# Budget Utilization Section
st.subheader("Utilización del Presupuesto")

if not budget_vs_actual.empty:
    # Calculate overall budget utilization
    overall_utilization = (budget_vs_actual["actual"].sum() / budget_vs_actual["budget"].sum() * 100).round(1)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Create gauge chart for overall utilization
        fig = create_gauge_chart(
            overall_utilization,
            title="Utilización Total del Presupuesto",
            min_val=0,
            max_val=120,
            threshold=100
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Format table data
        display_data = budget_vs_actual[["cliente", "budget", "actual", "utilization"]].head(7).copy()
        
        # Create styled dataframe
        st.markdown("""
        <style>
        .budget-table {
            width: 100%;
            border-collapse: collapse;
        }
        .budget-table th {
            background-color: #0A2463;
            color: white;
            padding: 8px 12px;
            text-align: left;
            font-weight: 500;
        }
        .budget-table td {
            padding: 8px 12px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .budget-table tr:hover {
            background-color: rgba(255,255,255,0.05);
        }
        .util-cell {
            text-align: right;
            font-weight: 500;
        }
        .util-high {
            color: #4CAF50;
        }
        .util-medium {
            color: #F36F21;
        }
        .util-low {
            color: #F44336;
        }
        </style>
        
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
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No hay datos de presupuesto disponibles")

# Top clients bar chart
st.subheader("Clientes Principales por Ingresos")
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
if not top_clients.empty:
    # Check if we have budget data
    if "budget" in top_clients.columns:
        fig = create_top_clients_bar_chart(
            top_clients,
            x_col="cliente",
            y_cols=["revenue", "budget"],
            title="Top 10 Clientes: Ingresos vs Presupuesto"
        )
    else:
        fig = create_top_clients_bar_chart(
            top_clients,
            x_col="cliente",
            y_cols=["revenue"],
            title="Top 10 Clientes por Ingresos"
        )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hay datos de clientes disponibles")
st.markdown('</div>', unsafe_allow_html=True)

# Detailed Analysis Section with clickable cards
st.header("Análisis Detallado")
st.markdown("Explore secciones específicas para un análisis más profundo:")

# Create clickable cards for navigation with custom HTML/CSS for better styling
st.markdown("""
<style>
.card-container {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 1rem;
    margin-bottom: 2rem;
}
.nav-card {
    flex: 1;
    min-width: 200px;
    background-color: #1E1E1E;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    border: 1px solid rgba(255,255,255,0.05);
    text-align: center;
    cursor: pointer;
}
.nav-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 15px rgba(0,0,0,0.2);
    border-color: #F36F21;
}
.nav-card h3 {
    color: white;
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
}
.nav-card p {
    color: rgba(255,255,255,0.7);
    font-size: 0.875rem;
    margin-bottom: 0;
}
</style>

<div class="card-container">
    <div class="nav-card" onclick="window.open('/Client_Overview','_self')">
        <h3>Visión de Clientes</h3>
        <p>Análisis detallado de clientes, marcas e industrias.</p>
    </div>
    
    <div class="nav-card" onclick="window.open('/Revenue_Analysis','_self')">
        <h3>Análisis de Ingresos</h3>
        <p>Tendencias, comparativas y proyecciones de ingresos.</p>
    </div>
    
    <div class="nav-card" onclick="window.open('/Budget_Management','_self')">
        <h3>Gestión de Presupuesto</h3>
        <p>Presupuesto vs real, análisis de varianzas y proyecciones.</p>
    </div>
    
    <div class="nav-card" onclick="window.open('/Financial_Performance','_self')">
        <h3>Rendimiento Financiero</h3>
        <p>Estado de resultados, análisis de costos y métricas financieras.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: rgba(255,255,255,0.5); font-size: 0.8rem;">
    <p>ActivaGroup Business Intelligence Dashboard © 2025</p>
</div>
""", unsafe_allow_html=True)
