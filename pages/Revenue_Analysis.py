"""
ActivaGroup Business Intelligence Dashboard
Revenue Analysis Page
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

# Check if user is logged in (if using login system)
if "logged_in" in st.session_state and not st.session_state.logged_in:
    st.warning("Por favor inicie sesión para acceder al dashboard")
    st.stop()

# Page header with smaller bottom margin
st.markdown("""
    <h1 style='margin-bottom:0.5rem;'>Análisis de Ingresos</h1>
    <p style='margin-bottom:2rem;'>Análisis detallado de ingresos, tendencias y distribución</p>
""", unsafe_allow_html=True)

# Add simple navigation tabs
st.markdown("""
    <div style="display: flex; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
        <a href="/dashboard" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;">Dashboard</a>
        <a href="/Client_Overview" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;">Visión de Clientes</a>
        <a href="/Revenue_Analysis" target="_self" style="color: white; text-decoration: none; padding: 8px 16px; margin-right: 8px; background: rgba(243, 111, 33, 0.2); border-bottom: 2px solid #F36F21; border-radius: 4px 4px 0 0;">Análisis de Ingresos</a>
        <a href="/Budget_Management" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px; margin-right: 8px;">Gestión de Presupuesto</a>
        <a href="/Financial_Performance" target="_self" style="color: rgba(255,255,255,0.7); text-decoration: none; padding: 8px 16px;">Rendimiento Financiero</a>
    </div>
""", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.title("Filtros")

# Load Data
with st.spinner("Cargando datos..."):
    try:
        # Get financial summary
        financial = connector.get_financial_summary()
        summary = financial.get("summary", {})
        
        # Get monthly revenue
        monthly_revenue = connector.get_monthly_revenue()
        
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

# Key Revenue Metrics
st.header("Métricas de Ingresos")

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
    # Average Monthly Revenue
    if not monthly_revenue.empty and "revenue" in monthly_revenue.columns:
        avg_monthly = monthly_revenue["revenue"].mean()
        create_kpi_card(
            "Promedio Mensual", 
            avg_monthly,
            is_currency=True
        )
    else:
        create_kpi_card(
            "Promedio Mensual", 
            "N/A",
            is_currency=True
        )

with col3:
    # Revenue per Client
    if "facturacion_x" in df.columns and len(df) > 0:
        revenue_per_client = df["facturacion_x"].sum() / len(df)
        create_kpi_card(
            "Ingreso por Cliente", 
            revenue_per_client,
            is_currency=True
        )
    else:
        create_kpi_card(
            "Ingreso por Cliente", 
            "N/A",
            is_currency=True
        )

with col4:
    # Top Client Contribution
    if "facturacion_x" in df.columns and len(df) > 0:
        total_facturacion = df["facturacion_x"].sum()
        if total_facturacion > 0:
            top_client_revenue = df["facturacion_x"].max()
            top_client_pct = (top_client_revenue / total_facturacion * 100)
            create_kpi_card(
                "Contrib. Cliente Principal", 
                top_client_pct,
                subtitle=f"${top_client_revenue:,.0f}"
            )
        else:
            create_kpi_card(
                "Contrib. Cliente Principal", 
                "N/A"
            )
    else:
        create_kpi_card(
            "Contrib. Cliente Principal", 
            "N/A"
        )

# Monthly Revenue Analysis
st.header("Análisis de Ingresos Mensuales")

if not monthly_revenue.empty and "revenue" in monthly_revenue.columns:
    # Create line chart for monthly revenue trend
    fig = px.line(
        monthly_revenue,
        x="month",
        y="revenue",
        markers=True,
        title="Tendencia de Ingresos Mensuales",
        labels={"revenue": "Ingresos ($)", "month": "Mes"}
    )
    
    # Update styling for dark theme
    fig.update_traces(
        line=dict(color=COLORS['secondary'], width=3),
        marker=dict(size=8, color=COLORS['secondary']),
        fill='tozeroy',
        fillcolor=f'rgba(243, 111, 33, 0.1)'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(
            showgrid=False,
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
    
    # Monthly statistics
    st.subheader("Estadísticas Mensuales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Highest month
        if len(monthly_revenue) > 0:
            max_idx = monthly_revenue["revenue"].idxmax()
            max_month = monthly_revenue.loc[max_idx]
            create_kpi_card(
                "Mes con Mayor Ingreso", 
                max_month.get("month", "N/A"),
                subtitle=f"${max_month.get('revenue', 0):,.0f}"
            )
        else:
            create_kpi_card(
                "Mes con Mayor Ingreso", 
                "N/A"
            )
    
    with col2:
        # Lowest month
        if len(monthly_revenue) > 0:
            min_idx = monthly_revenue["revenue"].idxmin()
            min_month = monthly_revenue.loc[min_idx]
            create_kpi_card(
                "Mes con Menor Ingreso", 
                min_month.get("month", "N/A"),
                subtitle=f"${min_month.get('revenue', 0):,.0f}"
            )
        else:
            create_kpi_card(
                "Mes con Menor Ingreso", 
                "N/A"
            )
    
    with col3:
        # Monthly Growth
        if len(monthly_revenue) >= 2:
            # Calculate month-over-month growth if we have a month_order column
            if "month_order" in monthly_revenue.columns:
                monthly_revenue_sorted = monthly_revenue.sort_values("month_order")
                monthly_revenue_sorted["prev_revenue"] = monthly_revenue_sorted["revenue"].shift(1)
                # Avoid division by zero
                monthly_revenue_sorted["growth"] = monthly_revenue_sorted.apply(
                    lambda x: ((x["revenue"] - x["prev_revenue"]) / x["prev_revenue"] * 100) if x["prev_revenue"] > 0 else 0, 
                    axis=1
                )
                
                # Calculate average growth (excluding NaN from first month)
                avg_growth = monthly_revenue_sorted["growth"].mean()
                create_kpi_card(
                    "Crecimiento Promedio", 
                    avg_growth,
                    subtitle="Promedio mensual"
                )
            else:
                create_kpi_card(
                    "Crecimiento Promedio", 
                    "N/A"
                )
        else:
            create_kpi_card(
                "Crecimiento Promedio", 
                "N/A"
            )
else:
    st.info("No hay datos de ingresos mensuales disponibles")

# Revenue Distribution Analysis
st.header("Distribución de Ingresos")

col1, col2 = st.columns(2)

with col1:
    # Revenue by Industry
    if not industry_breakdown.empty:
        # Create pie chart
        fig = px.pie(
            industry_breakdown,
            values="revenue",
            names="industry",
            title="Distribución de Ingresos por Industria",
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
            hovertemplate='<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de distribución por industria disponibles")

with col2:
    # Client Concentration
    if "facturacion_x" in df.columns and len(df) > 0:
        # Create client concentration data
        total_revenue = df["facturacion_x"].sum()
        
        if total_revenue > 0:
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
            
            # Create funnel chart
            fig = px.funnel(
                concentration_data,
                x="revenue",
                y="category",
                title="Concentración de Ingresos por Clientes",
                color_discrete_sequence=[COLORS["primary"], COLORS["secondary"], COLORS["teal"], COLORS["purple"]]
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=60, b=20),
                font=dict(family="Arial", size=12, color=COLORS['text']),
                title_font=dict(size=16, color=COLORS['text']),
                yaxis=dict(categoryarray=["Otros Clientes", "Clientes 11-20", "Clientes 6-10", "Top 5 Clientes"])
            )
            
            # Format hover template with percentages
            percentages = (concentration_data["revenue"] / total_revenue * 100).round(1)
            hover_templates = []
            
            for i, row in concentration_data.iterrows():
                pct = percentages.iloc[i]
                template = f'<b>{row["category"]}</b><br>${row["revenue"]:,.0f}<br>{pct:.1f}% del total'
                hover_templates.append(template)
            
            for i, template in enumerate(hover_templates):
                fig.data[0].hovertemplate = template
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay suficientes datos para mostrar la concentración de ingresos")
    else:
        st.info("No hay datos suficientes para mostrar la concentración de clientes")

# Top Clients by Revenue
st.header("Clientes Principales por Ingresos")

if "facturacion_x" in df.columns and len(df) > 0:
    # Get top 15 clients
    top_clients = df.nlargest(15, "facturacion_x")[["cliente", "industria", "facturacion_x"]]
    
    # Create horizontal bar chart
    fig = px.bar(
        top_clients,
        y="cliente",
        x="facturacion_x",
        color="industria",
        title="Top 15 Clientes por Ingresos",
        labels={"facturacion_x": "Ingresos ($)", "cliente": "Cliente", "industria": "Industria"},
        color_discrete_sequence=CHART_COLORS,
        orientation="h"
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=60),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="Ingresos ($)",
            tickprefix="$",
            tickformat=",",
            color=COLORS['text']
        ),
        yaxis=dict(
            showgrid=False,
            title="",
            categoryorder="total ascending",
            color=COLORS['text']
        ),
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=-0.2, 
            xanchor="center", 
            x=0.5,
            title="",
            font=dict(color=COLORS['text'])
        ),
        font=dict(family="Arial", size=12, color=COLORS['text']),
        title_font=dict(size=16, color=COLORS['text'])
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hay datos suficientes para mostrar los clientes principales")

# Revenue Table - Detailed breakdown
st.header("Detalles de Ingresos por Cliente")

# Prepare revenue data for display
if "facturacion_x" in df.columns and len(df) > 0:
    # Add search box for filtering the table
    search_term = st.text_input("Buscar Cliente", "")
    
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
        file_name="activagroup_ingresos.csv",
        mime="text/csv",
        help="Descargar la tabla de ingresos en formato CSV"
    )
else:
    st.info("No hay datos de ingresos disponibles")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: rgba(255,255,255,0.5); font-size: 0.8rem;">
    <p>ActivaGroup Business Intelligence Dashboard © 2025</p>
</div>
""", unsafe_allow_html=True)
