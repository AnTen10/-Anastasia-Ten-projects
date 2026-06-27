CREATE MATERIALIZED VIEW cafe.mv_avg_check_dynamics AS
WITH yearly_avg AS (
    SELECT 
        extract(YEAR FROM s.date)::int AS year,
        s.restaurant_uuid,
        round(avg(s.avg_check), 2) AS avg_check
    FROM cafe.sales s
    WHERE extract(YEAR FROM s.date)::int <> 2023
    GROUP BY s.restaurant_uuid, extract(YEAR FROM s.date)
)
SELECT
    ya.year,
    r.name AS restaurant_name,
    r.type AS restaurant_type,
    ya.avg_check AS current_avg_check,
    lag(ya.avg_check) OVER (
        PARTITION BY ya.restaurant_uuid
        ORDER BY ya.year
    ) AS prev_avg_check,
    round(
        CASE
	        WHEN LAG(ya.avg_check) OVER (PARTITION BY ya.restaurant_uuid ORDER BY ya.year) IS NULL
	            THEN NULL
	        ELSE (ya.avg_check - LAG(ya.avg_check) OVER (PARTITION BY ya.restaurant_uuid ORDER BY ya.year)) / LAG(ya.avg_check) OVER (PARTITION BY ya.restaurant_uuid ORDER BY ya.year) * 100
	    END, 2
	) AS change_percent
FROM yearly_avg ya
JOIN cafe.restaurants r ON ya.restaurant_uuid = r.restaurant_uuid
ORDER BY r.name, ya.year;