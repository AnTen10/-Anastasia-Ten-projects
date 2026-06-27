----------------------------------------------------
-- ЭТАП 1. Создание схем
----------------------------------------------------

CREATE SCHEMA raw_data;

CREATE TABLE raw_data.sales (
    id SERIAL PRIMARY KEY,
    auto VARCHAR,
    gasoline_consumption NUMERIC(5,2) NULL,
    price NUMERIC(9, 2),
    date DATE,
    person_name VARCHAR,
    phone VARCHAR,
    discount NUMERIC(5, 2),
    brand_origin VARCHAR NULL
);

COPY raw_data.sales(id, auto, gasoline_consumption, price, date, person_name, phone, discount, brand_origin)
FROM 'C:/cars.csv'
DELIMITER ','
NULL 'null'
CSV HEADER;

CREATE SCHEMA car_shop;

CREATE TABLE car_shop.countries (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE car_shop.brands (
    brand_id SERIAL PRIMARY KEY,
    brand_name VARCHAR UNIQUE NOT NULL,
    country_id INT REFERENCES car_shop.countries(country_id)
);

CREATE TABLE car_shop.models (
    model_id SERIAL PRIMARY KEY,
    brand_id INT REFERENCES car_shop.brands(brand_id),
    model_name VARCHAR NOT NULL,
    gasoline_consumption NUMERIC(5,2) NULL,
    UNIQUE (brand_id, model_name)
);

CREATE TABLE car_shop.colors (
    color_id SERIAL PRIMARY KEY,
    color_name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE car_shop.customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    phone VARCHAR UNIQUE NOT NULL
);

CREATE TABLE car_shop.sales (
    sale_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES car_shop.customers(customer_id),
    model_id INT REFERENCES car_shop.models(model_id),
    color_id INT REFERENCES car_shop.colors(color_id),
    price NUMERIC(9, 2),
    sale_date DATE NOT NULL,
    discount NUMERIC(5, 2)
);

INSERT INTO car_shop.countries (country_name)
SELECT DISTINCT brand_origin
FROM raw_data.sales
WHERE brand_origin IS NOT NULL
ON CONFLICT (country_name) DO NOTHING;

INSERT INTO car_shop.brands (brand_name, country_id)
SELECT DISTINCT
    SPLIT_PART(auto, ' ', 1) AS brand_name,
    c.country_id
FROM raw_data.sales s
LEFT JOIN car_shop.countries c ON s.brand_origin = c.country_name
ON CONFLICT (brand_name) DO NOTHING;


INSERT INTO car_shop.models (brand_id, model_name, gasoline_consumption)
SELECT DISTINCT
    b.brand_id,
    TRIM(SPLIT_PART(SPLIT_PART(s.auto, ',', 1), ' ', 2)) AS model_name, -- берём всё после бренда до запятой
    s.gasoline_consumption
FROM raw_data.sales s
JOIN car_shop.brands b ON SPLIT_PART(s.auto, ' ', 1) = b.brand_name;

INSERT INTO car_shop.colors (color_name)
SELECT DISTINCT TRIM(SPLIT_PART(auto, ',', 2)) AS color_name
FROM raw_data.sales
WHERE SPLIT_PART(auto, ',', 2) IS NOT NULL
ON CONFLICT (color_name) DO NOTHING;

INSERT INTO car_shop.customers (name, phone)
SELECT DISTINCT person_name, phone
FROM raw_data.sales
ON CONFLICT (phone) DO NOTHING;

INSERT INTO car_shop.sales (customer_id, model_id, color_id, price, sale_date, discount)
SELECT
    c.customer_id,
    m.model_id,
    col.color_id,
    s.price,
    s.date,
    s.discount
FROM raw_data.sales s
JOIN car_shop.customers c ON s.person_name = c.name AND s.phone = c.phone
JOIN car_shop.brands b ON SPLIT_PART(s.auto, ' ', 1) = b.brand_name
JOIN car_shop.models m ON m.brand_id = b.brand_id AND SPLIT_PART(s.auto, ' ', 2) = m.model_name
JOIN car_shop.colors col ON TRIM(SPLIT_PART(s.auto, ',', 2)) = col.color_name;

----------------------------------------------------
-- Этап 2. Создание выборок
----------------------------------------------------

---- Процент моделей машин, у которых нет параметра `gasoline_consumption`.

SELECT
    ROUND(
        100 * SUM(CASE WHEN gasoline_consumption IS NULL THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS nulls_percentage_gasoline_consumption
FROM car_shop.models;

---- Название бренда и среднюю цену его автомобилей в разбивке по всем годам с учётом скидки.

SELECT
    b.brand_name,
    EXTRACT(YEAR FROM s.sale_date) AS year,
    ROUND(AVG(s.price * (1 - COALESCE(s.discount, 0) / 100)), 2) AS price_avg
FROM car_shop.sales s
JOIN car_shop.models m ON s.model_id = m.model_id
JOIN car_shop.brands b ON m.brand_id = b.brand_id
GROUP BY b.brand_name, EXTRACT(YEAR FROM s.sale_date)
ORDER BY b.brand_name, year;

---- Средняя цена всех автомобилей с разбивкой по месяцам в 2022 году с учётом скидки.

SELECT
    EXTRACT(MONTH FROM s.sale_date) AS month,
    EXTRACT(YEAR FROM s.sale_date) AS year,
    ROUND(AVG(s.price * (1 - COALESCE(s.discount, 0) / 100)), 2) AS price_avg
FROM car_shop.sales s
WHERE EXTRACT(YEAR FROM s.sale_date) = 2022
GROUP BY year, month
ORDER BY month;

---- Список купленных машин у каждого пользователя.

SELECT 
    c.name AS person,
    STRING_AGG(DISTINCT b.brand_name || ' ' || m.model_name, ', ') AS cars
FROM car_shop.sales s
JOIN car_shop.customers c ON s.customer_id = c.customer_id
JOIN car_shop.models m ON s.model_id = m.model_id
JOIN car_shop.brands b ON m.brand_id = b.brand_id
GROUP BY c.name
ORDER BY c.name;

---- Самая большая и самая маленькая цена продажи автомобиля с разбивкой по стране без учёта скидки.

SELECT 
    s.brand_origin,
    ROUND(MAX(s.price / (1 - COALESCE(s.discount, 0) / 100)), 2) AS price_max,
    ROUND(MIN(s.price / (1 - COALESCE(s.discount, 0) / 100)), 2) AS price_min
FROM car_shop.sales s
JOIN car_shop.models m ON s.model_id = m.model_id
JOIN car_shop.brands b ON m.brand_id = b.brand_id
JOIN car_shop.countries co ON b.country_id = co.country_id
GROUP BY co.country_name
ORDER BY co.country_name;

---- Количество всех пользователей из США.

SELECT 
    COUNT(*) AS persons_from_usa_count
FROM car_shop.customers
WHERE phone LIKE '+1%';