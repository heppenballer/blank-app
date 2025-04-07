import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def calculate_revenue_metrics(data):
    """Calculate revenue-related metrics."""
    metrics = []
    if 'Qty Shipped' in data.columns and 'Price' in data.columns:
        data['Total Revenue'] = data['Qty Shipped'] * data['Price']
        total_revenue = data['Total Revenue'].sum()
        metrics.append(f"Total revenue: ${total_revenue:,.2f}")
    return metrics

def calculate_product_metrics(data):
    """Calculate product-related metrics."""
    metrics = []
    if 'Product Type' in data.columns and 'Qty Shipped' in data.columns:
        shipped_by_type = data.groupby('Product Type')['Qty Shipped'].sum().reset_index()
        metrics.append("Total shipped quantity by product type:")
        for _, row in shipped_by_type.iterrows():
            metrics.append(f"- {row['Product Type']}: {row['Qty Shipped']} units")
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

def generate_insights(data):
    """Generate business insights from the data."""
    insights = []
    
    # Add timestamp
    insights.append(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Calculate metrics
    insights.extend(calculate_revenue_metrics(data))
    insights.extend(calculate_product_metrics(data))
    insights.extend(calculate_trends(data))
    
    return insights

def display_visualizations(data):
    """Display data visualizations."""
    if 'Date Ordered' in data.columns and 'Total Revenue' in data.columns:
        st.subheader("Revenue Over Time")
        try:
            revenue_by_date = data.groupby('Date Ordered')['Total Revenue'].sum().reset_index()
            st.line_chart(revenue_by_date.set_index('Date Ordered'))
        except Exception as e:
            st.error(f"Could not generate revenue chart: {str(e)}")
    
    if 'Product Type' in data.columns and 'Qty Shipped' in data.columns:
        st.subheader("Quantity Shipped by Product Type")
        try:
            shipped_by_type = data.groupby('Product Type')['Qty Shipped'].sum().reset_index()
            st.bar_chart(shipped_by_type.set_index('Product Type'))
        except Exception as e:
            st.error(f"Could not generate product type chart: {str(e)}")

def main():
    st.title('Quantivo - Business Insights Generator')
    st.markdown("Upload your sales data to generate automated business insights.")
    
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])
    
    if uploaded_file:
        try:
            with st.spinner('Processing data...'):
                df = pd.read_excel(uploaded_file)
                
                st.success("Data loaded successfully!")
                st.subheader("Data Preview")
                st.dataframe(df.head())
                
                insights = generate_insights(df)
                
                st.subheader("Generated Insights")
                for insight in insights:
                    st.write(f"- {insight}")
                
                display_visualizations(df)
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()
