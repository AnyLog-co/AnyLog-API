import asyncio
import json

from certifi import where

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, exec_info, LevelMode, format_conditions
from src.data_management.dbms import async_connect_dbms, async_is_database, async_create_table
from src.generic.status import async_check_service_status

BRING_MODES = (None, "first", "last", "unique")


# 1a connect to blockchain logical database (if master)
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

# 1b create ledger table
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


def create_table_ledger(anylog_conn:AnyLogRest, destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    return asyncio.run(async_create_table_ledger(anylog_conn=anylog_conn, destination=destination, exec_mode=exec_mode))

# 2 check if policy exists
def _bring_keys(bring: str | list | tuple) -> list[str]:
    """'name, id' / ['name', 'id'] -> ['name', 'id']"""
    if isinstance(bring, str):
        bring = bring.split(",")
    return [key.strip() for key in bring if key and key.strip()]


def _build_bring_clause(policy_type: str, bring: str | list | tuple, key_separator: str = ":") -> str:
    """
    Build the AnyLog bring clause
        'name,id'                 -> [cluster][name] ":" [cluster][id]
        '[*][ip] ":" [*][port]'   -> passed through as-is (already AnyLog syntax)
    """
    if isinstance(bring, str) and "[" in bring:
        return bring
    ptype = policy_type if policy_type and policy_type != "*" and "," not in policy_type else "*"
    return f' "{key_separator}" '.join(f"[{ptype}][{key}]" for key in _bring_keys(bring))


def extract_bring(policies: list | dict | str, bring: str | list | tuple, bring_mode: str | None = None,
                  flatten: bool = True):
    """
    Local (python-side) equivalent of AnyLog's `bring`
    :args:
        policies - a policy, a list of policies, or the JSON string of either
        bring - key(s) to keep ('name,id' or ['name', 'id'])
        bring_mode - None (all) | 'first' | 'last' | 'unique'
        flatten - when a single key is brought, return its values instead of {policy_type: {key: value}}
    :return:
        bring_mode first / last -> a single item (or None)
        otherwise               -> a list
    """
    if bring_mode not in BRING_MODES:
        raise ValueError(f"Invalid bring_mode {bring_mode!r} - expected one of {BRING_MODES}")

    if isinstance(policies, str):
        try:
            policies = json.loads(policies)
        except json.JSONDecodeError:
            return None
    if isinstance(policies, dict):
        policies = [policies]
    if not isinstance(policies, list):
        return None

    keys = _bring_keys(bring)
    results = []
    for policy in policies:
        if not isinstance(policy, dict) or not policy:
            continue
        policy_type = next(iter(policy))
        body = policy.get(policy_type) or {}
        content = {key: body[key] for key in keys if key in body}
        if content:
            results.append({policy_type: content})

    if flatten and len(keys) == 1:
        results = [next(iter(r.values()))[keys[0]] for r in results]

    if bring_mode == "unique":
        seen, unique = set(), []
        for item in results:
            marker = json.dumps(item, sort_keys=True, default=str)
            if marker not in seen:
                seen.add(marker)
                unique.append(item)
        results = unique
    elif bring_mode == "first":
        return results[0] if results else None
    elif bring_mode == "last":
        return results[-1] if results else None

    return results


async def async_blockchain_get(anylog_conn:AnyLogRest, policy_type:str|list|tuple="*",
                               where:str|list|dict|None=None, bring:str|list|tuple|None=None,
                               bring_mode:str|None=None, local_bring:bool=False, flatten:bool =True,
                               separator:str|None=None, destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Execute `blockchain get` with an optional bring - done either by AnyLog or locally
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog
        policy_type:str|list|tuple - policy type(s) to get ('*' for all)
        where:str|list|dict - WHERE condition (str used as-is, list / dict formatted via format_conditions)
        bring:str|list|tuple - key(s) to bring ('name,id', ['name', 'id'], or a raw AnyLog clause '[*][ip] ":" [*][port]')
        bring_mode:str - None (all) | 'first' | 'last' | 'unique'
        local_bring:bool
            False - AnyLog executes `blockchain get ... bring[.mode] ...` (option 1) - returns AnyLog's text
            True  - get the full policies, then extract locally (option 2) - returns python objects
        flatten:bool - (local only) for a single bring key, return values instead of {policy_type: {key: value}}
        separator:str - (AnyLog only) separator between policies, e.g. ','
        destination:str - remote node to query
        exec_mode:ExecMode - Execution mode
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_blockchain_get)
        return None

    if bring_mode not in BRING_MODES:
        raise ValueError(f"Invalid bring_mode {bring_mode!r} - expected one of {BRING_MODES}")

    if isinstance(policy_type, (list, tuple)):
        policy_type = ",".join(policy_type)
    command = f"blockchain get {'(' + policy_type + ')' if ',' in policy_type else policy_type}"

    if where:
        if not isinstance(where, str):
            where = " and ".join(format_conditions(where))
        command += f" where {where}"

    if bring and not local_bring:
        command += f" bring{'.' + bring_mode if bring_mode else ''} {_build_bring_clause(policy_type, bring)}"
        if separator:
            command += f" separator={separator}"

    payload = {
        "command": command,
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": destination} if destination else {})
    }
    print(command)
    response = await anylog_conn.async_post(headers={"Content-Type": "application/json"}, payload=payload,
                                            exec_mode=exec_mode)
    if exec_mode != ExecMode.EXECUTE:
        return response

    try:
        result = response.json()
    except Exception:
        result = response.text

    if bring and local_bring:
        return extract_bring(policies=result, bring=bring, bring_mode=bring_mode, flatten=flatten)
    return result


def blockchain_get(anylog_conn: AnyLogRest, policy_type: str | list | tuple = "*",
                   where: str | list | dict | None = None, bring: str | list | tuple | None = None,
                   bring_mode: str | None = None, local_bring: bool = False, flatten: bool = True,
                   separator: str | None = None, destination: str | None = None,
                   exec_mode: ExecMode = ExecMode.EXECUTE):
    """Sync wrapper around `async_blockchain_get`"""
    return asyncio.run(async_blockchain_get(anylog_conn=anylog_conn, policy_type=policy_type, where=where,
                                            bring=bring, bring_mode=bring_mode, local_bring=local_bring,
                                            flatten=flatten, separator=separator, destination=destination,
                                            exec_mode=exec_mode))

# Publish policy
async def async_publish_policy(anylog_conn:AnyLogRest, policy:dict, destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE):
    policy_type = list(policy)[0]
    where_conditions = [
        f'name={policy.get(policy_type).get("name")}',
        f'company={policy.get(policy_type).get("company")}',
        f'ip={policy.get(policy_type).get("ip")}',
        f'port={policy.get(policy_type).get("port")}'
    ] if policy_type in ["master", "operator", "query", "publisher"] else [f"{key}={value}" for key, value in policy.get(policy_type).items()]


    is_policy  = await async_blockchain_get(anylog_conn, policy_type=policy_type,
                                            where=where_conditions,
                                            bring=None, destination=destination, exec_mode=exec_mode)
    if not is_policy:
        headers = {
            "command": "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
            "AnyLog-Agent": "AnyLog/1.23"
        }

        await anylog_conn.async_post(headers=headers, payload=f"<new_policy={json.dumps(policy)}>", exec_mode=exec_mode)


def publish_policy(anylog_conn:AnyLogRest, policy:dict, destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE):
    return asyncio.run(async_publish_policy(anylog_conn=anylog_conn, policy=policy, destination=destination,
                                      exec_mode=exec_mode))

# connect to the blockchain
async def async_lockchain_sync_master(anylog_conn:AnyLogRest, sync_time:str="30 seconds", source:str="master",
                                           dest:str="file", ledger_conn:str="!ledger_conn", destination:str|None=None,
                                           exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Define `run blockchain sync`
    :args:
        anylog_conn:AnyLogREST - connection to AnyLog
        sync_time:str - how often blockchain sync
        source:str - where the data is coming from
        dest:str - where the data goes
        ledger_conn:str - TCP connection for master node
        destination:str - Remote destination
        exec_mode:ExecMode - execution format
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_blockchain_get)
        return None

    if exec_mode == ExecMode.EXECUTE:
        response = await async_check_service_status(anylog_conn=anylog_conn, service_name="blockchain", exec_mode=exec_mode)
        if exec_mode == ExecMode.EXECUTE and response:
            return None

    headers = {
        "command": f"run blockchain sync where source={source} and time={sync_time} and dest={dest} and connection={ledger_conn}",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": destination} if destination else {})     # line 153 - the crash
    }

    return await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode )

def blockchain_sync_master(anylog_conn:AnyLogRest, sync_time:str="30 seconds", source:str="master",
                           dest:str="file", ledger_conn:str="!ledger_conn", destination:str|None=None,
                           exec_mode:ExecMode=ExecMode.EXECUTE):

    return asyncio.run(async_lockchain_sync_master(anylog_conn=anylog_conn, sync_time=sync_time, source=source,
                                                        dest=dest, ledger_conn=ledger_conn, destination=destination,
                                                        exec_mode=exec_mode))


