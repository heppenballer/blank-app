import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime

# ========================
# STATISTICAL ANALYSIS MODULE
# ========================

class SalesStatistics:
    @staticmethod
    def basic_descriptive_stats(df, numeric_cols):
        """Calculate basic descriptive statistics"""
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                'mean': np.mean(df[col]),
                'median': np.median(df[col]),
                'std_dev': np.std(df[col]),
                'min': np.min(df[col]),
                'max': np.max(df[col]),
                'skewness': stats.skew(df[col]),
                'kurtosis': stats.kurtosis(df[col])
            }
        return stats
    
    @staticmethod
    def time_series_analysis(df, date_col, value_col):
        """Analyze time series components"""
        try:
            df = df.set_index(date_col).sort_index()
            return {
                'monthly_growth_rate': df[value_col].pct_change().mean(),
                'rolling_3mo_avg': df[value_col].rolling(window=3).mean().to_dict(),
                'seasonality': df[value_col].groupby(df.index.month).mean().to_dict()
            }
        except Exception as e:
            return f"Time series analysis failed: {str(e)}"
    
    @staticmethod
    def correlation_analysis(df, cols):
        """Calculate correlation matrix"""
        return df[cols].corr()
    
    @staticmethod
    def price_elasticity(df, price_col, quantity_col):
        """Calculate basic price elasticity"""
        try:
            log_price = np.log(df[price_col])
            log_quantity = np.log(df[quantity_col])
            elasticity = stats.linregress(log_price, log_quantity).slope
            return elasticity
        except:
            return None

# ========================
# MAIN APPLICATION CODE
# ========================

def analyze_columns(df):
    """Column detection logic (unchanged)"""
    # ... (keep your existing analyze_columns function) ...
    return analysis

def auto_generate_insights(df, col_map):
    """Insight generation with statistical analysis"""
    insights = []
    processed_df = df.copy()
    stats_results = {}
    
    try:
        # Revenue calculation
        if col_map['quantity_col'] and col_map['price_col']:
            processed_df['revenue'] = processed_df[col_map['quantity_col']] * processed_df[col_map['price_col']]
            
            # Initialize statistics module
            stats_analyzer = SalesStatistics()
            
            # 1. Basic descriptive stats
            numeric_cols = [col_map['quantity_col'], col_map['price_col'], 'revenue']
            stats_results['descriptive'] = stats_analyzer.basic_descriptive_stats(processed_df, numeric_cols)
            
            # 2. Time series analysis
            if col_map['date_col']:
                stats_results['time_series'] = stats_analyzer.time_series_analysis(
                    processed_df, 
                    col_map['date_col'], 
                    'revenue'
                )
            
            # 3. Correlation analysis
            stats_results['correlation'] = stats_analyzer.correlation_analysis(
                processed_df,
                [col_map['quantity_col'], col_map['price_col'], 'revenue']
            )
            
            # 4. Price elasticity
            stats_results['price_elasticity'] = stats_analyzer.price_elasticity(
                processed_df,
                col_map['price_col'],
                col_map['quantity_col']
            )
            
        # ... (rest of your existing insight generation code) ...
        
    except Exception as e:
        insights.append(f"Error during analysis: {str(e)}")
    
    return insights, processed_df, stats_results

def display_statistical_results(stats_results):
    """Display the statistical analysis in Streamlit"""
    with st.expander("📊 Advanced Statistical Analysis", expanded=True):
        st.subheader("Descriptive Statistics")
        st.write(pd.DataFrame(stats_results['descriptive']).T)
        
        if 'time_series' in stats_results:
            st.subheader("Time Series Analysis")
            st.write("Monthly Growth Rate:", stats_results['time_series'].get('monthly_growth_rate', 'N/A'))
            
            st.write("Seasonal Patterns:")
            st.bar_chart(pd.DataFrame.from_dict(
                stats_results['time_series'].get('seasonality', {}), 
                orient='index'
            ))
        
        st.subheader("Correlation Matrix")
        st.write(stats_results['correlation'])
        
        if stats_results['price_elasticity']:
            st.subheader("Price Elasticity")
            st.write(f"Estimated Elasticity: {stats_results['price_elasticity']:.2f}")
            st.caption("Values < -1 indicate elastic demand")

def main():
    st.set_page_config("Sales Analyzer Pro", layout="wide")
    st.title("📈 Sales Data Analyzer with Statistics")
    
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            col_map = analyze_columns(df)
            
            # Generate insights and stats
            insights, processed_df, stats_results = auto_generate_insights(df, col_map)
            
            # Display results
            display_statistical_results(stats_results)
            
            # ... (rest of your existing display code) ...
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
