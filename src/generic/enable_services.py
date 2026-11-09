import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.generic.status import async_check_service_status
from src.core.support import ExecMode, exec_info

async def async_enable_operator(anylog_conn:AnyLogRest, operator_id:str, create_table:bool=True,
                                update_tsd_info:bool=True, compress_json:bool=True, compress_sql:bool=True,
                                archive_json:bool=True, archive_sql:bool=True, master_node="!ledger_conn",
                                operator_threads:int=6, destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):

    """
    Enable `run operator` service
    :args:
        anylog_conn:AnyLogREST - connection to AnyLog
        operator_id:str - operator ID
        create_table:bool - automatically create table
        update_tsd_info:bool - update tsd info table
        compress_json:bool - compress JSON files
        compress_sql:bool - compress SQL files
        archive_json:bool - archive JSON file(s)
        archive_sql:bool - archive SQL file(s)
        master_node:str -  Master node
        operator_threads:int - number of threads to use
        destination:str - remote destination to send to
        exec_mode:ExecMode - execution mode
    :return:
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_enable_operator)
        return None
    elif await async_check_service_status(anylog_conn=anylog_conn, service_name="operator", remote_destination=destination,
                                          exec_mode=exec_mode):
        return None

    headers = {
        "command": f"run operator where " +
                   f"create_table={'true' if create_table else 'false'} and " +
                   f"update_tsd_info={'true' if update_tsd_info else 'false'} and " +
                   f"compress_json={'true' if compress_json else 'false'} and " +
                   f"compress_sql={'true' if compress_sql else 'false'} and " +
                   f"archive_json={'true' if archive_json else 'false'} and " +
                   f"archive_sql={'true' if archive_sql else 'false'} and " +
                   f"master_node={master_node} and policy={operator_id} and threads={operator_threads}",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": destination} if destination else {})
    }

    return await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)


def enable_operator(anylog_conn:AnyLogRest, operator_id:str, create_table:bool=True,
                    update_tsd_info:bool=True, compress_json:bool=True, compress_sql:bool=True,
                    archive_json:bool=True, archive_sql:bool=True, master_node="!ledger_conn",
                    operator_threads:int=6, destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):

    asyncio.run(async_enable_operator(anylog_conn=anylog_conn, operator_id=operator_id, create_table=create_table,
                                      update_tsd_info=update_tsd_info, compress_json=compress_json,
                                      compress_sql=compress_sql, archive_json=archive_json, archive_sql=archive_sql,
                                      master_node=master_node, operator_threads=operator_threads, destination=destination,
                                      exec_mode=exec_mode))