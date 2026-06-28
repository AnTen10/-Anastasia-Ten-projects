CREATE TABLE stg.api_restaurants (
    id serial4 NOT NULL,
    object_id text NOT NULL,
    object_value jsonb NOT NULL,
    load_dttm timestamp DEFAULT now() NOT NULL,
    CONSTRAINT api_restaurants_pkey PRIMARY KEY (id),
    CONSTRAINT api_restaurants_object_id_uq UNIQUE (object_id)
);
