import datetime

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.python import PythonOperator
from airflow.providers.discord.operators.discord_webhook import DiscordWebhookOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


def check_postgresql_version(sql: str, postgres_conn_id: str) -> str:
    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    results = pg_hook.get_records(sql=sql)
    return results[0][0]


with DAG(
    dag_id="test_postgresql_and_discord",
    description="Test if we can connect to PostgreSQL database and send Discord message.",
    start_date=datetime.datetime(2022, 3, 27),
    schedule_interval="@once",
    catchup=False,
) as dag:
    pg_version_task_id = "postgresql_version"
    pg_check_version_task = PythonOperator(
        task_id=pg_version_task_id,
        python_callable=check_postgresql_version,
        op_args=["SELECT version();", "postgres_default"],
        do_xcom_push=True,
    )
    # PostgresOperator does not support pushing to XCOM so we do a workaround that way

    xcom_template = "{{ task_instance.xcom_pull(task_ids='" + pg_version_task_id + "') }}"
    send_discord_message_task = DiscordWebhookOperator(
        task_id="send_discord_message",
        http_conn_id="discord_webhook",
        webhook_endpoint="webhooks/{{ conn.discord_webhook.login }}/{{ conn.discord_webhook.password }}",
        message="Testing connectivity. PostgreSQL version: " + xcom_template,
    )
    # send_discord_message_task.template_fields = ["webhook_endpoint", "message", "username"]
    # use webhook_endpoint as template getting info from connection where token is a password
    # that way it won't show up in the logs

    # set relationship between tasks
    chain(
        pg_check_version_task,
        send_discord_message_task,
    )
