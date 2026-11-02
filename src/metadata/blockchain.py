import asyncio
from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, exec_info, LevelMode
from src.data_management.dbms import async_connect_dbms, async_is_database, async_create_table


async def async_connect_blockchain(anylog_conn:AnyLogRest, db_type:str, db_ip:str|None=None,
                                   db_port:int|None=None, db_user:str|None=None, db_password:str|None=None,
                                   destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Connect to `blockchain` logical database
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        db_name:str - logical database name
        db_type:str - logical database type
        db_ip:str - db IP
        db_port:int - db port
        db_user:str - db user
        db_password:str - db password
        in_memory:bool - whether to run in memory mode for SQLite or unlogged for PSQL
        exec_mode:ExecMode - Execution mode
    """
    is_blockchain = None
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_connect_blockchain)
        return None

    if exec_mode == ExecMode.EXECUTE:
        is_blockchain = await async_is_database(anylog_conn=anylog_conn, db_name="blockchain",
                                                remote_destination=destination, exec_mode=exec_mode)

    if not is_blockchain:
        return await async_connect_dbms(anylog_conn=anylog_conn, db_name="blockchain", db_type=db_type, db_ip=db_ip,
                                        db_port=db_port, db_user=db_user, db_password=db_password, in_memory=False,
                                        destination=destination, exec_mode=exec_mode)

    return None



async def async_create_table_ledger(anylog_conn:AnyLogRest, destination:str|None=None,
                                    exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Create logical table `ledger` against blockchain database
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        destination:str - remote destination to send request
        exec_mode:ExecMode - Execution mode
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_create_table_ledger)
        return None

    return await async_create_table(anylog_conn=anylog_conn, db_name="blockchain", table_name="ledger", destination=destination,
                                    exec_mode=exec_mode)



def connect_blockchain(anylog_conn:AnyLogRest, db_type:str, db_ip:str|None=None, db_port:int|None=None,
                       db_user:str|None=None, db_password:str|None=None, destination:str|None=None,
                       exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Connect to `blockchain` logical database
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        db_name:str - logical database name
        db_type:str - logical database type
        db_ip:str - db IP
        db_port:int - db port
        db_user:str - db user
        db_password:str - db password
        in_memory:bool - whether to run in memory mode for SQLite or unlogged for PSQL
        exec_mode:ExecMode - Execution mode
    """

    return asyncio.run(async_connect_blockchain(anylog_conn=anylog_conn, db_type=db_type, db_ip=db_ip, db_port=db_port,
                                                db_user=db_user, db_password=db_password, destination=destination,
                                                exec_mode=exec_mode))


def create_table_ledger(anylog_conn:AnyLogRest, destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    return asyncio.run(async_create_table_ledger(anylog_conn=anylog_conn, destination=destination, exec_mode=exec_mode))