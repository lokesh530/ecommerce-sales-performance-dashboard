import os
import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker with Indian locale
fake = Faker('en_IN')
Faker.seed(42)
random.seed(42)

# Configuration
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 500
NUM_ORDERS = 5000
NUM_ORDER_ITEMS = 10000

# Base directory for data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def generate_customers():
    print(f"Generating {NUM_CUSTOMERS} customers...")
    data = []
    for i in range(1, NUM_CUSTOMERS + 1):
        # Generate some messy data occasionally to require cleaning later
        has_null_email = random.random() < 0.05
        has_duplicate = random.random() < 0.01
        
        reg_date = fake.date_between(start_date='-3y', end_date='today')
        
        customer = {
            'customer_id': f"C{i:05d}",
            'customer_name': fake.name(),
            'gender': random.choice(['Male', 'Female', 'Other']),
            'email': None if has_null_email else fake.email(),
            'phone': fake.phone_number(),
            'city': fake.city(),
            'state': fake.state(),
            'country': 'India',
            'registration_date': reg_date
        }
        data.append(customer)
        if has_duplicate:
            data.append(customer.copy()) # Intentional duplicate
            
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, 'customers.csv'), index=False)
    return df

def generate_products():
    print(f"Generating {NUM_PRODUCTS} products...")
    categories = {
        'Electronics': ['Smartphone', 'Laptop', 'Headphones', 'Smartwatch', 'Tablet'],
        'Fashion': ['T-Shirt', 'Jeans', 'Sneakers', 'Jacket', 'Dress'],
        'Home & Kitchen': ['Mixer Grinder', 'Bedsheet', 'Cookware Set', 'Water Purifier', 'Wall Clock'],
        'Beauty & Personal Care': ['Shampoo', 'Face Wash', 'Perfume', 'Body Lotion', 'Hair Oil'],
        'Sports & Fitness': ['Yoga Mat', 'Dumbbells', 'Cricket Bat', 'Badminton Racket', 'Protein Powder']
    }
    
    brands = {
        'Electronics': ['Samsung', 'Apple', 'Xiaomi', 'Sony', 'Boat'],
        'Fashion': ['Puma', 'Nike', 'Levi\'s', 'Zara', 'H&M'],
        'Home & Kitchen': ['Prestige', 'Bajaj', 'Philips', 'Milton', 'Bombay Dyeing'],
        'Beauty & Personal Care': ['L\'Oreal', 'Nivea', 'Dove', 'Lakme', 'Mamaearth'],
        'Sports & Fitness': ['Decathlon', 'Nivia', 'Yonex', 'Optimum Nutrition', 'Cosco']
    }
    
    data = []
    for i in range(1, NUM_PRODUCTS + 1):
        category = random.choice(list(categories.keys()))
        product_type = random.choice(categories[category])
        brand = random.choice(brands[category])
        
        # Cost and Price logic (Profit margin between 10% and 50%)
        cost_price = round(random.uniform(100, 50000), 2)
        margin = random.uniform(1.1, 1.5)
        price = round(cost_price * margin, 2)
        
        data.append({
            'product_id': f"P{i:04d}",
            'product_name': f"{brand} {product_type} {fake.word().capitalize()}",
            'category': category,
            'brand': brand,
            'price': price,
            'cost_price': cost_price,
            'stock_quantity': random.randint(0, 500) # Include 0 for out of stock
        })
        
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, 'products.csv'), index=False)
    return df

def generate_orders(customers_df):
    print(f"Generating {NUM_ORDERS} orders...")
    customer_ids = customers_df['customer_id'].dropna().unique().tolist()
    
    data = []
    for i in range(1, NUM_ORDERS + 1):
        # Generate some messy statuses
        status = random.choices(
            ['Delivered', 'Pending', 'Cancelled', 'Shipped'],
            weights=[0.70, 0.10, 0.05, 0.15],
            k=1
        )[0]
        
        # Corrupted row simulation (missing payment method)
        has_missing_payment = random.random() < 0.02
        
        data.append({
            'order_id': f"ORD{i:06d}",
            'customer_id': random.choice(customer_ids),
            'order_date': fake.date_time_between(start_date='-2y', end_date='now'),
            'payment_method': None if has_missing_payment else random.choice(['UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Cash on Delivery']),
            'shipping_method': random.choice(['Standard', 'Express', 'Same Day']),
            'order_status': status,
            'total_amount': 0.0 # Will be updated after order items
        })
        
    df = pd.DataFrame(data)
    # Don't save to CSV yet, need to compute total_amount
    return df

def generate_order_items(orders_df, products_df):
    print(f"Generating {NUM_ORDER_ITEMS} order items...")
    order_ids = orders_df['order_id'].tolist()
    products_list = products_df[['product_id', 'price']].to_dict('records')
    
    data = []
    order_totals = {oid: 0.0 for oid in order_ids}
    
    # Ensure every order has at least one item
    item_id_counter = 1
    
    # First pass: 1 item per order (5000 items)
    for oid in order_ids:
        prod = random.choice(products_list)
        qty = random.randint(1, 5)
        data.append({
            'order_item_id': f"ITM{item_id_counter:07d}",
            'order_id': oid,
            'product_id': prod['product_id'],
            'quantity': qty,
            'unit_price': prod['price']
        })
        order_totals[oid] += qty * prod['price']
        item_id_counter += 1
        
    # Second pass: distribute the remaining 5000 items randomly
    for _ in range(NUM_ORDER_ITEMS - NUM_ORDERS):
        oid = random.choice(order_ids)
        prod = random.choice(products_list)
        qty = random.randint(1, 5)
        data.append({
            'order_item_id': f"ITM{item_id_counter:07d}",
            'order_id': oid,
            'product_id': prod['product_id'],
            'quantity': qty,
            'unit_price': prod['price']
        })
        order_totals[oid] += qty * prod['price']
        item_id_counter += 1
        
    items_df = pd.DataFrame(data)
    items_df.to_csv(os.path.join(DATA_DIR, 'order_items.csv'), index=False)
    
    # Update orders with total amount
    orders_df['total_amount'] = orders_df['order_id'].map(order_totals).round(2)
    orders_df.to_csv(os.path.join(DATA_DIR, 'orders.csv'), index=False)
    
    return items_df, orders_df

if __name__ == "__main__":
    print("--- Starting Data Generation ---")
    cust_df = generate_customers()
    prod_df = generate_products()
    ord_df = generate_orders(cust_df)
    items_df, ord_df = generate_order_items(ord_df, prod_df)
    print("--- Data Generation Complete! ---")
    print(f"Saved to: {DATA_DIR}")
