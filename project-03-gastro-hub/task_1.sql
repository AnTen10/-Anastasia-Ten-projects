CREATE OR REPLACE VIEW cafe.v_top3_avg_check AS
WITH avg_sales AS (
    SELECT
        s.restaurant_uuid,
        ROUND(AVG(s.avg_check), 2) AS avg_check
    FROM cafe.sales s
    GROUP BY s.restaurant_uuid
),
rating AS (
    SELECT
        r.name AS restaurant_name,
        r.type AS restaurant_type,
        a.avg_check,
        ROW_NUMBER() OVER (
            PARTITION BY r.type
            ORDER BY a.avg_check DESC
        ) AS rn
    FROM avg_sales a
    JOIN cafe.restaurants r ON a.restaurant_uuid = r.restaurant_uuid
)
SELECT restaurant_name, restaurant_type, avg_check
FROM rating
WHERE rn <= 3;