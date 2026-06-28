from lib.dict_util import json2str

class ApiSaver:
    def __init__(self, table_name: str):
        self._table_name = table_name

    def save(self, conn, rows):
        with conn.cursor() as cur:
            for object_id, object_value, load_dttm in rows:
                str_val = json2str(object_value)

                cur.execute(
                    f"""
                        INSERT INTO {self._table_name}
                        (object_id, object_value, load_dttm)
                        VALUES (%(id)s, %(val)s, %(load_dttm)s)
                        ON CONFLICT (object_id) DO NOTHING;
                    """,
                    {
                        "id": object_id,
                        "val": str_val,
                        "load_dttm": load_dttm
                    }
                )