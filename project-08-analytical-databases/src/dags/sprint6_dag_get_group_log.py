import pendulum
import boto3
import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.decorators import dag


def fetch_s3_file(bucket: str, key: str): 
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    os.makedirs("/data", exist_ok=True) 
    
    session = boto3.session.Session() 
    s3_client = session.client( 
        service_name='s3', 
        endpoint_url='https://storage.yandexcloud.net', 
        aws_access_key_id=aws_access_key_id, 
        aws_secret_access_key=aws_secret_access_key,
    ) 
    
    s3_client.download_file( 
        Bucket=bucket, 
        Key=key, 
        Filename=f'/data/{key}' 
    )


bash_command = """
echo "===== group_log.csv ====="
head -n 10 /data/group_log.csv
"""


@dag(schedule_interval=None, start_date=pendulum.parse('2022-07-13'), catchup=False)
def sprint6_dag_get_group_log():

    fetch_group_log = PythonOperator(
        task_id='fetch_group_log',
        python_callable=fetch_s3_file,
        op_kwargs={'bucket': 'sprint6', 'key': 'group_log.csv'},
    )

    print_10_lines = BashOperator(
        task_id='print_10_lines',
        bash_command=bash_command
    )

    fetch_group_log >> print_10_lines


_ = sprint6_dag_get_group_log()