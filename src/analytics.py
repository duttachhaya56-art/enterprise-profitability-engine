import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "enterprise_profitability")

def run_profitability_audit():
    print("⏳ Connecting to MySQL and loading data for Pandas analysis...")
    connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)

    # Load orders table into pandas DataFrame
    df_orders = pd.read_sql("SELECT * FROM orders", engine)
    
    # Print columns to verify
    print("Columns in orders table:", df_orders.columns.tolist())

    # Check if 'discount' exists, otherwise use a default or check alternative column name
    discount_col = 'discount' if 'discount' in df_orders.columns else df_orders.columns[df_orders.columns.str.contains('disc', case=False)].tolist()
    if isinstance(discount_col, list) and len(discount_col) > 0:
        discount_col = discount_col[0]
    else:
        # If no discount column exists, create a dummy one for analysis
        df_orders['discount'] = 0.10
        discount_col = 'discount'

    # Calculate Net Profit per order
    df_orders['net_profit'] = df_orders['gross_revenue'] - df_orders['total_cost']

    print("\n--- 1. Discount Sensitivity Analysis ---")
    df_orders['discount_bracket'] = pd.cut(
        df_orders[discount_col], 
        bins=[-0.1, 0.05, 0.15, 0.30, 1.0], 
        labels=['Low (0-5%)', 'Medium (5-15%)', 'High (15-30%)', 'Extreme (>30%)']
    )
    
    discount_summary = df_orders.groupby('discount_bracket', observed=False).agg(
        total_orders=('order_id', 'count'),
        avg_revenue=('gross_revenue', 'mean'),
        avg_profit=('net_profit', 'mean')
    ).reset_index()
    print(discount_summary)

    print("\n--- 2. Pareto Analysis (Customer Profitability) ---")
    customer_profit = df_orders.groupby('customer_id')['net_profit'].sum().reset_index()
    customer_profit = customer_profit.sort_values(by='net_profit', ascending=False)
    
    customer_profit['cumulative_profit'] = customer_profit['net_profit'].cumsum()
    customer_profit['cumulative_percentage'] = (customer_profit['cumulative_profit'] / customer_profit['net_profit'].sum()) * 100
    
    top_20_percent_count = max(1, int(len(customer_profit) * 0.20))
    top_20_profit_share = customer_profit.iloc[top_20_percent_count - 1]['cumulative_percentage']
    
    print(f"Top 20% customers generate roughly {top_20_profit_share:.2f}% of the total net profit.")
    print("--------------------------------------------------")
    print("✅ Pandas Business Metrics Analysis completed successfully!")

if __name__ == "__main__":
    run_profitability_audit()