"""
Publish data into AnyLog - POST (through a message client topic) or PUT (directly into a table)
"""
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ANYLOG_AGENT, ExecMode, exec_info, serialize_data
from src.core.support_logging import LevelMode, async_exec_logging

PUT_MODES = {"streaming", "file"}


async def async_post(anylog_conn:AnyLogRest, topic:str, payload:dict|list|str, exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Publish data via POST - routed by the node's message client, mapped by `topic`
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        topic:str - topic configured on the node (`run msg client ... topic=(name=...)`)
        payload:dict|list|str - a row (dict), list of rows, or an already-serialized JSON string
        exec_mode:ExecMode - Execution mode
    :cmd:
        data (header) + topic={topic}; rows sent as the body
    :return:
        response from node, or None if the input was invalid / there was nothing to send
    :raise:
        ValueError - missing topic (when FORCE_EXCEPTION is on)
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_post)
    if not topic or not str(topic).strip():
        return await async_exec_logging(message="Missing topic for POST data - request not sent",
                                        level=LevelMode.WARNING, exception_type=ValueError)

    serialized = serialize_data(payload)
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


def post(anylog_conn:AnyLogRest, topic:str, payload:dict|list|str, exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_post` - see that function for details"""
    return asyncio.run(async_post(anylog_conn=anylog_conn, topic=topic, payload=payload, exec_mode=exec_mode))


async def async_put(anylog_conn:AnyLogRest, db_name:str, table_name:str, payload:dict|list|str,
                    mode:str="streaming", exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Publish data via PUT - written directly into db_name.table_name, no topic mapping needed
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        db_name:str - logical database name
        table_name:str - table name
        payload:dict|list|str - a row (dict), list of rows, or an already-serialized JSON string
        mode:str - "streaming" (buffered, default) or "file"
        exec_mode:ExecMode - Execution mode
    :cmd:
        PUT headers type=json, dbms={db_name}, table={table_name}, mode={mode}; rows sent as the body
    :return:
        response from node, or None if the input was invalid / there was nothing to send
    :raise:
        ValueError - invalid mode or missing db_name / table_name (when FORCE_EXCEPTION is on)
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_put)

    mode = str(mode).strip().lower() if mode else ""
    if mode not in PUT_MODES:
        return await async_exec_logging(message=f"Invalid PUT mode {mode!r} - supported: {sorted(PUT_MODES)}",
                                        level=LevelMode.WARNING, exception_type=ValueError)
    if not db_name or not table_name:
        return await async_exec_logging(message="PUT requires both db_name and table_name - request not sent",
                                        level=LevelMode.WARNING, exception_type=ValueError)

    serialized = serialize_data(payload)
    if serialized is None:          # serialization failure was already logged
        return None
    if serialized.strip() in ("", "[]", "{}"):
        return await async_exec_logging(message=f"Empty payload for {db_name}.{table_name} - request not sent",
                                        level=LevelMode.WARNING, raise_exception=False)

    headers = {
        "type": "json",
        "dbms": db_name.strip(),
        "table": table_name.strip(),
        "mode": mode,
        "Content-Type": "application/json",
    }
    return await anylog_conn.async_put(headers=headers, payload=serialized, exec_mode=exec_mode)


def put(anylog_conn:AnyLogRest, db_name:str, table_name:str, payload:dict|list|str, mode:str="streaming",
        exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_put` - see that function for details"""
    return asyncio.run(async_put(anylog_conn=anylog_conn, db_name=db_name, table_name=table_name, payload=payload,
                                 mode=mode, exec_mode=exec_mode))
