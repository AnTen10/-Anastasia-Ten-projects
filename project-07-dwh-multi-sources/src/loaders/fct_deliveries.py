class FctDeliveries:

    def delivery(self, conn):
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dds.fct_deliveries (
                    delivery_id,
                    order_id,
                    courier_id,
                    order_ts,
                    rate,
                    tip_sum
                )
                SELECT
                    object_id,
                    (object_value->>'order_id')::text,
                    (object_value->>'courier_id')::text,
                    (object_value->>'delivery_ts')::timestamp,
                    (object_value->>'rate')::int,
                    (object_value->>'tip_sum')::numeric
                FROM stg.api_deliveries
                ON CONFLICT (delivery_id) DO NOTHING
                """
            ) 
