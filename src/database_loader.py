import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "enterprise_profitability")

def load_csv_to_mysql():
    print("⏳ Connecting to MySQL Database...")
    
    # Create SQLAlchemy engine for MySQL using PyMySQL
    connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)

    # Load raw CSV files
    df_customers = pd.read_csv('data/raw/customers.csv')
    df_products = pd.read_csv('data/raw/products.csv')
    df_orders = pd.read_csv('data/raw/orders.csv')
    df_logistics = pd.read_csv('data/raw/logistics.csv')

    # Push dataframes into MySQL tables
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)
    df_products.to_sql('products', engine, if_exists='replace', index=False)
    df_orders.to_sql('orders', engine, if_exists='replace', index=False)
    df_logistics.to_sql('logistics', engine, if_exists='replace', index=False)

    print("✅ All tables successfully loaded into MySQL Database!")

if __name__ == "__main__":
    load_csv_to_mysql()