import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(BASE_DIR, 'ecommerce.db')

def setup_database():
    print(f"Connecting to database: sqlite:///{DB_PATH}")
    engine = create_engine(f'sqlite:///{DB_PATH}')
    
    # 1. Load Customers
    print("Loading Customers...")
    customers_df = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))
    # Clean: Drop duplicates, handle missing emails
    customers_df.drop_duplicates(subset=['customer_id'], inplace=True)
    customers_df['email'].fillna('no_email@example.com', inplace=True)
    customers_df.to_sql('Customers', engine, if_exists='replace', index=False)
    
    # 2. Load Products
    print("Loading Products...")
    products_df = pd.read_csv(os.path.join(DATA_DIR, 'products.csv'))
    products_df.to_sql('Products', engine, if_exists='replace', index=False)
    
    # 3. Load Orders
    print("Loading Orders...")
    orders_df = pd.read_csv(os.path.join(DATA_DIR, 'orders.csv'))
    # Clean: handle missing payment method
    orders_df['payment_method'].fillna('Unknown', inplace=True)
    
    # Transform: Add Month and Year columns
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    orders_df['order_month'] = orders_df['order_date'].dt.month
    orders_df['order_year'] = orders_df['order_date'].dt.year
    orders_df.to_sql('Orders', engine, if_exists='replace', index=False)
    
    # 4. Load Order Items
    print("Loading Order Items...")
    order_items_df = pd.read_csv(os.path.join(DATA_DIR, 'order_items.csv'))
    
    # Transform: Add Profit Column (unit_price - cost_price * quantity)
    # Need to merge with Products to get cost_price
    merged_df = pd.merge(order_items_df, products_df[['product_id', 'cost_price']], on='product_id', how='left')
    merged_df['profit'] = (merged_df['unit_price'] - merged_df['cost_price']) * merged_df['quantity']
    
    merged_df.to_sql('Order_Items', engine, if_exists='replace', index=False)
    
    print(f"--- Database Setup Complete! ---")
    print(f"Database created at: {DB_PATH}")

if __name__ == "__main__":
    setup_database()
