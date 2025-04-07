# modular_insight_engine.py

import streamlit as st
import pandas as pd
from datetime import datetime
from abc import ABC, abstractmethod


class BaseInsight(ABC):
    @abstractmethod
    def generate(self, df: pd.DataFrame, col_map: dict) -> list[str]:
        pass


class ProductInsights(BaseInsight):
    def generate(self, df: pd.DataFrame, col_map: dict) -> list[str]:
        insights = []
        if col_map['product_col'] not in df:
            return insights

        product_rev = (
            df.groupby(col_map['product_col'])['revenue']
            .sum().sort_values(ascending=False).reset_index()
        )
        product_rev.columns = ['Product', 'Revenue']

        if len(product_rev) == 0:
            return ["No product revenue data available for analysis"]

        total_rev = product_rev['Revenue'].sum()
        top_product = product_rev.iloc[0]
        top_5 = product_rev.head(5)
        bottom_5 = product_rev.tail(5)

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

        top_percent = (top_product['Revenue'] / total_rev) * 100
        insights.append(
            f"Our #1 product ({top_product['Product']}) generates {top_percent:.1f}% of total revenue. "
            "Recommendations:\n"
            "- Analyze what makes this product successful\n"
            "- Explore line extensions or complementary products\n"
            "- Protect this revenue stream with inventory planning"
        )

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

        premium_products = product_rev[product_rev['Revenue'] > 10000]
        if len(premium_products) > 0:
            insights.append(
                f"We have {len(premium_products)} premium products (earning >$10,000 each). "
                "Suggestions:\n"
                "- Create 'premium' product category on website\n"
                "- Highlight in marketing materials\n"
                "- Train sales team on premium product benefits"
            )

        st.subheader("Top 25 Products by Revenue")
        st.dataframe(product_rev.head(25).style.format({'Revenue': '${:,.2f}'}))
        st.bar_chart(product_rev.set_index('Product').head(25))

        return insights


class MonthlyInsights(BaseInsight):
    def generate(self, df: pd.DataFrame, col_map: dict) -> list[str]:
        insights = []
        if col_map['date_col'] not in df:
            return insights

        df['date'] = pd.to_datetime(df[col_map['date_col']])
        monthly = df.set_index('date').resample('M')['revenue'].sum().reset_index()
        monthly.columns = ['Month', 'Revenue']
        monthly['Month'] = monthly['Month'].dt.strftime('%Y-%m')

        st.subheader("Monthly Revenue Trend")
        st.dataframe(monthly.style.format({'Revenue': '${:,.2f}'}))
        st.line_chart(monthly.set_index('Month'))

        if len(monthly) == 0:
            return ["No monthly revenue data available for analysis"]

        best_month = monthly.loc[monthly['Revenue'].idxmax()]
        worst_month = monthly.loc[monthly['Revenue'].idxmin()]
        monthly_diff = best_month['Revenue'] - worst_month['Revenue']

        insights.append(
            f"Revenue varies significantly by month, peaking in {best_month['Month']} "
            f"and dropping in {worst_month['Month']}. Difference: ${monthly_diff:,.2f}. Action items:\n"
            "- Plan inventory and staffing for peak periods\n"
            "- Develop off-season promotions to smooth demand\n"
            "- Analyze causes of seasonal fluctuations"
        )

        if len(monthly) > 1:
            monthly['Growth'] = monthly['Revenue'].pct_change() * 100
            avg_growth = monthly['Growth'].mean()
            if avg_growth > 0:
                insights.append(
                    f"Healthy average monthly growth of {avg_growth:.1f}%. To maintain momentum:\n"
                    "- Reinvest in top-performing channels\n"
                    "- Expand successful product lines\n"
                    "- Continue current marketing strategies"
                )
            else:
                insights.append(
                    f"Negative average monthly growth of {avg_growth:.1f}%. Corrective actions needed:\n"
                    "- Review pricing strategy\n"
                    "- Assess competitive landscape\n"
                    "- Conduct customer feedback surveys"
                )

        return insights


class InsightEngine:
    def __init__(self):
        self.modules: list[BaseInsight] = []

    def register(self, module: BaseInsight):
        self.modules.append(module)

    def generate_all(self, df: pd.DataFrame, col_map: dict) -> list[str]:
        insights = []
        for module in self.modules:
            insights.extend(module.generate(df, col_map))
        return insights
