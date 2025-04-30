"""
ActivaGroup Data Connector
Handles connections to the Django backend API
"""
import requests
import pandas as pd
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define cached functions outside the class to avoid the unhashable self error
@st.cache_data(ttl=300)
def _get_clients_cached(base_url, endpoint):
    """Cached function to get client data from API"""
    try:
        response = requests.get(f"{base_url}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return data.get("data", [])
        logger.warning(f"Failed to get clients: {response.status_code}")
        return []
    except Exception as e:
        logger.error(f"Error fetching client data: {str(e)}")
        return []

@st.cache_data(ttl=300)
def _get_financial_summary_cached(base_url, endpoint):
    """Cached function to get financial summary data"""
    try:
        response = requests.get(f"{base_url}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return {
                    "summary": data.get("summary", {}),
                    "detailed": data.get("data", [])
                }
        logger.warning(f"Failed to get financial summary: {response.status_code}")
        return {"summary": {}, "detailed": []}
    except Exception as e:
        logger.error(f"Error fetching financial data: {str(e)}")
        return {"summary": {}, "detailed": []}

@st.cache_data(ttl=300)
def _get_combined_metrics_cached(base_url, endpoint):
    """Cached function to get combined client metrics"""
    try:
        response = requests.get(f"{base_url}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return data.get("data", [])
        logger.warning(f"Failed to get combined metrics: {response.status_code}")
        return []
    except Exception as e:
        logger.error(f"Error fetching combined metrics: {str(e)}")
        return []

class ActivaDataConnector:
    """
    Data connector for ActivaGroup Dashboard.
    Handles API connections to the Django backend.
    """
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        """Initialize with API base URL"""
        self.base_url = base_url
        self.endpoints = {
            "test": "/api/test-connection/",
            "clients": "/api/clients/",
            "financial": "/api/financial-summary/",
            "combined": "/api/combined-metrics/"
        }
    
    # Methods that use the cached functions
    def get_clients(self):
        """Get client data from API"""
        return _get_clients_cached(self.base_url, self.endpoints["clients"])
    
    def get_financial_summary(self):
        """Get financial summary data"""
        return _get_financial_summary_cached(self.base_url, self.endpoints["financial"])
    
    def get_combined_metrics(self):
        """Get combined client metrics"""
        return _get_combined_metrics_cached(self.base_url, self.endpoints["combined"])
    
    def build_dataframe(self, data_list):
        """Convert API list data to pandas DataFrame with proper types"""
        if not data_list:
            return pd.DataFrame()
        
        df = pd.DataFrame(data_list)
        
        # Convert any nested lists/dicts to string representation for display
        for col in df.columns:
            if df[col].dtype == 'object' and len(df) > 0:
                # Check if first non-null value is a list or dict
                first_val = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                if isinstance(first_val, (list, dict)):
                    df[col] = df[col].apply(lambda x: str(x) if x is not None else "")
        
        # Convert revenue/budget columns to numeric
        for col in df.columns:
            if ('facturacion' in col.lower() or 'presupuesto' in col.lower() or 
                'revenue' in col.lower() or 'budget' in col.lower()):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
            
    def get_monthly_revenue(self):
        """
        Calculate monthly revenue from combined metrics
        
        Returns:
            DataFrame with month and revenue columns
        """
        try:
            combined = self.get_combined_metrics()
            if not combined:
                return pd.DataFrame(columns=["month", "revenue", "month_order"])
                
            # Convert to DataFrame
            df = pd.DataFrame(combined)
            
            # Define months with order for proper sorting
            months = {
                'ene': {'name': 'Enero', 'order': 1}, 
                'feb': {'name': 'Febrero', 'order': 2}, 
                'mar': {'name': 'Marzo', 'order': 3}, 
                'abr': {'name': 'Abril', 'order': 4}, 
                'may': {'name': 'Mayo', 'order': 5}, 
                'jun': {'name': 'Junio', 'order': 6},
                'jul': {'name': 'Julio', 'order': 7}, 
                'ago': {'name': 'Agosto', 'order': 8}, 
                'sep': {'name': 'Septiembre', 'order': 9}, 
                'oct': {'name': 'Octubre', 'order': 10}, 
                'nov': {'name': 'Noviembre', 'order': 11}, 
                'dic': {'name': 'Diciembre', 'order': 12}
            }
            
            monthly_data = []
            
            # Check for each month's column
            for month_abbr, month_info in months.items():
                col_name = f"facturacion_{month_abbr}"
                if col_name in df.columns:
                    # Sum revenue across all clients for this month
                    total = df[col_name].sum()
                    monthly_data.append({
                        "month": month_info['name'],
                        "month_abbr": month_abbr,
                        "month_order": month_info['order'],
                        "revenue": total
                    })
            
            # If no monthly columns, try using the total column
            if not monthly_data and "facturacion_x" in df.columns:
                # Just create a single data point with the total
                monthly_data.append({
                    "month": "Total",
                    "month_abbr": "total",
                    "month_order": 0,
                    "revenue": df["facturacion_x"].sum()
                })
                
            result_df = pd.DataFrame(monthly_data)
            # Sort by month order
            if not result_df.empty:
                result_df = result_df.sort_values(by="month_order")
                
            return result_df
        except Exception as e:
            logger.error(f"Error calculating monthly revenue: {str(e)}")
            return pd.DataFrame(columns=["month", "revenue", "month_order"])
    
    def get_top_clients(self, limit=10, include_brands=False):
        """
        Get top clients by revenue
        
        Args:
            limit: Maximum number of clients to return
            include_brands: Whether to include brand information
            
        Returns:
            DataFrame with top clients
        """
        try:
            combined = self.get_combined_metrics()
            if not combined:
                return pd.DataFrame()
                
            # Convert to DataFrame
            df = pd.DataFrame(combined)
            
            # Determine revenue column
            if "facturacion_x" in df.columns:
                revenue_col = "facturacion_x"
            else:
                # Look for monthly columns and create a total
                monthly_cols = [col for col in df.columns if col.startswith("facturacion_")]
                if monthly_cols:
                    df["total_revenue"] = df[monthly_cols].sum(axis=1)
                    revenue_col = "total_revenue"
                else:
                    logger.warning("No revenue columns found")
                    return pd.DataFrame()
            
            # Sort by revenue and get top clients
            top_clients = df.sort_values(by=revenue_col, ascending=False).head(limit)
            
            # Select relevant columns
            cols_to_keep = ["cliente", "industria", revenue_col]
            
            # Add budget column if available
            if "presupuesto_x" in df.columns:
                cols_to_keep.append("presupuesto_x")
            
            # Add brands if requested and available
            if include_brands and "marcas" in df.columns:
                cols_to_keep.append("marcas")
            
            # Return only the needed columns
            result = top_clients[cols_to_keep].copy()
            
            # Rename columns for clarity
            result = result.rename(columns={
                revenue_col: "revenue",
                "presupuesto_x": "budget" if "presupuesto_x" in cols_to_keep else None
            })
            
            return result
        except Exception as e:
            logger.error(f"Error getting top clients: {str(e)}")
            return pd.DataFrame()
    
    def get_industry_breakdown(self):
        """
        Get revenue breakdown by industry
        
        Returns:
            DataFrame with industry and revenue
        """
        try:
            combined = self.get_combined_metrics()
            if not combined:
                return pd.DataFrame()
                
            # Convert to DataFrame
            df = pd.DataFrame(combined)
            
            # Check if we have both industry and revenue columns
            if "industria" not in df.columns:
                logger.warning("No industry column found")
                return pd.DataFrame()
                
            # Determine revenue column
            if "facturacion_x" in df.columns:
                revenue_col = "facturacion_x"
            else:
                # Look for monthly columns and create a total
                monthly_cols = [col for col in df.columns if col.startswith("facturacion_")]
                if monthly_cols:
                    df["total_revenue"] = df[monthly_cols].sum(axis=1)
                    revenue_col = "total_revenue"
                else:
                    logger.warning("No revenue columns found")
                    return pd.DataFrame()
            
            # Group by industry and sum revenue
            industry_data = df.groupby("industria")[revenue_col].sum().reset_index()
            
            # Sort by revenue descending
            industry_data = industry_data.sort_values(by=revenue_col, ascending=False)
            
            # Rename columns for clarity
            industry_data = industry_data.rename(columns={
                revenue_col: "revenue",
                "industria": "industry"
            })
            
            return industry_data
        except Exception as e:
            logger.error(f"Error getting industry breakdown: {str(e)}")
            return pd.DataFrame()
    
    def get_budget_vs_actual(self):
        """
        Compare budget and actual revenue
        
        Returns:
            DataFrame with client, budget, actual, and variance
        """
        try:
            combined = self.get_combined_metrics()
            if not combined:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(combined)
            
            # Check if we have budget and revenue columns
            if "presupuesto_x" not in df.columns:
                logger.warning("No budget column found")
                return pd.DataFrame()
                
            if "facturacion_x" not in df.columns:
                logger.warning("No revenue column found")
                return pd.DataFrame()
            
            # Create budget vs actual DataFrame
            budget_df = df[["cliente", "industria", "presupuesto_x", "facturacion_x"]].copy()
            
            # Calculate variance and utilization
            budget_df["variance"] = budget_df["facturacion_x"] - budget_df["presupuesto_x"]
            budget_df["utilization"] = (budget_df["facturacion_x"] / budget_df["presupuesto_x"] * 100).round(2)
            
            # Clean up NaN values
            budget_df["utilization"] = budget_df["utilization"].fillna(0)
            budget_df["variance"] = budget_df["variance"].fillna(0)
            
            # Rename columns for clarity
            budget_df = budget_df.rename(columns={
                "facturacion_x": "actual",
                "presupuesto_x": "budget"
            })
            
            # Sort by actual revenue descending
            budget_df = budget_df.sort_values(by="actual", ascending=False)
            
            return budget_df
        except Exception as e:
            logger.error(f"Error comparing budget and actual: {str(e)}")
            return pd.DataFrame()
    
    def get_client_count_by_industry(self):
        """
        Count clients per industry
        
        Returns:
            DataFrame with industry and client count
        """
        try:
            combined = self.get_combined_metrics()
            if not combined:
                return pd.DataFrame()
                
            # Convert to DataFrame
            df = pd.DataFrame(combined)
            
            # Check if we have industry column
            if "industria" not in df.columns:
                logger.warning("No industry column found")
                return pd.DataFrame()
            
            # Group by industry and count clients
            industry_counts = df.groupby("industria").size().reset_index(name="count")
            
            # Sort by count descending
            industry_counts = industry_counts.sort_values(by="count", ascending=False)
            
            # Rename columns for clarity
            industry_counts = industry_counts.rename(columns={
                "industria": "industry"
            })
            
            return industry_counts
        except Exception as e:
            logger.error(f"Error counting clients by industry: {str(e)}")
            return pd.DataFrame()
    
    def get_brand_data(self):
        """
        Get brand data from client records
        
        Returns:
            DataFrame with client, brand, and industry
        """
        try:
            combined = self.get_combined_metrics()
            if not combined:
                return pd.DataFrame()
                
            # Convert to DataFrame
            df = pd.DataFrame(combined)
            
            # Check if we have brands column
            if "marcas" not in df.columns:
                logger.warning("No brands column found")
                return pd.DataFrame()
            
            # Explode the brands column to get one row per brand
            result = []
            
            for _, row in df.iterrows():
                cliente = row.get("cliente", "Unknown")
                industria = row.get("industria", "Unknown")
                marcas = row.get("marcas", [])
                
                if not isinstance(marcas, list):
                    continue
                    
                for marca in marcas:
                    result.append({
                        "cliente": cliente,
                        "industria": industria,
                        "marca": marca
                    })
            
            # Convert to DataFrame
            brands_df = pd.DataFrame(result)
            
            return brands_df
        except Exception as e:
            logger.error(f"Error processing brand data: {str(e)}")
            return pd.DataFrame()
    
    def get_profit_loss_data(self):
        """
        Get profit and loss data
        
        Returns:
            DataFrame with profit and loss data
        """
        try:
            financial = self.get_financial_summary()
            if not financial or not financial.get("detailed"):
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(financial.get("detailed"))
            
            return df
        except Exception as e:
            logger.error(f"Error getting profit loss data: {str(e)}")
            return pd.DataFrame()
        