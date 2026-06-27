from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import vertica_python
from airflow.hooks.base import BaseHook

DWH_SCHEMA = "VT26021862C020__DWH"

def get_vertica_connection():
    conn = BaseHook.get_connection("vertica_dwh")
    return vertica_python.connect(
        host=conn.host,
        port=conn.port,
        user=conn.login,
        password=conn.password,
        database=conn.schema,
        autocommit=False
    )

def load_global_metrics(**context):
    execution_date = context["ds"]

    conn = get_vertica_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        DELETE FROM {DWH_SCHEMA}.global_metrics
        WHERE date_update = '{execution_date}'
    """)

    cursor.execute(f"""
        INSERT INTO {DWH_SCHEMA}.global_metrics
        SELECT
            DATE(t.transaction_dt) AS date_update,
            t.currency_code AS currency_from,

            SUM(t.amount * c.currency_with_div) AS amount_total,
            COUNT(*) AS cnt_transactions,

            COUNT(*)::FLOAT / COUNT(DISTINCT t.account_number_from)
                AS avg_transactions_per_account,

            COUNT(DISTINCT t.account_number_from)
                AS cnt_accounts_make_transactions

        FROM VT26021862C020__STAGING.transactions t
        JOIN VT26021862C020__STAGING.currencies c
            ON t.currency_code = c.currency_code
           AND DATE(t.transaction_dt) = DATE(c.date_update)

        WHERE DATE(t.transaction_dt) = '{execution_date}'
          AND t.status = 'done'
          AND t.account_number_from > 0

        GROUP BY 1, 2
    """)

    conn.commit()
    cursor.close()
    conn.close()


with DAG(
    dag_id="global_metrics_dag",
    start_date=datetime(2022, 10, 1),
    schedule_interval="@daily",
    catchup=True
) as dag:

    load_metrics = PythonOperator(
        task_id="load_global_metrics",
        python_callable=load_global_metrics
    )