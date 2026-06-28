from datetime import datetime
from logging import Logger
import json
from lib.dict_util import str2json

class DmCouriersLoader:
    BATCH_LIMIT = 100

    def __init__(self, reader, saver, pg_dest, log: Logger):
        self.reader = reader
        self.saver = saver
        self.pg_dest = pg_dest
        self.log = log

    def load(self):
        self.log.info("Начинается загрузка dm_couriers")
        last_loaded_ts = datetime(2022, 1, 1)

        while True:
            batch = self.reader.get_couriers(last_loaded_ts, self.BATCH_LIMIT)
            if not batch:
                self.log.info("Нет новых курьеров для загрузки")
                break

            with self.pg_dest.connection() as conn:
                for row in batch:
                    payload = str2json(row["object_value"])
                    courier_id = payload.get("_id")
                    courier_name = payload.get("name")
                    if courier_id and courier_name:
                        self.saver.save_courier(conn, courier_id, courier_name)
            last_loaded_ts = max(r["load_dttm"] for r in batch)
        self.log.info("Загрузка dm_couriers завершена")
