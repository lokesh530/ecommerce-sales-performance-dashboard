-- ==============================================================================
-- E-Commerce Sales Performance Dashboard - Table Creation for MySQL
-- ==============================================================================

-- 1. Create Customers Table
CREATE TABLE IF NOT EXISTS Customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100),
    gender VARCHAR(20),
    email VARCHAR(100),
    phone VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(50),
    registration_date DATE
);

-- 2. Create Products Table
CREATE TABLE IF NOT EXISTS Products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10, 2),
    cost_price DECIMAL(10, 2),
    stock_quantity INT
);

-- 3. Create Orders Table
CREATE TABLE IF NOT EXISTS Orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_date DATETIME,
    payment_method VARCHAR(50),
    shipping_method VARCHAR(50),
    order_status VARCHAR(50),
    total_amount DECIMAL(10, 2),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

-- 4. Create Order_Items Table
CREATE TABLE IF NOT EXISTS Order_Items (
    order_item_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity INT,
    unit_price DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
