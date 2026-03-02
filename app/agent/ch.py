import os
import clickhouse_connect

def get_ch_client():
    host = os.environ["CLICKHOUSE_HOST"]  # e.g. http://...:8123 or https://...:8443
    user = os.environ.get("CLICKHOUSE_USER", "default")
    password = os.environ.get("CLICKHOUSE_PASSWORD", "")
    database = os.environ.get("CLICKHOUSE_DATABASE", "default")

    return clickhouse_connect.get_client(
        dsn=host,
        username=user,
        password=password,
        database=database,
    )

def run_select(sql: str, *, max_rows: int = 2000, max_time_s: int = 10):
    s = sql.strip().lower()
    if not s.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
    if ";" in sql:
        raise ValueError("Semicolons are not allowed.")

    client = get_ch_client()
    res = client.query(
        sql,
        settings={
            "max_execution_time": max_time_s,
            "max_result_rows": max_rows,
            "result_overflow_mode": "break",
        },
    )
    return res.column_names, res.result_rows
