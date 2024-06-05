import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from random import randint

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.constants import BASE_CURRENCY
from src.exchange_rates import fetch_and_merge_exchange_rates  # Make sure this module is available

# Define a function to simulate task branching
def choose_next_task():
    if randint(1, 100) > 50:
        return 'task_success'
    else:
        return 'task_failure'

# Define a simple success task
def success_task():
    print("Task succeeded")

# Define a simple failure task
def failure_task():
    print("Task failed")

# Define the DAG
with DAG(
    "my_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    # Define tasks
    fetch_exchange_rates = PythonOperator(
        task_id="fetch_exchange_rates",
        python_callable=fetch_and_merge_exchange_rates,
    )

    branch_task = BranchPythonOperator(
        task_id='branch_task',
        python_callable=choose_next_task,
    )

    task_success = PythonOperator(
        task_id='task_success',
        python_callable=success_task,
    )

    task_failure = PythonOperator(
        task_id='task_failure',
        python_callable=failure_task,
    )

    final_task = BashOperator(
        task_id='final_task',
        bash_command='echo "Pipeline complete!"',
        trigger_rule='none_failed_or_skipped',
    )

    # Set task dependencies
    fetch_exchange_rates >> branch_task
    branch_task >> [task_success, task_failure] >> final_task
