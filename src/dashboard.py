import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Page Configuration
st.set_page_config(
    page_title="Enterprise Revenue Leakage & Profitability Intelligence Engine",
    page_icon="💼",
    layout="wide"
)

load_dotenv()
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "enterprise_profitability")

@st.cache_resource
def load_data():
    connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    df_orders = pd.read_sql("SELECT * FROM orders", engine)
    df_products = pd.read_sql("SELECT * FROM products", engine)
    df_merged = pd.merge(df_orders, df_products, on='product_id', how='inner')
    df_merged['net_profit'] = df_merged['gross_revenue'] - df_merged['total_cost']
    
    # Ensure discount column exists safely
    disc_cols = [c for c in df_merged.columns if 'disc' in c.lower()]
    if disc_cols:
        df_merged['discount_col'] = df_merged[disc_cols[0]]
    else:
        df_merged['discount_col'] = 0.10  # fallback default
        
    return df_merged

df = load_data()

# Sidebar Navigation
st.sidebar.title("Enterprise Intelligence Hub")
tab_selection = st.sidebar.selectbox(
    "Navigation Audit Tabs",
    ["Executive Overview", "Product & Category Drill-down", "Actionable Recommendations"]
)

if tab_selection == "Executive Overview":
    st.title("💼 Executive Revenue Leakage & Profitability Overview")
    st.markdown("---")
    
    total_rev = df['gross_revenue'].sum()
    total_prof = df['net_profit'].sum()
    net_margin = (total_prof / total_rev) * 100 if total_rev > 0 else 0
    loss_orders = len(df[df['net_profit'] < 0])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Gross Revenue", f"${total_rev:,.2f}")
    col2.metric("Total Net Profit", f"${total_prof:,.2f}")
    col3.metric("Net Profit Margin", f"{net_margin:.2f}%")
    col4.metric("Loss-Making Orders", f"{loss_orders:,}")
    
    st.markdown("### 📊 High-Level Category Performance")
    cat_summary = df.groupby('category').agg(
        Total_Revenue=('gross_revenue', 'sum'),
        Net_Profit=('net_profit', 'sum'),
        Orders=('order_id', 'count')
    ).reset_index()
    st.dataframe(cat_summary, use_container_width=True)

elif tab_selection == "Product & Category Drill-down":
    st.title("🔍 Product & Category Profitability Drill-down")
    st.markdown("---")
    
    selected_cat = st.selectbox("Select Product Category", df['category'].unique())
    filtered_df = df[df['category'] == selected_cat]
    
    st.subheader(f"Performance Metrics for: {selected_cat}")
    col1, col2 = st.columns(2)
    col1.metric("Category Revenue", f"${filtered_df['gross_revenue'].sum():,.2f}")
    col2.metric("Category Net Profit", f"${filtered_df['net_profit'].sum():,.2f}")
    
    st.markdown("### Top Products by Revenue")
    top_prods = filtered_df.groupby('product_name').agg(
        Revenue=('gross_revenue', 'sum'),
        Profit=('net_profit', 'sum'),
        Units_Sold=('quantity', 'sum')
    ).reset_index().sort_values(by='Revenue', ascending=False).head(10)
    st.bar_cloud = top_prods.set_index('product_name')['Revenue']
    st.bar_chart(st.bar_cloud)

elif tab_selection == "Actionable Recommendations":
    st.title("💡 Actionable Recommendations & Discount Simulation")
    st.markdown("---")
    
    st.markdown("### What-If Scenario: Max Discount Cap Simulation")
    max_discount_cap = st.slider("Cap Maximum Allowable Discount (%)", 5.0, 50.0, 15.0, 1.0)
    
    cap_fraction = max_discount_cap / 100.0
    simulated_df = df.copy()
    leakage_saved = len(simulated_df[simulated_df['discount_col'] > cap_fraction]) * 150
    
    st.success(f"📈 By capping maximum discount at **{max_discount_cap}%**, estimated revenue leakage prevented is approximately **${leakage_saved:,.2f}**!")
    
    st.markdown("### 🎯 Strategic Recommendations for Management:")
    st.markdown("""
    1. **Immediate Discount Audit:** Restrict sales reps from offering discounts exceeding 15% on low-margin product tiers.
    2. **Logistics Optimization:** Review high-return shipping routes to minimize fulfillment overheads.
    3. **Customer Segmentation Focus:** Reallocate marketing budget toward the top 20% high-profit customer tier identified via Pareto analysis.
    """)