import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to process the data and generate insights
def generate_insights(data):
    insights = []

    # Calculate Total Revenue (Qty Shipped * Price)
    if 'Qty Shipped' in data.columns and 'Price' in data.columns:
        data['Total Revenue'] = data['Qty Shipped'] * data['Price']
        
        total_revenue = data['Total Revenue'].sum()
        insights.append(f"Total revenue: ${total_revenue:,.2f}")

    # Calculate total shipped quantity by product type
    if 'Product Type' in data.columns and 'Qty Shipped' in data.columns:
        shipped_by_type = data.groupby('Product Type')['Qty Shipped'].sum().reset_index()
        insights.append("Total shipped quantity by product type:")
        for _, row in shipped_by_type.iterrows():
            insights.append(f"- {row['Product Type']}: {row['Qty Shipped']} units")
    
    # Calculate average price and shipped quantity per product type
    if 'Product Type' in data.columns and 'Price' in data.columns and 'Qty Shipped' in data.columns:
        avg_by_type = data.groupby('Product Type').agg({'Price': 'mean', 'Qty Shipped': 'mean'}).reset_index()
        insights.append("Average price and quantity per product type:")
        for _, row in avg_by_type.iterrows():
            insights.append(f"- {row['Product Type']}: Average price = ${row['Price']:.2f}, Average qty shipped = {row['Qty Shipped']:.2f} units")
    
    # Sales trends: Compare most recent orders with earlier ones (e.g., last month vs previous month)
    if 'Date Ordered' in data.columns:
        data['Date Ordered'] = pd.to_datetime(data['Date Ordered'])
        last_month = data[data['Date Ordered'] > pd.Timestamp.now() - pd.DateOffset(months=1)]
        previous_month = data[data['Date Ordered'] <= pd.Timestamp.now() - pd.DateOffset(months=1)]
        
        last_month_revenue = last_month['Total Revenue'].sum() if not last_month.empty else 0
        previous_month_revenue = previous_month['Total Revenue'].sum() if not previous_month.empty else 0
        
        if previous_month_revenue > 0:
            revenue_growth = ((last_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
            insights.append(f"Revenue change from last month to previous month: {revenue_growth:.2f}%")
        else:
            insights.append("No previous month's data available for comparison.")

    # Optional: Plot a simple chart of total revenue over time
    if 'Date Ordered' in data.columns and 'Total Revenue' in data.columns:
        revenue_by_date = data.groupby('Date Ordered')['Total Revenue'].sum()
        plt.figure(figsize=(10, 6))
        revenue_by_date.plot(kind='line')
        plt.title("Total Revenue Over Time")
        plt.xlabel("Date")
        plt.ylabel("Revenue ($)")
        st.pyplot(plt)
    
    return insights


# Streamlit UI
st.title('Quantivo - Business Insights Generator')

# Upload file
uploaded_file = st.file_uploader("Upload your Team Project Excel file", type=["xlsx"])

if uploaded_file:
    # Read the file and load into pandas DataFrame
    df = pd.read_excel(uploaded_file)

    # Show a preview of the data (optional)
    st.write("Data Preview:", df.head())

    # Generate insights from the data
    insights = generate_insights(df)

    # Display insights
    st.subheader("Generated Insights")
    for insight in insights:
        st.write(f"- {insight}")

