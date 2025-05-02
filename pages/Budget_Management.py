"""
ActivaGroup Business Intelligence Dashboard
Budget Management Page - Modern Sleek Design
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
    create_kpi_card, create_gauge_chart, apply_dark_theme,
    create_dashboard_header
)

# Page configuration
st.set_page_config(
    page_title="Gestión de Presupuesto - ActivaGroup",
    page_icon="💰",
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
    "Gestión de Presupuesto", 
    "Análisis de presupuesto vs. real, varianzas y tendencias"
)

# Modern Navigation Bar with active state
st.markdown("""
<div class="nav-container">
    <a href="/" class="nav-link">Dashboard</a>
    <a href="/Client_Overview" class="nav-link">Visión de Clientes</a>
    <a href="/Revenue_Analysis" class="nav-link">Análisis de Ingresos</a>
    <a href="/Budget_Management" class="nav-link-active">Gestión de Presupuesto</a>
    <a href="/Financial_Performance" class="nav-link">Rendimiento Financiero</a>
</div>
""", unsafe_allow_html=True)

# Sidebar filters
with st.sidebar:
    st.markdown('<h3 style="font-size: 1.3rem; margin-bottom: 1rem;">Filtros</h3>', unsafe_allow_html=True)

# Load Data
with st.spinner("Cargando datos..."):
    try:
        # Get budget vs actual data
        budget_data = connector.get_budget_vs_actual()
        
        if budget_data.empty:
            st.error("No se pudo cargar la información de presupuesto")
            st.stop()
        
        # Get industry breakdown for budget allocation
        combined = connector.get_combined_metrics()
        
        if combined:
            df = pd.DataFrame(combined)
        else:
            df = pd.DataFrame()
    
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        st.stop()

# Add industry filter if data is available
if not df.empty and "industria" in df.columns:
    with st.sidebar:
        all_industries = ["Todas las Industrias"] + sorted(df["industria"].unique().tolist())
        selected_industry = st.selectbox("Industria", all_industries)
        
        # Filter data based on selection
        if selected_industry != "Todas las Industrias":
            # Filter budget data
            if "industria" in budget_data.columns:
                budget_data = budget_data[budget_data["industria"] == selected_industry]
            
            # Filter combined data
            df = df[df["industria"] == selected_industry]

# Key Budget Metrics
st.markdown('<h2>Métricas de Presupuesto</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Total Budget
    total_budget = budget_data["budget"].sum() if not budget_data.empty else 0
    create_kpi_card(
        "Presupuesto Total", 
        total_budget,
        is_currency=True,
        icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>'
    )

with col2:
    # Total Actual
    total_actual = budget_data["actual"].sum() if not budget_data.empty else 0
    create_kpi_card(
        "Ejecución Total", 
        total_actual,
        is_currency=True,
        icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg>'
    )

with col3:
    # Budget Variance
    if not budget_data.empty and total_budget > 0:
        variance = total_actual - total_budget
        variance_pct = round((variance / total_budget * 100), 1)
        create_kpi_card(
            "Varianza", 
            variance,
            subtitle=f"{variance_pct}% del presupuesto",
            is_currency=True,
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>'
        )
    else:
        create_kpi_card(
            "Varianza", 
            "N/A",
            is_currency=True,
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>'
        )

with col4:
    # Budget Utilization
    if not budget_data.empty and total_budget > 0:
        utilization = round((total_actual / total_budget * 100), 1)
        create_kpi_card(
            "Utilización", 
            utilization,
            subtitle="% del presupuesto ejecutado",
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
        )
    else:
        create_kpi_card(
            "Utilización", 
            "N/A",
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
        )

# Budget Utilization Overview
st.markdown('<h2>Utilización del Presupuesto</h2>', unsafe_allow_html=True)

if not budget_data.empty and total_budget > 0:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Calculate overall budget utilization
        overall_utilization = round((total_actual / total_budget * 100), 1)
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig = create_gauge_chart(
            overall_utilization,
            title="Utilización Global del Presupuesto",
            min_val=0,
            max_val=120,
            threshold=100
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
        # Create budget vs actual chart for top clients
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        top_budget_clients = budget_data.nlargest(7, "budget")
        
        st.markdown('<div class="chart-title">Top 7 Clientes: Presupuesto vs. Ejecución</div>', unsafe_allow_html=True)
        
        fig = px.bar(
            top_budget_clients,
            x="cliente",
            y=["budget", "actual"],
            barmode="group",
            labels={"value": "Monto ($)", "cliente": "Cliente", "variable": "Tipo"},
            color_discrete_map={
                "budget": COLORS['primary'],
                "actual": COLORS['secondary']
            }
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
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
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
        
        # Rename legend items
        for i, name in enumerate(["Presupuesto", "Ejecución"]):
            fig.data[i].name = name
            fig.data[i].marker.line.width = 0
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No hay datos de presupuesto disponibles")

# Budget Variance Analysis
st.markdown('<h2>Análisis de Varianzas</h2>', unsafe_allow_html=True)

if not budget_data.empty:
    # Add variance percentage if not already present
    if "variance_pct" not in budget_data.columns:
        budget_data["variance_pct"] = budget_data.apply(
            lambda x: round(((x["variance"] / x["budget"]) * 100), 1) if x["budget"] > 0 else 0,
            axis=1
        )
    
    # Create variance chart
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    budget_data_sorted = budget_data.sort_values("variance", ascending=False).head(15)
    
    st.markdown('<div class="chart-title">Top 15 Varianzas de Presupuesto</div>', unsafe_allow_html=True)
    
    fig = px.bar(
        budget_data_sorted,
        y="cliente",
        x="variance",
        color="variance",
        color_continuous_scale=["#F44336", "#EEEEEE", "#4CAF50"],
        color_continuous_midpoint=0,
        orientation="h",
        text="variance_pct"
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
    
    # Update text formatting and position
    fig.update_traces(
        texttemplate="%{text}%",
        textposition="outside",
        textfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
        hovertemplate="<b>%{y}</b><br>Varianza: $%{x:,.0f}<br>%{text}% del presupuesto",
        marker=dict(line=dict(width=0))
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Variance Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Count of over budget
        over_budget_count = (budget_data["variance"] > 0).sum()
        over_budget_pct = round((over_budget_count / len(budget_data) * 100), 1)
        create_kpi_card(
            "Clientes Sobre Presupuesto", 
            over_budget_count,
            subtitle=f"{over_budget_pct}% del total",
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
        )
    
    with col2:
        # Count of under budget
        under_budget_count = (budget_data["variance"] < 0).sum()
        under_budget_pct = round((under_budget_count / len(budget_data) * 100), 1)
        create_kpi_card(
            "Clientes Bajo Presupuesto", 
            under_budget_count,
            subtitle=f"{under_budget_pct}% del total",
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>'
        )
    
    with col3:
        # On budget (within 5% variance)
        if "variance_pct" in budget_data.columns:
            on_budget_count = ((budget_data["variance_pct"] <= 5) & (budget_data["variance_pct"] >= -5)).sum()
            on_budget_pct = round((on_budget_count / len(budget_data) * 100), 1)
            create_kpi_card(
                "Clientes En Presupuesto", 
                on_budget_count,
                subtitle=f"{on_budget_pct}% del total (±5%)",
                icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
            )
        else:
            create_kpi_card(
                "Clientes En Presupuesto", 
                "N/A",
                subtitle="(±5% varianza)",
                icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
            )
else:
    st.info("No hay datos de varianzas disponibles")

# Budget Allocation
st.markdown('<h2>Asignación del Presupuesto</h2>', unsafe_allow_html=True)

if not df.empty and "presupuesto_x" in df.columns and "industria" in df.columns:
    # Create budget allocation by industry
    budget_by_industry = df.groupby("industria")["presupuesto_x"].sum().reset_index()
    budget_by_industry = budget_by_industry.sort_values("presupuesto_x", ascending=False)
    
    # Rename columns for clarity
    budget_by_industry = budget_by_industry.rename(columns={
        "industria": "Industria", 
        "presupuesto_x": "Presupuesto"
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create bar chart instead of pie chart to avoid opacity issues
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Asignación de Presupuesto por Industria</div>', unsafe_allow_html=True)
        
        # Get top 7 industries
        top_industries = budget_by_industry.head(7)
        
        fig = px.bar(
            top_industries,
            y="Industria",
            x="Presupuesto",
            color="Presupuesto",
            color_continuous_scale=[[0, COLORS['info']], [0.5, COLORS['accent3']], [1, COLORS['secondary']]],
            orientation="h",
            text="Presupuesto"
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
        
        # Format text values
        fig.update_traces(
            texttemplate='$%{x:,.0f}',
            textposition='outside',
            textfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
            marker=dict(line=dict(width=0)),
            hovertemplate='<b>%{y}</b><br>$%{x:,.0f}'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Create bar chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Top 10 Industrias por Presupuesto</div>', unsafe_allow_html=True)
        
        fig = px.bar(
            budget_by_industry.head(10),
            y="Industria",
            x="Presupuesto",
            color="Presupuesto",
            color_continuous_scale=[[0, COLORS['info']], [0.5, COLORS['primary']], [1, COLORS['secondary']]],
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
            texttemplate='$%{x:,.0f}',
            textposition='outside',
            textfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text']),
            marker=dict(line=dict(width=0))
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No hay datos suficientes para mostrar la asignación de presupuesto")

# Budget vs Actual Details
st.markdown('<h2>Detalle de Presupuesto vs. Ejecución</h2>', unsafe_allow_html=True)

if not budget_data.empty:
    # Add search box for filtering the table
    search_box_container = st.container()
    with search_box_container:
        st.markdown('<div style="margin-bottom: 1rem;">', unsafe_allow_html=True)
        search_term = st.text_input("🔍 Buscar Cliente", "")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Prepare data for display
    display_df = budget_data.copy()
    
    # Ensure we have utilization percentage
    if "utilization" not in display_df.columns:
        display_df["utilization"] = display_df.apply(
            lambda x: round((x["actual"] / x["budget"] * 100), 1) if x["budget"] > 0 else 0,
            axis=1
        )
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        "cliente": "Cliente",
        "industria": "Industria",
        "budget": "Presupuesto",
        "actual": "Ejecución",
        "variance": "Varianza",
        "utilization": "Utilización (%)"
    })
    
    # Sort by budget descending
    display_df = display_df.sort_values("Presupuesto", ascending=False)
    
    # Filter by search term
    if search_term:
        display_df = display_df[display_df["Cliente"].str.contains(search_term, case=False, na=False)]
    
    # Format columns with numeric values
    for col, format_str in {
        "Presupuesto": "${:,.0f}",
        "Ejecución": "${:,.0f}",
        "Varianza": "${:,.0f}",
        "Utilización (%)": "{:.1f}%"
    }.items():
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: format_str.format(x) if pd.notna(x) else "N/A"
            )
    
    # Create styled dataframe with conditional formatting
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
            file_name="activagroup_presupuesto.csv",
            mime="text/csv",
            help="Descargar la tabla de presupuesto en formato CSV"
        )
else:
    st.info("No hay datos de presupuesto disponibles")

# Budget Performance Insights
st.markdown('<h2>Insights de Rendimiento Presupuestario</h2>', unsafe_allow_html=True)

if not budget_data.empty:
    # Ensure we have variance_pct
    if "variance_pct" not in budget_data.columns:
        budget_data["variance_pct"] = budget_data.apply(
            lambda x: round((x["variance"] / x["budget"] * 100), 1) if x["budget"] > 0 else 0,
            axis=1
        )
    
    # Ensure we have utilization
    if "utilization" not in budget_data.columns:
        budget_data["utilization"] = budget_data.apply(
            lambda x: round((x["actual"] / x["budget"] * 100), 1) if x["budget"] > 0 else 0,
            axis=1
        )
    
    # Calculate metrics for insights
    over_performers = budget_data[budget_data["utilization"] > 110].sort_values("variance", ascending=False)
    under_performers = budget_data[budget_data["utilization"] < 70].sort_values("variance")
    on_target = budget_data[(budget_data["utilization"] >= 90) & (budget_data["utilization"] <= 110)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Clientes Sobre Ejecución (>110%)</div>', unsafe_allow_html=True)
        
        if not over_performers.empty:
            over_df = over_performers[["cliente", "budget", "actual", "utilization"]].head(5)
            over_df = over_df.rename(columns={
                "cliente": "Cliente",
                "budget": "Presupuesto",
                "actual": "Ejecución",
                "utilization": "Utilización (%)"
            })
            
            # Format values
            over_df["Presupuesto"] = over_df["Presupuesto"].apply(lambda x: f"${x:,.0f}")
            over_df["Ejecución"] = over_df["Ejecución"].apply(lambda x: f"${x:,.0f}")
            over_df["Utilización (%)"] = over_df["Utilización (%)"].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(over_df, use_container_width=True, hide_index=True)
            
            if len(over_performers) > 0:
                total_over = over_performers["actual"].sum() - over_performers["budget"].sum()
                st.warning(f"Estos {len(over_performers)} clientes están sobre el presupuesto por un total de ${total_over:,.0f}.")
        else:
            st.success("No hay clientes con sobre-ejecución mayor al 110%.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Clientes Bajo Ejecución (<70%)</div>', unsafe_allow_html=True)
        
        if not under_performers.empty:
            under_df = under_performers[["cliente", "budget", "actual", "utilization"]].head(5)
            under_df = under_df.rename(columns={
                "cliente": "Cliente",
                "budget": "Presupuesto",
                "actual": "Ejecución",
                "utilization": "Utilización (%)"
            })
            
            # Format values
            under_df["Presupuesto"] = under_df["Presupuesto"].apply(lambda x: f"${x:,.0f}")
            under_df["Ejecución"] = under_df["Ejecución"].apply(lambda x: f"${x:,.0f}")
            under_df["Utilización (%)"] = under_df["Utilización (%)"].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(under_df, use_container_width=True, hide_index=True)
            
            if len(under_performers) > 0:
                total_under = under_performers["budget"].sum() - under_performers["actual"].sum()
                st.error(f"Estos {len(under_performers)} clientes están bajo el presupuesto por un total de ${total_under:,.0f}.")
        else:
            st.success("No hay clientes con bajo rendimiento presupuestario (<70%).")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # On-target performance
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Rendimiento Óptimo (90-110%)</div>', unsafe_allow_html=True)
    
    on_target_count = len(on_target)
    on_target_pct = round((on_target_count / len(budget_data) * 100), 1)
    
    st.info(f"{on_target_count} clientes ({on_target_pct}% del total) tienen una ejecución óptima entre el 90% y 110% del presupuesto.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No hay datos suficientes para generar insights")

# Footer with modern styling
st.markdown("""
<div class="footer">
    <p>ActivaGroup Business Intelligence Dashboard © 2025</p>
</div>
""", unsafe_allow_html=True)
