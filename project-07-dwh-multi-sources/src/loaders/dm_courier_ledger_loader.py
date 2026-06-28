from typing import Optional
import logging
from psycopg import Connection
from decimal import Decimal


class DmCourierLedgerLoader:
    PERCENT_RULES = [
        (Decimal("4.0"), Decimal("0.05"), Decimal("100")),
        (Decimal("4.5"), Decimal("0.07"), Decimal("150")),
        (Decimal("4.9"), Decimal("0.08"), Decimal("175")),
        (Decimal("5.0"), Decimal("0.10"), Decimal("200"))
    ]

    def __init__(self, pg_dest: Optional[Connection] = None, log: Optional[logging.Logger] = None):
        self.pg_dest = pg_dest
        self.log = log or logging.getLogger(__name__)

    def calculate_courier_order_sum(self, avg_rate, order_total) -> Decimal:
        avg_rate = Decimal(avg_rate)
        order_total = Decimal(order_total)

        for rate_threshold, pct, minimum in self.PERCENT_RULES:
            if avg_rate < rate_threshold:
                return max(order_total * pct, minimum)

        return max(order_total * Decimal("0.10"), Decimal("200"))

    def load_courier_ledger(self):
        self.log.info("Начинается загрузка dm_courier_ledger")

        sql = """
        WITH deliveries_with_order_sum AS (
            SELECT 
                d.delivery_id,
                d.courier_id,
                c.courier_name,
                d.order_ts,
                d.rate,
                d.tip_sum,
                COALESCE(ps_sum.total_order_sum, 0) AS total_order_sum
            FROM dds.fct_deliveries d
            JOIN dds.dm_couriers c ON d.courier_id = c.courier_id
            LEFT JOIN (
                SELECT o.id AS order_id, SUM(ps.total_sum) AS total_order_sum
                FROM dds.dm_orders o
                JOIN dds.fct_product_sales ps ON ps.order_id::text = o.id::text
                GROUP BY o.id
            ) ps_sum ON ps_sum.order_id::text = d.order_id::text
        ),
        monthly_agg AS (
            SELECT
                courier_id,
                courier_name,
                EXTRACT(YEAR FROM order_ts)::int AS settlement_year,
                EXTRACT(MONTH FROM order_ts)::int AS settlement_month,
                COUNT(*) AS orders_count,
                SUM(total_order_sum) AS orders_total_sum,
                AVG(rate)::numeric(3,2) AS rate_avg,
                SUM(tip_sum) AS courier_tips_sum
            FROM deliveries_with_order_sum
            GROUP BY courier_id, courier_name, settlement_year, settlement_month
        )
        INSERT INTO cdm.dm_courier_ledger (
            courier_id, courier_name, settlement_year, settlement_month,
            orders_count, orders_total_sum, rate_avg,
            order_processing_fee, courier_order_sum, courier_tips_sum, courier_reward_sum
        )
        SELECT
            courier_id,
            courier_name,
            settlement_year,
            settlement_month,
            orders_count,
            orders_total_sum,
            rate_avg,
            orders_total_sum * 0.25,
            0,
            courier_tips_sum,
            0
        FROM monthly_agg
        ON CONFLICT (courier_id, settlement_year, settlement_month) DO UPDATE
        SET
            orders_count = EXCLUDED.orders_count,
            orders_total_sum = EXCLUDED.orders_total_sum,
            rate_avg = EXCLUDED.rate_avg,
            order_processing_fee = EXCLUDED.order_processing_fee,
            courier_tips_sum = EXCLUDED.courier_tips_sum
        RETURNING id, rate_avg, orders_total_sum, courier_tips_sum;
        """

        with self.pg_dest.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()

                for r in rows:
                    record_id, avg_rate, orders_total, tips_sum = r

                    order_sum = self.calculate_courier_order_sum(avg_rate, orders_total)

                    tips_sum = Decimal(tips_sum or 0)
                    reward_sum = order_sum + tips_sum * Decimal("0.95")

                    cur.execute(
                        """
                        UPDATE cdm.dm_courier_ledger
                        SET courier_order_sum = %s,
                            courier_reward_sum = %s
                        WHERE id = %s
                        """,
                        (order_sum, reward_sum, record_id)
                    )

            conn.commit()

        self.log.info("dm_courier_ledger успешно загружен")
