from datetime import datetime

class DmCouriersSaver:

    def save_courier(self, conn, courier_id: str, courier_name: str):
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dds.dm_couriers (courier_id, courier_name)
                VALUES (%s, %s)
                ON CONFLICT (courier_id) DO NOTHING
                """,
                (courier_id, courier_name)
            )
