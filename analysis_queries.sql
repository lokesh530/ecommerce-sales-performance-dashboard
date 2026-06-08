-- ==============================================================================
-- E-Commerce Sales Performance Dashboard - Advanced SQL Analysis
-- Note: This syntax is compatible with SQLite (and most logic translates to MySQL)
-- ==============================================================================

-- ==========================================
-- 1. AGGREGATIONS & REVENUE ANALYSIS
-- ==========================================

-- Total Revenue
SELECT ROUND(SUM(total_amount), 2) AS total_revenue 
FROM Orders 
WHERE order_status = 'Delivered';

-- Monthly Revenue
SELECT order_year, order_month, ROUND(SUM(total_amount), 2) AS monthly_revenue
FROM Orders
WHERE order_status = 'Delivered'
GROUP BY order_year, order_month
ORDER BY order_year, order_month;

-- Yearly Revenue
SELECT order_year, ROUND(SUM(total_amount), 2) AS yearly_revenue
FROM Orders
WHERE order_status = 'Delivered'
GROUP BY order_year
ORDER BY order_year;

-- Daily Revenue (Top 10 Days)
SELECT date(order_date) as order_day, ROUND(SUM(total_amount), 2) AS daily_revenue
FROM Orders
WHERE order_status = 'Delivered'
GROUP BY order_day
ORDER BY daily_revenue DESC
LIMIT 10;

-- Average Order Value (AOV)
SELECT ROUND(AVG(total_amount), 2) AS average_order_value
FROM Orders
WHERE order_status = 'Delivered';

-- ==========================================
-- 2. TOP PERFORMERS
-- ==========================================

-- Top 10 Customers by Revenue
SELECT c.customer_name, c.city, c.state, ROUND(SUM(o.total_amount), 2) as total_spent
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
WHERE o.order_status = 'Delivered'
GROUP BY c.customer_id
ORDER BY total_spent DESC
LIMIT 10;

-- Top 10 Products by Revenue
SELECT p.product_name, p.category, ROUND(SUM(oi.unit_price * oi.quantity), 2) AS total_revenue
FROM Products p
JOIN Order_Items oi ON p.product_id = oi.product_id
JOIN Orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY p.product_id
ORDER BY total_revenue DESC
LIMIT 10;

-- Top 10 Categories by Revenue
SELECT p.category, ROUND(SUM(oi.unit_price * oi.quantity), 2) AS total_revenue
FROM Products p
JOIN Order_Items oi ON p.product_id = oi.product_id
JOIN Orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY p.category
ORDER BY total_revenue DESC
LIMIT 10;

-- Revenue by City (Top 10)
SELECT c.city, ROUND(SUM(o.total_amount), 2) AS revenue
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
WHERE o.order_status = 'Delivered'
GROUP BY c.city
ORDER BY revenue DESC
LIMIT 10;

-- Revenue by State
SELECT c.state, ROUND(SUM(o.total_amount), 2) AS revenue
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
WHERE o.order_status = 'Delivered'
GROUP BY c.state
ORDER BY revenue DESC;

-- Revenue by Brand
SELECT p.brand, ROUND(SUM(oi.unit_price * oi.quantity), 2) AS revenue
FROM Products p
JOIN Order_Items oi ON p.product_id = oi.product_id
JOIN Orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY p.brand
ORDER BY revenue DESC;

-- ==========================================
-- 3. CUSTOMER RETENTION & METRICS
-- ==========================================

-- Repeat Customer Percentage
WITH CustomerOrderCounts AS (
    SELECT customer_id, COUNT(order_id) AS num_orders
    FROM Orders
    GROUP BY customer_id
)
SELECT 
    COUNT(CASE WHEN num_orders > 1 THEN 1 END) * 100.0 / COUNT(*) AS repeat_customer_percentage
FROM CustomerOrderCounts;

-- ==========================================
-- 4. ORDER STATUS & PAYMENT ANALYSIS
-- ==========================================

-- Cancelled Orders Analysis (Loss in potential revenue)
SELECT COUNT(*) as cancelled_orders, ROUND(SUM(total_amount), 2) as lost_revenue
FROM Orders
WHERE order_status = 'Cancelled';

-- Pending Orders Analysis
SELECT COUNT(*) as pending_orders, ROUND(SUM(total_amount), 2) as pending_revenue
FROM Orders
WHERE order_status = 'Pending';

-- Payment Method Analysis
SELECT payment_method, COUNT(*) as transaction_count, ROUND(SUM(total_amount), 2) as total_revenue
FROM Orders
WHERE order_status = 'Delivered'
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- ==========================================
-- 5. PROFIT & INVENTORY ANALYSIS
-- ==========================================

-- Overall Profit & Profit Margin
SELECT 
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(unit_price * quantity)) * 100, 2) AS overall_profit_margin_percentage
FROM Order_Items oi
JOIN Orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered';

-- Stock Analysis / Inventory Alerts (Products running low on stock)
SELECT product_name, category, stock_quantity
FROM Products
WHERE stock_quantity < 50
ORDER BY stock_quantity ASC;

-- ==========================================
-- 6. ADVANCED SQL (WINDOW FUNCTIONS & CTES)
-- ==========================================

-- Monthly Growth Rate (Using LAG)
WITH MonthlySales AS (
    SELECT order_year, order_month, SUM(total_amount) AS revenue
    FROM Orders
    WHERE order_status = 'Delivered'
    GROUP BY order_year, order_month
),
GrowthCalculation AS (
    SELECT 
        order_year, 
        order_month, 
        revenue,
        LAG(revenue) OVER (ORDER BY order_year, order_month) AS prev_month_revenue
    FROM MonthlySales
)
SELECT 
    order_year, 
    order_month, 
    ROUND(revenue, 2) AS revenue, 
    ROUND(prev_month_revenue, 2) AS prev_month_revenue,
    ROUND(((revenue - prev_month_revenue) / prev_month_revenue) * 100, 2) AS growth_rate_percentage
FROM GrowthCalculation;

-- Customer Ranking by State (Using ROW_NUMBER, RANK, DENSE_RANK)
WITH CustomerSpend AS (
    SELECT c.state, c.customer_name, SUM(o.total_amount) as total_spent
    FROM Customers c
    JOIN Orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Delivered'
    GROUP BY c.state, c.customer_id
)
SELECT 
    state, 
    customer_name, 
    ROUND(total_spent, 2) AS total_spent,
    ROW_NUMBER() OVER (PARTITION BY state ORDER BY total_spent DESC) as row_num,
    RANK() OVER (PARTITION BY state ORDER BY total_spent DESC) as rank_val,
    DENSE_RANK() OVER (PARTITION BY state ORDER BY total_spent DESC) as dense_rank_val
FROM CustomerSpend
WHERE rank_val <= 3; -- Show top 3 per state

-- ==========================================
-- 7. SUBQUERIES
-- ==========================================

-- Single Row Subquery: Customer who spent the most on a single order
SELECT customer_name, city 
FROM Customers 
WHERE customer_id = (
    SELECT customer_id FROM Orders ORDER BY total_amount DESC LIMIT 1
);

-- Multiple Row Subquery: Products never sold
SELECT product_name, category 
FROM Products 
WHERE product_id NOT IN (
    SELECT DISTINCT product_id FROM Order_Items
);

-- Correlated Subquery: Customers whose order is greater than the average order value of their respective city
SELECT o.order_id, c.customer_name, c.city, o.total_amount
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
WHERE o.total_amount > (
    SELECT AVG(o2.total_amount)
    FROM Orders o2
    JOIN Customers c2 ON o2.customer_id = c2.customer_id
    WHERE c2.city = c.city
);

-- ==========================================
-- 8. VIEWS, TRIGGERS & INDEXES (DDL)
-- ==========================================

-- Create a View for Active High-Value Customers
DROP VIEW IF EXISTS High_Value_Customers;
CREATE VIEW High_Value_Customers AS
SELECT c.customer_id, c.customer_name, SUM(o.total_amount) as total_spent
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
HAVING total_spent > 50000;

-- Create Indexes for performance optimization
CREATE INDEX idx_order_status ON Orders(order_status);
CREATE INDEX idx_order_customer ON Orders(customer_id);
CREATE INDEX idx_order_items_product ON Order_Items(product_id);

-- Note: Stored Procedures are not natively supported in SQLite in the same way as MySQL. 
-- In a MySQL environment, you would use:
/*
DELIMITER //
CREATE PROCEDURE GetCustomerOrders(IN cust_id VARCHAR(10))
BEGIN
    SELECT * FROM Orders WHERE customer_id = cust_id;
END //
DELIMITER ;
*/
