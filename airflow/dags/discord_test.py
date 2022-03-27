import datetime

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.providers.discord.operators.discord_webhook import DiscordWebhookOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


with DAG(
    dag_id="test_postgresql_and_discord",
    description="Test if we can connect to PostgreSQL database and send Discord message.",
    start_date=datetime.datetime(2022, 3, 27),
    schedule_interval="@once",
    catchup=False,
) as dag:
    pg_version_task_id = "postgresql_version"
    pg_check_version_task = PostgresOperator(
        task_id=pg_version_task_id,
        sql="SELECT version();",
        do_xcom_push=True,
    )

    xcom_template = "{{ task_instance.xcom_pull(task_ids='" + pg_version_task_id + "') }}"
    send_discord_message_task = DiscordWebhookOperator(
        task_id="send_discord_message",
        http_conn_id="discord_webhook",
        message="Testing connectivity. PostgreSQL version: " + xcom_template,
    )

    # set relationship between tasks
    chain(
        pg_check_version_task,
        send_discord_message_task,
    )
