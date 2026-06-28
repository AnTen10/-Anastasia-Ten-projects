import time
import requests
import json
import pandas as pd

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.hooks.http_hook import HttpHook

http_conn_id = HttpHook.get_connection('http_conn_id')
api_key = http_conn_id.extra_dejson.get('api_key')
base_url = http_conn_id.host

postgres_conn_id = 'postgresql_de'

nickname = 'riciticiten'
cohort = '11'

headers = {
    'X-Nickname': nickname,
    'X-Cohort': cohort,
    'X-Project': 'True',
    'X-API-KEY': api_key,
    'Content-Type': 'application/x-www-form-urlencoded'
}


def generate_report(ti):
    print('Making request generate_report')
    response = requests.post(f'{base_url}/generate_report', headers=headers)
    response.raise_for_status()
    task_id = json.loads(response.content)['task_id']
    ti.xcom_push(key='task_id', value=task_id)
    print(f'Response is {response.content}')


def get_report(ti):
    print('Making request get_report')
    task_id = ti.xcom_pull(key='task_id')
    report_id = None

    for _ in range(20):
        response = requests.get(f'{base_url}/get_report?task_id={task_id}', headers=headers)
        response.raise_for_status()
        payload = json.loads(response.content)
        if payload['status'] == 'SUCCESS':
            report_id = payload['data']['report_id']
            break
        time.sleep(10)

    if not report_id:
        raise TimeoutError('Report generation timeout')

    ti.xcom_push(key='report_id', value=report_id)


def get_increment(date, ti):
    print('Making request get_increment')
    report_id = ti.xcom_pull(key='report_id')
    response = requests.get(
        f'{base_url}/get_increment?report_id={report_id}&date={str(date)}T00:00:00',
        headers=headers
    )
    response.raise_for_status()
    payload = json.loads(response.content)
    increment_id = payload['data']['increment_id']
    if not increment_id:
        raise ValueError('Increment is empty')
    ti.xcom_push(key='increment_id', value=increment_id)
    print(f'increment_id={increment_id}')


def upload_data_to_staging(filename, date, pg_table, pg_schema, ti):
    increment_id = ti.xcom_pull(key='increment_id')
    s3_filename = f'https://storage.yandexcloud.net/s3-sprint3/cohort_{cohort}/{nickname}/project/{increment_id}/{filename}'
    local_file = f"{date.replace('-', '')}_{filename}"

    response = requests.get(s3_filename)
    response.raise_for_status()
    with open(local_file, 'wb') as f:
        f.write(response.content)

    df = pd.read_csv(local_file)
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
    df = df.drop_duplicates(subset=['uniq_id'])
    if 'status' not in df.columns:
        df['status'] = 'shipped'

    postgres_hook = PostgresHook(postgres_conn_id)
    engine = postgres_hook.get_sqlalchemy_engine()
    existing_ids_query = f"SELECT uniq_id FROM {pg_schema}.{pg_table}"
    existing_ids_df = pd.read_sql(existing_ids_query, engine)
    if not existing_ids_df.empty:
        df = df[~df['uniq_id'].isin(existing_ids_df['uniq_id'])]
    if df.empty:
        print("Нет новых записей.")
        return
    df.to_sql(pg_table, engine, schema=pg_schema, if_exists='append', index=False)
    print(f"{len(df)} новых записей загружено в {pg_schema}.{pg_table}")


args = {
    "owner": "student",
    'email': ['riciticiten@yandex.ru'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}

business_dt = '{{ ds }}'

with DAG(
        dag_id='sales_mart',
        default_args=args,
        description='ETL pipeline sprint3 with customer retention',
        catchup=True,
        start_date=datetime.today() - timedelta(days=7),
        end_date=datetime.today() - timedelta(days=1),
) as dag:

    generate_report = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report
    )

    get_report = PythonOperator(
        task_id='get_report',
        python_callable=get_report
    )

    get_increment = PythonOperator(
        task_id='get_increment',
        python_callable=get_increment,
        op_kwargs={'date': business_dt}
    )

    upload_user_order_inc = PythonOperator(
        task_id='upload_user_order_inc',
        python_callable=upload_data_to_staging,
        op_kwargs={
            'date': business_dt,
            'filename': 'user_order_log_inc.csv',
            'pg_table': 'user_order_log',
            'pg_schema': 'staging'
        }
    )

    update_d_item_table = PostgresOperator(
        task_id='update_d_item',
        postgres_conn_id=postgres_conn_id,
        sql="sql/mart.d_item.sql"
    )

    update_d_customer_table = PostgresOperator(
        task_id='update_d_customer',
        postgres_conn_id=postgres_conn_id,
        sql="sql/mart.d_customer.sql"
    )

    update_d_city_table = PostgresOperator(
        task_id='update_d_city',
        postgres_conn_id=postgres_conn_id,
        sql="sql/mart.d_city.sql"
    )

    update_f_sales = PostgresOperator(
        task_id='update_f_sales',
        postgres_conn_id=postgres_conn_id,
        sql="sql/mart.f_sales.sql",
        parameters={"date": business_dt}
    )

    create_f_customer_retention = PostgresOperator(
        task_id='create_f_customer_retention',
        postgres_conn_id=postgres_conn_id,
        sql="sql/mart.f_customer_retention_create.sql"
    )

    update_customer_retention = PostgresOperator(
        task_id='update_customer_retention',
        postgres_conn_id=postgres_conn_id,
        sql="sql/mart.f_customer_retention.sql",
        parameters={"date": business_dt}
    )

    (
            generate_report
            >> get_report
            >> get_increment
            >> upload_user_order_inc
            >> [update_d_item_table, update_d_city_table, update_d_customer_table]
            >> update_f_sales
            >> create_f_customer_retention
            >> update_customer_retention
    )
