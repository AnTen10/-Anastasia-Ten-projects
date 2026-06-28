import json
from datetime import datetime

class RestaurantsLoader:
    def __init__(self, reader, pg_dest, saver, log):
        self._reader = reader
        self._pg_dest = pg_dest
        self._saver = saver
        self._log = log

    def load(self):
        self._log.info("Начинается загрузка ресторанов")

        total_rows = 0
        with self._pg_dest.connection() as conn:
            for batch in self._reader.get_restaurants():
                if not batch:
                    self._log.info("Нет ресторанов для загрузки")
                    break

                rows = [
                    (r["_id"], json.dumps(r), datetime.utcnow())
                    for r in batch
                ]

                self._saver.save(conn, rows)
                total_rows += len(rows)

        self._log.info(f"Загрузка ресторанов завершена. Всего строк: {total_rows}")
