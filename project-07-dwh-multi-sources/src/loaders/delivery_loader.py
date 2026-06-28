import json
from datetime import datetime

class DeliveryLoader:
    def __init__(self, reader, pg_dest, saver, log):
        self._reader = reader
        self._pg_dest = pg_dest
        self._saver = saver
        self._log = log

    def load(self):
        self._log.info("Начинается загрузка доставок")

        total_rows = 0
        with self._pg_dest.connection() as conn:
            for batch in self._reader.get_delivery():
                if not batch:
                    self._log.info("Нет доставок за указанный период")
                    break

                rows = [
                    (d["delivery_id"], json.dumps(d), datetime.utcnow())
                    for d in batch
                ]

                self._saver.save(conn, rows)
                total_rows += len(rows)

        self._log.info(f"Загрузка доставок завершена. Всего строк: {total_rows}")
