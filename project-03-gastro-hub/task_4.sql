WITH pizza_counts AS (
    SELECT
        r.name AS restaurant_name,
        COUNT(*) AS pizza_count
    FROM cafe.restaurants r
    CROSS JOIN jsonb_each_text(r.menu -> 'Пицца') m
    WHERE r.type = 'pizzeria'
    GROUP BY r.name
),
rating AS (
    SELECT
        restaurant_name,
        pizza_count,
        DENSE_RANK() OVER (ORDER BY pizza_count DESC) AS rk
    FROM pizza_counts
)
SELECT restaurant_name, pizza_count
FROM rating
WHERE rk = 1;
