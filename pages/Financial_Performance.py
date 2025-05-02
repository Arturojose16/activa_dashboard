"""
ActivaGroup Business Intelligence Dashboard
Financial Performance Page - Modern Sleek Design
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
    create_kpi_card, create_waterfall_chart, apply_dark_theme,
    create_dashboard_header, create_margin_trend_chart
)

# Page configuration
st.set_page_config(
    page_title="Rendimiento Financiero - ActivaGroup",
    page_icon="📊",
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
    "Rendimiento Financiero", 
    "Análisis detallado del desempeño financiero y métricas clave"
)

# Modern Navigation Bar with active state
st.markdown("""
<div class="nav-container">
    <a href="/" class="nav-link">Dashboard</a>
    <a href="/Client_Overview" class="nav-link">Visión de Clientes</a>
    <a href="/Revenue_Analysis" class="nav-link">Análisis de Ingresos</a>
    <a href="/Budget_Management" class="nav-link">Gestión de Presupuesto</a>
    <a href="/Financial_Performance" class="nav-link-active">Rendimiento Financiero</a>
</div>
""", unsafe_allow_html=True)

# Sidebar filters
with st.sidebar:
    st.markdown('<h3 style="font-size: 1.3rem; margin-bottom: 1rem;">Filtros</h3>', unsafe_allow_html=True)
    
    # Add time period filter (placeholder)
    period_options = ["2025 (Acumulado)", "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"]
    selected_period = st.selectbox("Período", period_options, index=0)

# Load Data
with st.spinner("Cargando datos..."):
    try:
        # Get financial summary
        financial = connector.get_financial_summary()
        summary = financial.get("summary", {})
        
        # Get profit and loss data
        pl_data = connector.get_profit_loss_data()
        
        # Load monthly revenue data for trends
        monthly_revenue = connector.get_monthly_revenue()
        
        # Get combined data for additional metrics
        combined_data = connector.get_combined_metrics()
        
        if not summary and pl_data.empty:
            st.error("No se pudo cargar la información financiera")
            st.stop()
        
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        st.stop()

# Key Financial Metrics Section
st.markdown('<h2>Métricas Financieras Clave</h2>', unsafe_allow_html=True)

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
    # Total Costs
    total_costs = summary.get("total_costs", 0)
    create_kpi_card(
        "Costos Totales", 
        total_costs,
        is_currency=True,
        icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line></svg>'
    )

with col3:
    # Gross Profit
    gross_profit = summary.get("gross_profit", 0)
    create_kpi_card(
        "Ganancia Bruta", 
        gross_profit,
        is_currency=True,
        icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>'
    )

with col4:
    # Gross Margin
    gross_margin = summary.get("gross_margin_percentage", 0)
    create_kpi_card(
        "Margen Bruto", 
        gross_margin,
        subtitle="Porcentaje de ganancia sobre ingresos",
        icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>'
    )

# Profit & Loss Waterfall Chart - With Error Handling
st.markdown('<h2>Estado de Resultados</h2>', unsafe_allow_html=True)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
if not pl_data.empty and "concepto" in pl_data.columns:
    # Check if we have the consolidated column
    consolidado_col = None
    for col in pl_data.columns:
        if col.upper() == "CONSOLIDADO" or "CONSOLID" in col.upper():
            consolidado_col = col
            break
    
    if consolidado_col:
        try:
            # Create a simplified dataset for the waterfall chart to avoid the error
            waterfall_data = []
            
            # Define key labels to look for
            key_items = [
                "Total Ingresos", "Ingresos Totales", "Total Revenue",
                "Total Costos", "Costos Totales", "Total Costs",
                "GROSS PROFIT", "Ganancia Bruta", "Utilidad Bruta",
                "Gastos de Ventas", "Ventas", "Sales", 
                "Gastos Administrativos", "Administrativos", "Administrative",
                "RESULTADO OPERATIVO", "Resultado Operacional", "Operating Result",
                "RESULTADO NETO", "Resultado Neto", "Net Result"
            ]
            
            # Find rows with these key labels
            found_items = []
            for key_label in key_items:
                for idx, row in pl_data.iterrows():
                    concept = row.get("concepto", "")
                    if isinstance(concept, str) and key_label.lower() in concept.lower():
                        value = row.get(consolidado_col, 0)
                        if pd.notna(value):
                            found_items.append({
                                "name": concept,
                                "value": float(value)
                            })
                            break  # Found one match for this key label, move to next
            
            if found_items:
                # Create custom waterfall chart with bar chart
                st.markdown('<div class="chart-title">Análisis de Estado de Resultados</div>', unsafe_allow_html=True)
                
                waterfall_df = pd.DataFrame(found_items)
                
                # Sort items if needed - typically revenue first, then costs, etc.
                if len(waterfall_df) > 1:
                    # Create a custom waterfall chart from scratch to avoid errors
                    fig = go.Figure()
                    
                    # Add bars for each item
                    for i, row in waterfall_df.iterrows():
                        # Determine color based on the name or value
                        if "ingreso" in row["name"].lower() or "revenue" in row["name"].lower():
                            color = COLORS['secondary']
                        elif "costo" in row["name"].lower() or "cost" in row["name"].lower() or "gasto" in row["name"].lower() or "expense" in row["name"].lower():
                            color = COLORS['danger']
                        elif "bruta" in row["name"].lower() or "gross" in row["name"].lower() or "profit" in row["name"].lower() or "neto" in row["name"].lower() or "net" in row["name"].lower():
                            color = COLORS['success']
                        else:
                            color = COLORS['info']
                        
                        # Add bar
                        fig.add_trace(go.Bar(
                            x=[row["name"]],
                            y=[row["value"]],
                            marker_color=color,
                            textposition="outside",
                            text=[f"${row['value']:,.0f}"],
                            name=row["name"]
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
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay suficientes datos para generar un gráfico cascada")
            else:
                st.info("No se encontraron los elementos clave del estado de resultados")
        except Exception as e:
            st.error(f"Error al crear el gráfico de cascada: {str(e)}")
            st.info("Los datos del estado de resultados están disponibles pero no se pudieron visualizar en el gráfico.")
    else:
        st.info("No hay datos consolidados disponibles para el estado de resultados")
else:
    st.info("No hay datos de estado de resultados disponibles")
st.markdown('</div>', unsafe_allow_html=True)

# Profit & Loss Detailed Analysis
st.markdown('<h2>Análisis Detallado de Estado de Resultados</h2>', unsafe_allow_html=True)

if not pl_data.empty and "concepto" in pl_data.columns:
    # Check available columns (excluding 'concepto')
    month_cols = [col for col in pl_data.columns if col != "concepto"]
    
    if month_cols:
        # Group P&L items by category for tabs
        # First, create a clean version of the data
        clean_pl_data = pl_data.copy()
        
        # Handle potential non-numeric values in numeric columns
        for col in month_cols:
            clean_pl_data[col] = pd.to_numeric(clean_pl_data[col], errors='coerce')
        
        # Try to identify different sections in the P&L data
        income_keywords = ["ingreso", "venta", "revenue", "income", "venta"]
        cost_keywords = ["costo", "cost", "gasto directo", "direct expense"]
        expense_keywords = ["gasto", "expense", "operating expense"]
        
        # Create a function to check if a concept contains any of the keywords
        def contains_keyword(concept, keywords):
            if not isinstance(concept, str):
                return False
            concept_lower = concept.lower()
            return any(keyword in concept_lower for keyword in keywords)
        
        # Group items
        income_items = clean_pl_data[clean_pl_data["concepto"].apply(lambda x: contains_keyword(x, income_keywords))]
        cost_items = clean_pl_data[clean_pl_data["concepto"].apply(lambda x: contains_keyword(x, cost_keywords))]
        expense_items = clean_pl_data[clean_pl_data["concepto"].apply(lambda x: contains_keyword(x, expense_keywords))]
        
        # If any of these are empty, try alternative grouping
        if income_items.empty and cost_items.empty and expense_items.empty:
            # Try to group by position in the dataframe
            total_rows = len(clean_pl_data)
            income_items = clean_pl_data.iloc[:total_rows//3]
            cost_items = clean_pl_data.iloc[total_rows//3:2*total_rows//3]
            expense_items = clean_pl_data.iloc[2*total_rows//3:]
        
        # Create tabs for different sections with enhanced styling
        tab1, tab2, tab3 = st.tabs(["Ingresos", "Costos", "Gastos"])
        
        with tab1:
            if not income_items.empty:
                st.subheader("Análisis de Ingresos")
                
                # Check if we have the consolidated column
                if "CONSOLIDADO" in income_items.columns:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    # Create bar chart for income items with enhanced styling
                    income_items_sorted = income_items.sort_values("CONSOLIDADO", ascending=False)
                    
                    st.markdown('<div class="chart-title">Desglose de Ingresos</div>', unsafe_allow_html=True)
                    
                    fig = px.bar(
                        income_items_sorted,
                        x="concepto",
                        y="CONSOLIDADO",
                        color="CONSOLIDADO",
                        color_continuous_scale=[[0, COLORS['info']], [0.5, COLORS['accent3']], [1, COLORS['secondary']]],
                        labels={"CONSOLIDADO": "Monto ($)", "concepto": "Categoría"}
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
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Show income data table with enhanced styling
                st.markdown('<div class="chart-container" style="padding: 0;">', unsafe_allow_html=True)
                st.dataframe(income_items, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No hay datos de ingresos disponibles")
        
        with tab2:
            if not cost_items.empty:
                st.subheader("Análisis de Costos")
                
                # Create bar chart for cost items with enhanced styling
                if "CONSOLIDADO" in cost_items.columns:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    cost_items_sorted = cost_items.sort_values("CONSOLIDADO", ascending=False)
                    
                    st.markdown('<div class="chart-title">Desglose de Costos</div>', unsafe_allow_html=True)
                    
                    fig = px.bar(
                        cost_items_sorted,
                        x="concepto",
                        y="CONSOLIDADO",
                        color="CONSOLIDADO",
                        color_continuous_scale=[[0, COLORS['info']], [0.5, COLORS['danger']], [1, COLORS['accent1']]],
                        labels={"CONSOLIDADO": "Monto ($)", "concepto": "Categoría"}
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
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Show cost data table with enhanced styling
                st.markdown('<div class="chart-container" style="padding: 0;">', unsafe_allow_html=True)
                st.dataframe(cost_items, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No hay datos de costos disponibles")
        
        with tab3:
            if not expense_items.empty:
                st.subheader("Análisis de Gastos")
                
                # Create bar chart for expense items with enhanced styling
                if "CONSOLIDADO" in expense_items.columns:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    expense_items_sorted = expense_items.sort_values("CONSOLIDADO", ascending=False)
                    
                    st.markdown('<div class="chart-title">Desglose de Gastos</div>', unsafe_allow_html=True)
                    
                    fig = px.bar(
                        expense_items_sorted,
                        x="concepto",
                        y="CONSOLIDADO",
                        color="CONSOLIDADO",
                        color_continuous_scale=[[0, COLORS['info']], [0.5, COLORS['accent2']], [1, COLORS['secondary']]],
                        labels={"CONSOLIDADO": "Monto ($)", "concepto": "Categoría"}
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
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Show expense data table with enhanced styling
                st.markdown('<div class="chart-container" style="padding: 0;">', unsafe_allow_html=True)
                st.dataframe(expense_items, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No hay datos de gastos disponibles")
    else:
        st.info("No hay datos mensuales disponibles")
else:
    st.info("No hay datos de estado de resultados disponibles")

# Monthly Financial Trends
st.markdown('<h2>Tendencias Financieras Mensuales</h2>', unsafe_allow_html=True)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
if not pl_data.empty and not monthly_revenue.empty:
    # Get monthly columns (excluding 'concepto' and 'CONSOLIDADO')
    month_cols = [col for col in pl_data.columns if col not in ["concepto", "CONSOLIDADO"]]
    
    if month_cols:
        try:
            # Find key financial metrics for monthly trends
            metrics_to_find = [
                {"keywords": ["Total Ingresos", "Ingresos Totales", "Total Revenue"], "name": "Ingresos", "color": COLORS["secondary"]},
                {"keywords": ["Total Costos", "Costos Totales", "Total Costs"], "name": "Costos", "color": COLORS["danger"]},
                {"keywords": ["GROSS PROFIT", "Ganancia Bruta", "Utilidad Bruta"], "name": "Ganancia Bruta", "color": COLORS["success"]}
            ]
            
            # Function to find a row that matches any of the keywords
            def find_matching_row(keywords):
                for keyword in keywords:
                    matching_rows = pl_data[pl_data["concepto"].str.contains(keyword, case=False, na=False)]
                    if not matching_rows.empty:
                        return matching_rows.iloc[0]
                return None
            
            # Create monthly trend data
            trend_data = []
            
            # For each metric, find the matching row and extract monthly values
            for metric in metrics_to_find:
                row = find_matching_row(metric["keywords"])
                if row is not None:
                    for month in month_cols:
                        if pd.notna(row[month]):
                            trend_data.append({
                                "month": month,
                                "metric": metric["name"],
                                "value": float(row[month]),
                                "color": metric["color"]
                            })
            
            if trend_data:
                # Convert to DataFrame
                trend_df = pd.DataFrame(trend_data)
                
                st.markdown('<div class="chart-title">Tendencias Mensuales Financieras</div>', unsafe_allow_html=True)
                
                # Create multi-line chart with enhanced styling
                fig = px.line(
                    trend_df,
                    x="month",
                    y="value",
                    color="metric",
                    labels={"value": "Monto ($)", "month": "Mes", "metric": "Métrica"},
                    color_discrete_map={
                        "Ingresos": COLORS["secondary"],
                        "Costos": COLORS["danger"],
                        "Ganancia Bruta": COLORS["success"]
                    }
                )
                
                # Update line and marker styles for a more professional look
                for i in range(len(fig.data)):
                    fig.data[i].update(
                        mode='lines+markers',
                        line=dict(
                            width=3,
                            shape='spline' # Smooth curves
                        ),
                        marker=dict(
                            size=8,
                            line=dict(
                                width=1,
                                color='white'
                            )
                        )
                    )
                
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
                    hovermode="x unified",
                    hoverlabel=dict(
                        bgcolor=COLORS['panel_bg'],
                        font_size=12,
                        font_family="Inter, sans-serif",
                        bordercolor='rgba(255,255,255,0.1)'
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate monthly margins if possible
                if "Ingresos" in trend_df["metric"].values and "Ganancia Bruta" in trend_df["metric"].values:
                    margin_data = []
                    months = trend_df["month"].unique()
                    
                    for month in months:
                        month_data = trend_df[trend_df["month"] == month]
                        revenue = month_data[month_data["metric"] == "Ingresos"]["value"].values
                        profit = month_data[month_data["metric"] == "Ganancia Bruta"]["value"].values
                        
                        if len(revenue) > 0 and len(profit) > 0 and revenue[0] > 0:
                            margin = (profit[0] / revenue[0] * 100)
                            margin_data.append({
                                "month": month,
                                "margin": margin
                            })
                    
                    if margin_data:
                        margin_df = pd.DataFrame(margin_data)
                        
                        # Create margin trend chart with enhanced styling
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        
                        # Use the new enhanced margin trend chart
                        fig = create_margin_trend_chart(
                            margin_df,
                            title="Tendencia de Margen Bruto Mensual"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se pudieron encontrar métricas financieras clave para mostrar tendencias")
        except Exception as e:
            st.error(f"Error al crear gráficos de tendencias: {str(e)}")
            st.info("No se pudieron visualizar las tendencias mensuales")
    else:
        st.info("No hay datos mensuales disponibles para tendencias")
else:
    st.info("No hay datos suficientes para mostrar tendencias financieras")
st.markdown('</div>', unsafe_allow_html=True)

# Full P&L Statement
st.markdown('<h2>Estado de Resultados Completo</h2>', unsafe_allow_html=True)

if not pl_data.empty:
    # Prepare data for display
    display_df = pl_data.copy()
    
    # Format numeric columns as currency
    numeric_cols = display_df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        display_df[col] = display_df[col].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
        )
    
    # Display the full P&L table with enhanced styling
    st.markdown('<div class="chart-container" style="padding: 0;">', unsafe_allow_html=True)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export options
    col1, col2 = st.columns([3, 1])
    with col2:
        st.download_button(
            label="Exportar a CSV",
            data=display_df.to_csv(index=False).encode('utf-8'),
            file_name="activagroup_resultados.csv",
            mime="text/csv",
            help="Descargar el estado de resultados en formato CSV"
        )
else:
    st.info("No hay datos de estado de resultados disponibles")

# Footer with modern styling
st.markdown("""
<div class="footer">
    <p>ActivaGroup Business Intelligence Dashboard © 2025</p>
</div>
""", unsafe_allow_html=True)
