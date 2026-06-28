import pendulum
import pandas as pd
import vertica_python
from airflow.decorators import dag
from airflow.operators.python import PythonOperator


def load_group_log_to_vertica():

    df_group_log = pd.read_csv("/data/group_log.csv")

    df_group_log['user_id_from'] = pd.array(df_group_log['user_id_from'], dtype="Int64")

    df_group_log['datetime'] = pd.to_datetime(df_group_log['datetime'])

    df_group_log = df_group_log.rename(columns={"datetime": "event_dt"})

    temp_file = "/data/group_log_prepared.csv"
    df_group_log.to_csv(temp_file, index=False)

    conn_info = {
        "host": os.getenv("VERTICA_HOST"),
        "port": int(os.getenv("VERTICA_PORT")),
        "user": os.getenv("VERTICA_USER"),
        "password": os.getenv("VERTICA_PASSWORD"),
        "database": os.getenv("VERTICA_DATABASE"),
        "autocommit": True
    }

    with vertica_python.connect(**conn_info) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            TRUNCATE TABLE VT26021862C020__STAGING.group_log;
        """)
        cur.execute(f"""
            COPY VT26021862C020__STAGING.group_log
            FROM LOCAL '{temp_file}'
            DELIMITER ','
            ENCLOSED BY '"'
            SKIP 1;
        """)


@dag(
    schedule_interval=None,
    start_date=pendulum.parse('2022-07-13'),
    catchup=False
)
def sprint6_dag_load_group_log():

    load_task = PythonOperator(
        task_id='load_group_log',
        python_callable=load_group_log_to_vertica
    )

    load_task


_ = sprint6_dag_load_group_log()