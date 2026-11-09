"""
Blockchain (metadata) - ledger database, querying policies, publishing policies and syncing with the master
"""
import asyncio
import json

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, build_headers, exec_info, format_conditions
from src.data_management.dbms import async_connect_dbms, async_create_table, async_is_database
from src.generic.status import async_check_service_status

BRING_MODES = (None, "first", "last", "unique")
NODE_POLICY_TYPES = ["master", "operator", "query", "publisher"]
NODE_POLICY_KEYS = ["name", "company", "ip", "port"]     # keys that identify a node policy when checking for duplicates


# ---------------------------------------------------------------------------------------------------------------------
# Ledger database
# ---------------------------------------------------------------------------------------------------------------------
async def async_connect_blockchain(anylog_conn:AnyLogRest, db_type:str, db_ip:str|None=None, db_port:int|None=None,
                                   db_user:str|None=None, db_password:str|None=None,
                                   remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Connect the node to the `blockchain` logical database (master nodes) - skipped if it's already connected
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        db_type:str - physical database type (psql, mongo, sqlite)
        db_ip:str - database IP
        db_port:int - database port
        db_user:str - database user
        db_password:str - database password
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        connect dbms blockchain where type={db_type} [and ip=...] [and port=...] [and user=...] [and password=...]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: connect dbms blockchain where type=sqlite" \
          -H "AnyLog-Agent: AnyLog/1.23"
    :return:
        response from node, or None if already connected
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_connect_blockchain)

    if exec_mode == ExecMode.EXECUTE and await async_is_database(anylog_conn=anylog_conn, db_name="blockchain",
                                                                 remote_destination=remote_destination,
                                                                 exec_mode=exec_mode):
        return None

    return await async_connect_dbms(anylog_conn=anylog_conn, db_name="blockchain", db_type=db_type, db_ip=db_ip,
                                    db_port=db_port, db_user=db_user, db_password=db_password, in_memory=False,
                                    remote_destination=remote_destination, exec_mode=exec_mode)


def connect_blockchain(anylog_conn:AnyLogRest, db_type:str, db_ip:str|None=None, db_port:int|None=None,
                       db_user:str|None=None, db_password:str|None=None, remote_destination:str|None=None,
                       exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_connect_blockchain` - see that function for details"""
    return asyncio.run(async_connect_blockchain(anylog_conn=anylog_conn, db_type=db_type, db_ip=db_ip,
                                                db_port=db_port, db_user=db_user, db_password=db_password,
                                                remote_destination=remote_destination, exec_mode=exec_mode))


async def async_create_table_ledger(anylog_conn:AnyLogRest, remote_destination:str|None=None,
                                    exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Create the `ledger` table in the `blockchain` database - skipped if it already exists
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        create table ledger where dbms=blockchain
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: create table ledger where dbms=blockchain" \
          -H "AnyLog-Agent: AnyLog/1.23"
    :return:
        response from node, or None if the table already exists
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_create_table_ledger)

    return await async_create_table(anylog_conn=anylog_conn, db_name="blockchain", table_name="ledger",
                                    remote_destination=remote_destination, exec_mode=exec_mode)


def create_table_ledger(anylog_conn:AnyLogRest, remote_destination:str|None=None,
                        exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_create_table_ledger` - see that function for details"""
    return asyncio.run(async_create_table_ledger(anylog_conn=anylog_conn, remote_destination=remote_destination,
                                                 exec_mode=exec_mode))


# ---------------------------------------------------------------------------------------------------------------------
# Get policies
# ---------------------------------------------------------------------------------------------------------------------
def _bring_keys(bring:str|list|tuple)->list[str]:
    """'name, id' / ['name', 'id'] -> ['name', 'id']"""
    if isinstance(bring, str):
        bring = bring.split(",")
    return [key.strip() for key in bring if key and key.strip()]


def _build_bring_clause(policy_type:str, bring:str|list|tuple, key_separator:str=":")->str:
    """
    Build the AnyLog bring clause
    :args:
        policy_type:str - policy type ('*' or several types -> [*])
        bring:str|list|tuple - key(s) to bring, or a raw AnyLog clause (passed through as-is)
        key_separator:str - separator between keys of the same policy
    :return:
        'name,id'                 -> [cluster][name] ":" [cluster][id]
        '[*][ip] ":" [*][port]'   -> as-is
    """
    if isinstance(bring, str) and "[" in bring:
        return bring
    bring_type = policy_type if policy_type and policy_type != "*" and "," not in policy_type else "*"
    return f' "{key_separator}" '.join(f"[{bring_type}][{key}]" for key in _bring_keys(bring))


def extract_bring(policies:list|dict|str, bring:str|list|tuple, bring_mode:str|None=None, flatten:bool=True):
    """
    Local (python-side) equivalent of AnyLog's `bring`
    :args:
        policies:list|dict|str - a policy, a list of policies, or the JSON string of either
        bring:str|list|tuple - key(s) to keep ('name,id' or ['name', 'id'])
        bring_mode:str - None (all) | 'first' | 'last' | 'unique'
        flatten:bool - for a single bring key, return its values instead of {policy_type: {key: value}}
    :return:
        bring_mode first / last -> a single item (or None)
        otherwise               -> a list
    :raise:
        ValueError - invalid bring_mode
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
        results = [next(iter(result.values()))[keys[0]] for result in results]

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
                               bring_mode:str|None=None, local_bring:bool=False, flatten:bool=True,
                               separator:str|None=None, remote_destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Get policies from the blockchain, with an optional bring - done either by AnyLog or locally
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        policy_type:str|list|tuple - policy type(s) to get ('*' for all)
        where:str|list|dict - where condition (str used as-is; list / dict formatted via format_conditions)
        bring:str|list|tuple - key(s) to bring ('name,id', ['name', 'id'], or a raw AnyLog clause '[*][ip] ":" [*][port]')
        bring_mode:str - None (all) | 'first' | 'last' | 'unique'
        local_bring:bool
            False - AnyLog executes the bring - returns AnyLog's text
            True  - get the full policies, then extract locally - returns python objects
        flatten:bool - (local bring only) for a single bring key, return values instead of {policy_type: {key: value}}
        separator:str - (AnyLog bring only) separator between policies, ex. ','
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        blockchain get {policy_type} [where {where}] [bring[.{bring_mode}] {bring}] [separator={separator}]
    :curl:
        curl -X POST http://[IP:Port] \
          -H "Content-Type: application/json" \
          -d '{"command": "blockchain get operator where name=\"XYZ\" and company=\"ABC\"", "AnyLog-Agent": "AnyLog/1.23"}'
    :return:
        policies (JSON), AnyLog's bring text, or the locally extracted bring
    :raise:
        ValueError - invalid bring_mode
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_blockchain_get)
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

    headers = build_headers(command=command, remote_destination=remote_destination)
    result = await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)
    if exec_mode != ExecMode.EXECUTE:
        return result

    if bring and local_bring:
        return extract_bring(policies=result, bring=bring, bring_mode=bring_mode, flatten=flatten)
    return result


def blockchain_get(anylog_conn:AnyLogRest, policy_type:str|list|tuple="*", where:str|list|dict|None=None,
                   bring:str|list|tuple|None=None, bring_mode:str|None=None, local_bring:bool=False,
                   flatten:bool=True, separator:str|None=None, remote_destination:str|None=None,
                   exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_blockchain_get` - see that function for details"""
    return asyncio.run(async_blockchain_get(anylog_conn=anylog_conn, policy_type=policy_type, where=where,
                                            bring=bring, bring_mode=bring_mode, local_bring=local_bring,
                                            flatten=flatten, separator=separator,
                                            remote_destination=remote_destination, exec_mode=exec_mode))


# ---------------------------------------------------------------------------------------------------------------------
# Publish policies
# ---------------------------------------------------------------------------------------------------------------------
async def async_publish_policy(anylog_conn:AnyLogRest, policy:dict, remote_destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Publish a policy to the blockchain - skipped if a matching policy already exists
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        policy:dict - policy to publish ({policy_type: {...}})
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :params:
        where_conditions:list - how an existing copy is found
            node policies - name, company, ip, port
            other policies - every simple (non list / dict) value
    :cmd:
        blockchain get {policy_type} where ...
        blockchain insert where policy=!new_policy and local=true and master=!ledger_conn
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: blockchain insert where policy=!new_policy and local=true and master=!ledger_conn" \
          -H "AnyLog-Agent: AnyLog/1.23" \
          -d '<new_policy={"cluster": {"name": "water-plant", "company": "Smart City", "status": "active"}}>'
    :return:
        response from node, or None if the policy already exists
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_publish_policy)

    policy_type = next(iter(policy))
    params = policy[policy_type]
    keys = NODE_POLICY_KEYS if policy_type in NODE_POLICY_TYPES else list(params)
    where_conditions = [f"{key}={params[key]}" for key in keys
                        if params.get(key) not in (None, "") and not isinstance(params[key], (dict, list))]

    existing_policy = await async_blockchain_get(anylog_conn, policy_type=policy_type, where=where_conditions,
                                                 remote_destination=remote_destination, exec_mode=exec_mode)
    if exec_mode == ExecMode.EXECUTE and existing_policy:
        return None

    headers = build_headers(command="blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
                            remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, payload=f"<new_policy={json.dumps(policy)}>",
                                        exec_mode=exec_mode)


def publish_policy(anylog_conn:AnyLogRest, policy:dict, remote_destination:str|None=None,
                   exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_publish_policy` - see that function for details"""
    return asyncio.run(async_publish_policy(anylog_conn=anylog_conn, policy=policy,
                                            remote_destination=remote_destination, exec_mode=exec_mode))


# ---------------------------------------------------------------------------------------------------------------------
# Blockchain sync
# ---------------------------------------------------------------------------------------------------------------------
async def async_blockchain_sync_master(anylog_conn:AnyLogRest, sync_time:str="30 seconds", source:str="master",
                                       dest:str="file", ledger_conn:str="!ledger_conn",
                                       remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    r"""
    Start syncing the node's copy of the metadata with the master - skipped if the sync is already running
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        sync_time:str - how often to sync (ex. "30 seconds")
        source:str - where the metadata comes from (master)
        dest:str - where the node keeps its copy (file, dbms)
        ledger_conn:str - master node TCP connection (ip:port | variable: '!ledger_conn')
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        run blockchain sync where source={source} and time={sync_time} and dest={dest} and connection={ledger_conn}
    :curl:
        curl -X POST http://[IP:Port] \
          -H "command: run blockchain sync where source=master and time=30 seconds and dest=file and connection=127.0.0.1:32048" \
          -H "AnyLog-Agent: AnyLog/1.23"
    :return:
        response from node, or None if the sync is already running
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_blockchain_sync_master)

    if exec_mode == ExecMode.EXECUTE and await async_check_service_status(anylog_conn=anylog_conn,
                                                                          service_name="blockchain",
                                                                          remote_destination=remote_destination,
                                                                          exec_mode=exec_mode) is True:
        return None

    command = f"run blockchain sync where source={source} and time={sync_time} and dest={dest} and connection={ledger_conn}"
    headers = build_headers(command=command, remote_destination=remote_destination)
    return await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)


def blockchain_sync_master(anylog_conn:AnyLogRest, sync_time:str="30 seconds", source:str="master", dest:str="file",
                           ledger_conn:str="!ledger_conn", remote_destination:str|None=None,
                           exec_mode:ExecMode=ExecMode.EXECUTE):
    """Sync wrapper around `async_blockchain_sync_master` - see that function for details"""
    return asyncio.run(async_blockchain_sync_master(anylog_conn=anylog_conn, sync_time=sync_time, source=source,
                                                    dest=dest, ledger_conn=ledger_conn,
                                                    remote_destination=remote_destination, exec_mode=exec_mode))
