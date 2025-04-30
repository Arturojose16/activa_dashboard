"""
ActivaGroup Business Intelligence Dashboard
Financial Performance Page
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
    create_kpi_card, apply_dark_theme
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

# Page header with smaller bottom margin
st.markdown("""
    <h1 style='margin-bottom:0.5rem;'>Rendimiento Financiero</h1>
    <p style='margin-bottom:2rem;'>Análisis detallado del desempeño financiero y métricas clave</p>
""", unsafe_allow_html=True)

# Add simple navigation tabs
st.markdown("""
    <div style="display: flex; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
        <a href="/dashboard" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;">Dashboard</a>
        <a href="/Client_Overview" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;">Visión de Clientes</a>
        <a href="/Revenue_Analysis" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;">Análisis de Ingresos</a>
        <a href="/Budget_Management" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;">Gestión de Presupuesto</a>
        <a href="/Financial_Performance" target="_self" style="color: white; text-decoration: none; padding: 8px 16px; background: rgba(243, 111, 33, 0.2); border-bottom: 2px solid #F36F21; border-radius: 4px 4px 0 0;">Rendimiento Financiero</a>
    </div>
""", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.title("Filtros")

# Add time period filter (placeholder)
period_options = ["2025 (Acumulado)", "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"]
selected_period = st.sidebar.selectbox("Período", period_options, index=0)

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

# Key Financial Metrics
st.header("Métricas Financieras Clave")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Total Revenue
    total_revenue = summary.get("total_income", 0)
    create_kpi_card(
        "Ingresos Totales", 
        total_revenue,
        is_currency=True
    )

with col2:
    # Total Costs
    total_costs = summary.get("total_costs", 0)
    create_kpi_card(
        "Costos Totales", 
        total_costs,
        is_currency=True
    )

with col3:
    # Gross Profit
    gross_profit = summary.get("gross_profit", 0)
    create_kpi_card(
        "Ganancia Bruta", 
        gross_profit,
        is_currency=True
    )

with col4:
    # Gross Margin
    gross_margin = summary.get("gross_margin_percentage", 0)
    create_kpi_card(
        "Margen Bruto", 
        gross_margin,
        subtitle="Porcentaje de ganancia sobre ingresos"
    )

# Profit & Loss Waterfall Chart - With Error Handling
st.header("Estado de Resultados")

if not pl_data.empty and "concepto" in pl_data.columns:
    # Check if we have the consolidated column
    consolidado_col = None
    for col in pl_data.columns:
        if col.upper() == "CONSOLIDADO" or "CONSOLID" in col.upper():
            consolidado_col = col
            break
    
    if consolidado_col:
        try:
            # Prepare data for waterfall chart - this is where the error was happening
            # We need to create a clean DataFrame with non-null values
            
            # Key items to look for in the P&L statement
            key_items = [
                "Total Ingresos", "Ingresos Totales", "Total Revenue",
                "Total Costos", "Costos Totales", "Total Costs", 
                "GROSS PROFIT", "Ganancia Bruta", "Utilidad Bruta",
                "Gastos de Ventas", "Ventas", "Sales",
                "Gastos Administrativos", "Administrativos", "Administrative",
                "RESULTADO OPERATIVO", "Resultado Operacional", "Operating Result",
                "RESULTADO NETO", "Resultado Neto", "Net Result"
            ]
            
            # Try to find these key items using partial matching
            waterfall_rows = []
            
            for item_name in key_items:
                # Using str.contains with case=False for partial, case-insensitive matching
                # Also handling NaN values with na=False
                matching_rows = pl_data[pl_data["concepto"].str.contains(item_name, case=False, na=False)]
                
                if not matching_rows.empty:
                    # Take first matching row
                    row_data = matching_rows.iloc[0]
                    
                    # Only add if the consolidado value is not null
                    if pd.notna(row_data[consolidado_col]):
                        waterfall_rows.append({
                            "name": row_data["concepto"],
                            "value": float(row_data[consolidado_col])  # Convert to float to avoid type issues
                        })
            
            if waterfall_rows:
                # Create DataFrame for waterfall chart
                waterfall_df = pd.DataFrame(waterfall_rows)
                
                # Create waterfall chart
                fig = go.Figure(go.Waterfall(
                    name="Waterfall",
                    orientation="v",
                    measure=["total"] + ["relative"] * (len(waterfall_df) - 2) + ["total"],
                    x=waterfall_df["name"],
                    textposition="outside",
                    text=[f"${x:,.0f}" for x in waterfall_df["value"]],
                    y=waterfall_df["value"],
                    connector={"line": {"color": "rgb(255, 255, 255, 0.5)"}},
                    decreasing={"marker": {"color": COLORS['danger']}},
                    increasing={"marker": {"color": COLORS['success']}},
                    totals={"marker": {"color": COLORS['secondary']}}
                ))
                
                fig.update_layout(
                    title="Análisis de Estado de Resultados",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=40, r=40, t=60, b=60),
                    showlegend=False,
                    xaxis=dict(
                        showgrid=False,
                        title="",
                        color=COLORS['text']
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(255,255,255,0.1)',
                        title="Monto ($)",
                        tickprefix="$",
                        tickformat=",",
                        color=COLORS['text']
                    ),
                    font=dict(family="Arial", size=12, color=COLORS['text']),
                    title_font=dict(size=16, color=COLORS['text'])
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se encontraron elementos clave para el gráfico de cascada")
        except Exception as e:
            st.error(f"Error al crear el gráfico de cascada: {str(e)}")
            st.info("Los datos del estado de resultados están disponibles pero no se pudieron visualizar en el gráfico.")
    else:
        st.info("No hay datos consolidados disponibles para el estado de resultados")
else:
    st.info("No hay datos de estado de resultados disponibles")

# Profit & Loss Detailed Analysis
st.header("Análisis Detallado de Estado de Resultados")

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
        
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["Ingresos", "Costos", "Gastos"])
        
        with tab1:
            if not income_items.empty:
                st.subheader("Análisis de Ingresos")
                
                # Check if we have the consolidated column
                if "CONSOLIDADO" in income_items.columns:
                    # Create bar chart for income items
                    income_items_sorted = income_items.sort_values("CONSOLIDADO", ascending=False)
                    
                    fig = px.bar(
                        income_items_sorted,
                        x="concepto",
                        y="CONSOLIDADO",
                        title="Desglose de Ingresos",
                        color="CONSOLIDADO",
                        color_continuous_scale=px.colors.sequential.Blues,
                        labels={"CONSOLIDADO": "Monto ($)", "concepto": "Categoría"}
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
                            title="Monto ($)",
                            tickprefix="$",
                            tickformat=",",
                            color=COLORS['text']
                        ),
                        coloraxis_showscale=False,
                        font=dict(family="Arial", size=12, color=COLORS['text']),
                        title_font=dict(size=16, color=COLORS['text'])
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Show income data table
                st.dataframe(income_items, use_container_width=True, hide_index=True)
            else:
                st.info("No hay datos de ingresos disponibles")
        
        with tab2:
            if not cost_items.empty:
                st.subheader("Análisis de Costos")
                
                # Create bar chart for cost items
                if "CONSOLIDADO" in cost_items.columns:
                    cost_items_sorted = cost_items.sort_values("CONSOLIDADO", ascending=False)
                    
                    fig = px.bar(
                        cost_items_sorted,
                        x="concepto",
                        y="CONSOLIDADO",
                        title="Desglose de Costos",
                        color="CONSOLIDADO",
                        color_continuous_scale=px.colors.sequential.Reds,
                        labels={"CONSOLIDADO": "Monto ($)", "concepto": "Categoría"}
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
                            title="Monto ($)",
                            tickprefix="$",
                            tickformat=",",
                            color=COLORS['text']
                        ),
                        coloraxis_showscale=False,
                        font=dict(family="Arial", size=12, color=COLORS['text']),
                        title_font=dict(size=16, color=COLORS['text'])
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Show cost data table
                st.dataframe(cost_items, use_container_width=True, hide_index=True)
            else:
                st.info("No hay datos de costos disponibles")
        
        with tab3:
            if not expense_items.empty:
                st.subheader("Análisis de Gastos")
                
                # Create bar chart for expense items
                if "CONSOLIDADO" in expense_items.columns:
                    expense_items_sorted = expense_items.sort_values("CONSOLIDADO", ascending=False)
                    
                    fig = px.bar(
                        expense_items_sorted,
                        x="concepto",
                        y="CONSOLIDADO",
                        title="Desglose de Gastos",
                        color="CONSOLIDADO",
                        color_continuous_scale=px.colors.sequential.Oranges,
                        labels={"CONSOLIDADO": "Monto ($)", "concepto": "Categoría"}
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
                            title="Monto ($)",
                            tickprefix="$",
                            tickformat=",",
                            color=COLORS['text']
                        ),
                        coloraxis_showscale=False,
                        font=dict(family="Arial", size=12, color=COLORS['text']),
                        title_font=dict(size=16, color=COLORS['text'])
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Show expense data table
                st.dataframe(expense_items, use_container_width=True, hide_index=True)
            else:
                st.info("No hay datos de gastos disponibles")
    else:
        st.info("No hay datos mensuales disponibles")
else:
    st.info("No hay datos de estado de resultados disponibles")

# Monthly Financial Trends
st.header("Tendencias Financieras Mensuales")

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
                
                # Create multi-line chart
                fig = px.line(
                    trend_df,
                    x="month",
                    y="value",
                    color="metric",
                    title="Tendencias Mensuales Financieras",
                    labels={"value": "Monto ($)", "month": "Mes", "metric": "Métrica"},
                    color_discrete_map={
                        "Ingresos": COLORS["secondary"],
                        "Costos": COLORS["danger"],
                        "Ganancia Bruta": COLORS["success"]
                    }
                )
                
                fig.update_traces(mode='lines+markers')
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=40, r=40, t=60, b=60),
                    xaxis=dict(
                        showgrid=False,
                        title="",
                        color=COLORS['text']
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(255,255,255,0.1)',
                        title="Monto ($)",
                        tickprefix="$",
                        tickformat=",",
                        color=COLORS['text']
                    ),
                    hovermode="x unified",
                    font=dict(family="Arial", size=12, color=COLORS['text']),
                    title_font=dict(size=16, color=COLORS['text']),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
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
                        
                        # Create margin trend chart
                        fig = px.line(
                            margin_df,
                            x="month",
                            y="margin",
                            title="Tendencia de Margen Bruto Mensual",
                            labels={"margin": "Margen Bruto (%)", "month": "Mes"}
                        )
                        
                        fig.update_traces(
                            line=dict(color=COLORS["primary"], width=3),
                            mode='lines+markers',
                            marker=dict(size=8, color=COLORS["primary"])
                        )
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=40, r=40, t=60, b=60),
                            xaxis=dict(
                                showgrid=False,
                                title="",
                                color=COLORS['text']
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(255,255,255,0.1)',
                                title="Margen Bruto (%)",
                                ticksuffix="%",
                                color=COLORS['text']
                            ),
                            hovermode="x unified",
                            font=dict(family="Arial", size=12, color=COLORS['text']),
                            title_font=dict(size=16, color=COLORS['text'])
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

# Full P&L Statement
st.header("Estado de Resultados Completo")

if not pl_data.empty:
    # Prepare data for display
    display_df = pl_data.copy()
    
    # Format numeric columns as currency
    numeric_cols = display_df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        display_df[col] = display_df[col].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
        )
    
    # Display the full P&L table
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Export options
    st.download_button(
        label="Exportar a CSV",
        data=display_df.to_csv(index=False).encode('utf-8'),
        file_name="activagroup_resultados.csv",
        mime="text/csv",
        help="Descargar el estado de resultados en formato CSV"
    )
else:
    st.info("No hay datos de estado de resultados disponibles")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: rgba(255,255,255,0.5); font-size: 0.8rem;">
    <p>ActivaGroup Business Intelligence Dashboard © 2025</p>
</div>
""", unsafe_allow_html=True)
