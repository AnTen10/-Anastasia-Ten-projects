import uuid
from datetime import datetime
from lib.pg import PgConnect


class DdsRepository:
    def __init__(self, db: PgConnect) -> None:
        self._db = db

    # H

    def insert_h_order(self, order_id: int, order_dt: str) -> uuid.UUID:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.h_order (
                        h_order_pk,
                        order_id,
                        order_dt,
                        load_dt,
                        load_src
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (order_id)
                    DO UPDATE SET order_id = EXCLUDED.order_id
                    RETURNING h_order_pk
                    """,
                    (uuid.uuid4(), order_id, order_dt, datetime.utcnow(), 'orders-system-kafka')
                )

                return cur.fetchone()[0]

    def insert_h_user(self, user_id: str) -> uuid.UUID:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.h_user (
                        h_user_pk,
                        user_id,
                        load_dt,
                        load_src
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id)
                    DO UPDATE SET user_id = EXCLUDED.user_id
                    RETURNING h_user_pk
                    """,
                    (uuid.uuid4(), user_id, datetime.utcnow(), 'orders-system-kafka')
                )

                return cur.fetchone()[0]

    def insert_h_restaurant(self, restaurant_id: str) -> uuid.UUID:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.h_restaurant (
                        h_restaurant_pk,
                        restaurant_id,
                        load_dt,
                        load_src
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (restaurant_id)
                    DO UPDATE SET restaurant_id = EXCLUDED.restaurant_id
                    RETURNING h_restaurant_pk
                    """,
                    (uuid.uuid4(), restaurant_id, datetime.utcnow(), 'orders-system-kafka')
                )

                return cur.fetchone()[0]

    def insert_h_product(self, product_id: str) -> uuid.UUID:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.h_product (
                        h_product_pk,
                        product_id,
                        load_dt,
                        load_src
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (product_id)
                    DO UPDATE SET product_id = EXCLUDED.product_id
                    RETURNING h_product_pk
                    """,
                    (uuid.uuid4(), product_id, datetime.utcnow(), 'orders-system-kafka')
                )

                return cur.fetchone()[0]
            
    def insert_h_category(self, category_name: str) -> uuid.UUID:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.h_category (
                        h_category_pk,
                        category_name,
                        load_dt,
                        load_src
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (category_name)
                    DO UPDATE SET category_name = EXCLUDED.category_name
                    RETURNING h_category_pk
                    """,
                    (
                        uuid.uuid4(),
                        category_name,
                        datetime.utcnow(),
                        'orders-system-kafka'
                    )
                )

                return cur.fetchone()[0]

    # L

    def insert_l_order_user(self, h_order_pk, h_user_pk):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.l_order_user (
                        hk_order_user_pk,
                        h_order_pk,
                        h_user_pk,
                        load_dt,
                        load_src
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (uuid.uuid4(), h_order_pk, h_user_pk, datetime.utcnow(), 'orders-system-kafka')
                )

    def insert_l_order_product(self, h_order_pk, h_product_pk):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.l_order_product (
                        hk_order_product_pk,
                        h_order_pk,
                        h_product_pk,
                        load_dt,
                        load_src
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (uuid.uuid4(), h_order_pk, h_product_pk, datetime.utcnow(), 'orders-system-kafka')
                )

    def insert_l_product_restaurant(self, h_product_pk, h_restaurant_pk):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.l_product_restaurant (
                        hk_product_restaurant_pk,
                        h_product_pk,
                        h_restaurant_pk,
                        load_dt,
                        load_src
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (uuid.uuid4(), h_product_pk, h_restaurant_pk, datetime.utcnow(), 'orders-system-kafka')
                )

    def insert_l_product_category(
        self,
        h_product_pk,
        h_category_pk
    ):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.l_product_category (
                        hk_product_category_pk,
                        h_product_pk,
                        h_category_pk,
                        load_dt,
                        load_src
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        uuid.uuid4(),
                        h_product_pk,
                        h_category_pk,
                        datetime.utcnow(),
                        'orders-system-kafka'
                    )
                )

    # S
    
    def insert_s_order_cost(self, h_order_pk, cost, payment):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.s_order_cost (
                        h_order_pk,
                        cost,
                        payment,
                        load_dt,
                        load_src,
                        hk_order_cost_hashdiff
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (h_order_pk, load_dt) DO NOTHING
                    """,
                    (
                        h_order_pk,
                        cost,
                        payment,
                        datetime.utcnow(),
                        'orders-system-kafka',
                        uuid.uuid4()
                    )
                )

    def insert_s_order_status(self, h_order_pk, status):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.s_order_status (
                        h_order_pk,
                        status,
                        load_dt,
                        load_src,
                        hk_order_status_hashdiff
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (h_order_pk, load_dt) DO NOTHING
                    """,
                    (
                        h_order_pk,
                        status,
                        datetime.utcnow(),
                        'orders-system-kafka',
                        uuid.uuid4()
                    )
                )

    def insert_s_product_names(
        self,
        h_product_pk,
        name
    ):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.s_product_names (
                        h_product_pk,
                        name,
                        load_dt,
                        load_src,
                        hk_product_names_hashdiff
                    )
                    VALUES (%s,%s,%s,%s,%s)
                    ON CONFLICT (h_product_pk, load_dt)
                    DO NOTHING
                    """,
                    (
                        h_product_pk,
                        name,
                        datetime.utcnow(),
                        'orders-system-kafka',
                        uuid.uuid4()
                    )
                )


    def insert_s_restaurant_names(
        self,
        h_restaurant_pk,
        name
    ):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.s_restaurant_names (
                        h_restaurant_pk,
                        name,
                        load_dt,
                        load_src,
                        hk_restaurant_names_hashdiff
                    )
                    VALUES (%s,%s,%s,%s,%s)
                    ON CONFLICT (h_restaurant_pk, load_dt)
                    DO NOTHING
                    """,
                    (
                        h_restaurant_pk,
                        name,
                        datetime.utcnow(),
                        'orders-system-kafka',
                        uuid.uuid4()
                    )
                )


    def insert_s_user_names(
        self,
        h_user_pk,
        username,
        userlogin
    ):
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dds.s_user_names (
                        h_user_pk,
                        username,
                        userlogin,
                        load_dt,
                        load_src,
                        hk_user_names_hashdiff
                    )
                    VALUES (%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (h_user_pk, load_dt)
                    DO NOTHING
                    """,
                    (
                        h_user_pk,
                        username,
                        userlogin,
                        datetime.utcnow(),
                        'orders-system-kafka',
                        uuid.uuid4()
                    )
                )