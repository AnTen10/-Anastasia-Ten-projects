from lib.pg import PgConnect


class CdmRepository:
    def __init__(self, db: PgConnect):
        self._db = db


    def get_h_product_pk(self, product_id):
        """
        product_id из Kafka = business key (mongo id)
        получаем h_product_pk (uuid)
        """
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT h_product_pk
                    FROM dds.h_product
                    WHERE product_id = %s
                    LIMIT 1
                    """,
                    (product_id,)
                )

                row = cur.fetchone()
                return row[0] if row else None


    def get_product_name(self, h_product_pk):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT name
                    FROM dds.s_product_names
                    WHERE h_product_pk=%s
                    ORDER BY load_dt DESC
                    LIMIT 1
                    """,
                    (h_product_pk,)
                )

                row = cur.fetchone()
                return row[0] if row else "unknown"


    def get_category(self, h_product_pk):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        c.h_category_pk,
                        c.category_name
                    FROM dds.l_product_category l
                    JOIN dds.h_category c
                      ON l.h_category_pk = c.h_category_pk
                    WHERE l.h_product_pk=%s
                    LIMIT 1
                    """,
                    (h_product_pk,)
                )

                return cur.fetchone()


    def upsert_user_product(
        self,
        user_id,
        product_id,
        product_name
    ):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cdm.user_product_counters(
                        user_id,
                        product_id,
                        product_name,
                        order_cnt
                    )
                    VALUES (%s,%s,%s,1)

                    ON CONFLICT (user_id, product_id)
                    DO UPDATE SET
                    order_cnt=
                    cdm.user_product_counters.order_cnt+1
                    """,
                    (
                        user_id,
                        product_id,
                        product_name
                    )
                )


    def upsert_user_category(
        self,
        user_id,
        category_id,
        category_name
    ):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cdm.user_category_counters(
                        user_id,
                        category_id,
                        category_name,
                        order_cnt
                    )
                    VALUES (%s,%s,%s,1)

                    ON CONFLICT (user_id, category_id)
                    DO UPDATE SET
                    order_cnt=
                    cdm.user_category_counters.order_cnt+1
                    """,
                    (
                        user_id,
                        category_id,
                        category_name
                    )
                )