import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

# Page config MUST be the first Streamlit command
st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")

# ==========================================
# 1. DATA LOADING & CACHING
# ==========================================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'ecommerce.db')
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Load Tables
    customers = pd.read_sql("SELECT * FROM Customers", engine)
    products = pd.read_sql("SELECT * FROM Products", engine)
    orders = pd.read_sql("SELECT * FROM Orders", engine)
    order_items = pd.read_sql("SELECT * FROM Order_Items", engine)
    
    # Convert dates
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    customers['registration_date'] = pd.to_datetime(customers['registration_date'])
    
    # Create master merged dataframe for easy analysis
    master_df = order_items.merge(orders, on='order_id', how='left')\
                           .merge(products, on='product_id', how='left')\
                           .merge(customers, on='customer_id', how='left')
    return master_df, customers, products, orders

# Load the data
try:
    df, customers_df, products_df, orders_df = load_data()
except Exception as e:
    st.error(f"Error loading database: {e}. Please ensure you have run db_setup.py.")
    st.stop()

# ==========================================
# 2. SIDEBAR NAVIGATION & FILTERS
# ==========================================
st.sidebar.title("🛒 E-Commerce Dashboard")

# Navigation
page = st.sidebar.radio("Navigate", ["Home", "Sales", "Products", "Customers", "Profit", "Inventory"])

st.sidebar.markdown("---")
st.sidebar.header("Global Filters")

# Filters
date_range = st.sidebar.date_input("Date Range", 
                                   value=(df['order_date'].min().date(), df['order_date'].max().date()),
                                   min_value=df['order_date'].min().date(),
                                   max_value=df['order_date'].max().date())

# Apply Date Filter
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['order_date'].dt.date >= start_date) & (df['order_date'].dt.date <= end_date)]
else:
    filtered_df = df

selected_category = st.sidebar.multiselect("Category", options=filtered_df['category'].unique(), default=filtered_df['category'].unique())
selected_state = st.sidebar.multiselect("State", options=filtered_df['state'].unique(), default=[])

# Apply other filters
if selected_category:
    filtered_df = filtered_df[filtered_df['category'].isin(selected_category)]
if selected_state:
    filtered_df = filtered_df[filtered_df['state'].isin(selected_state)]

st.sidebar.markdown("---")
st.sidebar.info("Industry-Level Dashboard built with Streamlit, Plotly, and SQLAlchemy.")

# Function to download CSV
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# ==========================================
# 3. PAGES
# ==========================================

# --- HOME PAGE ---
if page == "Home":
    st.title("📊 E-Commerce Performance Overview")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    total_revenue = filtered_df['unit_price'].multiply(filtered_df['quantity']).sum()
    total_profit = filtered_df['profit'].sum()
    total_orders = filtered_df['order_id'].nunique()
    total_customers = filtered_df['customer_id'].nunique()
    
    col1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    col2.metric("Total Profit", f"₹{total_profit:,.2f}")
    col3.metric("Total Orders", f"{total_orders:,}")
    col4.metric("Total Customers", f"{total_customers:,}")
    
    st.markdown("---")
    
    # Quick Charts
    c1, c2 = st.columns(2)
    with c1:
        rev_by_cat = filtered_df.groupby('category').apply(lambda x: (x['unit_price'] * x['quantity']).sum()).reset_index(name='revenue')
        fig = px.pie(rev_by_cat, names='category', values='revenue', title="Revenue by Category", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        status_counts = filtered_df.groupby('order_status')['order_id'].nunique().reset_index(name='count')
        fig2 = px.bar(status_counts, x='order_status', y='count', title="Order Status Distribution", color='order_status')
        st.plotly_chart(fig2, use_container_width=True)

# --- SALES DASHBOARD ---
elif page == "Sales":
    st.title("📈 Sales Dashboard")
    
    # Group by Date
    daily_sales = filtered_df.groupby(filtered_df['order_date'].dt.date).apply(lambda x: (x['unit_price'] * x['quantity']).sum()).reset_index(name='revenue')
    daily_sales.columns = ['Date', 'Revenue']
    
    fig = px.line(daily_sales, x='Date', y='Revenue', title="Revenue Trend over Time")
    st.plotly_chart(fig, use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        monthly_sales = filtered_df.groupby(['order_year', 'order_month']).apply(lambda x: (x['unit_price'] * x['quantity']).sum()).reset_index(name='revenue')
        monthly_sales['Month-Year'] = monthly_sales['order_year'].astype(str) + '-' + monthly_sales['order_month'].astype(str)
        fig_m = px.bar(monthly_sales, x='Month-Year', y='revenue', title="Monthly Sales")
        st.plotly_chart(fig_m, use_container_width=True)
        
    with c2:
        payment_sales = filtered_df.groupby('payment_method').apply(lambda x: (x['unit_price'] * x['quantity']).sum()).reset_index(name='revenue')
        fig_p = px.pie(payment_sales, names='payment_method', values='revenue', title="Revenue by Payment Method")
        st.plotly_chart(fig_p, use_container_width=True)

    st.download_button(label="Download Sales Data as CSV", data=convert_df(daily_sales), file_name='sales_data.csv', mime='text/csv')

# --- PRODUCTS DASHBOARD ---
elif page == "Products":
    st.title("🛍️ Product Dashboard")
    
    # Top Products
    product_revenue = filtered_df.groupby('product_name').apply(lambda x: (x['unit_price'] * x['quantity']).sum()).reset_index(name='revenue')
    top_products = product_revenue.sort_values(by='revenue', ascending=False).head(10)
    
    fig = px.bar(top_products, x='revenue', y='product_name', orientation='h', title="Top 10 Products by Revenue", color='revenue', color_continuous_scale='Viridis')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        brand_revenue = filtered_df.groupby('brand').apply(lambda x: (x['unit_price'] * x['quantity']).sum()).reset_index(name='revenue')
        fig_b = px.bar(brand_revenue.sort_values(by='revenue', ascending=False).head(10), x='brand', y='revenue', title="Top 10 Brands")
        st.plotly_chart(fig_b, use_container_width=True)
    with c2:
        cat_analysis = filtered_df.groupby('category').agg({'quantity':'sum'}).reset_index()
        fig_c = px.pie(cat_analysis, names='category', values='quantity', title="Items Sold by Category")
        st.plotly_chart(fig_c, use_container_width=True)

# --- CUSTOMER DASHBOARD ---
elif page == "Customers":
    st.title("👥 Customer Dashboard")
    
    # Customer Growth
    cust_growth = customers_df.groupby(customers_df['registration_date'].dt.to_period("M")).size().reset_index(name='new_customers')
    cust_growth['registration_date'] = cust_growth['registration_date'].astype(str)
    fig_g = px.line(cust_growth, x='registration_date', y='new_customers', title="Customer Acquisition Trend", markers=True)
    st.plotly_chart(fig_g, use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        top_cust = filtered_df.groupby('customer_name').apply(lambda x: (x['unit_price'] * x['quantity']).sum()).reset_index(name='revenue')
        top_cust = top_cust.sort_values(by='revenue', ascending=False).head(10)
        fig_tc = px.bar(top_cust, x='revenue', y='customer_name', orientation='h', title="Top 10 Customers", color='revenue')
        fig_tc.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_tc, use_container_width=True)
    with c2:
        state_rev = filtered_df.groupby('state').apply(lambda x: (x['unit_price'] * x['quantity']).sum()).reset_index(name='revenue')
        fig_s = px.bar(state_rev.sort_values(by='revenue', ascending=False).head(10), x='state', y='revenue', title="Top 10 States by Revenue")
        st.plotly_chart(fig_s, use_container_width=True)

# --- PROFIT DASHBOARD ---
elif page == "Profit":
    st.title("💰 Profit Dashboard")
    
    total_rev = filtered_df['unit_price'].multiply(filtered_df['quantity']).sum()
    total_prof = filtered_df['profit'].sum()
    margin = (total_prof / total_rev) * 100 if total_rev > 0 else 0
    
    st.metric("Overall Profit Margin", f"{margin:.2f}%")
    
    # Profit by Category
    prof_cat = filtered_df.groupby('category')['profit'].sum().reset_index()
    fig_pc = px.bar(prof_cat.sort_values('profit', ascending=False), x='category', y='profit', title="Profit by Category", color='profit', color_continuous_scale='Greens')
    st.plotly_chart(fig_pc, use_container_width=True)
    
    # Profit Trend
    daily_prof = filtered_df.groupby(filtered_df['order_date'].dt.date)['profit'].sum().reset_index()
    daily_prof.columns = ['Date', 'Profit']
    fig_pt = px.line(daily_prof, x='Date', y='Profit', title="Profit Trend over Time")
    st.plotly_chart(fig_pt, use_container_width=True)

# --- INVENTORY DASHBOARD ---
elif page == "Inventory":
    st.title("📦 Inventory Dashboard")
    
    low_stock = products_df[products_df['stock_quantity'] < 50].sort_values('stock_quantity')
    st.warning(f"⚠️ Warning: {len(low_stock)} products are running low on stock (Less than 50 units)!")
    
    fig = px.bar(low_stock.head(20), x='stock_quantity', y='product_name', orientation='h', 
                 title="Top 20 Lowest Stock Products", color='stock_quantity', color_continuous_scale='Reds_r')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(low_stock[['product_name', 'category', 'brand', 'stock_quantity']], use_container_width=True)
    st.download_button(label="Download Low Stock Report", data=convert_df(low_stock), file_name='low_stock.csv', mime='text/csv')
