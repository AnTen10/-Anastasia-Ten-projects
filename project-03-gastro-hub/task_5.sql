WITH pizza_menu AS (
    SELECT
        r.name AS restaurant_name,
        t.key AS pizza_name,
        t.value::INT AS price
    FROM cafe.restaurants r,
         jsonb_each(r.menu -> 'Пицца') AS t(key, value)
    WHERE r.type = 'pizzeria'
),
ranked_pizza AS (
    SELECT
        restaurant_name,
        pizza_name,
        price,
        ROW_NUMBER() OVER (PARTITION BY restaurant_name ORDER BY price DESC) AS rn
    FROM pizza_menu
)
SELECT
    restaurant_name AS "Название заведения",
    pizza_name AS "Название пиццы",
    price AS "Цена"
FROM ranked_pizza
WHERE rn = 1
ORDER BY restaurant_name;