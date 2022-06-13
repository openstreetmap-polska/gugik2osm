from typing import List, Optional, NamedTuple

from airflow.providers.postgres.hooks.postgres import PostgresHook


class StatusNames(NamedTuple):
    success: str
    fail: str


class ProcessNames(NamedTuple):
    full_update: str
    incremental_update: str


PROCESS_NAMES = ProcessNames(
    full_update="prg_full_update",
    incremental_update="prg_partial_update",
)

STATUSES = StatusNames("SUCCESS", "FAIL")


def get_data(sql: str, params: Optional[dict], postgres_conn_id: str = "postgres_default") -> List[tuple]:
    """Queries Postgres database and returns a list of tuples."""

    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    results = pg_hook.get_records(sql=sql, parameters=params) if params else pg_hook.get_records(sql=sql)

    return results


def full_prg_update_in_progress() -> bool:
    """Checks if full data update is in progress and returns True or False."""

    rows = get_data(
        sql="""
            SELECT in_progress
            FROM process_locks
            WHERE process_name = %(full_update_name)s
        """,
        params={
            "full_update_name": PROCESS_NAMES.full_update,
        },
    )
    updates_in_progress = [row[0] for row in rows]

    return any(updates_in_progress)


def any_prg_updates_in_progress() -> bool:
    """Checks if any PRG data updates are in progress and returns True or False."""

    rows = get_data(
        sql="""
            SELECT in_progress
            FROM process_locks
            WHERE process_name in (%(full_update_name)s, %(incremental_update_name)s)
        """,
        params={
            "full_update_name": PROCESS_NAMES.full_update,
            "incremental_update_name": PROCESS_NAMES.incremental_update,
        },
    )
    updates_in_progress = [row[0] for row in rows]

    return any(updates_in_progress)


def no_prg_updates_in_progress() -> bool:
    return not any_prg_updates_in_progress()


def set_process_status_running(process_name: str, postgres_conn_id: str = "postgres_default") -> None:
    """"""

    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    conn = pg_hook.get_conn()
    cur = conn.cursor()
    cur.execute(
        'UPDATE process_locks SET (in_progress, start_time, end_time) = (true, \'now\', null) ' +
        'WHERE process_name = %s',
        (process_name,)
    )
    print(cur.statusmessage)
    conn.commit()
    conn.close()


def set_process_status_finished(process_name: str, status: str, postgres_conn_id: str = "postgres_default") -> None:
    """"""

    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    conn = pg_hook.get_conn()
    cur = conn.cursor()
    cur.execute(
        'UPDATE process_locks SET (in_progress, end_time, last_status) = (false, \'now\', %s) ' +
        'WHERE process_name = %s',
        (status, process_name)
    )
    print(cur.statusmessage)
    conn.commit()
    conn.close()
