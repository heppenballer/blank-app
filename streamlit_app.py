import streamlit as st
import pandas as pd
from datetime import datetime

def analyze_columns(df):
    """Automatically detect and analyze available columns."""
    analysis = {}
    
    # Convert all column names to lowercase for easier matching
    df.columns = df.columns.str.strip().str.lower()
    cols = set(df.columns)
    
    # Detect quantity columns
    qty_cols = [c for c in cols if any(kw in c for kw in ['qty', 'quantity', 'ship'])]
    analysis['quantity_col'] = qty_cols[0] if qty_cols else None
    
    # Detect price columns
    price_cols = [c for c in cols if any(kw in c for kw in ['price', 'cost', 'amount'])]
    analysis['price_col'] = price_cols[0] if price_cols else None
    
    # Detect date columns
    date_cols = [c for c in cols if any(kw in c for kw in ['date', 'time', 'day', 'month'])]
    analysis['date_col'] = date_cols[0] if date_cols else None
    
    # Detect product info
    product_cols = [c for c in cols if any(kw in c for kw in ['product', 'item', 'sku', 'part'])]
    analysis['product_col'] = product_cols[0] if product_cols else None
    
    return analysis

def auto_generate_insights(df, col_map):
    """Generate insights based on detected columns."""
    insights = []
    processed_df = df.copy()
    
    try:
        # Revenue calculation if we have quantity and price
        if col_map['quantity_col'] and col_map['price_col']:
            processed_df['revenue'] = processed_df[col_map['quantity_col'] * processed_df[col_map['price_col']]
            total_rev = processed_df['revenue'].sum()
            insights.append(f"Total Revenue: ${total_rev:,.2f}")
            
            # Revenue by product if available
            if col_map['product_col']:
                product_rev = processed_df.groupby(col_map['product_col'])['revenue'].sum()
                insights.append("\nRevenue by Product:")
                for product, rev in product_rev.items():
                    insights.append(f"- {product}: ${rev:,.2f}")
        
        # Time trends if date available
        if col_map['date_col']:
            try:
                processed_df['date'] = pd.to_datetime(processed_df[col_map['date_col']])
                monthly = processed_df.resample('M', on='date')['revenue'].sum()
                insights.append("\nMonthly Revenue Trend:")
                insights.append(monthly.to_string())
            except Exception as e:
                insights.append(f"\nCould not analyze trends: {str(e)}")
                
    except Exception as e:
        insights.append(f"Error during analysis: {str(e)}")
    
    return insights, processed_df

def main():
    st.set_page_config("Smart Sales Analyzer", layout="wide")
    st.title("🔍 Auto-Detecting Sales Analyzer")
    
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            st.success(f"File loaded successfully with {len(df)} rows")
            
            # Auto-detect columns
            col_map = analyze_columns(df)
            
            st.subheader("Detected Columns:")
            st.write(col_map)
            
            # Generate and display insights
            insights, processed_df = auto_generate_insights(df, col_map)
            
            st.subheader("Generated Insights")
            for insight in insights:
                st.write(insight)
                
            # Show processed data
            with st.expander("View Processed Data"):
                st.dataframe(processed_df.head())
                
            # Download results
            st.download_button(
                "Download Analysis",
                processed_df.to_csv(index=False),
                "sales_analysis.csv"
            )
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

if __name__ == "__main__":
    main()
