WITH
dwh_delta AS (
    SELECT
        dcs.customer_id AS customer_id,
        dcs.customer_name AS customer_name,
        dcs.customer_email AS customer_email,
        dcs.customer_address AS customer_address,
        dcs.customer_birthday AS customer_birthday,
        fo.order_id AS order_id,
        dp.product_id AS product_id,
        dp.product_price AS product_price,
        dp.product_type AS product_type,
        dc.craftsman_id AS craftsman_id,
        DATE_PART('year', AGE(dc.craftsman_birthday)) AS craftsman_age,
        fo.order_completion_date - fo.order_created_date AS diff_order_date,
        fo.order_status AS order_status,
        TO_CHAR(fo.order_created_date, 'yyyy-mm') AS report_period,
        crd.customer_id AS exist_customer_id,
        dcs.load_dttm AS customer_load_dttm,
        dc.load_dttm AS craftsman_load_dttm,
        dp.load_dttm AS product_load_dttm
    FROM dwh.f_order fo
        INNER JOIN dwh.d_customer dcs ON fo.customer_id = dcs.customer_id
        INNER JOIN dwh.d_craftsman dc ON fo.craftsman_id = dc.craftsman_id
        INNER JOIN dwh.d_product dp ON fo.product_id = dp.product_id
        LEFT JOIN dwh.customer_report_datamart crd ON dcs.customer_id = crd.customer_id
    WHERE 
        fo.load_dttm > (SELECT COALESCE(MAX(load_dttm),'1900-01-01') FROM dwh.load_dates_customer_report_datamart)
        OR dcs.load_dttm > (SELECT COALESCE(MAX(load_dttm),'1900-01-01') FROM dwh.load_dates_customer_report_datamart)
        OR dc.load_dttm > (SELECT COALESCE(MAX(load_dttm),'1900-01-01') FROM dwh.load_dates_customer_report_datamart)
        OR dp.load_dttm > (SELECT COALESCE(MAX(load_dttm),'1900-01-01') FROM dwh.load_dates_customer_report_datamart)
),

dwh_update_delta AS (
    SELECT dd.exist_customer_id AS customer_id
    FROM dwh_delta dd
    WHERE dd.exist_customer_id IS NOT NULL
),

dwh_delta_insert_result AS (
    WITH
    T_top_category AS (
        SELECT
            dd.customer_id,
            dd.product_type,
            COUNT(dd.product_id) AS count_product,
            ROW_NUMBER() OVER (
                PARTITION BY dd.customer_id ORDER BY COUNT(dd.product_id) DESC
            ) AS rn
        FROM dwh_delta dd
        WHERE dd.exist_customer_id IS NULL
        GROUP BY dd.customer_id, dd.product_type
    ),
    
    T_top_craftsman AS (
        SELECT
            dd.customer_id,
            dd.craftsman_id,
            COUNT(dd.order_id) AS cnt_orders,
            ROW_NUMBER() OVER (
                PARTITION BY dd.customer_id ORDER BY COUNT(dd.order_id) DESC
            ) AS rn
        FROM dwh_delta dd
        WHERE dd.exist_customer_id IS NULL
        GROUP BY dd.customer_id, dd.craftsman_id
    )
    
    SELECT 
        T2.customer_id,
        T2.customer_name,
        T2.customer_email,
        T2.customer_address,
        T2.customer_birthday,
        T2.customer_money,
        T2.platform_money,
        T2.count_order,
        T2.avg_price_order,
        T2.avg_age_craftsman,
        tc.product_type AS top_product_category,
        tm.craftsman_id AS top_craftsman_id,
        T2.median_time_order_completed,
        T2.count_order_created,
        T2.count_order_in_progress,
        T2.count_order_delivery,
        T2.count_order_done,
        T2.count_order_not_done,
        T2.report_period
    FROM (
        SELECT 
            T1.customer_id,
            T1.customer_name,
            T1.customer_email,
            T1.customer_address,
            T1.customer_birthday,
            SUM(T1.product_price) - SUM(T1.product_price) * 0.1 AS customer_money,
            SUM(T1.product_price) * 0.1 AS platform_money,
            COUNT(T1.order_id) AS count_order,
            AVG(T1.product_price) AS avg_price_order,
            AVG(T1.craftsman_age) AS avg_age_craftsman,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY T1.diff_order_date) AS median_time_order_completed,
            SUM(CASE WHEN T1.order_status = 'created' THEN 1 ELSE 0 END) AS count_order_created,
            SUM(CASE WHEN T1.order_status = 'in progress' THEN 1 ELSE 0 END) AS count_order_in_progress,
            SUM(CASE WHEN T1.order_status = 'delivery' THEN 1 ELSE 0 END) AS count_order_delivery,
            SUM(CASE WHEN T1.order_status = 'done' THEN 1 ELSE 0 END) AS count_order_done,
            SUM(CASE WHEN T1.order_status != 'done' THEN 1 ELSE 0 END) AS count_order_not_done,
            T1.report_period
        FROM dwh_delta T1
        WHERE T1.exist_customer_id IS NULL
        GROUP BY 
            T1.customer_id, T1.customer_name, T1.customer_email,
            T1.customer_address, T1.customer_birthday, T1.report_period
    ) T2
    LEFT JOIN T_top_category tc 
        ON T2.customer_id = tc.customer_id AND tc.rn = 1
    LEFT JOIN T_top_craftsman tm
        ON T2.customer_id = tm.customer_id AND tm.rn = 1
),

dwh_delta_update_result AS (
    WITH
    T_top_category AS (
        SELECT
            dd.customer_id,
            dd.product_type,
            COUNT(dd.product_id) AS count_product,
            ROW_NUMBER() OVER (
                PARTITION BY dd.customer_id ORDER BY COUNT(dd.product_id) DESC
            ) AS rn
        FROM dwh_delta dd
        GROUP BY dd.customer_id, dd.product_type
    ),
    
    T_top_craftsman AS (
        SELECT
            dd.customer_id,
            dd.craftsman_id,
            COUNT(dd.order_id) AS cnt_orders,
            ROW_NUMBER() OVER (
                PARTITION BY dd.customer_id ORDER BY COUNT(dd.order_id) DESC
            ) AS rn
        FROM dwh_delta dd
        GROUP BY dd.customer_id, dd.craftsman_id
    )
    
    SELECT 
        T2.customer_id,
        T2.customer_name,
        T2.customer_email,
        T2.customer_address,
        T2.customer_birthday,
        T2.customer_money,
        T2.platform_money,
        T2.count_order,
        T2.avg_price_order,
        T2.avg_age_craftsman,
        tc.product_type AS top_product_category,
        tm.craftsman_id AS top_craftsman_id,
        T2.median_time_order_completed,
        T2.count_order_created,
        T2.count_order_in_progress,
        T2.count_order_delivery,
        T2.count_order_done,
        T2.count_order_not_done,
        T2.report_period
    FROM (
        SELECT 
            T1.customer_id,
            T1.customer_name,
            T1.customer_email,
            T1.customer_address,
            T1.customer_birthday,
            SUM(T1.product_price) - SUM(T1.product_price) * 0.1 AS customer_money,
            SUM(T1.product_price) * 0.1 AS platform_money,
            COUNT(T1.order_id) AS count_order,
            AVG(T1.product_price) AS avg_price_order,
            AVG(T1.craftsman_age) AS avg_age_craftsman,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY T1.diff_order_date) AS median_time_order_completed,
            SUM(CASE WHEN T1.order_status = 'created' THEN 1 ELSE 0 END) AS count_order_created,
            SUM(CASE WHEN T1.order_status = 'in progress' THEN 1 ELSE 0 END) AS count_order_in_progress,
            SUM(CASE WHEN T1.order_status = 'delivery' THEN 1 ELSE 0 END) AS count_order_delivery,
            SUM(CASE WHEN T1.order_status = 'done' THEN 1 ELSE 0 END) AS count_order_done,
            SUM(CASE WHEN T1.order_status != 'done' THEN 1 ELSE 0 END) AS count_order_not_done,
            T1.report_period
        FROM (
            SELECT 
                dcs.customer_id,
                dcs.customer_name,
                dcs.customer_email,
                dcs.customer_address,
                dcs.customer_birthday,
                dc.craftsman_id,
                DATE_PART('year', AGE(dc.craftsman_birthday)) AS craftsman_age,
                fo.order_id,
                dp.product_id,
                dp.product_price,
                dp.product_type,
                fo.order_completion_date - fo.order_created_date AS diff_order_date,
                fo.order_status,
                TO_CHAR(fo.order_created_date, 'yyyy-mm') AS report_period
            FROM dwh.f_order fo
                INNER JOIN dwh.d_craftsman dc ON fo.craftsman_id = dc.craftsman_id
                INNER JOIN dwh.d_customer dcs ON fo.customer_id = dcs.customer_id
                INNER JOIN dwh.d_product dp ON fo.product_id = dp.product_id
                INNER JOIN dwh_update_delta ud ON fo.customer_id = ud.customer_id
        ) T1
        GROUP BY
            T1.customer_id, T1.customer_name, T1.customer_email,
            T1.customer_address, T1.customer_birthday, T1.report_period
    ) T2
    LEFT JOIN T_top_category tc 
        ON T2.customer_id = tc.customer_id AND tc.rn = 1
    LEFT JOIN T_top_craftsman tm
        ON T2.customer_id = tm.customer_id AND tm.rn = 1
),

insert_delta AS (
    INSERT INTO dwh.customer_report_datamart (
        customer_id,
        customer_name,
        customer_email,
        customer_address,
        customer_birthday,
        customer_money,
        platform_money,
        count_order,
        avg_price_order,
        avg_age_craftsman,
        median_time_order_completed,
        top_product_category,
        top_craftsman_id,
        count_order_created,
        count_order_in_progress,
        count_order_delivery,
        count_order_done,
        count_order_not_done,
        report_period
    )
    SELECT 
        customer_id,
        customer_name,
        customer_email,
        customer_address,
        customer_birthday,
        customer_money,
        platform_money,
        count_order,
        avg_price_order,
        avg_age_craftsman,
        median_time_order_completed,
        top_product_category,
        top_craftsman_id,
        count_order_created,
        count_order_in_progress,
        count_order_delivery,
        count_order_done,
        count_order_not_done,
        report_period
    FROM dwh_delta_insert_result
),

update_delta AS (
    UPDATE dwh.customer_report_datamart SET
        customer_name = u.customer_name,
        customer_email = u.customer_email,
        customer_address = u.customer_address,
        customer_birthday = u.customer_birthday,
        customer_money = u.customer_money,
        platform_money = u.platform_money,
        count_order = u.count_order,
        avg_price_order = u.avg_price_order,
        avg_age_craftsman = u.avg_age_craftsman,
        median_time_order_completed = u.median_time_order_completed,
        top_product_category = u.top_product_category,
        top_craftsman_id = u.top_craftsman_id,
        count_order_created = u.count_order_created,
        count_order_in_progress = u.count_order_in_progress,
        count_order_delivery = u.count_order_delivery,
        count_order_done = u.count_order_done,
        count_order_not_done = u.count_order_not_done,
        report_period = u.report_period
    FROM dwh_delta_update_result u
    WHERE dwh.customer_report_datamart.customer_id = u.customer_id 
      AND dwh.customer_report_datamart.report_period = u.report_period
),

insert_load_date AS (
    INSERT INTO dwh.load_dates_customer_report_datamart (load_dttm)
    SELECT GREATEST(
        COALESCE(MAX(customer_load_dttm), NOW()),
        COALESCE(MAX(craftsman_load_dttm), NOW()),
        COALESCE(MAX(product_load_dttm), NOW())
    )
    FROM dwh_delta
)

SELECT 'increment customer datamart';
