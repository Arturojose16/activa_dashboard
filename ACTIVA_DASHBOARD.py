import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="ActivaGroup Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR CON LOGO Y NAVEGACIÓN ---
with st.sidebar:
    logo = Image.open("/Users/ajcamarena/Desktop/activa_dashboard/Screenshot_Activa_Logo.png")  # ✅ Make sure this matches your logo file
    st.image(logo, width=200)
    st.markdown("### Bienvenido, Activa Team 👋", unsafe_allow_html=True)
    st.markdown("---")
    nav = st.radio("Navegación", ["Dashboard", "Analytics", "AI Assistant"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("#### ⚙️ Configuración")
    st.markdown("Arturo Camarena  \narturo@ie.edu")

# --- DATOS FICTICIOS PARA DEMO ---
df = pd.DataFrame({
    "Month": pd.date_range(start="2024-01-01", periods=6, freq="MS"),  # Fixed future warning
    "Revenue": [25000000, 30000000, 28000000, 35000000, 38000000, 40000000],
    "Costs": [15000000, 18000000, 16000000, 20000000, 22000000, 23000000],
    "Unit": ["BTL", "Eventos", "BTL", "Digital", "Eventos", "BTL"]
})

# --- ENCABEZADO + BUSCADOR ---
st.markdown("<h1 style='color:#f36f21;'>📊 ActivaGroup Dashboard</h1>", unsafe_allow_html=True)
search_query = st.text_input("🔍 Escribe una pregunta, por ejemplo: '¿Cuál fue el ingreso en Q1 2024?'", "")

# --- KPIs SUPERIORES ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Ingresos", f"${df['Revenue'].sum():,.0f}")
col2.metric("Total Costos", f"${df['Costs'].sum():,.0f}")
col3.metric("Ganancia Neta", f"${df['Revenue'].sum() - df['Costs'].sum():,.0f}")

# --- GRÁFICO DE LÍNEAS: INGRESOS VS COSTOS ---
st.markdown("### 📈 Tendencia de Ingresos vs Costos")
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=df["Month"], y=df["Revenue"], mode='lines+markers',
    name='Ingresos', line=dict(color='#f36f21')
))
fig_line.add_trace(go.Scatter(
    x=df["Month"], y=df["Costs"], mode='lines+markers',
    name='Costos', line=dict(color='#003366')
))
fig_line.update_layout(margin=dict(l=20, r=20, t=30, b=20), template="plotly_dark", height=350)
st.plotly_chart(fig_line, use_container_width=True)

# --- GRÁFICO DE BARRAS: INGRESOS POR UNIDAD ---
st.markdown("### 📊 Ingresos por Unidad de Negocio")
fig_bar = px.bar(
    df, x="Unit", y="Revenue", color="Unit",
    template="plotly_dark",
    color_discrete_sequence=["#f36f21", "#006699", "#003366"]
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- BOTÓN DEL ASISTENTE DE IA ---
if st.button("🤖 Activar Asistente de IA"):
    st.info("Aquí se integrará un asistente de inteligencia artificial para consultar datos empresariales.")