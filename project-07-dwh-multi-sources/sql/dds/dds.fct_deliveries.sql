CREATE TABLE dds.fct_deliveries (
    delivery_id text NOT NULL,
    order_id text NULL,
    courier_id text NULL,
    order_ts timestamp NULL,
    rate int4 NULL,
    tip_sum numeric(14, 2) NULL,
    CONSTRAINT fct_deliveries_pkey PRIMARY KEY (delivery_id)
);
