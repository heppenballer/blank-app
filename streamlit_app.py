# src/sales_insights_app.py

import streamlit as st
import pandas as pd
from datetime import datetime
from insights import InsightEngine
from utils import analyze_columns, format_currency_in_text


def display_insights(insights):
    st.subheader("Key Business Insights")
    with st.expander("View Detailed Recommendations", expanded=True):
        for insight in insights:
            formatted_insight = format_currency_in_text(insight)
            parts = formatted_insight.split("Recommendations:") if "Recommendations:" in formatted_insight else formatted_insight.split("Action items:")
            if len(parts) > 1:
                st.markdown(f"**{parts[0]}**")
                st.markdown(f"*Recommendations:* {parts[1]}")
            else:
                st.info(formatted_insight)
            st.write("")


def main():
    st.set_page_config("Sales Insights Pro", layout="wide")
    st.title("📊 Actionable Sales Analysis")

    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            st.success(f"✅ File loaded successfully with {len(df)} records")

            col_map = analyze_columns(df)
            st.subheader("Detected Columns:")
            st.json({k: v for k, v in col_map.items() if v is not None})

            if not col_map['quantity_col'] or not col_map['price_col']:
                st.error("Missing quantity or price column for revenue calculation")
                return

            engine = InsightEngine(df, col_map)
            insights, processed_df = engine.run_all()

            display_insights(insights)

            with st.expander("🔍 View Processed Data", expanded=False):
                st.dataframe(processed_df.head())

            st.download_button(
                "👅 Download Full Analysis",
                processed_df.to_csv(index=False),
                "complete_sales_analysis.csv",
                "text/csv"
            )

        except Exception as e:
            st.error(f"Error loading file: {str(e)}")


if __name__ == "__main__":
    main()
