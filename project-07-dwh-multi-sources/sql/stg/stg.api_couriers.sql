CREATE TABLE IF NOT EXISTS stg.api_couriers (
    id SERIAL PRIMARY KEY,
    object_id TEXT NOT NULL,
    object_value JSONB NOT NULL,
    load_dttm TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT api_couriers_object_id_uq UNIQUE (object_id)
);