"""
Build AnyLog policies as dicts - publish the result separately (blockchain.async_publish_policy)

Policy builders:
    config  - node configuration (networking + startup scripts)           built locally
    node    - master, operator, query, publisher                           built by the node (`create policy ... with defaults`)
    cluster - cluster an operator belongs to                               built by the node (`create policy ... with defaults`)
    object  - object definition, referenced by a UNS policy                built locally
    uns     - unified namespace entry pointing to an object                built locally
    generic - any other policy type, content taken as-is                   built locally

`id`, `date` and `ledger` are added by the network when the policy is published - don't set them here.
"""
import ast
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, build_headers, exec_info
from src.core.support_logging import LevelMode, async_exec_logging

POLICY_REQUIRED_PARAMS = {
    "config":    ["company", "name"],
    "master":    ["company", "name"],
    "cluster":   ["company", "name"],
    "operator":  ["company", "name", "cluster"],
    "query":     ["company", "name"],
    "publisher": ["company", "name"],
    "object":    ["name"],
    "uns":       ["namespace", "object_id"],
}
NODE_TYPES = ["master", "operator", "query", "publisher"]
NODE_TYPE_ALIASES = {
    "standalone": "operator",
    "standalone-operator": "operator",
    "master-operator": "operator",
    "standalone-publisher": "publisher",
    "master-publisher": "publisher",
}


# ---------------------------------------------------------------------------------------------------------------------
# Support
# ---------------------------------------------------------------------------------------------------------------------
def _clean(params:dict)->dict:
    """Drop params with no value (None / empty string) - 0 and False are kept"""
    return {key: value for key, value in params.items() if value is not None and value != ""}


def _format_val(value, is_loc:bool=False):
    """
    Convert a value (ex. from .env) to its python type
    :args:
        value - value to convert
        is_loc:bool - value is a location
    :return:
        None / "" -> None
        location (tuple / list / "lat,lon") -> "lat, lon" string (format Grafana expects)
        "123" -> 123 | "true" / "false" -> True / False | python literal string -> its value
        anything else -> as-is
    """
    if value is None or value == "":
        return None
    if is_loc:
        if isinstance(value, (tuple, list)) and len(value) == 2:
            lat, lon = value
        else:
            lat, lon = str(value).strip("()[] ").split(",")
        return f"{float(lat):.4f}, {float(lon):.4f}"
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    if isinstance(value, str) and value.strip().lower() in ("true", "false"):
        return value.strip().lower() == "true"
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError, TypeError):
        return value


def _where_value(value)->str:
    """Quote a `create policy ... where` value that contains whitespace"""
    value = str(value)
    return f'"{value}"' if any(char.isspace() for char in value) and value[:1] not in ("'", '"') else value


async def _missing_params(policy_type:str, params:dict)->bool:
    """
    Check params against POLICY_REQUIRED_PARAMS[policy_type]
    :args:
        policy_type:str - policy type; types not in POLICY_REQUIRED_PARAMS have no required params
        params:dict - policy params
    :return:
        True if a required param is missing or empty (error logged / raised), otherwise False
    :raise:
        ValueError - missing params (when FORCE_EXCEPTION is on)
    """
    missing = [key for key in POLICY_REQUIRED_PARAMS.get(policy_type, [])
               if params.get(key) is None or (isinstance(params.get(key), str) and not params[key].strip())]
    if missing:
        await async_exec_logging(message=f"Missing critical param(s) for {policy_type} policy: "
                                         f"{', '.join(missing)} - policy not created",
                                 level=LevelMode.ERROR, exception_type=ValueError)
    return bool(missing)


async def _async_create_policy_defaults(anylog_conn:AnyLogRest, policy_type:str, where:dict,
                                        remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Have the node build a policy, filling in the defaults it knows (IPs, ports, ...)
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        policy_type:str - policy type
        where:dict - params sent with the command (None / empty values are skipped)
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
    :cmd:
        create policy {policy_type} with defaults where {key}={value} and ...
    :return:
        {policy_type: {...}} - policy built by the node
        str / None - COMMAND / HELP mode
    """
    where = _clean(where)
    command = f"create policy {policy_type} with defaults"
    if where:
        command += " where " + " and ".join(f"{key}={_where_value(value)}" for key, value in where.items())

    headers = build_headers(command=command, remote_destination=remote_destination)
    response = await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)
    if exec_mode != ExecMode.EXECUTE:
        return response
    return response.json()


# ---------------------------------------------------------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------------------------------------------------------
async def async_generic_policy(policy_type:str, exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|None:
    """
    Build a policy of any type, content taken as-is
    :args:
        policy_type:str - policy type (ex. sensor, table, mapping)
        exec_mode:ExecMode - Execution mode (only INFO changes behavior)
        kwargs - policy params (None / empty values are skipped)
    :return:
        {policy_type: {...}}
        None - INFO mode, or missing policy type when exceptions are disabled
    :raise:
        ValueError - missing policy type (when FORCE_EXCEPTION is on)
    :sample-output:
        {"sensor": {"name": "temp-1", "company": "Acme", "unit": "celsius"}}
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_generic_policy)
    if not policy_type:
        return await async_exec_logging(message="Missing policy type - policy not created",
                                        level=LevelMode.ERROR, exception_type=ValueError)

    return {policy_type: _clean(kwargs)}


def generic_policy(policy_type:str, exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|None:
    """Sync wrapper around `async_generic_policy` - see that function for details"""
    return asyncio.run(async_generic_policy(policy_type=policy_type, exec_mode=exec_mode, **kwargs))


# ---------------------------------------------------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------------------------------------------------
async def async_config_policy(name:str, company:str, node_type:str, version:str|None="",
                              ip:str="!ip", local_ip:str|None=None,
                              port:int|str="!anylog_server_port.int", tcp_threads:int|str|None="!tcp_threads.int",
                              tcp_bind:bool|str|None="!tcp_bind.bool",
                              rest_port:int|str="!anylog_rest_port.int", rest_threads:int|str|None="!rest_threads.int",
                              rest_timeout:int|str|None="!rest_timeout.int", rest_bind:bool|str|None="!rest_bind.bool",
                              broker_port:int|str|None="!anylog_broker_port.int",
                              broker_threads:int|str|None="!broker_threads.int",
                              broker_bind:bool|str|None="!broker_bind.bool",
                              script:list|None=None, exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|None:
    """
    Build a configuration policy - networking + the scripts a node runs at startup
    Every networking value defaults to an AnyLog variable, resolved by the node when the policy is applied
    :args:
        name:str - config policy name (ex. query-acme-configs)
        company:str - company name
        node_type:str - node type the config is for (master, operator, query, publisher, ...)
        version:str - config version
        ip:str - TCP IP (static: 24.16.32.123 | variable: '!ip')
        local_ip:str - internal IP, not set by default (static: 192.168.1.32 | variable: '!local_ip')
        port:int|str - TCP port (int: 32048 | variable: '!anylog_server_port.int')
        tcp_threads:int|str - TCP worker threads (int: 6 | variable: '!tcp_threads.int')
        tcp_bind:bool|str - TCP listens only on `ip` rather than all interfaces (bool | variable: '!tcp_bind.bool')
        rest_port:int|str - REST port (int: 32049 | variable: '!anylog_rest_port.int')
        rest_threads:int|str - REST worker threads (int: 6 | variable: '!rest_threads.int')
        rest_timeout:int|str - REST timeout in seconds (int: 30 | variable: '!rest_timeout.int')
        rest_bind:bool|str - REST listens only on `ip` (bool | variable: '!rest_bind.bool')
        broker_port:int|str - message broker port; None = no broker (int: 32050 | variable: '!anylog_broker_port.int')
        broker_threads:int|str - broker worker threads (int: 6 | variable: '!broker_threads.int')
        broker_bind:bool|str - broker listens only on `ip` (bool | variable: '!broker_bind.bool')
        script:list - AnyLog commands run when the config is applied; None / [] = no script
        exec_mode:ExecMode - Execution mode (only INFO changes behavior)
        kwargs - additional config params (None / empty values are skipped)
    :return:
        {"config": {...}}
        None - INFO mode, or missing params when exceptions are disabled
    :raise:
        ValueError - missing params (when FORCE_EXCEPTION is on)
    :sample-output:
        {"config": {"name": "query-acme-configs", "company": "Acme", "node_type": "query", "version": "",
                    "ip": "!ip", "port": "!anylog_server_port.int", ..., "script": [...]}}
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_config_policy)

    params = {"name": name, "company": company, "node_type": node_type}
    if await _missing_params(policy_type="config", params=params):
        return None

    config = {
        **params,
        "version": version or "",       # kept even when empty, as in existing config policies
        **_clean({
            "ip": ip,
            "local_ip": local_ip,
            "port": _format_val(port),
            "tcp_threads": _format_val(tcp_threads),
            "tcp_bind": _format_val(tcp_bind),
            "rest_port": _format_val(rest_port),
            "rest_threads": _format_val(rest_threads),
            "rest_timeout": _format_val(rest_timeout),
            "rest_bind": _format_val(rest_bind),
        }),
        **({"script": list(script)} if script else {}),
    }
    if broker_port not in (None, ""):
        config.update(_clean({
            "broker_port": _format_val(broker_port),
            "broker_threads": _format_val(broker_threads),
            "broker_bind": _format_val(broker_bind),
        }))
    config.update(_clean(kwargs))
    return {"config": config}


def config_policy(name:str, company:str, node_type:str, version:str|None="", ip:str="!ip", local_ip:str|None=None,
                  port:int|str="!anylog_server_port.int", tcp_threads:int|str|None="!tcp_threads.int",
                  tcp_bind:bool|str|None="!tcp_bind.bool", rest_port:int|str="!anylog_rest_port.int",
                  rest_threads:int|str|None="!rest_threads.int", rest_timeout:int|str|None="!rest_timeout.int",
                  rest_bind:bool|str|None="!rest_bind.bool", broker_port:int|str|None="!anylog_broker_port.int",
                  broker_threads:int|str|None="!broker_threads.int", broker_bind:bool|str|None="!broker_bind.bool",
                  script:list|None=None, exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|None:
    """Sync wrapper around `async_config_policy` - see that function for details"""
    return asyncio.run(async_config_policy(name=name, company=company, node_type=node_type, version=version, ip=ip,
                                           local_ip=local_ip, port=port, tcp_threads=tcp_threads, tcp_bind=tcp_bind,
                                           rest_port=rest_port, rest_threads=rest_threads, rest_timeout=rest_timeout,
                                           rest_bind=rest_bind, broker_port=broker_port, broker_threads=broker_threads,
                                           broker_bind=broker_bind, script=script, exec_mode=exec_mode, **kwargs))


# ---------------------------------------------------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------------------------------------------------
async def async_node_policy(anylog_conn:AnyLogRest, node_type:str, name:str, company:str, cluster:str|None=None,
                            ip:str|None=None, port:int|None=None, tcp_bind:bool|str=False,
                            rest_port:int|None=None, rest_bind:bool|str=False,
                            broker_port:int|None=None, broker_bind:bool|str=False,
                            remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE,
                            **kwargs)->dict|str|None:
    """
    Build a node policy (master, operator, query, publisher) - node defaults, overridden by the params given
    :args:
        anylog_conn:AnyLogRest - connection to the node the policy is for
        node_type:str - master, operator, query, publisher
            aliases: standalone / standalone-operator / master-operator -> operator,
                     standalone-publisher / master-publisher -> publisher
        name:str - node name
        company:str - company name
        cluster:str - cluster policy ID (required for operator)
        ip:str - IP to publish when TCP is bound (default: the node's internal / local IP)
        port:int - TCP port (default: node's)
        tcp_bind:bool|str - TCP bound to a single IP
        rest_port:int - REST port (default: node's)
        rest_bind:bool|str - REST bound to a single IP
        broker_port:int - message broker port
        broker_bind:bool|str - broker bound to a single IP
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
        kwargs - additional node params (None / empty values are skipped)
            hostname:str - node hostname
            main:bool|str - operator is the main member of its cluster
            loc:str - "latitude, longitude"
            country:str - country
            state:str - state
            city:str - city
    :binding:
        tcp_bind=False - policy keeps the node's ip (external) and internal ip
        tcp_bind=True  - policy publishes a single "ip" = ip param, or the node's internal / local IP
        rest_bind / broker_bind=True - adds "rest_ip" / "broker_ip" = the same IP
    :cmd:
        create policy {node_type} with defaults where name={name} and company={company} [and cluster={cluster}]
    :return:
        {node_type: {...}}
        str - COMMAND mode
        None - INFO / HELP mode, or invalid node type / missing params when exceptions are disabled
    :raise:
        ValueError - invalid node type or missing params (when FORCE_EXCEPTION is on)
    :sample-output:
        {"operator": {"name": "water-plant-operator1", "company": "Smart City", "hostname": "smart-city-operator1",
                      "ip": "172.105.60.50", "port": 32148, "rest_port": 32149, "broker_port": 32150,
                      "cluster": "64999c0d4d8762f67f6fe4f120c7a54b", "main": true,
                      "loc": "33.7490, -84.3880", "country": "US", "state": "GA", "city": "Atlanta"}}
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_node_policy)

    node_type = NODE_TYPE_ALIASES.get(node_type, node_type)
    if node_type not in NODE_TYPES:
        return await async_exec_logging(message=f"Invalid node type {node_type!r} - supported: "
                                                f"{', '.join(NODE_TYPES + list(NODE_TYPE_ALIASES))} - policy not created",
                                        level=LevelMode.ERROR, exception_type=ValueError)
    if await _missing_params(policy_type=node_type, params={"name": name, "company": company, "cluster": cluster}):
        return None

    policy = await _async_create_policy_defaults(anylog_conn=anylog_conn, policy_type=node_type,
                                                 where={"name": name, "company": company,
                                                        "cluster": cluster if node_type == "operator" else None},
                                                 remote_destination=remote_destination, exec_mode=exec_mode)
    if not isinstance(policy, dict):
        return policy       # COMMAND -> command string | HELP -> None
    node = policy.get(node_type) or {}

    tcp_bind = _format_val(tcp_bind) is True
    if not ip:
        ip = (node.get("internal_ip") or node.get("local_ip")) if tcp_bind else node.get("ip")
    if tcp_bind:
        node["ip"] = ip
        node.pop("internal_ip", None)
        node.pop("local_ip", None)

    if port:
        node["port"] = _format_val(port)
    if rest_port:
        node["rest_port"] = _format_val(rest_port)
    if _format_val(rest_bind) is True:
        node["rest_ip"] = ip
    if broker_port:
        node["broker_port"] = _format_val(broker_port)
        if _format_val(broker_bind) is True:
            node["broker_ip"] = ip

    for key, value in kwargs.items():
        if value is not None and value != "":
            node[key] = _format_val(value, is_loc=key.startswith("loc"))

    return {node_type: _clean(node)}


def node_policy(anylog_conn:AnyLogRest, node_type:str, name:str, company:str, cluster:str|None=None,
                ip:str|None=None, port:int|None=None, tcp_bind:bool|str=False, rest_port:int|None=None,
                rest_bind:bool|str=False, broker_port:int|None=None, broker_bind:bool|str=False,
                remote_destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|str|None:
    """Sync wrapper around `async_node_policy` - see that function for details"""
    return asyncio.run(async_node_policy(anylog_conn=anylog_conn, node_type=node_type, name=name, company=company,
                                         cluster=cluster, ip=ip, port=port, tcp_bind=tcp_bind, rest_port=rest_port,
                                         rest_bind=rest_bind, broker_port=broker_port, broker_bind=broker_bind,
                                         remote_destination=remote_destination, exec_mode=exec_mode, **kwargs))


# ---------------------------------------------------------------------------------------------------------------------
# Cluster
# ---------------------------------------------------------------------------------------------------------------------
async def async_cluster_policy(anylog_conn:AnyLogRest, name:str, company:str, remote_destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|str|None:
    """
    Build a cluster policy - operators reference it by ID ("cluster" in the operator policy)
    :args:
        anylog_conn:AnyLogRest - connection to AnyLog node
        name:str - cluster name
        company:str - company name
        remote_destination:str - send the request through the connected node to another agent
        exec_mode:ExecMode - Execution mode
        kwargs - additional cluster params, override the node's defaults (None / empty values are skipped)
    :cmd:
        create policy cluster with defaults where name={name} and company={company}
    :return:
        {"cluster": {...}}
        str - COMMAND mode
        None - INFO / HELP mode, or missing params when exceptions are disabled
    :raise:
        ValueError - missing params (when FORCE_EXCEPTION is on)
    :sample-output:
        {"cluster": {"company": "Smart City", "name": "water-plant", "status": "active"}}
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_cluster_policy)
    if await _missing_params(policy_type="cluster", params={"name": name, "company": company}):
        return None

    policy = await _async_create_policy_defaults(anylog_conn=anylog_conn, policy_type="cluster",
                                                 where={"name": name, "company": company},
                                                 remote_destination=remote_destination, exec_mode=exec_mode)
    if not isinstance(policy, dict):
        return policy       # COMMAND -> command string | HELP -> None

    return {"cluster": {**(policy.get("cluster") or {}), **_clean(kwargs)}}


def cluster_policy(anylog_conn:AnyLogRest, name:str, company:str, remote_destination:str|None=None,
                   exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|str|None:
    """Sync wrapper around `async_cluster_policy` - see that function for details"""
    return asyncio.run(async_cluster_policy(anylog_conn=anylog_conn, name=name, company=company,
                                            remote_destination=remote_destination, exec_mode=exec_mode, **kwargs))


# ---------------------------------------------------------------------------------------------------------------------
# Object / UNS
# ---------------------------------------------------------------------------------------------------------------------
async def async_object_policy(name:str, description:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE,
                              **kwargs)->dict|None:
    """
    Build an object policy - publish it first, then use its ID as `object_id` in the UNS policy
    :args:
        name:str - object name
        description:str - object description
        exec_mode:ExecMode - Execution mode (only INFO changes behavior)
        kwargs - additional object params (None / empty values are skipped)
    :return:
        {"object": {...}}
        None - INFO mode, or missing params when exceptions are disabled
    :raise:
        ValueError - missing params (when FORCE_EXCEPTION is on)
    :sample-output:
        {"object": {"name": "proveit", "description": "object for MQTT proveit"}}
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_object_policy)
    if await _missing_params(policy_type="object", params={"name": name}):
        return None

    return {"object": _clean({"name": name, "description": description, **kwargs})}


def object_policy(name:str, description:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|None:
    """Sync wrapper around `async_object_policy` - see that function for details"""
    return asyncio.run(async_object_policy(name=name, description=description, exec_mode=exec_mode, **kwargs))


async def async_uns_policy(name:str, object_id:str, namespace:str|None=None, source_node:str|None=None,
                           exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|None:
    """
    Build a UNS (unified namespace) policy that points to an object policy
    Read back together with: `blockchain get uns extend object bring.first`
    :args:
        name:str - UNS name
        object_id:str - ID of the published object policy
        namespace:str - namespace; defaults to name
        source_node:str - node providing the data (ex. bottle-factory2@173.255.212.88:32148)
        exec_mode:ExecMode - Execution mode (only INFO changes behavior)
        kwargs - additional UNS params (None / empty values are skipped)
    :return:
        {"uns": {...}}
        None - INFO mode, or missing params when exceptions are disabled
    :raise:
        ValueError - missing params (when FORCE_EXCEPTION is on)
    :sample-output:
        {"uns": {"name": "proveit", "namespace": "proveit", "source_node": "bottle-factory2@173.255.212.88:32148",
                 "object_id": "96b8c7d6f6e14e26939169a517f5229a"}}
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_uns_policy)

    namespace = namespace or name
    if await _missing_params(policy_type="uns", params={"namespace": namespace, "object_id": object_id}):
        return None

    return {"uns": _clean({"name": name, "namespace": namespace, "source_node": source_node,
                           "object_id": object_id, **kwargs})}


def uns_policy(name:str, object_id:str, namespace:str|None=None, source_node:str|None=None,
               exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|None:
    """Sync wrapper around `async_uns_policy` - see that function for details"""
    return asyncio.run(async_uns_policy(name=name, object_id=object_id, namespace=namespace,
                                        source_node=source_node, exec_mode=exec_mode, **kwargs))
