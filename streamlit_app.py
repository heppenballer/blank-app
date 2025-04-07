import streamlit as st
import pandas as pd
from datetime import datetime

def check_dependencies():
    """Check for required dependencies."""
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
        
        # Add revenue by product type
        revenue_by_type = data.groupby('Product Type')['Total Revenue'].sum().reset_index()
        metrics.append("\nRevenue by product type:")
        for _, row in revenue_by_type.iterrows():
            metrics.append(f"- {row['Product Type']}: ${row['Total Revenue']:,.2f}")
    return metrics, data

def calculate_product_metrics(data):
    """Calculate product-related metrics."""
    metrics = []
    if 'Product Type' in data.columns and 'Qty Shipped' in data.columns:
        # Total shipped by product type
        shipped_by_type = data.groupby('Product Type')['Qty Shipped'].sum().reset_index()
        metrics.append("Total shipped quantity by product type:")
        for _, row in shipped_by_type.iterrows():
            metrics.append(f"- {row['Product Type']}: {row['Qty Shipped']} units")
        
        # Average metrics
        avg_by_type = data.groupby('Product Type').agg({
            'Price': 'mean', 
            'Qty Shipped': 'mean',
            'Pieces per Carton': 'mean'
        }).reset_index()
        
        metrics.append("\nAverage metrics per product type:")
        for _, row in avg_by_type.iterrows():
            metrics.append(
                f"- {row['Product Type']}: "
                f"Price = ${row['Price']:.2f}, "
                f"Qty shipped = {row['Qty Shipped']:.2f}, "
                f"Pieces/carton = {row['Pieces per Carton']:.2f}"
            )
    return metrics

def calculate_trends(data):
    """Calculate sales trends over time."""
    metrics = []
    if 'Date Ordered' in data.columns and 'Total Revenue' in data.columns:
        try:
            data['Month'] = data['Date Ordered'].dt.to_period('M')
            monthly_revenue = data.groupby('Month')['Total Revenue'].sum()
            
            if len(monthly_revenue) > 1:
                current_month = monthly_revenue.iloc[-1]
                previous_month = monthly_revenue.iloc[-2]
                growth = ((current_month - previous_month) / previous_month) * 100
                metrics.append(
                    f"Month-over-month revenue change: "
                    f"{growth:.2f}% "
                    f"(${previous_month:,.2f} → ${current_month:,.2f})"
                )
            else:
                metrics.append("Need at least 2 months of data for trend analysis")
                
        except Exception as e:
            metrics.append(f"Trend calculation error: {str(e)}")
    return metrics

def display_visualizations(data):
    """Display interactive visualizations."""
    if 'Date Ordered' in data.columns and 'Total Revenue' in data.columns:
        with st.expander("📈 Revenue Trends", expanded=True):
            # Monthly revenue breakdown
            monthly = data.set_index('Date Ordered')['Total Revenue'].resample('M').sum().reset_index()
            st.subheader("Monthly Revenue")
            st.bar_chart(monthly, x='Date Ordered', y='Total Revenue')
            
            # Cumulative revenue
            monthly['Cumulative'] = monthly['Total Revenue'].cumsum()
            st.subheader("Cumulative Revenue")
            st.line_chart(monthly, x='Date Ordered', y='Cumulative')
    
    if 'Product Type' in data.columns:
        with st.expander("📦 Product Analysis", expanded=True):
            # Product type distribution
            product_dist = data['Product Type'].value_counts().reset_index()
            product_dist.columns = ['Product Type', 'Count']
            st.subheader("Product Type Distribution")
            st.bar_chart(product_dist, x='Product Type', y='Count')
            
            # Price distribution
            if 'Price' in data.columns:
                st.subheader("Price Distribution")
                st.bar_chart(
                    data.groupby('Product Type')['Price'].mean().reset_index(),
                    x='Product Type', 
                    y='Price'
                )

def main():
    # Page configuration
    st.set_page_config(
        page_title="Quantivo Sales Analyzer",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check dependencies
    if not check_dependencies():
        st.stop()
    
    # Custom styling
    st.markdown("""
        <style>
            .metric-box {
                padding: 15px;
                border-radius: 10px;
                background: #f8f9fa;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .highlight {
                background-color: #fffde7;
                padding: 2px 5px;
                border-radius: 3px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.title('📊 Sales Data Analyzer')
    st.markdown("Upload your sales Excel file to generate insights and visualizations.")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose Excel File", 
        type=["xlsx", "xls"],
        help="Should contain: Order Number, Part Number, Qty Shipped, Product Type, Pieces per Carton, Date Ordered, Price"
    )
    
    if uploaded_file is None:
        st.info("ℹ️ Please upload a file to begin analysis")
        return
    
    try:
        with st.spinner('Analyzing data...'):
            # Read file
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            else:
                df = pd.read_excel(uploaded_file)
            
            # Data validation
            required_cols = {
                'Order Number', 'Part Number', 'Qty Shipped', 
                'Product Type', 'Pieces per Carton', 'Date Ordered', 'Price'
            }
            missing_cols = required_cols - set(df.columns)
            
            if missing_cols:
                st.error(f"Missing columns: {', '.join(missing_cols)}")
                st.info("Your file must contain these exact column names:")
                st.code(", ".join(required_cols))
                return
            
            # Data cleaning
            df['Date Ordered'] = pd.to_datetime(df['Date Ordered'])
            df = df.dropna(subset=['Qty Shipped', 'Price', 'Date Ordered'])
            
            # Show data summary
            st.success(f"✅ Successfully loaded {len(df)} records")
            with st.expander("🔍 View Raw Data", expanded=False):
                st.dataframe(df.head())
                st.write(f"Date range: {df['Date Ordered'].min().date()} to {df['Date Ordered'].max().date()}")
            
            # Process data
            revenue_metrics, df = calculate_revenue_metrics(df)
            product_metrics = calculate_product_metrics(df)
            trend_metrics = calculate_trends(df)
            
            # Display metrics
            st.header("Key Metrics")
            
            cols = st.columns(3)
            with cols[0]:
                st.subheader("Revenue")
                for metric in revenue_metrics[:3]:
                    st.markdown(f'<div class="metric-box">{metric}</div>', unsafe_allow_html=True)
            
            with cols[1]:
                st.subheader("Products")
                for metric in product_metrics[:3]:
                    st.markdown(f'<div class="metric-box">{metric}</div>', unsafe_allow_html=True)
            
            with cols[2]:
                st.subheader("Trends")
                for metric in trend_metrics:
                    st.markdown(f'<div class="metric-box">{metric}</div>', unsafe_allow_html=True)
            
            # Show detailed metrics
            with st.expander("📋 Detailed Metrics", expanded=False):
                st.write("### Revenue Details")
                for metric in revenue_metrics[3:]:
                    st.markdown(f'- {metric}')
                
                st.write("### Product Details")
                for metric in product_metrics[3:]:
                    st.markdown(f'- {metric}')
            
            # Visualizations
            display_visualizations(df)
            
            # Data export
            st.download_button(
                label="📥 Download Processed Data (CSV)",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='processed_sales_data.csv',
                mime='text/csv'
            )
    
    except Exception as e:
        st.error(f"""
        ❌ Error processing file:
        {str(e)}
        
        Please check:
        1. File is a valid Excel document
        2. Contains all required columns
        3. Has numeric values in Qty Shipped and Price columns
        """)

if __name__ == "__main__":
    main()
