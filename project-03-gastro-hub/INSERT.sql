INSERT INTO cafe.restaurants (restaurant_uuid, name, type, menu)
SELECT
    gen_random_uuid() AS restaurant_uuid,
    s.cafe_name AS name,
    CASE lower(s.type)
        WHEN 'кофейня' THEN 'coffee_shop'::cafe.restaurant_type
        WHEN 'coffee_shop' THEN 'coffee_shop'::cafe.restaurant_type
        WHEN 'ресторан' THEN 'restaurant'::cafe.restaurant_type
        WHEN 'restaurant' THEN 'restaurant'::cafe.restaurant_type
        WHEN 'бар' THEN 'bar'::cafe.restaurant_type
        WHEN 'bar' THEN 'bar'::cafe.restaurant_type
        WHEN 'пиццерия' THEN 'pizzeria'::cafe.restaurant_type
        WHEN 'pizzeria' THEN 'pizzeria'::cafe.restaurant_type
        ELSE 'restaurant'::cafe.restaurant_type
    END AS type,
    COALESCE(m.menu, '{}'::jsonb) AS menu
FROM (
    SELECT DISTINCT ON (cafe_name) cafe_name, type
    FROM raw_data.sales
    ORDER BY cafe_name
) s
LEFT JOIN raw_data.menu m ON m.cafe_name = s.cafe_name;


INSERT INTO cafe.managers (manager_uuid, name, phone)
SELECT gen_random_uuid(), manager, manager_phone
FROM (
    SELECT DISTINCT manager, manager_phone
    FROM raw_data.sales
) t
WHERE manager IS NOT NULL;


INSERT INTO cafe.restaurant_manager_work_dates (restaurant_uuid, manager_uuid, work_start, work_end)
SELECT
    r.restaurant_uuid,
    m.manager_uuid,
    MIN(s.report_date)::date AS work_start,
    MAX(s.report_date)::date AS work_end
FROM raw_data.sales s
JOIN cafe.restaurants r ON s.cafe_name = r.name
JOIN cafe.managers m ON s.manager = m.name
GROUP BY r.restaurant_uuid, m.manager_uuid;


INSERT INTO cafe.sales (date, restaurant_uuid, avg_check)
SELECT
    s.report_date::date AS date,
    r.restaurant_uuid,
    s.avg_check
FROM raw_data.sales s
JOIN cafe.restaurants r ON s.cafe_name = r.name;