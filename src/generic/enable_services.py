"""
Enable node services
"""
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, build_headers, exec_info
from src.generic.status import async_check_service_status


def _bool(value)->str:
    """Python bool -> AnyLog true / false"""
    return "true" if value else "false"


async def async_enable_operator(anylog_conn:AnyLogRest, operator_id:str, create_table:bool=True,
                                update_tsd_info:bool=True, compress_json:bool=True, compress_sql:bool=True,
                                archive_json:bool=True, archive_sql:bool=True, master_node:str="!ledger_conn",
                                operator_threads:int=6, remote_destination:str|None=None,
                                exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Start the operator service - skipped if it's already running
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        operator_id:str - ID of the node's operator policy
        create_table:bool - create tables automatically
        update_tsd_info:bool - update the tsd_info table
        compress_json:bool - compress JSON files
        compress_sql:bool - compress SQL files
        archive_json:bool - archive JSON files
        archive_sql:bool - archive SQL files
        master_node:str - master node TCP connection (ip:port | variable: '!ledger_conn')
        operator_threads:int - number of operator threads
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        run operator where create_table={create_table} and update_tsd_info={update_tsd_info} and
            compress_json={compress_json} and compress_sql={compress_sql} and archive_json={archive_json} and
            archive_sql={archive_sql} and master_node={master_node} and policy={operator_id} and threads={operator_threads}
    :return:
        response from node, or None if the operator is already running
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_enable_operator)
    if await async_check_service_status(anylog_conn=anylog_conn, service_name="operator",
                                        remote_destination=remote_destination, exec_mode=exec_mode) is True:
        return None

    command = (f"run operator where create_table={_bool(create_table)} and update_tsd_info={_bool(update_tsd_info)} "
               f"and compress_json={_bool(compress_json)} and compress_sql={_bool(compress_sql)} "
               f"and archive_json={_bool(archive_json)} and archive_sql={_bool(archive_sql)} "
               f"and master_node={master_node} and policy={operator_id} and threads={operator_threads}")
    headers = build_headers(command=command, remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)


def enable_operator(anylog_conn:AnyLogRest, operator_id:str, create_table:bool=True,
                    update_tsd_info:bool=True, compress_json:bool=True, compress_sql:bool=True,
                    archive_json:bool=True, archive_sql:bool=True, master_node:str="!ledger_conn",
                    operator_threads:int=6, remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_enable_operator` - see that function for details"""
    return asyncio.run(async_enable_operator(anylog_conn=anylog_conn, operator_id=operator_id,
                                             create_table=create_table, update_tsd_info=update_tsd_info,
                                             compress_json=compress_json, compress_sql=compress_sql,
                                             archive_json=archive_json, archive_sql=archive_sql,
                                             master_node=master_node, operator_threads=operator_threads,
                                             remote_destination=remote_destination, exec_mode=exec_mode))
