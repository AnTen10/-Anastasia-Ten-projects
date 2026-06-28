INSERT INTO mart.f_customer_retention (
    period_id,
    period_name,
    item_id,
    new_customers_count,
    returning_customers_count,
    refunded_customer_count,
    new_customers_revenue,
    returning_customers_revenue,
    customers_refunded
)
WITH weekly_sales AS (
    SELECT
        EXTRACT(WEEK FROM to_date(fs.date_id::text, 'YYYYMMDD')) AS period_id,
        fs.item_id,
        fs.customer_id,
        fs.status,
        SUM(fs.payment_amount) AS revenue,
        COUNT(*) AS order_count
    FROM mart.f_sales fs
    WHERE to_date(fs.date_id::text, 'YYYYMMDD')
          BETWEEN to_date('{{ ds }}', 'YYYY-MM-DD') - INTERVAL '6 days'
              AND to_date('{{ ds }}', 'YYYY-MM-DD')
    GROUP BY 1, 2, 3, 4
)
SELECT
    period_id,
    'weekly' AS period_name,
    item_id,
    COUNT(DISTINCT CASE WHEN order_count = 1 AND status != 'refunded' THEN customer_id END) AS new_customers_count,
    COUNT(DISTINCT CASE WHEN order_count > 1 AND status != 'refunded' THEN customer_id END) AS returning_customers_count,
    COUNT(DISTINCT CASE WHEN status = 'refunded' THEN customer_id END) AS refunded_customer_count,
    SUM(CASE WHEN order_count = 1 AND status != 'refunded' THEN revenue ELSE 0 END) AS new_customers_revenue,
    SUM(CASE WHEN order_count > 1 AND status != 'refunded' THEN revenue ELSE 0 END) AS returning_customers_revenue,
    SUM(CASE WHEN status = 'refunded' THEN revenue ELSE 0 END) AS customers_refunded
FROM weekly_sales
GROUP BY period_id, item_id
ORDER BY period_id, item_id;