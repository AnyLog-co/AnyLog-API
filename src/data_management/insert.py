import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, exec_info
from src.core.support_logging import LevelMode, async_exec_logging

ANYLOG_AGENT = "AnyLog/1.23"
PUT_MODES = {"streaming", "file"}

async def async_post(anylog_conn:AnyLogRest, topic:str, payload:dict|list|str, exec_mode=ExecMode.EXECUTE):
    """
    Publish data into AnyLog via POST (goes through the node's message client, mapped by `topic`)
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        topic:str - publishing topic configured on the node (`run msg client ... topic=(name=...)`)
        payload - a row (dict), list of rows, or an already-serialized JSON string
        exec_mode:ExecMode - mode to execute request
    :return:
        response from node, or None if the input was invalid / nothing to send
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_post)
    if not topic or not str(topic).strip():
        return await async_exec_logging(message="Missing topic for POST data - request not sent",
                                        level=LevelMode.WARNING, exception_type=ValueError)

    serialized = await data_support.serialize_data(payload)
    if serialized is None:          # serialization failure was already logged
        return None
    if serialized.strip() in ("", "[]", "{}"):
        return await async_exec_logging(message=f"Empty payload for topic '{topic}' - request not sent",
                                        level=LevelMode.WARNING, raise_exception=False)

    headers = {
        "command": "data",
        "topic": str(topic).strip(),
        "AnyLog-Agent": ANYLOG_AGENT,
        "Content-Type": "application/json",
    }
    return await anylog_conn.async_post(headers=headers, payload=serialized, exec_mode=exec_mode)


def post(anylog_conn: AnyLogRest, topic: str, payload: dict | list | str, exec_mode=ExecMode.EXECUTE):
    """Sync wrapper around `async_post` - see that function for details."""
    if exec_mode == ExecMode.INFO:
        return exec_info(func=post)
    return asyncio.run(async_post(anylog_conn=anylog_conn, topic=topic, payload=payload, exec_mode=exec_mode))


async def async_put(anylog_conn: AnyLogRest, dbms: str, table: str, payload: dict | list | str,
                    mode: str = "streaming", exec_mode=ExecMode.EXECUTE):
    """
    Publish data into AnyLog via PUT (written directly into dbms.table, no topic mapping needed)
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        dbms:str - logical database
        table:str - table name
        payload - a row (dict), list of rows, or an already-serialized JSON string
        mode:str - "streaming" (buffered, default) or "file"
        exec_mode:ExecMode - mode to execute request
    :return:
        response from node, or None if the input was invalid / nothing to send
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_put)

    mode = str(mode).strip().lower() if mode else ""
    if mode not in PUT_MODES:
        return await async_exec_logging(message=f"Invalid PUT mode {mode!r} - supported: {sorted(PUT_MODES)}",
                                        level=LevelMode.WARNING, exception_type=ValueError)
    if not dbms or not table:
        return await async_exec_logging(message="PUT requires both dbms and table - request not sent",
                                        level=LevelMode.WARNING, exception_type=ValueError)

    serialized = await data_support.serialize_data(payload)
    if serialized is None:          # serialization failure was already logged
        return None
    if serialized.strip() in ("", "[]", "{}"):
        return await async_exec_logging(message=f"Empty payload for {dbms}.{table} - request not sent",
                                        level=LevelMode.WARNING, raise_exception=False)

    headers = {
        "type": "json",
        "dbms": dbms.strip(),
        "table": table.strip(),
        "mode": mode,
        "Content-Type": "application/json",
    }
    return await anylog_conn.async_put(headers=headers, payload=serialized, exec_mode=exec_mode)


def put(anylog_conn: AnyLogRest, dbms: str, table: str, payload: dict | list | str, mode: str = "streaming",
        exec_mode=ExecMode.EXECUTE):
    """Sync wrapper around `async_put` - see that function for details."""
    if exec_mode == ExecMode.INFO:
        return exec_info(func=put)
    return asyncio.run(async_put(anylog_conn=anylog_conn, dbms=dbms, table=table, payload=payload, mode=mode,
                                 exec_mode=exec_mode))
