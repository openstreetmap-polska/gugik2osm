from datetime import datetime, timedelta
from typing import NamedTuple, Optional

from airflow.models.variable import Variable
from airflow.providers.discord.operators.discord_webhook import DiscordWebhookOperator


class DagAntispamStats(NamedTuple):
    number_of_messages: int
    last_message_ts: Optional[datetime]


AIRFLOW_VAR_ID = "antispam_stats"


def send_message(message: str, context: dict, http_conn_id: str = "discord_webhook") -> None:
    """Sends message to discord channel."""

    DiscordWebhookOperator(
        task_id="send_discord_message",
        http_conn_id=http_conn_id,
        webhook_endpoint="webhooks/{{ conn.discord_webhook.login }}/{{ conn.discord_webhook.password }}",
        message=message,
    ).execute(context)
    # use webhook_endpoint as template getting info from connection where token is a password
    # that way it won't show up in the logs


def send_dag_run_status(context: dict, antispam: bool = True) -> None:
    """Sends info about dag run status to discord channel.
    If antispam parameter is set to True repeating messages won't be sent.
    """

    dag_id = context["dag"].dag_id
    execution_date = context["execution_date"].isoformat()
    url = _dag_run_url(dag_id, execution_date)
    stats = _increment_dag_antispam_stats(dag_id)
    if antispam:
        if _should_send(stats):
            send_message(
                message=(
                        "DAG: {{ dag_run.dag_id }} finished with status: {{ dag_run.state }}, " +
                        "started: {{ dag_run.start_date }}, ended: {{ dag_run.end_date }}.\n" +
                        "There were a few messages sent already. To avoid spam new messages will be suppressed " +
                        "for an hour.\n" +
                        url
                ),
                context=context,
            )
        else:
            print("Suppressing message to avoid spam.")
    else:
        send_message(
            message=(
                "DAG: {{ dag_run.dag_id }} finished with status: {{ dag_run.state }}, " +
                "started: {{ dag_run.start_date }}, ended: {{ dag_run.end_date }}.\n" +
                url
            ),
            context=context,
        )


def _should_send(stats: DagAntispamStats) -> bool:
    if (
            stats.number_of_messages > 3
            and stats.last_message_ts
            and stats.last_message_ts - datetime.now() < timedelta(hours=1)
    ):
        return False
    else:
        return True


def _dag_run_url(dag_id: str, execution_date: str) -> str:
    return f"https://budynki.openstreetmap.org.pl/airflow/graph?dag_id={dag_id}&root=&execution_date={execution_date}"


def _check_dag_antispam_stats(dag_id: str) -> DagAntispamStats:
    results = Variable.get(
        key=AIRFLOW_VAR_ID,
        default_var=dict(),
        deserialize_json=True,
    ).get(dag_id)
    if results is None:
        return DagAntispamStats(number_of_messages=0, last_message_ts=None)
    else:
        return DagAntispamStats(
            number_of_messages=results["number_of_messages"],
            last_message_ts=datetime.fromisoformat(results["last_message_ts"]),
        )


def _increment_dag_antispam_stats(dag_id: str) -> DagAntispamStats:
    """"""

    current_stats = _check_dag_antispam_stats(dag_id)
    all_data = Variable.get(
        key=AIRFLOW_VAR_ID,
        default_var=dict(),
        deserialize_json=True,
    )
    new_number = current_stats.number_of_messages + 1
    new_ts = datetime.now()
    all_data[dag_id] = {"number_of_messages": new_number, "last_message_ts": new_ts.isoformat()}
    Variable.set(key=AIRFLOW_VAR_ID, value=all_data, serialize_json=True)

    return DagAntispamStats(number_of_messages=new_number, last_message_ts=new_ts)
