# AnyLog API

`AnyLog-API` gives you a Python client for talking to an AnyLog/EdgeLake node over REST — built so you can either 
`pip install` it as a standalone package, or drop the `src/` folder straight into your own codebase as an import. 
The goal is for a user (you, or a customer) to build on top of this rather than hand-rolling REST calls against 
AnyLog/EdgeLake themselves: connect once, then call Python functions instead of constructing HTTP requests and AnyLog 
command strings by hand.

A full list of available functions is in [FUNCTIONS.md](FUNCTIONS.md) — that's the original planned layout; 
if you land on a better dir/file structure, go for it.

## Roadmap

Rough priority order for what's left before this is something to hand to customers:

### 1. Finish `ExecMode.INFO` support

Every function in `generic/config.py` and `generic/logs.py` still needs its `if exec_mode == ExecMode.INFO:` check 
added (see **Sample method** below). `generic/status.py` already has this — use it as the reference.

### 2. Node deployment as REST calls

Functions that execute each part of deploying an AnyLog/EdgeLake node, expressed as Python calls through `AnyLogRest` 
rather than hand-written commands. Give the caller two ways to run it: as a single config policy (one blockchain policy 
describing the whole node), or standalone, command by command, over REST.

**The full path:**
1. Read a `.env` file — deployment parameters (node type, IP/port, database settings, cluster info, etc.) live in a dotenv file rather than being hardcoded.
2. Convert those params into configs — values from `.env` get mapped into the config dict(s) each deployment command needs.
3. Generate / execute commands based on user input — build the config policy, or generate and run the equivalent commands one by one over REST.

Reference logic and sample commands:[`deployment-scripts/node-deployment`](https://github.com/AnyLog-co/deployment-scripts/tree/os-dev), 
specifically [`config_policy.al`](https://github.com/AnyLog-co/deployment-scripts/blob/os-dev/node-deployment/policies/config_policy.al).

**Generic node** (assumes TCP, REST, and optionally Broker ports are already configured):
1. Set node name
2. Connect to logical database(s) + table(s)
3. `run blockchain sync`
4. Define node policy — operator nodes also need a cluster defined
5. `run scheduler 1`
6. Enable the MCP server
7. Set license

**Operator nodes**, additionally:
1. Partition + scheduled partition-clean process
2. Data distributor / data consumer
3. Blob archiver, streamer + buffering
4. `run operator`

**Publisher nodes**, additionally:
1. Streamer + buffering
2. `run publisher`

### 3. Data support

The package should let a user send data into AnyLog via PUT or POST, and query data — plus query the blockchain — via 
GET and/or POST.

> **Do this before Advanced (below).**

### 4. Advanced

Lower priority than data support:
- Node monitoring
- Configurable `run msg client`

## Sample method

Every action function follows the same shape: build a `headers` dict describing the AnyLog command, then hand it to the 
`AnyLogRest` connection to actually send. `exec_mode == ExecMode.INFO` short-circuits before any of that — it prints the 
method's name and docstring summary via the shared `exec_info()` helper (`src/core/support.py`) and returns without 
touching the network.

```python
import asyncio

from src.core.anylog_rest_api import AnyLogRest
from src.core.support import ExecMode, exec_info

async def async_get_status(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    Asynchronized `get status` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
        json_format:bool - whether to return results in JSON format
        remote_destination:str - run request against a remote node, if so provide IP and port
    :params:
        headers:dict - REST headers
    :return:
        node status
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=async_get_status)

    headers = {
        "command": "get status where format=json" if json_format else "get status",
        "AnyLog-Agent": "AnyLog/1.23",
        **({"destination": remote_destination} if remote_destination else {})
    }

    return await anylog_conn.async_get_via_post(headers=headers, exec_mode=exec_mode)

def get_status(anylog_conn:AnyLogRest, json_format:bool=True, remote_destination:str|None=None, exec_mode=ExecMode.EXECUTE):
    """
    `get status` against AnyLog node
    :args:
        anylog_conn:AnyLogRest - connection to node
        json_format:bool - whether to return results in JSON format
        remote_destination:str - run request against a remote node, if so provide IP and port
    :params:
        headers:dict - REST headers
    :return:
        node status
    """
    if exec_mode == ExecMode.INFO:
        return exec_info(func=get_status)

    return asyncio.run(async_get_status(anylog_conn=anylog_conn, json_format=json_format,
                                        remote_destination=remote_destination, exec_mode=exec_mode))
```

New action functions (config, logs, deployment, etc.) should follow this same pattern: `headers` dict in, 
`anylog_conn.get_via_post` / `.async_get_via_post` / `.post` / `.put` out, with the `ExecMode.INFO` check as the first 
line of the function body

## How to test / use it

The fastest way to validate a change is against a real node rather than mocks — AnyLog/EdgeLake's command surface is large enough that a mocked response can hide real issues.

1. Deploy a generic AnyLog/EdgeLake node (Docker is the quickest route — see the `Dockerfile` in this repo, or your own existing node).
2. Point `AnyLogRest` (or the higher-level functions in `src/generic/`, `src/core/`, etc.) at that node's REST endpoint.
3. Run the commands you're testing through it — `get_status`, `test_node`, etc. — and confirm the response shape matches what the docstring promises.
4. For a quick sanity check without hitting the network at all, call the same function with `exec_mode=ExecMode.COMMAND` (returns the generated AnyLog command string) or `exec_mode=ExecMode.INFO` (prints the method + docstring summary) before running it for real.