DROP TABLE IF EXISTS tmp_sources_fact;

CREATE TEMP TABLE tmp_sources_fact AS 
SELECT
    dp.product_id,
    dc.craftsman_id,
    dcust.customer_id,
    src.order_created_date,
    src.order_completion_date,
    src.order_status,
    current_timestamp AS load_dttm
FROM tmp_sources src
JOIN dwh.d_craftsman dc
    ON dc.craftsman_name = src.craftsman_name 
    AND dc.craftsman_email = src.craftsman_email
JOIN dwh.d_customer dcust 
    ON dcust.customer_name = src.customer_name 
    AND dcust.customer_email = src.customer_email 
JOIN dwh.d_product dp 
    ON dp.product_name = src.product_name 
    AND dp.product_description = src.product_description 
    AND dp.product_price = src.product_price;

MERGE INTO dwh.f_order f
USING tmp_sources_fact t
ON f.product_id = t.product_id 
AND f.craftsman_id = t.craftsman_id 
AND f.customer_id = t.customer_id 
AND f.order_created_date = t.order_created_date
WHEN MATCHED THEN
    UPDATE SET
        order_completion_date = t.order_completion_date, 
        order_status = t.order_status,
        load_dttm = current_timestamp
WHEN NOT MATCHED THEN
    INSERT (
        product_id, 
        craftsman_id, 
        customer_id, 
        order_created_date, 
        order_completion_date, 
        order_status, 
        load_dttm
    )
    VALUES (
        t.product_id, 
        t.craftsman_id, 
        t.customer_id, 
        t.order_created_date, 
        t.order_completion_date, 
        t.order_status, 
        current_timestamp
    );