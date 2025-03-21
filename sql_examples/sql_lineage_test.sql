-- Create tables
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    country VARCHAR(50)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date DATE,
    total_amount DECIMAL(10,2)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2)
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity INT,
    subtotal DECIMAL(10,2)
);

-- Insert sample data
INSERT INTO customers (name, email, country) VALUES
('Alice Smith', 'alice@example.com', 'USA'),
('Bob Johnson', 'bob@example.com', 'Canada'),
('Charlie Brown', 'charlie@example.com', 'UK');

INSERT INTO products (name, price) VALUES
('Laptop', 1200.00),
('Phone', 800.00),
('Tablet', 500.00);

INSERT INTO orders (customer_id, order_date, total_amount) VALUES
(1, '2024-03-10', 2000.00),
(2, '2024-03-12', 800.00);

INSERT INTO order_items (order_id, product_id, quantity, subtotal) VALUES
(1, 1, 1, 1200.00),
(1, 3, 2, 1000.00),
(2, 2, 1, 800.00);

-- Query for SQL Lineage Testing
WITH customer_orders AS (
    SELECT c.customer_id, c.name, o.order_id, o.order_date, o.total_amount
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
)
SELECT co.name AS customer_name, p.name AS product_name, oi.quantity, oi.subtotal
FROM customer_orders co
JOIN order_items oi ON co.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE co.total_amount > 1000;

-- Aggregate sales per country
SELECT c.country, SUM(o.total_amount) AS total_sales
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.country;

-- Most purchased product
SELECT p.name, SUM(oi.quantity) AS total_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.name
ORDER BY total_sold DESC LIMIT 1;

-- View creation for SQL Lineage Testing
CREATE VIEW customer_summary AS
SELECT c.name, COUNT(o.order_id) AS total_orders, SUM(o.total_amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.name;

-- Test the view
SELECT * FROM customer_summary;

-- Cleanup for multiple runs
DROP VIEW IF EXISTS customer_summary;
DROP TABLE IF EXISTS order_items, orders, products, customers CASCADE;
