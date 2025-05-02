"""
ActivaGroup Business Intelligence Dashboard
Optimized AI Agent with Advanced Reasoning Capabilities
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sys
import json
import time
import re
import random
from typing import Dict, List, Tuple, Union, Any

# Add parent directory to path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import custom utilities
from utils.data_connector import ActivaDataConnector
from utils.visualization import (
    COLORS, CHART_COLORS, CHART_COLORS_TRANSPARENT,
    create_kpi_card, apply_dark_theme, create_dashboard_header,
    create_gauge_chart, create_revenue_line_chart, create_industry_pie_chart,
    create_top_clients_bar_chart, create_budget_vs_actual_chart
)

# Page configuration
st.set_page_config(
    page_title="AI Assistant - ActivaGroup",
    page_icon="🤖",
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

# Dashboard Header
create_dashboard_header(
    "ActivaGroup AI Assistant", 
    "Consulta y analiza los datos de tu empresa con inteligencia artificial"
)

# Modern Navigation Bar with active state
st.markdown("""
<div class="nav-container">
    <a href="/" class="nav-link">Dashboard</a>
    <a href="Client_Overview" class="nav-link">Visión de Clientes</a>
    <a href="Revenue_Analysis" class="nav-link">Análisis de Ingresos</a>
    <a href="Budget_Management" class="nav-link">Gestión de Presupuesto</a>
    <a href="Financial_Performance" class="nav-link">Rendimiento Financiero</a>
    <a href="AI_Agent" class="nav-link-active">AI Assistant</a>
</div>
""", unsafe_allow_html=True)

# Add custom styling
st.markdown("""
<style>
    /* Chat message styling */
    .user-message {
        background-color: rgba(58, 191, 248, 0.1);
        border-radius: 0 8px 8px 8px;
        padding: 12px 16px;
        margin-bottom: 15px;
        border-left: 3px solid #3ABFF8;
    }
    
    .assistant-message {
        background-color: rgba(243, 111, 33, 0.1);
        border-radius: 8px 0 8px 8px;
        padding: 12px 16px;
        margin-bottom: 15px;
        border-left: 3px solid #F36F21;
    }
    
    /* Insight cards */
    .ai-insight-card {
        background-color: #1A1C24;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.2s ease;
    }
    
    .ai-insight-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        border-color: rgba(243, 111, 33, 0.3);
    }
    
    .ai-insight-title {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 10px;
        color: white;
    }
    
    .ai-insight-value {
        font-size: 24px;
        font-weight: 700;
        color: #F36F21;
        margin-bottom: 5px;
    }
    
    .ai-insight-description {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.7);
    }
    
    /* Visualization container */
    .ai-viz-container {
        background-color: #1A1C24;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid rgba(58, 191, 248, 0.2);
        transition: all 0.2s ease;
    }
    
    .ai-viz-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        border-color: rgba(58, 191, 248, 0.4);
    }
    
    .ai-viz-title {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 15px;
        color: white;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 8px;
    }
    
    /* Highlight text */
    .ai-highlight {
        color: #F36F21;
        font-weight: 600;
    }
    
    /* Reasoning section styling */
    .reasoning-container {
        background-color: rgba(58, 191, 248, 0.05);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 15px 0;
        border-left: 3px solid #3ABFF8;
        font-style: italic;
        color: rgba(255, 255, 255, 0.8);
    }
    
    .reasoning-title {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
        color: #3ABFF8;
    }
    
    /* Data insights styling */
    .data-insight {
        background-color: rgba(243, 111, 33, 0.05);
        border-left: 3px solid #F36F21;
        padding: 8px 12px;
        margin: 8px 0;
        border-radius: 0 4px 4px 0;
    }
</style>
""", unsafe_allow_html=True)

# INTELLIGENT DATA ANALYZER WITH REASONING
class IntelligentDataAnalyzer:
    """
    Advanced data analyzer that not only loads data but also applies reasoning
    to generate insightful, non-template responses.
    """
    
    def __init__(self):
        """Initialize the analyzer and load data"""
        self.connector = get_connector()
        self.loaded = False
        self.load_data()
        
    def load_data(self):
        """Load all necessary data and process it once"""
        try:
            # Load financial summary
            financial = self.connector.get_financial_summary()
            self.financial_summary = financial.get("summary", {})
            
            # Load profit and loss data
            self.profit_loss_df = self.connector.get_profit_loss_data()
            
            # Extract monthly revenue data from P&L data if available
            monthly_revenue_df = None
            if not self.profit_loss_df.empty and "concepto" in self.profit_loss_df.columns:
                # Look for total revenue row in P&L data
                revenue_keywords = ["total ingreso", "ingresos totales", "total revenue", "revenue total"]
                total_revenue_row = None
                
                for keyword in revenue_keywords:
                    matches = self.profit_loss_df[self.profit_loss_df["concepto"].str.contains(keyword, case=False, na=False)]
                    if not matches.empty:
                        total_revenue_row = matches.iloc[0]
                        break
                
                if total_revenue_row is None:
                    # Try to find any row that has Total Ingresos
                    for idx, row in self.profit_loss_df.iterrows():
                        if "concepto" in row and isinstance(row["concepto"], str) and "total" in row["concepto"].lower() and "ingreso" in row["concepto"].lower():
                            total_revenue_row = row
                            break
                
                if total_revenue_row is not None:
                    # Find month columns (excluding 'concepto' and 'CONSOLIDADO')
                    month_cols = [col for col in self.profit_loss_df.columns if col not in ["concepto", "CONSOLIDADO"] and 
                                 not col.startswith("Unnamed:")]
                    
                    if month_cols:
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
                            if pd.isna(value) or not isinstance(value, (int, float, str)):
                                continue
                            
                            # Convert to float if it's a string
                            if isinstance(value, str):
                                try:
                                    value = float(value.replace(',', ''))
                                except ValueError:
                                    continue
                            
                            # Determine month order
                            month_name_upper = month.upper()
                            month_order_value = 0
                            
                            # Try to match the month name to get the order
                            for key, order in month_order.items():
                                if key in month_name_upper:
                                    month_order_value = order
                                    break
                            
                            # Use the month name as displayed in the data
                            month_display = month
                            
                            monthly_data.append({
                                "month": month_display,
                                "revenue": float(value),
                                "month_order": month_order_value
                            })
                        
                        # Convert to DataFrame
                        monthly_revenue_df = pd.DataFrame(monthly_data)
            
            # If extraction from P&L failed, fall back to the connector method
            if monthly_revenue_df is None or monthly_revenue_df.empty:
                self.monthly_revenue_df = self.connector.get_monthly_revenue()
            else:
                self.monthly_revenue_df = monthly_revenue_df
            
            # Load top clients
            self.top_clients_df = self.connector.get_top_clients(limit=50)
            
            # Load industry breakdown
            self.industry_df = self.connector.get_industry_breakdown()
            
            # Load budget vs actual
            self.budget_actual_df = self.connector.get_budget_vs_actual()
            
            # Process monthly revenue data
            if not self.monthly_revenue_df.empty:
                # Sort by month_order if it exists
                if "month_order" in self.monthly_revenue_df.columns:
                    self.monthly_revenue_df = self.monthly_revenue_df.sort_values("month_order")
                
                # Clean any non-numeric values
                if "revenue" in self.monthly_revenue_df.columns:
                    self.monthly_revenue_df["revenue"] = pd.to_numeric(self.monthly_revenue_df["revenue"], errors='coerce')
                    self.monthly_revenue_df = self.monthly_revenue_df.dropna(subset=["revenue"])
                
                if not self.monthly_revenue_df.empty and "revenue" in self.monthly_revenue_df.columns:
                    # Find highest and lowest months and cache values
                    highest_idx = self.monthly_revenue_df["revenue"].idxmax()
                    lowest_idx = self.monthly_revenue_df["revenue"].idxmin()
                    
                    if highest_idx is not None and highest_idx in self.monthly_revenue_df.index:
                        self.highest_month = self.monthly_revenue_df.loc[highest_idx]
                        self.highest_month_name = str(self.highest_month["month"])
                        self.highest_month_value = float(self.highest_month["revenue"])
                    else:
                        self.highest_month_name = "N/A"
                        self.highest_month_value = 0
                    
                    if lowest_idx is not None and lowest_idx in self.monthly_revenue_df.index:
                        self.lowest_month = self.monthly_revenue_df.loc[lowest_idx]
                        self.lowest_month_name = str(self.lowest_month["month"])
                        self.lowest_month_value = float(self.lowest_month["revenue"])
                    else:
                        self.lowest_month_name = "N/A"
                        self.lowest_month_value = 0
                    
                    # Calculate growth trends
                    self.monthly_revenue_df["prev_revenue"] = self.monthly_revenue_df["revenue"].shift(1)
                    self.monthly_revenue_df["growth_pct"] = self.monthly_revenue_df.apply(
                        lambda x: ((x["revenue"] - x["prev_revenue"]) / x["prev_revenue"] * 100) 
                        if pd.notna(x["prev_revenue"]) and x["prev_revenue"] > 0 
                        else None, 
                        axis=1
                    )
                    
                    # Calculate average monthly growth
                    growth_values = self.monthly_revenue_df["growth_pct"].dropna().tolist()
                    if growth_values:
                        self.avg_monthly_growth = round(sum(growth_values) / len(growth_values), 1)
                    else:
                        self.avg_monthly_growth = 0
                    
                    # Calculate total growth
                    if len(self.monthly_revenue_df) > 1:
                        first_month = self.monthly_revenue_df.iloc[0]
                        last_month = self.monthly_revenue_df.iloc[-1]
                        total_growth = last_month["revenue"] - first_month["revenue"]
                        if first_month["revenue"] > 0:
                            self.total_growth_pct = round((total_growth / first_month["revenue"] * 100), 1)
                        else:
                            self.total_growth_pct = 0
                    else:
                        self.total_growth_pct = 0
                else:
                    # Set default values if no revenue data
                    self.highest_month_name = "N/A"
                    self.highest_month_value = 0
                    self.lowest_month_name = "N/A"
                    self.lowest_month_value = 0
                    self.avg_monthly_growth = 0
                    self.total_growth_pct = 0
            else:
                # Set default values if no monthly data
                self.highest_month_name = "N/A"
                self.highest_month_value = 0
                self.lowest_month_name = "N/A"
                self.lowest_month_value = 0
                self.avg_monthly_growth = 0
                self.total_growth_pct = 0
            
            # Process top clients data
            if not self.top_clients_df.empty:
                self.total_client_revenue = self.top_clients_df["revenue"].sum()
                if len(self.top_clients_df) > 0:
                    self.top_client = self.top_clients_df.iloc[0]
                    self.top_client_name = str(self.top_client["cliente"])
                    self.top_client_revenue = float(self.top_client["revenue"])
                    self.top_client_pct = round((self.top_client_revenue / self.total_client_revenue * 100), 1) if self.total_client_revenue > 0 else 0
                
                # Calculate top 5 concentration
                if len(self.top_clients_df) >= 5:
                    self.top5_clients = self.top_clients_df.iloc[:5]
                    self.top5_revenue = self.top5_clients["revenue"].sum()
                    self.top5_pct = round((self.top5_revenue / self.total_client_revenue * 100), 1) if self.total_client_revenue > 0 else 0
                else:
                    self.top5_pct = 100 if self.total_client_revenue > 0 else 0
            else:
                self.total_client_revenue = 0
                self.top_client_name = "N/A"
                self.top_client_revenue = 0
                self.top_client_pct = 0
                self.top5_pct = 0
            
            # Process industry data
            if not self.industry_df.empty:
                self.total_industry_revenue = self.industry_df["revenue"].sum()
                if len(self.industry_df) > 0:
                    self.top_industry = self.industry_df.iloc[0]
                    self.top_industry_name = str(self.top_industry["industry"])
                    self.top_industry_revenue = float(self.top_industry["revenue"])
                    self.top_industry_pct = round((self.top_industry_revenue / self.total_industry_revenue * 100), 1) if self.total_industry_revenue > 0 else 0
                
                # Calculate top 3 industry concentration
                if len(self.industry_df) >= 3:
                    self.top3_industries = self.industry_df.iloc[:3]
                    self.top3_industry_revenue = self.top3_industries["revenue"].sum()
                    self.top3_industry_pct = round((self.top3_industry_revenue / self.total_industry_revenue * 100), 1) if self.total_industry_revenue > 0 else 0
                else:
                    self.top3_industry_pct = 100 if self.total_industry_revenue > 0 else 0
            else:
                self.total_industry_revenue = 0
                self.top_industry_name = "N/A"
                self.top_industry_revenue = 0
                self.top_industry_pct = 0
                self.top3_industry_pct = 0
            
            # Process budget vs actual data
            if not self.budget_actual_df.empty:
                self.total_budget = self.budget_actual_df["budget"].sum()
                self.total_actual = self.budget_actual_df["actual"].sum()
                self.total_variance = self.total_actual - self.total_budget
                self.budget_utilization = round((self.total_actual / self.total_budget * 100), 1) if self.total_budget > 0 else 0
                
                # Count over/under budget clients
                self.over_budget_count = int((self.budget_actual_df["variance"] > 0).sum())
                self.under_budget_count = int((self.budget_actual_df["variance"] < 0).sum())
                
                # Add utilization column if not present
                if "utilization" not in self.budget_actual_df.columns:
                    self.budget_actual_df["utilization"] = self.budget_actual_df.apply(
                        lambda x: round((x["actual"] / x["budget"] * 100), 1) if x["budget"] > 0 else 0,
                        axis=1
                    )
                
                # Get clients with extreme variance
                self.budget_actual_df["abs_variance"] = self.budget_actual_df["variance"].abs()
                self.extreme_variance_clients = self.budget_actual_df.nlargest(5, "abs_variance")
            else:
                self.total_budget = 0
                self.total_actual = 0
                self.total_variance = 0
                self.budget_utilization = 0
                self.over_budget_count = 0
                self.under_budget_count = 0
                self.extreme_variance_clients = pd.DataFrame()
            
            self.loaded = True
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            self.loaded = False
    
    def analyze_query(self, query):
        """
        Analyze the query to understand user intent and context
        for generating a reasoned response
        
        Args:
            query: User's question
            
        Returns:
            Dict with analysis info
        """
        query_lower = query.lower()
        analysis = {
            "intent": None,
            "focus": None,
            "timeframe": "current",
            "comparison": False,
            "specifics": []
        }
        
        # Determine the primary intent
        if any(term in query_lower for term in ["margen", "margin", "bruto", "ganancia", "rentabilidad"]):
            analysis["intent"] = "margin"
            analysis["focus"] = "profitability"
            
        elif any(term in query_lower for term in ["mes", "mayor", "ingreso", "mensual", "evolucion", "evolución", "tendencia"]):
            analysis["intent"] = "revenue_trend"
            
            # Check if asking about specific month
            month_match = re.search(r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)", query_lower)
            if month_match:
                analysis["focus"] = "specific_month"
                analysis["specifics"].append(month_match.group(0))
            else:
                analysis["focus"] = "monthly_trend"
                
            if "tendencia" in query_lower or "evolución" in query_lower or "evolucion" in query_lower:
                analysis["focus"] = "trend_analysis"
                
        elif any(term in query_lower for term in ["cliente", "clientes"]):
            analysis["intent"] = "client"
            
            if "top" in query_lower or "principales" in query_lower or "mejores" in query_lower:
                analysis["focus"] = "top_clients"
                # Check if asking for specific number
                limit_match = re.search(r"top\s+(\d+)|(\d+)\s+(?:principales|mejores)", query_lower)
                if limit_match:
                    analysis["specifics"].append(int(limit_match.group(1) or limit_match.group(2) or 5))
                else:
                    analysis["specifics"].append(5)
            else:
                # Look for specific client name
                client_match = re.search(r'cliente\s+([A-Za-z\s]+?)[\.|\?]|información sobre\s+([A-Za-z\s]+?)[\.|\?]|datos de\s+([A-Za-z\s]+?)[\.|\?]', query)
                if client_match:
                    analysis["focus"] = "specific_client"
                    client_name = ''.join([word for word in client_match.group(1) if word]).strip()
                    analysis["specifics"].append(client_name)
                else:
                    analysis["focus"] = "client_overview"
            
        elif any(term in query_lower for term in ["industria", "sector", "segmento"]):
            analysis["intent"] = "industry"
            
            if re.search(r"industria\s+([A-Za-z\s]+?)[\.|\?]|sector\s+([A-Za-z\s]+?)[\.|\?]", query_lower):
                analysis["focus"] = "specific_industry"
                industry_match = re.search(r"industria\s+([A-Za-z\s]+?)[\.|\?]|sector\s+([A-Za-z\s]+?)[\.|\?]", query_lower)
                industry_name = ''.join([word for word in industry_match.groups() if word]).strip()
                analysis["specifics"].append(industry_name)
            else:
                analysis["focus"] = "industry_distribution"
                
            if "génera" in query_lower or "genera" in query_lower or "mayor" in query_lower:
                analysis["focus"] = "top_industry"
            
        elif any(term in query_lower for term in ["presupuesto", "ejecución", "ejecucion", "budget", "variance", "varianza"]):
            analysis["intent"] = "budget"
            
            if "compara" in query_lower:
                analysis["focus"] = "budget_vs_actual"
                analysis["comparison"] = True
            elif "varianza" in query_lower:
                analysis["focus"] = "variance_analysis"
            else:
                analysis["focus"] = "budget_overview"
                
        elif any(term in query_lower for term in ["costo", "gasto", "cost"]):
            analysis["intent"] = "cost"
            analysis["focus"] = "cost_analysis"
                
        else:
            analysis["intent"] = "general"
            analysis["focus"] = "overview"
        
        # Look for comparison indicators
        if any(term in query_lower for term in ["compara", "comparación", "vs", "versus", "contra"]):
            analysis["comparison"] = True
        
        return analysis
    
    def generate_reasoning(self, analysis, data):
        """
        Generate reasoning based on the analysis and available data
        
        Args:
            analysis: Query analysis dictionary
            data: Relevant data dictionary
            
        Returns:
            Reasoning text
        """
        reasoning = []
        
        # Add reasoning based on intent and focus
        if analysis["intent"] == "margin":
            margin = data.get("margin", 0)
            industry_avg = data.get("industry_avg", 30)
            
            reasoning.append(f"Analizando el margen bruto del {margin}% contra el promedio del sector del {industry_avg}%.")
            
            if margin > industry_avg:
                diff = margin - industry_avg
                reasoning.append(f"El margen está {diff} puntos porcentuales por encima del promedio, lo que indica una eficiencia de costos superior.")
                if margin > 40:
                    reasoning.append("Este es un margen excepcionalmente alto que puede provenir de servicios premium o una estructura de costos optimizada.")
            elif margin < industry_avg:
                diff = industry_avg - margin
                reasoning.append(f"El margen está {diff} puntos porcentuales por debajo del promedio sectorial, lo que podría señalar presión competitiva en precios o costos operativos elevados.")
            else:
                reasoning.append("El margen está en línea con el promedio del sector, lo que sugiere un equilibrio competitivo adecuado.")
        
        elif analysis["intent"] == "revenue_trend":
            if analysis["focus"] == "specific_month":
                month = data.get("month", "")
                is_highest = data.get("is_highest", False)
                is_lowest = data.get("is_lowest", False)
                growth = data.get("growth")
                
                reasoning.append(f"Examinando el desempeño específico de {month}.")
                
                if is_highest:
                    reasoning.append(f"{month} representa el pico de ingresos en el periodo analizado, lo que amerita entender qué factores específicos contribuyeron a este resultado excepcional.")
                elif is_lowest:
                    reasoning.append(f"{month} muestra los ingresos más bajos del periodo, por lo que sería valioso investigar las causas de este comportamiento.")
                else:
                    reasoning.append(f"Este mes muestra un desempeño intermedio en el periodo analizado.")
                
                if growth is not None:
                    if growth > 10:
                        reasoning.append(f"Con un crecimiento del {growth:.1f}%, este mes muestra una aceleración significativa respecto al anterior, lo que indica un impulso positivo.")
                    elif growth > 0:
                        reasoning.append(f"El crecimiento moderado del {growth:.1f}% indica estabilidad con tendencia positiva.")
                    elif growth < -10:
                        reasoning.append(f"La caída del {abs(growth):.1f}% respecto al mes anterior señala una contracción significativa que requiere atención.")
                    else:
                        reasoning.append(f"La ligera disminución del {abs(growth):.1f}% sugiere una estabilización con tendencia a la baja.")
            
            elif analysis["focus"] == "monthly_trend" or analysis["focus"] == "trend_analysis":
                highest_month = data.get("highest_month", "")
                lowest_month = data.get("lowest_month", "")
                avg_growth = data.get("avg_growth", 0)
                
                reasoning.append("Analizando la tendencia completa de ingresos mensuales para identificar patrones.")
                
                if highest_month and lowest_month:
                    reasoning.append(f"La diferencia entre el mes de mayor ingreso ({highest_month}) y el de menor ({lowest_month}) revela la volatilidad del negocio.")
                
                if avg_growth > 5:
                    reasoning.append(f"Con un crecimiento promedio mensual del {avg_growth}%, la empresa muestra una fuerte trayectoria ascendente que supera significativamente la inflación.")
                elif avg_growth > 0:
                    reasoning.append(f"El crecimiento promedio del {avg_growth}% mensual indica una expansión estable aunque moderada.")
                elif avg_growth < -5:
                    reasoning.append(f"La tendencia de crecimiento negativo del {avg_growth}% mensual señala una contracción preocupante que requiere intervención estratégica.")
                else:
                    reasoning.append(f"El crecimiento casi plano del {avg_growth}% mensual sugiere un mercado maduro o saturado que requiere innovación para reactivarse.")
        
        elif analysis["intent"] == "client":
            if analysis["focus"] == "top_clients":
                clients_pct = data.get("clients_pct", 0)
                limit = data.get("limit", 5)
                
                reasoning.append(f"Analizando la concentración de ingresos en los {limit} clientes principales.")
                
                if clients_pct > 70:
                    reasoning.append(f"Con una concentración del {clients_pct}% en apenas {limit} clientes, existe un riesgo significativo de dependencia que podría comprometer la estabilidad financiera ante la pérdida de cualquiera de ellos.")
                elif clients_pct > 50:
                    reasoning.append(f"La concentración del {clients_pct}% en {limit} clientes representa un nivel de dependencia moderado que amerita estrategias de diversificación a mediano plazo.")
                else:
                    reasoning.append(f"La distribución de ingresos muestra una diversificación saludable, con solo el {clients_pct}% concentrado en los principales {limit} clientes.")
            
            elif analysis["focus"] == "client_overview":
                reasoning.append("Examinando la estructura general de la cartera de clientes para identificar oportunidades y riesgos.")
        
        elif analysis["intent"] == "industry":
            if analysis["focus"] == "top_industry" or analysis["focus"] == "industry_distribution":
                top_industry = data.get("top_industry", "")
                top_industry_pct = data.get("top_industry_pct", 0)
                
                reasoning.append(f"Analizando la concentración sectorial, con enfoque en {top_industry} que representa el {top_industry_pct}% de los ingresos.")
                
                if top_industry_pct > 60:
                    reasoning.append(f"La alta dependencia del sector {top_industry} podría representar un riesgo significativo ante cambios regulatorios o disrupción en esa industria específica.")
                elif top_industry_pct > 40:
                    reasoning.append(f"La concentración moderada en {top_industry} sugiere la necesidad de monitorear de cerca las tendencias en este sector mientras se busca diversificación adicional.")
                else:
                    reasoning.append(f"La concentración del {top_industry_pct}% en {top_industry} indica una exposición equilibrada que permite capitalizar el conocimiento del sector sin una dependencia excesiva.")
        
        elif analysis["intent"] == "budget":
            utilization = data.get("utilization", 0)
            total_variance = data.get("total_variance", 0)
            over_budget_count = data.get("over_budget_count", 0)
            under_budget_count = data.get("under_budget_count", 0)
            
            if analysis["focus"] == "budget_vs_actual":
                reasoning.append(f"Comparando el presupuesto planificado con la ejecución actual que está en {utilization}%.")
                
                if utilization > 100:
                    reasoning.append(f"La ejecución supera el presupuesto en un {utilization - 100}%, lo que indica posibles estimaciones conservadoras o gastos no previstos que requieren ajustes en la planificación.")
                elif utilization > 90:
                    reasoning.append(f"Con una utilización del {utilization}%, la ejecución está muy cercana al objetivo presupuestario, lo que demuestra una planificación precisa y una gestión financiera eficaz.")
                elif utilization > 70:
                    reasoning.append(f"La utilización del {utilization}% indica una subejecución moderada que podría requerir reasignación de recursos para maximizar oportunidades.")
                else:
                    reasoning.append(f"La baja ejecución del {utilization}% señala una significativa disparidad entre lo planificado y lo ejecutado, lo que podría indicar obstáculos operativos o estimaciones poco realistas.")
                
                reasoning.append(f"Con {over_budget_count} clientes sobre presupuesto y {under_budget_count} por debajo, se observa un desbalance que merece análisis detallado por cliente.")
            
            elif analysis["focus"] == "variance_analysis":
                if total_variance > 0:
                    reasoning.append(f"La varianza positiva de ${total_variance:,.0f} indica una ejecución por encima de lo presupuestado, lo que podría reflejar oportunidades no previstas o costos subestimados.")
                else:
                    reasoning.append(f"La varianza negativa de ${abs(total_variance):,.0f} muestra una ejecución por debajo del presupuesto, lo que podría indicar eficiencias operativas o retrasos en la implementación de proyectos.")
        
        elif analysis["intent"] == "cost":
            cost_percentage = data.get("cost_percentage", 0)
            
            reasoning.append(f"Analizando la estructura de costos que representa el {cost_percentage}% de los ingresos totales.")
            
            if cost_percentage > 80:
                reasoning.append("La elevada proporción de costos limita significativamente el margen y requiere una revisión exhaustiva de la estructura operativa y de precios.")
            elif cost_percentage > 60:
                reasoning.append("La proporción de costos es moderadamente alta pero dentro del rango esperable para el sector, aunque existe espacio para optimización.")
            else:
                reasoning.append("La proporción relativamente baja de costos indica una estructura operativa eficiente que contribuye a márgenes saludables.")
        
        elif analysis["intent"] == "general":
            reasoning.append("Realizando un análisis general de los KPIs más relevantes para proporcionar un panorama completo del negocio.")
        
        return "\n".join(reasoning)
    
    def generate_insight_recommendations(self, analysis, data):
        """
        Generate business recommendations based on data analysis
        
        Args:
            analysis: Query analysis dictionary
            data: Relevant data dictionary
            
        Returns:
            List of insight recommendations
        """
        insights = []
        
        # Generate insights based on intent and data
        if analysis["intent"] == "margin":
            margin = data.get("margin", 0)
            industry_avg = data.get("industry_avg", 30)
            
            if margin < industry_avg:
                insights.append("Revisar la estructura de costos para identificar oportunidades de optimización")
                insights.append("Considerar ajustes selectivos de precios en segmentos de mayor valor")
                insights.append("Evaluar la mezcla de productos/servicios para priorizar aquellos con mejores márgenes")
            else:
                insights.append("Mantener ventaja competitiva de margen mediante revisión continua de eficiencia operativa")
                insights.append("Evaluar si existe espacio para inversión estratégica aprovechando el margen superior")
                insights.append("Monitorear las presiones competitivas que podrían erosionar el margen")
                
        elif analysis["intent"] == "revenue_trend":
            if "specific_month" in analysis["focus"]:
                month_growth = data.get("growth")
                is_highest = data.get("is_highest", False)
                is_lowest = data.get("is_lowest", False)
                
                if is_highest:
                    insights.append("Analizar en detalle los factores de éxito detrás del desempeño excepcional de este mes")
                    insights.append("Evaluar si las estrategias aplicadas pueden replicarse en otros periodos")
                elif is_lowest:
                    insights.append("Investigar las causas específicas del bajo desempeño para implementar medidas correctivas")
                    insights.append("Revisar si existen factores estacionales que expliquen la variación")
                
                if month_growth and month_growth < 0:
                    insights.append("Desarrollar estrategias específicas para revertir la tendencia negativa")
            else:
                avg_growth = data.get("avg_growth", 0)
                
                if avg_growth < 3:
                    insights.append("Desarrollar iniciativas de crecimiento para acelerar la tendencia actual")
                    insights.append("Identificar segmentos de alta potencialidad para enfocar esfuerzos comerciales")
                else:
                    insights.append("Asegurar la infraestructura operativa necesaria para sostener el ritmo de crecimiento")
                    insights.append("Evaluar la escalabilidad de los sistemas actuales frente a la proyección de crecimiento")
                
        elif analysis["intent"] == "client":
            if analysis["focus"] == "top_clients":
                clients_pct = data.get("clients_pct", 0)
                
                if clients_pct > 50:
                    insights.append("Implementar programa de diversificación para reducir dependencia de clientes principales")
                    insights.append("Desarrollar estrategias de retención específicas para clientes clave")
                    insights.append("Evaluar el riesgo de concentración en la planificación financiera")
                else:
                    insights.append("Mantener el equilibrio actual de la cartera mientras se busca profundizar relaciones con clientes top")
                    insights.append("Analizar el potencial de cross-selling entre los diferentes segmentos de clientes")
                
        elif analysis["intent"] == "industry":
            top_industry_pct = data.get("top_industry_pct", 0)
            
            if top_industry_pct > 50:
                insights.append("Desarrollar plan de expansión hacia industrias complementarias para diversificar riesgos")
                insights.append("Monitorear indicadores macroeconómicos del sector dominante para anticipar cambios")
            else:
                insights.append("Evaluar especialización adicional en sectores de mayor rentabilidad")
                insights.append("Identificar sinergias entre el conocimiento de diferentes industrias")
                
        elif analysis["intent"] == "budget":
            utilization = data.get("utilization", 0)
            
            if utilization < 70:
                insights.append("Revisar las razones de la baja ejecución presupuestaria y ajustar proyecciones")
                insights.append("Evaluar si existen barreras operativas para la implementación de proyectos")
                insights.append("Considerar reasignación de recursos para maximizar la utilización efectiva")
            elif utilization > 110:
                insights.append("Implementar controles adicionales para proyectos con sobrecostos significativos")
                insights.append("Revisar el proceso de estimación presupuestaria para mejorar precisión")
                insights.append("Analizar el retorno de la inversión adicional para validar el sobregasto")
                
        elif analysis["intent"] == "cost":
            cost_percentage = data.get("cost_percentage", 0)
            
            if cost_percentage > 70:
                insights.append("Realizar análisis detallado de componentes de costo para identificar áreas de optimización")
                insights.append("Evaluar eficiencia operativa comparada con benchmarks del sector")
                insights.append("Considerar revisión de la estrategia de precios para mejorar márgenes")
            else:
                insights.append("Documentar las mejores prácticas actuales para mantener la eficiencia operativa")
                insights.append("Evaluar si existe espacio para reinversión estratégica")
                
        return insights[:3]  # Limit to top 3 insights
    
    def generate_response(self, query):
        """
        Generate a reasoned, data-driven response to the user's query
        
        Args:
            query: User's question
            
        Returns:
            Dict with response text, reasoning, data, and visualization info
        """
        # If data not loaded, return error
        if not self.loaded:
            return {
                "text": "Lo siento, no he podido cargar los datos necesarios para responder a tu consulta. Por favor, intenta de nuevo más tarde.",
                "success": False
            }
        
        # Analyze query to understand intent
        analysis = self.analyze_query(query)
        
        # Get relevant data based on the analysis
        data = self.get_data_for_analysis(analysis)
        
        # Generate reasoning about the data
        reasoning = self.generate_reasoning(analysis, data)
        
        # Generate relevant recommendations/insights
        insights = self.generate_insight_recommendations(analysis, data)
        
        # Generate the main response text
        response_text = self.generate_response_text(analysis, data)
        
        # Determine visualization type
        viz_info = self.determine_visualization(analysis, data)
        
        return {
            "text": response_text,
            "reasoning": reasoning,
            "insights": insights,
            "viz_type": viz_info.get("type", None),
            "viz_data": viz_info.get("data", {}),
            "data": data,
            "success": True
        }
    
    def get_data_for_analysis(self, analysis):
        """
        Gather relevant data based on query analysis
        
        Args:
            analysis: Query analysis dictionary
            
        Returns:
            Dict with relevant data
        """
        data = {}
        
        if analysis["intent"] == "margin":
            data["margin"] = self.financial_summary.get("gross_margin_percentage", 0)
            data["industry_avg"] = 30  # Example industry average
            data["revenue"] = self.financial_summary.get("total_income", 0)
            data["costs"] = self.financial_summary.get("total_costs", 0)
            data["gross_profit"] = self.financial_summary.get("gross_profit", 0)
            
        elif analysis["intent"] == "revenue_trend":
            if analysis["focus"] == "specific_month" and analysis["specifics"]:
                month_name = analysis["specifics"][0]
                month_data = self.get_month_data(month_name)
                
                if month_data:
                    data.update(month_data)
            
            # Add general monthly data regardless of specific month
            data["highest_month"] = self.highest_month_name
            data["highest_revenue"] = self.highest_month_value
            data["lowest_month"] = self.lowest_month_name
            data["lowest_revenue"] = self.lowest_month_value
            data["avg_growth"] = self.avg_monthly_growth
            data["total_growth"] = self.total_growth_pct
            data["monthly_data"] = self.monthly_revenue_df.to_dict('records') if not self.monthly_revenue_df.empty else []
        
        elif analysis["intent"] == "client":
            if analysis["focus"] == "top_clients":
                limit = analysis["specifics"][0] if analysis["specifics"] else 5
                limit = min(limit, len(self.top_clients_df))
                
                if not self.top_clients_df.empty:
                    clients = self.top_clients_df.iloc[:limit]
                    clients_revenue = clients["revenue"].sum()
                    clients_pct = round((clients_revenue / self.total_client_revenue * 100), 1) if self.total_client_revenue > 0 else 0
                    
                    data["clients"] = clients.to_dict('records')
                    data["limit"] = limit
                    data["total_revenue"] = self.total_client_revenue
                    data["clients_revenue"] = clients_revenue
                    data["clients_pct"] = clients_pct
                    data["top_client_name"] = self.top_client_name
                    data["top_client_revenue"] = self.top_client_revenue
            
            elif analysis["focus"] == "specific_client" and analysis["specifics"]:
                client_name = analysis["specifics"][0]
                client_data = self.get_client_data(client_name)
                
                if client_data:
                    data.update(client_data)
            
            else:
                # General client data
                data["total_clients"] = len(self.top_clients_df)
                data["top_client_name"] = self.top_client_name
                data["top_client_revenue"] = self.top_client_revenue
                data["top_client_pct"] = self.top_client_pct
                data["top5_pct"] = self.top5_pct
        
        elif analysis["intent"] == "industry":
            data["top_industry"] = self.top_industry_name
            data["top_industry_revenue"] = self.top_industry_revenue
            data["top_industry_pct"] = self.top_industry_pct
            data["top3_industry_pct"] = self.top3_industry_pct
            data["industry_count"] = len(self.industry_df) if not self.industry_df.empty else 0
            
            if not self.industry_df.empty:
                data["industries"] = self.industry_df.to_dict('records')
            
            if analysis["focus"] == "specific_industry" and analysis["specifics"]:
                industry_name = analysis["specifics"][0]
                industry_data = self.get_industry_data(industry_name)
                
                if industry_data:
                    data.update(industry_data)
        
        elif analysis["intent"] == "budget":
            data["total_budget"] = self.total_budget
            data["total_actual"] = self.total_actual
            data["total_variance"] = self.total_variance
            data["utilization"] = self.budget_utilization
            data["over_budget_count"] = self.over_budget_count
            data["under_budget_count"] = self.under_budget_count
            
            if not self.budget_actual_df.empty:
                data["budget_data"] = self.budget_actual_df.to_dict('records')
                
                if not self.extreme_variance_clients.empty:
                    data["extreme_variance_clients"] = self.extreme_variance_clients.to_dict('records')
        
        elif analysis["intent"] == "cost":
            costs = self.financial_summary.get("total_costs", 0)
            revenue = self.financial_summary.get("total_income", 0)
            gross_profit = self.financial_summary.get("gross_profit", 0)
            
            data["total_costs"] = costs
            data["total_revenue"] = revenue
            data["gross_profit"] = gross_profit
            data["cost_percentage"] = round((costs / revenue * 100), 1) if revenue > 0 else 0
        
        else:
            # General data for overview
            data["revenue"] = self.financial_summary.get("total_income", 0)
            data["margin"] = self.financial_summary.get("gross_margin_percentage", 0)
            data["top_industry"] = self.top_industry_name
            data["top_industry_pct"] = self.top_industry_pct
            data["budget_utilization"] = self.budget_utilization
            data["top_client_pct"] = self.top_client_pct
        
        return data
    
    def get_month_data(self, month_name):
        """Get data for a specific month"""
        if self.monthly_revenue_df.empty:
            return None
            
        # Standardize month name for matching
        month_mapping = {
            "enero": ["enero", "ene", "january", "jan"],
            "febrero": ["febrero", "feb", "february"],
            "marzo": ["marzo", "mar", "march"],
            "abril": ["abril", "abr", "april", "apr"],
            "mayo": ["mayo", "may"],
            "junio": ["junio", "jun", "june"],
            "julio": ["julio", "jul", "july"],
            "agosto": ["agosto", "ago", "august", "aug"],
            "septiembre": ["septiembre", "sep", "september"],
            "octubre": ["octubre", "oct", "october"],
            "noviembre": ["noviembre", "nov", "november"],
            "diciembre": ["diciembre", "dic", "december", "dec"]
        }
        
        # Find the standard month name
        std_month = None
        month_name_lower = month_name.lower()
        for std, variants in month_mapping.items():
            if month_name_lower in variants:
                std_month = std
                break
        
        if std_month is None:
            return None
            
        # Find the month in the data
        month_data = None
        for _, row in self.monthly_revenue_df.iterrows():
            month_str = str(row["month"]).lower()
            if any(variant in month_str for variant in month_mapping[std_month]):
                month_data = row
                break
        
        if month_data is None:
            return None
        
        # Create a structured response
        result = {
            "month": std_month.capitalize(),
            "revenue": month_data["revenue"],
            "is_highest": str(month_data["month"]).lower() == self.highest_month_name.lower(),
            "is_lowest": str(month_data["month"]).lower() == self.lowest_month_name.lower()
        }
        
        # Add growth percentage if available
        if "growth_pct" in month_data and pd.notna(month_data["growth_pct"]):
            result["growth"] = month_data["growth_pct"]
        
        return result
    
    def get_client_data(self, client_name):
        """Get data for a specific client"""
        if self.top_clients_df.empty:
            return None
        
        # Try to find an exact match first
        client_matches = self.top_clients_df[self.top_clients_df["cliente"] == client_name]
        
        # If no exact match, try partial match
        if client_matches.empty:
            client_matches = self.top_clients_df[self.top_clients_df["cliente"].str.contains(client_name, case=False, na=False)]
        
        if client_matches.empty:
            return None
        
        # Take the first match
        client_data = client_matches.iloc[0]
        
        # Get budget data if available
        budget_data = None
        if not self.budget_actual_df.empty:
            budget_matches = self.budget_actual_df[self.budget_actual_df["cliente"] == client_data["cliente"]]
            if not budget_matches.empty:
                budget_data = budget_matches.iloc[0]
        
        # Create structured result
        result = {
            "client_name": client_data["cliente"],
            "revenue": client_data["revenue"],
            "industry": client_data.get("industria", "")
        }
        
        # Add budget data if available
        if budget_data is not None:
            result.update({
                "budget": budget_data["budget"],
                "actual": budget_data["actual"],
                "variance": budget_data["variance"],
                "utilization": budget_data["utilization"]
            })
        
        # Calculate position in revenue ranking
        for i, (_, row) in enumerate(self.top_clients_df.iterrows(), 1):
            if row["cliente"] == client_data["cliente"]:
                result["position"] = i
                break
        
        return result
    
    def get_industry_data(self, industry_name):
        """Get data for a specific industry"""
        if self.industry_df.empty:
            return None
        
        # Try to find an exact match first
        industry_matches = self.industry_df[self.industry_df["industry"] == industry_name]
        
        # If no exact match, try partial match
        if industry_matches.empty:
            industry_matches = self.industry_df[self.industry_df["industry"].str.contains(industry_name, case=False, na=False)]
        
        if industry_matches.empty:
            return None
        
        # Take the first match
        industry_data = industry_matches.iloc[0]
        
        # Create structured result
        result = {
            "industry_name": industry_data["industry"],
            "revenue": industry_data["revenue"],
            "percentage": round((industry_data["revenue"] / self.total_industry_revenue * 100), 1) if self.total_industry_revenue > 0 else 0
        }
        
        # Calculate position in revenue ranking
        for i, (_, row) in enumerate(self.industry_df.iterrows(), 1):
            if row["industry"] == industry_data["industry"]:
                result["position"] = i
                break
        
        return result
    
    def generate_response_text(self, analysis, data):
        """
        Generate dynamic response text based on analysis and data
        
        Args:
            analysis: Query analysis dictionary
            data: Data dictionary with relevant information
            
        Returns:
            Response text
        """
        # Generate varied intros based on query type to avoid templated responses
        intros = []
        
        if analysis["intent"] == "margin":
            margin = data.get("margin", 0)
            industry_avg = data.get("industry_avg", 30)
            comparison = "por encima" if margin > industry_avg else "por debajo"
            
            intros = [
                f"El margen bruto actual de ActivaGroup es del **{margin}%**, lo cual está {comparison} del promedio del sector ({industry_avg}%).",
                f"Actualmente, ActivaGroup opera con un margen bruto del **{margin}%**, posicionándose {comparison} del promedio sectorial del {industry_avg}%.",
                f"Los datos muestran que el margen bruto se sitúa en **{margin}%**, {comparison} del {industry_avg}% que representa el promedio de la industria."
            ]
            
            # Select random intro
            response = random.choice(intros)
            
            # Add explanation
            response += f" Este valor representa el porcentaje de ganancia después de considerar los costos directos. Con un margen del {margin}%, por cada $100 en ventas, la empresa retiene ${margin} después de costos directos."
        
        elif analysis["intent"] == "revenue_trend":
            if analysis["focus"] == "specific_month" and "month" in data:
                month = data["month"]
                revenue = data.get("revenue", 0)
                is_highest = data.get("is_highest", False)
                is_lowest = data.get("is_lowest", False)
                growth = data.get("growth")
                
                intros = [
                    f"En **{month}**, los ingresos fueron de **${revenue:,.0f}**.",
                    f"Los datos para **{month}** muestran ingresos de **${revenue:,.0f}**.",
                    f"El análisis de **{month}** revela ingresos por **${revenue:,.0f}**."
                ]
                
                response = random.choice(intros)
                
                # Add context based on relative performance
                if is_highest:
                    response += f" Este fue el mes con mayor ingreso en el periodo analizado."
                elif is_lowest:
                    response += f" Este fue el mes con menor ingreso en el periodo analizado."
                else:
                    highest_month = data.get("highest_month", "")
                    highest_revenue = data.get("highest_revenue", 0)
                    response += f" El mes con mayor ingreso fue **{highest_month}** con **${highest_revenue:,.0f}**."
                
                # Add growth information if available
                if growth is not None:
                    growth_text = "un crecimiento" if growth > 0 else "una disminución"
                    response += f" En comparación con el mes anterior, {month} mostró {growth_text} del **{abs(growth):.1f}%**."
            
            else:
                # Monthly trends
                highest_month = data.get("highest_month", "")
                highest_revenue = data.get("highest_revenue", 0)
                lowest_month = data.get("lowest_month", "")
                lowest_revenue = data.get("lowest_revenue", 0)
                avg_growth = data.get("avg_growth", 0)
                
                intros = [
                    f"El análisis de ingresos mensuales muestra que **{highest_month}** fue el mes con mayor ingreso (**${highest_revenue:,.0f}**), mientras que **{lowest_month}** registró el menor (**${lowest_revenue:,.0f}**).",
                    f"En el periodo analizado, el pico de ingresos se alcanzó en **{highest_month}** con **${highest_revenue:,.0f}**, contrastando con el mínimo de **${lowest_revenue:,.0f}** en **{lowest_month}**.",
                    f"La distribución de ingresos mensuales muestra a **{highest_month}** como el mes más fuerte con **${highest_revenue:,.0f}**, mientras que **{lowest_month}** presentó el desempeño más bajo con **${lowest_revenue:,.0f}**."
                ]
                
                response = random.choice(intros)
                
                # Add trend information
                growth_qualifier = "crecimiento sostenido" if avg_growth > 5 else "crecimiento moderado" if avg_growth > 0 else "tendencia negativa" if avg_growth < 0 else "estabilidad relativa"
                response += f" La tendencia general muestra un {growth_qualifier} con un promedio mensual del **{avg_growth:.1f}%**."
        
        elif analysis["intent"] == "client":
            if analysis["focus"] == "top_clients":
                limit = data.get("limit", 5)
                clients_revenue = data.get("clients_revenue", 0)
                clients_pct = data.get("clients_pct", 0)
                
                intros = [
                    f"Los {limit} principales clientes generan **${clients_revenue:,.0f}** en ingresos, lo que representa el **{clients_pct}%** del total.",
                    f"El análisis de concentración muestra que los primeros {limit} clientes aportan **${clients_revenue:,.0f}**, equivalente al **{clients_pct}%** de los ingresos totales.",
                    f"Los ingresos de los {limit} clientes más importantes ascienden a **${clients_revenue:,.0f}**, constituyendo el **{clients_pct}%** del ingreso total."
                ]
                
                response = random.choice(intros) + "\n\n"
                
                # Add client list if available
                if "clients" in data:
                    response += f"**Top {limit} Clientes:**\n"
                    for i, client in enumerate(data["clients"], 1):
                        response += f"{i}. **{client['cliente']}**: ${client['revenue']:,.0f}\n"
                
                # Add risk assessment
                if clients_pct > 50:
                    response += "\nEsta alta concentración podría representar un riesgo si alguno de estos clientes reduce su inversión."
                else:
                    response += "\nEsta distribución muestra una diversificación adecuada de la cartera de clientes."
            
            else:
                # General client info
                top_client_name = data.get("top_client_name", "")
                top_client_pct = data.get("top_client_pct", 0)
                top5_pct = data.get("top5_pct", 0)
                
                intros = [
                    f"El principal cliente es **{top_client_name}** que representa el **{top_client_pct}%** de los ingresos totales.",
                    f"**{top_client_name}** se posiciona como el cliente más importante con una contribución del **{top_client_pct}%** a los ingresos.",
                    f"En términos de concentración de ingresos, **{top_client_name}** lidera con el **{top_client_pct}%** del total."
                ]
                
                response = random.choice(intros)
                
                # Add top 5 concentration
                response += f" Los cinco principales clientes concentran el **{top5_pct}%** de los ingresos."
                
                # Add concentration assessment
                if top5_pct > 60:
                    response += " Esta elevada concentración sugiere la necesidad de estrategias de diversificación para mitigar riesgos."
                elif top5_pct > 40:
                    response += " Esta concentración moderada indica un balance entre el enfoque en clientes clave y una diversificación saludable."
                else:
                    response += " Esta distribución muestra una cartera de clientes bien diversificada."
        
        elif analysis["intent"] == "industry":
            top_industry = data.get("top_industry", "")
            top_industry_revenue = data.get("top_industry_revenue", 0)
            top_industry_pct = data.get("top_industry_pct", 0)
            top3_industry_pct = data.get("top3_industry_pct", 0)
            industry_count = data.get("industry_count", 0)
            
            intros = [
                f"La industria principal es **{top_industry}** con **${top_industry_revenue:,.0f}** en ingresos, representando el **{top_industry_pct}%** del total.",
                f"El sector de **{top_industry}** lidera la distribución con ingresos de **${top_industry_revenue:,.0f}**, equivalentes al **{top_industry_pct}%** del total.",
                f"**{top_industry}** se posiciona como el sector dominante, generando **${top_industry_revenue:,.0f}** (**{top_industry_pct}%** del ingreso total)."
            ]
            
            response = random.choice(intros)
            
            # Add additional context
            response += f" Las tres industrias principales representan el **{top3_industry_pct}%** de los ingresos totales, con un total de **{industry_count}** industrias atendidas."
        
        elif analysis["intent"] == "budget":
            total_budget = data.get("total_budget", 0)
            total_actual = data.get("total_actual", 0)
            total_variance = data.get("total_variance", 0)
            utilization = data.get("utilization", 0)
            over_budget_count = data.get("over_budget_count", 0)
            under_budget_count = data.get("under_budget_count", 0)
            
            variance_qualifier = "favorable" if total_variance >= 0 else "desfavorable"
            
            intros = [
                f"El presupuesto total es de **${total_budget:,.0f}** y la ejecución actual es de **${total_actual:,.0f}**, lo que representa una utilización del **{utilization}%**.",
                f"La comparación presupuestaria muestra un total planificado de **${total_budget:,.0f}** frente a una ejecución de **${total_actual:,.0f}**, resultando en un **{utilization}%** de utilización.",
                f"Los datos presupuestarios revelan que de un total de **${total_budget:,.0f}** se han ejecutado **${total_actual:,.0f}**, alcanzando un **{utilization}%** de implementación."
            ]
            
            response = random.choice(intros)
            
            # Add variance information
            response += f" La varianza es de **${abs(total_variance):,.0f}** ({variance_qualifier}). "
            
            # Add client counts
            response += f"Hay **{over_budget_count}** clientes por encima del presupuesto y **{under_budget_count}** por debajo."
        
        elif analysis["intent"] == "cost":
            costs = data.get("total_costs", 0)
            revenue = data.get("total_revenue", 0)
            gross_profit = data.get("gross_profit", 0)
            cost_percentage = data.get("cost_percentage", 0)
            profit_percentage = 100 - cost_percentage
            
            intros = [
                f"Los costos totales ascienden a **${costs:,.0f}**, lo que representa el **{cost_percentage}%** de los ingresos totales (**${revenue:,.0f}**).",
                f"El análisis de costos muestra un total de **${costs:,.0f}**, equivalente al **{cost_percentage}%** de los **${revenue:,.0f}** en ingresos.",
                f"La estructura de costos suma **${costs:,.0f}**, representando un **{cost_percentage}%** del ingreso total de **${revenue:,.0f}**."
            ]
            
            response = random.choice(intros)
            
            # Add profit information
            response += f" La ganancia bruta es de **${gross_profit:,.0f}**, lo que representa el **{profit_percentage}%** de los ingresos."
        
        else:
            # General overview
            revenue = data.get("revenue", 0)
            margin = data.get("margin", 0)
            top_industry = data.get("top_industry", "")
            top_industry_pct = data.get("top_industry_pct", 0)
            budget_utilization = data.get("budget_utilization", 0)
            
            intros = [
                f"ActivaGroup registra **${revenue:,.0f}** en ingresos totales con un margen bruto del **{margin}%**.",
                f"El desempeño general muestra ingresos por **${revenue:,.0f}** y un margen bruto del **{margin}%**.",
                f"El análisis financiero revela ingresos totales de **${revenue:,.0f}** con un margen del **{margin}%**."
            ]
            
            response = random.choice(intros)
            
            # Add additional context if available
            if top_industry:
                response += f" La industria más importante es **{top_industry}**."
            
            if budget_utilization > 0:
                response += f" La utilización presupuestaria actual es del **{budget_utilization}%**."
        
        return response
    
    def determine_visualization(self, analysis, data):
        """
        Determine the appropriate visualization based on query analysis
        
        Args:
            analysis: Query analysis dictionary
            data: Data dictionary
            
        Returns:
            Dict with visualization type and data
        """
        viz_info = {
            "type": None,
            "data": {}
        }
        
        if analysis["intent"] == "margin":
            viz_info["type"] = "gauge"
            viz_info["data"] = {
                "value": data.get("margin", 0),
                "min": 0,
                "max": 100,
                "threshold": data.get("industry_avg", 30),
                "title": "Margen Bruto"
            }
            
        elif analysis["intent"] == "revenue_trend":
            if not self.monthly_revenue_df.empty:
                if analysis["focus"] == "specific_month" and "month" in data:
                    viz_info["type"] = "line"
                    viz_info["data"] = {
                        "df": self.monthly_revenue_df,
                        "x": "month",
                        "y": "revenue",
                        "title": "Ingresos Mensuales",
                        "highlight": data["month"]
                    }
                else:
                    # Create a combined revenue-cost dataset for better visualization
                    monthly_costs_data = self.monthly_revenue_df.copy()
                    
                    # Generate cost estimates based on gross margin if available
                    if "gross_margin_percentage" in self.financial_summary and self.financial_summary["gross_margin_percentage"] > 0:
                        margin = self.financial_summary["gross_margin_percentage"]
                        cost_ratio = 1 - (margin / 100)
                        monthly_costs_data["costs"] = monthly_costs_data["revenue"] * cost_ratio
                    else:
                        # Default to 70% cost ratio
                        monthly_costs_data["costs"] = monthly_costs_data["revenue"] * 0.7
                    
                    viz_info["type"] = "revenue_cost"
                    viz_info["data"] = {
                        "df": monthly_costs_data,
                        "title": "Tendencia de Ingresos y Costos Mensuales"
                    }
        
        elif analysis["intent"] == "client":
            if analysis["focus"] == "top_clients" and "clients" in data:
                clients_df = pd.DataFrame(data["clients"])
                if not clients_df.empty:
                    viz_info["type"] = "bar"
                    viz_info["data"] = {
                        "df": clients_df,
                        "x": "cliente",
                        "y": "revenue",
                        "title": f"Top {data.get('limit', 5)} Clientes por Ingresos"
                    }
            elif analysis["focus"] == "specific_client" and "client_name" in data:
                if "budget" in data and "actual" in data:
                    # Create small DataFrame for this client
                    client_df = pd.DataFrame([{
                        "cliente": data["client_name"],
                        "budget": data["budget"],
                        "actual": data["actual"]
                    }])
                    
                    viz_info["type"] = "budget_vs_actual"
                    viz_info["data"] = {
                        "df": client_df,
                        "client_col": "cliente",
                        "budget_col": "budget",
                        "actual_col": "actual",
                        "title": f"Presupuesto vs Ejecución: {data['client_name']}"
                    }
            
        elif analysis["intent"] == "industry":
            if not self.industry_df.empty:
                viz_info["type"] = "pie"
                viz_info["data"] = {
                    "df": self.industry_df,
                    "value": "revenue",
                    "name": "industry",
                    "title": "Distribución por Industria"
                }
        
        elif analysis["intent"] == "budget":
            if analysis["focus"] == "budget_vs_actual" or analysis["focus"] == "budget_overview":
                viz_info["type"] = "gauge"
                viz_info["data"] = {
                    "value": data.get("utilization", 0),
                    "min": 0,
                    "max": 130,
                    "threshold": 100,
                    "title": "Utilización del Presupuesto"
                }
                
                # Add secondary visualization if we have extreme variance clients
                if "extreme_variance_clients" in data and not self.extreme_variance_clients.empty:
                    viz_info["secondary_type"] = "budget_vs_actual"
                    viz_info["secondary_data"] = {
                        "df": self.extreme_variance_clients,
                        "client_col": "cliente",
                        "budget_col": "budget",
                        "actual_col": "actual",
                        "title": "Clientes con Mayor Varianza"
                    }
            
            elif analysis["focus"] == "variance_analysis":
                # Create bar chart of top variances
                if not self.budget_actual_df.empty:
                    variance_df = self.budget_actual_df.nlargest(10, "abs_variance")
                    
                    viz_info["type"] = "bar"
                    viz_info["data"] = {
                        "df": variance_df,
                        "x": "cliente",
                        "y": "variance",
                        "title": "Top 10 Varianzas de Presupuesto"
                    }
        
        elif analysis["intent"] == "cost":
            # Create simple pie chart for cost vs profit
            viz_info["type"] = "pie"
            viz_info["data"] = {
                "labels": ["Costos", "Ganancia Bruta"],
                "values": [data.get("total_costs", 0), data.get("gross_profit", 0)],
                "title": "Distribución de Ingresos y Costos"
            }
        
        else:
            # Determine based on available data
            if not self.monthly_revenue_df.empty:
                # Create a combined revenue-cost dataset for better visualization
                monthly_costs_data = self.monthly_revenue_df.copy()
                
                # Generate cost estimates based on gross margin if available
                if "gross_margin_percentage" in self.financial_summary and self.financial_summary["gross_margin_percentage"] > 0:
                    margin = self.financial_summary["gross_margin_percentage"]
                    cost_ratio = 1 - (margin / 100)
                    monthly_costs_data["costs"] = monthly_costs_data["revenue"] * cost_ratio
                else:
                    # Default to 70% cost ratio
                    monthly_costs_data["costs"] = monthly_costs_data["revenue"] * 0.7
                
                viz_info["type"] = "revenue_cost"
                viz_info["data"] = {
                    "df": monthly_costs_data,
                    "title": "Tendencia de Ingresos y Costos Mensuales"
                }
            elif not self.top_clients_df.empty:
                viz_info["type"] = "bar"
                viz_info["data"] = {
                    "df": self.top_clients_df.iloc[:10],
                    "x": "cliente",
                    "y": "revenue",
                    "title": "Top 10 Clientes por Ingresos"
                }
            elif not self.industry_df.empty:
                viz_info["type"] = "pie"
                viz_info["data"] = {
                    "df": self.industry_df,
                    "value": "revenue",
                    "name": "industry",
                    "title": "Distribución por Industria"
                }
        
        return viz_info

# INTELLIGENT AI ASSISTANT with REASONING
class IntelligentAIAssistant:
    """
    Advanced AI Assistant that uses reasoning and dynamic responses
    to provide insightful analysis of business data
    """
    
    def __init__(self):
        """Initialize the AI assistant with the data analyzer"""
        self.data_analyzer = IntelligentDataAnalyzer()
    
    def process_query(self, query, viz_container=None):
        """
        Process a user query and return a comprehensive response with 
        reasoning and visualization
        
        Args:
            query: User's question
            viz_container: Streamlit container for visualization
            
        Returns:
            Response text
        """
        # Generate the response from the analyzer
        response_data = self.data_analyzer.generate_response(query)
        
        if not response_data["success"]:
            return response_data["text"]
        
        # Create visualization if container provided
        if viz_container and response_data.get("viz_type"):
            self._create_visualization(response_data, viz_container)
        
        # Build the final response with reasoning and insights
        final_response = response_data["text"]
        
        # Add reasoning and insights sections - only one of these depending on the case
        if random.random() > 0.5 and "reasoning" in response_data:
            final_response += f"\n\n<div class='reasoning-container'><div class='reasoning-title'>Análisis de Datos:</div>{response_data['reasoning']}</div>"
        elif "insights" in response_data and response_data["insights"]:
            insights_html = "<div class='reasoning-container'><div class='reasoning-title'>Recomendaciones Estratégicas:</div>"
            for insight in response_data["insights"]:
                insights_html += f"<div class='data-insight'>• {insight}</div>"
            insights_html += "</div>"
            
            final_response += f"\n\n{insights_html}"
        
        return final_response
    
    def _create_visualization(self, response_data, container):
        """
        Create appropriate visualization based on response data
        
        Args:
            response_data: Response data dictionary
            container: Streamlit container for visualization
        """
        viz_type = response_data.get("viz_type")
        viz_data = response_data.get("viz_data", {})
        
        if not viz_type or not viz_data:
            return
        
        with container:
            st.markdown(f"<div class='ai-viz-container'>", unsafe_allow_html=True)
            
            # Add title if provided
            if "title" in viz_data:
                st.markdown(f"<div class='ai-viz-title'>{viz_data['title']}</div>", unsafe_allow_html=True)
            
            # Create appropriate visualization based on type
            if viz_type == "line":
                self._create_line_chart(viz_data)
                
            elif viz_type == "bar":
                self._create_bar_chart(viz_data)
                
            elif viz_type == "pie":
                self._create_pie_chart(viz_data)
                
            elif viz_type == "gauge":
                self._create_gauge_chart(viz_data)
                
            elif viz_type == "budget_vs_actual":
                self._create_budget_vs_actual_chart(viz_data)
                
            elif viz_type == "revenue_cost":
                self._create_revenue_cost_chart(viz_data)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Create insight cards if available
            if "data" in response_data:
                data = response_data["data"]
                
                # Determine which cards to show based on the data and visualization type
                cards = self._generate_insight_cards(viz_type, data)
                
                if cards:
                    st.markdown("<div style='display: flex; gap: 10px; margin-top: 10px;'>", unsafe_allow_html=True)
                    
                    for card in cards:
                        st.markdown(f"""
                        <div class="ai-insight-card" style="flex: 1;">
                            <div class="ai-insight-title">{card['title']}</div>
                            <div class="ai-insight-value">{card['value']}</div>
                            <div class="ai-insight-description">{card['description']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Add secondary visualization if provided
            if "secondary_type" in response_data and "secondary_data" in response_data:
                st.markdown("<div class='ai-viz-container' style='margin-top: 15px;'>", unsafe_allow_html=True)
                
                # Add title if provided
                if "title" in response_data["secondary_data"]:
                    st.markdown(f"<div class='ai-viz-title'>{response_data['secondary_data']['title']}</div>", unsafe_allow_html=True)
                
                # Create appropriate visualization based on type
                sec_viz_type = response_data["secondary_type"]
                
                if sec_viz_type == "budget_vs_actual":
                    self._create_budget_vs_actual_chart(response_data["secondary_data"])
                elif sec_viz_type == "bar":
                    self._create_bar_chart(response_data["secondary_data"])
                elif sec_viz_type == "line":
                    self._create_line_chart(response_data["secondary_data"])
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    def _generate_insight_cards(self, viz_type, data):
        """
        Generate insight cards based on visualization type and data
        
        Args:
            viz_type: Visualization type
            data: Data dictionary
            
        Returns:
            List of card data
        """
        cards = []
        
        if viz_type == "line" or viz_type == "revenue_cost":
            # Monthly revenue insights
            if "highest_month" in data and "highest_revenue" in data:
                cards.append({
                    "title": "Mes Máximo",
                    "value": f"${data['highest_revenue']:,.0f}",
                    "description": f"{data['highest_month']}"
                })
            
            if "lowest_month" in data and "lowest_revenue" in data:
                cards.append({
                    "title": "Mes Mínimo",
                    "value": f"${data['lowest_revenue']:,.0f}",
                    "description": f"{data['lowest_month']}"
                })
            
            if "avg_growth" in data:
                cards.append({
                    "title": "Crecimiento Promedio",
                    "value": f"{data['avg_growth']:.1f}%",
                    "description": "mensual"
                })
        
        elif viz_type == "bar" and "clients_pct" in data:
            # Top clients insights
            cards.append({
                "title": "Concentración",
                "value": f"{data['clients_pct']}%",
                "description": f"en top {data.get('limit', 5)} clientes"
            })
            
            if "clients" in data and len(data["clients"]) > 0:
                top_client = data["clients"][0]
                cards.append({
                    "title": "Cliente Principal",
                    "value": f"${top_client['revenue']:,.0f}",
                    "description": f"{top_client['cliente']}"
                })
        
        elif viz_type == "pie" and "top_industry_pct" in data:
            # Industry insights
            cards.append({
                "title": "Industria Principal",
                "value": f"{data['top_industry_pct']}%",
                "description": f"{data['top_industry']}"
            })
            
            if "top3_industry_pct" in data:
                cards.append({
                    "title": "Top 3 Industrias",
                    "value": f"{data['top3_industry_pct']}%",
                    "description": "de los ingresos totales"
                })
            
            if "industry_count" in data:
                cards.append({
                    "title": "Total Industrias",
                    "value": f"{data['industry_count']}",
                    "description": "sectores atendidos"
                })
        
        elif viz_type == "gauge" and "utilization" in data:
            # Budget insights
            if "total_budget" in data:
                cards.append({
                    "title": "Presupuesto",
                    "value": f"${data['total_budget']:,.0f}",
                    "description": "Total planificado"
                })
            
            if "total_actual" in data:
                cards.append({
                    "title": "Ejecución",
                    "value": f"${data['total_actual']:,.0f}",
                    "description": "Total ejecutado"
                })
            
            cards.append({
                "title": "Utilización",
                "value": f"{data['utilization']}%",
                "description": f"Varianza: ${data.get('total_variance', 0):,.0f}"
            })
        
        # Ensure we have at most 3 cards
        return cards[:3]
    
    def _create_line_chart(self, viz_data):
        """Create an enhanced line chart for monthly revenue"""
        if "df" not in viz_data or viz_data["df"].empty:
            st.info("No hay datos suficientes para crear la visualización")
            return
            
        df = viz_data["df"]
        x_col = viz_data.get("x", "month")
        y_col = viz_data.get("y", "revenue")
        
        # Create better line chart with area fill and improved styling
        fig = go.Figure()
        
        # Add revenue line with improved styling
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='lines+markers',
            name='Ingresos',
            line=dict(
                color=COLORS['secondary'],
                width=3,
                shape='spline'  # Smooth curves
            ),
            marker=dict(
                size=8,
                color=COLORS['secondary'],
                line=dict(
                    width=1,
                    color='white'
                )
            ),
            fill='tozeroy',
            fillcolor=CHART_COLORS_TRANSPARENT[0],
            hovertemplate='<b>%{x}</b><br>$%{y:,.0f}<extra></extra>'
        ))
        
        # Update layout with improved styling
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
            showlegend=False,
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor=COLORS['panel_bg'],
                font_size=12,
                font_family="Inter, sans-serif",
                bordercolor='rgba(255,255,255,0.1)'
            )
        )
        
        # Add highlight for specific month if provided
        if "highlight" in viz_data:
            highlight_month = viz_data["highlight"]
            
            # Find the month in data
            for i, (_, row) in enumerate(df.iterrows()):
                month_str = str(row[x_col]).lower()
                if highlight_month.lower() in month_str.lower():
                    # Add marker highlight
                    fig.add_trace(go.Scatter(
                        x=[row[x_col]],
                        y=[row[y_col]],
                        mode='markers',
                        marker=dict(
                            size=12,
                            color=COLORS['accent3'],
                            line=dict(width=2, color='white')
                        ),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    
                    # Add annotation
                    fig.add_annotation(
                        x=row[x_col],
                        y=row[y_col],
                        text=f"${row[y_col]:,.0f}",
                        showarrow=True,
                        arrowhead=1,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor=COLORS['accent3'],
                        font=dict(color=COLORS['accent3'], size=12),
                        ax=0,
                        ay=-40
                    )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_revenue_cost_chart(self, viz_data):
        """Create enhanced revenue vs costs chart visualization"""
        if "df" not in viz_data or viz_data["df"].empty:
            st.info("No hay datos suficientes para crear la visualización")
            return
            
        df = viz_data["df"]
        
        # Create chart
        fig = go.Figure()
        
        # Add revenue line with area
        fig.add_trace(go.Scatter(
            x=df["month"],
            y=df["revenue"],
            mode='lines+markers',
            name='Ingresos',
            line=dict(
                color=COLORS['secondary'],
                width=3,
                shape='spline'  # Smooth curves
            ),
            marker=dict(
                size=8,
                color=COLORS['secondary'],
                line=dict(
                    width=1,
                    color='white'
                )
            ),
            fill='tozeroy',
            fillcolor=CHART_COLORS_TRANSPARENT[0],
            hovertemplate='<b>%{x}</b><br>Ingresos: $%{y:,.0f}<extra></extra>'
        ))
        
        # Add costs line
        if "costs" in df.columns:
            fig.add_trace(go.Scatter(
                x=df["month"],
                y=df["costs"],
                mode='lines+markers',
                name='Costos',
                line=dict(
                    color=COLORS['danger'],
                    width=3,
                    shape='spline'  # Smooth curves
                ),
                marker=dict(
                    size=8,
                    color=COLORS['danger'],
                    line=dict(
                        width=1,
                        color='white'
                    )
                ),
                hovertemplate='<b>%{x}</b><br>Costos: $%{y:,.0f}<extra></extra>'
            ))
        
        # Calculate margin
        if "costs" in df.columns:
            margins = (df["revenue"] - df["costs"]) / df["revenue"] * 100
            margin_title = "Margen Promedio"
            avg_margin = margins.mean()
            
            # Find the highest and lowest margin months
            highest_margin_idx = margins.idxmax()
            lowest_margin_idx = margins.idxmin()
            
            # Add annotations for highest and lowest margin months
            if highest_margin_idx is not None:
                highest_month = df.loc[highest_margin_idx, "month"]
                highest_margin = margins.loc[highest_margin_idx]
                
                fig.add_annotation(
                    x=highest_month,
                    y=df.loc[highest_margin_idx, "revenue"],
                    text=f"Margen más alto: {highest_margin:.1f}%",
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=-40,
                    arrowcolor=COLORS['success'],
                    font=dict(color=COLORS['success'], size=10)
                )
            
            if lowest_margin_idx is not None and lowest_margin_idx != highest_margin_idx:
                lowest_month = df.loc[lowest_margin_idx, "month"]
                lowest_margin = margins.loc[lowest_margin_idx]
                
                fig.add_annotation(
                    x=lowest_month,
                    y=df.loc[lowest_margin_idx, "revenue"],
                    text=f"Margen más bajo: {lowest_margin:.1f}%",
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=40,
                    arrowcolor=COLORS['danger'],
                    font=dict(color=COLORS['danger'], size=10)
                )
        else:
            margin_title = ""
            avg_margin = 0
        
        # Enhanced layout
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
        
        # Add margin info if available
        if "costs" in df.columns and avg_margin > 0:
            fig.add_annotation(
                xref='paper',
                yref='paper',
                x=0.01,
                y=0.99,
                text=f"{margin_title}: {avg_margin:.1f}%",
                showarrow=False,
                font=dict(
                    family="Inter, sans-serif",
                    size=12,
                    color=COLORS['success']
                ),
                align="left",
                bgcolor=COLORS['panel_bg'],
                bordercolor=COLORS['success'],
                borderwidth=1,
                borderpad=4
            )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_bar_chart(self, viz_data):
        """Create enhanced bar chart for clients or industries"""
        if "df" not in viz_data or viz_data["df"].empty:
            st.info("No hay datos suficientes para crear la visualización")
            return
            
        df = viz_data["df"]
        x_col = viz_data.get("x", "cliente")
        y_col = viz_data.get("y", "revenue")
        
        # Sort data for better visualization
        df_sorted = df.sort_values(by=y_col, ascending=True)
        
        # Create enhanced bar chart
        fig = go.Figure()
        
        # Add bars with gradient color based on revenue
        fig.add_trace(go.Bar(
            y=df_sorted[x_col], 
            x=df_sorted[y_col],
            orientation='h',
            marker=dict(
                color=df_sorted[y_col],
                colorscale=[[0, COLORS['info']], [0.5, COLORS['accent3']], [1, COLORS['secondary']]],
                line=dict(width=0)
            ),
            hovertemplate='<b>%{y}</b><br>$%{x:,.0f}<extra></extra>'
        ))
        
        # Add total percentage annotations
        total_revenue = df_sorted[y_col].sum()
        
        for i, row in df_sorted.iterrows():
            percentage = row[y_col] / total_revenue * 100
            if percentage >= 5:  # Only show percentage for significant contributors
                fig.add_annotation(
                    x=row[y_col] + (total_revenue * 0.01),  # Small offset
                    y=row[x_col],
                    text=f"{percentage:.1f}%",
                    showarrow=False,
                    font=dict(color=COLORS['secondary_text'], size=10),
                    xanchor="left"
                )
        
        # Update layout with enhanced styling
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
            showlegend=False,
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
            textfont=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_pie_chart(self, viz_data):
        """Create pie chart for industry distribution"""
        # Check if we have direct pie chart data
        if "labels" in viz_data and "values" in viz_data:
            # Create a simple pie chart
            fig = go.Figure()
            
            fig.add_trace(go.Pie(
                labels=viz_data["labels"],
                values=viz_data["values"],
                hole=0.6,
                marker=dict(colors=[COLORS['danger'], COLORS['success']]),
                textinfo='percent',
                textfont=dict(family="Inter, sans-serif", size=12, color=COLORS['text']),
                hoverinfo='label+value',
                hovertemplate='%{label}: $%{value:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.1,
                    xanchor="center",
                    x=0.5,
                    font=dict(family="Inter, sans-serif", size=11, color=COLORS['secondary_text'])
                )
            )
            
            # Add total in the center if we have it
            if "total_revenue" in viz_data:
                fig.add_annotation(
                    text=f"${viz_data['total_revenue']:,.0f}",
                    x=0.5,
                    y=0.5,
                    font=dict(size=16, color=COLORS['text']),
                    showarrow=False
                )
            
            st.plotly_chart(fig, use_container_width=True)
            return
            
        # Otherwise use dataframe data
        if "df" not in viz_data or viz_data["df"].empty:
            st.info("No hay datos suficientes para crear la visualización")
            return
            
        df = viz_data["df"]
        value_col = viz_data.get("value", "revenue")
        name_col = viz_data.get("name", "industry")
        
        # Create pie chart using visualization utility
        fig = create_industry_pie_chart(df, value_col=value_col, name_col=name_col)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_gauge_chart(self, viz_data):
        """Create gauge chart for utilization or margin"""
        value = viz_data.get("value", 0)
        min_val = viz_data.get("min", 0)
        max_val = viz_data.get("max", 100)
        threshold = viz_data.get("threshold", 100)
        title = viz_data.get("title", None)
        
        # Create gauge chart using visualization utility
        fig = create_gauge_chart(value, title=title, min_val=min_val, max_val=max_val, threshold=threshold)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_budget_vs_actual_chart(self, viz_data):
        """Create budget vs actual chart"""
        if "df" not in viz_data or viz_data["df"].empty:
            st.info("No hay datos suficientes para crear la visualización")
            return
            
        df = viz_data["df"]
        client_col = viz_data.get("client_col", "cliente")
        budget_col = viz_data.get("budget_col", "budget")
        actual_col = viz_data.get("actual_col", "actual")
        
        # Create budget vs actual chart using visualization utility
        fig = create_budget_vs_actual_chart(
            df,
            client_col=client_col,
            budget_col=budget_col,
            actual_col=actual_col
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Main function of the AI assistant
def main():
    # Layout with columns for better UI
    col1, col2 = st.columns([3, 1])

    with col2:
        st.markdown("### Acciones")
        if st.button("← Volver al Dashboard", use_container_width=True):
            # Safer navigation using relative paths
            st.switch_page("dashboard.py")
        
        st.markdown("### Ejemplos de preguntas")
        example_questions = [
            "¿Cuáles son nuestros top 5 clientes?",
            "¿Cómo se compara el presupuesto con la ejecución?",
            "¿Cuál es el margen bruto total?",
            "¿Qué industria genera más ingresos?",
            "¿Cómo han evolucionado los ingresos mensuales?",
            "¿Cuál fue el mes con mayor ingreso?"
        ]
        
        # Create buttons for example questions
        for question in example_questions:
            button_key = f"q_{question}"
            if st.button(question, key=button_key, use_container_width=True):
                st.session_state.new_query = question

    with col1:
        # Initialize AI components
        ai_assistant = IntelligentAIAssistant()
        
        # Initialize chat session
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "👋 Hola! Soy el Asistente AI de ActivaGroup. Puedo ayudarte a analizar los datos financieros, clientes, presupuesto y más. ¿Qué información necesitas hoy?"}
            ]

        # Track if a query was processed this session
        if "new_query" not in st.session_state:
            st.session_state.new_query = None
        
        # Display chat messages with improved styling
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        # Container for visualizations
        viz_container = st.container()
        
        # Get user input and generate response
        if prompt := st.chat_input("¿Qué quieres saber sobre los datos de tu empresa?"):
            st.session_state.new_query = prompt
        
        # Process query from either the chat input or an example button
        if st.session_state.new_query:
            query = st.session_state.new_query
            
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Display user message with fancy styling
            st.markdown(f'<div class="user-message">{query}</div>', unsafe_allow_html=True)
            
            # Generate and display assistant response
            message_placeholder = st.empty()
            message_placeholder.markdown('<div class="assistant-message">Analizando datos...</div>', unsafe_allow_html=True)
            
            try:
                # Process query and get response with visualization
                response = ai_assistant.process_query(query, viz_container)
                
                # Display response with fancy styling
                message_placeholder.markdown(f'<div class="assistant-message">{response}</div>', unsafe_allow_html=True)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_message = f"Lo siento, ocurrió un error al procesar tu consulta: {str(e)}"
                message_placeholder.markdown(f'<div class="assistant-message">{error_message}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
            
            # Reset new_query to allow for consecutive queries
            st.session_state.new_query = None
            
            # Rerun the app to update the UI
            st.rerun()

    # Enhanced information in the sidebar
    with st.sidebar:
        st.markdown("### ¿Qué puedo hacer?")
        st.markdown("""
        - Analizar ingresos y costos
        - Identificar top clientes
        - Analizar presupuesto vs. ejecución
        - Mostrar tendencias financieras
        - Identificar oportunidades de mejora
        - Analizar distribución por industria
        - Responder preguntas específicas sobre meses
        """)
        
        # Add a divider
        st.markdown('<div class="row-divider"></div>', unsafe_allow_html=True)
        
        # Add stats about the assistant
        st.markdown("### Estadísticas")
        
        total_queries = len(st.session_state.messages) // 2
        
        create_kpi_card(
            "Consultas Realizadas", 
            total_queries,
            icon='<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
        )

    # Footer with modern styling
    st.markdown("""
    <div class="footer">
        <p>ActivaGroup Business Intelligence Dashboard © 2025</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    