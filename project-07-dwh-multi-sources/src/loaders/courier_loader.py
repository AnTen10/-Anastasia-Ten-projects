import json
from datetime import datetime
from lib import PgConnect


class CourierLoader:

    def __init__(self, reader, pg_dest: PgConnect, saver, log):
        self._reader = reader
        self._pg_dest = pg_dest
        self._saver = saver
        self._log = log

    def load(self):
        self._log.info("Начинается загрузка курьеров")

        all_rows = []

        for couriers_batch in self._reader.get_couriers():
            for courier in couriers_batch:
                row = (
                    courier["_id"],
                    json.dumps(courier),
                    datetime.utcnow()
                )
                all_rows.append(row)

        if not all_rows:
            self._log.info("Нет курьеров для загрузки")
            return

        with self._pg_dest.connection() as conn:
            self._saver.save(conn, all_rows)

        self._log.info(f"Загрузка курьеров завершена. Загружено {len(all_rows)} строк")