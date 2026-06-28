CREATE TABLE IF NOT EXISTS mart.f_customer_retention (
    period_id INT NOT NULL,
    period_name VARCHAR(20) NOT NULL,
    item_id INT NOT NULL,
    new_customers_count INT,
    returning_customers_count INT,
    refunded_customer_count INT,
    new_customers_revenue NUMERIC(10,2),
    returning_customers_revenue NUMERIC(10,2),
    customers_refunded NUMERIC(10,2)
);