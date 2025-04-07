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
    
    # Detect product info - prioritize part number if exists
    part_cols = [c for c in cols if any(kw in c for kw in ['part', 'sku', 'model'])]
    product_cols = [c for c in cols if any(kw in c for kw in ['product', 'item', 'name'])]
    analysis['product_col'] = part_cols[0] if part_cols else (product_cols[0] if product_cols else None)
    
    return analysis

def generate_product_insights(product_rev):
    """Generate actionable business insights about top products"""
    insights = []
    
    if len(product_rev) == 0:
        return ["No product revenue data available for analysis"]
    
    total_rev = product_rev['Revenue'].sum()
    top_product = product_rev.iloc[0]
    top_5 = product_rev.head(5)
    bottom_5 = product_rev.tail(5)
    
    # Revenue concentration analysis
    top_5_rev = top_5['Revenue'].sum()
    top_5_percent = (top_5_rev / total_rev) * 100
    insights.append(
        f"{top_5_percent:.1f}% of total revenue comes from just the top 5 products. "
        "Consider expanding marketing efforts for these winners through:\n"
        "- Targeted advertising campaigns\n"
        "- Bundled product deals\n"
        "- Limited-time promotions\n"
        "- Customer loyalty incentives"
    )
    
    # Top product spotlight
    top_percent = (top_product['Revenue'] / total_rev) * 100
    insights.append(
        f"Our #1 product ({top_product['Product']}) generates {top_percent:.1f}% of total revenue. "
        "Recommendations:\n"
        "- Analyze what makes this product successful\n"
        "- Explore line extensions or complementary products\n"
        "- Protect this revenue stream with inventory planning"
    )
    
    # Underperformer analysis
    bottom_5_avg = bottom_5['Revenue'].mean()
    top_5_avg = top_5['Revenue'].mean()
    
    if top_5_avg > 0 and bottom_5_avg > 0:
        ratio = top_5_avg / bottom_5_avg
        insights.append(
            f"Top products sell {ratio:.1f}x more than the bottom performers. "
            "For underperforming products, consider:\n"
            "- Price point adjustments\n"
            "- Better shelf placement or website positioning\n"
            "- Product refresh or packaging updates\n"
            "- Potential discontinuation if consistently underperforming"
        )
    
    # High-value threshold
    premium_products = product_rev[product_rev['Revenue'] > 10000]
    if len(premium_products) > 0:
        insights.append(
            f"We have {len(premium_products)} premium products (earning >$10,000 each). "
            "Suggestions:\n"
            "- Create 'premium' product category on website\n"
            "- Highlight in marketing materials\n"
            "- Train sales team on premium product benefits"
        )
    
    return insights

def generate_monthly_insights(monthly):
    """Generate actionable business insights about monthly trends"""
    insights = []
    
    if len(monthly) == 0:
        return ["No monthly revenue data available for analysis"]
    
    monthly['Revenue'] = monthly['Revenue'].str.replace('$', '').str.replace(',', '').astype(float)
    
    # Seasonal patterns
    best_month = monthly.loc[monthly['Revenue'].idxmax()]
    worst_month = monthly.loc[monthly['Revenue'].idxmin()]
    monthly_diff = best_month['Revenue'] - worst_month['Revenue']
    
    insights.append(
        f"Revenue varies significantly by month, peaking in {best_month['Month']} (${best_month['Revenue']:,.2f}) "
        f"and dropping in {worst_month['Month']} (${worst_month['Revenue']:,.2f}). "
        f"That's a ${monthly_diff:,.2f} difference. Action items:\n"
        "- Plan inventory and staffing for peak periods\n"
        "- Develop off-season promotions to smooth demand\n"
        "- Analyze causes of seasonal fluctuations"
    )
    
    # Growth trends
    if len(monthly) > 1:
        monthly['Growth'] = monthly['Revenue'].pct_change() * 100
        avg_growth = monthly['Growth'].mean()
        
        if avg_growth > 0:
            insights.append(
                f"Healthy average monthly growth of {avg_growth:.1f}%. "
                "To maintain momentum:\n"
                "- Reinvest in top-performing channels\n"
                "- Expand successful product lines\n"
                "- Continue current marketing strategies"
            )
        else:
            insights.append(
                f"Negative average monthly growth of {avg_growth:.1f}%. "
                "Corrective actions needed:\n"
                "- Review pricing strategy\n"
                "- Assess competitive landscape\n"
                "- Conduct customer feedback surveys"
            )
    
    # Quarterly planning
    if len(monthly) >= 12:
        quarterly = monthly.set_index('Month')['Revenue'].resample('Q').sum()
        best_q = quarterly.idxmax().strftime('%Y-Q%q')
        worst_q = quarterly.idxmin().strftime('%Y-Q%q')
        
        insights.append(
            f"Quarterly performance shows strongest results in {best_q} and weakest in {worst_q}. "
            "Planning suggestions:\n"
            "- Align product launches with strong quarters\n"
            "- Schedule maintenance/upgrades in slower periods\n"
            "- Adjust quarterly sales targets accordingly"
        )
    
    return insights

def auto_generate_insights(df, col_map):
    """Generate insights with plain English explanations"""
    insights = []
    processed_df = df.copy()
    
    try:
        # Revenue calculation
        if col_map['quantity_col'] and col_map['price_col']:
            processed_df['revenue'] = processed_df[col_map['quantity_col']] * processed_df[col_map['price_col']]
            total_rev = processed_df['revenue'].sum()
            insights.append(f"Total Revenue: ${total_rev:,.2f}")
            
            # Product insights
            if col_map['product_col']:
                product_rev = (processed_df.groupby(col_map['product_col'])['revenue']
                             .sum()
                             .sort_values(ascending=False)
                             .reset_index()
                             .head(25))
                product_rev.columns = ['Product', 'Revenue']
                
                # Generate and add product insights
                product_insights = generate_product_insights(product_rev)
                insights.extend(product_insights)
                
                # Display top products
                st.subheader("Top 25 Products by Revenue")
                st.dataframe(product_rev.style.format({'Revenue': '${:,.2f}'}))
                st.bar_chart(product_rev.set_index('Product'))
            
            # Monthly insights
            if col_map['date_col']:
                monthly = processed_df.resample('M', on=col_map['date_col'])['revenue'].sum().reset_index()
                monthly.columns = ['Month', 'Revenue']
                monthly['Month'] = monthly['Month'].dt.strftime('%Y-%m')
                monthly['Revenue'] = monthly['Revenue'].apply(lambda x: f"${x:,.2f}")
                
                # Generate and add monthly insights
                monthly_insights = generate_monthly_insights(monthly.copy())
                insights.extend(monthly_insights)
                
                # Display monthly trends
                st.subheader("Monthly Revenue Trend")
                st.dataframe(monthly)
                st.line_chart(
                    monthly.assign(Revenue=monthly['Revenue'].str.replace('$', '').str.replace(',', '').astype(float))
                    .set_index('Month')
                )
    
    except Exception as e:
        insights.append(f"Analysis error: {str(e)}")
    
    return insights, processed_df

def display_insights(insights):
    """Display insights in an organized way"""
    st.subheader("Key Business Insights")
    with st.expander("View Detailed Recommendations", expanded=True):
        for insight in insights:
            # Split into main observation and recommendations
            parts = insight.split("Recommendations:") if "Recommendations:" in insight else insight.split("Action items:")
            if len(parts) > 1:
                st.markdown(f"**{parts[0]}**")
                st.markdown(f"*Recommendations:* {parts[1]}")
            else:
                st.info(insight)
            st.write("")  # Add spacing

def main():
    st.set_page_config("Sales Insights Pro", layout="wide")
    st.title("📊 Actionable Sales Analysis")
    
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            st.success(f"✅ File loaded successfully with {len(df)} records")
            
            # Auto-detect columns
            col_map = analyze_columns(df)
            
            st.subheader("Detected Columns:")
            st.json({k:v for k,v in col_map.items() if v is not None})
            
            if not col_map['quantity_col'] or not col_map['price_col']:
                st.error("Could not find both quantity and price columns needed for revenue calculation")
                return
            
            # Generate insights
            insights, processed_df = auto_generate_insights(df, col_map)
            
            # Display insights
            display_insights(insights)
            
            # Show raw data
            with st.expander("🔍 View Processed Data", expanded=False):
                st.dataframe(processed_df.head())
                
            # Download options
            st.download_button(
                "📥 Download Full Analysis",
                processed_df.to_csv(index=False),
                "complete_sales_analysis.csv",
                "text/csv"
            )
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

if __name__ == "__main__":
    main()
