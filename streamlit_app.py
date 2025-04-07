import streamlit as st
import pandas as pd
from datetime import datetime

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
        
        # Add average metrics
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
                
                # Add monthly breakdown
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
                
                # Add price distribution
                if 'Price' in data.columns:
                    st.subheader("Price Distribution by Product Type")
                    price_by_type = data.groupby('Product Type')['Price'].mean().reset_index()
                    st.bar_chart(price_by_type, x='Product Type', y='Price')
            except Exception as e:
                st.error(f"Could not generate product type chart: {str(e)}")

def main():
    # Configure page
    st.set_page_config(page_title="Quantivo Insights", layout="wide")
    
    # Custom styling
    st.markdown("""
        <style>
            .big-font { font-size:20px !important; }
            .metric-box { padding: 10px; border-radius: 5px; background: #f0f2f6; margin: 10px 0; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title('📊 Quantivo - Business Insights Generator')
    st.markdown("Upload your sales data to generate automated business insights.")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"], 
                                   help="Upload your Team Project Excel file with sales data")
    
    if uploaded_file:
        try:
            with st.spinner('Processing data...'):
                # Use openpyxl engine for xlsx files
                if uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Generate insights
                revenue_metrics, df = calculate_revenue_metrics(df)
                product_metrics = calculate_product_metrics(df)
                trend_metrics = calculate_trends(df)
                
                # Display results
                st.success("✅ Data loaded successfully!")
                
                # Data preview
                with st.expander("🔍 Data Preview", expanded=False):
                    st.dataframe(df.head())
                
                # Metrics columns
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
                
                # Download button for processed data
                st.download_button(
                    label="📥 Download Processed Data",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name='processed_sales_data.csv',
                    mime='text/csv'
                )
                
        except ImportError:
            st.error("""
            ❌ Required package not found. Please install openpyxl by running:
            ```
            pip install openpyxl
            ```
            or
            ```
            pip install -r requirements.txt
            ```
            """)
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")

if __name__ == "__main__":
    main()
