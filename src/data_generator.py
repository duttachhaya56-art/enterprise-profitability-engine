import os
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

def generate_enterprise_data():
    # Ensure raw data directory exists
    os.makedirs('data/raw', exist_ok=True)
    
    fake = Faker()
    Faker.seed(42)
    np.random.seed(42)

    print("⏳ Generating Enterprise Client Financial Dataset...")

    # 1. CUSTOMERS TABLE
    customer_data = []
    segments = ['Enterprise', 'SMB', 'Consumer']
    countries = ['India', 'United States', 'United Kingdom', 'Germany', 'Singapore']

    for i in range(1, 151):
        customer_data.append({
            'customer_id': f"CUST-{1000 + i}",
            'customer_name': fake.company() if random.random() > 0.4 else fake.name(),
            'segment': random.choice(segments),
            'country': random.choice(countries),
            'signup_date': fake.date_between(start_date='-2y', end_date='today')
        })
    df_customers = pd.DataFrame(customer_data)

    # 2. PRODUCTS TABLE
    product_data = []
    categories = ['Electronics', 'Office Supplies', 'Furniture', 'Software Subscriptions']

    for i in range(1, 41):
        category = random.choice(categories)
        unit_cost = round(random.uniform(20.0, 500.0), 2)
        base_price = round(unit_cost * random.uniform(1.3, 1.6), 2)
        
        product_data.append({
            'product_id': f"PROD-{500 + i}",
            'product_name': f"{category} Item {i}",
            'category': category,
            'unit_cost': unit_cost,
            'base_price': base_price
        })
    df_products = pd.DataFrame(product_data)

    # 3. ORDERS TABLE (With intentional Revenue Leakage via high discounts & returns)
    order_data = []
    shipping_modes = ['Standard', 'Express', 'Same Day']
    start_date = datetime.now() - timedelta(days=365)

    for i in range(1, 1201):
        customer = df_customers.sample(1).iloc[0]
        product = df_products.sample(1).iloc[0]
        
        quantity = random.randint(1, 15)
        order_date = start_date + timedelta(days=random.randint(0, 365))
        
        # 20% orders get aggressive discounts leading to potential negative profit
        if random.random() < 0.20:
            discount_pct = round(random.uniform(0.25, 0.45), 2)
        else:
            discount_pct = round(random.uniform(0.0, 0.15), 2)
            
        unit_selling_price = product['base_price'] * (1 - discount_pct)
        gross_revenue = round(unit_selling_price * quantity, 2)
        total_cost = round(product['unit_cost'] * quantity, 2)
        is_returned = 1 if random.random() < 0.08 else 0
        
        order_data.append({
            'order_id': f"ORD-{10000 + i}",
            'customer_id': customer['customer_id'],
            'product_id': product['product_id'],
            'order_date': order_date.strftime('%Y-%m-%d'),
            'quantity': quantity,
            'discount_pct': discount_pct,
            'gross_revenue': gross_revenue,
            'total_cost': total_cost,
            'is_returned': is_returned
        })
    df_orders = pd.DataFrame(order_data)

    # 4. LOGISTICS TABLE
    logistics_data = []
    for _, order in df_orders.iterrows():
        shipping_mode = random.choice(shipping_modes)
        base_ship_cost = random.uniform(5.0, 25.0)
        
        if shipping_mode == 'Same Day':
            shipping_cost = round(base_ship_cost * 2.5, 2)
        elif shipping_mode == 'Express':
            shipping_cost = round(base_ship_cost * 1.5, 2)
        else:
            shipping_cost = round(base_ship_cost, 2)
            
        logistics_data.append({
            'order_id': order['order_id'],
            'shipping_mode': shipping_mode,
            'shipping_cost': shipping_cost,
            'delivery_status': 'Returned' if order['is_returned'] == 1 else 'Delivered'
        })
    df_logistics = pd.DataFrame(logistics_data)

    # Save CSV files into data/raw/
    df_customers.to_csv('data/raw/customers.csv', index=False)
    df_products.to_csv('data/raw/products.csv', index=False)
    df_orders.to_csv('data/raw/orders.csv', index=False)
    df_logistics.to_csv('data/raw/logistics.csv', index=False)

    print("✅ Raw Enterprise Data successfully generated and saved inside `data/raw/`!")

if __name__ == "__main__":
    generate_enterprise_data()