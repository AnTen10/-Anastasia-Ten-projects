from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2
import vertica_python
from airflow.hooks.base import BaseHook

SCHEMA = "VT26021862C020__STAGING"
BATCH_SIZE = 1000


def get_pg_connection():
    conn = BaseHook.get_connection("pg_source")
    return psycopg2.connect(
        host=conn.host,
        port=conn.port,
        dbname=conn.schema,
        user=conn.login,
        password=conn.password
    )

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

def format_value(val):
    if val is None:
        return 'NULL'
    elif isinstance(val, str):
        return f"'{val}'"
    elif isinstance(val, datetime):
        return f"'{val}'"
    else:
        return str(val)


def generate_values(rows):
    values = []
    for row in rows:
        formatted = [format_value(v) for v in row]
        values.append(f"({','.join(formatted)})")
    return ",".join(values)


def load_transactions(**context):
    execution_date = context['ds']

    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()

    vertica_conn = get_vertica_connection()
    vertica_cursor = vertica_conn.cursor()

    vertica_cursor.execute(f"""
        DELETE FROM {SCHEMA}.transactions
        WHERE DATE(transaction_dt) = '{execution_date}'
    """)

    pg_cursor.execute(f"""
        SELECT *
        FROM public.transactions
        WHERE DATE(transaction_dt) = '{execution_date}'
        AND status = 'done'
    """)

    rows = pg_cursor.fetchall()

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        values_str = generate_values(batch)

        vertica_cursor.execute(f"""
            INSERT INTO {SCHEMA}.transactions
            VALUES {values_str}
        """)

    vertica_conn.commit()

    print(f"[transactions] Loaded {len(rows)} rows for {execution_date}")

    pg_cursor.close()
    vertica_cursor.close()
    pg_conn.close()
    vertica_conn.close()

def load_currencies(**context):
    execution_date = context['ds']

    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()

    vertica_conn = get_vertica_connection()
    vertica_cursor = vertica_conn.cursor()

    vertica_cursor.execute(f"""
        DELETE FROM {SCHEMA}.currencies
        WHERE DATE(date_update) = '{execution_date}'
    """)

    pg_cursor.execute(f"""
        SELECT *
        FROM public.currencies
        WHERE DATE(date_update) = '{execution_date}'
    """)

    rows = pg_cursor.fetchall()

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        values_str = generate_values(batch)

        vertica_cursor.execute(f"""
            INSERT INTO {SCHEMA}.currencies
            VALUES {values_str}
        """)

    vertica_conn.commit()

    print(f"[currencies] Loaded {len(rows)} rows for {execution_date}")

    pg_cursor.close()
    vertica_cursor.close()
    pg_conn.close()
    vertica_conn.close()
    

with DAG(
    dag_id='load_staging',
    start_date=datetime(2022, 10, 1),
    schedule_interval='@daily',
    catchup=True
) as dag:

    load_transactions_task = PythonOperator(
        task_id='load_transactions',
        python_callable=load_transactions
    )

    load_currencies_task = PythonOperator(
        task_id='load_currencies',
        python_callable=load_currencies
    )

    load_transactions_task >> load_currencies_task