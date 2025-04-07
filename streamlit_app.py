import streamlit as st
import pandas as pd
from datetime import datetime

def check_dependencies():
    """Check for required dependencies and display installation instructions if missing."""
    try:
        import openpyxl
        return True
    except ImportError:
        st.error("""
        ❌ Missing required package: openpyxl
        
        Please install it by running:
        ```
        pip install openpyxl
        ```
        or create a requirements.txt file with:
        ```
        streamlit>=1.0
        pandas>=1.0
        openpyxl>=3.0
        ```
        and then run:
        ```
        pip install -r requirements.txt
        ```
        """)
        return False

def calculate_revenue_metrics(data):
    """Calculate revenue-related metrics."""
    metrics = []
    if 'Qty Shipped' in data.columns and 'Price' in data.columns:
        data['Total Revenue'] = data['Qty Shipped'] * data['Price']
        total_revenue = data['Total Revenue'].sum()
        metrics.append(f"Total revenue: ${total_revenue:,.2f}")
    return metrics, data

def calculate_product_metrics(data):
    """Calculate product-related metrics."""
    metrics = []
    if 'Product Type' in data.columns and 'Qty Shipped' in data.columns:
        shipped_by_type = data.groupby('Product Type')['Qty Shipped'].sum().reset_index()
        metrics.append("Total shipped quantity by product type:")
        for _, row in shipped_by_type.iterrows():
            metrics.append(f"- {row['Product Type']}: {row['Qty Shipped']} units")
        
        avg_by_type = data.groupby('Product Type').agg({'Price': 'mean', 'Qty Shipped': 'mean'}).reset_index()
        metrics.append("\nAverage price and quantity per product type:")
        for _, row in avg_by_type.iterrows():
            metrics.append(f"- {row['Product Type']}: Average price = ${row['Price']:.2f}, Average qty shipped = {row['Qty Shipped']:.2f} units")
    return metrics

def calculate_trends(data):
    """Calculate sales trends over time."""
    metrics = []
    if 'Date Ordered' in data.columns and 'Total Revenue' in data.columns:
        try:
            data['Date Ordered'] = pd.to_datetime(data['Date Ordered'])
            last_month = data[data['Date Ordered'] > pd.Timestamp.now() - pd.DateOffset(months=1)]
            previous_month = data[data['Date Ordered'] <= pd.Timestamp.now() - pd.DateOffset(months=1)]
            
            last_month_revenue = last_month['Total Revenue'].sum() if not last_month.empty else 0
            previous_month_revenue = previous_month['Total Revenue'].sum() if not previous_month.empty else 0
            
            if previous_month_revenue > 0:
                revenue_growth = ((last_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
                metrics.append(f"Revenue change from last month to previous month: {revenue_growth:.2f}%")
            else:
                metrics.append("No previous month's data available for comparison.")
        except Exception as e:
            metrics.append(f"Could not calculate trends: {str(e)}")
    return metrics

def display_visualizations(data):
    """Display data visualizations using Streamlit native charts."""
    if 'Date Ordered' in data.columns and 'Total Revenue' in data.columns:
        with st.expander("📈 Revenue Trends", expanded=True):
            st.subheader("Revenue Over Time")
            try:
                revenue_by_date = data.groupby('Date Ordered')['Total Revenue'].sum().reset_index()
                st.line_chart(revenue_by_date, x='Date Ordered', y='Total Revenue')
                
                monthly_revenue = data.set_index('Date Ordered')['Total Revenue'].resample('M').sum().reset_index()
                st.bar_chart(monthly_revenue, x='Date Ordered', y='Total Revenue')
            except Exception as e:
                st.error(f"Could not generate revenue chart: {str(e)}")
    
    if 'Product Type' in data.columns and 'Qty Shipped' in data.columns:
        with st.expander("📦 Product Analysis", expanded=True):
            st.subheader("Quantity Shipped by Product Type")
            try:
                shipped_by_type = data.groupby('Product Type')['Qty Shipped'].sum().reset_index()
                st.bar_chart(shipped_by_type, x='Product Type', y='Qty Shipped')
                
                if 'Price' in data.columns:
                    st.subheader("Price Distribution by Product Type")
                    price_by_type = data.groupby('Product Type')['Price'].mean().reset_index()
                    st.bar_chart(price_by_type, x='Product Type', y='Price')
            except Exception as e:
                st.error(f"Could not generate product type chart: {str(e)}")

def main():
    # Configure page
    st.set_page_config(page_title="Quantivo Insights", layout="wide")
    
    # Check dependencies first
    if not check_dependencies():
        st.stop()  # Don't proceed if openpyxl is missing
    
    # Custom styling
    st.markdown("""
        <style>
            .big-font { font-size:20px !important; }
            .metric-box { padding: 10px; border-radius: 5px; background: #f0f2f6; margin: 10px 0; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title('📊 Quantivo - Business Insights Generator')
    st.markdown("Upload your sales data to generate automated business insights.")
    
    # File uploader with enhanced debugging
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
    
    if uploaded_file is None:
        st.warning("Please upload an Excel file to begin analysis")
        return
    
    try:
        with st.spinner('Processing data...'):
            # Read file with explicit engine
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            else:
                df = pd.read_excel(uploaded_file)
            
            # DEBUG: Show file info
            st.success(f"✅ File loaded successfully! Rows: {len(df)}")
            with st.expander("🔍 Raw Data Preview", expanded=False):
                st.dataframe(df.head())
                st.write("Columns detected:", df.columns.tolist())
            
            # Validate required columns
            required_columns = {'Qty Shipped', 'Price', 'Product Type', 'Date Ordered'}
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                st.error(f"❌ Missing required columns: {missing_columns}")
                st.info("Please ensure your file contains these exact column names:")
                st.code(", ".join(required_columns))
                return
            
            # Process data
            df['Date Ordered'] = pd.to_datetime(df['Date Ordered'])  # Ensure datetime
            df = df.dropna(subset=list(required_columns))  # Remove rows with missing data
            
            # Generate insights
            revenue_metrics, df = calculate_revenue_metrics(df)
            product_metrics = calculate_product_metrics(df)
            trend_metrics = calculate_trends(df)
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💰 Revenue Metrics")
                for metric in revenue_metrics:
                    st.markdown(f'<div class="metric-box">{metric}</div>', unsafe_allow_html=True)
                
                st.subheader("📅 Trends")
                for metric in trend_metrics:
                    st.markdown(f'<div class="metric-box">{metric}</div>', unsafe_allow_html=True)
            
            with col2:
                st.subheader("📦 Product Metrics")
                for metric in product_metrics:
                    st.markdown(f'<div class="metric-box">{metric}</div>', unsafe_allow_html=True)
            
            # Visualizations
            display_visualizations(df)
            
            # Download processed data
            st.download_button(
                label="📥 Download Processed Data",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='processed_sales_data.csv',
                mime='text/csv'
            )
            
    except Exception as e:
        st.error(f"""
        ❌ Critical error processing file:
        {str(e)}
        
        Please check:
        1. File is not password protected
        2. Contains valid Excel data
        3. Has at least 5 rows of data
        """)

if __name__ == "__main__":
    main()
