import pandas as pd
from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator,BashOperator
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

username=os.getenv('username')
password=os.getenv('password')
login_cmd = "docker login -u " + username + " -p " + password

with DAG(
        dag_id="wacef_app_deploy_dag",
        schedule_interval="@monthly",
        default_args={
            "owner": "airflow",
            "retries": 3,
            "retry_delay": timedelta(minutes=30), #Because building app can take few minutes
            "start_date": datetime(2022, 12, 4),
        },
        catchup=False) as f:

    build_image_task = BashOperator(
    task_id="build_image_task",
    bash_command='docker build -t wacef_app:latest .',
    )
    
    login_docker_hub_task = BashOperator(
    task_id="login_docker_hub_task",
    bash_command=login_cmd
    )
    
    push_image_task = BashOperator(
    task_id="push_image_task",
    bash_command='docker push wacef_app:latest',
    )
    
    run_container_task = BashOperator(
    task_id="run_container_task",
    bash_command='docker run --name wacef-container -d -p 8080:8080 wacef_app:latest',
    )
    
    inspect_running_container_task = BashOperator(
    task_id="inspect_running_container_task",
    bash_command='docker inspect -f "{{ .Config.Hostname }}" wacef-container',
    )
    


build_image_task >> login_docker_hub_task >> push_image_task >> run_container_task >> inspect_running_container_task


