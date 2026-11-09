"""
Build AnyLog policies as dicts - nothing is sent to the AnyLog node.
Publish the result separately (ex. blockchain.async_publish_policy).

Policy builders:
    config  - node configuration (networking + startup scripts)
    node    - master, operator, query, publisher
    cluster - cluster an operator belongs to
    object  - object definition, referenced by a UNS policy
    uns     - unified namespace entry pointing to an object
    generic - any other policy type, content taken as-is

`id`, `date` and `ledger` are added by the network when the policy is published - don't set them here.
"""
import ast
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, exec_info
from src.core.support_logging import LevelMode, async_exec_logging


POLICY_REQUIRED_PARAMS = {
    "config": ["company", "name"],
    "master":    ["company", "name"],
    "cluster": ["company", "name"],
    "operator":  ["company", "name", "cluster"],
    "query":     ["company", "name"],
    "publisher": ["company", "name"],
    "object": ["name"],
    "uns": ["namespace", "object"]
}


# ---------------------------------------------------------------------------------------------------------------------
# Support
# ---------------------------------------------------------------------------------------------------------------------
def _clean(params:dict)->dict:
    """Drop params with no value (None / empty string) - 0 and False are kept"""
    return {key: value for key, value in params.items() if value is not None and value != ""}


def _format_val(value, is_loc:bool=False):
    """
    convert value to int or boolean
    """

    if value is None or value == "":
        return None
    elif is_loc:
        """Location -> "lat, lon" string (format Grafana expects); accepts tuple / list / string"""
        if isinstance(value, (tuple, list)) and len(value) == 2:
            lat, lon = value
        else:
            lat, lon = str(value).strip("()[] ").split(",")
        return f"{float(lat):.4f}, {float(lon):.4f}"
    elif isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    elif isinstance(value, str) and value.strip().lower() in ("true", "false"):
        return True if value.strip().lower() == "true" else False
    try:
        return ast.literal_eval(value)
    except Exception as error:
        return  value

async def _missing_params(policy_type:str, params:dict)->bool:
    """
    Check params against POLICY_REQUIRED_PARAMS[policy_type]
    :args:
        policy_type:str - policy type; types not in POLICY_REQUIRED_PARAMS have no required params
        params:dict - policy params
    :return:
        True if a required param is missing or empty (error logged / raised), otherwise False
    """
    missing = [key for key in POLICY_REQUIRED_PARAMS.get(policy_type, [])
               if params.get(key) is None or (isinstance(params.get(key), str) and not params[key].strip())]
    if missing:
        await async_exec_logging(message=f"Missing critical param(s) for {policy_type} policy: "
                                         f"{', '.join(missing)} - policy not created",
                                 level=LevelMode.ERROR, exception_type=ValueError)
    return bool(missing)

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
    :sample-output:
        {"sensor": {"name": "temp-1", "company": "Acme", "unit": "celsius"}}
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_generic_policy)
        return None
    if not policy_type:
        return await async_exec_logging(message="Missing policy type - policy not created",
                                        level=LevelMode.ERROR, exception_type=ValueError)

    return {policy_type: _clean(kwargs)}


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
        script:list - AnyLog commands run when the config is applied; None = DEFAULT_CONFIG_SCRIPT, [] = no script
        exec_mode:ExecMode - Execution mode (only INFO changes behavior)
        kwargs - additional config params (None / empty values are skipped)
    :return:
        {"config": {...}}
        None - INFO mode, or missing params when exceptions are disabled
    :sample-output:
        {"config": {"name": "query-acme-configs", "company": "Acme", "node_type": "query", "version": "",
                    "ip": "!ip", "port": "!anylog_server_port.int", ..., "script": [...]}}
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_config_policy)
        return None

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
        **{{"script": script} if script else {}}
    }
    if broker_port not in (None, ""):
        config.update(_clean({
            "broker_port": _format_val(broker_port),
            "broker_threads": _format_val(broker_threads),
            "broker_bind": _format_val(broker_bind),
        }))
    config.update(_clean(kwargs))
    return {"config": config}


# ---------------------------------------------------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------------------------------------------------
async def _async_create_policy_defaults(anylog_conn:AnyLogRest, policy_type:str, name:str, company:str,
                                       cluster_id:str|None=None, destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE):
    """
    Using the minimal requirements, this generates blockchain metadata policy for node types. Automatically integrating the
    built-in / already used IPs + ports for the node
    :args:
        anylog_conn:AnyLogREST - connection to AnyLog
        policy_type:str - Node policy type
        name:str - node name
        company:str - company name
        cluster_id:Str - for operator node the associated cluster ID
    :return:
        generate node policy
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=_async_create_policy_defaults)
        return None

    headers = {
        "command": f"create policy {policy_type} with defaults where name={name} and company={company} {f'and cluster={cluster_id}' if policy_type == 'operator' else ''}",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": destination} if destination else {})
    }

    response = await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)
    return response.json()


async def async_node_policy(anylog_conn:AnyLogRest,node_type:str, name:str, company:str,
                            cluster:str|None=None, ip:str|None=None, tcp_port:int|None=None, tcp_bind:bool|str=False,
                            rest_port:int|None=None, rest_bind:bool|str=False, broker_port:int|None=None,
                            broker_bind:bool|str=False, destination:str|None=None, exec_mode:ExecMode=ExecMode.EXECUTE,
                            **kwargs)->dict|None:
    """
    Build a node policy (master, operator, query, publisher)
    :args:
        node_type:str - master, operator, query, publisher, master-operator or master-publisher
        name:str - node name
        company:str - company name
        ip:str - force use a specific IP address if bidning is true
        tcp_port:int|None - TCP port
        rest_port:int|None - REST port
        broker_port:int|None - message broker port

        tcp_bind:bool|str - TCP bound to a single IP
        rest_bind:bool|str - REST bound to a single IP
        broker_bind:bool|str - Broker bound to a single IP

        kwargs - additional node params (None / empty values are skipped)
            hostname:str - node hostname
            cluster:str - cluster policy ID (required for operator / master-operator)
            main:bool|str - operator is the main member of its cluster
            loc:str - "latitude,longitude"
            country:str - country
            state:str - state
            city:str - city
        exec_mode:ExecMode - Execution mode (only INFO changes behavior)
    :binding:
        tcp_bind=False - policy publishes ip (external) and local_ip (internal)
        tcp_bind=True  - policy publishes a single "ip" = local_ip (or ip if local_ip isn't set)
    :return:
        {node_type: {...}}
        None - INFO mode, or invalid node type / missing params when exceptions are disabled
    :sample-output:
        {"operator": {"name": "water-plant-operator1", "company": "Smart City", "hostname": "smart-city-operator1",
                      "ip": "172.105.60.50", "port": 32148, "rest_port": 32149, "broker_port": 32150,
                      "cluster": "64999c0d4d8762f67f6fe4f120c7a54b", "main": true,
                      "loc": "33.7490,-84.3880", "country": "US", "state": "GA", "city": "Atlanta"}}
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_node_policy)
        return None
    elif node_type in ["standalone", "standalone-operator", "master-operator"]:
        node_type = "operator"
    elif node_type in ["standalone-publisher", "master-publisher"]:
        node_type = "publisher"

    supported_node_types = [node for node in POLICY_REQUIRED_PARAMS if node not in ["object", "uns", "cluster"]]
    if node_type not in supported_node_types:
        # if not a valid node type: master, operator, query, publisher
        return await async_exec_logging(message=f"Invalid node type {node_type!r} - supported: { ','.join(supported_node_types)} "
                                                f"- policy not created",
                                        level=LevelMode.ERROR, exception_type=ValueError)
    elif (not name or not company) or (node_type == "operator" and not cluster):
        # if valid node type but missing config - operator also requires cluster (ID)
        return await async_exec_logging(
            message=f"Invalid base configurations for type {node_type!r} - required params: {','.join(POLICY_REQUIRED_PARAMS.get(node_type))} "
                    f"- policy not created",
            level=LevelMode.ERROR, exception_type=ValueError)


    default_config = await _async_create_policy_defaults(anylog_conn=anylog_conn, policy_type=node_type, name=name,
                                                         company=company, cluster_id=cluster, destination=destination,
                                                         exec_mode=exec_mode)


    node = default_config.get(node_type)
    if not ip:
        ip = node.pop("internal_ip", None) or node.pop("local_ip", None) if _format_val(tcp_bind) is True else node.get("ip")

    node["ip"] = ip if _format_val(tcp_bind) is True else node["ip"]
    node["port"] = _format_val(tcp_port) if tcp_port else node["port"]
    node["rest_port"] = _format_val(rest_port) if rest_port else node["rest_port"]
    if _format_val(rest_bind):
        node["rest_ip"] = ip
    if broker_port:
        node["broker_port"] = _format_val(broker_port)
        if _format_val(broker_bind):
            node["broker_ip"] = ip

    if kwargs:
        for key, value in kwargs.items():
            if value:
                node[key] = _format_val(value, is_loc=True if key.startswith("loc") else False)

    return {node_type: _clean(node)}

# ---------------------------------------------------------------------------------------------------------------------
# Cluster
# ---------------------------------------------------------------------------------------------------------------------
async def _async_cluster_policy_defaults(anylog_conn:AnyLogRest, name:str, company:str, destination:str|None=None,
                                         exec_mode:ExecMode=ExecMode.EXECUTE):

    headers = {
        "command": f"create policy cluster with defaults where name={name} and company={company}",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": destination} if destination else {})
    }

    response = await anylog_conn.async_post(headers=headers, payload=None, exec_mode=exec_mode)
    return  response.json()

async def async_cluster_policy(anylog_conn:AnyLogRest, name:str, company:str, destination:str|None=None,
                               exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|None:
    """
    Build a cluster policy - operators reference it by ID ("cluster" in the operator policy)
    :args:
        name:str - cluster name
        company:str - company name
        status:str - cluster status
        exec_mode:ExecMode - Execution mode (only INFO changes behavior)
        kwargs - additional cluster params (None / empty values are skipped)
    :return:
        {"cluster": {...}}
        None - INFO mode, or missing params when exceptions are disabled
    :sample-output:
        {"cluster": {"company": "Smart City", "name": "water-plant", "status": "active"}}
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_cluster_policy)
        return None

    default_policy = await _async_cluster_policy_defaults(anylog_conn, name=name, company=company, destination=destination,
                                                    exec_mode=exec_mode)

    if not kwargs:
        return default_policy

    return {"cluster": {**default_policy.get("cluster"), **_clean(**kwargs)}}


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
    :sample-output:
        {"object": {"name": "proveit", "description": "object for MQTT proveit"}}
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_object_policy)
        return None

    if await _missing_params(policy_type="object", params={"name": name}):
        return None

    return {"object": _clean({"name": name, "description": description, **kwargs})}


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
    :sample-output:
        {"uns": {"name": "proveit", "namespace": "proveit", "source_node": "bottle-factory2@173.255.212.88:32148",
                 "object_id": "96b8c7d6f6e14e26939169a517f5229a"}}
    """
    if exec_mode == ExecMode.INFO:
        exec_info(func=async_uns_policy)
        return None

    params = {"name": name, "object_id": object_id}
    if await _missing_params(policy_type="uns", params=params):
        return None

    return {"uns": _clean({"name": name, "namespace": namespace or name, "source_node": source_node,
                           "object_id": object_id, **kwargs})}


# ---------------------------------------------------------------------------------------------------------------------
# Sync wrappers - same arguments as the async version
# ---------------------------------------------------------------------------------------------------------------------
def generic_policy(*args, **kwargs)->dict|None:
    """Sync wrapper around `async_generic_policy`"""
    return asyncio.run(async_generic_policy(*args, **kwargs))


def config_policy(*args, **kwargs)->dict|None:
    """Sync wrapper around `async_config_policy`"""
    return asyncio.run(async_config_policy(*args, **kwargs))


def node_policy(anylog_conn:AnyLogRest,node_type:str, name:str, company:str,  cluster:str|None=None, ip:str|None=None,
                tcp_port:int|None=None, tcp_bind:bool|str=False, rest_port:int|None=None, rest_bind:bool|str=False,
                broker_port:int|None=None, broker_bind:bool|str=False, destination:str|None=None,
                exec_mode:ExecMode=ExecMode.EXECUTE, **kwargs)->dict|None:
    """Sync wrapper around `async_node_policy`"""
    return asyncio.run(async_node_policy(anylog_conn=anylog_conn, node_type=node_type, name=name, company=company,
                                         cluster=cluster, ip=ip, tcp_port=tcp_port, tcp_bind=tcp_bind,
                                         rest_port=rest_port, rest_bind=rest_bind, broker_port=broker_port,
                                         broker_bind=broker_bind, destination=destination, exec_mode=exec_mode,
                                         **kwargs))


def cluster_policy(name:str, company:str, *args, **kwargs)->dict|None:
    """Sync wrapper around `async_cluster_policy`"""
    return asyncio.run(async_cluster_policy(name=name, company=company, *args, **kwargs))


def object_policy(*args, **kwargs)->dict|None:
    """Sync wrapper around `async_object_policy`"""
    return asyncio.run(async_object_policy(*args, **kwargs))


def uns_policy(*args, **kwargs)->dict|None:
    """Sync wrapper around `async_uns_policy`"""
    return asyncio.run(async_uns_policy(*args, **kwargs))