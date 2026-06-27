CREATE SCHEMA cafe;

CREATE TYPE cafe.restaurant_type AS ENUM
    ('coffee_shop', 'restaurant', 'bar', 'pizzeria');

CREATE TABLE cafe.restaurants (
    restaurant_uuid uuid PRIMARY KEY DEFAULT GEN_RANDOM_UUID(),
    name VARCHAR NOT NULL,
    type cafe.restaurant_type NOT NULL,
    menu jsonb
);

CREATE TABLE cafe.managers (
    manager_uuid uuid PRIMARY KEY DEFAULT GEN_RANDOM_UUID(),
    name VARCHAR NOT NULL,
    phone VARCHAR
);

CREATE TABLE cafe.restaurant_manager_work_dates (
    restaurant_uuid UUID NOT NULL,
    manager_uuid UUID NOT NULL,
    work_start DATE NOT NULL,
    work_end DATE NOT NULL,
    PRIMARY KEY (restaurant_uuid, manager_uuid),
    FOREIGN KEY (restaurant_uuid) REFERENCES cafe.restaurants(restaurant_uuid),
    FOREIGN KEY (manager_uuid) REFERENCES cafe.managers(manager_uuid)
);

CREATE TABLE cafe.sales (
    date DATE NOT NULL,
    restaurant_uuid UUID NOT NULL,
    avg_check NUMERIC,
    PRIMARY KEY (date, restaurant_uuid),
    FOREIGN KEY (restaurant_uuid) REFERENCES cafe.restaurants(restaurant_uuid)
);
