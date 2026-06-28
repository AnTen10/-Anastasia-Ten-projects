DROP TABLE IF EXISTS dwh.craftsman_report_datamart;
CREATE TABLE IF NOT EXISTS dwh.craftsman_report_datamart (
    id BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    craftsman_id BIGINT NOT NULL,
    craftsman_name VARCHAR NOT NULL,
    craftsman_address VARCHAR NOT NULL,
    craftsman_birthday DATE NOT NULL,
    craftsman_email VARCHAR NOT NULL,
    craftsman_money NUMERIC(15,2) NOT NULL,
    platform_money BIGINT NOT NULL,
    count_order BIGINT NOT NULL,
    avg_price_order NUMERIC(10,2) NOT NULL,
    avg_age_customer NUMERIC(3,1) NOT NULL,
    median_time_order_completed NUMERIC(10,1),
    top_product_category VARCHAR NOT NULL,
    count_order_created BIGINT NOT NULL,
    count_order_in_progress BIGINT NOT NULL,
    count_order_delivery BIGINT NOT NULL,
    count_order_done BIGINT NOT NULL,
    count_order_not_done BIGINT NOT NULL,
    report_period VARCHAR NOT NULL,
    CONSTRAINT craftsman_report_datamart_pk PRIMARY KEY (id)
);

DROP TABLE IF EXISTS dwh.load_dates_craftsman_report_datamart;
CREATE TABLE IF NOT EXISTS dwh.load_dates_craftsman_report_datamart (
    id BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    load_dttm DATE NOT NULL,
    CONSTRAINT load_dates_craftsman_report_datamart_pk PRIMARY KEY (id)
);