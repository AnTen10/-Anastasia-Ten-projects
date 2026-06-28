from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "data_lake_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
)

# -----------------------------
# Step 2
# -----------------------------
step2 = BashOperator(
    task_id="step2_user_vitrina",
    bash_command="""
    spark-submit /lessons/plugins/step2_user_vitrina.py
    """,
    dag=dag
)

# -----------------------------
# Step 3
# -----------------------------
step3 = BashOperator(
    task_id="step3_zone_vitrina",
    bash_command="""
    spark-submit /lessons/plugins/step3_zone_vitrina.py
    """,
    dag=dag
)

# -----------------------------
# Step 4
# -----------------------------
step4 = BashOperator(
    task_id="step4_friend_recommendation",
    bash_command="""
    spark-submit /lessons/plugins/step4_friend_recommendation.py
    """,
    dag=dag
)

# -----------------------------
# Зависимости
# -----------------------------
step2 >> step3 >> step4