from typing import List
from psycopg.rows import dict_row
from lib import PgConnect
from datetime import datetime


class DmCouriersReader:
    def __init__(self, pg: PgConnect):
        self.pg = pg

    def get_couriers(self, last_loaded_ts: datetime, limit: int) -> List[dict]:
        with self.pg.client().cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT object_id, object_value, load_dttm
                FROM stg.api_couriers
                WHERE load_dttm > %(threshold)s
                ORDER BY load_dttm
                LIMIT %(limit)s;
                """,
                {"threshold": last_loaded_ts, "limit": limit}
            )
            return cur.fetchall()
