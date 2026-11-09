"""
Shared helpers used by every module in `src/`
"""
import ast
import asyncio
import json
import inspect
import os
import re

from enum import Enum

from src.core.support_logging import LevelMode, async_exec_logging

ANYLOG_AGENT = "AnyLog/1.23"    # value of the `AnyLog-Agent` header on every request


class ListCommands:
    """
    Help with function information
    """
    def list_commands(self):
        """
        Docstring of every public method, keyed by method name
        """
        return {
            name: getattr(self, name).__doc__
            for name in dir(self)
            if not name.startswith("_") and callable(getattr(self, name))
        }


class ExecMode(Enum):
    EXECUTE = "execute"     # run the command against the node
    COMMAND = "command"     # return the AnyLog command without sending it
    HELP = "help"           # print AnyLog's help for the command
    INFO = "info"           # print the python function name + description


# ---------------------------------------------------------------------------------------------------------------------
# REST
# ---------------------------------------------------------------------------------------------------------------------
def build_headers(command:str, remote_destination:str|None=None, **extra_headers)->dict:
    """
    REST headers for an AnyLog command
    :args:
        command:str - AnyLog command
        remote_destination:str - send the request through the connected node to another agent
            None / "local" - run on the connected node only
            "network" - every relevant node in the network
            "ip:port" (comma-separated for several) - specific node(s)
        extra_headers - additional headers (ex. topic, Content-Type)
    :return:
        {"command": command, "AnyLog-Agent": ANYLOG_AGENT, ["destination": remote_destination], **extra_headers}
    """
    headers = {"command": command, "AnyLog-Agent": ANYLOG_AGENT}
    if remote_destination and str(remote_destination).strip().lower() != "local":
        headers["destination"] = remote_destination
    headers.update(extra_headers)
    return headers


def url_builder(conn:str, is_auth:bool=False)->str:
    """
    Full URL for an AnyLog REST connection
    :args:
        conn:str - host:port, or a full URL (returned as-is)
        is_auth:bool - use https (authenticated connection)
    :return:
        http(s)://host:port
    """
    if conn.startswith("http"):
        return conn
    scheme = "https" if is_auth else "http"
    return f"{scheme}://{conn}"


def load_json(file_path:str)->dict:
    """
    Load a JSON file whose keys are numeric (ex. HTTP status codes)
    :args:
        file_path:str - JSON file (~ and $VARS are expanded)
    :return:
        dict with int keys
    :raise:
        FileNotFoundError - file doesn't exist
    """
    full_path = os.path.expandvars(os.path.expanduser(file_path))
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(full_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    return {int(key): value for key, value in data.items()}


def exec_info(func):
    """
    Print the python function name + the first line of its docstring (ExecMode.INFO)
    :args:
        func - function
    :return:
        None - info is printed
    :sample-output:
        method: async_get_status
        description: Execute `get status` against AnyLog node
    """
    doc = inspect.getdoc(func) or ""
    summary = doc.splitlines()[0] if doc else ""  # just the first line of the docstring
    info = f"method: {func.__name__}\ndescription: {summary}"
    print(info)
    return None

# ---------------------------------------------------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------------------------------------------------
def serialize_data(payload)->str|None:
    """
    Serialize payload to a JSON string for publishing
    :args:
        payload - dict, list, or an already-serialized string (returned as-is)
    :return:
        JSON string, or None if the payload can't be serialized
    :raise:
        TypeError - payload can't be serialized (when FORCE_EXCEPTION is on)
    """
    if isinstance(payload, str):
        return payload
    try:
        return json.dumps(payload)
    except (TypeError, ValueError) as error:
        return asyncio.run(async_exec_logging(message=f"Failed to serialize content to be published (Error: {error})",
                                              level=LevelMode.ERROR, exception_type=TypeError, cause=error))


def format_value(value)->str:
    """
    Format a value for an AnyLog where condition
    :args:
        value -
            bool / 'true' / 'false' -> true / false
            int / float / numeric string -> as is
            string -> "quoted" (left alone if already quoted)
    :return:
        formatted value
    """
    if isinstance(value, bool):          # check before int - bool is a subclass of int
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)

    value = str(value).strip()
    if value.lower() in ("true", "false"):
        return value.lower()
    if re.fullmatch(r"-?\d+(\.\d+)?", value):
        return value
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):  # already quoted
        return value
    return f"'{value}'" if '"' in value else f'"{value}"'


def format_conditions(conditions)->list[str]:
    """
    Format where conditions, quoting each value with `format_value`
    :args:
        conditions - list ('key=value'), dict, or a stringified list (ex. from a CLI / env var)
    :return:
        ['name=My Cluster', 'status=active'] -> ['name="My Cluster"', 'status="active"']
    """
    if isinstance(conditions, str):
        conditions = conditions.strip().strip('"')
        try:
            conditions = ast.literal_eval(conditions)
        except (ValueError, SyntaxError):
            conditions = [conditions]

    if isinstance(conditions, dict):
        return [f"{k}={format_value(v)}" for k, v in conditions.items()]

    formatted = []
    for cond in conditions:
        key, sep, val = str(cond).partition("=")   # split on first '=' only
        formatted.append(f"{key.strip()}={format_value(val)}" if sep else str(cond))
    return formatted